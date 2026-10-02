---
name: obsidian-sync-fix
description: "Use when 'ob sync' says no config found."
version: 1.0.0
author: Pixel
tags: [obsidian, sync, handoff, config, xdg]
---

# Obsidian Sync Fix — $HOME/XDG config path

## When to Use
- `ob sync` / `ob sync-status` says **"No sync configuration found"** even though config exists on disk.
- Handoffs written to the vault aren't reaching other agents (they read via Obsidian sync, not git).
- `ob sync-list-local` shows "No vaults configured" but `/root/.config/obsidian-headless/sync/` has a vault folder.

## Root Cause
The `ob` CLI resolves its config dir from `$HOME` (or `XDG_CONFIG_HOME`). On this host, `$HOME` is the **profile home** (`/root/.hermes/profiles/pixel/home`), NOT `/root`. So `ob` looks in the wrong place and can't see the real config at `/root/.config/obsidian-headless/`.

## The Fix — always set XDG_CONFIG_HOME
```bash
XDG_CONFIG_HOME=/root/.config ob sync --path /root/vaults/gentech
```

## Verify config is visible
```bash
XDG_CONFIG_HOME=/root/.config ob sync-list-local
# Should show the Gentech vault, Path: /root/vaults/gentech
# The id as of 2026-10-01 is: e2c92dacc2d71cc70e7e8d315741b4cb
# If the id DIFFERS, the vault was RELINKED — that is not a failure. The Path and the
# vault name are the check; the id is the value. A hard-coded id here is what made this
# step impossible to pass once the remote was recreated (the superseded id and host are
# recorded, labelled, in the obsidian-sync runbook's WITHDRAWN banner — deliberately not
# repeated here, so that a literal audit of this file does not have to special-case it),
# and a check that cannot pass is worse than no check, because it teaches the reader to skip it.
```

## Verify a handoff actually reached Obsidian cloud
Run the sync, then grep the output for your file:
```bash
XDG_CONFIG_HOME=/root/.config ob sync --path /root/vaults/gentech 2>&1 | grep -iE "Upload complete <your-file>|Fully synced"
```
`Upload complete <file>` = delivered to Obsidian cloud (the channel other agents read).

## "Sync failed: Error: Vault limit exceeded" — the quota, not the config

Different failure, same symptom (handoffs stop arriving): `ob` connects fine, then dies on upload.

```
[..] New file <path>
[..] Uploading file <path>
[..] Sync error: {}
Sync failed: Error: Vault limit exceeded.
```

**Diagnose — does not require guessing:**
```bash
# last time it worked (the quota tripped after this)
grep "Fully synced" "$XDG_CONFIG_HOME/obsidian-headless/sync/<vaultId>/sync.log" | tail -3
# the real error (the CLI prints `Sync error: {}` — an EMPTY object; the message is one line lower)
grep -i "limit exceeded" "$XDG_CONFIG_HOME/obsidian-headless/sync/<vaultId>/sync.log" | tail -3
# what is actually consuming quota: files UNDER the per-file ceiling
find . -path ./.git -prune -o -type f -size -5000k -print0 | xargs -0 stat -c%s | awk '{s+=$1} END {printf "%.0f MB\n", s/1048576}'
```

**Key facts that decide the fix:**
- Files **over** 5 MB are *skipped by design* — they never count against quota. So a vault that looks
  huge may have a small sync bill; measure with `-size -5000k`, not `du -sh`.
- Quota is consumed by **file count and version churn**, not just bytes. A vendored `node_modules`
  (tens of thousands of small files) is the classic silent eater — it should never sit in a synced vault.
- **`Sync error: {}` is an empty object.** The real cause is the `Sync failed: Error: ...` line further
  down. Grep for that, don't trust the `{}`.

**It is a fleet/account decision, not a seat-level edit.** Deleting peer media or vendored trees to buy
quota headroom is a call Jordan owns; report the measurements and the cheapest options, delete nothing.

**Workaround while the quota is full:** git push still works. On the VPS all seats read the same
on-disk tree, so a peer on the same host still sees the file — but a **desktop seat (Forge) is cut off**,
since Obsidian is its only channel. Say which machines are affected rather than calling it "delivered".

## Pitfalls
- **git push vault is NOT the delivery channel for handoffs.** Other agents (Forge) read via Obsidian sync. A file committed+git-pushed but not Obsidian-synced is NOT delivered.
- The sync can be slow on first run (it reconciles the whole vault, including node_modules). Run with a generous timeout (180s+).
- `ob sync` is one-shot; use `--continuous` only if you want a daemon. For handoffs, run it after writing each handoff.
- The config lives at `/root/.config/obsidian-headless/sync/<vaultId>/config.json` — as of 2026-10-01 vaultId `e2c92dacc2d71cc70e7e8d315741b4cb`, vault "Gentech", host `sync-72.obsidian.md`. **The id AND the host move together when the remote vault is recreated** — the previous pair is recorded, labelled as superseded, in the obsidian-sync runbook's WITHDRAWN banner, and is deliberately not repeated here; read both live with `ob sync-list-local` rather than trusting the pair written here.

## Verification
- [ ] `XDG_CONFIG_HOME=/root/.config ob sync-list-local` shows the Gentech vault.
- [ ] After writing a handoff, `ob sync` output shows `Upload complete <file>`.
- [ ] Other agents can see the handoff in their Obsidian-synced vault.
