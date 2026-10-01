---
title: "Farmable vs. tradeable: a worked LP classification"
---

# When a coin is farmable vs. when it is only tradeable

A token can be *good to own* and *bad to LP*. The distinction is measurable:
**our size relative to the pool**, **the fee core**, and **the owner’s thesis**.
Use this as a worked reference when the user asks *"can we farm X?"* for a
coin that is currently held for accumulation.

## Decision checklist

Before classifying a token as FARM vs TRADE, answer these four questions:

1. **Does a real pool exist with measurable depth?**
   - Chain-check the pool address itself (not a wrapper, not a vault).
   - Confirm TVL > threshold where our deployment is a meaningful share.
   - A pool with rewards ended, APY `-`, and TVL <$1k is "sleeping" — not a farm.

2. **What is the fee core?**
   - Compute from swap events: `fees/day = volume/day × fee_tier`.
   - `fee_apr_pct = fees/day × 365 / TVL × 100`.
   - `capital_for_goal = (goal_USD_per_day × 365) / (fee_apr_pct / 100)`.
   - Do not use aggregator APY or reward-emissions APY for the entry decision.

3. **Is our deployment big enough to matter, but small enough not to be the pool?**
   - `expected_share = capital_deployed / TVL`.
   - `expected_fees_per_day = fees/day × expected_share`.
   - If `expected_fees_per_day` is less than one transaction gas cost across a
     realistic hold, the pool is too thin for our position.

4. **Does the LP help or fight the accumulation thesis?**
   - If the thesis is *accumulate on dips and ride upside*, a two-sided LP
     sells the asset into every green candle and fights the thesis.
   - A **bid-only ladder below spot** is the structure that still collects fees
     on chop while preserving upside exposure.

## Worked example: COQ/WAVAX CL, 1% tier

Observed 2026-09-30:

| metric | value |
|---|---|
| volume/day | ~$1,628 |
| fees/day | ~$16.28 |
| TVL | ~$842 (CL) / ~$88 (LFJ vault) |
| fee APR at pool TVL | ~0.7% |
| capital needed for $5/day at that depth | ~$258,588 |
| our $5 earns | ~$0.000097/day |

Conclusion: the pool exists and the chop is real, but our deployment is too
small to capture it. The transaction cost exceeds many years of expected fees.
**The decisive metric was size-to-depth, not impermanent loss.**

## When the observation changes

Re-run the same measurement when any of these flip:

- TVL clears ~$50k at similar volume (fee APR rises to ~30% pool-average).
- The LFJ vault or another gauge shows live rewards again.
- A deeper venue lists the pair with higher turnover.

Then evaluate again against the same checklist.
