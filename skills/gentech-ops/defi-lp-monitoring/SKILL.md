---
name: defi-lp-monitoring
description: "DeFi LP position monitoring — shape-aware efficiency, data flow across config/reader/hub/rainbow, and rebalance sync protocol."
tags: [defi, lp, monitoring, lfj, avalanche]
related_skills:
  - agent-coordination
  - gentech-hub
---

# DeFi LP Monitoring

Live LP position monitoring for LFJ AVAX/USDC on Avalanche. Covers data flow, shape-aware calculations, and rebalance synchronization.

## Position Lifecycle Tracking (Jul 3, 2026)

Every rebalance records entry/exit dates for macro pattern analysis (e.g., "Bitcoin bottom ~1000 days"). Data lives in `defi-data.json.positionLifecycle`:

```json
{
  "currentEntryDate": "2026-07-03",
  "daysInPosition": 1,
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
```

**How it works:**
- `reader.mjs` compares `lastRangeKey` from previous run against current range
- On range change → pushes old entry to `rebalanceHistory`, resets `currentEntryDate`
- `daysInPosition` = time since current entry date
- Rebalance history kept at last 20 entries

**Macro use:** Track position duration vs macro events. Jordan references Oct 5th cycle bottom theory — lifecycle data makes it queryable.

## Fee Calibration — Keeping Estimates Honest

The reader's fee estimate (`fees.dailyFees` in defi-data.json) uses a calibrated volume-based formula. **How to calibrate:**

1. Jordan reads actual daily fee from LFJ UI (e.g. "$0.24/day")
2. Run base formula manually: `volume_24h * (feeBps/10000) * (lp_value / pool_tvl)`
3. Calculate: `correct_multiplier = actual_fees / base_formula_result`
4. Update `shapeMultiplier` in `reader.mjs` lines 222-233
5. Also update `apy_override` in `fee-tracker-config.json`: `APY = actual_fees * 365 / position_value * 100`
6. Verify by re-running reader and checking output

**Reference:** `references/fee-calibration.md` for full pipeline diagram and math.

## Cron Script Path: Global vs Profile (Critical Pitfall)

The `lp-monitor-v2.py` script explicitly reads from `/root/.hermes/scripts/` (the **global** path), NOT the profile path:

```python
# ALWAYS use /root/.hermes/scripts/ — NOT the profile path
HOME_SCRIPTS = "/root/.hermes/scripts"
```

This is a deliberate design choice to avoid overwrite conflicts. **When fixing config after a rebalance:**
- ✅ Update profile config: `/root/.hermes/profiles/gentech/scripts/.lfj-aae-config.json`
- ✅ **ALSO** update global config: `/root/.hermes/scripts/.lfj-aae-config.json`
- ✅ **ALSO** update both position tracker paths

Failing to update the global path = cron reports stale data indefinitely.

**Files the cron reads from (non-obvious):**
| File | Path | What it provides |
|------|------|-----------------|
| Global config | `/root/.hermes/scripts/.lfj-aae-config.json` | range, shape, position amounts |
| Global tracker | `/root/.hermes/scripts/.lfj-position-tracker.json` | entry price (fallback) |
| Dashboard | `/root/ProtoJay4789.github.io/DeFi/defi-data.json` | fee estimates (calibrated) |

## Fee Pipeline: Architecture Summary

```
reader.mjs (--shape) → defi-data.json (primary fee source)
    ↕ calibrated via Jordan's LFJ UI reports
lp-monitor-v2.py → reads from defi-data.json (dashboard)
fee-tracker.py → DEPRECATED for live reads, kept for projections
```

**Data flows one way:** Reader writes → Dashboard stores → Monitor reads. No circular dependencies, no overwrite conflicts.

## Data Flow Architecture (Revised Jul 3, 2026)

Includes position lifecycle tracking and calibrated fee estimates. See `references/fee-calibration.md` for the full pipeline diagram.

When Jordan rebalances, the change must propagate through this chain:

```
Jordan rebalances on LFJ UI
    ↓
1. .lfj-position-tracker.json  ← SOURCE OF TRUTH for shape, range, amounts
    ↓
2. .lfj-aae-config.json        ← mirrors position tracker
    ↓
3. On-chain reader (run-reader.py) → reads shape from position tracker
    ↓
4. defi-data.json               ← reader writes shape + calculated efficiency
    ↓
5. Hub DeFi tab                 ← reads from defi-data.json
6. Rainbow data                 ← consolidated monitor writes BOTH locations:
   ├→ scripts/yield-rainbow-data.json       (local tools)
   └→ GitHub Pages/rainbow/yield-rainbow-data.json  (dashboard HTML)
7. Consolidated monitor script  ← reads from config + state + DexScreener
```

**Critical:** The position tracker (step 1) is the source of truth. If it's not updated, everything downstream gets the wrong shape.

**Dual-path write (step 6):** The consolidated monitor writes rainbow data to BOTH the scripts directory AND the GitHub Pages `rainbow/` directory. The dashboard HTML reads from GitHub Pages via relative path. If you only write to one location, the other goes stale. See `RAINBOW_OUTPUT_PATH` and `RAINBOW_DASHBOARD_PATH` in `defi-lp-consolidated.py`.

## Shape-Aware Efficiency (BIN-WEIGHTED)

**CRITICAL FIX (Jul 4, 2026):** The simplified efficiency model capped bid-ask at 75% and was inaccurate at range edges. The correct bin-weighted model accounts for how LFJ actually distributes liquidity.

### Correct Formulas

| Shape | Efficiency Behavior | Formula | Range |
|-------|---------------------|---------|-------|
| **Bid-Ask** | Peaks at edges (100%), valley at center (50%) | `50 + dist_from_center` | 50-100% |
| **Curve** | Flat across range, higher in middle | `60 + dist_from_edge * 80` | 60-100% |
| **Spot** | Always at peak | `100` | 100% |
| **Out of Range** | No fee capture | `0` | 0% |

Where:
- `pos = (price - rangeLow) / (rangeHigh - rangeLow)` (0 = low edge, 1 = high edge)
- `dist_from_center = abs(pos - 0.5) * 100` (0 = center, 50 = edge)
- `dist_from_edge = min(pos, 1 - pos)` (0 = edge, 0.5 = center)

### Edge Behavior Examples

| Position in Range | OLD Formula (Capped) | NEW Formula (Bin-Weighted) |
|-------------------|---------------------|----------------------------|
| Edge (0% or 100%) | 75% | **100%** (bid-ask), 60% (curve) |
| Near edge (10% or 90%) | 55% | **90%** (bid-ask), 68% (curve) |
| Center (50%) | 50% | 50% (bid-ask), **100%** (curve) |

### The Pitfall: Bid-Ask "Between Edges" = 0% Efficiency

**Jordan's correction (Jul 19, 2026):** The bin-weighted formula is correct when price is AT an edge. But with bid-ask on LFJ V2.2, ALL liquidity sits at the two edge bins. If price lands BETWEEN the bid and ask edges, **no bins are being crossed** → 0% fee efficiency regardless of what the position-based formula says.

Example from Jul 19: Range $6.3656–$6.5856, price $6.57, bid-ask shape. Position formula computed 93% efficiency (near high edge). But Jordan said 0% — because the capital was deployed at the two extreme edges ($6.3656 and $6.5856), and $6.57 sat between them with no bin cross.

**When to trust the formula vs Jordan's signal:**
- If reader reports "In Range" AND active bins > 0 AND the reader's efficiency is non-zero → trust bin-weighted formula
- If reader reports "In Range" but Jordan says 0% efficiency → trust Jordan. The formula overestimates when price is between the concentrated edge bins
- **Fix:** When Jordan corrects efficiency to 0%, update the dashboard AND acknowledge the reader's estimate is wrong for the current price position

**This is a reader limitation:** The reader calculates efficiency based on overall range position, not on whether price is actively crossing the specific edge bins where liquidity sits. A future improvement would be to read per-bin liquidity and determine which bins are actually being crossed.

**OLD simplified model:**
```python
# WRONG — capped at 75%, inaccurate at edges
center_dist = abs(pos - 0.5) * 2
efficiency = 50 + (center_dist * 25)  # Max 75%
```

**NEW bin-weighted model:**
```python
# CORRECT — bid-ask peaks at 100% edges
dist_from_center = abs(pos - 0.5) * 100
efficiency = 50 + dist_from_center  # Max 100%
```

