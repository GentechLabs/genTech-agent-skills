# Yield Strategy Comparison Pattern

How to quickly compare DeFi yield opportunities across strategies using live data. Used for the Inference Farming vs AVAX Staking vs AVAX-USDC LP analysis.

## Data Sources (Priority Order)

| Data | Tool | Cost | Notes |
|------|------|------|-------|
| Token price | `blockrun_price` | Free (crypto) | Pyth-backed, real-time |
| Yield pool APY | `blockrun_defi(path="yields")` | $0.005 | Huge dataset, filter locally |
| Protocol TVL | `blockrun_defi(path="protocol/{slug}")` | $0.005 | Per-protocol breakdown |
| DEX pair data | DexScreener (free HTTP) | Free | 10 req/min, no key needed |
| Market research | `web_search` | Free | News, forums, docs |
| Staking APY | `web_search` + protocol docs | Free | Cross-reference 3+ sources |

## Comparison Framework

For each opportunity, gather the same 5 metrics:

1. **Entry cost** — minimum capital to participate
2. **APY** — base yield + any incentive tokens (with sources)
3. **Risk** — IL exposure, lock periods, protocol risk, token price risk
4. **Effort** — passive (set and forget) vs active (monitor + rebalance)
5. **Max upside** — what drives outsized returns

## Side-by-Side Template

```
|                    | Strategy A | Strategy B | Strategy C |
|--------------------|-----------|-----------|-----------|
| Entry cost         | $X        | $Y        | $Z        |
| APY                | X%        | Y%        | Z%        |
| Risk               | Low/Med/High | ...     | ...       |
| Effort             | Passive/Active | ...   | ...       |
| Max upside         | What drives it | ...   | ...       |
```

## ROI Estimation

```python
# Monthly return on $N investment
monthly = amount * (apy / 100) / 12

# With compounding
import math
monthly_compound = amount * (math.pow(1 + apy/100/365, 30) - 1)
```

## Pitfalls

- **APY varies by source** — staking APY from Coinbase (3.44%) may differ from on-chain (6-8%). Cross-reference.
- **LP APY includes token incentives** — base swap fees may be much lower than advertised "total APY"
- **IL kills LP returns** — always estimate impermanent loss before entering an LP pool
- **Entry cost ≠ minimum** — some protocols have minimum stake amounts (e.g. 25 AVAX to self-validate) vs delegation minimums (1 AVAX)
- **Yield is state-dependent** — APY changes with TVL and volume. Capture current numbers, don't assume they're stable
