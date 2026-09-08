---
name: lp-shape-detector
description: "GenTech Original — Detect LP strategy shapes (Curve/Bid-Ask/Spot) by analyzing on-chain bin distribution. Works with any bin-based AMM: LFJ V2.1 (Avalanche) and Meteora DLMM (Solana)."
tags: [lp, shape, detector, defi, lfj, meteora, avalanche, solana, genTech-original]
trigger: "When analyzing LP positions, detecting strategy shapes, or comparing LP strategies across pools."
related_skills:
  - defi-lp-consolidated  # uses shape for efficiency calc
  - dca-rebalance-handler  # shape affects DCA strategy
version: 1.1.0
author: Gentech Labs
---

# LP Shape Detector — GenTech Original

**Detect LP strategy shapes by analyzing on-chain bin distribution.**

Works with any bin-based concentrated liquidity AMM:
- **LFJ V2.1** (Trader Joe) on Avalanche — reads `curveData.bins` from `defi-data.json`
- **Meteora DLMM** on Solana — same Spot/Curve/Bid-Ask shapes, discrete price bins
- Chain-agnostic — any AMM with discrete bin distribution

## Supported Shapes

| Shape | Pattern | Best For |
|-------|---------|----------|
| **Curve** | Bell-curve, peak at center | Range-bound markets |
| **Bid-Ask** | Liquidity at edges | Volatile/trending markets |
| **Spot** | Single bin concentration | Precision plays |
| **Asymmetric** | Skewed distribution | Directional bets |

## Platform Compatibility

| Platform | Chain | AMM Type | Shape Support | Data Source |
|----------|-------|----------|---------------|-------------|
| **LFJ V2.1** (Trader Joe) | Avalanche | Liquidity Book (bins) | Spot, Curve, Bid-Ask | `defi-data.json` → `curveData.bins` |
| **Meteora DLMM** | Solana | DLMM (bins) | Spot, Curve, Bid-Ask | On-chain bin query via RPC |

**Key insight (Jul 16, 2026):** Meteora DLMM uses the identical Spot/Curve/Bid-Ask liquidity shape system as Trader Joe's Liquidity Book. Both organize liquidity into discrete price bins with configurable distribution. The LP Shape Detector's classification algorithm (center concentration, edge concentration, peak position, symmetry, skew) works unchanged on Meteora bin data.

**Meteora discovery context:** Jordan was comparing TAO/USDC yield farming opportunities on Solana. Meteora's DLMM surfaced as the equivalent to Trader Joe — same shape system, same strategy playbook. All existing shape analysis tools (LP Shape Detector, efficiency calculator, regime classifier) apply to Meteora positions without modification.

## Usage

```bash
python3 /root/.hermes/profiles/gentech/scripts/lp-shape-detector.py
python3 /root/.hermes/profiles/gentech/scripts/lp-shape-detector.py --json
```

## Detection Algorithm

1. **Read bin data** from `curveData.bins` in defi-data.json
2. **Calculate metrics:**
   - Center concentration: liquidity in middle 30% of range
   - Edge concentration: liquidity in outer 25%
   - Peak position: where max liquidity sits
   - Symmetry: left vs right balance
   - Skew: directional bias
3. **Score each shape** based on metrics
4. **Classify** with confidence percentage

## Example Output

```
📈 LP Shape Analysis

Detected Shape: Curve (center-weighted)
Confidence: 90%

Distribution Metrics:
  Bins: 37
  Center concentration: 55.2%
  Edge concentration: 25.0%
  Peak position: 0.556 (near center)
  Symmetry: 0.891

Strategy Implications:
  • Earns most when price stays near center
  • Best for range-bound markets
  • Consider switching to Bid-Ask if breakout expected
```

## Integration with Monitor

The shape detector can be called before efficiency calculations:

```python
import subprocess
result = subprocess.run(
    ["python3", "/root/.hermes/profiles/gentech/scripts/lp-shape-detector.py", "--json"],
    capture_output=True, text=True
)
# Parse JSON output for shape classification
```

## Cloudflare Worker Deployment (Jul 2, 2026)

The shape detection algorithm was ported from Python to JavaScript and deployed as an x402-monetized Cloudflare Worker:

- **URL**: https://gentech-lp-analytics.jordanjones0902.workers.dev
- **Source**: `lp-analytics/worker.js` in vault
- **Porting Notes**:
  - No external dependencies (pure JS, no numpy/pandas needed)
  - Returns 402 payment response for unpaid requests (x402 protocol)
  - Supports POST with JSON body (`{ bins: number[], volatility?: number }`)
  - Classification order adjusted: CenterConcentration checked before EdgeConcentration (ensures proper bell curves classify as Curve, not Bid-Ask)
- **Three paid endpoints**: `/api/lp/shape` ($0.025), `/api/lp/efficiency` ($0.01), `/api/lp/strategies` ($0.005)
  - `/api/lp/shape` — POST. Classifies shape from bin distribution, returns shape name + confidence + metrics
  - `/api/lp/efficiency` — POST. Takes bins + volatility (0-1, default 0.5). Returns shape-fit efficiency score (0-100) + marketFit label (High/Medium/Low)
  - `/api/lp/strategies` — GET. Returns strategy catalog (Curve, Bid-Ask, Spot, Asymmetric) with descriptions and best-fit regimes
- **Free endpoints**: `/health`, `/pricing`

### JS Thresholds (identical to Python)

```javascript
Spot:       maxBinShare > 0.6
Curve:      centerConcentration > 0.4    // checked BEFORE edge
Bid-Ask:    edgeConcentration > 0.35
Asymmetric: |skew| > 0.3
```

## For Agent Kit

This is a GenTech Labs original. When deploying agents that manage LP positions:

1. **Always detect shape first** — don't assume Bid-Ask or Curve
2. **Match shape to market** — Curve for stable, Bid-Ask for volatile
3. **Monitor shape drift** — position shape may change if bins are added/removed
4. **Use confidence score** — low confidence = need more bins or manual check

## Future: Regime-Based Shape Switching (Jun 2026)

Jordan's vision: don't stay in one shape forever. Detect the market regime and switch shape accordingly:

| Regime | Signal | Optimal Shape |
|--------|--------|---------------|
| **Volatility** | High ATR, price bouncing between bins | Bid-Ask |
| **Consolidation** | Low ATR, tight range, low volume | Curve |
| **Accumulation** | Price building a base, buyers stepping in | Spot |
| **Payout** | Price pushing into resistance, selling pressure | Widen Up |

The regime classifier would read price action history + volume + edge proximity and recommend the optimal shape. User approves before switching.

The detector already provides the shape classification — the next step is feeding that into a regime engine that triggers shape changes.

The detector is chain-agnostic — works with any LFJ V2.1 pool (Avalanche) or Meteora DLMM pool (Solana) using identical classification logic.
