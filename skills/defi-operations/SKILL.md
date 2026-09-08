---
name: defi-operations
description: "Complete DeFi LP operations: position monitoring with alert escalation, regime-based strategy decisions, daily dashboard digests, market intelligence, and config management across multi-agent profiles. Covers LFJ/Uniswap V3-style concentrated liquidity on Avalanche."
tags: [defi, lp, monitoring, avalanche, lfj, dashboard, market, crypto]
related_skills: [crypto-market-monitoring]
triggers:
  - Setting up or modifying LP position monitoring
  - Configuring price range alerts for liquidity pools
  - Tracking fee efficiency on LP positions
  - Generating DeFi dashboard digests
  - Deciding when to LP vs spot based on market regime
  - Updating LP position parameters after a rebalance
  - Managing DeFi cron jobs across agent profiles
---

# DeFi Operations

Complete DeFi LP management — from real-time monitoring and alert escalation to strategic regime decisions and daily market intelligence reports.

## Lifecycle

```
Monitor → Alert → Analyze → Decide → Update → Report → Defense
   │        │        │         │        │        │        │
   │     alert-   regime-   position-  config-  dashboard- breakout-
   │   escalation strategy  update    management  digest    defense
   └──────────────────────────────────────────────────────────────┘
```

### 0. Tactical Retreat Defense Mode (NEW — Jul 19, 2026)

Adds a defense layer to the LP monitoring lifecycle. When price breaks out of range and stays out for a configurable timer (default 3 min), the system confirms a breakout and transitions through a state machine:

NORMAL → SENTINEL (out of range starts timer) → RETREATED (timer expires, breakout confirmed)

**State machine fields in `.lfj-defi-state.json`:**
```json
{
  "defense_mode": null,
  "breakout_start": null,
  "breakout_confirmed": false,
  "breakout_threshold_seconds": 180
}
```

**Auto-switch triggers:**
- **Breakout:** Price out of range > threshold → BREAKOUT_CONFIRMED → always report to user
- **FOMC:** 24h before FOMC meeting → auto-set SENTINEL mode regardless of price position
- **Post-FOMC:** After FOMC decision → clear SENTINEL mode, resume normal monitoring

**LP report now includes defense status line:**
```
Defense: 🛡️ RETREATED | 👁️ SENTINEL | ✅ NORMAL
```

**Integration:** `lp-monitor-v2.py` (breakout detection) + `fed-event-tracker.py` (FOMC auto-switch). See `references/tactical-retreat-defense.md`.

## 1. LP Position Monitoring

Automated monitoring for concentrated liquidity positions (LFJ, Uniswap V3-style) with tiered alert escalation.

### Alert Escalation (Current — Jul 20, 2026)

```
Normal (≥50% efficiency, in range) → report every 30 min (2x/hour)
Low efficiency (<50%)              → immediate alert + rebalance recommendation, 10 min debounce
Out of range                       → immediate alert + migration suggestion, no debounce
Quiet hours (11 PM – 6 AM ET)     → truly silent, no message at all
```

**Severity mapping:**
- Price out of range → HIGH (immediate alert with migration suggestion)
- Fee efficiency < 50% → MEDIUM (immediate alert with shape/range recommendation, 10 min debounce)
- Fee efficiency ≥ 50% → NORMAL (report every 30 min so user sees fee efficiency)

**No re-alerting on same condition within debounce window.** Once an alert fires, the same condition is suppressed until the debounce expires.

### Debounce Logic (Jul 20, 2026)

Two-track debounce system:

```python
LOW_EFF_DEBOUNCE_SECONDS = 600   # 10 min between low-efficiency alerts
NORMAL_INTERVAL_SECONDS = 1800   # 30 min between normal check-ins
```

**State fields:**
```json
{
  "last_report_time": null,      # last time any report was sent
  "last_low_alert_time": null,   # last time a low-efficiency alert fired
  "last_price": null,
  "last_efficiency": null,
  "last_in_range": null,
  "last_check": null
}
```

**Alert trigger conditions:**
- OUT_OF_RANGE → Immediate alert with range migration suggestion, resets both timers
- Efficiency < 50% → Immediate alert with shape/range optimization suggestion, debounces 10 min
- Efficiency ≥ 50% → Report every 30 min (2x/hour) so user sees fee efficiency humming

**AAE Platform Integration:**
This debounce + suggestion pattern is the signal layer for AAE's automated range migration service. The approval → execution flow:
1. Agent alerts with suggestion
2. User approves via prompt or UI
3. Agent executes LFJ CLI with gas auto-payment
4. Confirmation delivered

### Smart DCA Zones (Efficiency-Based)

| Efficiency Zone | Condition | DCA Amount | Rationale |
|-----------------|-----------|------------|-----------|
| 🟢 Center | ≥ 70% | $50 (full) | Deep in range, earning optimally |
| 🟡 Mid | 50–70% | $30 (reduced) | Approaching edges — size down |
| 🟠 Low | 30–50% | $20 (micro) | Near edge — watch for rebalance |
| 🔴 Edge/Crash | < 30% | $10 (micro) + URGENT | Earnings collapsed — rebalance |

### Duplicate Signal Suppression

SHA-256 hash-based deduplication with 10-minute window. Prevents spam from persistent conditions across monitoring intervals.

### On-Chain Position Reading (LFJ V2.2)

**Always read on-chain data.** Never use hardcoded/calculated position values.

**Direct RPC calls** — no API key needed:
- `eth_getBalance` for native AVAX
- ERC-20 `balanceOf(address)` for USDC
- LFJ pool is **ERC1155** (not ERC721) — standard `ownerOf`/`balanceOf` reverts

**Pitfall: getActiveId and getBinStep revert on V2.2 pools.** The function selectors `0x80afabfa` (getActiveId) and `0xd327e941` (getBinStep) may revert on LFJ V2.2 pools via public RPC. This is a known issue — see `references/lfj-v22-rpc-pitfalls.md` for full details and workarounds. When this happens:
- Fall back to DexScreener for price data (it returns the current price directly)
- Use the LFJ subgraph (if available) for bin-level data
- Read position data from the LFJ web UI screenshots as a last resort
- The `onchain-reader.mjs` script uses the @traderjoe-xyz/sdk-v2 package which handles the ABI correctly, but requires a working viem installation

