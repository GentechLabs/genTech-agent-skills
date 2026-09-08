# Entry Price Sync Issue Fix Protocol

## Problem Description
After manual rebalance, cron scripts may continue showing outdated entry price while position has new range, causing incorrect IL calculations.

**Symptoms:**
- Cron shows "Entry: $6.71" but current price is $6.46
- Position range shows $6.40-$6.62 (correct from rebalance)
- IL calculation shows -3.15% (wrong)
- Actual IL should be -0.47%

**Root Cause:**
- Dashboard data (`defi-data.json`) has stale entry price
- Multiple config files not updated after manual rebalance
- Cron scripts read from stale data sources

## Fix Protocol

### Step 1: Verify Current Range
```bash
# Check current position range from monitor
python3 ~/.hermes/profiles/gentech/scripts/defi-lp-consolidated.py

# Look for "Range: $X.XXXX - $X.XXXX" in output
```

### Step 2: Calculate Correct Entry Price
Entry price = geometric mean of range bounds
```python
import math
range_low = 6.4039  # from monitor output
range_high = 6.6186  # from monitor output
entry_price = math.sqrt(range_low * range_high)
print(f"Corrected entry price: ${entry_price:.4f}")
# Result: $6.5104
```

### Step 3: Run Fix Protocol
```bash
python3 ~/.hermes/profiles/gentech/scripts/fix-entry-price.py --range 6.4039 6.6186
```

### Step 4: Verify Fix
```bash
# Check that all entry prices are now consistent
python3 ~/.hermes/profiles/gentech/scripts/defi-lp-consolidated.py

# Should show correct IL calculation
```

## Files Updated by Fix Protocol
- `.lfj-position-tracker.json` (2 copies)
- `defi-data.json` (4-5 copies)
- All `.lfj-aae-config.json` files (9 copies)

## Prevention
After manual rebalance, always update all config files using the fix protocol rather than updating individual files.

## Detection
Monitor for: Cron entry price ≠ range midpoint AND current price within new range