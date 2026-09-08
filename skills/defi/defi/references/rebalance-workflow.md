# Rebalance Workflow (Full)

> Absorbed from `lfj-rebalance-handler` skill. Complete rebalance processing protocol.

## Step 1: Parse Input

**Two modes:**
- **Screenshot mode** — extract from image: current price, new range, shape, balances
- **Direct params mode** — Jordan gives exact values, skip screenshot parsing

**Extract:** Current price, New range (min–max), Shape (spot/curve/bid-ask), Position value, Pool stats

## Step 2: Update ALL .lfj-aae-config.json Copies (9 files)

```bash
find /root/.hermes -name ".lfj-aae-config.json"
```

Update `position` object in EACH file:
```json
{
  "position": {
    "total_usd": <total>,
    "token0_amount": <avax>,
    "token1_amount": <usdc>,
    "range_low": <min>,
    "range_high": <max>,
    "shape": "<curve|bid-ask|spot>"
  }
}
```

## Step 3: Update ALL .lfj-aae-state.json Copies (5 files)

```bash
find /root/.hermes -name ".lfj-aae-state.json"
```

Update: `last_price`, `last_position_usd`, `last_check`, append to `price_history` and `tvl_history`.

Update `last_rebalance`:
```json
{
  "timestamp": "ISO 8601",
  "shape": "<shape>",
  "range_low": <min>,
  "range_high": <max>,
  "position_value_usd": <value>,
  "avax_amount": <amount>,
  "usdc_amount": <amount>
}
```

## Step 4: Update Position Trackers (PRIMARY source of truth)

```bash
find /root/.hermes -name ".lfj-position-tracker.json"
```

Update: `entry_avax_price`, `range_low`, `range_high`, `shape`, `strategy`, `avax_amount`, `usdc_amount`, `position_value_usd`, `last_rebalance`, `last_rebalance_source`

**⚠️ Copy main to profile after updating:**
```bash
cp /root/.hermes/scripts/.lfj-position-tracker.json /root/.hermes/profiles/gentech/scripts/
```

## Step 4b: Update Dashboard Files

**5 data paths:**

1. **`DeFi/defi-data.json`** — hero, lpPosition, curveData, strategyAdvisor, feeMilestones
2. **`DeFi/defi-dashboard.html`** — hardcoded values in fetchLiveData()
3. **`hub.html`** — RANGE_LOW, RANGE_HIGH, AVAX_HELD, USDC_HELD, SHAPE constants
4. **`HQ/config/defi-lp-config.env`** — env vars for cron scripts
5. **`Strategies/scripts/defi-master-cron.py`** — POOL dict with range/shape

**⚠️ Triple data path:** If any path is missed, dashboard shows stale data.

## Step 5: Check Cron Scripts & run-reader.sh

### 5a. Update run-reader.sh shape default (CRITICAL)
```bash
grep 'SHAPE=' /root/vaults/gentech/scripts/run-reader.sh
```
Must match current shape. If wrong, reader overwrites defi-data.json with wrong shape.

### 5b. Check hardcoded ranges in scripts
```bash
grep -n "range_low\|range_high\|RANGE_LOW\|RANGE_HIGH"   /root/vaults/gentech/03-Strategies/scripts/lp-*.py
```

### 5c. Check Cron Job Prompts
If cron prompt has hardcoded range, update it too.

## Step 6: Confirm to Jordan

```
✅ Position updated — all automated jobs synced
Range: {low} – {high} | Shape: {shape}
Value: ${total} ({avax} AVAX + {usdc} USDC)
Entry: ${entry_price} | IL: {il}%
Configs updated: {count} files | Trackers: {count} files
📊 LP vs Staking: {apr}% vs 7% — {outperforming/underperforming}
```

## Step 7: Verify Cron Reads Correct Data

```bash
cd /root/.hermes/profiles/gentech/scripts && python3 defi-lp-consolidated.py 2>&1 | head -20
```

Expected: Report shows new range, new shape, correct efficiency.

## Step 8: Verify All Copies In Sync

```python
import json, glob
for f in glob.glob('/root/.hermes/**/scripts/.lfj-aae-config.json', recursive=True):
    with open(f) as fh: data = json.load(fh)
    pos = data.get("position", {})
    print(f"{f} → {pos.get('range_low')}-{pos.get('range_high')}")
```

All should show new range.

## Pitfalls

- **HERMES_HOME resolves to profile dir** — Update BOTH global and profile-specific files
- **Monitor reads from tracker first** — Tracker is primary source, not defi-data.json
- **run-reader.sh shape default** — If wrong, overwrites dashboard data
- **Multiple config copies** — Updating only one causes stale data in other profiles
- **Shape display mapping** — `bidirectional` → display as `BID-ASK`

## DCA Scaling

| Efficiency Zone | DCA % of Position |
|-----------------|-------------------|
| ≥70% (center) | 15% |
| 50-70% (mid) | 12% |
| 30-50% (low) | 10% |
| <30% (edge) | 5% |
| Floor | $5 minimum |

## Gas Cost Note

Avalanche gas is ~$0.01. Core wallet covers gas on "free gas" transactions.