**Key contracts (Avalanche):**
| Contract | Address |
|----------|---------|
| Pool (LB Pair) | `0x864d4e5ee7318e97483db7eb0912e09f161516ea` |
| Position Manager | `0x18556da13313f3532c54711497a8fedac273220e` |
| WAVAX | `0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7` |
| USDC | `0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E` |

### Quiet Hours

Respect config-based quiet hours (default: 11 PM – 6:30 AM ET).

### State Schema

```json
{
  "out_of_range_start": null,
  "efficiency_low_start": null,
  "last_alerted_condition": null,
  "last_signal_hash": null,
  "last_signal_time": 0,
  "last_price": 9.1589,
  "last_check": "2026-05-07T16:20:00-04:00"
}
```

### Alert Prefix Convention

```
ALERT:out_of_range_<direction>  → HIGH severity
ALERT:low_efficiency_critical   → MEDIUM severity
MILESTONE:$<amount>             → tier reached
STATUS:OK                       → silent run
QUIET_HOURS                     → suppressed
```

### Decision Guidance Layer (BORROWED from AgentLayer — Aug 15, 2026)

**The gap it fills:** our LP alerts report *numbers* (efficiency %, in/out of range) but
don't explain the *why* — the trade-off behind the recommendation. AgentLayer's Uniswap
Liquidity skill showed the missing layer: **explain fee-tier / range-width /
capital-efficiency / out-of-range trade-offs, and make IL risk understandable BEFORE a
liquidity decision.** We borrow the mechanism, not the tool (we're on Trader Joe/LFJ, not
Uniswap V3/V4).

**Rule:** every rebalance / range-change recommendation MUST include a plain-language
"why" — not just the alert. Structure it as:

```
Why this range is suboptimal:
- Too wide  → fees diluted across idle bins (low capital-efficiency)
- Too narrow → high out-of-range risk (position stops earning when price drifts)
- IL trade-off → [current IL%] — the wider the range, the lower the IL but the
  thinner the fees; the tighter the range, the higher the fees but the sharper the IL
  if price exits. We're trading fee capture vs IL exposure.
```

**When to include it:**
- LOW_EFFICIENCY alert → explain the width/efficiency trade-off
- OUT_OF_RANGE alert → explain the narrow-range risk that caused it
- Any rebalance recommendation → frame the fee-vs-IL trade-off before the move

**Why it matters:** turns the monitor from "here's a number" into "here's the trade-off,
here's why" — so Jordan (or the agent, in autonomous mode) decides with the reasoning
visible, not just the metric. This is the "explain-before-decide" layer that separates a
guided workflow from a raw alert.

## 2. Regime-Based Strategy

Framework for deciding when to LP (earn fees in chop) vs spot (capture trend).

### 4 Regime Types

| Regime | Action | LP Allocation |
|--------|--------|---------------|
| Range-bound | 100% LP | Full position |
| Bull confirmed | 25% LP + 75% spot | Capture trend upside |
| Bear confirmed | 100% LP or stable | Earn fees in decline |
| Uncertain | Wide-range LP | Maximize range |

### "Go Spot" Signal Framework

5 signals — 3+ fire → exit 75% LP to spot:
1. Price holds above level for 48h+
2. BTC trend confirmation
3. Macro pivot signal
4. Volume 2x average
5. Higher lows pattern

### LP Re-Entry at Resistance

Consolidation at level for 12-24h → re-LP. Blast through → stay spot.

### Exit Everything Signal

RSI >85, BTC distribution, macro shock, 3x from recent levels.

## 3. Position Updates

One-shot workflow for updating LP position parameters across all systems.

**4-step sequence:**
1. Patch `.env` config file
2. Update cron job prompts
3. Replace memory entry
4. Confirm to group

**Config file management** — after ANY rebalance, update ALL copies:
- 7 known copies of `.lfj-aae-config.json` across profiles
- `HERMES_HOME` resolves to profile dir, not `/root`
- Always batch-sync all copies after rebalance

**Batch sync pattern:**
```python
import json, glob
for path in glob.glob("/root/.hermes/**/.lfj-aae-config.json", recursive=True):
    with open(path) as f:
        config = json.load(f)
    config["position"].update(NEW_POSITION)
    with open(path, "w") as f:
        json.dump(config, f, indent=2)
```

**Pitfalls:**
- Config drift across profile copies causes false alerts
- Range updates require job prompt edits — don't just change config
- Cron prompt-only jobs fabricate data when agent lacks API tools — always use `script` parameter

## 4. Dashboard Digests

Daily DeFi dashboard digests combining LP status, watchlist tracking, market context, and commentary.

### Data Sources (Priority Chain)

1. **CMC Pro API** (preferred) — `https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest`
2. **CoinGecko fallback** — free API, rate-limited
3. **Browser scraping fallback** — JS console extraction patterns

### Watchlist from Obsidian Vault

Source: `03-Strategies/cron-watchlist-config.md`

### Movement Detection

Threshold-based skip logic (1.5%) to avoid redundant notifications.

### News Context Chain

CoinDesk → DuckDuckGo → Google fallback

### Wallet Integration

DeBank API + Snowtrace for on-chain balances.

### CMC API Key Rotation

6-step process across config files when keys expire.

### Price Formatting Rules by Tier

- BTC: full amounts
- Small caps: scientific notation avoidance

## 5. Market Intelligence

Complete crypto watchlist monitoring with price fetches, LP position status, and investment report synthesis.

### 5-Phase Workflow

1. **Data Collection** — CMC → CoinGecko → DexScreener fallback
2. **LP Position Analysis** — Out-of-range (🚨), Efficiency-low (⚠️), In-range (✅)
3. **News & Macro Context** — RSS feeds (CryptoPanic, CoinDesk, Decrypt) → Bing News fallback
4. **Report Synthesis** — YoYo investment report template
5. **State Update** — persist for next run

### LP Status Mapping

- 🚨 Out-of-range
- ⚠️ Efficiency-low (<30%)
- ✅ In-range (with 2% edge proximity flag)

### Macro Indicators

Fear & Greed, BTC dominance, Fed/regulatory headlines.

### Critical Config Files

- `defi-lp-config.env`
- `cmc_config.json`
- `.lfj-position-state.json`

**Pitfalls:**
- CoinGecko ID mismatches (silent empty responses)
- DexScreener 404s on new pools
- Bing general search Cloudflare-blocked

## Cron Job Architecture

### Consolidated Job Registry (Post-Cleanup — Jun 30, 2026)

