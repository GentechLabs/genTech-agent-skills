# Training Data Collection Guide

## File
`/root/vaults/gentech/defi-training-data.json`

## When to Log
1. **After every rebalance** — New sample with full context
2. **After market events** — Selloffs, catalysts, regime changes
3. **When monitor detects patterns** — Unusual fee spikes, efficiency anomalies

## Sample Structure
```json
{
  "timestamp": "ISO 8601",
  "price": 6.425,
  "shape": "bid-ask",
  "range_low": 6.30,
  "range_high": 6.559,
  "position_usd": 64.05,
  "avax_amount": 4.673,
  "usdc_amount": 34.0,
  "avax_pct": 46.9,
  "daily_fees_usd": 0.887,
  "fee_efficiency_pct": null,
  "efficiency_zone": "harvest",
  "volatility_24h": null,
  "volume_24h": null,
  "tvl": null,
  "in_range": true,
  "milestone_tier": "unranked",
  "market_regime": "volatile",
  "notes": "Why this happened and what we learned"
}
```

## Notes Field Guidelines
The `notes` field is the most valuable training signal. Include:
- **Catalyst:** What caused the price move (institutional news, selloff, etc.)
- **Decision:** Why this shape/range was chosen
- **Lesson:** What worked, what didn't, what to do differently

## Example Notes
- "Asian market bloodbath ($800B wiped). Fee spike visible on chart. Bid-ask performing well."
- "Rebalanced UP after TIS/Avalanche Japan catalyst. Institutional news pushed price through range quickly."
