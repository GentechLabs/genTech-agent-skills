---
name: defi
description: "Unified DeFi operations umbrella: LP monitoring, rebalancing, dashboard sync, strategy design, on-chain reading, LFJ orchestration, AAE app architecture, rank/prestige engine, and security intelligence. One skill to rule them all."
tags: [defi, lp, monitoring, rebalance, dashboard, strategy, on-chain, lfj, avalanche, solana, meteora, aae, ranks, prestige]
trigger: "Any DeFi-related task: LP monitoring, rebalancing, dashboard sync, strategy design, on-chain reads, LFJ operations, fee milestones, AAE app architecture design, rank/prestige engine, Meteora DLMM pools, or security intel."
related_skills: [market-macro-monitor, link-research-summary]
version: 2.7.0
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
- `/root/.hermes/profiles/gentech/scripts/lp-monitor-v2.py` — Line 66-97

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
- Weekly DCA: $15-25 range
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
- `/ProtoJay4789.github.io/DeFi/` (GitHub Pages deployment)
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
cp vault-data.json /ProtoJay4789.github.io/DeFi/data.json

# Deploy to GitHub Pages
cd ProtoJay4789.github.io && git add && git commit -m "Update dashboard" && git push
```

**Data Feed Requirements**:
- ALL top-level keys MUST exist or dashboard sections break
- Use number types, not strings, for numeric calculations
- Include real-time updates with simulated data feeds

> **Reference:** `/ProtoJay4789.github.io/DeFi/defi-suite-dashboard.html` for dashboard template

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
34. **On-chain reader now works — use it instead of guessing range from screenshots** — After fixing the keccak256 bug, the Python reader at /root/vaults/gentech/scripts/onchain-reader.py can pull live bin data. Price formula: (1 + bin_step/10000) ** (bin_id - 2^23) * 10^12. Still needs shape and entry price from user config.

---

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
bash /root/vaults/gentech/scripts/run-reader.sh
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

*Consolidated from 7 skills into 1 unified umbrella. Version 2.7.0 — Jul 20, 2026. Updated debounce to 3-tier (2x/hour normal, 10-min low-eff debounce, truly silent quiet hours). Added keccak256 vs SHA3-256 pitfall (#33) and on-chain reader fix (#34). CMC-primary for price fetching. User preference: show cron 2x/hour when things are good, not just silent.*