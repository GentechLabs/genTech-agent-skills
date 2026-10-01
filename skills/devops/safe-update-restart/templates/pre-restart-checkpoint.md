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
**Action required:** Checkpoint your work, verify the claims below against your own state, then ACK. Do NOT start new long-running work.

**This is a PER-EVENT checkpoint.** An ACK you gave for an earlier phase of the same migration (e.g. the Hermes update) does NOT cover this restart. State at 02:00 and 11:00 may differ, and the mechanism being restarted may differ.

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
2. **Verify the claims in this request against your own state.** Do not echo them as facts.
   Typical claims to check: config migration, cron repointing, provider switch, current gateway topology.
   Measure, then include the result in your ACK.
3. **Record the machine state at ACK time.** Note which gateway processes are running,
   which heartbeat files are fresh, and whether a multiplexer or per-profile gateways are up.
   This becomes the recovery baseline if the restart is interrupted.
4. **Do NOT start any new long-running task** until the restart completes.
5. **Reply with ACK** — a return note confirming you've saved state, verified the claims, and are
   safe to restart. The vault write (commit + sync) is the delivery; attempt the wake DM only after
   the note is durable. Format:
   ```
   ✅ CHECKPOINTED — <profile> safe to restart.
   In-flight: <one line>
   State saved to: <path>
   Verified: <config/cron/topology claims you checked>
   Host at ACK: <gateway processes running / multiplexer or per-profile>
   ACK note: 01-HANDOFFS/<profile>-to-gentech/<date>-<topic>.md
   ```

## Guardrail

- If you are mid-task and CANNOT checkpoint safely right now, say so explicitly
  ("NOT READY — mid-<task>") instead of ACKing. We will wait.
- Silence is NOT treated as ACK. We wait for your explicit return note.
- If your wake DM fails because the target gateway is already down, the vault note is still the ACK.
  Do not hold the restart waiting for a DM confirmation that cannot arrive.

## Topology note for migration checkpoints

If this restart is part of a gateway topology migration (per-profile → multiplex):
- A "half-migrated" host (one gateway down, multiplexer not yet up) is explicitly supported.
- The migration preflight can be read without changes: `hermes gateway migrate --multiplex --dry-run`.
- There is no rollback command, but a `gateway.standalone: true` shim exists for temporary per-profile continuity.
- Record the running gateway processes and heartbeat times in your ACK so the post-migration state is recoverable.

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
