# BRIEFING.md File Creation Guide

## When This Applies
Use this reference when `00-BRIEFING.md` file is missing and wake-up protocol fails.

## Quick Creation Command
```bash
# Create the briefing file in the correct location
cat > /root/vaults/gentech/00-BRIEFING.md << 'EOF'
---
name: GenTech BRIEFING
version: 2.0.0
last_updated: 2026-06-30
purpose: Identity and behavioral rules for GenTech agent - READ ON EVERY RESTART
---

# GenTech BRIEFING — Agent Identity & Rules

[See skill template for complete structure]
EOF
```

## File Structure Requirements
The file must contain:
- YAML header with identity metadata
- Identity section: "WHO AM I?" with GenTech role description
- Jordan's profile with location, job search, AI stack, business plan
- People & collaborators section
- Two Gentechs architecture
- Current milestones
- Critical workflows
- Communication protocols
- Recovery protocols
- Skills to load first

## Detection Method
Wake-up auto-detection script checks for file existence:
```python
BRIEFING_PATH = VAULT_ROOT / "00-BRIEFING.md"
if not BRIEFING_PATH.exists():
    print("[ERROR] Could not read BRIEFING.md — wake-up incomplete")
    return 2
```

## Prevention
The `session-startup` skill should create this file if missing on fresh sessions.