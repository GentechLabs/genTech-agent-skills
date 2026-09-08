# Pre-Restart Checkpoint Handoff — TEMPLATE

> **Purpose:** Before ANY gateway restart, every affected agent must park its work
> cleanly. This is the controlled-window handoff that prevents surprise-reboot data loss.
> **Owner:** Gentech (HQ) dispatches to each profile before a fleet restart.
> **Rule:** NO restart until every affected agent returns an ACK. Never restart on timeout
> or assume silence = safe.

## How to use

1. Copy this template once per affected profile (gentech, gentech-treasury, gizmo, pixel).
2. Fill the `[ ]` placeholders.
3. Save to `01-HANDOFFS/gentech-to-<profile>/<date>-pre-restart-checkpoint.md`.
4. The gateway delivers it to that agent. Wait for its return ACK in
   `01-HANDOFFS/<profile>-to-gentech/` (or INBOX).
5. Only when ALL acks are in → run `fleet_update.py --restart-only`.

## Template

```markdown
# ⏸️ Pre-Restart Checkpoint — <PROFILE> (from Gentech HQ)

**Date:** <YYYY-MM-DD HH:MM ET>
**Re:** Fleet gateway restart — controlled window
**Action required:** Checkpoint your work, then ACK. Do NOT start new long-running work.

---

## Why

We're about to restart the fleet gateways (all 4 profiles) to load fresh config.
A gateway restart drops your current session — you resume blind on the next turn.
This handoff gives you a chance to **park your work cleanly** before we cycle.

## What to do (in order)

1. **Save your in-flight state to the vault NOW.** If you're mid-task, write a
   progress note to `01-HANDOFFS/<profile>-to-gentech/<date>-checkpoint.md` (or your
   lane's handoff dir) capturing:
   - What you were working on
   - What's done / what's half-done / what's next
   - Any state that must survive the restart (positions, files, config, keys)
2. **Do NOT start any new long-running task** until the restart completes.
3. **Reply with ACK** — a short return note confirming you've saved state and are
   safe to restart. Format:
   ```
   ✅ CHECKPOINTED — <profile> safe to restart.
   In-flight: <one line>
   State saved to: <path>
   ```

## Guardrail

- If you are mid-task and CANNOT checkpoint safely right now, say so explicitly
  ("NOT READY — mid-<task>") instead of ACKing. We will wait.
- Silence is NOT treated as ACK. We wait for your explicit return note.

— Gentech HQ
```

## ACK tracking (Gentech fills this)

| Profile | Handoff sent | ACK received | Safe to restart? |
|---------|--------------|--------------|------------------|
| gentech | [ ] | [ ] | [ ] |
| gentech-treasury | [ ] | [ ] | [ ] |
| gizmo | [ ] | [ ] | [ ] |
| pixel | [ ] | [ ] | [ ] |

**Restart gate:** ALL rows must be ✅ before `fleet_update.py --restart-only`.
