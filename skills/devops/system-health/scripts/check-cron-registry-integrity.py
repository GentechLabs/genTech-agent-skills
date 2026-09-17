#!/usr/bin/env python3
"""Detect missing cron registry files across Hermes agent profiles.

Purpose:
  Identifies the "cron.json missing entirely" failure pattern where scheduled
  job definitions are absent from one or more agent profiles. This prevents
  any cron dispatch from working for those agents, even if the cron daemon
  is running.

Usage:
  python3 scripts/check-cron-registry-integrity.py

Output:
  Prints JSON summary to stdout. Exits with code 0 if all cron files present
  and non-empty; exits with code 1 if any missing or empty; writes details
  to stderr for human scanning.

Related skill: system-health (detects and remediates missing cron registry)
"""

import json
import os
import sys
from pathlib import Path

AGENTS = ["gentech", "yoyo", "dmob", "desmond"]
HERMES_ROOT = Path.home() / ".hermes"
PROFILES_DIR = HERMES_ROOT / "profiles"


def check_agent_cron_file(agent: str) -> dict:
    """Return status dict for a single agent's cron registry."""
    cron_path = PROFILES_DIR / agent / "cron.json"
    result = {
        "agent": agent,
        "cron_file_exists": cron_path.exists(),
        "cron_file_size": 0,
        "job_count": 0,
        "status": "ok",
        "error": None,
    }

    if not cron_path.exists():
        result["status"] = "missing"
        result["error"] = "cron.json file not found"
        return result

    result["cron_file_size"] = cron_path.stat().st_size

    if cron_path.stat().st_size == 0:
        result["status"] = "empty"
        result["error"] = "cron.json exists but is zero bytes"
        return result

    try:
        with open(cron_path) as f:
            data = json.load(f)
        jobs = data.get("jobs", []) if isinstance(data, dict) else []
        result["job_count"] = len(jobs)
        if len(jobs) == 0:
            result["status"] = "no_jobs"
            result["error"] = "cron.json parsed but jobs list is empty"
    except json.JSONDecodeError as e:
        result["status"] = "corrupted"
        result["error"] = f"JSON parse error: {e}"

    return result


def main():
    all_results = []
    has_issues = False

    for agent in AGENTS:
        res = check_agent_cron_file(agent)
        all_results.append(res)
        if res["status"] != "ok":
            has_issues = True

    # Print machine-readable summary
    print(json.dumps({"agents": all_results, "summary": {"has_issues": has_issues}}, indent=2))

    # Human-readable scan output to stderr
    for res in all_results:
        if res["status"] == "ok":
            print(f"[OK]   {res['agent']}: {res['job_count']} jobs", file=sys.stderr)
        else:
            print(f"[{res['status'].upper()}] {res['agent']}: {res['error']}", file=sys.stderr)

    if has_issues:
        print("\nRemediation:", file=sys.stderr)
        print("  1. Check global jobs: hermes cron list --format json", file=sys.stderr)
        print("  2. Re-sync profile: hermes cron sync --profile <agent>", file=sys.stderr)
        print("  3. Restart gateways: hermes gateway run --profile <agent> --replace", file=sys.stderr)
        sys.exit(1)
    else:
        print("All cron registries present and valid.", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
