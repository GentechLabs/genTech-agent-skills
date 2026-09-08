# Current DeFi Strategy (Jul 16, 2026)

## Overview

Jordan's DeFi strategy is a two-track approach: income generation through LP fees + capital appreciation through spot accumulation. This feeds toward an Avalanche L1 deployment targeted for next year.

## Income Track: AVAX-USDC LP

| Target | Vehicle | Platform | Chain |
|--------|---------|----------|-------|
| **$200/day** in LP fees | WAVAX-USDC concentrated liquidity | Trader Joe (LFJ) | Avalanche |

**Rationale for AVAX-USDC focus:**
- Lower AVAX price ($6.75) = cheaper to build position
- Pool has strong volume ($746K daily) and 37% APY
- Jordan already has the tooling (LP Shape Detector, monitor, rebalance sync)
- Known platform — no learning curve
- Easier to scale $200/day target with lower entry prices

**Position sizing estimate for $200/day:**
- Pool daily fees: ~$1,865/day from $746K volume (at 0.25% fee tier)
- Required share of pool: ~$40-50K deployed (varies by fee tier and incentives)
- That's ~3,000-3,700 AVAX at current prices

## Speculation Track: Spot Accumulation

| Asset | Thesis | Strategy |
|-------|--------|----------|
| **TAO** | Dominant decentralized AI coin, $200 floor, strong TAO/BTC chart | Buy spot, yield farm on Solana (Meteora DLMM) |
| **SOL** | Solana ecosystem growth, Meteora LP Army community | Buy spot |
| **LINK** | Oracle infrastructure, real utility | Buy spot |

## Capital Allocation Philosophy

**Dry powder is the name of the game.** Jordan watches from the sidelines, accumulating during the bear market, deploying when conviction is high. The $200/day LP target is the income engine; the spot bags are the upside lever.

## Infrastructure Timeline

| Phase | Timeline | Action |
|-------|----------|--------|
| **Now** | This year | Train models (DeFi, gaming, travel/food), yield farm AVAX-USDC, accumulate spot |
| **Next** | Next year | Deploy Avalanche L1 with sovereign token, x402 payment rails, trained models as anchor tenants |

## Key Insight

The $200/day LP strategy isn't just about income — it's about **building capital to fund the Avalanche L1**. Every dollar earned from LP fees is a dollar that doesn't need to come out of pocket for infrastructure next year.

## References

- `lp-shape-detector` SKILL.md for shape analysis on any bin-based AMM
- `defi-lp-monitoring` SKILL.md for position monitoring and rebalance protocol
- `message-length-discipline` SKILL.md for Telegram output formatting
