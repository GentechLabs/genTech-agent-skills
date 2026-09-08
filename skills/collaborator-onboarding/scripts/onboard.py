#!/usr/bin/env python3
"""
GenTech Onboarding Tool — Add a new collaborator across all platforms.
Usage: python3 onboard.py --name "StudentName" --username "@handle" --telegram_id 123456789 --topics "voice,tts" --permissions "voice,content"

One command to:
  - Add Telegram ID to TELEGRAM_ALLOWED_USERS
  - Create vault profile (00-HQ/collaborators/)
  - Update mapping.json
  - Log to progress tracker
"""

import os, sys, argparse, json, datetime
from pathlib import Path

PROFILE = os.environ.get("HERMES_PROFILE", "gentech")
ENV_PATH = Path(f"/root/.hermes/profiles/{PROFILE}/.env")
VAULT_DIR = Path("/root/vaults/gentech")
COLLAB_DIR = VAULT_DIR / "00-HQ" / "collaborators"
MAPPING_PATH = COLLAB_DIR / "mapping.json"

parser = argparse.ArgumentParser(description="Onboard a new collaborator")
parser.add_argument("--name", required=True)
parser.add_argument("--username", default=None)
parser.add_argument("--telegram_id", required=True)
parser.add_argument("--topics", default="")
parser.add_argument("--permissions", default="")
parser.add_argument("--notes", default="")
args = parser.parse_args()

name = args.name.lower()
topics_list = [t.strip() for t in args.topics.split(",") if t.strip()]
perms_list = [p.strip() for p in args.permissions.split(",") if p.strip()]

print(f"\n=== Onboarding: {args.name} ===")
print(f"  Telegram: {args.username or '(none)'} / ID: {args.telegram_id}")

# Step 1: Add to TELEGRAM_ALLOWED_USERS
if ENV_PATH.exists():
    env_content = ENV_PATH.read_text()
    allowed_line = [l for l in env_content.split("\n") if l.startswith("TELEGRAM_ALLOWED_USERS=")]
    if allowed_line:
        current = allowed_line[0]
        ids = current.split("=", 1)[1].split(",")
        if args.telegram_id not in ids:
            ids.append(args.telegram_id)
            new_line = f"TELEGRAM_ALLOWED_USERS={','.join(ids)}"
            env_content = env_content.replace(current, new_line)
            ENV_PATH.write_text(env_content)
            print(f"  ✅ Added {args.telegram_id} to TELEGRAM_ALLOWED_USERS")
        else:
            print(f"  ⏭️  Already in TELEGRAM_ALLOWED_USERS")
    else:
        print(f"  ⚠️  TELEGRAM_ALLOWED_USERS not found in .env")

# Step 2: Create vault profile
COLLAB_DIR.mkdir(parents=True, exist_ok=True)
profile_path = COLLAB_DIR / f"{name}.md"
profile_content = f"""# {args.name} — GenTech Labs Collaborator

## Role
- New collaborator

## Background
{args.notes if args.notes else 'TBD'}

## Topics
{chr(10).join(f'- {t}' for t in topics_list) if topics_list else '- TBD'}

## Permissions
{chr(10).join(f'- {p}' for p in perms_list) if perms_list else '- TBD'}

## Telegram
- Username: {args.username or 'N/A'}
- User ID: {args.telegram_id}

---
**Added:** {datetime.date.today().isoformat()}
**Status:** Onboarding
"""
profile_path.write_text(profile_content)
print(f"  ✅ Profile: 00-HQ/collaborators/{name}.md")

# Step 3: Update mapping.json
if MAPPING_PATH.exists():
    mapping = json.loads(MAPPING_PATH.read_text())
else:
    mapping = {"version": "1.0", "last_updated": "", "collaborators": {}}
mapping["collaborators"][name] = {
    "telegram_username": args.username,
    "telegram_id": args.telegram_id,
    "profile": f"00-HQ/collaborators/{name}.md",
    "topics": topics_list,
    "permissions": perms_list,
    "status": "onboarding" if not perms_list else "active"
}
mapping["last_updated"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
MAPPING_PATH.write_text(json.dumps(mapping, indent=2))
print(f"  ✅ Mapping updated")

# Step 4: Create progress tracker
progress_path = COLLAB_DIR / f"{name}-progress.md"
if not progress_path.exists():
    content = f"""# {args.name} — Progress Tracker

## Status: Onboarding

### Profile
- Name: {args.name}
- Telegram: {args.username or 'N/A'} ({args.telegram_id})
- Topics: {', '.join(topics_list) or 'TBD'}

### Training Track
| Stage | Status | Date | Notes |
|-------|--------|------|-------|
| Onboarding complete | ✅ Done | {datetime.date.today().isoformat()} | Vault + env + mapping |

### Progress Log
**{datetime.date.today().isoformat()} — Onboarding Complete**
- Added to TELEGRAM_ALLOWED_USERS
- Vault profile created
- Mapping registered
"""
    progress_path.write_text(content)
    print(f"  ✅ Progress tracker created")

print(f"\n✅ {args.name} onboarded. Messages will now be delivered.")