**Why it matters:** When price is at $7.0066 and range top is $7.0067, you're literally on the edge. Old model said 75%, new model correctly says 100%. Jordan caught this: "The only thing I would say is the efficiency should be much, much higher than 75%."

### Implementation

**All scripts calculating efficiency must use the bin-weighted model:**
```python
def calc_efficiency(price, range_low, range_high, shape):
    """
    Calculate fee-capture efficiency based on LP shape.
    BIN-WEIGHTED: bid-ask peaks at edges (100%), valley at center (50%).
    """
    pos = (price - range_low) / (range_high - range_low) if (range_high - range_low) > 0 else 0.5
    
    # Out of range = 0% efficiency
    if price < range_low or price > range_high:
        return 0.0
    
    # Shape-aware efficiency
    if shape == "spot":
        return 100.0
    elif shape == "bid-ask":
        # Bid-ask: concentrated on edges, valley at center
        # Efficiency = 50% + (distance_from_center * 50%)
        # At edges (0% or 100% position): 100% efficiency
        # At center (50% position): 50% efficiency
        dist_from_center = abs(pos - 0.5) * 100
        return round(50 + dist_from_center, 1)
    elif shape == "bidirectional":
        # Bidirectional: peak at center
        return round(max(0, min(100, pos * 100)), 1)
    else:  # curve
        # Curve: flat distribution, higher in middle
        dist_from_edge = min(pos, 1 - pos)
        return round(min(100, 60 + dist_from_edge * 80), 1)
```

**Files updated (Jul 4, 2026):**
- `/root/.hermes/scripts/lp-position-reader.py` — bin-weighted calculation
- `/root/.hermes/profiles/gentech/scripts/lp-monitor-v2.py` — bin-weighted calculation

## Data Source Priority (Jordan's Rule, Jun 24, 2026)

**On-chain reader is PRIMARY. Screenshots are FALLBACK.**

| Priority | Source | When to Use |
|----------|--------|-------------|
| 1 | On-chain reader (run-reader.sh) | Always — auto-corrects config drift |
| 2 | DexScreener overlay | Live price + pool stats |
| 3 | Screenshot (LFJ UI) | Only if reader fails or Jordan sends one |

**The reader auto-corrects:**
- Range (detects drift between config and on-chain)
- Balances (AVAX + USDC amounts)
- Shape (from bin distribution)
- Entry price (from transaction history in defi-data.json)

**When Jordan sends a screenshot:**
- Use it to VERIFY on-chain data, not as primary input
- If reader and screenshot disagree, trust the reader
- Only manually update if reader is broken

## Rebalance Sync Protocol

When Jordan rebalances (detected by on-chain reader or screenshot):

1. **On-chain reader detects change** → writes fresh `defi-data.json` (auto-commits + pushes to GitHub)
   ⚠️ Reader does NOT update the position tracker or AAE config. These must be synced manually (step 3).
2. **If reader fails:** Extract from screenshot → update position tracker manually
3. **Update config + tracker** — Mirror on-chain data to both `.lfj-aae-config.json` and `.lfj-position-tracker.json` (profile + global paths). The reader's `defi-data.json` has the correct on-chain amounts and range, but the tracker files drive the monitor cron.
4. **Sync BOTH paths** — profile + global (see Dual-Path Sync section)
5. **Resolve git divergence** — If reader push was rejected (divergent branches), follow `references/git-divergence-resolution.md`
6. **Verify:** Check next monitor cron output matches on-chain data

**Entry price tracking:**
- Entry price changes on each rebalance
- Read from transaction history in `defi-data.json` (transactions array)
- Last recorded entry is the source of truth
- IL calculation: `((current_price - entry_price) / entry_price) * 100`

## Dual-Path Sync (Profile vs Global)

**Pitfall:** Hermes runs from `/root/.hermes/profiles/gentech/` but the position tracker also exists at `/root/.hermes/scripts/`. Jordan's manual rebalances update the GLOBAL path, but cron scripts read from the PROFILE path. If they drift, the monitor reports stale ranges and false "OUT OF RANGE" alerts.

**Fix:** The `sync_tracker()` and `sync_config()` helper functions in `defi-lp-consolidated.py` write to BOTH paths simultaneously:
```python
def sync_tracker(data: dict):
    """Write position tracker to BOTH profile and global paths."""
    for path in [PROFILE_TRACKER_PATH, GLOBAL_TRACKER_PATH]:
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
```

**When rebalancing manually:** Always update BOTH `.lfj-position-tracker.json` files, or the next cron run will report with stale data.

**Implementation:** See [references/dual-path-sync-implementation.md](references/dual-path-sync-implementation.md) for the `sync_tracker()` and `sync_config()` function bodies and where to wire them in.

## Shape Decision Framework — Jordan's Rule (Jul 22, 2026)

**Curve is the default. Always.** Spot is overrated — people recommend it for bull runs, but bull runs are rare. 90% of the time we're in chop or mild trends, and Curve is simply better for that.

| Shape | When | Why |
|-------|------|-----|
| **Curve** | **Default — always** | Starts at peak efficiency, degrades gracefully. Best for chop, ranging, and mild trends. |
| **Spot** | Rare — only in confirmed directional moves | Peak efficiency but narrow. Falls off a cliff if price moves wrong. |
| **Bid-Ask** | Macro events (Fed, CPI, NFP) | Captures volatility on both sides. |

### The Regime Switch — From Command Center to War Room

Two modes:

1. **Accumulation Mode (default)** — Curve, farm fees, compound, DCA. The command center tracks everything, alerts on issues, but we're not betting directionally.

2. **Bull Mode (triggered)** — Buy and hold the asset. Stop farming fees and start accumulating the token itself. The command center becomes a war room — tracking entries, exits, position sizing.

**The trigger question** — when do we switch? Signals to watch:
- CLARITY Act passes → structural green light
- Tariff pivot → macro headwind removed
- BTC breaks and holds above a key level
- Global regulatory race accelerates (Russia Sep 1, Japan expanding, etc.)

When enough of those line up, flip the switch. Until then, Curve is the right call.

### On-Chain Reader is Source of Truth for Range (Jul 22, 2026)

**Jordan's explicit rule:** "No wrong range. Check on chain data." The on-chain reader is the authoritative source for range detection. Screenshots are fallback only. When the reader works, trust it over the UI.

**Protocol:**
1. Run on-chain reader → get active bin, bin distribution, reserves
2. Compute range from bin IDs using the price formula: `(1 + binStep/10000) ^ (id - 2^23) * 10^12`
3. Update config files with the on-chain verified range
4. If reader fails (RPC revert), fall back to screenshot

**Pitfall:** The LFJ UI shows 149 bins in the slider by default, but the actual deployed position may have far fewer (e.g. 21 bins). The UI shows the available range, not what's actually active. Always verify with on-chain data.

## AAE Regime-Switching Strategy — CURVE vs Bid-Ask (Jul 19, 2026)

**Core thesis:** The market has two distinct regimes. Each demands a different liquidity shape. The Agentic Treasury should detect the regime and switch automatically.

### Regime 1: Chop / No Direction (Default → CURVE)

- **When**: Between macro events, consolidation, priced-in anxiety, low volatility
- **Shape**: CURVE (wide distribution across range)
- **Behavior**: Set and forget. All bins earn as price oscillates within range.
- **Why**: No clear directional bias. Bid-ask would sit in the dead zone between edges and earn 0%.
- **Jordan's call**: "Markets are not dropping dropping fast right now, just chop. Cooling from the recent pump."

### Regime 2: Macro Event (Fed / CPI / NFP → Bid-Ask)

- **When**: 24h before Fed meetings, CPI/NFP releases, major data
- **Shape**: Bid-Ask (concentrated at two edges)
- **Behavior**: Price moves hard one direction → one edge catches it → peak efficiency
- **Why**: You know the direction of risk (usually risk-off for macro surprises). No point spreading liquidity across a range when 90% of the action is at one edge.
- **Jordan's call**: "Bid ask is perfect for fed meetings and macro data coming out"
- **Next event**: FOMC Jul 29-30 — switch to bid-ask by Jul 28 EOD

### Execution Plan