| Job ID | Name | Schedule | Script | Purpose |
|--------|------|----------|--------|---------|
| `92c52122abab` | LP Monitor v2 | `3,13,23,33,43,53 12-22 * * *` | `lp-monitor-v2.py` | Config-first, dashboard-free monitoring. Reports 2x/hour in normal conditions, immediate alerts on low efficiency or out-of-range. Truly silent during quiet hours (11 PM – 6 AM ET). |
| `d8d1c3adbbb4` | Hub Nightly Sync | `0 20 * * *` | `hub-sync-nightly.py` | Non-position data only (narrative, rainbow) |

**Removed jobs (Jun 30, 2026):**
- `2600f8fc0f0e` — Old LP monitor (read from dashboard, got corrupted data)
- `4cb4f1e92116` — On-chain reader (wrote to dashboard, caused race condition)

**Architecture change:** LP monitor v2 reads ONLY from config + position tracker + DexScreener. Zero dashboard dependency. This eliminates the race condition where multiple scripts overwrote each other's data.

### Key Pattern: Script + Prompt

Use `script` parameter to run data-fetching code, then `prompt` to format output. This prevents prompt-only fabrication.

**Hub Sync Architecture — Data Writer Concurrency (Jun 2026)**

**Critical architecture rule:** Only ONE cron job should write core position data to `DeFi/defi-data.json`. Multiple writers cause stale data conflicts.

**Data flow:**
```
On-chain reader (run-reader.sh → reader.mjs)
    ↓
Position tracker (.lfj-position-tracker.json) [source of truth for shape]
    ↓
defi-lp-consolidated.py (primary data writer)
    ↓
defi-data.json (GitHub Pages)
    ↓
Hub fetch & renders (HTML/CSS)
```

**Hub sync problem (discovered Jun 28, 2026):**
- `hub-sync-nightly.py` was BUILDING entire JSON from scratch, overwriting correct on-chain data
- `defi-lp-consolidated.py` had correct data but wasn't writing to JSON properly
- Position tracker path bug in `run-reader.sh` pointed to wrong location (`/root/.hermes/scripts/` instead of `/root/.hermes/profiles/gentech/scripts/`)
- Result: Hub showed wrong shape (bid-ask vs curve), zero efficiency, stale amounts

**Fix implementation:**
1. `run-reader.sh` — Fixed position tracker path to `/root/.hermes/profiles/gentech/scripts/.lfj-position-tracker.json`
2. `hub-sync-nightly.py` — Changed to READ from existing JSON instead of OVERWRITING:
   ```python
   # Load existing dashboard data as the base (preserve everything)
   existing = {}
   if os.path.exists(DASHBOARD_DATA_PATH):
       with open(DASHBOARD_DATA_PATH) as f:
           existing = json.load(f)
   
   # Use on-chain data if available (primary source from LP monitor)
   shape = onchain.get("shape") or lp.get("shape", "curve")
   efficiency = onchain.get("efficiency") if onchain.get("efficiency") is not None else existing.get("efficiency", 0)
   # ... cascade through all position fields
   ```

**Verification command:**
```python
# Check what's syncing to Hub
with open("/root/ProtoJay4789.github.io/DeFi/defi-data.json") as f:
    data = json.load(f)
lp = data.get("lpPosition", {})
print(f"Shape: {lp.get('shape')}")
print(f"Efficiency: {data.get('efficiency')}%")
print(f"Position: ${lp.get('totalValueUSD', 0):.2f}")
print(f"AVAX: {lp.get('avaxAmount')}")
print(f"USDC: ${lp.get('usdcAmount')}")
print(f"In Range: {lp.get('inRange')}")
```

**Expected on-chain fields:**
- `lpPosition.shape` — "curve" (from position tracker)
- `lpPosition.displayShape` — "CURVE"
- `efficiency` — 60-96% (calculated from bin distribution)
- `lpPosition.avaxAmount` — 1.0-3.0 AVAX (varies by DCA)
- `lpPosition.usdcAmount` — $27-40 USDC (varies by DCA)
- `lpPosition.totalValueUSD` — $47-48 total position
- `lpPosition.inRange` — true/false
- `lpPosition.rangeMin` / `lpPosition.rangeMax` — current range

**Sync verification pattern:**
1. Run `defi-lp-consolidated.py` with force_send=True
2. Read `defi-data.json` and check core fields
3. Open Hub in browser to verify visual render
4. If mismatch → fix writer, then re-verify

**Writer priority:**
1. `defi-lp-consolidated.py` — primary (on-chain data)
2. `hub-sync-nightly.py` — secondary (only for non-position data: narrative rotation, rainbow data) — MUST preserve existing position fields
3. `fed-event-tracker.py` — macro events only (writes to `DeFi/economic-calendar.json`)

**Never let `hub-sync-nightly.py` overwrite `lpPosition` or `efficiency` — it lacks on-chain shape awareness.**

### Entry Price Consistency Protocol (NEW - Jun 29, 2026)

**Problem:** After rebalances, entry price and impermanent loss calculations diverge across multiple config files due to inconsistent updates.

**Root Cause:** Multiple config files (9 total) were not updating simultaneously after position changes, causing data drift.

**Solution Protocol:**

**1. Single Source of Truth**
- Entry price = geometric mean of active range: `sqrt(rangeMin * rangeMax)`
- Apply this calculation immediately after ANY rebalance
- Update ALL 9 config files in a single atomic operation

**2. Target Files for Sync**
```python
config_files = [
    "~/.hermes/scripts/.lfj-position-tracker.json",      # Primary source
    "/root/ProtoJay4789.github.io/DeFi/defi-data.json", # Dashboard
    # ... 7 additional config files
]
```

**3. Atomic Update Script Pattern**
```python
# Entry price fix script template
def fix_entry_price(range_low, range_high):
    import math, json
    
    # Calculate correct entry price
    entry_price = math.sqrt(range_low * range_high)
    current_price = get_current_price()
    il_percent = ((current_price - entry_price) / entry_price) * 100
    
    # Update ALL files atomically
    for file_path in config_files:
        # Load existing data
        with open(file_path) as f:
            data = json.load(f)
        
        # Update entry price fields
        data['lpPosition']['entryPrice'] = entry_price
        data['hero']['entryPrice'] = entry_price
        data['hero']['impermanentLossPercent'] = round(il_percent, 2)
        data['ilCalculator'] = {
            'entryPrice': entry_price,
            'impermanentLossPercent': round(il_percent, 2)
        }
        
        # Save with backup
        backup_path = file_path + '.bak'
        shutil.copy(file_path, backup_path)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
```

