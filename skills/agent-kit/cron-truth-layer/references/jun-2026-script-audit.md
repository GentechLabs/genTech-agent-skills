# Cron Script Audit — June 22, 2026

## Trigger
User saw only preflight output from AAE DeFi Monitor cron job, no actual report.
Investigation revealed `force_send` flag was set but never checked.

## Bugs Found & Fixed

### 1. `defi-lp-consolidated.py` — `force_send` never checked
- **Line 297:** `if state.get("force_send"):` existed but the main flow never reached it
- **Root cause:** High-efficiency stability override (≥70% efficiency + in range) returned before debounce logic
- **Fix:** Added `force_send` check at top of `should_send_report()`, before efficiency override

### 2. `cmc-watchlist.py` — `[SILENT]` leak
- **Line 206:** `print("[SILENT]")` when movement < threshold
- **Impact:** User saw "[SILENT]" as a Telegram message (no_agent=true)
- **Fix:** Removed print, just `return` (empty stdout = nothing delivered)

### 3. `defi-master-cron.py` — `[SILENT]` leak + hardcoded config drift
- **Lines 454, 467:** Two `print("[SILENT]")` calls
- **POOL dict:** Hardcoded range $6.30–$6.55, shape "bidirectional", position_usd $44.74
- **Actual values:** range $6.01–$6.18, shape "curve", position_usd ~$43
- **Milestones:** 4 tiers (missing Fisher at $100/day)
- **Fix:** Removed [SILENT] prints. Replaced hardcoded POOL with `load_pool_config()` reading from `.lfj-aae-config.json`. Updated milestones to 5 tiers.

## Scripts Verified Clean
- `run-reader.py` — wrapper only, no suppression logic
- `cron-health-monitor.py` — silent-when-healthy (correct watchdog pattern)
- `hub-sync-nightly.py` — always prints status
- `narrative-rotation.py` — always prints
- `fed-event-tracker.py` — silent-when-no-events (correct)
- `revenue-monitor.py` — no suppression
- `wallet-monitor.py` — always outputs JSON
- `refresh_nous_oauth_quiet_wrapper.py` — legitimate quiet hours wrapper

## Cron Jobs Audited (30 total)
All 30 jobs listed in the cron fleet. 10 have script-backed no_agent execution. The rest are agent-driven (LLM processes the prompt, no script stdout concern).

## Path Notes
- `/root/.hermes/scripts/` (global) has newer preflight.py (Jun 22) vs profile copy (Jun 20)
- State files split between global and profile dirs — not a bug but fragile
- Config file: `~/.hermes/scripts/.lfj-aae-config.json` — single source of truth for position