1. Fed event tracker cron checks macro calendar daily (already exists as `fed-event-tracker.py`)
2. 24h before FOMC/CPI/NFP → auto-switch config to bid-ask at current macro-relevant range
3. 24h after event settles → auto-switch back to CURVE
4. Manual override always available (Jordan sets shape directly on LFJ)

### Strategy Document

Full spec saved at: `/root/vaults/gentech/03-Strategies/aae-regime-switching.md`

### Tactical Retreat — Active Defense Loop

**Phase 1 spec:** `references/tactical-retreat.md` — breakout detection + 2-5 min timer wired into the LP monitor. The full loop: deploy → breakout → hold → retreat to USDC → sentinel → re-enter on signals. Phase 1 is the first build target for Labs.

### Pitfall: Reader Shape Default

The on-chain reader (`run-reader.sh`) has a hardcoded shape default:
```bash
SHAPE="${SHAPE:-bid-ask}"
```

This used to default to `curve` — if it's still showing "Curve" in reader output after Jordan switched to bid-ask, update this env default in the shell script. Fixed Jul 19, 2026.

## Macro Event Integration

The Fed event tracker (`fed-event-tracker.py`) now includes impact analysis for each event:
- **Crypto volatility range** (BTC + altcoin expected move)
- **Direction** (what each scenario means for risk assets)
- **Rainbow zone shift** (how the event could move the yield spectrum)
- **Typical AVAX move** (historical range)

Each event in `EVENT_IMPACT` dict maps to a full impact profile. The output shows analysis for today's and tomorrow's events plus a position reminder.

**Warsh era context:** New Fed Chair doesn't telegraph. FOMC meetings are HIGH VOLATILITY. PCE/CPI prints hit harder. Rainbow zone can shift 2+ bands in a single day.

## Key Levels Engine

Added to `defi-lp-consolidated.py` — every report now shows:

**📍 Key Levels to Watch:**
- **Range Floor** — first support level, price approaching from above
- **Range Ceiling** — first resistance level, price approaching from below
- **Rebalance Trigger (Below)** — 15% below floor, automatic rebalance zone
- **Rebalance Trigger (Above)** — 15% above ceiling, automatic rebalance zone
- **Distance %** — how far current price is from each level (as % of range width)

**Proximity zones:**
- `🟢 CENTER` — price within 15% of range midpoint, no action needed
- `🟡 IN RANGE` — in range but off-center, monitor for drift
- `⚠️ NEAR LOWER EDGE` — within 15% of floor, watch for bounce or break
- `⚠️ NEAR UPPER EDGE` — within 15% of ceiling, watch for rejection or break
- `🔴 BELOW/ABOVE RANGE` — broken through, rebalance immediately

**⚠️ Rebalance Advice** — only appears when urgency != none:
- `WATCH` — near edge, pre-planned range ready in case of break
- `IMMEDIATE` — out of range, specific range + shape recommendation provided

## Consolidation Time Tracking

Price near an edge for 5 minutes ≠ price near an edge for 2 hours. The script tracks how long price has been sitting near an edge:

| Phase | Duration | Meaning |
|-------|----------|---------|
| `⏱️ EARLY (<15m)` | 0-15 min | Just arrived at edge. Too early to act. |
| `🟡 WATCHING (30m+)` | 15-60 min | Consolidation forming. Monitor for direction. |
| `🟡 MATURE (1h+)` | 1-2 hours | Breakout likely soon. Be ready to rebalance. |
| `🔴 CRITICAL (2h+)` | 2+ hours | Extended consolidation. Next move = rebalance now. |

**How it works:** State tracks `edge_start` timestamp and `edge_direction` (low/high). Timer resets when:
- Price moves back to range center (>15% from both edges)
- Price switches to the opposite edge
- A new edge event starts

**Practical use:** If price has been consolidating at the floor for 2 hours, the next breakout move is a rebalance signal — not a "wait and see" situation. Extended consolidation means the market has decided where it wants to go.

## Fee Velocity vs Static Efficiency (Jun 25, 2026)

**Key insight from live trading:** "Efficiency is a snapshot. Fees are a function of movement." — Jordan

The efficiency metric measures WHERE price sits in the range. But fee income is driven by HOW MUCH price moves through the bins. A position at 29% efficiency with high volatility can earn 7× more than a position at 88% efficiency with no movement.

| Scenario | Efficiency | Volatility | Fee Generation |
|----------|-----------|------------|----------------|
| Static at center | 88% | Low | Low (no bin crossings) |
| Volatile at edge | 29% | High | **High** (constant ticks) |

**Why this matters:** The rainbow zone shows efficiency bands, but LP farmers should also consider volatility when picking ranges. A "Bleeding Edge" zone with high volatility can out-earn a "Harvest Mode" zone that's flat.

**Jordan's thesis:** "They're head hunting longs/shorts with these moves, but we're farming the chaos they create."

## Fee Estimation Strategy — Live Yield Rate + Calibrated Volume

**Priority chain (revised Jul 22, 2026):**
1. **LFJ UI ground truth** — used to calibrate yield rate (Jordan reads actual, we derive the rate)
2. **Live yield-rate calculation** → `lp-monitor-v2.py` calculates daily rate from position value
3. **Fee History Tracker** → `.lfj-fee-history.json` stores daily snapshots for accurate week/month/year totals
4. **Dashboard cache** → `defi-data.json.fees.dailyFees` — updated every cron tick by lp-monitor-v2.py
5. **Volume-based estimate** → fallback calculation when position value unavailable

### Fee History Tracker (Jul 22, 2026)

**Jordan's request:** Replace projection-based fee trajectory ("$0.11/day rate → $3.42/month projected") with actual accumulated data from on-chain or Trader Joe. Replace ATH with rank.

**Implementation in `lp-monitor-v2.py`:**

```python
FEE_HISTORY_PATH = os.path.join(HOME_SCRIPTS, ".lfj-fee-history.json")

def update_fee_history(daily_rate):
    history = load_json(FEE_HISTORY_PATH, {"days": []})
    today = now_et().strftime("%Y-%m-%d")
    for day in history["days"]:
        if day["date"] == today:
            day["daily_fees"] = round(daily_rate, 4)
            break
    else:
        history["days"].append({"date": today, "daily_fees": round(daily_rate, 4)})
    history["days"] = history["days"][-400:]
    save_json(FEE_HISTORY_PATH, history)
    return history

def compute_fee_totals(history):
    days = history.get("days", [])
    today_entry = next((d for d in days if d["date"] == today_str), None)
    daily = today_entry["daily_fees"] if today_entry else 0.0
    week = sum(d["daily_fees"] for d in days[-7:])
    month = sum(d["daily_fees"] for d in days[-30:])
    year = sum(d["daily_fees"] for d in days[-365:])
    return round(daily, 4), round(week, 2), round(month, 2), round(year, 2)
```

**Report format change:**
```
# BEFORE (projections):
📈 Fee Trajectory
  Daily:    $0.1141 rate
├─ Week:    $0.80
├─ Month:   $3.48
├─ Year:    $41.68 projected
└─ ATH:     $5.00

# AFTER (actuals + rank):
📈 Fee Trajectory
  Daily:    $0.1141
├─ Week:    $0.11
├─ Month:   $0.11
├─ Year:    $0.11
└─ Rank:    Tier 0 — Grunt ($10.0/day next) [1%]
```

**Note:** Week/Month/Year show low numbers initially since tracking starts fresh. After 7+ days of data, they reflect real accumulated fees.

**Live yield-rate method (added Jul 3, 2026):**
```python
# In lp-monitor-v2.py — calibrated to LFJ UI
DAILY_YIELD_RATE = 0.00515  # $0.24/day on $46.59 position
# Use position value for live calculation
if dash_fees and daily_fees > 0:
    live_daily = daily_fees  # prefer dashboard override
else:
    live_daily = round(lp_value * DAILY_YIELD_RATE, 4)
# Write back to defi-data.json for dashboard sync
```

**Why this is better:** The old volume-based method depended on DexScreener volume data, which could be stale or incomplete. The yield-rate method uses the position value (which updates with price) × a calibrated percentage. It's simpler, more reliable, and matches LFJ UI within 0.8%.

**Calibrating the yield rate:**
```
rate = LFJ_UI_daily / position_value
     = $0.24 / $46.59
     = 0.00515  (0.515% per day)
```
Re-calibrate when fee tier changes, pool TVL shifts >20%, or position value changes >50%.