**4. Validation Command**
```bash
# Verify consistency across all systems
curl -s "https://raw.githubusercontent.com/ProtoJay4789/ProtoJay4789.github.io/main/DeFi/defi-data.json" | \
python3 -c "
import json, sys
data = json.load(sys.stdin)
ep = data.get('hero', {}).get('entryPrice')
il = data.get('hero', {}).get('impermanentLossPercent')
cp = data.get('hero', {}).get('currentPrice')
print(f'Entry: ${ep:.4f}, IL: {il}%, Current: ${cp}')
# Verify IL calculation
calculated_il = ((cp - ep) / ep) * 100
print(f'IL Verification: Dashboard={il}%, Calculated={calculated_il:.2f}%')
" 2>/dev/null || echo "Need manual verification"
```

**5. After-Action Checklist**
- [ ] Execute fix script after every rebalance
- [ ] Verify entry price appears in dashboard hero section
- [ ] Confirm IL calculation is accurate (< 0.01% tolerance)
- [ ] Push updates to GitHub to sync Hub dashboard
- [ ] Test cron job reports show correct entry price

**Key Insight:** Entry price must be recalculated as geometric mean of the new range after rebalances, not carried forward from previous positions. This ensures accurate IL tracking and prevents false efficiency reports.

### Shape Detection Critical Protocol (NEW - Jun 30, 2026)

**Problem:** LP shape detection returning wrong shape ("curve" vs "bid-ask"), causing 7-54% efficiency calculation errors that compromise rebalancing decisions.

**Root Cause:** Dashboard data source had conflicting shape field vs config file, monitor script missing "bid-ask" alias in normalize_shape function.

**Impact Analysis:**
- Curve efficiency formula: `efficiency = (1 - abs(position - 0.5) * 2) * 100`
- Bidirectional efficiency formula: `efficiency = abs(position - 0.5) * 2 * 100`
- At 73.2% range position: curve = 53.6%, bidirectional = 46.4%, difference = 7.2%
- At 61.4% range position: curve = 77.3%, bidirectional = 22.7%, difference = 54.6%

**Solution Protocol:**

**1. Multi-Source Shape Synchronization**
- ✅ Config: Update `shape: "bid-ask"` in all `.lfj-aae-config.json`
- ✅ Dashboard: Update `lpPosition.shape: "bid-ask"` and all display references
- ✅ Monitor Script: Add `"bid-ask": "bidirectional"` to normalize_shape aliases
- ✅ Range Alignment: Ensure range_low/range_high consistent across sources

**2. Cross-Source Validation Pattern**
```python
def validate_shape_consistency():
    """Ensure all sources report the same shape"""
    sources = {
        "Config": "/root/.hermes/scripts/.lfj-aae-config.json",
        "Dashboard": "/root/ProtoJay4789.github.io/DeFi/defi-data.json"
    }
    
    for name, path in sources.items():
        with open(path, 'r') as f:
            data = json.load(f)
        
        if "position" in data:
            shape = data["position"].get("shape", "NOT_FOUND")
        elif "lpPosition" in data:
            shape = data["lpPosition"].get("shape", "NOT_FOUND")
        
        normalized = normalize_shape(shape)
        print(f"{name}: {shape} → {normalized}")
    
    return True  # Add error checking
```

**3. GLM-5.2 Audit Protocol**
- Use GLM-5.2 ("Jill") for complex DeFi system analysis
- Cross-validate all data sources systematically
- Calculate efficiency impact differences
- Verify system integration works correctly
- Confirm business impact resolution

**4. Verification Checklist**
- [ ] Monitor script shows "Shape: BIDIRECTIONAL" (not curve)
- [ ] Dashboard shows all shape references as "bid-ask"
- [ ] Efficiency calculations use correct bidirectional formula
- [ ] Range values consistent across all sources
- [ ] Cron output matches expected strategy
- [ ] Rebalancing triggers based on accurate efficiency

**Critical Learning:** Shape is a fundamental LP parameter that affects ALL efficiency calculations. A single field error across sources can compromise the entire strategy optimization system. Always cross-validate shape consistency across config, dashboard, and monitor systems.

**Key Insight:** Different efficiency formulas produce wildly different results (up to 54% difference), making shape detection accuracy non-negotiable for LP strategy decisions.

**Pitfall: Three-Config-File Race Condition (Jun 30, 2026)**
- THREE copies of `.lfj-aae-config.json` exist with DIFFERENT data:
  1. `/root/.hermes/scripts/.lfj-aae-config.json` — CORRECT (bid-ask, $6.3792, range 6.3656–6.5856)
  2. `/root/.hermes/profiles/gentech/scripts/.lfj-aae-config.json` — STALE (curve, $6.13, range 6.2771–6.4812)
  3. `/root/.hermes/profiles/gentech/home/.hermes/scripts/.lfj-aae-config.json` — STALE (bid-ask but wrong range/entry)
- `HERMES_HOME` env var resolves to `/root/.hermes/profiles/gentech` in cron context, NOT `/root/.hermes`
- Scripts using `os.environ.get("HERMES_HOME")` read the STALE profile copy, not the correct one
- Multiple cron jobs (LP monitor + on-chain reader) write to the same dashboard JSON, creating a race condition that overwrites correct data within seconds
- **Permanent fix:** Created `lp-monitor-v2.py` — a clean, self-contained script that:
  - Hardcodes config path to `/root/.hermes/scripts/` (NOT env-var-based)
  - Reads ALL data from config + position tracker (never from dashboard)
  - Fetches live price directly from DexScreener API
  - Has ZERO dashboard read/write dependency — eliminates the race entirely
  - Uses bid-ask as a DISTINCT shape (not aliased to bidirectional)
  - Bid-ask efficiency: 50% at center → ~75% at edges (configurable)
- Old cron jobs removed: `2600f8fc0f0e` (old monitor), `4cb4f1e92116` (on-chain reader)
- New cron job: `92c52122abab` — `lp-monitor-v2.py`, every 10min, no_agent=True
- **Lesson:** When multiple scripts write to the same file, eliminate the shared file dependency rather than trying to coordinate writes

