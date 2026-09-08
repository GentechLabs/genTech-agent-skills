# Nightly Maintenance Script Pattern

The `nightly-maintenance.py` script runs at midnight ET (4:00 UTC) via the V4 Nightly Maintenance cron. It is a `no_agent` script — fully autonomous, no LLM reasoning.

## Purpose

Infrastructure-only tasks. Brain audit is now handled by the Nightly Build Session when the build queue is empty.

1. **Git sync** — pull remote, commit any new changes, push
2. **Handoff archive** — move handoff files older than 7 days in `01-HANDOFFS/` to `_archive/`
3. **Root cleanup** — remove stale v3 root directories that may linger after vault consolidation
4. **Git push** — stage, commit, and push any changes

## Git Sync — The Right Pattern

Wrong (broken in production):
```bash
git pull --rebase
git push
```

Right:
```bash
git stash push -m 'nightly-YYYY-MM-DD'
git pull --rebase vault main
git stash pop
git add -A
git commit -m 'Nightly maintenance YYYY-MM-DD'
git push vault main
```

**Why:** The vault has two remotes (`origin` = portfolio, `vault` = gentech-vault.git). `git pull --rebase` without arguments fails when rebasing against a divergent remote. `git push` without arguments pushes to the wrong remote.

## Handoff Path — Single Source of Truth

All handoffs live under `01-HANDOFFS/`:
- `01-HANDOFFS/gentech-to-forge/` — Forge task lists
- `01-HANDOFFS/` (root) — Jordan action items

The old path `Gentech/handoffs/gentech-to-forge/` is dead code from the vault consolidation. Any script still referencing it has a stale path bug that silently fails to clean up handoffs.

## Script Location & Cron Wiring

- **Cron copy:** `/root/.hermes/profiles/gentech/scripts/nightly-maintenance.py` (the cron reads from Hermes profile scripts)
- **Vault copy:** `/root/vaults/gentech/scripts/nightly-maintenance.py` (for git tracking)
- **Cron job ID:** `f1fa47f76045`
- **Schedule:** `0 4 * * *` (midnight ET)
- **Mode:** `no_agent=True` (pure script, no LLM)

## Update Procedure

When changing the maintenance script:

1. Edit the Hermes profile copy: `/root/.hermes/profiles/gentech/scripts/nightly-maintenance.py`
2. Copy to vault for git tracking: `cp /root/.hermes/profiles/gentech/scripts/nightly-maintenance.py /root/vaults/gentech/scripts/`
3. The cron references it by filename — no cron update needed if filename stays the same

## Verification

```bash
# Test the script locally
python3 /root/.hermes/profiles/gentech/scripts/nightly-maintenance.py

# Check cron fires correctly
cronjob(action='list')
```
