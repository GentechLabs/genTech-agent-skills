# Out-of-Range Recovery Protocol

When the position falls out of range (price below floor or above ceiling), several pipeline components need manual correction before the monitor produces reliable output again.

## Fee Projection During Out-of-Range

**Critical rule:** When `not in_range`, fee projections **must** show $0.00, not a live-volume estimate. Projecting fees on volume you aren't capturing is misleading.

### The Fix (lp-monitor-v2.py)

```python
# WRONG — projects fees even when position can't capture them
if liquidity > 0 and volume_24h > 0:
    pool_share = lp_value / liquidity
    total_fees_24h = volume_24h * POOL_FEE_RATE
    live_daily = total_fees_24h * pool_share * CONCENTRATION_MULTIPLIER

# CORRECT — zero out fees when out of range
if not in_range:
    live_daily = 0.0
elif liquidity > 0 and volume_24h > 0:
    pool_share = lp_value / liquidity
    total_fees_24h = volume_24h * POOL_FEE_RATE
    live_daily = total_fees_24h * pool_share * CONCENTRATION_MULTIPLIER
```

**Same rule applies to yield-rate fallback.** After the out-of-range check, the fallback should also be skipped:
```python
if not in_range:
    live_daily = 0.0
elif liquidity > 0 and volume_24h > 0:
    ...
else:
    live_daily = round(lp_value * DAILY_YIELD_RATE, 4)  # only when in range
```

**Verification:** After fixing, run the script and check `Daily: $0.0000` in the report output.

## State File Staleness Recovery

When the `.lfj-defi-state.json` file hasn't been updated for days (e.g., because cron was paused or quiet hours prevented reports), the debounce/silence logic operates on stale data and won't fire fresh detection cycles.

### Symptoms
- Previous `last_price` differs from current price by >$0.50
- `last_in_range` is `true` but the position is now out of range
- `last_check` timestamp is days old
- Silent period timers (`silence_until`) don't fire because the low-efficiency counters are never incremented

### Fix

Reset BOTH global and profile state files with current data:

```python
# /root/.hermes/scripts/.lfj-defi-state.json  (global — script reads this)
# /root/.hermes/profiles/gentech/scripts/.lfj-defi-state.json  (profile — backup)
{
  "last_price": 6.48,                  # current AVAX price
  "last_efficiency": 0,                # 0 if out of range, or actual %
  "last_in_range": false,              # match reality
  "last_check": "2026-07-17T08:20:00.000000-04:00",
  "efficiency_low_start": null,        # clear timers
  "efficiency_low_total": 0,
  "silence_until": null
}
```

After reset, the next monitor run starts a fresh detection cycle:
- First tick: triggers `OUT_OF_RANGE` alert immediately (no debounce)
- Subsequent ticks: debounce logic operates from a clean baseline

## Dashboard Data Sync When Out of Range

The dashboard (`defi-data.json`) may have stale range data if it wasn't updated after the rebalance that caused the out-of-range condition. Update these fields:

| Section | Fields to Update | Notes |
|---------|-----------------|-------|
| `currentPrice` | Set to current AVAX price | From DexScreener or Pyth |
| `lpPosition` | `rangeMin`/`rangeMax`, `currentPrice`, `inRange`, `avaxAmount`, `usdcAmount`, `totalValue` | Match config source of truth |
| `hero` | `rangeMin`/`rangeMax`, `currentPrice`, `rangeStatus`, `efficiency`, `dailyFees` | Must match lpPosition |
| `fees` | `dailyFees` | Set to 0 when out of range |
| `strategyAdvisor` | `recommendedAction`, `efficiencyZone`, `riskLevel`, `riskNote` | Reflect out-of-range state |
| `ilCalculator` | `currentPrice`, `entryPrice`, `positionUsd` | For accurate IL display |
| `positionLifecycle` | `currentEntryDate`, `daysInPosition`, `lastRangeKey` | Can be lost during manual sync |

### PositionLifecycle Restoration

The `positionLifecycle` key can be dropped during manual dashboard edits because it's separate from the main data flow and not touched by the monitor script. If missing during an out-of-range fix:

```json
{
  "positionLifecycle": {
    "currentEntryDate": "2026-07-03",
    "daysInPosition": 14,
    "lastRangeKey": "6.7861-7.0067",
    "rebalanceHistory": [
      {
        "entryDate": "2026-06-20",
        "exitDate": "2026-07-03",
        "daysActive": 13,
        "range": "6.2897-6.4747"
      }
    ]
  }
}
```

Estimate `daysInPosition` from the last rebalance date; `currentEntryDate` should match the most recent `range_low/range_high` entry date from the config.

## Full Recovery Sequence (Jul 17, 2026 Worked Example)

Given: price $6.48, config range $6.7861–$7.0067, state stale since Jul 5.

1. **Fetch live price** → DexScreener or Pyth ($6.48)
2. **Verify config is source of truth** → Check `.lfj-aae-config.json` has correct range + amounts
3. **Sync dashboard** → Update all fields in the table above
4. **Reset state files** → Both global + profile paths
5. **Sync script to global path** → `cp` profile to `/root/.hermes/scripts/`
6. **Run monitor manually** → Verify OUT_OF_RANGE detected, fees $0, IL correct
7. **Resume cron** → Confirm next scheduled tick produces clean output