**⚠️ Out-of-range override:** If the position is out of range, fee projections must show $0 regardless of volume or yield rate. The `lp-monitor-v2.py` script checks `not in_range` before any fee calculation. See `references/out-of-range-recovery.md` for the implementation pattern.

**Calibration method** (legacy — for the volume-based estimator in reader.mjs):
- reader.mjs uses `volume_24h * feeBps * (lpValue/poolTVL) * shapeMultiplier`
- shapeMultiplier for bid-ask was calibrated from 3.2x → **2.3x** based on Jordan's $0.24/day LFJ UI report
- Re-calibrate when fee tier, pool TVL, or position value changes significantly (>20%)

## Milestone/Tier Structure (Jul 3, 2026)

**Tier 0 = Grunt at $5/day.** The cron script hardcodes this as the baseline:

```python
grunt_tier = {"tier": 0, "label": "Grunt", "daily_fees": 5.0, 
              "description": "Activation threshold — $5/day"}
```

Config milestones start at Tier 1 (Recruit at $10/day) through Tier 39 (Divine IV at $200/day). The `get_milestone()` function:
- Returns Tier 0 = Grunt for any daily fees below $5
- Returns the next config milestone when fees exceed $5
- Progress percentage = `current_fees / next_target * 100`

**Dashboard view** (`defi-data.json.feeMilestones.tiers`):
| Tier | Label | Target | Unlocks |
|------|-------|--------|---------|
| 0 | Grunt 🪖 | $5/day | Activation — basic fee generation |
| 1 | Scout 🔭 | $10/day | Entry strategies (CURVE) |
| 2 | Raider ⚔️ | $20/day | SPOT + BIDIRECTIONAL shapes |
| 3 | Warlord 👑 | $50/day | Multi-pool positions |
| 4 | Sovereign 🏰 | $100/day | Custom strategy + mentorship |

**Pitfall:** There are TWO milestone systems — the dashboard's 5-tier array and the config's 39-tier array. The cron script's `get_milestone()` reads from the CONFIG milestones for the "Next" display line. If you update one but not the other, the report shows wrong next-target numbers.

## Pipeline Audit Methodology (Jul 3, 2026)

When fee numbers are wrong and the cause isn't obvious, use this structured audit:

**1. Trace end-to-end** — Read every file in the pipeline path. For the fee system: cron script → defi-data.json → reader script → config → position tracker.

**2. Run the cron manually** — Execute the script directly, check its output. If it reads from a static cache (defi-data.json fees field), verify THAT file's content.

**3. Audit with a strong reasoning model** — Jordan specifies GLM 5.2 (zai/glm-5 via BlockRun) for pipeline audits. Feed the full script + data file contents into the model and ask it to trace the calculation chain. The model spots stale-input problems that look like logic bugs.

**4. Fix the root, not the symptom** — The cron output was wrong, but the cron was correct. The input file (defi-data.json) had stale data. Fixing the cron would miss the real problem.

**5. Write back** — After fixing, make the pipeline self-healing: the cron should write its calculated value back to the cache file so the next tick has fresh data. Eliminate the "stale cache that never updates" pattern.

**6. Single step repair** — Don't change 3 things and test once. Change one thing, test, verify. The test IS the verification — run the script and check output.

See `references/pipeline-audit-methodology.md` for a worked example using the Jul 3, 2026 fee discrepancy.

See `references/fee-calibration.md` for the full pipeline diagram and calibration math.

**Key insight from live trading:** "Efficiency is a snapshot. Fees are a function of movement." — Jordan

The efficiency metric measures WHERE price sits in the range. But fee income is driven by HOW MUCH price moves through the bins. A position at 29% efficiency with high volatility can earn 7× more than a position at 88% efficiency with no movement.

| Scenario | Efficiency | Volatility | Fee Generation |
|----------|-----------|------------|----------------|
| Static at center | 88% | Low | Low (no bin crossings) |
| Volatile at edge | 29% | High | **High** (constant ticks) |

**Why this matters:** The rainbow zone shows efficiency bands, but LP farmers should also consider volatility when picking ranges. A "Bleeding Edge" zone with high volatility can out-earn a "Harvest Mode" zone that's flat.

**Jordan's thesis:** "They're head hunting longs/shorts with these moves, but we're farming the chaos they create."
The cron report must always label the source. See `references/live-fee-estimation.md` for why the deprecated Heroku `joe-api-v2` endpoint is dead, how the DexScreener proxy is computed, and why the tracker hardcoded `$0.201` caused the July 2026 mismatch against Trader Joe's `$0.35` UI value.

**Key insight from live trading:** "Efficiency is a snapshot. Fees are a function of movement." — Jordan

The efficiency metric measures WHERE price sits in the range. But fee income is driven by HOW MUCH price moves through the bins. A position at 29% efficiency with high volatility can earn 7× more than a position at 88% efficiency with no movement.

| Scenario | Efficiency | Volatility | Fee Generation |
|----------|-----------|------------|----------------|
| Static at center | 88% | Low | Low (no bin crossings) |
| Volatile at edge | 29% | High | **High** (constant ticks) |

**Why this matters:** The rainbow zone shows efficiency bands, but LP farmers should also consider volatility when picking ranges. A "Bleeding Edge" zone with high volatility can out-earn a "Harvest Mode" zone that's flat.

**Future product direction:** Volatility-mapped rainbow zone — overlay ATR/std dev on the efficiency chart. Shows which price zones have the most movement. Users pick ranges where volatility is highest, not just where efficiency looks good.

**Jordan's thesis:** "They're head hunting longs/shorts with these moves, but we're farming the chaos they create."

## LFJ Platform Constraint

LFJ (Trader Joe) concentrated liquidity does NOT let you choose an entry price. You deposit at the current market price and set your range around it. This means:

- You can't "buy the dip" and LP at the same time
- The "yield entry order" concept (deploy LP when price hits $X) would need to be built as a separate automation layer on top of LFJ
- When price is at a level you don't like, your options are: (a) wait for price to come to you, or (b) deposit now and rebalance later

This constraint is why the regime detection + auto-switch concept matters — you adapt your shape to wherever price is, rather than trying to pick your entry.

## Shape Strategy: Narrow vs Wide

Bid-ask width tradeoff differs from curve:

**Curve:** Wider = more coverage, price can move further before going out of range. Taller = deeper bins = more fees when price sits in center.

**Bid-ask:**
- **Narrow** = peaks close together → more frequent fee captures on bounces, but price exits range quickly if it trends
- **Wide** = peaks far apart → fewer fees per touch, but survives bigger swings
- **Narrow** is better for small positions ($64) in sideways markets
- **Wide** needs more capital to fill bins effectively

At small position sizes, you can't be both tall AND wide. Pick narrow bid-ask for oscillating markets, wide for volatile/trending markets.

## Silencing Threshold

The monitor silences reports when fee efficiency is ≥70% and position is in range. Jordan's rationale: at 70%+ efficiency, the bid-ask is doing its job, no need for noise.

**Behavior:**
- Efficiency ≥70% + in range + no alerts → silent (no report sent)
- Efficiency <70% OR out of range OR alerts → report sent
- Material changes (price >1% or >$0.20, zone flip, range flip) → always report regardless of efficiency

**Pitfall**: The silence counter does NOT automatically reset on price movement. After 2 clean runs in one hour, the monitor goes silent even if price starts moving. **See `references/silencing-behavior.md`** for the fix — silence must reset when price moves ≥1% or ≥$0.20.

**Two-tier efficiency alerts**: 50% warning (one alert, then quiet) and 30% critical (one alert, then quiet). Implementation details in `references/silencing-behavior.md`.

**Config:** Change threshold in `should_send_report()` function of `defi-lp-consolidated.py`.

## 3-Component Dashboard Sync

The consolidated monitor (`defi-lp-consolidated.py`) now syncs all 3 dashboard components on every run:

| # | Component | Data File | Source |
|---|-----------|-----------|--------|
| 1 | Position Dashboard | `defi-data.json` | On-chain reader (`run-reader.py`) |
| 2 | Rainbow Zone | `yield-rainbow-data.json` | Consolidated monitor |
| 3 | Harvest Mode Card | `yield-rainbow-data.json` → `currentBand` | Consolidated monitor |

