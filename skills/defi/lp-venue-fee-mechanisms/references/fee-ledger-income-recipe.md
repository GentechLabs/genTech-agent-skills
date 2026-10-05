# Recipe — Record OUR income in an LP fee ledger

Use this when building or fixing a fee ledger for a Liquidity Book position (LFJ / Meteora DLMM).

## What the ledger already has

A typical snapshot carries:
```json
{
  "t": 1791050482,
  "value_usd": 249.10,
  "price": 11.1187,
  "fee_factor": 36.912,
  "our_wavax": 9.487,
  "our_usdc": 143.614,
  "bins": 25,
  "rebuild": false
}
```

`fee_factor` is the pool's cumulative fees **per unit of liquidity**. It is the right source, but it
cannot be naively differenced.

## What to add

Add `fees_usd` and `window_income_usd` to every snapshot, with these semantics:

- `fees_usd`: cumulative fees earned by **our** position since the last `baseline_reset`.
- `window_income_usd`: income earned during **this specific window** (the delta since the previous
  snapshot, or `null` if a baseline reset happened between them).
- `shape`: the shape in force for this window (`curve`, `bid-ask`, `spot`).

## The algorithm

For each snapshot, in time order:

1. If `rebuild == true` or `shape` changed since the previous snapshot:
   - Set `baseline_reset = true`.
   - Set `fees_usd = 0.0`.
   - Set `window_income_usd = null` with reason `rebuild` or `shape_change`.
   - Record the current `fee_factor` as the new baseline for this shape.
2. Else:
   - Compute `delta_factor = fee_factor - previous_fee_factor`.
   - Compute `window_income_usd = delta_factor * our_liquidity_units`.
   - Add it to `fees_usd`.

**Why `our_liquidity_units` is not `value_usd`:** `fee_factor` is per unit of liquidity, not per
dollar. Convert position value to liquidity units using the pool's price and the bin formula, or use
the venue's own liquidity accounting if exposed.

## What to never do

- **Do not compute a delta across a rebuild.** The liquidity changes, so the factor is not
  comparable.
- **Do not average income across shapes.** A curve window and a bid-ask window grade different
  decisions.
- **Do not derive our income from pool-level receipts.** Pool fees × our pool share is wrong unless
  activity is uniformly distributed, which it is not on a concentrated book.

## Verification

After implementing:
1. Run on a known window with no rebuilds. The cumulative `fees_usd` should match an independent
   estimate from Swap events in our bins within a small tolerance.
2. Inject a synthetic rebuild between two snapshots. The second snapshot must show
   `baseline_reset = true` and `window_income_usd = null`.
3. Inject a synthetic shape change. Same result as a rebuild.
