# DeFi Training Data Schema

Used by the GenTech DeFi model training pipeline. Every LP observation gets logged with labeled features for future model training.

## Location

`/root/vaults/gentech/defi-training-data.json`

## Schema

```json
{
  "timestamp": "ISO 8601",
  "price": "AVAX/USDC price at observation",
  "shape": "curve | bid-ask | spot",
  "range_low": "LP range lower bound",
  "range_high": "LP range upper bound",
  "position_usd": "Total LP value in USD",
  "avax_amount": "AVAX in position",
  "usdc_amount": "USDC in position",
  "avax_pct": "Percentage of position in AVAX (0-100)",
  "daily_fees_usd": "Fees earned in last 24h",
  "fee_efficiency_pct": "How efficiently fees are earned vs theoretical max",
  "efficiency_zone": "euphoria | peak | harvest | accumulation | bleeding | panic",
  "volatility_24h": "Price change % in last 24h",
  "volume_24h": "Pool trading volume in last 24h",
  "tvl": "Total pool TVL",
  "in_range": "boolean — is price within LP range",
  "milestone_tier": "current AAE milestone tier",
  "market_regime": "bull | bear | sideways | volatile",
  "notes": "Free-text context"
}
```

## What Gets Logged

- Every Jordan DCA or rebalance (from LFJ screenshots)
- Every cron monitor report (from defi-lp-consolidated.py)
- Every narrative rotation scan (sentiment + zone)

## Training Use Cases

1. **Shape prediction** — given price action + volatility, which shape earns most?
2. **Range optimization** — given market regime, what range width maximizes fees?
3. **Rebalance timing** — given efficiency trend, when should you rebalance?
4. **Mode routing** — given sentiment + rainbow zone, which mode (harvest/accumulate/dry powder)?

## Connection to Routing Layer

The routing layer spec (`Strategies/smart-routing-layer-spec.md`) defines how mode decisions are made. This training data captures the inputs and outcomes so the model can learn which decisions worked.