**Key change:** Rainbow data is now written by `defi-lp-consolidated.py` on every cron tick — even during quiet hours and debounce periods. The separate `yield-rainbow.py` script is now redundant (kept for standalone use).

**Why this matters:** Before this fix, the rainbow zone and harvest mode card would go stale after a rebalance because `yield-rainbow.py` wasn't called by the cron pipeline. Now all 3 components update together.

**⚠️ CRITICAL: Dashboard Data Embed Pattern (Jun 25)**

The on-chain reader (`run-reader.py`) writes a CLEAN `defi-data.json` every 10 minutes, overwriting all extra keys. The consolidated monitor runs 3 min later and MUST re-embed these keys:

- `regime` — market regime classification
- `strategyComparison` — shape comparison (bid-ask vs curve vs spot)
- `yieldSpectrum` — rainbow zone data

**The pattern:** Reader writes → monitor reads → embeds extras → writes back. The `embed_dashboard_extras()` function handles this. If you modify the reader, make sure it doesn't break this flow.

**Gaming hub:** No issues — uses separate data files per feature, no overwrite risk. DeFi was the only hub with the overwrite problem because everything shares one `defi-data.json` file.

## Files Reference

| File | Location | Purpose |
|------|----------|---------|
| Position tracker (profile) | `/root/.hermes/profiles/gentech/scripts/.lfj-position-tracker.json` | Primary — cron scripts read from HERE |
| Position tracker (global) | `/root/.hermes/scripts/.lfj-position-tracker.json` | Secondary — must be synced with profile |
| AAE config (profile) | `/root/.hermes/profiles/gentech/scripts/.lfj-aae-config.json` | Full position config |
| AAE config (global) | `/root/.hermes/scripts/.lfj-aae-config.json` | Secondary — must be synced with profile |
| State | `/root/.hermes/profiles/gentech/scripts/.lfj-defi-state.json` | Debounce state, fee tracking, edge timers |
| AAE config (global) | `/root/.hermes/scripts/.lfj-aae-config.json` | Secondary — must be synced with profile |
| State | `/root/.hermes/scripts/.lfj-defi-state.json` | Debounce state, fee tracking |
| Dashboard data | `/root/ProtoJay4789.github.io/DeFi/defi-data.json` | Hub data source |
| Rainbow data (scripts) | `/root/.hermes/profiles/gentech/scripts/yield-rainbow-data.json` | Local tools read from here |
| Rainbow data (dashboard) | `/root/ProtoJay4789.github.io/DeFi/rainbow/yield-rainbow-data.json` | Dashboard HTML reads from here |
| Reader script | `/root/vaults/gentech/scripts/run-reader.sh` | On-chain reader wrapper |
| Monitor script | `/root/.hermes/profiles/gentech/scripts/defi-lp-consolidated.py` | 10-min cron report + rainbow sync |

## Rainbow Band Classification

The Yield Rainbow uses efficiency to classify the farming zone:

| Band | Efficiency | Color | Advice |
|------|-----------|-------|--------|
| Euphoria | 90-100% | 🔴 Red | Take profits, diversify |
| Peak Yield | 75-90% | 🟠 Orange | Hold strong, compound |
| Harvest Mode | 60-75% | 🟡 Yellow | Keep farming |
| Accumulation | 40-60% | 🟢 Green | DCA into position |
| Bleeding Edge | 20-40% | 🔵 Blue | Micro-DCA only |
| Panic Farm | 0-20% | 🟣 Purple | Generational entry |

**Shape matters:** Bid-Ask at edge = high efficiency (Peak Yield). Curve at edge = low efficiency (Bleeding Edge). Same price, different story.

## Clean Cron Output

Jordan does NOT want pre-flight checks, vault sync messages, or auto-correction noise in the LP monitor Telegram output. Only the report itself should appear.

**How it works:** The `defi-lp-consolidated.py` script now redirects preflight output and verification warnings to stderr. Only the formatted report goes to stdout (which is what the `no_agent` cron job delivers to Telegram).

If you're modifying the script and need to add diagnostic output, use `print(msg, file=sys.stderr)` — never bare `print()` for diagnostics.

**Low-efficiency spam fix (Jun 25):** Debug prints like `LOW_EFFICIENCY:DETECTED` and `OUT_OF_RANGE:DETECTED` were going to stdout, causing repeated Telegram spam. Now redirected to stderr. Jordan: "I appreciate the alert, but you don't have to keep alerting me if the efficiency is low." The "alert once per condition" logic in `check_alerts()` handles dedup — one alert when condition starts, silence until it resolves.

**Behavior:**
- Efficiency drops below 30% → one Telegram alert, then silent
- Efficiency recovers above 30% → alert flag resets (can alert again if it drops later)
- Out of range → one Telegram alert after 5min debounce, then silent
- Quiet hours (22:00-08:00 ET) → no Telegram, rainbow data still syncs

## Training Data Collection

Every rebalance and significant observation should be logged to `/root/vaults/gentech/defi-training-data.json`. This feeds the GenTech DeFi model training pipeline.

**When to log:**
- After every rebalance (new sample with shape, range, position, fees)
- After significant market events (Asian selloff, institutional catalyst)
- When the monitor detects unusual patterns

**Schema fields:** timestamp, price, shape, range_low/high, position_usd, avax/usdc amounts, avax_pct, daily_fees, fee_efficiency, efficiency_zone, volatility_24h, volume_24h, tvl, in_range, milestone_tier, market_regime, notes.

**Notes field:** Always include the WHY — what catalyst caused the move, what lesson was learned. This is the most valuable training signal.

## Regime Classifier

The `embed_dashboard_extras()` function classifies market regime based on price position within the range:

| Position in Range | Regime | Recommended Shape | DCA |
|-------------------|--------|-------------------|-----|
| < 25% from edge | **Volatile** | Bid-Ask | Aggressive |
| 25-35% from edge | Sideways | Bid-Ask | Moderate |
| 35-65% (center) | **Sideways** | Curve | Conservative |
| > 75% from edge | **Volatile** | Bid-Ask | Moderate |

**Logic:** Near edges = price is moving = volatile. Near center = consolidation = sideways.

**Regime data structure** (what the dashboard renderer expects):
```python
{
    'current': 'volatile' | 'sideways' | 'bull_trend' | 'bear_trend',
    'previous': '...',
    'changedAt': 'ISO timestamp',
    'signals': {'price': float, 'ma20': float, 'volume24h': float, 'volatility': 'high'|'low'},
    'strategy': {'shape': 'bid-ask'|'curve', 'dcaAggressiveness': 'aggressive'|'moderate'|'conservative'},
    'recommended': 'string'
}
```

**⚠️ Dashboard renderer data shapes (PITFALL):**

The regime renderer (`renderRegimeDetector`) expects `signals.price` and `signals.ma20` as NUMERIC values. If these are undefined, it throws `Cannot read properties of undefined (reading 'toFixed')`.

The strategy comparison renderer (`renderStrategyComparison`) expects: `lpApr`, `lpDailyFees`, `stakingApr`, `stakingDaily`, `hodlReturn`, `entryPrice`, `currentPrice`, `outperforming`, `verdict`. It does NOT accept `bidAsk`/`curve`/`spot` keys — those are for a different renderer.

**Always match the data shape to the renderer.** Check the renderer function in `defi-dashboard.html` to see what destructured keys it expects.

## Cron Timing Dependency

The reader and monitor have a 3-minute offset:
- **Reader** runs at `:00, :10, :20, ...` — writes clean `defi-data.json`
- **Monitor** runs at `:03, :13, :23, ...` — reads fresh data, embeds extras

This means the monitor always reads the reader's latest output and re-embeds regime/comparison/rainbow keys. If the timing is changed (e.g., both run at :00), the reader may overwrite the monitor's embeds. **Always ensure the monitor runs AFTER the reader.**

## Config-First UX — Never Guess Shape/Range/Entry (Jul 19, 2026)

**The single biggest correction from Jul 19:** The AI cannot reliably infer shape, entry price, or intent from on-chain data. Multiple cycles of "Jordan sets shape → AI misreads it → Jordan corrects → AI fixes" proved this is a structural failure, not a one-off bug.

**The fix:** Config-First architecture.

### The Cycle That Broke

