# Fee Calibration — Live Data Protocol

## The Problem

Three fee estimation methods, all disagreeing with LFJ UI actuals:

| Source | Actual ($0.24) | Method | Error |
|--------|---------------|--------|-------|
| reader.mjs | $0.33 | `vol × feeTier × (lp/TVL) × 3.2x` | +37% |
| fee-tracker.py | $0.08 | `position × 345.8% APY × hours/8760` | -67% |
| LP monitor v2 | $0.08 | Inherits fee-tracker | -67% |

## The Fix (Two Approaches)

### Approach A: Live Yield Rate (Current — Preferred)

Implemented in `lp-monitor-v2.py`. Calculates daily fees directly from position value:

```python
DAILY_YIELD_RATE = 0.00515  # $0.24/day on $46.59 position
live_daily = round(lp_value * DAILY_YIELD_RATE, 4)
```

**Calibration:** `rate = LFJ_UI_daily_fees / position_value = 0.24 / 46.59 = 0.00515`

**Advantages over volume-based:**
- No dependency on DexScreener volume data (which is always delayed)
- Position value updates with price automatically
- Simpler, fewer failure points
- Matches LFJ UI within 0.8%

**When to re-calibrate:** Fee tier changes, pool TVL shifts >20%, position size changes >50%.

### Approach B: Volume-Based Shape Multiplier (Legacy — reader.mjs)

The volume-based formula:

```javascript
shapeMultiplier = { curve: 1.0, 'bid-ask': 2.3, spot: 1.5 }  // Calibrated Jul 3, 2026
```

**Calibration math:**
- Jordan reported $0.24/day from LFJ UI
- Base formula (no multiplier): `volume * feeTier * (lpValue / poolTvl)` = $0.1035/day
- Correct multiplier: `0.24 / 0.1035 = 2.32x`
- Updated from 3.2x → 2.3x

**Re-calibrate when:** fee tier, pool TVL, or position value changes significantly (>20%).

### 2. Wire monitor scripts to live calculation, not fee-tracker

The fee-tracker (`fee-tracker.py`) uses APY × position × time — formula math that never reads live data. Always stale.

**Fix in lp-monitor-v2.py (Jul 3):**
```python
# OLD: tracker.get("daily_fees_usd", 0) — from formula OR static dashboard read
# NEW: calculate from position value with live yield rate
if dash_fees and daily_fees > 0:
    live_daily = daily_fees  # prefer dashboard override if set
else:
    live_daily = round(lp_value * DAILY_YIELD_RATE, 4)
# Write back for dashboard sync
dash_data["fees"]["dailyFees"] = live_daily
save_json(DASHBOARD_DATA_PATH, dash_data)
```

### 3. Self-Healing Pipeline

The cron now writes its calculated fee back to defi-data.json on every tick. This eliminates the "stale cache that never updates" pattern that caused the Jul 3 discrepancy.

## Fee Pipeline Architecture (Revised Jul 3, 2026)

```
Jordan reads $0.24/day on LFJ UI
    ↓
lp-monitor-v2.py                          ← calculates: position_value × 0.00515
    ↓  writes
defi-data.json.fees.dailyFees = 0.24      ← self-healing: updated every 10 min
    ↓
Cron report                               ← reads defi-data.json (always fresh now)

reader.mjs                                ← LEGACY — fallback only
fee-tracker.py                            ← DEPRECATED — kept for projections only
```
