---
name: pool-analytics
description: "Use when measuring a pool's fees, volume, TVL, or LP flows."
version: 1.2.0
author: GenTech Treasury
tags: [defi, analytics, fees, tvl, avalanche, re-entry, cl, competitor-analysis, emissions, runway]
trigger: "Measuring a liquidity pool's real economics from chain truth: fee APR, swap volume, TVL trend, whether LPs are leaving, what exits do to rewards. Runs with or without an active position — competitor analysis after an exit, re-entry evaluation, pre-entry pool vetting, venue health."
---

# Pool Analytics from Chain Truth

Measuring a pool's fee yield, volume, TVL, and LP flows — for competitor analysis
after an exit ("who else pulled out and what does it do to rewards"), re-entry
evaluation, pre-entry vetting, or venue health. Concrete selectors, topics, and
code patterns: `references/algebra-chain-reads.md`.

## Always-on rules

- **State farming rules as observations with re-check triggers, not as
  immutable principles.** A principle ("never farm token X") forbids a good
  trade the moment depth and turnover arrive; an observation ("no pool for
  token X is worth entering at TVL Y and fee APR Z") carries the conditions
  that would change it. Record the threshold explicitly: target TVL, target
  volume, or the venue that would make it work. Re-run the measurement when any
  of those thresholds flip.
- **Size-to-depth is the entry gate before impermanent loss.** A token can have
  a thesis, momentum, and real fee tiers and still be unfarmable because the
  position is a rounding error in the pool. Always compute:

      capital_needed_for_goal = (goal_USD_per_day × 365) ÷ (fee_apr_pct ÷ 100)
      expected_share_of_pool = capital_deployed ÷ TVL
      expected_fees_per_day  = fees_per_day × expected_share_of_pool

  If expected fees per day are smaller than one transaction's gas cost across a
  realistic hold period, the pool is too thin regardless of the fee APR or the
  thesis. Report that number; do not hide it behind impermanent-loss warnings.
- **Never report a number derived from one method.** Derive it, then cross-check
  with a second independent source (swap events vs fee-growth math; DefiLlama vs
  raw reserves). A plausible-looking number is not evidence.
- **A zero is a claim, not a default.** Before trusting any zero (0 swaps, $0
  fees, 0 logs), run the same query against a range or contract known to have
  data. If the control also reads empty, the QUERY is broken — fix the query,
  never report the zero. Aggregator zeros are the same trap from the other side:
  a third-party field showing 0 (e.g. an exchange's apyBase) while chain
  measurement shows real fees is a DATA GAP in the aggregator — fill it from
  chain truth and label it as such, never adopt the aggregator's zero.
- **Identify the pool family FIRST, then pick the price method.** Algebra/tick
  (CL) pools: read `globalState().price` (sqrtPriceX96) — a concentrated pool
  holds only what its ranges dictate, so reserves reflect position composition,
  not price (a reserve-ratio "price" understated AVAX ~4.5x, inflated TVL ~3x,
  and fired a bogus collapse alert). Solidly/volatile (constant-product) pools:
  reserves ARE the correct input — applying sqrtPriceX96 to them reads garbage.
  Resolve which family the pool is (factory/pool type, or the router route's
  concentrated flag) before any price or TVL math.
- **Bounds-check every derived price and APR in code, not in your head.** Resolve
  `token0()`/`token1()` before any reserve-based math (a backwards token order
  printed a $24k token price and an 11-digit APR), and have the script REFUSE an
  implausible result (a farm reward token priced at thousands of dollars, an APR
  above a few thousand %) instead of reporting or alerting on it — a code-level
  guard turns a silent nonsense number into a loud refusal.
- **TVL is the honest gauge of LP flows.** Active liquidity swings with price
  (in/out of range), and a single-sided reserve decline is mostly a price-driven
  composition shift (AVAX falls → pool shifts toward WAVAX), not withdrawals.
  Where the two effects can't be separated without per-LP analysis, say so
  instead of presenting reserve deltas as "LPs leaving".

## Procedure

1. **Venue level (DefiLlama).** `api.llama.fi/protocol/<slug>` →
   `chainTvls.<Chain>.tvl[]` for the now / 7d / 30d TVL trend;
   `api.llama.fi/summary/fees/<slug>?dataType=dailyFees` → `total24h`,
   `total7d`, `change_1d`. Confirm the returned `name` matches the intended
   protocol — a wrong slug silently returns another project's numbers.
2. **Pool size and reserves (eth_call).** `balanceOf(pool)` per token → TVL =
   Σ reserve × price. Read at `latest` AND at head−43200 / −302400 / −1296000
   (24h / 7d / 30d on a 2s chain). Archive check: read one selector at 3+ of
   these blocks — identical values mean the node is serving latest state for
   historical calls, i.e. false history.
3. **Confirm the contract you are measuring is the actual pool, not a wrapper.**
   A `balanceOf` call against a Yield Yak vault, gauge, or other wrapper returns
   LP tokens or reward tokens, not the underlying reserves. Verify the address
   maps to a pool before using its balance as evidence of depth. If the response
   contradicts prior knowledge, re-check the address type before reporting it.
4. **Volume and fee revenue (paginated swap events).** `eth_getLogs` on the
   pool with the Swap topic, paginated in ~2000-block windows. Decode amount0 /
   amount1 as SIGNED int256; per swap take (|amount0|·price + |amount1|)/2 as
   the volume leg. Fee revenue = volume × fee tier; fee APR = fees/day × 365 ÷
   TVL.
5. **Fee-growth cross-check (integer math only).**
   `fees = liquidity × (growthNow − growthBefore) / 2^128` using Algebra
   `totalFeeGrowth0/1Token` (0x6378ae44 / 0xecdecf42) and `liquidity`
   (0x1a686502). If this prints ~0 while swaps demonstrably crossed, the
   formula/ABI is wrong — report the swap-event number, never the zero.
6. **LP-flow trend.** Compare TVL across the historical offsets; treat active-
   liquidity swings as range effects, not exits (see rule above).

## Decision frame — what LP exits do to rewards

Fees are paid to whoever is IN RANGE when swaps cross — not split across every
LP ever deposited. Fewer LPs competing for the same fee flow RAISES the APR for
those who stay. Judge the pool by the pair:

| Signal | Meaning | Action |
|---|---|---|
| TVL down + volume up | share consolidation, not a death spiral | re-entry tailwind for a concentrated position |
| TVL down + volume down | volume death spiral | stay out |
| TVL up + volume flat | crowding dilutes APR | demand higher conviction before entering |

### Yield durability — split every yield quote into fee core + emissions

A farm's headline APR blends two income streams with different durability.
Measure them separately and report the SPLIT — "fee 119% + emissions 120%", not
a blended 239%: fee APR = volume x fee tier x 365 / TVL; emissions APR =
reward/day x chain-verified reward price x 365 / TVL. Emissions are conditional
income (the rate gets cut, the funding source runs dry) while the fee core needs
only volume — size any re-entry on the fee core alone and treat the emissions
half as a bonus that can go to zero. When emissions are a large share of total
yield (≳40%), tracking the emission runway (treasury-report-truth →
references/staking-and-emissions-verification.md, Part 4) becomes part of owning
the position.

Concentration caveat: pool-average fee APR UNDERSTATES what a narrow-range
position earns (a concentrated position takes a multiple of the average share)
and OVERSTATES a wide one. Compare realized position yield against pool-average
APR to quantify the concentration multiple before re-entering.

### Staking for emissions is an exit-design decision, not free upside

The user's standing rule: fees are the point ("I mainly cared about where I was
earning the most fees"). Staking a position into the gauge/farm buys the
emissions half at the price of extra exit steps (harvest → reward-token approve
→ sell → unstake), and every one of those steps is a way to strand capital at
exactly the moment you want OUT — the emissions leg is where exits historically
break. Gas does not decide this: price the full multi-tx path first (an
11-transaction exit+recovery cost ~$0.001 on Avalanche — gas is noise); the real
cost of staking is failure surface. Stake only when the emissions half is real
AND durable (funding source topped up, runway comfortable); otherwise enter
UNSTAKED for the fee core and treat staking as a deliberate upgrade — never the
default you must unwind under pressure.

Same-fee-tier venue comparison: when two pools share a fee tier, the fee-APR
ratio equals the turnover ratio (vol/TVL) — compare turnover directly. State
the comparison basis: venue-canonical pool numbers (aggregator) and the exact
pool held (chain) differ when a venue's flagship pool is not the one we farm.

Run this analysis on any pool right after exiting it — post-exit competitor
analysis is a standing step of every exit (see lp-exit-liquidity), not an
ad-hoc question. Run it BEFORE entering a new pool too; entry and re-entry
decisions deserve the same numbers.

When a user asks whether a token currently held for accumulation can also be
farmed, run the classification in `references/coq-lp-case.md`: pool depth,
fee core, size-to-depth, and whether the LP fights the accumulation thesis.
Never substitute the coin's momentum or fee tier for these measurements.

## Cross-rail venue comparison — the Yield Farm Report

When comparing venues across chains (AVAX vs SOL vs TAO vs LINK rails), rank by
**capital-to-goal on the FEE CORE**, not by headline APY:

    capital_needed = (goal_USD_per_day × 365) ÷ (fee_apr_pct ÷ 100)

This is the number that answers the actual question ("what does it take to make
$5/day?") and it does not evaporate when a farm's emissions end. Always show the
fee/emissions split beside it. When two pools share a fee tier, the fee-APR
ratio equals the turnover ratio (vol/TVL) — compare turnover directly.

Aggregator caveat: an `apyBase` of 0 with `apyReward` above 0 is usually a
REPORTING GAP (DefiLlama reports apyBase=0 for Blackhole CLMM while chain
measurement shows ~120% real fees), never a true zero-fee pool. Flag it and fill
it from chain truth.

### Price level moves the EMISSIONS APR, not the fee core

Measured on 196 days of Avalanche history (Blackhole WAVAX/USDC):
`corr(token price, pool TVL) = +0.826` and `corr(token price, emissions APR) =
−0.430`. Mechanism: the emission rate is FIXED per second, so when price falls
the token half of TVL shrinks and the SAME emission lands on less capital — the
reward APR rises. A fixed $/day goal therefore needs LESS capital at a lower
price.

Two hard limits on that relationship:
- It applies to the **emissions layer only**. Fees track VOLUME, not price level,
  so fee-core sizing is roughly price-independent — always size on the fee core.
- A correlation over one history is a **measured relationship, not a law**. Present
  it as a reason to weigh the emissions layer when price is low, never as promised
  income.

What a cheaper entry actually buys (and what it does NOT): it buys MORE TOKENS
per dollar and less top-of-range risk (fewer forced re-centers) — it does NOT
raise the fee APR, because APR is earned on deployed capital. State this every
time a dip ladder is shown, so the ladder cannot be misread as a yield boost.