```
Jordan sets CURVE on LFJ
    ↓
Reader passes "--shape bid-ask" (wrong default)
    ↓
AI reports "Bid-Ask 93% efficiency"
    ↓
Jordan: "I'm doing CURVE"
    ↓
AI fixes config, reader still wrong
    ↓
Jordan rebalances → loop repeats
```

### The Correct Flow

```
User intent → Config form → Preview card → Deploy on LFJ → Verify on-chain matches config
```

1. **User fills a form** — shape, range, entry price, amount. User's input is the source of truth.
2. **AI writes config** — the config is the canonical reference. The on-chain reader verifies AGAINST it, not instead of it.
3. **On-chain reader validates** — reader checks: "Does on-chain match what the user said?" If yes → silent. If no → flag mismatch.
4. **Config always wins** — if reader detects a different shape but config says CURVE, the config is right. Flag the discrepancy to the user, don't auto-correct.

### Implementation Rules

- **Never auto-detect shape from bin distribution** — the lp-shape-detector.py script should only run when config shape is "unknown"
- **Never infer entry price from transaction history** — the user's stated entry is the canonical value. Use it for IL calculations.
- **Never overwrite user-declared range with on-chain range** — if they differ, alert the user
- **The AAE Yield Farm UX spec** (DeFi/aae-yield-farm-ux.md in repo) formalizes this as a deploy form + preview card + verify cycle

### Files Updated (Jul 19, 2026)

- run-reader.sh — shape default changed from curve to bid-ask (now back to curve as default)
- All 4 config files — manually corrected shape through multiple rebalances
- Spec drafted at DeFi/aae-yield-farm-ux.md and DeFi/aae-tactical-retreat.md in repo

### Pitfall: Reader Hardcodes Shape Default

The on-chain reader (run-reader.sh line 7) has SHAPE env default. This means every reader run echoes "Curve" UNLESS the SHAPE env var is explicitly set. If Jordan switched to bid-ask but no one updated this default, every reader run shows the wrong shape on the dashboard. **The reader's shape output is not reliable for monitoring — it's a label the agent passes, not a detection result.**

Fix: The reader should read shape from the AAE config file, not an env default. Or better: Config-First approach — user declares shape, reader just uses it.

## Fee Calibration — Jul 19 Live Check

On Jul 19, Jordan's LFJ UI showed actual 24h fees of **$0.14** on a **$24.42** position (CURVE shape). The dashboard was projecting **$0.074/day** — nearly 2x under-estimate.

Recalibration: actual_rate = $0.14 / $24.42 = 0.573% per day (was 0.515% for bid-ask on $46.59 position). CURVE in chop earns higher than bid-ask model projected. Re-calibrate per shape; re-check when pool TVL changes >20%, position value >50%, or shape changes.

## Entry Price Verification — IL IS CRITICAL

**Jordan's emphasis (Jul 19, 2026):** "Calculating Impermanent loss is critical."

IL is not a secondary metric — it determines whether the LP strategy is actually outperforming a simple hold. Every rebalance must verify entry price against Jordan's stated entry before closing the loop.

The on-chain reader may not always report the correct entry price. After a rebalance:
1. Check the position tracker entry price matches what Jordan says
2. If Jordan corrects the entry (e.g., "entry should be $6.13"), update BOTH the tracker AND the AAE config
3. IL is calculated as `((current_price - entry_price) / entry_price) * 100` — wrong entry = wrong IL

**Jun 25 incident:** Reader showed entry at $6.055, Jordan corrected to $6.13. The $0.075 difference flipped IL from +0.91% to -0.33%. Always verify entry price against Jordan's stated entry after rebalance.

## Efficiency Calculation — Use Dashboard Value

**Critical:** The on-chain reader calculates efficiency correctly using **bin weights/depths**. The monitor script must **never recalculate** efficiency with the position-based formula.

| Source | Formula | Accuracy |
|--------|---------|----------|
| Dashboard (`defi-data.json`) | Bin-weighted (liquidity distribution) | ✅ Correct |
| Monitor position formula | `abs(pos - 0.5) * 2 * 100` | ❌ Wrong for bid-ask |

**Why it matters:** Bid-ask efficiency = liquidity concentration near current price. The position formula ignores where liquidity is actually deployed.

```python
# CORRECT: Use pre-calculated from dashboard
efficiency = dash.get("efficiency", None)
if efficiency is None:
    # Fallback only if missing
    efficiency = calc_fee_efficiency(price, range_low, range_high, shape, bins)
```

**Jun 27 incident:** Monitor reported 3.2% efficiency using position formula, but dashboard showed 69% (correct bin-weighted). Jordan caught this: "fee efficiency should be way higher because we're getting very close to our last bin."

**Pitfall:** Do not recalculate efficiency when dashboard has it. The reader writes the correct value to `defi-data.json`. Read it, don't recompute.

## Silencing Logic — Movement Resets Quiet Mode

**Jordan's rule:** "Only quiet if it's literally not moving too much... if it's almost stagnant. When moves are being made, I want to see the cron job."

**Silence clearing on movement:**
- Price moves >1% **OR** >$0.20 → `consecutive_quiet_runs` resets to 0
- Reports resume at 10-minute frequency
- This ensures you see movement when it happens

**The old problem:** Micro-movement rule silenced immediately on <0.2% moves, keeping the system quiet even during active periods.

**Removed logic:**
```python
# REMOVED: instant silence on micro-moves
if price_change_pct < 0.2 and price_change_abs < 0.05:
    return False, "micro-movement — silent"
```

**New logic:**
```python
# Material movement: 1% or $0.20 threshold → reset silence
if price_change_pct >= 1.0 or price_change_abs >= 0.20:
    reasons.append(f"price {price_change_pct:.1f}%")
    state["consecutive_quiet_runs"] = 0  # RESET
    state["last_report_hour"] = now_dt.hour
```

## Smart Alerts with Range Migration Suggestions (Jul 4, 2026)

**AAE DeFi milestone integration:** The cron now emits actionable suggestions when position needs rebalancing — not just passive alerts.

### Debounce Logic

| Alert Condition | First Alert | Repeat | Silence | Suggestion |
|---|---|---|---|---|
| **OUT_OF_RANGE** | Immediate | N/A | N/A | Shift range + suggest CURVE |
| **Efficiency < 50%** | Immediate | After 5 min | 1 hr after 20 min total | Switch shape or widen range |
| **Efficiency recovered** | Immediate | N/A | N/A | Reset all timers |

### Silence Rules

**Why silence matters:** Jordan's rule — "If the cron job says, hey, your fee efficiency is low more than once within maybe like 20 minutes, we make the cron job silent because I already know I need to rebalance, but it doesn't have to run every 10 minutes if we're not moving that much."

**Implementation:**
```python
LOW_EFF_THRESHOLD = 50.0
INITIAL_DEBOUNCE_SECONDS = 300  # 5 min
SILENCE_THRESHOLD_MINUTES = 20  # total low-efficiency time before silence
SILENCE_DURATION_MINUTES = 60   # stay silent for 1 hour after
```

- First detection: alert immediately
- Repeat detection: wait 5 minutes
- After 20+ minutes cumulative low-efficiency: go silent for 1 hour
- Movement resets: any material price move (>$0.20 or >1%) resets timers

### Range Migration Suggestions

**The prompt-based approach:** "What if we were to prompt what the next shape should look like? And we say between what range we want it at, right? If the way that Trader Joe works is you can only yield farm at the current price, right? I'm guessing that's how most platforms are, unless maybe we could be different."

**Implementation:** The `suggest_new_range()` function provides actionable migration prompts:

#### OUT_OF_RANGE Examples

**Above range:**
```
🔧 MIGRATE: Shift range to $6.9318-$7.1524 (CURVE) — price $7.0200 above $7.0067
```

**Below range:**
```
🔧 MIGRATE: Shift range to $6.6545-$6.8751 (CURVE) — price $6.7500 below $6.7861
```

**Migration logic:**
- If above range: shift up, use wider spread (40% below price, 60% above)
- If below range: shift down, use wider spread (60% below price, 40% above)
- Suggest CURVE shape for OUT_OF_RANGE (wider coverage, less sensitivity to edges)

#### LOW_EFFICIENCY Examples

**Bid-ask in center valley:**
```
🔧 OPTIMIZE: Switch to CURVE at $6.7640-$7.0288 — bid-ask inefficient at center (price 52% of range)
```

