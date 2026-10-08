#!/usr/bin/env python3
"""
Leaver / group-retirement delivery sweep.

Run on a host where all Hermes profile roots are visible. It reads each profile's
cron/jobs.json, resolves `deliver=origin` to its stored origin, and flags any job
whose resolved chat_id or user_id matches a leaver or retired group.

Add `--dry-run` to print without changing anything. Without --dry-run the script
only READS; use its output to drive explicit `cronjob update` commands.

Example:
    python3 leaver-delivery-sweep-script.py \
        --leaver-chats -1003893562036 \
        --leaver-users 8774981477 \
        --profiles pixel gentech gentech-treasury gizmo
"""
import argparse, json, os, sys
from pathlib import Path

def load_jobs(profile):
    p = Path(f"/root/.hermes/profiles/{profile}/cron/jobs.json")
    if not p.exists():
        return []
    return json.loads(p.read_text()).get("jobs", [])

def resolve_target(job):
    d = job.get("deliver", "")
    if isinstance(d, str) and d.strip() == "origin":
        o = job.get("origin") or {}
        if o:
            return f"origin:{o.get('platform')}:{o.get('chat_id')}:{o.get('user_id')}", o
        return "origin:unresolved", {}
    return str(d), {}

def main():
    parser = argparse.ArgumentParser(description="Sweep cron deliveries for leavers/retired groups")
    parser.add_argument("--profiles", nargs="+", default=["pixel","gentech","gentech-treasury","gizmo"])
    parser.add_argument("--leaver-chats", nargs="*", default=[], help="chat_ids that are retired")
    parser.add_argument("--leaver-users", nargs="*", default=[], help="user_ids of people leaving")
    parser.add_argument("--leaver-names", nargs="*", default=[], help="strings that flag ownership (prompt/intent)")
    parser.add_argument("--exclude-strings", nargs="*", default=["not ", "exclude ", "ignore ", "skip "],
                        help="if a prompt contains these, the name match is an exclusion, not ownership")
    parser.add_argument("--dry-run", action="store_true", default=True)
    args = parser.parse_args()

    leaver_chats = set(args.leaver_chats)
    leaver_users = set(args.leaver_users)
    leaver_names = [n.lower() for n in args.leaver_names]

    findings = []
    for profile in args.profiles:
        for j in load_jobs(profile):
            if not j.get("enabled"):
                continue
            target, origin = resolve_target(j)
            prompt = (j.get("prompt") or "").lower()
            intent = (j.get("intent") or j.get("name") or "").lower()
            text = f"{prompt} {intent}"

            # 1. resolved deliver points at leaver
            origin_chat = str(origin.get("chat_id") or "")
            origin_user = str(origin.get("user_id") or "")
            by_target = origin_chat in leaver_chats or origin_user in leaver_users

            # 2. name appears in prompt/intent
            name_hits = [n for n in leaver_names if n in text]
            # 3. but is it an exclusion?
            excluded = any(excl in prompt for excl in args.exclude_strings)

            if by_target or (name_hits and not excluded):
                findings.append({
                    "profile": profile,
                    "id": j.get("id"),
                    "name": j.get("name"),
                    "deliver": j.get("deliver"),
                    "resolved": target,
                    "reason": "target is leaver" if by_target else f"name match {name_hits} (not exclusion)",
                })

    if not findings:
        print("No enabled job resolves to a leaver/retired target.")
        return 0

    print(f"Found {len(findings)} job(s) that need review:")
    for f in findings:
        print(f"  [{f['profile']}] {f['id']}  {f['name']}")
        print(f"      deliver={f['deliver']}  resolved={f['resolved']}")
        print(f"      reason={f['reason']}")
    return 1

if __name__ == "__main__":
    sys.exit(main())
