---
name: defi
description: "Unified DeFi operations umbrella: LP monitoring, rebalancing, dashboard sync, strategy design, on-chain reading, LFJ orchestration, AAE app architecture, rank/prestige engine, and security intelligence. One skill to rule them all."
tags: [defi, lp, monitoring, rebalance, dashboard, strategy, on-chain, lfj, avalanche, solana, meteora, aae, ranks, prestige]
trigger: "Any DeFi-related task: LP monitoring, rebalancing, dashboard sync, strategy design, on-chain reads, LFJ operations, fee milestones, AAE app architecture, rank/prestige engine, Meteora DLMM pools, security intel, or operator shape directives."
related_skills: [market-macro-monitor, link-research-summary]
version: 2.8.0
author: Gentech
---

# DeFi Operations (Unified Umbrella)

All DeFi LP management in one skill — monitoring, rebalancing, dashboard sync, strategy, on-chain reading, LFJ orchestration, milestones, and security intel.

> **Consolidated from:** `defi-operations`, `defi-lfj-monitoring`, `defi-lp-monitoring`, `lfj-rebalance-handler`, `dashboard-sync`, `defi-dashboard-sync`

---

### Quick Decision Table

| User Intent | Section | Reference |
|-------------|---------|-----------|
| Detect on-chain entry for a wallet | §5 On-Chain Entry Detection | references/onchain-entry-detection.md |
| "How's my pool doing?" / Run monitor | §1 LP Monitoring | references/lp-monitoring-workflow.md |
| "Why are fees wrong?" / Fee tracking issue | §1 Fee Tracking | §1 (inline — merged monitor) |
| "Rebalance to [shape] [range]" | §2 Rebalance | references/rebalance-workflow.md |
| Update dashboard after rebalance | §3 Dashboard Sync | references/dashboard-sync-protocol.md |
| "What shape should I use?" / Regime | §4 Strategy | references/strategy-design.md |
| Read on-chain position data | §5 On-Chain Reading | references/onchain-reading.md |
| LFJ scripts, config locations, cron | §6 LFJ Orchestration | references/lfj-orchestration.md |
| Fee milestones, tier progress | §7 Milestones | §7 (inline) |
| Security incident monitoring | §8 Security Intel | references/security-intel.md |
| External APIs (Arsenal, GOAT, etc.) | §9 External APIs | references/external-apis.md |
| Market sentiment by narrative | §10 Narrative Sentiment | references/narrative-rotation-sentiment.md |
| Routing layer / mode decisions | §11 Routing Layer | references/routing-layer-quick-ref.md |
| Training data schema | §12 DeFi Model | references/training-data-schema.md |
| Prompt-to-yield / Agent rebalance service | §13 Prompt-to-Yield | references/prompt-to-yield-service.md |
| AAE app architecture, rank/prestige | §19 AAE DeFi Hub | references/defi-operations.md (AAE sections) |
| Meteora DLMM pool analysis | §20 Meteora DLMM | references/defi-operations.md (Meteora section) | references/entry-price-il-fix-protocol.md |
| Entry price sync issues after rebalance | §16b Sync Issue Protocol | references/entry-price-sync-issue-fix.md |
| Cron jobs running during quiet hours | §6 LFJ Orchestration | references/cron-quiet-hours-enforcement.md |
| Agentic Treasury / Yield Farm Command Center | §21 Agentic Treasury | references/agentic-treasury-architecture.md |
| Robinhood Trading MCP setup | §22 Robinhood MCP | references/robinhood-trading-mcp.md |
| Fee history tracker / replace ATH with rank | §1 Fee Tracking | references/fee-history-tracker.md |
| Build a Command Center dashboard | §21 Agentic Treasury | references/agentic-treasury-architecture.md |
| Human-Agent collaboration modes | §21 Agentic Treasury | references/agentic-treasury-architecture.md |
| LP Curve canvas visualization | §21 Agentic Treasury | references/agentic-treasury-architecture.md |
| Demo site card for a subdomain dashboard | §21 Agentic Treasury | references/agentic-treasury-architecture.md |

---

## 1. LP Position Monitoring

### Smart Debounce & Range Migration Suggestions (UPDATED Jul 20, 2026)

**User Preference (Jul 20, 2026):** "I like to see the cron job from time to time, especially with the fee efficiency being so high. But find a balance between showing off the cron job and it not being annoying."

**Debounce Rules (3-tier):**

| Situation | Behavior | 
|-----------|----------|
| 🟢 In range, ≥50% efficiency | Reports **2x/hour** (every 30 min) — user sees fee efficiency humming |
| ⚠️ Efficiency < 50% | **Immediate alert** with rebalance recommendation, then 10 min debounce |
| 🔴 Out of range | **Immediate alert** with migration suggestion, no debounce |
| 🌙 11 PM – 6 AM ET | **Truly silent** — no message at all (sys.exit(0), no print) |
| 💰 User adds capital / DCAs | Run **full AAE suite**: fee efficiency, position value, milestone progress, next rank |

**Implementation in lp-monitor-v2.py (`check_debounce()`):**
```python
LOW_EFF_THRESHOLD = 50.0
LOW_EFF_DEBOUNCE_SECONDS = 600    # 10 min between low-efficiency alerts
NORMAL_INTERVAL_SECONDS = 1800    # 30 min between normal check-ins

# State tracking via .lfj-defi-state.json:
#   last_report_time — when we last sent any report
#   last_low_alert_time — when we last sent a low-efficiency alert
```

**Alert Conditions:**

| Condition | Threshold | Suggestion |
|-----------|-----------|------------|
| OUT_OF_RANGE (above) | Price > range_high | Shift range upward + suggest CURVE |
| OUT_OF_RANGE (below) | Price < range_low | Shift range downward + suggest CURVE |
| LOW_EFFICIENCY (bid-ask center) | Efficiency < 50%, price near center | Switch to CURVE |
| LOW_EFFICIENCY (curve edge) | Efficiency < 50%, price near edge | Consider BID-ASK |
| LOW_EFFICIENCY (generic) | Efficiency < 50% | Widen range by 15% |

**Example Suggestion Outputs:**

OUT_OF_RANGE (above $7.0067):
```
🔧 MIGRATE: Shift range to $6.9318-$7.1524 (CURVE) — price $7.0200 above $7.0067
```

BID-ASK at center:
```
🔧 OPTIMIZE: Switch to CURVE at $6.7640-$7.0288 — bid-ask inefficient at center (price 52% of range)
```

**User Preference:** "If the cron job says 'hey, your fee efficiency is low more than once within maybe like 20 minutes, we make the cron job silent because I already know I need to rebalance." — Encoded as the 20-minute cumulative silence threshold.

**Implementation in lp-monitor-v2.py:**
- `check_debounce()` function tracks `efficiency_low_start` and `efficiency_low_total`
- `suggest_new_range()` function generates actionable migration prompts
- State file `.lfj-defi-state.json` stores debounce state across runs

### Fee Tracking — Live Volume-Based Calculation (NEW)

**Dynamic fee rate calculation from live DexScreener data:**
```python
# Pool's total daily fees from volume
total_fees_24h = volume_24h × (fee_tier_bps / 10000)

# Position's proportional share of pool TVL
pool_share = lp_value / liquidity

# Our daily fees, boosted by concentration multiplier
daily_fees = total_fees_24h × pool_share × CONCENTRATION_MULTIPLIER
```

**Concentration multiplier (calibrated Jul 3, 2026):** 4.92x for bid-ask positions on AVAX/USDC 5bps pool.

**Fallback to yield-rate method:**
```python
DAILY_YIELD_RATE = 0.00515  # $0.24/day on $46.59 position
daily_fees = round(position_value * DAILY_YIELD_RATE, 4)
```

**Key advantage:** Fee rate auto-adjusts when volume changes. If pool volume jumps to $1M, the next cron tick shows higher daily rate without manual recalibration.

### Alert Escalation

```
Stage 1: Condition detected         → start 5-min debounce
Stage 2: Same condition persists 5m → fire ONE alert (MEDIUM or HIGH)
Stage 3: After alert fires          → SILENT until condition fully clears
```

**Severity:** Out-of-range = HIGH | Efficiency <30% = MEDIUM | Efficiency 30-50% = informational

### 🚩 "Not earning" is a red flag, not an advisory

Jordan: *"Yes not earning is a red flag, should get immediate attention."*

A book can be **deployed, in-range, and structurally healthy** — every visible check passes — while its fee rate has collapsed. This is the hardest failure mode to see from outside: there is no empty capital, no escaped price, no broken config, only money that is not being made.

**Classification rule:** a sustained "not earning" condition is **MATERIAL**, not advisory. It bypasses quiet-hour and overnight gates, and it alerts immediately.

