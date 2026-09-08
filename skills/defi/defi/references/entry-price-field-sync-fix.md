# Entry Price Field Synchronization Fix

## Problem (Jun 29, 2026)

**Symptom:** Cron job showing incorrect IL calculations + efficiency tracking after rebalance
- Dashboard showed correct entry price: $6.7119
- Cron showed wrong IL: +7.41% instead of -0.03%
- Cron showed wrong efficiency: 51% instead of ~49%

**Root Cause:** Field naming inconsistency across multiple files:
- **Position tracker:** Had both `entry_avax_price: 6.23` (OLD) and `entry_price: 6.711891576895444` (NEW)
- **Cron script:** Using `entry_avax_price` field instead of the correct `entry_price`
- **Dashboard:** Using correct `entry_price` field

## Fix Applied

### 1. Updated Cron Script (`defi-lp-consolidated.py`)

**Change:** Priority fallback for entry price field reading
```python
# BEFORE (line 723)
entry_price = position_tracker.get("entry_avax_price", "?")

# AFTER  
entry_price = position_tracker.get("entry_price", position_tracker.get("entry_avax_price", "?"))
```

**Also fixed line 1333:**
```python
# BEFORE
entry_p = pos_tracker.get("entry_avax_price") or pos_cfg.get("entry_price", 6.30)

# AFTER
entry_p = pos_tracker.get("entry_price") or pos_tracker.get("entry_avax_price", 6.30)
```

### 2. Updated Position Tracker (`.lfj-position-tracker.json`)

**Removed deprecated field, kept single source of truth:**
```json
{
  "last_rebalance": "rebalance_detected",
  "entry_price": 6.711891576895444,  // NEW: Single entry price field
  // ... other fields
}
```

**REMOVED:** `entry_avax_price: 6.23` to prevent conflicts

### 3. Verification

**Manual test after fix:**
```bash
python3 /root/.hermes/profiles/gentech/scripts/defi-lp-consolidated.py
# Result: ✅ Rainbow data synced: 🟡 Harvest Mode (efficiency: 69%)
```

**IL verification:**
```
Entry Price: 6.711891576895444
Current Price: 6.71
IL: -0.03% (correct!)
Range: $6.6054 - $6.8201
Efficiency: ~49% (correct)
```

## Prevention

### Check for Field Conflicts
```bash
# Find all entry price fields in codebase
grep -r "entry.*price" ~/.hermes/scripts/ --include="*.py" | grep -E "(get\(|\[\"" | head -10
```

### Standardize Field Names
**Primary field:** `entry_price` (numeric, geometric mean of range)
**Legacy field:** `entry_avax_price` (deprecated, remove after migration)

### Multi-System Sync Protocol
After ANY rebalance:
1. Update `.lfj-position-tracker.json` with single `entry_price` field
2. Update `defi-data.json` with matching `entry_price` in both `lpPosition` and `hero` sections
3. Run `fix-entry-price.py --range [LOW] [HIGH]` to enforce consistency
4. Verify cron job uses correct field on next run

## Detection Script

**Check for field conflicts:**
```bash
python3 -c "
import json
import glob

# Check all config files for inconsistent entry price fields
configs = glob.glob('/root/.hermes/**/scripts/.lfj-aae-config.json', recursive=True) + ['/root/.hermes/scripts/.lfj-position-tracker.json']

for config in configs:
    with open(config) as f:
        data = json.load(f)
    
    old_field = data.get('entry_avax_price')
    new_field = data.get('entry_price')
    
    if old_field and new_field and abs(old_field - new_field) > 0.01:
        print(f'❌ CONFLICT: {config}')
        print(f'   old: {old_field}, new: {new_field}')
    elif new_field:
        print(f'✅ OK: {config} → {new_field}')
" 
```

## Additional Context

This fix resolves **Critical Pitfall #25** more comprehensively - the issue wasn't just hardcoded data, but inconsistent field naming that persisted even after manual updates.

**Cross-reference:** 
- Section 16: Entry Price Protocol
- Critical Pitfall #25: defi-master-cron.py hardcoded stale position data