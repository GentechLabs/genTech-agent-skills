# Manual Rebalance Sync Protocol

**Date:** July 1, 2026  
**Context:** User performed manual LP rebalance but cron job showed stale data

## Problem Statement

Manual position rebalances aren't automatically reflected in config files and position tracker. This causes false "OUT OF RANGE" alerts because:

1. Cron job fetches **live price** from DexScreener (accurate)
2. Cron job reads **range** from config/position tracker (stale)
3. Result: Live price vs stale range → false OUT OF RANGE status

## Critical Learning: Verify Before Syncing

**The monitor is usually correct.** Before assuming stale data:

```bash
# 1. Fetch live price from DexScreener
curl -s "https://api.dexscreener.com/latest/dex/pairs/avalanche/0x864d4e5ee7318e97483db7eb0912e09f161516ea" | jq '.pairs[].priceUsd'

# 2. Check current range
cat /root/.hermes/scripts/.lfj-aae-config.json | jq '.position | {range_low, range_high}'

# 3. Manual verification
# Example: Price $6.63, Range $6.3656-$6.5856
# Is $6.63 >= $6.3656 AND $6.63 <= $6.5856?
# $6.63 >= $6.3656 ✅ True
# $6.63 <= $6.5856 ❌ False
# Result: OUT OF RANGE is CORRECT → rebalance needed
```

## Two Scenarios

| Scenario | Monitor Says | Reality | Action |
|----------|--------------|---------|--------|
| **Monitor correct** | OUT OF RANGE | Price outside range | **Rebalance needed** |
| **Monitor stale** | OUT OF RANGE | Price in range, config outdated | **Sync data** |

## Sync Protocol

### Step 1: Verify Current Position

```bash
# Check actual position vs market price
CURRENT_PRICE=$(curl -s "https://api.dexscreener.com/latest/dex/pairs/avalanche/0x864d4e5ee7318e97483db7eb0912e09f161516ea" | jq -r '.pairs[].priceUsd')
RANGE_LOW=$(cat /root/.hermes/scripts/.lfj-aae-config.json | jq -r '.position.range_low')
RANGE_HIGH=$(cat /root/.hermes/scripts/.lfj-aae-config.json | jq -r '.position.range_high')

# Check if actually in range
python3 -c "print(f'Price: \${CURRENT_PRICE}, Range: \${RANGE_LOW}-\${RANGE_HIGH}, In range: {float(RANGE_LOW) <= float(CURRENT_PRICE) <= float(RANGE_HIGH)}')"
```

### Step 2: Update Position Tracker

```python
import json
import datetime
from pathlib import Path

# Paths
CONFIG_PATH = Path("/root/.hermes/scripts/.lfj-aae-config.json")
TRACKER_PATH = Path("/root/.hermes/scripts/.lfj-position-tracker.json")

# Read config for base data
with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

# Get current price from DexScreener
current_price = 6.63  # Fetch from API or use known value

# Create updated position tracker
tracker_data = {
    "last_rebalance": f"manual_sync_{datetime.datetime.now().strftime('%Y-%m-%d')}",
    "last_rebalance_source": "manual_verification", 
    "rebalance_type": "manual",
    "entry_price": config["position"]["entry_price"],
    "avax_amount": config["position"]["token0_amount"],
    "usdc_amount": config["position"]["token1_amount"],
    "range_low": 6.40,  # Updated range
    "range_high": 6.80, # Updated range
    "current_price": current_price,
    "shape": config["position"]["shape"],
    "strategy": config["position"]["strategy"],
    "bins": config["position"]["bins"],
    "daily_fees_usd": 0.201,
    "cumulative_fees_usd": 1.0325,
    "last_updated": datetime.datetime.now().isoformat(),
    "source": "manual_sync",
    "entry_avax_price": config["position"]["entry_price"],
    "updated": datetime.datetime.now().strftime('%Y-%m-%d')
}

# Write updated tracker
with open(TRACKER_PATH, 'w') as f:
    json.dump(tracker_data, f, indent=2)

print("✅ Position tracker synced")
```

### Step 3: Update Config File

```python
# Update config to match rebalanced range
config['position']['range_low'] = 6.40
config['position']['range_high'] = 6.80
config['range_low'] = 6.40
config['range_high'] = 6.80

# Write updated config
with open(CONFIG_PATH, 'w') as f:
    json.dump(config, f, indent=2)

print("✅ Config file synced")
```

### Step 4: Verify Sync

```bash
# Test monitor output
python3 /root/.hermes/profiles/gentech/scripts/lp-monitor-v2.py

# Expected: Status should show IN RANGE if price is within new range
```

## Quality Gates

| Check | Pass Condition | Action |
|-------|----------------|--------|
| Current price in range | $6.40 ≤ $6.63 ≤ $6.80 | ✅ PASS |
| Shape matches config | "bid-ask" == "bid-ask" | ✅ PASS |
| Monitor status | IN RANGE | ✅ PASS |
| Live price matches DexScreener | Manual fetch == monitor output | ✅ PASS |

## Executable Script

**Location:** `scripts/lp-data-sync.py`

**Usage:**
```bash
python3 /root/.hermes/profiles/gentech/scripts/lp-data-sync.py
```

**Features:**
- Fetches current price from DexScreener
- Updates position tracker with manual rebalance values
- Verifies sync by running monitor test
- Reports success/failure with clear status

## Prevention Protocol

**After ANY manual rebalance:**

1. **Immediately update position tracker** with new range values
2. **Verify monitor output** shows correct status
3. **Update all config files** with new range
4. **Test cron job** to ensure it picks up changes

**Automated reminder:** Add to rebalance checklist in wallet interface

## Case Study: July 1, 2026

**User statement:** "Sorry I am rebalancing, check now"

**Investigation:**
1. Monitor showed: Price $6.63, Range $6.3656-$6.5856 → OUT OF RANGE
2. User believed they were IN RANGE
3. **Verification:** $6.63 > $6.5856 → Monitor was CORRECT
4. **Action:** User completed rebalance to wider range ($6.40-$6.80)
5. **Sync:** Updated config and position tracker
6. **Result:** Monitor now shows IN RANGE with 52.5% efficiency

**Lesson:** Don't assume monitor is wrong. Verify with live data first.

## Integration with LP Monitor v2

The `lp-monitor-v2.py` script is designed to work with this protocol:

- ✅ Reads config from hardcoded path (`/root/.hermes/scripts/`)
- ✅ Fetches live price from DexScreener API
- ✅ Calculates efficiency based on current range
- ✅ Shows accurate status after manual sync

**After manual rebalance:**
1. Sync config + position tracker
2. Run `lp-monitor-v2.py --test` to verify
3. Cron job will automatically pick up changes next run

## References

- LP Monitor v2 Architecture: `references/lp-monitor-v2-architecture.md`
- Config-First Design: Eliminates multi-writer race conditions
- DexScreener API: Real-time price feed for Avalanche pools