### Manual Rebalance Data Sync Protocol (Jul 1, 2026)
- **Guiding Principle (User Preference):** When user reports a rebalance or position change, ALWAYS verify with live price data FIRST before assessing monitor output
- **Pitfall: Rules doc is NOT the source of truth.** The `LP-Monitor-Rules.md` file in the vault is a human-readable summary that goes stale. The live config at `/root/.hermes/scripts/.lfj-aae-config.json` is the actual source of truth. Always read the config file, not the rules doc, when answering "how is the pool?" — the rules doc is for reference, the config is for data.
- **Config-First Verification (Jul 20, 2026):** When the user asks "how is the pool?" or shows a screenshot:
  1. Read the live config at `/root/.hermes/scripts/.lfj-aae-config.json` — source of truth
  2. Do NOT read the rules doc (`LP-Monitor-Rules.md`) — it's a human-readable summary that goes stale
  3. Verify with live price from DexScreener before assessing monitor output
  4. If user shows a screenshot, update the config files immediately, then run the monitor to confirm

### Screenshot Reading Protocol (Jul 20, 2026)

**CRITICAL: Do NOT guess the range from memory or stale config.** Always extract from the screenshot.

When the user shows a screenshot of their LP position (from LFJ/Trader Joe mobile or web UI):

1. **Use vision_analyze** on the screenshot image to extract actual numbers — do NOT guess or use stale config data
2. **Key fields to extract:**
   - AVAX amount and USDC amount (from "Deposit Balance" section)
   - Total position value (Balance: $XX.XX)
   - 24h fees earned (from "Fees Earned" section — both AVAX and USDC breakdown)
   - Range boundaries — **use the explicit "Min Price" / "Max Price" input fields, NOT the chart x-axis labels**
   - Number of bins (from the chart or "Num Bins" field)
   - Shape (Spot/Curve/Bid-Ask from the shape selector)
3. **After extraction:**
   - Update all three config files immediately
   - Run the monitor script to verify the new data produces correct output
   - Present the corrected snapshot to the user
4. **Pitfall: Chart x-axis labels are NOT the range boundaries.** The chart shows price points along the curve (e.g. 6.53319, 6.56692, 6.59882, 6.63188) — these are bin price labels, not the min/max of your position. The actual range is in the "Min Price" and "Max Price" input fields below the chart (e.g. 6.12836511 and 7.10539292). Using chart labels instead of input fields will give you a wrong, too-narrow range.
5. **Pitfall:** The "Deposit Balance" section shows current position composition — this is the most reliable source for token amounts. The "Fees Earned" section shows 24h accumulation, not position value.
6. **Pitfall: Multiple rebalances in one session.** The user may rebalance multiple times in a single conversation. Each screenshot is a new snapshot — don't assume the previous update is still current. Always extract fresh from the latest screenshot.
- **Update Protocol (Jul 20, 2026):** When Jordan shows new position data, update these files:
  1. `/root/.hermes/scripts/.lfj-aae-config.json` — position amounts, range, entry price
  2. `/root/.hermes/scripts/.lfj-position-tracker.json` — amounts + range
  3. The vault rules doc at `03-Strategies/LP-Monitor-Rules.md` — summary section
  The LP Monitor cron job reads from #1 and #2 — no script changes needed. Next run picks up the new data automatically.
- PROBLEM: Manual position rebalances aren't automatically reflected in config files and position tracker
- Root cause: Cron jobs only update data based on on-chain reads, not manual wallet changes
- Detection: Cron shows "OUT OF RANGE" but user believes they're in range
- **Critical verification step:** Always verify with actual data before assuming monitor is wrong
- **Detection workflow:**
  1. Manual rebalance → actual position changes
  2. Cron job shows stale data from position tracker
  3. User detects discrepancy ("I'm rebalancing, check now")
  4. **Verify reality:** Fetch live price, compare against current range
  5. **Two scenarios:**
     - **Monitor is right:** Price is actually outside range → rebalance needed
     - **Monitor has stale data:** Range updated in wallet but not in config → sync needed
  6. **Immediate fix:** Update position tracker with actual rebalanced values
  7. **Verify:** Run monitor script to confirm data sync
- **Verification command:**
  ```bash
  # Check if price is actually in range
  curl -s "https://api.dexscreener.com/latest/dex/pairs/avalanche/0x864d4e5ee7318e97483db7eb0912e09f161516ea" | jq '.pairs[].priceUsd'
  # Manual check: price >= range_low AND price <= range_high?
  ```
- **Position tracker update pattern:**
  ```json
  {
    "last_rebalance": "manual_rebalance_2026-07-01",
    "last_rebalance_source": "manual_verification", 
    "rebalance_type": "manual",
    "entry_price": 6.3792,
    "avax_amount": 3.262981,
    "usdc_amount": 27.274526,
    "range_low": 6.40,
    "range_high": 6.80,
    "current_price": 6.63,
    "shape": "bid-ask",
    "strategy": "BID-ASK",
    "bins": 149,
    "daily_fees_usd": 0.201,
    "cumulative_fees_usd": 1.0325,
    "last_updated": "2026-07-01T12:06:52.184150",
    "source": "manual_sync",
    "entry_avax_price": 6.3792,
    "updated": "2026-07-01"
  }
  ```
- **Detection method:** Compare cron output with actual market data — if user says "I'm rebalancing" and monitor says "OUT OF RANGE", verify with live price fetch FIRST
- **Prevention:** After any manual rebalance, update `.lfj-position-tracker.json` immediately before next cron run
- **Critical insight:** The monitor is usually correct — it fetches live price from DexScreener. Don't assume stale data without verification. Config-first architecture protects against race conditions, but manual changes require manual data sync in position tracker files
- **Executable sync script:** `scripts/lp-data-sync.py` — automated position tracker sync after manual rebalance

**Pitfall: Cron Script Location Mismatch (Jun 30, 2026)**
- Cron jobs may use scripts in different locations than those being edited
- Multiple script copies can exist:
  - Vault scripts: `/root/vaults/gentech/Strategies/scripts/defi-lp-consolidated.py`
  - Profile scripts: `/root/.hermes/profiles/gentech/scripts/defi-lp-consolidated.py`
  - Cron-specific scripts may be in other profile directories
- If manual script run shows correct output but cron output shows old behavior → wrong script version is being executed
- Fix: Identify the ACTUAL script path cron uses (check job config or audit with GLM-5.2), then edit the script in the cron execution path
- **Better fix:** Write a new clean script with hardcoded paths rather than patching old ones — eliminates path resolution ambiguity entirely

**Visual upgrade for all GenTech cron outputs** — matches Hermes dashboard style.

