# Inbox vs. Sender-Folder — Where a Handoff Actually Gets Delivered

## The rule
The `handoff-watcher` cron (every 15 min) scans **only** `01-HANDOFFS/INBOX/<group>/`.
A handoff written to the explicit sender→receiver folder (`gentech-to-forge/`,
`labs-to-treasury/`, etc.) is **invisible to the watcher** and will NOT be picked
up by the target agent.

- **`INBOX/<group>/`** = the delivery lane. Write the canonical `Status: open`
  note here. The watcher surfaces it on the next tick.
- **`<from>-to-<to>/`** = records/returns (completion reports, context). NOT delivery.

## Proven failure (2026-08-26)
Gizmo wrote a 3DGS training handoff to `01-HANDOFFS/gentech-to-forge/` and told
Jordan it was "routed to Forge." Jordan asked **"Did you send the hand off?"** —
correctly — because the note was not in Forge's inbox. It was only delivered
after the note was placed in `01-HANDOFFS/INBOX/forge/` and verified with:

```bash
python3 ${PROFILE_DIR}/scripts/handoff-watcher.py
# → 🆕 NEW handoffs: • [forge] 2026-08-26-3dgs-training.md
```

## Verification checklist (do this before claiming a handoff is sent)
1. Note exists in `01-HANDOFFS/INBOX/<target>/` (not just `<from>-to-<to>/`).
2. `Status: open` in the frontmatter/header.
3. Run `python3 handoff-watcher.py` and confirm the target's lane shows the note.
4. Commit + push the vault.
