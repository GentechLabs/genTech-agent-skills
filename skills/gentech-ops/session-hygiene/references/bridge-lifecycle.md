# Context Bridge Lifecycle Reference

## What It Is
A timestamped session snapshot saved to `09-Green Room/context-bridge/context-{timestamp}.md`. The symlink `latest-context.md` always points to the most recent save so wake-up reads a fixed path.

## When It Saves

| Trigger | Who | When |
|---------|-----|------|
| Pre-restart bridge | `daily-gateway-restart.sh` | 6:25 AM ET daily (before gateway restart) |
| Memory ≥85% | session-hygiene auto-detect | During any session on any memory() save |
| Memory ≥90% (emergency) | session-hygiene auto-detect | Immediate — stops all new saves |
| Manual | Jordan says "save progress" | Any time |

## What Goes In The Bridge

```
# 🔄 Context Bridge — {timestamp}
## Active Projects (what I was building)
## Decisions This Session
## Key Facts Discovered
## Blockers Flagged
## Resume Instructions
```

## Who Reads It

- **wake-up-protocol** — reads `latest-context.md` at Step 7 (Context Recovery). This is the PRIMARY resume path, checked before session_search.
- **session-startup** — wakes up, runs identity, then reads bridge to restore working context.

## The Full Lifecycle

```
Overnight work (midnight-6:25 AM)
  ↓
Gateway restart script runs context-save.py (6:25 AM)
  ↓
Bridge written to context-{timestamp}.md + latest-context.md symlink updated
  ↓
Gateway restarts (6:25:30 AM) — all sessions cleared
  ↓
First morning cron fires (~6:30 AM)
  ↓
session-startup detects fresh session → wake-up-protocol runs
  ↓
wake-up-protocol Step 7 reads latest-context.md → context restored
  ↓
Agent resumes with full overnight context — no blank slate
```

## Script

`/root/.hermes/profiles/gentech/skills/gentech-ops/session-hygiene/scripts/context-save.py`

Run manually:
```bash
python3 /root/.hermes/profiles/gentech/skills/gentech-ops/session-hygiene/scripts/context-save.py
```

## Related
- session-hygiene SKILL.md (auto-detect rules)
- wake-up-protocol SKILL.md (bridge-first resume)
- session-startup SKILL.md (wake-up sequence)
- daily-gateway-restart.sh (pre-restart save)