**What "not earning" means here:**
- The measured fee efficiency has fallen below the active threshold (e.g. below the shape's Hold band) and stayed there through the confirmation window.
- The position is still deployed and still in range — if it were idle or out of range, those conditions would already fire their own alerts.

**What it is NOT:**
- A transient dip. One bad sample is noise; the alert fires only after the sustained rule is satisfied.
- A geometry score on a correctly-built shape. A bid-ask at its junction reads low by design; that is the shape working, not the position failing. "Not earning" is a measured fee-rate condition, not a shape-geometry complaint.

**Alert behavior:**
- Fire once, then dedupe on a **stable signature** (e.g. `NOT EARNING`). A signature that includes tx hashes, counts, or timestamps changes every run and can never suppress itself — so the same condition would wake the user every cycle.
- Re-arm only when the condition clears.

**Attention is not the same as automatic rebuild.** The alert raises immediately; the capital action still follows the budget, churn cap, and operator directive. A red flag tells the operator the book has stopped earning. Spending gas to chase a number that is green on a different shape is a separate decision and must not be hidden inside the alert.

### ⚠️ Scanner Thresholds and Config Drift

**The threshold is source-of-truth in code, not in memory.** The user may recall an original
rule as one number while the code holds another. Until the rule is written in the Constitution
or the code constant is updated, the code wins by default.

**When changing a threshold:**
1. Read the current constant in `fee_efficiency.py` (e.g. `LOW_EFF_THRESHOLD`, `BAND_HOLD`,
   `BAND_REDUCED`, `LOW_DUTY_MIN`).
2. Check whether the new threshold conflicts with an intentional low-reading shape
   (e.g. a bid-ask reads ~33% by construction when price is near centre).
3. If it conflicts, add an **exemption rule** before changing the number, or the book will
   churn forever.
4. Update the code constant and the Constitution together; do not update one without the other.

**Example:** raising "stay above" from 50% to 75% is correct for a curve, but **deadly** for a
deliberate dip-gathering bid-ask unless the bid-ask is exempt. Write the exemption first.

**When the user asks "what did you see when you rebuilt?", the answer must come from a JOURNAL,
not memory.** A churn ledger that records only a timestamp and a zone cannot answer whether the
book was green, yellow, or red at the moment of action. Build a rebuild journal at the single
confirmed-action site and record: efficiency, zone, in-range, margin in bins, spot, band, trigger,
and shape. A missing reading is `null` — never a guess, because the journal is what justifies
future threshold changes.

**A threshold is also not a substitute for an operator directive.** A bid-ask at 25% efficiency is
exactly where a bid-ask often sits when price is near its junction. If the operator chose that shape
deliberately, no efficiency threshold should trigger a rebuild. Check for an active operator shape
directive before any efficiency-driven shape switch.

### Rebuild Journal — what the book looked like when we acted

Every real rebuild must write one record at the confirmed-action site (after on-chain verification
shows the position re-opened). Store both JSONL beside the state file and a markdown table in the
vault. Required fields:

- `tenant`, `trigger`, `efficiency`, `zone`, `in_range`, `margin_bins`, `spot`, `band_lo`, `band_hi`,
  `shape`
- `ts` and `iso` — use the true event timestamp, not the time the row was written. A journal whose
  rows carry write-time cannot answer "what did you see when".

**Backfill from logs only what can be recovered honestly.** If the cron log carries the zone but
not the efficiency, backfill zone and leave efficiency null. A fabricated number in a journal is
worse than a blank, because it will be used to justify changing a threshold.

**Use the journal to answer three questions the user will ask:**
1. How often did we rebuild while still Green (≥75%)?
2. How often was the book legitimately below the threshold?
3. How often can we not tell because the reading was never recorded?

**Record the EVENT that drove the action, not a downstream side-effect.** A journal that logs gas-floor checks, health pings, or sample counts cannot answer "were we rebuilding while already green?" — even if every row carries a timestamp and a zone. Before designing the journal, decide which question it must answer; then confirm the row is written at the confirmed-action site with the actual decision inputs (`trigger`, `zone`, `efficiency`, `shape`, `path taken`), not at an earlier monitor step that runs whether or not an action occurred. If the classification that produces the zone does not reach the action site, fix the wiring; do not backfill a plausible zone from a different log.

### When several brakes interact, measure which one binds

A cadence change, a cooldown change, and a confirmation-window change are not interchangeable. After changing any of them, count the actual gap between rebuilds and compare it to each brake in isolation. If the observed median gap is shorter than the cooldown that should bind it, a bypass path exists — and widening the window or slowing the cadence will not fix the churn until the bypass is closed. Report the binding brake and the bypass separately; do not let a rule change that looks correct on paper hide a path that still walks past every gate.

### Smart DCA Zones

| Zone | Efficiency | DCA Amount | Action |
|------|-----------|------------|--------|
| 🟢 Center | ≥70% | $50 (full) | Hold, earn optimally |
| 🟡 Mid | 50-70% | $30 (reduced) | Approaching edges |
| 🟠 Low | 30-50% | $20 (micro) | Watch for rebalance |
| 🔴 Edge | <30% | $10 + URGENT | Rebalance now |

### Skip-Logic

| Condition | Action |
|-----------|--------|
| Price delta <0.5% + IL <0.5% + in-range | Skip vault append |
| IL ≥1.0% OR price exits range | Append vault, flag review |
| Milestone tier achieved | Append vault, celebrate |

### Notification Policy

**Alert once per condition change. Stay silent otherwise.** Track `last_alerted_condition` in state. Empty stdout = no delivery. Only fire on condition change or 1-hour cooldown.

### Fee Tracking Integration (Merged into LP Monitor)

Fee tracking runs **inside the LP monitor script** (`lp-monitor-v2.py`) — NOT as a separate cron job. This was previously split (24/7 Fee Tracker ran hourly) but the user insisted on consolidation to reduce noise.

**How it works:**
- LP monitor loads `fee-tracker-config.json` (position value, APY override) and `fee-tracker-state.json` (accumulated totals)
- On each run, calculates fees earned since last check: `value × APY/100 × hours_elapsed/8760`
- Accumulates to daily/weekly/monthly/all-time totals with automatic period resets
- Fee Trajectory section shows **actual accrued** figures (Today/Week/Month/All-time) — NOT projections
- Only the Yearly line is a forward projection from APY math

**CRITICAL — Initial seed:** On first setup or after config change, `fee-tracker-state.json` accumulates from 0. You MUST seed it with real values from Trader Joe UI or the user's confirmed fee numbers. The user will immediately notice if the tracker shows $0.46 when they know they've earned $4.29/week.

**Key files:**
- `fee-tracker-config.json` — Position wallet, APY, fee tier, pool address
- `fee-tracker-state.json` — Running totals, period tracking, history

**Known calibration number (verified Jul 2, 2026):** $46.43 position earns $0.44/day (345.8% effective APY for concentrated bid-ask on high-volume pool).

> **Full workflow:** references/lp-monitoring-workflow.md

---

## 2. Rebalance Workflow

### ⚠️ CRITICAL: Config-First Principle (NEW)

**NEVER guess shape, entry price, or range from on-chain data alone.** The user sets these on LFJ manually. The AI's job is to:

1. **ASK** the user what they deployed (shape, range, entry price)
2. **WRITE** the config from their answer (source of truth)
3. **VERIFY** against on-chain data (reader confirms, doesn't infer)

**This prevents the read-back failure loop:**
```
❌ Before: User sets CURVE → Reader says "Curve" (but from config default, not on-chain) → AI shows wrong data → User corrects
✅ After:  User says "CURVE $6.40-$6.55 entry $6.48" → AI writes config → Reader verifies match → Done
```

**If the user doesn't provide shape/entry — ASK THEM.** Don't look at the reader output and make assumptions. The `run-reader.sh` defaults shape to `curve` and the reader doesn't detect shape from on-chain — it echos whatever `--shape` was passed.

### Two Input Modes

1. **Screenshot mode** — parse LFJ screenshot for range, shape, balances
2. **Direct params mode** — Jordan gives exact values: "rebalance: entry X, shape Y, range Z-W"

### 7-File Update Protocol

After EVERY rebalance, update ALL of these:

| # | File | What to update |
|---|------|---------------|
| 1 | `.lfj-position-tracker.json` (×2) | range, shape, entry price, amounts |
| 2 | `defi-data.json` (×4-5 copies) | hero, lpPosition, curveData, strategyAdvisor |
| 3 | `.lfj-aae-config.json` (all 9 copies) | position.range_low/high, shape |
| 4 | `defi-lp-config.env` | RANGE_LOW, HIGH, SHAPE, POSITION_USD |
| 5 | `run-reader.sh` | SHAPE default |
| 6 | `defi-master-cron.py` | POOL dict |
| 7 | `defi-dashboard.html` | Hardcoded values in fetchLiveData() |
| 8 | `hub.html` | RANGE_LOW, RANGE_HIGH, SHAPE constants |

### Config File Locations (9 copies of .lfj-aae-config.json)

```
~/.hermes/scripts/.lfj-aae-config.json
~/.hermes/profiles/gentech/scripts/.lfj-aae-config.json
~/.hermes/profiles/gentech/.hermes/scripts/.lfj-aae-config.json
~/.hermes/profiles/gentech/home/.hermes/scripts/.lfj-aae-config.json
~/.hermes/profiles/gentech/home/portfolio/Strategies/scripts/.lfj-aae-config.json
~/.hermes/profiles/gentech/home/portfolio/.lfj-aae-config.json
~/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-aae-config.json
~/.hermes/profiles/dmob/home/.hermes/scripts/.lfj-aae-config.json
~/.hermes/profiles/desmond/home/.hermes/scripts/.lfj-aae-config.json
```

### Shape-Aware Efficiency (BIN-WEIGHTED — Updated Jul 5, 2026)

**Critical Fix:** The simplified efficiency model capped bid-ask at 75%, but actual bin-weighted efficiency reaches 100% at range edges. Use the corrected formula below.

```python
def calc_efficiency(price, range_low, range_high, shape):
    """
    BIN-WEIGHTED: bid-ask peaks at edges (100%), valley at center (50%).
    Position in range as percentage (0 = low edge, 100 = high edge)
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

**Efficiency by Shape:**
| Shape | Center (50%) | Near Edge (75-90%) | Edge (0%/100%) | Out of Range | **Pitfall** |
|-------|--------------|-------------------|----------------|--------------|-------------|
| Spot | — | — | 100% | 0% | — |
| Bid-Ask | **50%** | 75-90% | **100%** | 0% | **0% REAL FEES if price between edges** — no bins are crossed |
| Curve | **100%** | 75-90% | 60% | 0% | — |
| Bidirectional | 100% | 75-90% | 100% | 0% | — |

**⚠️ BID-ASK REALITY:** The efficiency formula shows 50-100% across the range, but in practice **when price is between the bid and ask edges, NO bins are crossed and NO fees are earned.** The "efficiency" reflects bin distribution density, not actual fee-earning status. Always check: is price at an edge? If not, bid-ask is earning $0/day regardless of what the efficiency % says.

**Files using this formula:**
- `/root/.hermes/scripts/lp-position-reader.py` — Line 320-344
- `${PROFILE_DIR}/scripts/lp-monitor-v2.py` — Line 66-97

### Bin Generation

**Curve:** Peak at center, taper at edges. `depth = 0.05 + 0.95 * (1 - dist_from_mid / max_dist)`
**Bid-Ask:** Peak at edges, low at center. `depth = 0.05 + 0.95 * (1 - dist_from_mid / max_dist)` with center dip.
**Spot:** Single peak at current price.

### Verification

```bash
# Check all configs match
python3 -c "
import json, glob
for f in glob.glob('/root/.hermes/**/scripts/.lfj-aae-config.json', recursive=True):
    with open(f) as fh: c = json.load(fh)
    p = c.get('position', {})
    print(f'{f} → {p.get(\"range_low\")}-{p.get(\"range_high\")} {p.get(\"shape\")}')" 
```

### Deploy & Verify Intelligence (NEW)

**READER VERIFICATION PROTOCOL — DO NOT INFER SHAPE:**

The on-chain reader (`run-reader.sh` → `reader.mjs`) accepts `--shape` as a CLI argument. It does NOT detect shape from on-chain data. The shape line in its output is whatever was passed via `--shape` or the default in the script.

**Default shape in run-reader.sh:** `curve` (was `bid-ask` for one session, changed back Jul 19, 2026).

**Verification pattern (use this every rebalance):**

1. User says: "I set CURVE at $6.40-$6.55 entry $6.48"
2. AI writes config: shape=curve, range_low=6.4039, range_high=6.5463, entry_price=6.48
3. AI runs reader: `SHAPE=curve bash run-reader.sh` (or export SHAPE=curve first)
4. AI compares reader output vs config — flag if mismatch
5. If mismatch: "You said CURVE but on-chain shows 23 bins at edges — did you deploy bid-ask?" → ask, don't auto-correct

**Never auto-correct reader data into config.** The reader writes to defi-data.json with whatever shape was passed. If the wrong shape was passed, the dashboard shows wrong data until corrected.

---

## 4. Strategy Design

### Regime → Shape Mapping

| Regime | Shape | Range | DCA |
|--------|-------|-------|-----|
| Range-bound | Curve | Tight (3%) | Steady |
| Bull confirmed | 25% LP + 75% spot | — | Capture trend |
| Bear confirmed | Bid-Ask or LP | Wide (6%) | Conservative |
| Volatile | Bid-Ask | Max (8%) | Opportunistic |
| Uncertain | Wide-range LP | Max | Maximize range |

### Regime-Switching Framework (NEW — Jul 19, 2026)

**Two distinct regimes, two default shapes:**

| Regime | Shape | When | Behavior |
|--------|-------|------|----------|
| **Chop / No Direction** | **CURVE** | Between macro events, consolidation, F&G 25-40 | Set and forget. All bins earn as price oscillates. |
| **Macro Event** | **Bid-Ask** | 24h before Fed/CPI/NFP/geopolitics | One edge catches the move. Peak efficiency. |

**Switch timing:**
- CURVE → Bid-Ask: 24h before FOMC (Jul 29-30 next), CPI, NFP
- Bid-Ask → CURVE: 24h after event, once volatility settles

**Next scheduled events:** Check `fed-event-tracker.py` or the macro calendar cron.

**Tactical Retreat — Active Defense Loop (NEW — Jul 19, 2026)**

Full spec at repo `DeFi/aae-tactical-retreat.md`. High-level:

```
DEPLOY → EARNING → BREAKOUT? → HOLD 2-5min → RETREAT to USDC → SENTINEL → RE-ENTER
```

| Phase | Action | Timing |
|-------|--------|--------|
| Deploy | Position set as CURVE or Bid-Ask | Per strategy |
| Earning | Normal LP monitoring | Every 10 min |
| Breakout detected | Price exits range — start timer | Immediate |
| Hold 2-5 min | Wait for re-entry or further break | 2-5 min |
| Retreat | Convert to 100% USDC (stop-loss) | After timer |
| Sentinel | Monitor F&G, volume, consolidation, macro calendar | Every 30 min |
| Re-enter | 3 of 4 signals positive → deploy | On signal |

**Sentinel signals for re-entry:**
1. Fear & Greed rising above 35 (from Extreme Fear)
2. 1h volume returning to 24h average
3. Price consolidating in a narrow range for 2+ hours
4. Macro calendar clear for 48+ hours

### "Go Spot" Signals (3+ = exit 75% LP)

1. Price holds above level for 48h+
2. BTC trend confirmation
3. Macro pivot signal
4. Volume 2x average
5. Higher lows pattern

### Shape Selection

| Condition | Best Shape |
|-----------|-----------|
| Choppy/ranging | Curve |
| High volatility, no direction | Bid-Ask |
| Strong bullish breakout | Exit → spot |
| Crash/panic dump | Skewed curve (70% stablecoin) |
| Consolidation after rally | Curve at new range |

### ⚠️ The Real Cost Is Divergence, Not Fees

A concentrated LP book **sells its upside away** as the price rises and **buys it back** as the price falls. Fees are real and durable, but they are the headline; divergence is the bill. In a measured window (30 days of real swap history, AVAX/USDC concentrated position), the curve-like shape earned **$106.82 in fees** yet lost **$88.37 to divergence** and finished behind HODL.

**This flips the way you read a report:**
- High fee efficiency / high daily fees → **good**, but not enough
- Low divergence / high ending value vs HODL → **the real score**
- A shape that rebalances 133 times in 30 days → **a treadmill**, not a strategy

**Rule:** do not optimize for fees alone. Optimize for **net value vs the simplest alternative** (HODL, or the static range you would have held anyway).

### Regime → Instrument (Updated 2026-09-30)

| Regime | Primary instrument | Why |
|---|---|---|
| **Chop / range-bound** | **Concentrated LP** (curve or bid-ask) | Earns fees as price oscillates |
| **Trending up** | **HODL the asset** | Concentration sells the upside; HODL keeps it |
| **Trending down** | **Stable / hedge** | Stop paying divergence, preserve capital |
| **Euphoria** | **Exit market making → full asset** | The most expensive thing to do at the top is keep selling rallies |
| **Bullish consolidation / accumulation** | **BID_ONLY** | Hold spot + bid ladder: keeps all upside, collects fees above the bids, DCA's every fill |

**Perpetuals are available for both directions, not only shorts.** Funding rates determine whether
a long pays or earns: when funding is positive, longs pay shorts, so a **short earns** and a **long
pays** a carrying cost. That makes a cash-and-carry (hold spot + short the perp) a delta-neutral
funding-yield strategy — a genuine bank-account-shaped return that the LP farm cannot provide. Do
not describe perps as "only for shorting"; describe them by their cost and their directional fit.

**This makes the treasury a cycle instrument, not a perpetual fee machine:** farm the chop, hold the euphoria, accumulate the dips.

### The BID_ONLY hybrid — spot upside + fee capture + DCA

When the operator says "accumulating and loading the spring," the correct instrument is not a
two-sided spread. A bid-ask or a curve **sells the upside** by construction — the ask side
converts WAVAX to USDC as price rises. The hybrid that preserves the thesis is:

- **Spot WAVAX held outright** — keeps 100% of the upside, no ask side.
- **USDC deployed as a bid-only ladder** below spot — earns fees while price chops above it, and
  every fill automatically buys the dip.

This resolves the **bank-account vs beat-holding** conflict rather than splitting the difference:
- It is **not** a bank account (it is long AVAX).
- It is **not** a pure hold (it earns fees and DCA's lower).
- It removes the exact divergence cost that made managed shapes lose to HODL: **there is no ask
  side to sell rallies.**

**When to use it:**
- Bullish trend expected to continue.
- Operator wants to **buy dips, not sell rips**.
- Willing to be ~90%+ in the asset (the bid ladder only softens the entry; it is still a
  directional position).

**When NOT to use it:**
- Range-bound chop with no trend expectation (use a curve instead).
- Deep bear or risk-off (it is still long the asset; use stables).
- Operator needs stable income regardless of price direction (use a balanced two-sided book).

**Implementation pattern:** withdraw the two-sided book to free both legs, hold the full WAVAX
amount as spot, then deploy the USDC leg as a `bid` with `kind=uniform` (or a decayed weight)
reaching down to the target accumulation zone. **Do not** leave an ask leg attached.

**Verification after build:** confirm the on-chain position contains only `bid` bins; there must
be zero ask-side ownership. The wallet balance will show WAVAX (spot) plus the LP position. Report
both as a combined exposure table so the operator sees the actual asset concentration.

> **Full decision table and worked examples:** references/bid-only-hybrid-shape.md

### Operator Shape Directive — the machine does not outrank the user

When the operator explicitly chooses a shape and split, that choice is the authority. Fee efficiency,
regime labels, and classifier outputs are inputs — they are not the decision. A machine that silently
rebuilds the book into a "higher-efficiency" shape after the operator chose a different one has
**overridden the operator**, not optimized the position.

**This requires a persisted directive, not a conversation-state assumption.** The operator may tell
you in chat, but the watchdog runs from files. The directive must be written where the re-centering
loop reads it, with a clear scope and an expiry/clear condition.

Minimum fields for an operator shape directive:
- `shape` — curve / bid-ask / spot
- `split` — token/stable ratio or explicit amounts
- `set_at` — timestamp
- `reason` — one-line operator rationale
- `escalate_if` — conditions that should surface for confirmation (e.g. efficiency below X% for Y min)
- `expires_at` or `auto_clear_on` — when the machine may resume autonomous shape selection

**Behaviour:**
- While the directive is active, the machine **holds the shape** and reports `SHAPE OVERRIDE HELD`.
- It still monitors efficiency, divergence, and range status — and reports them.
- It may propose a switch, but it does not execute one without operator confirmation.
- If the directive has no expiry, the operator must clear it; never infer expiry from market movement.

**When the operator's choice conflicts with the efficiency model, say so plainly and hold the choice.**
A bid-ask near its natural trough will read 25% while a curve at the same spot reads 75%. That is not
a bug in the model — it is the cost of the operator's thesis. Report both numbers and the override.

### Directive durability — a directive that does not survive the loop is not a directive

**Write the directive into the vault as DATA, not into the conversation or a running script.** The
watchdog that acts on it reads files, not chat history. The canonical record must live in the vault
first and be enrolled in the sync manifest so the profile copy the cron executes cannot drift back
to a version without it. A directive that exists only in the vault copy the human sees is invisible to
the machine; one that exists only in the profile copy is overwritten by the next sync.

**A directive set as material must survive every later materiality reset.** The cascade path or an
operator override may set `MATERIAL=1` early in the script, but if a classification block resets
`MATERIAL=0` later in the same scope and no restoring path can see the override, the most important
condition the script can detect is delivered as a non-material advisory. Decide materiality ONCE,
after all action, using the output that proves it — or explicitly restore the override flag after any
reset.

**If the directive file cannot be read, the failure must be LOUD.** A missing or malformed directive
must print `UNREADABLE OPERATOR DIRECTIVE` and refuse to act on efficiency alone. Falling back
silently to the autonomous path means the operator's instruction was overridden by default.

**A directive is not done when it is written — it is done when the running copy reads it.** After
writing, sync, then run the watchdog once and inspect its stdout for the directive line. No line
means the file is in the wrong path, not in the manifest, or the reader is looking elsewhere.

**A fork is when two reasonable readings of the same market point to different shapes or actions and
the choice is material.** When you detect a fork:
1. State the fork in one sentence, with the two readings and the capital at stake.
2. **Pause the autonomous path** so it cannot act on either reading while the operator decides.
3. Present 2–3 explicit options with the shape, split, and expected exposure of each.
4. Log the paused state and the reason.

Do not pick the "higher-efficiency" option as the default. Do not average the options. Do not deploy
a compromise shape (a widened curve is not a bid-ask; a 60/40 curve is a different bet). The operator
calls the shape; the machine executes it cleanly.

> **Worked example and reference implementation:** references/operator-shape-directive.md

### Every LP ledger must record our income, not just the pool's

A position ledger that records geometry (`bins`, `range`, `value_usd`, `efficiency`) but never OUR
accrued income lets a book sit for a month at 2% while the operator assumes it is working. The
ledger must publish a measured income figure: **our share, in dollars, over a stated window**, and
it must be keyed to the shape in force.

**Three rules:**
1. **Key the income to the shape.** A curve window and a bid-ask window are not the same measurement;
   averaging them across a shape change manufactures a number that belongs to neither.
2. **Reset the baseline after a rebuild.** `fee_factor` is cumulative fees **per unit of liquidity**,
   and a rebuild changes the liquidity. A naive delta across a rebuild measures the rebuild, not the
   earnings.
3. **Never interpolate across a shape change.** If a window contains a rebuild or shape switch, write
   `null` with the reason. A derived number across the boundary is worse than no number.

**A ledger whose every snapshot carries `fees_usd: null` is an unmeasured position.** A position whose
income cannot be stated is an experiment and must be labelled one.

### The same abstraction holds across all rails, but the read path differs

Every DEX that uses concentrated liquidity tracks fees as a **cumulative amount per unit of our share**.
Build the income tracker on that abstraction, with one adapter per rail. Writing it per venue means
writing it three times and the third will disagree with the first about what "income" means.

| Venue family | Where | How our fees are read |
|---|---|---|
| **LFJ Liquidity Book** (Avalanche) | bin-based | per-bin cumulative fee accumulator (`fee_factor`) × our share of each bin |
| **Meteora DLMM** (Solana) | bin-based (same family) | **accrued fees exposed per position** (`feeX` / `feeY` on the position account) — directly readable, no share-denominator math |
| **Uniswap v3/v4** (Ethereum, the TAO pools) | tick-based | `feeGrowthGlobal0/1X128` × our liquidity |

**Two rules that apply everywhere:**
- **Never compute a fee delta across a change in our share** — a rebuild, re-centre, add, or remove resets the meaningful baseline. Write `baseline_reset` and start a new window.
- **Fees and reward emissions are separate income** and are shown separately. A venue paying mostly in emissions is a promotion, not a yield.

**Why this is a precondition for Solana, not an afterthought:** a Meteora rebalance costs ~$0.001–0.01 against ~$0.19 on Avalanche. **A cheap re-centre is only a good idea if we can measure whether it earned more than it cost.** The income tracker makes the Solana test a measurement instead of a feeling.

> **Worked example and reproduction recipe:** references/held-asset-yield-scan.md

### Yield discovery scans held assets, not the whole market

A general yield leaderboard is noise — it surfaces 4,000% APYs on tokens the treasury will never own.
The useful question is: *is there a new venue for an asset we already hold?* Hold that search separate
from the rail/buy-list watch; one asks whether to buy, the other asks where to put what we own.

**Filters that prevent garbage results:**
- Every token in the pair must be in the held-asset set. Matching on *any* shared symbol part (e.g.
  every `SOMETHING-USDC` pool) produces hundreds of false positives.
- The chain must be a rail we can reach.
- A TVL floor and an APY sanity ceiling keep artefact pools out.
- Fee yield (`apyBase`) and reward emissions (`apyReward`) are reported separately; sort by the
  durable one first.
- Stablecoin pools paying >60% get a warning, not a recommendation.

**Silence doctrine applies:** alert once when a new venue appears or an old one disappears; an empty
stdout means no message. Seed the watch state on first deployment so the cron starts quiet.

> **Full scan recipe and verification checklist:** references/held-asset-yield-scan.md

### Income tracking must be one abstraction across rails, not one reader per venue

Concentrated-liquidity venues all track fees the same way: **cumulative fees per unit of our share**.
Build the income tracker on that abstraction with one adapter per rail, or you will write the same
logic three times and the third version will disagree with the first about what "income" means.

- **LFJ Liquidity Book** (Avalanche, bin-based): per-bin `fee_factor` × our share of each bin.
- **Meteora DLMM** (Solana, bin-based): `feeX`/`feeY` per position — directly readable, no share math.
- **Uniswap v3/v4** (Ethereum, tick-based, the TAO pools): `feeGrowthGlobalX128` × our liquidity.

**Rules that apply everywhere:** key the income to the active shape, reset the baseline after any
change in our share (rebuild, re-centre, add, remove), never interpolate across a shape change, and
keep fees separate from reward emissions.

> **Implementation recipe and verification checklist:** references/cross-rail-income-tracker.md

### Escalate genuine forks, do not resolve them alone

A fork is when two reasonable readings of the same market point to different shapes or actions and
the choice is material. Examples:
- Regime says curve, price action says breakout.
- Efficiency model says curve, operator previously said bid-ask.
- Two messages from the operator point in opposite directions.

**When you detect a fork:**
1. State the fork in one sentence, with the two readings and the capital at stake.
2. Pause the autonomous path so it cannot act on either reading while the operator decides.
3. Present 2–3 explicit options with the shape, split, and expected exposure of each.
4. Log the paused state and the reason.

Do not pick the "higher-efficiency" option as the default. Do not average the options. Do not deploy
a compromise shape (a widened curve is not a bid-ask; a 60/40 curve is a different bet). The operator
calls the shape; the machine executes it cleanly.

### Backtest Before You Decide

When the user asks "which shape?" or "should I be market making?", do not answer from doctrine.
Run `mcp__vfat__backtest_strategy` (or the equivalent live rail) on a comparable pool over at
least one full regime window, then compare against HODL and a static range.

**Key inputs to hold constant across runs:**
- Same pool / same fee tier / same deposit size
- Same days / same swap history
- Same auto-rebalance delay
- Only vary the geometry (shape, width, skew)

**The comparison must include:**
- Fees earned
- Costs (gas, swap impact)
- **Divergence** (the shape's PnL drift from HODL)
- **Rebalance count** (a first-class metric — high count = high churn)
- Ending value vs HODL
- Time in range

**Then match to the regime.** A shape that wins in chop may lose in a trend; that is expected,
not a bug. The rule is: **instrument follows regime.**

> **Worked example and reproduction recipe:** references/backtesting-shape-vs-regime.md

### Audit First, Then Shape

A shape decision is only as good as the *state* it is built from. Before deciding, prove:
1. **Which venue** is actually holding the money (LFJ V2.2, Blackhole, Meteora, etc.).
2. **Which pool** within that venue (contract address, binStep/tickSpacing, fee tier).
3. **Whether the position is empty, partial, or whole** — scan the actual bin ranges and owned NFTs.
4. **What shape is on-chain** vs what the user says — both can be wrong if a stale run raced a redeploy.
5. **Whether any operator directive** is active; if so, it outranks the efficiency model.

Failure to do this produces the worst kind of error: a correctly executed trade into the wrong
premise. Verify the venue and position before every deploy/withdraw/rebalance.

> **Consolidation/audit scope traps:** references/audit-consolidation-scope-traps.md

### Levels retire when the market clears them

A price level is only a reference while the market respects it. Once price moves cleanly through it
and holds on the other side, the old level stops being a meaningful entry target. A machine that
keeps waiting for a retest of a cleared level will miss the move and may deploy capital into air.

When a key level is cleared:
1. Record the level, the direction, and the closing confirmation in the position log.
2. Mark the level as **retired** in the strategy context; do not use it as the primary reference for
   new entries.
3. Replace it with the next structural level in that direction (next support above, next resistance
   below) or a regime-based range.
4. State the retirement out loud when reporting the next shape decision.

This applies to any level the operator has been anchoring on: prior swing low, DCA target, range
boundary, or macro line. A level does not retire on a wick — it retires on a confirmed break.

> **Full strategy design:** references/strategy-design.md

---

## 5. On-Chain Position Reading

### LFJ V2.1 (Avalanche)

**Pool:** `0x864d4e5ee7318e97483db7eb0912e09f161516ea`
**RPC:** `https://api.avax.network/ext/bc/C/rpc`

| Selector | Function | Returns |
|----------|----------|---------|
| `0xdbe65edc` | activeId() | Current bin ID |
| `0x0902f1ac` | getReserves() | reserve0 (AVAX), reserve1 (USDC) |
| `0xe77366f8` | getSwapOut(1e18) | USDC amount for 1 AVAX |
| `0x00fdd58e` | balanceOf(addr, binId) | User shares in bin |
| `0xbd85b039` | totalSupply(binId) | Total shares in bin |

**Position scan:** ±200 bins from active. Calculate share: `userLiquidity / totalSupply * binReserves`.

**⚠️ EIP-1167 proxy:** `balanceOf` reverts with raw `eth_call`. Use viem multicall with SDK ABI. See Node.js approach in references.

### On-Chain Entry Detection (UPDATED)

LFJ V2.2 uses **TransferBatch** events (not TransferSingle) for ERC-1155 bin shares:

- **Topic0**: `0x4a39dc06d4c0dbc64b70af90fd698a233a518aa5d07e595d983b8c0526c8f7fb`
- **Topic3** (`to`): wallet address = deposit, `0x0` = withdrawal
- **Topic2** (`from`): `0x0` = mint, wallet address = withdrawal

**Search pattern:** Scan eth_getLogs backwards in 2048-block chunks. First event with `to=wallet` is the entry. Cache the result — don't re-query every time.

**RPC limit:** Public Avalanche RPC caps at 2048 blocks per eth_getLogs. BlockRun RPC ($0.002/call) handles wider ranges.

**Parsing TransferBatch data** — `data` field is ABI-encoded: offset (32B), length (32B), bin_ids[], values[]. Decode to get all bins deposited.

**4-Hour Active Day Rule (NEW):**

User requirement: "If you're in the pool for at least four hours, that counts as a day." This accommodates scenarios where the user rebalances multiple times in a day but was still active earning fees.

**Active day calculation logic:**
```python
for day in each_day():
    time_in_pool = 0
    deposit_events = filter(deposits, date=day)
    withdraw_events = filter(withdrawals, date=day)
    
    for deposit, withdraw in zip(deposit_events, withdraw_events):
        time_in_pool += withdraw.timestamp - deposit.timestamp
    
    # Events spanning day boundaries carry over
    if time_in_pool >= 4 hours OR num_events >= 3:
        active_days += 1
```

**User insight on asymmetry:** "On the right edge (selling into strength), it's not too much of a big deal to rebalance. But if you're breaking down [left edge], now impermanent loss is just kind of eating at you and you're not earning. It's like a double negative if you don't rebalance on the lower edge."

**Cache file:** `.lfj-entry-cache.json` stores:
- `first_deposit_block`: Block number of first entry
- `first_deposit_tx`: Transaction hash
- `first_deposit_date`: YYYY-MM-DD
- `active_days_4h`: Days with 4+ hours in pool (de-duped)
- `total_deposits`: Number of deposit events
- `total_withdrawals`: Number of withdrawal events (rebalances)

**User confirmation:** "I love having the fee trajectory, having the position and the on-chain activity. Fantastic. Because now I can see I've been active a long time. Wow, that's crazy." — The on-chain entry detection provides exactly this visibility for the AAE reputation system.

> **Full workflow:** references/onchain-entry-detection.md

**Production reader:** `/root/projects/lp-reader/reader.mjs` — Node.js + viem + LFJ SDK ABIs

> **Full reading guide:** references/onchain-reading.md

---

## 6. LFJ Orchestration

### Script Matrix

| Script | Purpose | Frequency |
|--------|---------|-----------|
| `defi-milestone-summary.py` | Daily executive snapshot | Once daily |
| `defi-master-cron.py` | Consolidated watchlist + LP + DCA | 4× daily |
| `lp-aae-signal-monitor.py` | AAE signal generation | On-demand |
| `lp-unified-monitor.py` | Silent range + milestone monitor | Every 5-10min |
| `lfj_monitor.py` | Price + wallet tracker | 4× daily |
| `lp-position-reader.py` | On-chain bin decoding | On-demand |
| `defi-lp-consolidated.py` | Primary monitor — alert-once | Every 10min |
| `lp-monitor-v2.py` | Config-first LP monitor with fee tracking | Every 10min |
| `fee-tracker.py` | Legacy — absorbed into lp-monitor-v2.py | REMOVED Jul 2, 2026 |
| `reader.mjs` | On-chain position reader | Every 3 hours |

### Fee Tracker Config Files (merged into LP Monitor)

| File | Purpose |
|------|---------|
| `fee-tracker-config.json` | Position wallet, APY override, fee tier |
| `fee-tracker-state.json` | Accumulated daily/weekly/monthly/all-time totals |

**⚠️ Config position amounts go stale.** The `.lfj-aae-config.json` has position amounts manually set. After deposits, withdrawals, or rebalances, the amounts drift from reality. The LP monitor will show the wrong position value until the config is updated. Only the on-chain reader (queued in build queue) can fix this permanently.

### Config Files

| File | Location | Purpose |
|------|----------|---------|
| `.lfj-aae-config.json` | 9 copies across profiles | Position + milestones |
| `.lfj-position-tracker.json` | 2 copies (global + profile) | Primary source of truth |
| `.lfj-aae-state.json` | 5 copies | Persistent state |
| `defi-lp-config.env` | HQ/config/ | Cron env vars |
| `defi-data.json` | 4-5 copies | Dashboard data |

### Verification Scripts

**Entry Price Field Validator** (`scripts/entry-price-field-validator.py`):
```bash
# Check for conflicts
python3 scripts/entry-price-field-validator.py

# Auto-fix conflicts
python3 scripts/entry-price-field-validator.py --fix

# Preview changes
python3 scripts/entry-price-field-validator.py --dry-run
```

**Entry Price Fix Protocol** (`scripts/fix-entry-price.py`):
```bash
# Fix entry price sync issues when cron shows outdated data
python3 scripts/fix-entry-price.py --range LOW HIGH

# Example: Fix after rebalance to $6.40-$6.62 range
python3 scripts/fix-entry-price.py --range 6.4039 6.6186
```

**Quick Health Check** (<30s): `python3 defi-milestone-summary.py`
2. **Full Signal Analysis** (<60s): `python3 lp-aae-signal-monitor.py`
3. **Consistency Verification**: diff configs across scripts
4. **Deep Dive** (if needed): `python3 lp-position-reader.py` + `lfj_monitor.py`

### Cron Architecture

| Job | ID | Schedule | Purpose |
|-----|----|----------|---------|
| On-Chain Reader | `4cb4f1e92116` | `*/10 0-23 * * *` | Reads position, writes defi-data.json |
| DeFi Monitor | `2600f8fc0f0e` | `3,13,23,33,43,53 11-23,0-2 * * *` | Shape-aware efficiency alerts |

**⚠️ Reader and monitor MUST be staggered 3+ minutes.** They share defi-data.json. Reader fires at :00/:10/:20/:30/:40/:50, monitor fires at :03/:13/:23/:33/:43/:53 — always 3min after reader.

**⚠️ Schedule coverage must overlap.** Both jobs must run during the same hours. If the reader skips hours the monitor covers, defi-data.json goes stale and preflight flags it. (Fixed Jun 22, 2026 — reader was `6-23` UTC but monitor includes `0-2` UTC.)

**Cron health check after any script change:**
```bash
# Verify no non-zero exit codes in monitoring scripts
grep -n "sys.exit(1)\|sys.exit(2)" ~/.hermes/profiles/gentech/scripts/defi-lp-consolidated.py
# Should return nothing — all alerts are in stdout, exit always 0
```

> **Full orchestration:** references/lfj-orchestration.md

---

## 7. Fee Milestone System

### Tier Ladder

| Tier | Label | Target | Unlocks |
|------|-------|--------|---------|
| 0 | 🔭 Scout | $5/day | AVAX-USDC, learn the pool rhythm |
| 1 | ⚔️ Raider | $10/day | Deepen AVAX-USDC position |
| 2 | 🏛️ Greek | $20-30/day | AVAX-USDC + start TAO/SOL on Meteora |
| 3 | 🛡️ Warrior | $50+/day | Full multi-chain deployment |
| 4 | 👑 Sovereign | $100+/day | Custom strategy creation |
| 5 | 🏰 Warlord | $200+/day | Avalanche L1 funding tier |

### Progress Bar Format

```
Current: Tier 0 — Scout ($5.0/day)
Next: Tier 1 — Raider ($10.0/day) [24%]
```

### Milestone Display Logic

When daily fees < $5/day, display:
- **Current**: Tier 0 — Scout ($5.0/day)
- **Next**: First config milestone (Raider at $10/day)
- **Progress**: `(daily_fees / 5.0) * 100`%

### Fee Estimation (TVL-Weighted)

```python
pool_daily_fees = volume_24h × (fee_tier_bps / 10000)
pool_share = our_position / pool_tvl
estimated_daily = pool_daily_fees × pool_share × cl_multiplier (3.0x active)
```

### Fee Trajectory Report (Actual Accrued)

The LP monitor's Fee Trajectory section shows the **daily rate** as the headline, with **prorated today** underneath:

```
📈 Fee Trajectory
  Daily:    $0.2400 rate         ← the key number (matches LFJ UI)
  Today:    $0.1222 accrued      ← prorated by time of day
├─ Week:    $1.68
├─ Month:   $7.32
├─ Year:    $87.60 projected
└─ All-time: $0.02
```

- **Daily**: Full daily rate (from on-chain reader or calibrated yield rate)
- **Today**: Prorated by hour-of-day so it climbs to match the daily rate by midnight
- **Week/Month/Year**: Multiples of the daily rate
- **All-time**: Cumulative from fee tracker state

**User preference**: The daily rate must be the headline — never show the prorated "Today" as the primary number. The user looks at the daily rate to see what they're earning.

### Fee Calculation — Yield Rate Method

When On-chain reader fees aren't available, calculate from position value:
```python
DAILY_YIELD_RATE = 0.00515  # calibrated: $0.24/day on $46.59 position
live_daily = round(position_value * DAILY_YIELD_RATE, 4)
```

Calibrate the yield rate by dividing LFJ UI daily fee by position value: `$0.24 / $46.59 = 0.00515`.

Write the calculated fee back to `defi-data.json` so the dashboard and cron stay in sync.

**⚠️ NEVER use bin-level share_pct as pool share.** It produces impossible estimates ($966/day for $178 position).

---

## 8. Security Intelligence

Post-incident recon: official blogs, governance proposals, competitor responses, on-chain stats.

**Risk Rubric:** IMPROVED (protocol upgrade) | UNCHANGED (no change) | WORSENED (new vectors)

> **Full workflow:** references/security-intel.md

---

## 9. External APIs & Integrations

- **Arsenal API** — 70+ DeFi skills (Jupiter, DefiLlama). No LFJ yet.
- **GOAT SDK** — 200+ plugins, MCP support. Potential middleware.
- **Krexa** — Agent credit infrastructure on Solana.
- **Circle Arc** — Stablecoin-native L1 (testnet only as of Jun 2026).
- **Oracles** — Pyth (Solana prices), Switchboard (custom feeds), RedStone (high-freq), API3 (external APIs).

> **Full integrations:** references/external-apis.md

---

## 13. Decision Engine Integration

### Autonomous Decision-to-Task Pipeline

When Jordan provides strategy rules (e.g., "60/40 allocation", "$6 AVAX trigger"), implement the **Decision Engine → Build Queue → Autonomous Execution** pattern:

**Decision Engine** (`scripts/defi-decision-engine.py`):
- Implements user's specific strategy logic
- Outputs decisions in JSON format with confidence scoring
- Integrates market regime detection and portfolio optimization

**Build Queue Integration** (`scripts/defi-build-queue-integration.py`):
- Converts decisions to priority-queued tasks
- Maps decision types to execution protocols (Trader Joe, Black Hole, etc.)
- Handles task format, priority assignment, and verification

**Key Integration Pattern**:
```python
# Priority mapping based on decision type
priority_mapping = {
    'rebalance': 'MEDIUM',
    'accumulate': 'HIGH', 
    'deploy': 'HIGH',
    'hold': 'LOW',
    'reduce': 'MEDIUM'
}

# Protocol-specific execution handlers
protocol_handlers = {
    'AVAX/USDC_LP': self.execute_trader_joe,
    'BLACK_HOLE_POOL': self.execute_black_hole,
    'LP_POSITIONS': self.execute_lp_optimization,
    'DCA_TARGET': self.execute_dca
}
```

**Usage**: Run full integration cycle: `python3 scripts/defi-build-queue-integration.py`

### Decision Engine Configuration

**Jordan's Strategy Example**:
- Core Allocation: 60% BTC / 40% ETH  
- AVAX Trigger: Heavy accumulation below $6, light accumulation above
- Yield-farm cadence: $20–$150 every TWO WEEKS into AVAX/SOL yield (the farm doubles as an entry-timing signal — a pullback there is a good buy)
- Normal accumulation: add on good entries outside the scheduled cadence
- Rebalance Threshold: 5%
- Time Horizon: 3 months bearish outlook

**Regime Detection**:
- **Bull**: Trend up, volume spike, RSI > 70
- **Crash**: Rapid dump, volume spike, RSI < 30  
- **Sideways**: Range-bound, low volatility, fee harvesting mode

> **Reference:** `scripts/defi-decision-engine.py` for implementation examples

---

## 14. Real-Time Dashboard Architecture

### Dashboard Creation Workflow

For DeFi monitoring dashboards, use the **HTML + JavaScript + Data Feed** pattern:

**Component Structure**:
- `/gentechlabs.github.io/DeFi/` (GitHub Pages deployment)
- HTML dashboard with live data binding
- JSON data feed (`defi-data.json`) updated periodically
- CSS animations for pool performance visualization

**Key Elements**:
- Portfolio overview with real-time metrics
- Market regime indicators
- Decision recommendations with confidence bars
- Pool performance cards with APY/TVL data
- Animated progress bars and shimmer effects

**Deployment Pattern**:
```bash
# Update data feed
cp vault-data.json /gentechlabs.github.io/DeFi/data.json

# Deploy to GitHub Pages
cd gentechlabs.github.io && git add && git commit -m "Update dashboard" && git push
```

**Data Feed Requirements**:
- ALL top-level keys MUST exist or dashboard sections break
- Use number types, not strings, for numeric calculations
- Include real-time updates with simulated data feeds

> **Reference:** `/gentechlabs.github.io/DeFi/defi-suite-dashboard.html` for dashboard template

---

## 15. MCP Integration Strategy

When MCP servers don't exist (common issue), use **Real Protocol Tools + Wrapper Integration** instead of chasing phantom servers:

**Pattern**: 
1. Check MCP registry for actual servers
2. Use existing protocol tools (Trader Joe SDK, Black Hole APIs)
3. Build wrapper layer for integration
4. Document real server availability

**Available Servers** (as of June 2026):
- `ampersend`, `blockrun`, `coinbase`, `hive`, `pay`, `brickken`, `wurm`, `q402`, `composio`

**Configuration**:
```yaml
mcp_servers:
  trader_joe:
    command: npx -y @modelcontextprotocol/server-traderjoe
    env:
      TRADER_JOE_RPC: "https://api.avax.network/ext/bc/C/rpc"
  
  black_hole:
    command: npx -y @modelcontextprotocol/server-black-hole
    env:
      BLACK_HOLE_RPC: "..."
```

**Strategy**: When official MCP servers don't exist, use direct protocol APIs via Python HTTP clients or SDKs.

> **Reference:** `designs/defi-mcp-integration-revised.md` for full strategy

---

## Critical Pitfalls (Top 30)

1. **HERMES_HOME resolves to profile dir** — Always update BOTH global and profile-specific state files
2. **run-reader.sh shape default** — Must match current shape after rebalance. Reader passes `--shape $SHAPE` (default `curve`). This is NOT detected from on-chain — it's passed as a CLI arg.
3. **Dashboard HTML hardcoded values** — Update fetchLiveData() after every rebalance
4. **Two-repo sync** — Dashboard reads from Pages repo, not vault
5. **EIP-1167 proxy reverts** — balanceOf fails with raw eth_call, use viem multicall
6. **Bin-level share ≠ pool share** — Never use bin efficiency as pool share %
7. **Config staleness in cron position amounts** — `.lfj-aae-config.json` position amounts drift from reality after deposits/withdrawals/rebalances. The LP monitor shows correct range/shape but wrong total value. Fix: update `token0_amount` and `token1_amount` in config OR use on-chain reader. Confirmed Jul 2, 2026: config showed $49.30, actual position was $46.43.
8. **Shared state file corruption** — Filter non-numeric entries from history arrays
9. **Dashboard CDN caching** — raw.githubusercontent.com caches 5+ min
10. **Git push failure = stale dashboard** — Check for detached HEAD
11. **LFJ V2.1 vs V2.2 ABI** — Pool is V2.1, use getReserves() + getActiveId()
12. **execute_code blocked in cron** — Use terminal() with python3 -c instead
13. **Security scanner blocks curl pipes** — Use execute_code with urllib.request
14. **DexScreener price drift** — Use on-chain price for range/status checks
15. **Renderer field contracts** — Read actual HTML renderer code, not docs
16. **Cron script exit codes cause false "error" status** — Monitoring scripts that exit with code 1/2 for alerts cause cron to report "error." Always exit 0 — alert content is in stdout, not exit codes. Fixed in `defi-lp-consolidated.py` (Jun 21, 2026). **Verification:** `grep -n "sys.exit(1)\\|sys.exit(2)" ~/.hermes/profiles/gentech/scripts/defi-lp-consolidated.py` should return nothing.
17. **Config updates during cron execution cause crashes** — If you update config files while a cron job is running, the script may read a partially-written file and crash. Wait for cron cycle to complete before updating, or update all files atomically. Symptom: cron reports "error" but manual script run succeeds.
18. **Producer-consumer schedule gaps cause stale data warnings** — When two cron jobs share a data file (one writes, one reads), the producer must cover ALL hours the consumer runs. If the reader runs `6-23` but the monitor runs `0-2` too, defi-data.json is stale during the gap. Preflight flags this but doesn't block — it's noise, not a blocker. Fix: extend the producer schedule to match or exceed the consumer's hours. Verify alignment by comparing cron schedules side-by-side.
19. **On-chain reader defaults shape to curve** — `reader.mjs` takes `--shape` as CLI arg with default `curve`. This does NOT read shape from on-chain. After rebalance, update `run-reader.sh` SHAPE default AND pass the correct shape via the env var.
20. **Two state files cause confusion** — `.lfj-defi-state.json` exists in BOTH `~/.hermes/scripts/` (global) AND `~/.hermes/profiles/gentech/scripts/` (profile). The script reads from whichever `HERMES_HOME` resolves to. Always update the profile-specific one. Check both when debugging state issues.
21. **force_send flag existed but was never checked** — The state file had a `force_send` boolean but `should_send_report()` never read it. Added check Jun 22, 2026. Use for testing/debugging: set `force_send: true` in state, script will report once then clear flag.
22. **On-chain verification auto-corrects config drift** — `verify_on_chain()` in `defi-lp-consolidated.py` compares on-chain data (defi-data.json) against config files. If range drifts >2¢ or shape mismatches, it auto-corrects BOTH `.lfj-position-tracker.json` AND `.lfj-aae-config.json`. Also flags imbalanced positions (>90% one token). **BUT** — this relies on the reader having the correct shape. If the reader was passed `--shape curve` but user set bid-ask, it auto-corrects to the WRONG shape.
23. **Preflight noise — preflight runs before debounce** — If a script has both preflight checks AND debounce/silence logic, preflight MUST run AFTER the debounce gate, not before. Otherwise the user sees orphaned preflight messages with no report attached. Found in `defi-lp-consolidated.py` (Jun 22, 2026). Fix: move `preflight()` call to after the `should_send_report()` check passes.
24. **[SILENT] markers leak in no_agent scripts** — Scripts with `no_agent: true` deliver stdout directly to the user. If the script prints `[SILENT]` when suppressing, the user sees that text. Fix: use empty stdout (just `return` or `sys.exit(0)`) instead of printing a silence marker. Found in `cmc-watchlist.py` and `defi-master-cron.py` (Jun 22, 2026).
25. **defi-master-cron.py had hardcoded stale position data** — Range, shape, and position_usd were hardcoded instead of reading from config. After rebalance, the cron reported wrong ranges. Fix: `load_pool_config()` reads from `.lfj-aae-config.json` at runtime. Also updated milestones to include Fisher tier ($100/day).
26. **Entry price field naming conflicts cause tracking drift** — Position tracker has both `entry_avax_price` (deprecated) and `entry_price` (current). Cron scripts using the old field cause wrong IL calculations. Fix: Update scripts to prioritize `entry_price` with fallback to `entry_avax_price`, and remove deprecated field after migration. Check with `grep -r "entry.*price" ~/.hermes/scripts/` to detect conflicts.
27. Cron data sync stale entry price — After manual rebalance, cron scripts may continue showing old entry price ($6.71) while actual position has new range. This causes incorrect IL calculations. Use fix-entry-price.py --range LOW HIGH to recalculate entry price (geometric mean) and sync all config files. Trigger: Cron shows "Entry: $6.71" but current price is in new range (e.g., $6.46 in $6.40-$6.62 range).
28. Fee tracker state must be seeded on initial setup — fee-tracker-state.json accumulates from 0 when first created or config changed. The user sees $0.46 when they've earned $4.29/week. Seed weekly_total, monthly_total, all_time with real values from Trader Joe UI or user's confirmed numbers before first LP monitor run.
29. **Fee tracking merged into LP monitor — do NOT create a separate cron** — Earlier design had a separate 24/7 Fee Tracker cron job that ran hourly. User rejected this. Fee tracking must run inside lp-monitor-v2.py as part of the normal 10-min cycle. The fee-tracker.py script exists as a reference but should not be scheduled separately.
30. **Pool label/chain mismatch in fee tracker config causes wrong metadata** — fee-tracker-config.json had position labeled "USDC/USDT — Arbitrum" when actual pool was AVAX/USDC on Avalanche. The APY/projections still worked because value x APY is the same but pool metadata was misleading. Always verify pool address, chain, and label match the actual position.
31. **CONFIG-FIRST = DON'T GUESS SHAPE/ENTRY** — The reader does NOT detect shape from on-chain. It echos whatever `--shape` was passed. If you pass the wrong shape, the dashboard shows wrong data. Always ask the user what they deployed. This is the #1 source of user frustration. (Confirmed Jul 19, 2026: Jordan corrected shape 3 times in one session.)
32. **Bid-ask = 0% real fees when price is between edges** — The efficiency formula shows 50-100% across the range, but in practice, NO bins are crossed when price sits between bid and ask edges. This means $0/day earnings. Don't tell the user "93% efficiency" with bid-ask in chop unless the price is actually at an edge. Be honest about 0% fee earnings.
33. **Python hashlib.sha3_256 is NOT Ethereum keccak256** — NIST SHA-3 and the original Keccak are different hash functions. Using hashlib.sha3_256 produces wrong selectors. Install pycryptodome and use Crypto.Hash.keccak. Correct LFJ V2.2 selectors: getActiveId()=0xdbe65edc, getBinStep()=0x17f11ecc, balanceOf(address,uint256)=0x00fdd58e, getBin(uint24)=0x0abe9688.
34. **On-chain reader now works — use it instead of guessing range from screenshots** — After fixing the keccak256 bug, the Python reader at ${VAULT_DIR}/scripts/onchain-reader.py can pull live bin data. Price formula: (1 + bin_step/10000) ** (bin_id - 2^23) * 10^12. Still needs shape and entry price from user config.
35. **A threshold that lives in more than one file is not fixed until every copy matches** — A rule such as "stay above X% fee efficiency" has at least three versions: what the user remembers, what the Constitution says, and what the code constant holds. In this session, the same rule was 60% in memory, 50% in code, and 75% in intent — and the code's 50% appeared in TWO independent files (`fee_efficiency.py` and `lp-monitor-v2.py`). **Before acting, read the code constant, grep the scripts tree for every assignment of the same symbol, and reconcile all three in writing.** Raising the threshold in only the authority file leaves the monitor firing on the old number, which is worse than leaving it alone because the two systems now disagree. And if the threshold change would harm a deliberate shape (e.g. a bid-ask reads ~33% by construction), write the exemption before you move the number, not after.
36. **"Not earning" must be a first-class MATERIAL alert, not an advisory.** A deployed, in-range book with a collapsed fee rate is the hardest condition to detect from outside. It must alert immediately (not wait for morning), use a stable dedupe signature, and remain distinct from the geometry score of a correctly-built shape. Raising the flag and spending capital to fix it are two separate decisions; the alert must not be hidden inside a rebuild.
37. **Yield-funded buy-list legs are credit-ledgers, not allowances.** When the operator wants a recurring buy funded by the farm ("take $5 out of the LP and put it into COQ"), build a credit ledger that accrues only measured realized proceeds, fires at a threshold, debits on spend, and preserves the existing weekly-dip fallback. Unmeasurable windows (e.g. a re-center inside the fee window) must credit zero, not be deferred. Keep the weekly allowance and the yield credit as separate pots; a buy funded by one must not debit the other.
38. **Check the perp rail before recommending leverage.** A "strong market" does not mean perps are deployable. Read the live account state on the actual rail (e.g. Hyperliquid clearinghouseState) before treating leverage as an option. If the account holds $0 and zero positions, deploying perps requires funding a new account with new capital — which changes the risk calculus entirely. Do not answer the perps question from price action alone.
39. **Stale position records are false receipts.** A file that claims an open trade with no matching on-chain/live-account position is a liability, not history. When the account reads zero positions but a local JSON still claims a live 3x long, mark the record stale and surface it for cleanup. Do not let a dashboard or tracker report a profitable-looking position that cannot be verified.
40. **Gas reserve target is one config value, and it must be uniform across a shared fleet.** A wallet whose `floor_usd` is set lower than its siblings will be refilled to that lower target and then drain again under normal rebuild load. Before diagnosing a "broken" refill, read `tenants.<tenant>.gas.floor_usd` for every tenant. Fix the floor, then measure whether `[4a] PROVISION GAS` actually runs.
41. **Refill gas by unwrapping WAVAX, not by swapping USDC.** The cheapest on-chain leg is WAVAX → native AVAX (~36k gas on Avalanche). A USDC → AVAX swap costs ~147k gas and should only be used when no WAVAX is available. The refill runs between withdraw and redeploy because that is when the book is liquid as WAVAX + USDC.
42. **A money tool's "SUCCESS" receipt is not proof of meaningful action.** Verify the post-state numerically. Flags like `--amount` may be in token units, not dollars, so a "$1" swap can move micro-dollars and still print a green line. Read balances, not receipts.
43. **An LP exit cannot spend the native-gas reserve.** A deliberate exit returns WAVAX + USDC; the reserve lives in native AVAX. The floor check on exit is informational, never blocking — an exit is the repair path, and a floor that blocked it would strand capital.
44. **Use an operator hold for any deliberate full withdrawal.** Set the hold before the action and clear it after. A held flat book is intentional, not IDLE CAPITAL. Require an expiry on every hold so one cannot persist by accident.
45. **The number on the page must be the number the machine acts on.** A dashboard that calls the same efficiency function as the loop but feeds it different inputs can flat the book by 16-22 points. The published value must come from the exact source the autonomous rail uses, with its provenance attached, or the operator is reading a flattering fiction while the machine acts on a harsher truth. Divergence between display and authority is a defect, not a rounding difference.
46. **Verify client-side rendered dashboards at the payload, not the static HTML.** A page that builds itself from a JSON payload will not contain the numbers in its raw HTML. Searching the HTML for `$268.42` or `97.0%` returns false negatives and invents a defect. The audit check must read the payload (e.g., `defi-data-<tenant>.json`) and then confirm the page's JavaScript consumes that payload, not grep the source.
47. **A rendered block that is empty on every tenant usually means the reader is pointed at the wrong file.** When code is written for a ledger carrying `rows`/`generated_at`/`source` but the path resolves to a SNAPSHOT file carrying `snapshots`, the row list is always empty and every field the page advertises returns None. Two files, one name pattern, wrong one read — check both the schema the code expects and the schema the file at `_p` actually contains. The fix is to read the file that matches the schema, or to rename/merge the files so the reader and writer agree.
48. **An error message can name the wrong layer.** An alert that says *"the router CANNOT pull this token"* points at the allowance, but the allowance may merely be moved and the script may fix that itself with an approve-and-retry. If the wallet lacks gas to pay for that approve, the simulation reverts with the same message and the loop retries forever. Verify the TRUE blocker by reading wallet gas, the reserve floor, and whether the next required transaction is affordable — do not treat the symptom text as the root cause.
49. **Cross-tenant numbers must be withheld, not borrowed.** A pool-level receipt (total fees, swap count) is true for every tenant page, but a per-tenant share (`our_share`) cannot be shown against a name it was not measured for. When the source file does not record which book produced the share, render it as `withheld` with the reason printed — never show one tenant's number on another's page to make the block look full.
50. **Size the reserve to the complete atomic operation, not to one cycle.** A curve deploy is TWO single-sided legs; when the router allowance has moved it is THREE transactions (approve + two legs). A reserve sized for one transaction leaves the wallet unable to pay for the second leg's approve, the simulation reverts, and the retry loop spins forever with the book EMPTY and capital idle. Worse, with no book there is no book WAVAX for the gas refill to draw on, so the machine cannot deploy, cannot refill, and cannot escape. The unit of reserve is the whole deploy — measure the gas of all legs plus the approve and add headroom.
51. **A failed re-center must STOP and escalate after repeated identical failures, not retry forever.** A deterministic gas/allowance/config deadlock does not self-heal by repetition; each failed attempt may consume gas and may leave a half-built position. After two consecutive failures with the same root signature, surface the condition and require operator input before the next attempt.
52. **A missing `--yes` from the wrapper is a missing confirmation.** A leg that requires both `--execute` and `--yes` cannot approve when the wrapper forwards only `--execute`. The symptom is a recurring `0x32e2717a` revert after a successful withdraw, which leaves the book flat and capital idle. Forward the confirmation, then verify by checking for `APPROVE SENT` in the wrapper's output.

---

### Gas reserve must cover the whole atomic operation, not one cycle

A curve deploy is TWO single-sided legs. When a router allowance has moved it can be THREE
transactions (approve + two legs). A reserve sized for one transaction may leave the wallet unable
to pay for the second leg's approve, so the simulation reverts and the retry loop spins forever with
the book EMPTY and capital idle. Size the reserve to the whole deploy — all legs plus the approve —
plus headroom.

### A wrapper must forward the operator's confirmation to the leg

`lfj_bid_deploy.py` only sends its router approve when both `--execute` and `--yes` are set. A
wrapper that forwards only `--execute` leaves the legs in permanent dry-run: they can never approve,
so every deploy that needs a fresh allowance reverts `0x32e2717a` ("the router CANNOT pull this
token"), and because a rebuild withdraws first, the capital parks in the wallet while the loop
retries forever. The wrapper is the human's confirmation gate; it must pass `--yes` down to any leg
it invokes. Verify by running the wrapper and checking that `APPROVE SENT` appears when a leg is
short.

### A sample taken mid-rebuild is a frame, not a state

A rebuild withdraws first, then redeploys. For one to two minutes the book is genuinely empty; while
one leg has landed and the other has not, it is genuinely partial. A single scan during this window
is correct about the instant and wrong about the state.

- Confirm with two independent readers after the cycle completes, or have the reader report whether a
  rebuild was in flight at sample time.
- Treat "0 bins" and "13 bins" as equally transient when the preceding action was a rebuild; neither
  is reportable until settled.
- The wallet-side mirror is the same: a low base balance plus a withdrawn volatile leg is the
  fingerprint of a rebuild in progress, not a loss.

### Verify identity against the platform, not a display name

A display name is a claim; the platform-assigned user id is the fact. The chain that maps identity
to tenant to privilege is load-bearing: if it is wrong, no ceiling absorbs the mistake.

- Call `getChatMember` for the recorded id and compare against actual group membership. A 400 means
  the id is not in the chat — record that as evidence, not an assumption.
- Every human in a treasury group must have a row in the speaker/identity map, and no human in the
  group may be unmapped. An unmapped speaker resolves to UNKNOWN and gets no privilege.
- When a privilege level or ceiling changes, update the file that enforces it AND the file that
  labels it, and verify with a file search that no stale prose still describes the old limit.

### A dollar ceiling and a capability level are different controls

`capital_ceiling_usd` limits how much may be at risk. A level (`L0_OBSERVE` ... `L3_AUTONOMOUS`)
limits what actions the tenant may trigger. Conflating them means reporting "the ceiling is removed"
while a real restriction still binds, or reporting "the level is bounded" while the dollar limit is
already null.

- Name which control is being changed before changing it.
- Update every file that names the control: the registry, the speaker map, and the enforcement code.
- Verify with a file search that no stale label or prose describes the old state.

## Quick Reference

### Shape Names (LFJ ↔ Config ↔ Display)

**⚠️ Use `bid-ask` as the internal name everywhere. The legacy name `bidirectional` is deprecated.**

| LFJ UI | Config (internal) | Display |
|--------|-------------------|---------|
| Curve | `curve` | CURVE |
| Bid-Ask | `bid-ask` | BID-ASK |
| Spot | `spot` | SPOT |

### run-reader.sh Shape Default

The reader passes shape via env var `SHAPE` or defaults to `curve`. After every rebalance:

```bash
# Before running reader, ensure SHAPE matches user's actual shape
export SHAPE=curve   # or bid-ask or spot
bash ${VAULT_DIR}/scripts/run-reader.sh
```

### Price Range Precision

Always use `.toFixed(4)` for ranges (e.g. `6.2000` not `6.20`). LFJ uses 5+ decimal places.

### Gas Note

Avalanche gas is ~$0.01 — negligible for rebalances. Core wallet covers gas on "free gas" transactions.

### IL Calculation — Entry Price

After every rebalance, log the new entry price. IL = deviation from that price, not from the original deposit.

```python
il_pct = (2 * (price_ratio ** 0.5) / (1 + price_ratio)) - 1
```
Where `price_ratio = current_price / entry_price`.

**When entry matches current price: IL = 0%.** This is the most common state right after a rebalance.

---

## Related Skills

- `market-macro-monitor` — Price data and macro context
- `link-research-summary` — Protocol research before building
- `stock-analysis` — Traditional market analysis

---

*Consolidated from 7 skills into 1 unified umbrella. Version 2.7.1 — Oct 2, 2026. Added "not earning" as a first-class MATERIAL alert, distinct from shape geometry and from advisory low-efficiency. Updated the threshold-multi-file pitfall. CMC-primary for price fetching. User preference: show cron 2x/hour when things are good, not just silent.*