# Shape Detection Critical Protocol

**Date:** Jun 30, 2026  
**Issue:** LP shape detection returning wrong shape ("curve" vs "bid-ask")  
**Impact:** 7-54% efficiency calculation errors compromising rebalancing decisions  
**Resolution:** ✅ GLM-5.2 audit + multi-source synchronization

## Problem Description

### Root Cause Analysis
- Dashboard data source had conflicting `shape: "curve"` vs config `shape: "bid-ask"`
- Monitor script missing "bid-ask" alias in `normalize_shape` function
- No cross-source validation protocol

### Impact Analysis
Different efficiency formulas produce wildly different results:

| Range Position | Curve Formula | Bidirectional Formula | Difference |
|----------------|---------------|----------------------|------------|
| 73.2% | 53.6% | 46.4% | 7.2% |
| 61.4% | 77.3% | 22.7% | 54.6% |

**Formulae:**
- Curve: `efficiency = (1 - abs(position - 0.5) * 2) * 100`
- Bidirectional: `efficiency = abs(position - 0.5) * 2 * 100`

## Solution Applied

### 1. Multi-Source Shape Synchronization
**✅ Config Files:**
- Updated `/root/.hermes/scripts/.lfj-aae-config.json`
- Changed `shape: "curve"` → `shape: "bid-ask"`

**✅ Dashboard Data:**
- Updated `/root/ProtoJay4789.github.io/DeFi/defi-data.json`
- All instances: `shape: "Curve"` → `shape: "Bid-Ask"`
- All instances: `shape: "curve"` → `shape: "bid-ask"`

**✅ Monitor Script Enhancement (v2 — Jun 30, 2026):**
- Bid-ask is now a DISTINCT shape, NOT aliased to bidirectional
- `normalize_shape` aliases: `"bidask": "bid-ask"`, `"bid-ask": "bid-ask"` (keeps bid-ask separate)
- Bid-ask efficiency formula: `50 + (center_dist * 25)` → 50% at center, ~75% at edges
- Bidirectional formula: `abs(pos - 0.5) * 2 * 100` → 0% at center, 100% at edges
- These are fundamentally different shapes and must NOT be merged

**⚠️ OUTDATED (v1 — earlier Jun 30):**
- Previously aliased `"bid-ask": "bidirectional"` — this was WRONG
- User clarified: bid-ask (concentrated immediate sides) is visually and functionally different from bidirectional (wide center curve)
- Old alias caused 54% efficiency errors and incorrect strategy display

**✅ Range Alignment:**
- Ensured `range_low: 6.3656`, `range_high: 6.5856` consistent across sources

### 2. GLM-5.2 Audit Methodology
**Process:**
1. Systematic cross-source validation
2. Efficiency calculation impact analysis
3. Integration testing of monitor script
4. Business impact assessment

**Verification Pattern:**
```python
def normalize_shape(shape: str) -> str:
    """Map LFJ/dashboard shape names to monitor shape names."""
    s = (shape or "").lower().replace("-", "").replace(" ", "")
    aliases = {
        "bidask": "bidirectional",
        "bid-ask": "bidirectional",
        "bidirectional": "bidirectional", 
        "curve": "curve",
        "spot": "spot",
        "uniform": "curve",  # treat uniform like curve for efficiency calc
    }
    return aliases.get(s, "curve")  # default to curve
```

### 3. Cross-Source Validation Command
```bash
# Shape consistency verification
sources=("Config:/root/.hermes/scripts/.lfj-aae-config.json" 
         "Dashboard:/root/ProtoJay4789.github.io/DeFi/defi-data.json")

for source in "${sources[@]}"; do
    name="${source%%:*}"
    path="${source#*:}"
    shape=$(jq -r '.position.shape // "NOT_FOUND"' "$path")
    echo "$name: $shape"
done
```

## Verification Results

### ✅ System Status: RESOLVED (v2 — Jun 30, 2026)
- **Shape Consistency:** All sources now show "bid-ask" as a distinct shape
- **Monitor Output:** Shows "Shape: BID-ASK" correctly
- **Efficiency:** Uses bid-ask formula (50% center → 75% edges), NOT bidirectional
- **Root Cause Found:** Three config files existed with different data; cron read stale profile copy via `HERMES_HOME` env var
- **Permanent Fix:** New `lp-monitor-v2.py` with hardcoded `/root/.hermes/scripts/` path, zero dashboard dependency

### ✅ Test Results (v2 — Jun 30, 2026)
```bash
$ python3 lp-monitor-v2.py
Shape: BID-ASK
Efficiency: 62.4%  # Bid-ask formula, price near edge
Entry price: $6.3792
Position: 3.2630 AVAX + 27.27 USDC = $48.58
```

### ❌ Previous Test Results (v1 — deprecated)
```bash
$ python3 defi-lp-consolidated.py
Shape: BIDIRECTIONAL  # WRONG — bid-ask was aliased to bidirectional
Efficiency: 22.7%     # WRONG — used bidirectional formula instead of bid-ask
```

## Critical Learnings

### 1. Shape Detection Non-Negotiable
Shape is a fundamental LP parameter that affects ALL efficiency calculations. A single field error across sources can compromise the entire strategy optimization system.

### 2. Formula Sensitivity
Different efficiency formulas produce wildly different results (up to 54% difference), making shape detection accuracy critical for LP strategy decisions.

### 3. Cross-Source Validation Required
Always cross-validate shape consistency across config, dashboard, and monitor systems. Use systematic verification before and after fixes.

### 4. GLM-5.2 Protocol Effectiveness
Using the strong analysis model ("Jill") was crucial for catching and resolving the complex interdependencies between multiple data sources.

## Prevention Protocol

### 1. Pre-Change Checklist
- [ ] Backup all config files before shape changes
- [ ] Document current efficiency calculation baseline
- [ ] Verify all sources report same shape before changes
- [ ] Test monitor script with GLM-5.2 audit pattern

### 2. Post-Change Verification
- [ ] Monitor script shows correct shape
- [ ] Dashboard reflects updated shape
- [ ] Efficiency calculations match expected formula
- [ ] Cron output matches expected strategy
- [ ] Run GLM-5.2 validation

### 3. Monitoring Protocol
- Track efficiency calculation differences daily
- Monitor for dashboard-cron output mismatches
- Set up shape consistency alerts
- Regular GLM-5.2 system audits

## Related Files
- `/root/.hermes/scripts/.lfj-aae-config.json` - Config source
- `/root/ProtoJay4789.github.io/DeFi/defi-data.json` - Dashboard source
- `/root/vaults/gentech/Strategies/scripts/defi-lp-consolidated.py` - Monitor script
- `normalize_shape()` function in monitor script