**Theme module:** `/root/.hermes/profiles/gentech/scripts/cron_theme.py`

**Design elements:**
- Notched corners (`╭ ╮ ╰ ╯`) — Hermes-style frames
- Glow progress bars (`▌▓▓▓▓▓▓▓░░`) — visual efficiency
- Minimal status icons (`✓ ⚠ ✖`) — clean hierarchy
- Cyan glow borders — tech aesthetic
- Dark backgrounds with gradient simulation

**Import pattern:**
```python
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.path.pardir))
from cron_theme import (
    render_header, render_card, close_card, render_row, render_progress_bar,
    render_tree, render_footer, get_status_icon, get_status_color,
    truncate, BLUE, RED, GREEN, YELLOW, SILVER, BLACK
)
```

**Output sample:**
```
╭────────────────────────────────────────────────────╮
│  ✓ DeFi Milestone + LP Report                      │
│  2026-06-28 13:59 EDT                              │
╰────────────────────────────────────────────────────╯

╭────────────────────────────────────────────────────╮
│  📊 LFJ AVAX/USDC 5bps                              │

│  Status                                  ✓ In Range │
│  Eff                               ▌▓▓▓▓▓▓▓░░ 83.0% │
│  Shape                                        CURVE │
╰────────────────────────────────────────────────────╯
```

**Proven deployments:**
- DeFi LP Monitor (`defi-lp-consolidated.py`) — fully migrated
- Fed Event Reminder (`fed-event-tracker.py`) — partially migrated

**Strategic split:**
- **Telegram cron jobs** — Compressed ASCII alerts (current theme)
- **Hub dashboard** — Rich visuals (HTML/CSS, gradients, animations)

**Cron jobs write JSON; Hub renders HTML.** Never try to make Telegram look like the Hub — different platforms, different capabilities.

## 6. Free-API Data Collection Pattern (Jul 2, 2026)

When BlockRun wallet balance is low ($0.002) or unfunded, **do not use BlockRun-dependent MCP tools** (blockrun_defi, blockrun_rpc, blockrun_surf, blockrun_chat). Use free public APIs via direct HTTP instead.

### Free Alternatives Matrix

| Data Need | Free API | Endpoint | Notes |
|-----------|----------|----------|-------|
| Token prices | CoinGecko | `api.coingecko.com/api/v3/simple/price` | Rate-limited, use `requests` with caching |
| DEX pair data | DexScreener | `api.dexscreener.com/latest/dex/search` | No key needed, 10 req/min recommended |
| Yield / APY | DefiLlama | `yields.llama.fi/pool?search=` | Massive dataset, filter by chain locally |
| Pool volume/liq | DexScreener | `api.dexscreener.com/latest/dex/pairs/{chain}/{pool}` | No key needed, specific pair lookup |

### Fee Tracker Specimen

The `fee-tracker.py` script demonstrates this pattern:

- **Architecture**: Python script + JSON config + JSON state file
- **Schedule**: `no_agent=true` cron every 60 min
- **Cost**: $0 — all HTTP to free APIs
- **State accumulation**: Reads last check timestamp from state file, calculates hours elapsed, multiplies position_value × APY × (hours / 8760), accumulates to daily/weekly/monthly running totals
- **Config-driven**: `fee-tracker-config.json` defines positions with `position_value_usd`, `apy_override` (optional), `weekly_contribution`
- **Auto-APY fallback chain**: manual override → DefiLlama → DexScreener volume estimate → previous snapshot
- **Reset logic**: Resets daily at UTC midnight, weekly at Monday, monthly at 1st
- **LP Monitor integration**: `lp-monitor-v2.py` reads fee-tracker-state.json and appends Daily/Weekly/Monthly/Projected section to every LP report

**Location**: `scripts/fee-tracker.py` + `scripts/fee-tracker-config.json`
**Cron job ID**: `774c36d9acdf` (24/7 Fee Tracker, every 1h, delivers to Strategies group)
**LP Monitor integration**: Added Jul 2, 2026 — `lp-monitor-v2.py` reads fee tracker state and includes weekly/monthly/projected trajectory in each 10-min report

### Seed-from-Screenshot Pattern

When the fee tracker starts fresh (all_time = 0), seed it with real accumulated data from a protocol screenshot:

1. User provides screenshot of accumulated fees from protocol dashboard
2. Use vision (`browser_vision` or GLM-5 via BlockRun chat) to extract: `all_time` (total accumulated), `daily_total` (recent session)
3. Write these into `fee-tracker-state.json` manually
4. Subsequent runs build on the seeded baseline

This prevents the "starts from zero" problem — the tracker reflects real history from day one.

### Pitfalls

- CoinGecko ID mismatches cause silent empty responses — use exact coingecko ID (e.g. `avalanche-2` not `avax`)
- DexScreener limits: ~10 req/min without issues, larger bursts trigger 429
- DefiLlama yields response is extremely large (10M+ chars) — filter by chain AND search param server-side, then filter client-side in Python
- Vision analysis (screenshot reading) requires a vision-capable model — DeepSeek Flash lacks native vision. Use GLM-5 via BlockRun chat when funded; fall back to user description when BlockRun is on hold.

## 7. On-Chain Entry Detection (Jul 3, 2026)

Track when a wallet first entered a pool using ERC-1155 TransferBatch events — the equivalent of Jane Street wallet activity tracking for LP positions.

### Key Discovery

LFJ V2.2 uses **TransferBatch** (not TransferSingle) for ERC-1155 bin shares:
- **TransferBatch sig:** `0x4a39dc06d4c0dbc64b70af90fd698a233a518aa5d07e595d983b8c0526c8f7fb`
- **Mint (deposit):** `from=0x0, to=wallet`
- **Burn (withdraw):** `from=wallet, to=0x0`
- **Operator:** LBRouter (`0x18556da13313f3532c54711497a8fedac273220e`)

### Implementation

`find_onchain_entry()` in `lp-position-reader.py`:
1. **Caches first** — reads `.lfj-entry-cache.json`
2. **Searches deposits** — eth_getLogs with topics[3]=wallet, 2048-block chunks
3. **Searches withdrawals** — topics[2]=wallet
4. **Batch timestamps** — 5 blocks per batch
5. **Active days** — group events by day, measure span

### 4-Hour Active Days Rule

A day counts active if time span >= 4h OR 3+ events. Rebalances don't penalize the count.

