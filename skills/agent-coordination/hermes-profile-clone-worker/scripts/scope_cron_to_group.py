#!/usr/bin/env python3
"""Scope a cloned Hermes profile's cron/jobs.json down to one group's jobs.

Usage:
    python3 scope_cron_to_group.py <profile_dir> <chat_id>

Keeps only jobs whose `deliver == 'telegram:<chat_id>'`. This prevents the
cloned worker from double-firing jobs that also live in the source profile.
Leaves a .bak of the original jobs.json.

Example:
    python3 scope_cron_to_group.py /root/.hermes/profiles/gentech-treasury -1002916759037
"""
import json
import shutil
import sys
from datetime import datetime


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    profile_dir, chat_id = sys.argv[1], sys.argv[2]
    jobs_path = f"{profile_dir}/cron/jobs.json"
    target = f"telegram:{chat_id}"

    with open(jobs_path) as f:
        data = json.load(f)
    jobs = data.get("jobs", data)

    keep = [j for j in jobs if j.get("deliver") == target]
    dropped = len(jobs) - len(keep)

    if not keep:
        print(f"WARNING: no jobs deliver to {target}; profile would be empty. Aborting.")
        sys.exit(1)

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.copy2(jobs_path, f"{jobs_path}.bak-{ts}")
    data["jobs"] = keep
    with open(jobs_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Scoped to {len(keep)} jobs delivering to {target} (dropped {dropped}).")
    print(f"Backup: {jobs_path}.bak-{ts}")
    for j in keep:
        print(f"  - {j.get('name')}")


if __name__ == "__main__":
    main()
