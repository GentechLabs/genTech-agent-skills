# Backtesting Shape vs Regime

**When to use this file:** the user asks "which shape should I use?", "should I be market
making?", or "why did my LP lose to HODL?" Run this comparison on a comparable pool before
answering.

---

## 1. Tool and inputs

Use `mcp__vfat__backtest_strategy` (vfat.io v4 strategy-backtest endpoint). It simulates a
deposit in a concentrated-liquidity pool over up to 90 days of the pool's actual swap history,
with auto-rebalance, and compares against HODL.

**Hold constant across runs:**
- Chain, pool address, fee tier
- Deposit size (USD)
- Days / history window
- `autoRebalance: true`
- Rebalance delay (`delayMin`)
- Rewards handling

**Vary only the geometry:** `tickSpacesBelow`, `tickSpacesAbove`.

---

## 2. Worked example: WAVAX/USDC, Avalanche, 30 days ending 2026-09-30

**Pool:** Uniswap V3 `0xfae3f424a0a47706811521e3ee268f00cfb5c45e`, 5bp fee tier, tickSpacing 10  
**Deposit:** $114  
**Window:** 2026-08-31 to 2026-09-30 (553,725 swaps, 720 hours, no gaps)  
**Rebalance delay:** 10 minutes  
**AVAX move:** roughly +54% over the window

| | Curve-like 12/13 | Bid-ask-like 15/30 | Static (no rebalance) | Full-range passive | HODL |
|---|---|---|---|---|---|
| Fees earned | $106.82 | $72.12 | $9.84 | $1.16 | — |
| Costs | −$13.13 | −$7.16 | $0 | $0 | — |
| Divergence | −$88.37 | −$56.19 | +$0.41 | +$27.36 | — |
| **Total PnL** | **+$5.32** | **+$8.78** | **+$10.26** | **+$28.51** | — |
| Ending value | $119.32 | $122.78 | $124.26 | $142.51 | **$146.05** |
| Time in range | 91.0% | 95.5% | 13.6% | 100% | — |
| **Rebalances** | **133** | **70** | **0** | **0** | — |

### Key readings

1. **The tighter the shape, the more it churns.** 133 rebalances vs 70 for a wider shape on the
   same pool. Churn is a property of geometry, not of the trigger.
2. **A never-rebalanced range beat both managed shapes.** 13.6% time in range, $9.84 of fees, but
   no divergence cost.
3. **Divergence is the bill.** The curve-like shape earned $106.82 in fees but lost $88.37 to
   divergence — selling AVAX on the way up and buying it back on the way down.
4. **Everything lost to HODL** in a +54% rally. Concentration is a bet against a trend.

---

## 3. Honest limits

- **Not your exact pool.** Uniswap V3 is tick-based; LFJ is bin-based. The result is
  **indicative**, not exact.
- **No emissions.** This pool paid none in the simulation. Add emissions only if you can verify
  the real reward stream.
- **Past history is not a forecast.** The window is one asset in one regime.
- **A single window is not doctrine.** Before changing strategy, test at least three regimes:
  trend, chop, drawdown.

---

## 4. Reproduction recipe

```python
# Curve-like run
mcp__vfat__backtest_strategy(
    chainId=43114,
    pool="0xfae3f424a0a47706811521e3ee268f00cfb5c45e",
    depositUsd=114,
    days=30,
    strategy={
        "autoRebalance": True,
        "delayMin": 10,
        "tickSpacesBelow": 12,
        "tickSpacesAbove": 13
    }
)

# Bid-ask-like run
mcp__vfat__backtest_strategy(
    chainId=43114,
    pool="0xfae3f424a0a47706811521e3ee268f00cfb5c45e",
    depositUsd=114,
    days=30,
    strategy={
        "autoRebalance": True,
        "delayMin": 10,
        "tickSpacesBelow": 15,
        "tickSpacesAbove": 30
    }
)
```

Compare the `feesUsd`, `divergenceUsd`, `costsUsd`, `totalPnlUsd`, `endingValueUsd`,
`timeInRangePct`, and `rebalances` fields across the results.

---

## 5. Decision rule

| If the backtest window was | And concentration | Then the lesson is |
|---|---|---|---|
| A strong trend | Lost to HODL | Farm the chop, hold the trend |
| Sideways / choppy | Beat HODL | Concentration earns its keep |
| A drawdown | Preserved capital vs HODL | Defensive shape / stable hedge worked |

**Instrument follows regime.** Never choose a shape because it is the default. Choose it because
the backtest for the current regime says it wins.
