# Group-to-Group INBOX Handoff System (Aug 12, 2026)

Jordan's preferred handoff model for multi-agent delegation. Supersedes the
earlier one-directional `<group>-to-gentech/` + `*-completions.md` sprawl.

## Why
- Most agents delegate to HQ (Gentech), but peers also need to hand work to
  each other (Labs→Entertainment, Forge→Labs, etc.) — the old model couldn't
  do group-to-group.
- Jordan wants ONE recognizable board he can read to see every handoff and
  where it's going.

## Layout
```
01-HANDOFFS/INBOX/<group>/
    <YYYY-MM-DD>-<topic>.md    # handoff note for that group
    _archive/                  # resolved notes (auto-purged >7d)
```
Groups: hq, forge, labs, entertainment, strategies, finance, treasury, gizmo.
`INBOX/README.md` holds the full protocol + note template.

## Protocol
1. **Send:** any agent writes `<date>-<topic>.md` into the target group's
   inbox. Commit + push (or `ob sync`). Format:
   ```markdown
   # <topic>
   **From:** <agent/group>
   **To:** <group>
   **Date:** <YYYY-MM-DD>
   **Status:** open | [x] resolved
   ## What's needed
   ...
   ## Context / files
   ...
   ```
2. **Read:** each group's wake-up / morning digest reads its inbox. Gentech
   reads ALL inboxes every morning and surfaces anything unaddressed.
3. **Resolve:** tick `- [x]`, move file to `_archive/` (or delete).
4. **Purge:** nightly maintenance (`nightly-maintenance.py` at
   `profiles/gentech/scripts/`, cron id f1fa47f76045) purges `_archive/`
   entries older than 7 days, and archives stale OPEN notes older than 7d.
   This extends the existing >7d archive logic to the INBOX tree.

## Desktop (Forge) connection — Obsidian Sync, not a live socket
- The Windows desktop Hermes (Forge) is a **dev-only workbench**. All comms
  stay on VPS Gentech Telegram. The desktop app won't pair to the VPS backend;
  do NOT waste time on SSH/remote-gateway pairing for it.
- The shared brain is the **vault**, mirrored to Windows via **Obsidian Sync**
  (Jordan already has it configured). Point Forge at the local Obsidian folder
  path (Settings→About in Obsidian shows the absolute path); subfolders map
  directly: `01-HANDOFFS/INBOX/forge/`, `scripts/build_queue.json`, etc.
- `SETUP.md` (repo root) is Forge's onboarding: role, task loop, queue rules,
  INBOX protocol.

## Reinstall pitfall — "Restore local changes now?"
On a Hermes reinstall/update, if prompted to restore stashed local changes:
**answer No.** Those are code-level edits to the app itself, not config/memory/
skills (which live in the profile folder and are untouched). Reapplying old
local code edits onto a heavily-reworked codebase causes conflicts.

## Morning digest integration
Daily Session Reset (cron c00b01c74988, 7 AM) now:
- Reads every `01-HANDOFFS/INBOX/<group>/` open note → "📥 Handoffs for today"
- Surfaces Forge desktop tasks ("🖥️ Forge needs to do:")
- Reads `*-completions.md` + resolved inbox items → reports what shipped, by group
