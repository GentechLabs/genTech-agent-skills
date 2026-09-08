# Position Tracker Drift Incident — Jun 28, 2026

## Summary

Cron job reported completely wrong data due to stale position tracker:
- **Reported:** Shape `BID-ASK`, Entry `$6.13`, IL `+2.71%`
- **Actual:** Shape `CURVE`, Entry `$6.23`, IL `+1.06%`

User noticed: "Wrong liquidity shape, entry price, and Impermanent loss. Are you using our skills to read on chain data to determine liquidity shape?"

## Root Cause

Position tracker (`.lfj-position-tracker.json`) was never updated after Jordan's rebalance to curve. The cron job reads from tracker FIRST before falling back to on-chain data, so it used stale values.

## Reproduction Recipe

```python
# Check current tracker state
cat /root/.hermes/profiles/gentech/scripts/.lfj-position-tracker.json

# Expected after curve rebalance:
{
  "shape": "curve",
  "entry_avax_price": 6.23,
  "rebalance_type": "curve"
}

# Actual (stale):
{
  "shape": "bid-ask",
  "entry_avax_price": 6.13,
  "rebalance_type": "bid-ask"
}
```

## Fix Applied

1. Ran on-chain reader with correct shape:
```bash
cd /root/projects/lp-reader && node reader.mjs --wallet 0x7ebff... --shape curve
```

2. Updated BOTH tracker paths:
```bash
# Profile path (cron reads from here)
/root/.hermes/profiles/gentech/scripts/.lfj-position-tracker.json

# Global path (must stay synced)
/root/.hermes/scripts/.lfj-position-tracker.json
```

3. Updated tracker content:
```json
{
  "shape": "curve",
  "entry_avax_price": 6.23,
  "rebalance_type": "curve",
  "avax_amount": 1.1396,
  "usdc_amount": 39.89,
  "position_value_usd": 47.08,
  "range_low": 6.1899,
  "range_high": 6.3783,
  "current_price": 6.3085
}
```

## Prevention

**After ANY Jordan rebalance:**

1. **Detect rebalance** — Watch for user saying "I rebalanced to X" or similar
2. **Run on-chain reader** with appropriate shape flag:
```bash
node reader.mjs --wallet <address> --shape <curve|bid-ask|spot>
```
3. **Update position tracker** with on-chain values
4. **Sync BOTH paths** (profile + global) to prevent drift
5. **Verify** next cron report matches on-chain data

## Cron Job Data Flow

```
Jordan rebalances on LFJ UI
    ↓
1. .lfj-position-tracker.json  ← SOURCE OF TRUTH (MUST UPDATE)
    ↓
2. .lfj-aae-config.json        ← mirrors position tracker
    ↓
3. On-chain reader (run-reader.py) → reads shape from position tracker
    ↓
4. defi-data.json               ← reader writes shape + calculated efficiency
    ↓
5. Hub DeFi tab                 ← reads from defi-data.json
6. Rainbow data                 ← monitor writes BOTH locations
```

**Critical:** If step 1 is skipped, everything downstream gets wrong data.

## Related Skills

- `defi-lp-monitoring` — main LP monitoring workflow
- `lp-shape-detector` — on-chain shape detection