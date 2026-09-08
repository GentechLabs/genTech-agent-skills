# LP Monitor v2 — Config-First, Dashboard-Free Architecture

**Date:** Jun 30, 2026
**Problem:** Multiple cron jobs writing to the same dashboard JSON caused a race condition where correct data was overwritten within seconds
**Solution:** New monitor script with zero dashboard dependency

## The Race Condition (Root Cause)

Three concurrent processes wrote to `/root/ProtoJay4789.github.io/DeFi/defi-data.json`:
1. `defi-lp-consolidated.py` (LP monitor) — wrote position data
2. `run-reader.py` (on-chain reader) — wrote position data with different values
3. `hub-sync-nightly.py` — rebuilt JSON from scratch, overwriting everything

Plus THREE config files existed with different data:
```
/root/.hermes/scripts/.lfj-aae-config.json                          → CORRECT (bid-ask, $6.3792)
/root/.hermes/profiles/gentech/scripts/.lfj-aae-config.json          → STALE (curve, $6.13)
/root/.hermes/profiles/gentech/home/.hermes/scripts/.lfj-aae-config.json → STALE (wrong range)
```

`HERMES_HOME` env var in cron context = `/root/.hermes/profiles/gentech`, so scripts using `os.environ.get("HERMES_HOME")` read the STALE config.

## The Fix: lp-monitor-v2.py

**Script location:** `/root/.hermes/profiles/gentech/scripts/lp-monitor-v2.py`

**Design principles:**
1. **Hardcoded paths** — never use `HERMES_HOME` env var for config
2. **Config-first** — read ALL position data from `/root/.hermes/scripts/.lfj-aae-config.json`
3. **Zero dashboard dependency** — no reads, no writes to `defi-data.json`
4. **Live price via API** — DexScreener direct fetch
5. **Bid-ask as distinct shape** — NOT aliased to bidirectional

**Data sources:**
| Data | Source | Path/URL |
|------|--------|----------|
| Shape, range, entry price, amounts | Config | `/root/.hermes/scripts/.lfj-aae-config.json` |
| Daily fees, cumulative fees | Position tracker | `/root/.hermes/scripts/.lfj-position-tracker.json` |
| Live price, volume, liquidity | DexScreener API | `api.dexscreener.com/latest/dex/pairs/avalanche/{pool}` |
| Debounce state | State file | `/root/.hermes/scripts/.lfj-defi-state.json` |

**Efficiency formulas (3-shape system):**
| Shape | Formula | Range |
|-------|---------|-------|
| Spot | 100% always | 100% |
| Bid-ask | `50 + (center_dist * 25)` | 50% center → 75% edges |
| Bidirectional | `abs(pos - 0.5) * 2 * 100` | 0% center → 100% edges |
| Curve | `(1 - abs(pos - 0.5) * 2) * 100` | 100% center → 0% edges |

## Verification Process (develop → test → verify)

1. **Develop:** Write clean script with hardcoded paths
2. **Test:** Run `python3 lp-monitor-v2.py` manually
3. **Verify:** Check ALL output fields against expected values:
   - Shape: BID-ASK ✅
   - Entry price: $6.3792 ✅
   - Position amounts: 3.2630 AVAX + 27.27 USDC ✅
   - Range: $6.3656 – $6.5856 ✅
   - Live price: from DexScreener ✅
   - Efficiency: 50-75% range ✅
4. **Troubleshoot:** If wrong, trace data source (config vs tracker vs API)
5. **Present:** Show verified output to user

## Cron Job Details

| Field | Value |
|-------|-------|
| Job ID | `92c52122abab` |
| Name | LP Monitor v2 — Config-First (10min) |
| Schedule | `3,13,23,33,43,53 6-22 * * *` |
| Script | `lp-monitor-v2.py` |
| no_agent | true (script-only, no LLM needed) |
| Deliver | telegram:-1002916759037 (Strategies group) |

## Key Lesson

> When multiple scripts write to the same file, eliminate the shared file dependency rather than trying to coordinate writes. File locks and read-only flags are band-aids; removing the dependency is the cure.

## Reusable Pattern

This architecture applies to ANY monitoring cron job that had data corruption from concurrent writers:

1. Identify the single source of truth (config file)
2. Write a self-contained script that reads ONLY from that source + live APIs
3. Eliminate all reads/writes to shared intermediate files
4. Hardcode paths — don't rely on env vars that differ between contexts
5. Test the actual output before deploying
