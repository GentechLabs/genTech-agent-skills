# Config-First Architecture Pattern

**Date:** June 30, 2026  
**Problem:** Multiple automated scripts kept overwriting manual fixes to dashboard data  
**Root Cause:** Scripts prioritized auto-detection over user-configured values  

## Incident Summary

The cron job kept displaying wrong data (shape: "curve" instead of "bid-ask", entry price: $6.23 instead of $6.38) despite repeated fixes. Investigation revealed:

1. **18 scripts write to dashboard** — `hub-sync-nightly.py`, `pool-reader.py`, `lp-shape-detector.py`, etc.
2. **Shape detector auto-detects incorrectly** — Analyzes bin distribution and classifies bid-ask as "curve"
3. **Multiple data sources without hierarchy** — Config, position tracker, dashboard, all updating independently
4. **Monitor script reads from dashboard** — Dashboard was the first priority, but kept getting corrupted

## Config-First Architecture Solution

**Principle:** User's config is the single source of truth. All scripts must read config before auto-detecting. Auto-detection only happens if config explicitly says "unknown" or "curve".

### Implementation Pattern

```python
# 1. CONFIG-FIRST: Read user's choice FIRST
def classify_shape(metrics: dict) -> dict:
    try:
        with open('/root/.hermes/scripts/.lfj-aae-config.json', 'r') as f:
            user_config = json.load(f)
        user_shape = user_config.get('position', {}).get('shape', None)
        
        # Only auto-detect if user explicitly wants it
        if user_shape and user_shape not in ["unknown", "curve"]:
            print(f"Using user-configured shape: {user_shape}")
            return {
                "shape": user_shape,
                "confidence": 100,
                "shape_source": "user_config",
                "reason": "User-configured shape override",
                **metrics,
            }
    except Exception as e:
        print(f"Warning: Could not read user config: {e}")
    
    # 2. AUTO-DETECT: Only if config allows
    # ... existing auto-detection logic ...
```

### Data Source Hierarchy (Updated)

```
1. CONFIG (source of truth) → .lfj-aae-config.json
   ↓
2. POSITION TRACKER → .lfj-position-tracker.json (should mirror config)
   ↓
3. DASHBOARD → defi-data.json (read-only for auto-detection scripts)
   ↓
4. ON-CHAIN DATA → For verification, not primary source
```

### Monitor Script Priority Fix

```python
# BEFORE: Dashboard first (gets overwritten)
shape = normalize_shape(lp.get("shape") or pos_cfg.get("shape") or cfg.get("shape", "curve"))

# AFTER: Config first (immune to dashboard corruption)
shape = normalize_shape(pos_cfg.get("shape") or cfg.get("shape", "curve"))
```

## Verification Protocol

After implementing config-first architecture:

1. **Test shape detector**: Should print "Using user-configured shape: bid-ask"
2. **Test monitor script**: Should show correct shape regardless of dashboard state
3. **Verify all data sources**: Config → Tracker → Dashboard should all show same values
4. **Monitor for regression**: Next 1-2 cron cycles should maintain correct data

## When Config-First Doesn't Work

If dashboard corruption persists despite config-first fixes:

1. **Disable dashboard writers** — Make dashboard read-only (chmod 444)
2. **Monitor script unlocks temporarily** — Update, then re-lock
3. **Find the corrupting script** — Check file modification times and cron schedules
4. **Fix the corruptor** — Either disable it or make it config-first

## Key Learning

**User intent > Auto-detection.** When Jordan sets `shape: "bid-ask"`, that's not a suggestion — it's a command. Automated scripts must respect user choices unless explicitly overridden.

Auto-detection is a tool for when the user doesn't know the shape or wants to verify their manual classification. It should never override an explicit user choice.