# Measuring an LP Fee Rate

Getting a defensible fee RATE is harder than it looks. Most obvious instruments are invalid on a
rebalancing position. Use these, in this order.

## Instruments that DO work (use two, publish the bracket)

1. **Static fee parameters from the pool** — `getStaticFeeParameters()` → effective fee ≈
   `baseFactor x binStep x 1e-10`. This is the venue's own configuration; it is the floor of what
   you can claim about the rate.
2. **Real `Swap` events** — compute the effective rate per leg from the actual amounts, then take
   the **median** across the window.

Then combine with externally-sourced volume and TVL to get our share:
`daily_fees ≈ volume_24h x fee_rate x (our_lp_usd / pool_tvl)`.

**When the two routes disagree, publish the BRACKET with both sources named** — never the
flattering end. A near-CONSTANT ratio between two derivations is itself informative: it means the
shared term (our pool share) is right and the differing assumption is the one to fix.

## Instruments that do NOT work — do not retry these

- **`max()` of per-leg fee rates.** Selecting the priciest swap in a window and presenting it as
  typical structurally flatters a fee-INCOME figure. Use the **median**. (Switching max→median
  moved a published discrepancy from x7.1 to x3.8 — the honest direction.)

- **A price-invariant factor like `sqrt(token0_amount x token1_amount)`** as a proxy for accrued
  value. A re-center changes the factor with **no fee earned**, and an out-of-range window collapses
  one side to 0. Replayed over ~49h it produced segment rates of −124%/day, +818%/day and +448%/day —
  nonsense. It needs rebuild-anchored segmentation and an in-range gate before it can measure
  anything, and until then no rate should be quoted from it.

- **Short-window Δvalue at a fixed price.** Range traversal **dwarfs** the fee — measured at roughly
  **60x**. A bin set that did not visibly move can still show a large "gain" purely from composition
  shift (token0 up, token1 down, total roughly flat). Never quote a rate from Δvalue over a short
  window.

- **A ledger whose windows are swamped by re-centers.** If the position re-centers ~10x/day, most
  naive time windows contain a rebalance and measure the rebalance, not the fees. Find the longest
  **rebuild-free, in-range** window; if that is only 3-10h, say so rather than quoting a number.

- **A rate COMPOUNDED across a series that contains rebuilds.** A snapshot ledger recording position
  value (or a fee factor) each pass does NOT contain the fee series once the position rebuilds: a
  teardown writes the position to ZERO, the redeploy writes it back, and any rate taken across those
  points measures the rebuild, not the yield. Measured: **+1668% APR** off a series whose independent
  milestone estimate was **~$0.18/day** — 20 zero-value snapshots and 26% of all steps larger than
  ±20%, value jumping `144.68 -> 43.50 -> 145.90` inside 20 minutes.
  **Discriminator: a real fee series rises slowly and monotonically; a rebuild series JUMPS.**
  Before quoting a compounded figure, count the zero snapshots and the >±20% steps, and cross-check
  the magnitude against an independent estimate — a disagreement of an order of magnitude means the
  SERIES is the artifact, not the estimate. A teardown mid-cycle reads as a collapse.
  *Fix:* measure fees over **continuously-deployed** windows only (segment on rebuild-anchored
  boundaries), or report UNKNOWN.

- **A metric that REFUSES is worth more than one that reports a second wrong number.** When you
  segment a series and the segments disagree in **SIGN**, the segmentation is wrong and no rate from
  it is meaningful. **LP fees are never negative** — a negative segment is proof the window is
  measuring something other than fees (a rebuild, a composition shift, a price cross), not proof of a
  loss. So the correct output is a hard refusal naming every segment's rate, and the fix is the
  SEGMENTATION, not the number:

  ```
  NO TRUSTWORTHY RATE — the segments disagree in SIGN:
    -115.80%/day, -61.01%/day, -0.45%/day, +0.13%/day, +33.71%/day
  ```

  **Generalise it:** for any quantity with a known SIGN constraint (a fee, a volume, a count, an
  elapsed time), a sign violation is a MEASUREMENT INVALIDATION, not a data point. A metric that
  averages across it hides the invalidation and produces a plausible-looking number — and a
  "plausible" figure here is more dangerous than an absent one, because it will be quoted.

- **A rebuild marker that nothing READS is not a detector.** A marker written into each snapshot so
  downstream logic could exclude rebuild windows is worthless if no consumer loads it — and the
  detector that IS wired up (a bin-count change) is blind whenever the rebuild restores the SAME bin
  count, which is the normal case for a re-center that keeps its geometry. Two independent failures
  that cancel into silence: the marker exists, the fallback detector can't see the event, and the
  series looks continuous. **Grep for a marker's READERS the same way you grep for a key's routes** —
  a field written and never consumed is a comment with a schema.

## Reporting

- Quote the rate with its window and its method, and name both derivations.
- If a figure could only be produced by an instrument listed under "do not work", report
  **UNKNOWN** and say why. An honest gap beats a confident number.
- Do not convert a rate into a headline money figure without saying whether it is a range.
- **Never quote a compounded APR whose series contains rebuild steps.** Count the zero/teardown
  snapshots and say the count alongside the figure, or report UNKNOWN. The DIRECTION can be right
  while the MAGNITUDE is garbage — state which of the two you actually have. "Real progress,
  honestly unmeasured" is the correct report when the series cannot support a number.