```python
active_days_4h = 0
for day, timestamps in day_events.items():
    timestamps.sort()
    span_hours = (timestamps[-1] - timestamps[0]) / 3600
    if span_hours >= 4 or len(timestamps) >= 3:
        active_days_4h += 1
```

### AAE Reputation Metrics

- **Consistency:** `active_days_4h / calendar_days`
- **Activity:** `total_withdrawals / active_days_4h`
- **Duration:** `days_active` since first deposit

### Cache

`/root/.hermes/scripts/.lfj-entry-cache.json` — pre-seeded, avoids expensive chain scan.

### Volume-Based Live Fee Calculation (NEW - Jul 3, 2026)

**Problem:** Fixed yield rates drift as pool volume changes. A hardcoded `DAILY_YIELD_RATE` ($0.00515/day) goes stale when volume or liquidity shifts. User reports actual fee doesn't match the estimate.

**Solution:** Calculate daily fees from live pool data every cron tick:
```
daily_fees = volume_24h × fee_rate × (position_value / TVL) × concentration_multiplier
```

**Pipeline (every 10-min tick):**
1. `fetch_price()` — DexScreener returns `price`, `volume_24h`, `liquidity` (TVL)
2. Fee rate = pool's swap fee in decimal (5 bps = `5 / 10000`)
3. Position's proportional TVL share = `lp_value / liquidity`
4. Total pool fees = `volume_24h × fee_rate`
5. Position's share = `total_pool_fees × tvl_share × concentration_multiplier`

**Calibration:** Concentration multiplier (4.92x for bid-ask) captures the concentrated liquidity benefit — our position earns ~4.9x a proportional share because bins are tight around the active price. Calibrated from: `actual_fee / (volume × fee_rate × tvl_share)`.

**Updates automatically** when volume or liquidity changes — no manual recalibration needed.

**Fallback:** When DexScreener returns zero volume, use a flat yield rate (`lp_value × 0.004`).

**Pitfall (Jul 3, 2026):** The cron script was updated in the profile path (`/root/.hermes/profiles/gentech/scripts/`) but the global path (`/root/.hermes/scripts/`) had the stale version. Cron resolves relative scripts from the profile path, but other tools may read from the global path. Always sync BOTH copies after changes:
```bash
cp /root/.hermes/profiles/gentech/scripts/*.py /root/.hermes/scripts/
```

### ATH Fee Tracking (User Preference)

Display the highest daily fee rate ever achieved, not cumulative fees:
- Seeded from known peak (e.g., $5.00/day)
- Stored in `.lfj-ath.json`
- Auto-updates when current rate exceeds stored ATH
- Display label: "ATH" not "All-time"

### Fee Trajectory Display Format (User Preference)

```
📈 Fee Trajectory
  Daily:    $0.2400 rate
├─ Week:    $1.68
├─ Month:   $7.32
├─ Year:    $87.60 projected
└─ ATH:     $5.00
```

- No prorated "Today" line — it confuses the picture
- Daily rate is the headline (matches LFJ UI)
- All projections are direct multipliers

### Tier Structure (User Preference)

- **Tier 0 = Grunt = $5/day** — entry milestone, hardcoded in cron
- Config milestones start at Tier 1 (above Grunt)
- Progress shown as % toward next tier

---

## Screenshot Analysis Fallback

When on-chain data isn't available from screenshots:

1. Try `browser_vision` first
2. If vision fails → OCR with tesseract
3. Dark-themed UIs produce garbage — crop into thirds and OCR each
4. Always present extracted data as "approximately X" and ask for confirmation

## AAE DeFi Hub App Architecture (Jul 16, 2026)

The AAE DeFi Hub is a dual-interface yield farm command center deployed on **gentechlabs.net** — one backend serving both a human dashboard and an agent API.

### Stack

| Layer | Technology | Location |
|-------|-----------|----------|
| **Frontend** | React + RainbowKit (wallet connect) | Cloudflare Pages — `defi.gentechlabs.net` |
| **Backend API** | Cloudflare Workers | `api.gentechlabs.net` (x402 gateway v7.0.0+) |
| **Agent API** | x402-gated endpoints | Same gateway — agents pay per call in USDC |
| **Data** | DexScreener / BlockRun / On-chain RPCs | Workers fetch live, KV caches for performance |
| **Auth** | Wallet Connect (human) / x402 proof (agent) | RainbowKit for UI, X-Payment-Proof header for API |

### Dual-Interface Principle

Same pool data, same position state, two front doors:

```
User Browser (React + RainbowKit) → defi.gentechlabs.net  (charts, controls)
Agent / Script → api.gentechlabs.net (x402)               (JSON, triggers)
                                           ↓
                    Workers → BlockRun / DexScreener / On-chain RPCs
                                           ↓
                                KV cache for performance
```

### API Endpoint Spec (v1)

**Human endpoints** (wallet-connect auth):

| Endpoint | Returns |
|----------|---------|
| `GET /pools` | All tracked pools with live APY, TVL, volume |
| `GET /pools/:id` | Single pool — bin distribution, shape, fee tier |
| `GET /positions` | User's positions across all chains |
| `GET /positions/:id` | Single position — fee breakdown, IL, shape efficiency |
| `GET /dashboard` | Today's fees, total fees, active positions, current rank |
| `GET /ranks` | Scout→Raider→Greek→Warrior progress, next milestone |

**Agent endpoints** (x402-gated):

| Endpoint | Cost | What |
|----------|------|------|
| `GET /agent/positions/:id` | $0.01 | Read position + shape efficiency |
| `POST /agent/rebalance` | $0.025 | Get rebalance recommendation |
| `POST /agent/compound` | $0.025 | Trigger fee compounding |
| `GET /agent/alerts` | $0.01 | IL risk, shape drift, pool health |

### Deployment Plan

| Week | Milestone |
|------|-----------|
| **1** | Single-chain MVP (Avalanche) — backend + frontend on `defi.gentechlabs.net` |
| **2** | Multi-chain (add Solana via Meteora DLMM) |
| **3** | Agent automation + rank engine live |

## Rank Engine (Jul 16, 2026)

Gamified tier progression modeled on Call of Duty prestige system. Every yield farmer has a visible rank based on sustained daily fee generation.

### Tier Definitions