**Curve near edge:**
```
🔧 OPTIMIZE: Consider BID-ASK to capture edge efficiency — price 78% toward high edge
```

**Generic widen:**
```
🔧 OPTIMIZE: Widen to $6.6681-$7.1247 (BID-ASK) — efficiency low at 50% of range
```

### API Service Roadmap

**Jordan's ask:** "If this could be an API service, let's look into that as well."

**Current state (signal layer):**
- Cron detects condition → emits suggestion → Jordan approves manually on LFJ
- This is the AAE DeFi milestone "intelligent alerts layer"

**Future state (execution layer):**
1. **Flask API** — expose `suggest_new_range()` as HTTP endpoint
2. **Approval callback** — agent sends prompt → Jordan clicks "yes"
3. **Auto-execution** — agent runs `lfj position migrate` CLI
4. **Gas auto-payment** — built-in x402 integration for transaction costs

**AAE platform positioning:**
- Other platforms: "prompt to yield farm" (you do everything)
- Our advantage: "prompt to do THIS specific thing" (the agent figures out the range migration)
- Edge case: LFJ UI forces bin selection around current price — but CLI/contract don't have that limitation
- For range migration: withdraw → calculate new bin IDs → add liquidity → report completion

### Files Updated (Jul 4, 2026)

- `/root/.hermes/profiles/gentech/scripts/lp-monitor-v2.py` — smart debounce + suggestions
- `/root/.hermes/scripts/lp-monitor-v2.py` — global copy for cron
- `/root/.hermes/scripts/lp-position-reader.py` — bin-weighted efficiency
- Commit: "feat: smart LP alerts — range migration suggestions"
- Commit: "fix: bin-weighted LP efficiency calculation"

## Data Field Consistency — Entry Price Protocol

**CRITICAL (Jun 30, 2026):** Multiple data sources with inconsistent field names caused incorrect entry price and IL calculations. The system had correct range detection but wrong entry price sources.

### Field Name Synchronization Required

Every script reading config data must use **identical field names**:

| Data Source | Entry Price Field | Range Fields | Status |
|-------------|-------------------|--------------|---------|
| **Position Tracker** | `entry_price` | `range_low`, `range_high` | ✅ Correct |
| **Config File** | `entry_price` | `range_low`, `range_high` | ✅ Fixed |
| **Dashboard** | `entryPrice` | Current structure | ✅ Fixed |
| **Cron Script** | `entry_price` | `range_low`, `range_high` | ✅ Working |

### The Field Name Gap (Incident)

```python
# BEFORE: Field name mismatch broke everything
config['position']['range']['low']    # Wrong nesting
config['position']['range']['high']   # Wrong nesting
# No entry_price field anywhere in config

# AFTER: Unified field names
config['position']['range_low'] = 6.2771     # ✅
config['position']['range_high'] = 6.4812    # ✅
config['position']['entry_price'] = 6.3792   # ✅
dashboard['hero']['entryPrice'] = 6.3792     # ✅
```

### After Every Rebalance Protocol

1. **Update ALL sources consistently**:
   ```bash
   python3 /root/.hermes/profiles/gentech/scripts/entry-price-fix.py \
     --range-low 6.XXXX \
     --range-high 6.XXXX \
     --shape curve \
     --avax-amount X.XXXX \
     --usdc-amount X.XX
   ```

2. **Verify consistency**:
   ```bash
   python3 /root/.hermes/profiles/gentech/scripts/test-entry-price-fix.py
   ```

3. **Check dashboard**: Confirm ProtoJay4789.github.io/DeFi shows correct entry price

### Key Learning

**Field name consistency is more important than calculation accuracy.** The IL formula was correct, but inconsistent field names broke the entire data chain. Every script reading config data must use the same field names.

**Impact**: Before fix, IL calculations used wrong entry price ($6.2771 vs correct $6.3792), leading to faulty metrics. After fix, all sources show consistent data.

### Verification Tool

See [scripts/test-entry-price-fix.py](scripts/test-entry-price-fix.py) for automated consistency verification after rebalances.

## Audit Workflow Intelligence — Verification Protocol

**CRITICAL:** Every LP position fix requires verification, not just application. This protocol prevents stale data, incorrect entry prices, and false IL calculations.

### The Verify Everything Protocol

When Jordan rebalances or a fix is applied, the sequence must be:

1. **APPLY FIX** → Update position tracker + config + scripts
2. **VERIFY WORKS** → Run verification script to confirm data consistency
3. **MONITOR REGRESSION** → Watch for next 1-2 cycles to ensure no reversion

### Verification Quality Gates

After ANY fix (entry price, range, shape), these gates must pass:

| Quality Gate | Check Method | Threshold | Severity |
|-------------|-------------|-----------|----------|
| **Entry Price Accuracy** | Compare dashboard vs manual calculation | < $0.01 difference | Critical |
| **Range Consistency** | Verify current price in range | Within bounds | High |
| **Shape-Sync** | Check AAE config matches position tracker | Exact match | High |
| **IL Calculation** | Verify matches manual `((current-entry)/entry)*100` | < 0.1% difference | Critical |

### The Universal Verifier

Use the Gentech Verify Everything system for consistent verification:

```bash
# After fixing entry price
python3 /root/.hermes/profiles/gentech/scripts/gentech-verify.py cron-job \
  "/root/.hermes/profiles/gentech/scripts/defi-lp-consolidated.py"

# After fixing GitHub pages  
python3 /root/.hermes/profiles/gentech/scripts/gentech-verify.py github-page \
  "docs/index.html"
```

### Verification Pattern

**When Jordan says "I just rebalanced":**

1. **Detect Change** → Run the on-chain reader (`run-reader.py`). It auto-detects the new on-chain position and writes fresh `defi-data.json`. Note: the reader does NOT auto-update the position tracker or AAE config — those must be synced explicitly.
2. **Update Source of Truth** → Position tracker + AAE config (BOTH profile and global paths). Even if the reader caught the rebalance, the tracker files are stale until manually updated.
3. **Resolve Git Divergence** → Check if the reader's push succeeded. If other processes (gaming sync, nightly sync) committed between reader cycles, the push may have been rejected. See `references/git-divergence-resolution.md` for the fast reset-and-re-run sequence.
4. **Verify Dashboard** → Confirm `ProtoJay4789.github.io/DeFi/defi-data.json?t=<timestamp>` shows correct data. Use a cache-busting query param to bypass GitHub's CDN.
5. **Monitor for Regression** → Next 1-2 monitor cycles (at :03/:13/:23) must show consistent data. If the monitor reports old range/different entry price, the position tracker was not synced correctly.

### The Fix-Then-Verify Loop

```python
# Example: Entry price fix protocol
def fix_and_verify_entry_price(range_low, range_high):
    # 1. Apply fix
    result = subprocess.run([
        'python3', 'fix-entry-price.py', 
        '--range', str(range_low), str(range_high)
    ])
    
    if result.returncode != 0:
        return {"success": False, "error": "Fix application failed"}
    
    # 2. Verify fix
    verification = verify_task("cron", {
        "script": "defi-lp-consolidated.py",
        "description": "Verify entry price fix"
    })
    
    if not verification["success"]:
        return {
            "success": False, 
            "verification_failed": verification["recommendations"]
        }
    
    # 3. Confirm dashboard update
    dashboard_data = load_dashboard_data()
    expected_entry = sqrt(range_low * range_high)
    actual_entry = dashboard_data.get("lpPosition", {}).get("entryPrice")
    
    if abs(actual_entry - expected_entry) > 0.01:
        return {
            "success": False,
            "dashboard_mismatch": f"Expected {expected_entry}, got {actual_entry}"
        }
    
    return {"success": True}
```

### Common Fix Scenarios

**Scenario 1: Entry Price Stale (Jun 30, 2026)**
- Problem: Dashboard showed $6.71, actual was $6.46  
- Fix: `fix-entry-price.py --range 6.4039 6.6186`
- Verify: Check dashboard shows $6.5104
- Prevent: Add verification step after every manual rebalance

**Scenario 2: Range Drift**  
- Problem: Position tracker has old range, on-chain updated
- Fix: Run `sync_tracker()` function to update both paths
- Verify: Check `defi-lp-consolidated.py` reports correct range
- Prevent: Run on-chain reader before monitor scripts

