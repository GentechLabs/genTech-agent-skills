# Automated Script Overwrite Incident (Jun 30, 2026)

## Incident Summary

The LP monitor cron job kept printing **wrong data** (shape: "curve", entry price: $6.23 vs correct $6.38, wrong position amounts) despite multiple manual fixes. The root cause was an **automated shape detector script** that kept overwriting manual dashboard updates.

## Root Cause

### Primary: lp-shape-detector.py Overwrites

The `lp-shape-detector.py` script analyzes on-chain bin distribution from Trader Joe and classifies the LP position shape. It then **writes to `defi-data.json`**, overwriting any manual fixes.

- **Problem**: The detector incorrectly classified a bid-ask position as "curve"
- **Impact**: Every time the detector ran, it reverted manual fixes (shape: bid-ask → curve, entry price: $6.38 → NOT_SET)
- **Evidence**: Dashboard timestamps showed updates at `19:50:56` after manual fixes at `19:28:13`

### Secondary: Multiple Dashboard-Writing Scripts

Found **18 scripts** that write to the dashboard:

```
✍️ WRITES to dashboard:
  • poe2-patch-monitor.py
  • fed-event-tracker.py  
  • hub-sync-nightly.py
  • defi-lp-consolidated.py
  • pool-reader.py
  • narrative-rotation.py
  • build-health-check.py
  • lp-shape-detector.py
  • audit-lp-monitor.py
  • portfolio_sync.py
  • fix-entry-price.py
  • ...and more
```

Each script could potentially overwrite data from other scripts, creating a **race condition**.

### Tertiary: Dual Script Versions

The monitor script exists in **two locations**:

1. `/root/vaults/gentech/Strategies/scripts/defi-lp-consolidated.py` (vault)
2. `/root/.hermes/profiles/gentech/scripts/defi-lp-consolidated.py` (profile)

The **cron job runs from the profile path**. If you fix the vault version but not the profile version, the fix never takes effect.

## Diagnostic Path

### Step 1: GLM-5.2 Audit Revealed Data Reversion

```
🔍 CURRENT DASHBOARD STATE:
  Shape: curve  ← Should be bid-ask (was fixed)
  Entry Price: NOT_SET  ← Should be 6.3792 (was fixed)
  AVAX: 1.454999  ← Should be 3.262981 (was fixed)
  USDC: 36.754685  ← Should be 27.274526 (was fixed)

🔍 FILE MODIFICATION TIMES:
  defi-lp-consolidated.py: 19:28:13 (manual fix time)
  .lfj-aae-config.json: 19:28:13 (manual fix time)  
  defi-data.json: 19:50:56  ← OVERWRITTEN AFTER FIX
```

### Step 2: Found the Overwrite Culprit

Searched for scripts that reference `defi-data.json` and found `lp-shape-detector.py`:

```python
# lp-shape-detector.py classification logic
classify_shape() → ['unknown', 'curve', 'bid-ask', 'spot', 'asymmetric']
json.dump(dashboard, f)  ← OVERWRITES MANUAL FIXES
```

### Step 3: Investigated Shape Detection Logic

The detector uses `analyze_bin_distribution()` and `classify_shape()` functions to determine shape from bin data. For Jordan's Trader Joe bid-ask position, it incorrectly returned "curve".

## Temporary Emergency Fix

Applied a **manual override** to force dashboard data from config:

```python
# Force correct values and disable auto-detection
dashboard['lpPosition']['shape_source'] = 'config_manual'
dashboard['lpPosition']['auto_shape_detection_disabled'] = True
```

This prevents automatic overwrites until the detector is fixed or disabled.

## Permanent Solutions

### Option 1: Fix lp-shape-detector.py Classification

Update the `classify_shape()` function to correctly identify bid-ask shapes:

```python
def classify_shape(bin_distribution):
    # Look for dual peaks near current price (bid-ask signature)
    # vs single peak at center (curve signature)
    # vs single narrow peak at current price (spot signature)
    
    if has_dual_peaks(bin_distribution):
        return "bid-ask"
    elif has_center_peak(bin_distribution):
        return "curve"
    elif has_narrow_peak(bin_distribution):
        return "spot"
    else:
        return "unknown"
```

### Option 2: Disable the Detector Cron Job

Find and disable the cron job that runs `lp-shape-detector.py`:

```bash
# List cron jobs
hermes cron list

# Find the job that uses lp-shape-detector.py
# Then disable or remove it
hermes cron update --job-id <ID> --enabled false
```

### Option 3: Make Dashboard Read-Write Coordinated

Implement a **dashboard lock system** where only one script can write at a time:

```python
# Use file locking to prevent concurrent writes
import fcntl

with open('/root/ProtoJay4789.github.io/DeFi/defi-data.json', 'r+') as f:
    fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # Exclusive lock
    
    # Read, modify, write
    data = json.load(f)
    # ... modify data ...
    json.dump(data, f)
    
    fcntl.flock(f.fileno(), fcntl.LOCK_UN)  # Release lock
```

## Verification Protocol

After ANY manual dashboard fix:

1. **Check for Overwrite Scripts**: List all cron jobs that write to dashboard
2. **Time-Stamp Check**: Verify file modification times don't show later updates
3. **Monitor Next Cycle**: Watch for 1-2 cron cycles to confirm no reversion
4. **Run Universal Verifier**: Use `gentech-verify.py` to check all quality gates

```bash
# Monitor for regression
python3 /root/.hermes/profiles/gentech/scripts/defi-lp-consolidated.py
# Check output: Shape should remain BID-ASK
```

## Key Learning

**Automated data pipelines can overwrite manual fixes.** When multiple scripts write to the same file, you need either:

1. **Single source of truth** with all other scripts reading only, OR
2. **Coordinated write access** with locking, OR  
3. **Conflict resolution system** that prioritizes certain data sources

In this case, the position tracker should be the **sole write source** for shape/range/entry/amounts, with all other scripts reading from it.

## Related Skills

- **defi-lp-monitoring** — Main DeFi LP monitoring system
- **gentech-ops** — Operational patterns and verification protocols