```json
{
  "scout":   { "target": 5,   "icon": "🔭", "color": "#8899aa" },
  "raider":  { "target": 10,  "icon": "⚔️", "color": "#3b82f6" },
  "greek":   { "target": 25,  "icon": "🏛️", "color": "#a855f7" },
  "warrior": { "target": 50,  "icon": "🛡️", "color": "#e84142" },
  "elite":   { "target": 100, "icon": "⚡",  "color": "#00ff88" },
  "apex":    { "target": 200, "icon": "👑", "color": "#ffd700" }
}
```

### Ranking Formula

```
7-day rolling avg fees = sum(last 7 days) / 7

If avg >= 200 → Apex
If avg >= 100 → Elite
If avg >= 50  → Warrior
If avg >= 25  → Greek
If avg >= 10  → Raider
If avg >= 5   → Scout
Else          → Unranked
```

### Time-in-Pool Requirement

Rank progression requires BOTH fee targets AND minimum active pool time:

| Rank | Min Daily Fee | Min Active Pool Time | Streak to Earn |
|------|--------------|----------------------|----------------|
| Scout | $5 | 4 hrs | 3 days |
| Raider | $10 | 6 hrs | 5 days |
| Greek | $25 | 8 hrs | 7 days |
| Warrior | $50 | 10 hrs | 14 days |
| Elite | $100 | 12 hrs | 21 days |
| Apex | $200 | 12 hrs | 30 days |

**Time counts when:** Position is in-range and earning fees. Out-of-range time does not count.

### Prestige System

When a user reaches Apex, they may **prestige** — rank resets to Scout but they earn a permanent star:

| Prestige | Badge | Requirement |
|----------|-------|-------------|
| 0 | No star | First climb through all ranks |
| ⭐ 1st | Silver star | Hit Apex once, reset |
| ⭐⭐ 2nd | Gold star | Hit Apex twice |
| ⭐⭐⭐ 3rd | Red star | Three times |
| 🏆 | Master Yieldman | 5 prestige cycles |

### Subscription Meritocracy

Each prestige permanently reduces the monthly subscription fee by **$5**:

| Prestige | Base $29/mo | You Pay | Maintenance Requirement |
|----------|-------------|---------|------------------------|
| 0 | $29 | $29 | None |
| ⭐ 1 | -$5 | $24 | Maintain Raider avg |
| ⭐⭐ 2 | -$10 | $19 | Maintain Greek avg |
| ⭐⭐⭐ 3 | -$15 | $14 | Maintain Warrior avg |
| ⭐⭐⭐⭐ 4 | -$20 | $9 | Maintain Elite avg |
| 🏆 5 | -$25 | **$4** | Maintain Apex avg |

If 7-day avg drops below maintenance rank for 14 consecutive days, discount decays one tier. Subscription price displays your skill level.

### Streak Logic

| Event | Result |
|-------|--------|
| Hit all targets for the day | Streak +1 day |
| Miss one day | Streak freezes (no loss) |
| Miss 3 consecutive days | Streak decays -1/day |
| Miss 7 days | Rank drops one tier |
| Recover | Streak resumes from freeze point |

## The 3-in-1 Combo (Jul 16, 2026)

Three operating modes, one agent, all liquidity shapes:

| Mode | Who Drives | Best For |
|------|-----------|----------|
| **Dry Powder** | Agent full auto | Stablecoin vault — cross-chain rotation, capital preservation |
| **Normal** | Agent full auto | Active LP — shape-adjusted fee capture, auto-rebalance, compounding |
| **Hybrid** | Human + Agent | Agent handles routine + alerts, human makes strategic calls |

Progression path:

| Phase | Rank Range | Mode |
|-------|-----------|------|
| Learn | Scout → Raider | **Hybrid** — you open, agent monitors |
| Scale | Greek → Warrior | **Normal** — agent rebalances + compounds |
| Master | Elite → Apex | **Dry Powder** — agent rotates chains + narratives |

## Meteora DLMM Support (Jul 16, 2026)

Meteora's DLMM on Solana uses the **same bin-based architecture as Trader Joe's Liquidity Book** — discrete price bins, concentrated liquidity, same three shapes (Spot, Curve, Bid-Ask).

**LP Shape Detector works on Meteora pools without modification.** The bin-distribution analysis (center concentration, edge concentration, peak position, symmetry, skew) reads from the same bin data structure.

Key integration points:
- **DLMM program ID:** `LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo` on Solana mainnet
- **TAO/USDC pool:** ~$194K liq, $67K daily volume, 270 txns/24h — real liquidity
- **LP Army community** — Solana's largest LP community, build Gentech reputation
- **Dynamic fees** — rise during volatility, protect LPs
- **Liquidity mining** — reward pools distribute incentive tokens to active positions
- **Raydium CLMM** is Uniswap V3-style (continuous ranges, no bins) — NOT compatible with shape detector

## References

- `references/yield-comparison-pattern.md` — Yield strategy comparison: how to research and compare APYs, entry costs, risks across strategies using live data
- `references/tactical-retreat-defense.md` — Breakout detection timer, SENTINEL/RETREATED state machine, FOMC auto-defense (Jul 2026)
- `references/config-drift-incident.md` — 7 config copies, HERMES_HOME path resolution
- `references/job-registry-snapshot.md` — discovered sprawl across profiles
- `references/cron-provider-troubleshooting.md` — 401 errors, missing skills
- `references/persistent-alert-debounce.md` — hourly silence (deprecated, retained for reference)
- `references/entry-price-fix-protocol.md` — entry price drift after rebalances, geometric mean formula, 9-file sync pattern (Jun 29, 2026)
- `references/entry-price-fix-script.py` — executable script for atomic entry price updates
- `references/shape-detection-protocol.md` — LP shape detection fix, 7-54% efficiency calculation errors, GLM-5.2 audit methodology, multi-source synchronization (Jun 30, 2026)
- `references/lp-monitor-v2-architecture.md` — Config-first, dashboard-free monitor design that eliminates multi-writer race conditions (Jun 30, 2026)
- `references/manual-rebalance-sync-protocol.md` — Manual rebalance data sync workflow with verification steps and executable script (Jul 1, 2026)
- `scripts/fee-tracker.py` — 24/7 fee accumulator using free APIs only (DexScreener, CoinGecko, DefiLlama). Cron: every 1h, no_agent=true. Config at `scripts/fee-tracker-config.json`
- `references/current-defi-strategy.md` — Jordan's current DeFi playbook: $200/day AVAX-USDC LP target + spot accumulation (TAO/SOL/LINK) + Avalanche L1 infrastructure timeline (Jul 16, 2026)