**Scenario 3: Shape Mismatch**
- Problem: Position tracker says "curve", Jordan moved to "bid-ask"
- Fix: Update tracker with correct shape, update AAE config
- Verify: Check efficiency calculation uses correct formula
- Prevent: Always verify shape after manual rebalance

### The Universal Verification Matrix

| Task Type | Verification Points | Quality Gates | Success Criteria |
|----------|-------------------|---------------|------------------|
| **LP Fix** | Entry price, range, shape, IL | Entry accuracy < $0.01, in range, shape sync | All gates pass |
| **Cron Job** | Execution, errors, schedule | No errors, schedule compliance | Script runs cleanly |
| **GitHub Page** | HTML validity, links, performance | Valid HTML, working links, load < 3s | Page renders correctly |
| **API Change** | Response time, errors, format | < 2s response, 200 status, valid JSON | All endpoints functional |

### Integration with Build Queue

The Verify Everything protocol should be added to the build queue:

```yaml
tasks:
  - name: "Fix LP entry price"
    type: "verification_required"
    verification:
      required: true
      type: "functional"
      checks: ["entry-price", "range-consistency", "shape-sync"]
      quality_gates: ["entry-accuracy", "in-range", "no-regressions"]
```

**Key Insight:** Every Gentech task, big or small, needs verification. This turns reactive problem-solving into proactive reliability engineering.

## Pitfalls
**Pitfalls:**
- **Git divergence after reader push** — The on-chain reader commits and pushes `defi-data.json` every 10 min. If other processes (gaming hub sync, POE2 sync, nightly hub sync) pushed between reader cycles, the reader's push is rejected as non-fast-forward. The reader's `pull --rebase` can then create merge conflict artifacts (`<<<<<<< Updated upstream`) in the remote file, corrupting the dashboard data. **A second form of corruption:** a `git merge` (not rebase) can commit unresolved conflict markers into the file, with the same result. Fix (rebase scenario): `git fetch origin && git reset --hard origin/main && re-run reader`. Fix (merge-commit scenario — corruption already on origin): `git show <pre-merge-commit>:path > path` then commit+push the clean version. See `references/git-divergence-resolution.md` for both scenarios.
- **Position tracker not updated on rebalance** — Root cause of shape/entry/IL drift. The position tracker (`/.lfj-position-tracker.json`) is the SOURCE OF TRUTH for shape, entry price, and range. When Jordan rebalances manually on LFJ, the tracker MUST be updated immediately. If it says "curve" but Jordan moved to "bid-ask", every downstream component (monitor, dashboard, rainbow zone) gets wrong data. Cron jobs read from tracker, not just on-chain reader. See `references/position-tracker-drift-incident.md` for the Jun 28 incident where stale tracker caused wrong shape, entry price ($6.13 vs actual $6.23), and IL reporting (+2.71% vs +1.06% actual).
- **Rainbow data dual-path write** — The dashboard HTML reads from `ProtoJay4789.github.io/DeFi/rainbow/yield-rainbow-data.json` (relative path in the HTML). If the consolidated monitor only writes to the scripts directory, the dashboard shows stale data. Always write to BOTH `RAINBOW_OUTPUT_PATH` (scripts) and `RAINBOW_DASHBOARD_PATH` (GitHub Pages). This caused "nothing has changed" feedback from Jordan on Jun 25.
- **Hub sync must include rainbow data** — The nightly hub sync (`hub-sync-nightly.py`) does `git add DeFi/defi-data.json`. If it doesn't also add `DeFi/rainbow/yield-rainbow-data.json`, the rainbow data is written locally but never pushed to GitHub Pages. The `git add` command must include both files.
- **Quiet hours must not kill dashboard sync** — The old `defi-lp-consolidated.py` did `sys.exit(0)` during quiet hours (23:00–06:00 ET), which killed the entire script including any dashboard data writes. The fix: set `quiet_mode = True` instead, suppress only the Telegram report, but still run the rainbow data write. Dashboard must stay fresh 24/7 regardless of quiet hours.
- **Bid-ask imbalance false positive** — The monitor flags "96% USDC = IMBALANCED" but for bid-ask shapes, heavy USDC at the upper range is CORRECT (you've been selling rips). The monitor now reads shape from AAE config and suppresses the alert for bid-ask/spot. If someone re-enables the old check, bid-ask will false-alarm again.
- **Jordan expects screenshots to match reports** — When Jordan sends LFJ screenshots, the pipeline data MUST match. If the monitor says $0.42/day but LFJ shows $0.84/day, that's a sync gap. Always cross-check against LFJ data before reporting.
- **Automated shape detector overwrites manual fixes** — The `lp-shape-detector.py` script analyzes on-chain bin distribution and classifies shape, then writes to `defi-data.json`. This can overwrite manual config updates if it detects the wrong shape. If you manually fix the dashboard shape to "bid-ask" but the detector classifies it as "curve" (incorrectly), it will revert your changes on next run. **Fix: Implement config-first architecture — auto-detection only if config says "unknown" or "curve".** See `references/config-first-architecture-pattern.md` for the implementation pattern and `references/automated-script-overwrite-incident.md` for the Jun 30, 2026 incident where 18 dashboard-writing scripts caused data reversion.
- **Cron script location mismatch** — There are TWO versions of the monitor script: `/root/vaults/gentech/Strategies/scripts/defi-lp-consolidated.py` (vault) and `/root/.hermes/profiles/gentech/scripts/defi-lp-consolidated.py` (profile). The cron job runs from the **profile path**. If you fix the vault version but not the profile version, the cron still uses the broken code. **Always edit both files or the fix won't take effect.**
- **Multi-copy defi-data.json sync** — There are 9 copies of `defi-data.json` across repos, vault, and portfolio directories. When fixing fee data or milestones, grep for all copies: `grep -r 'dailyFees' /root/*/DeFi/defi-data.json /root/vaults/gentech/DeFi/defi-data.json` then `cp` from the canonical copy (the GitHub Pages repo) to all others. The repos copy at `/root/repos/ProtoJay4789.github.io/DeFi/defi-data.json` is the most commonly stale one because it's a mirror not synced by normal workflows.
- **`~` path expansion with custom HOME** — When `HERMES_HOME` is set, `os.path.expanduser("~")` returns that path, not `/root`. Use absolute paths for critical files.
- **GitHub raw file caching** — After pushing updated defi-data.json, the raw GitHub URL may serve stale content for 1-5 minutes. Add `?v=<timestamp>` to bypass.
- **On-chain reader overwrites manual updates** — The reader runs every 10 minutes and writes to defi-data.json. If you manually update defi-data.json but don't update the position tracker, the reader reverts your changes on next run.
- **Institutional news pushes price through range quickly** — The TIS/Avalanche Japan catalyst (Jun 23) pushed AVAX from $6.20 to $6.43 in hours, breaking through the old range ceiling. When fundamental catalysts appear, consider rebalancing up proactively rather than waiting.
- **Knife vs consolidation** — A "knife" drop is a sharp 5-10% candle with volume. A "consolidation" is a gradual drift over hours with tight candles. Before rebalancing, check: is this a fast drop (knife, may bounce) or slow drift (consolidation, likely continuing)? Use hourly candles to tell — tight candles over 6h = consolidation, not a knife.
- **Shared quiet hours module** — Multiple cron scripts need quiet hours checks. Instead of duplicating the logic, use the shared module at `scripts/quiet_hours.py`. Import with `from quiet_hours import is_quiet_hours`. The module defines `QUIET_START=22, QUIET_END=8` (ET). All GenTech cron scripts should use this, not their own quiet hours constants. The DeFi consolidated script has its own copy for backward compat, but new scripts should import from the shared module.
- **Fee projection during out-of-range** — The volume-based fee formula projects earnings even when the position isn't in range to capture fees. This misleads the report into showing a positive daily rate during an out-of-range period. The fix: add `if not in_range: live_daily = 0.0` before any fee calculation in `lp-monitor-v2.py`. See `references/out-of-range-recovery.md` for the complete protocol (fee fix + state reset + dashboard sync).
- **positionLifecycle lost on manual dashboard sync** — The `defi-data.json.positionLifecycle` key is not written by any cron script; it's set initially by the on-chain reader and can be dropped during manual dashboard edits. When restoring, populate from the last rebalance date. Schema and example in `references/out-of-range-recovery.md`.
