#!/usr/bin/env python3
"""Verify Hermes agent bytecode integrity by checking .pyc magic numbers.

Detects corrupted Python bytecode cache files before they cause import failures.
Exit code 0 = all clear; 1 = corruption detected; 2 = error.

Usage:
  python verify_bytecode_integrity.py [--path /usr/local/lib/hermes-agent]
  python verify_bytecode_integrity.py --all-agent-caches
"""

import argparse
import os
import struct
import sys
from pathlib import Path

# Python 3.11 magic number (little-endian uint32)
# Source: https://github.com/python/cpython/blob/main/Python/magicnumbers.h
PYTHON_311_MAGIC = b'\x33\x0d\x0d\x0a'

# Known Hermes agent cache directories
HERMES_CACHE_PATHS = [
    "/usr/local/lib/hermes-agent/agent/__pycache__/",
    "/usr/local/lib/hermes-agent/tools/__pycache__/",
]

def check_pyc_magic(pyc_path: Path) -> tuple[bool, int]:
    """Return (is_valid, claimed_source_size)."""
    try:
        with open(pyc_path, 'rb') as f:
            header = f.read(16)
            if len(header) < 12:
                return False, 0
            magic = header[:4]
            claimed_src_size = struct.unpack('<I', header[4:8])[0]
            return magic == PYTHON_311_MAGIC, claimed_src_size
    except Exception:
        return False, 0

def scan_directory(root: Path, pattern: str = "*.pyc") -> dict:
    """Scan directory recursively for .pyc files and return integrity report."""
    results = {
        "total": 0,
        "corrupted": 0,
        "corrupted_files": [],
        "ok": 0,
    }
    for pyc_file in root.rglob(pattern):
        results["total"] += 1
        is_valid, claimed_size = check_pyc_magic(pyc_file)
        if not is_valid:
            results["corrupted"] += 1
            results["corrupted_files"].append({
                "path": str(pyc_file),
                "claimed_size": claimed_size,
            })
        else:
            results["ok"] += 1
    return results

def main():
    parser = argparse.ArgumentParser(description="Verify Hermes bytecode integrity")
    parser.add_argument("--path", type=Path, help="Specific directory or .pyc file to check")
    parser.add_argument("--all-agent-caches", action="store_true", help="Scan both agent and tools __pycache__ dirs")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args()

    if args.path:
        paths = [args.path]
    elif args.all_agent_caches:
        paths = [Path(p) for p in HERMES_CACHE_PATHS if Path(p).exists()]
        if not paths:
            print("ERROR: No agent cache directories found at expected locations.", file=sys.stderr)
            sys.exit(2)
    else:
        # Default: scan current directory
        paths = [Path('.')]

    total_corrupted = 0
    total_files = 0
    all_corrupted = []

    for scan_path in paths:
        if not scan_path.exists():
            print(f"WARNING: Path does not exist: {scan_path}", file=sys.stderr)
            continue
        results = scan_directory(scan_path)
        total_files += results["total"]
        total_corrupted += results["corrupted"]
        all_corrupted.extend(results["corrupted_files"])

    if args.json:
        import json
        report = {
            "total_files": total_files,
            "corrupted_count": total_corrupted,
            "corrupted_files": all_corrupted,
            "status": "CORRUPT" if total_corrupted > 0 else "OK",
        }
        print(json.dumps(report, indent=2))
        sys.exit(1 if total_corrupted > 0 else 0)
    else:
        print(f"Total .pyc files scanned: {total_files}")
        print(f"Corrupted headers detected: {total_corrupted}")
        if total_corrupted > 0:
            print("\nCorrupted files (first 20):")
            for item in all_corrupted[:20]:
                print(f"  {item['path']} (claimed src size: {item['claimed_size']})")
            if len(all_corrupted) > 20:
                print(f"  ...and {len(all_corrupted) - 20} more")
            print("\n⚠️  BYTECODE CORRUPTION CONFIRMED — gateway restart required after cleanup")
            sys.exit(1)
        else:
            print("✓ All bytecode headers valid")
            sys.exit(0)

if __name__ == "__main__":
    main()
