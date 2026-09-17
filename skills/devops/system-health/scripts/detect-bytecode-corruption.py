#!/usr/bin/env python3
"""
Detect corrupted Python bytecode (.pyc) files in Hermes installation.

Scans __pycache__ directories and checks .pyc header sanity. Corrupted
files typically have header source-size fields that are unreasonably large
(gigabytes) while the actual .py file is only tens of kilobytes.

Usage:
  python3 detect_bytecode_corruption.py [/path/to/hermes-agent]
  # defaults to /usr/local/lib/hermes-agent
"""

import struct, glob, os, sys
from pathlib import Path

def check_pyc(pyc_path):
    """Return (is_corrupted, reason) tuple."""
    try:
        with open(pyc_path, 'rb') as f:
            header = f.read(16)
        if len(header) < 16:
            return True, "header too short (<16 bytes)"

        # .pyc header: 4-byte magic, 4-byte mtime, 4-byte source size, (4-byte flags for 3.7+)
        magic = header[:4]
        source_size_in_header = struct.unpack('<I', header[8:12])[0]

        # Find corresponding .py file
        py_path = pyc_path.replace('__pycache__/', '').replace('.cpython-311.pyc', '.py')
        # Handle other python versions too
        for version_suffix in ['.cpython-310.pyc', '.cpython-39.pyc', '.cpython-38.pyc', '.pyc']:
            test_py = pyc_path.replace('__pycache__/', '').replace(version_suffix, '.py')
            if os.path.exists(test_py):
                py_path = test_py
                break

        if os.path.exists(py_path):
            actual_size = os.path.getsize(py_path)
            # Heuristic: header size should be within 2x of actual source size
            if source_size_in_header > actual_size * 10 or source_size_in_header < actual_size * 0.1:
                return True, f"header_size={source_size_in_header} actual={actual_size}"
        else:
            # .py file missing — still check if header size is absurd
            if source_size_in_header > 50_000_000:
                return True, f"header_size={source_size_in_header} (source_missing)"

        return False, None
    except Exception as e:
        return True, str(e)

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else '/usr/local/lib/hermes-agent'
    print(f"Scanning {root} for corrupted .pyc files...")

    pycache_dirs = glob.glob(f'{root}/**/__pycache__', recursive=True)
    print(f"Found {len(pycache_dirs)} __pycache__ directories")

    corrupted = []
    total = 0
    for pcd in pycache_dirs:
        pyc_files = glob.glob(f'{pcd}/*.pyc')
        for pyc in pyc_files:
            total += 1
            is_corrupt, reason = check_pyc(pyc)
            if is_corrupt:
                corrupted.append((pyc, reason))

    print(f"\nTotal .pyc files scanned: {total}")
    print(f"Corrupted files found: {len(corrupted)}")

    if corrupted:
        print("\nCorrupted files:")
        for path, reason in corrupted[:50]:
            print(f"  {path}")
            print(f"    → {reason}")
        print("\nTo fix: rm -rf <directory>/__pycache__ and restart Hermes gateways")
        return 1
    else:
        print("\n✓ No bytecode corruption detected")
        return 0

if __name__ == '__main__':
    sys.exit(main())
