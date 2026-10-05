---
name: lp-venue-fee-mechanisms
description: Use when compounding or measuring LP fees per venue.
version: 1.0.0
tags: [defi, lp, fees, compounding, harvest, liquidity-book, concentrated-liquidity, algebra, lfj]
---

# LP Venue Fee & Compounding Mechanisms

**Compounding is not one feature — it is a property of the venue.** Before building, scheduling, or
debugging anything that claims or compounds fees, establish which mechanism the venue actually has.
Treating them as interchangeable produces an engine that asserts one venue's answer on another
venue's path.

## The two mechanisms

| | Liquidity Book (LFJ / Trader Joe, Meteora DLMM) | Concentrated Liquidity (Algebra V3 / Blackhole, Uniswap V3) |
|---|---|---|
| Fee accrual | folded into **bin reserves at swap time**, protocol-internally | **outside** the position, against `feeGrowthInside0LastX128` / `feeGrowthInside1LastX128` |
| Claim step | **NONE** | **YES** — an explicit `collect()` |
| Emissions | none (no gauge, no emissions token) | gauge-staked NFT → reward token, harvested via the farming center |
| Compounding path | nothing to do — the venue already does it | collect → claim → approve → **swap rewards into pool tokens** → increase liquidity |
| Gas to "claim a fee" | **0, because no claim EXISTS** | real, multi-transaction; measure it, do not assume |
| Strategy lever | **bin shapes** (curve / bid-ask / spot) | **range width + re-center timing** — no shape families |

## What the ledger must record: our income, not the pool's

A Liquidity Book ledger that records the position (`bins`, `our_token0`, `our_token1`, `value_usd`,
`price`, `fee_factor`, `rebuild`) but never OUR accrued income is **geometry without earnings**. It
can tell you the book is deployed and in range while giving no number for what that deployment
produced. That makes every shape choice unfalsifiable: you know the efficiency score, but not whether
the shape earned more than the one it replaced.

**The rule:** every LP ledger must publish a measured income figure — **our share, in dollars, over a
stated window** — and it must be **keyed to the shape in force**.

**Three implementation requirements:**

1. **Store the measured income per window, keyed to the shape.** A curve window and a bid-ask window
   are not the same measurement; averaging them manufactures a number that belongs to neither.
2. **Mark the window after a rebuild as `baseline_reset`, and do not compute an income delta across
   it.** `fee_factor` is cumulative fees **per unit of liquidity**, and a rebuild changes the
   liquidity. A naive delta across a rebuild does not measure earnings — it measures the rebuild.
3. **Never interpolate across a shape change.** If a window contains a rebuild or a shape switch,
   write `null` with the reason, exactly as the ledger already refuses elsewhere.

**The acceptance test:** a ledger whose every snapshot carries `fees_usd: null` is an unmeasured
position, regardless of how precise the geometry looks. A position whose income cannot be stated is
an experiment, and it must be labelled one.

## Rules

1. **A revert is a valid answer, not always a failure.** If `pendingFees` / `collectFees` reverts on
a Liquidity Book pair, that is the venue telling you the function does not exist. Confirm by calling
a selector you KNOW works on the **same pair at the same block** (`getBin(uint24)` returning 64
bytes, `totalSupply` returning 32 bytes). A revert **plus a working sibling call** is evidence; a
revert alone is not — it could equally be a wrong selector or a bad ABI. When you cannot prove the
call is correct, report **UNKNOWN**, never 0.

2. **Never hold emissions as yield** — sell them back into pool tokens immediately. And never CLAIM
emissions you cannot SELL: if the sell route is unusable, claiming strands the reward token and the
claim call then reverts with nothing left to collect. **Simulate the swap route before claiming** and
gate the claim on that simulation.

3. **No venue fact may be a module-level constant in an engine that routes by venue.** "Gas to claim
a fee" is 0 on one venue and real on another. If the venue is not knowable at the point of the
check (e.g. position type is loaded later by a discovery subprocess), the check must SAY SO and
defer to where the venue is known — it must not assert a venue it cannot see.

4. **An unmeasured cost renders UNKNOWN, never 0.** A `0` reads as "measured, and it is zero" — a
claim about the venue you may not have. A claim that cannot be priced cannot be licensed.

5. **Match venues by family prefix, not exact string.** Discovery layers name rails inconsistently
(`lfj` vs `lfj_v22`). A lookup table whose only key is never produced will always answer "unknown" —
safe, but useless. A miss must fall through to UNKNOWN rather than to another venue's answer.

6. **`liquidity == 0` on a position means read nothing else from it.** A position with zero
liquidity and zero tokens-owed is a **drained remnant**: no fees, nothing to harvest or compound. A
wallet can hold several remnants alongside the live position, and an index-based selector will
happily pick one. Read `liquidity` first.

7. **Read the venue's own struct, not a sibling's.** Algebra is a V3 *fork*, not a clone — extra
fields shift the offsets. Reuse the existing adapter's ABI rather than re-deriving the interface;
hand-rolled struct layouts decode garbage instead of erroring.

## When a spec describes compounding

A spec that says "claim fees → swap half → add liquidity back" is describing a **concentrated
liquidity** venue. If your capital is on a Liquidity Book venue, that spec does not describe your
position — there is nothing to claim, and building the flow has nothing to run on. Check which
mechanism the venue has before adopting the design.

## Supporting files

- `references/fee-rate-measurement.md` — how to measure a fee RATE correctly, the instruments that
  do NOT work, and the two routes that cross-check each other.
- `references/fee-ledger-income-recipe.md` — how to record OUR income in an LP fee ledger, keyed to
  the shape in force and segmented around rebuilds.

## Our share vs the pool's receipts

Pool-level fee receipts (from Swap logs or volume × fee tier) are true for the venue but are **not
ours**. A pool printing $4,000/day does not mean our $250 position earns a proportional $4/day,
because trading volume concentrates in whichever bins spot is sitting in, and our liquidity share of
the pool is **not** our share of its activity.

**Do not derive our income by multiplying pool fees by our pool-share percentage** unless you can
prove the activity is uniformly distributed — it almost never is on a concentrated book.

**The honest path:** measure the fees that accrued to OUR bins over a window (using the venue's
`fee_factor` or equivalent, with the rebuild-segmentation rules above), or report UNKNOWN. A derived
number that looks precise is more dangerous than an absent one, because it will be quoted and acted
on.

## An unreadable read is NOT a zero

**The most dangerous output this class of tool produces is a confident number built from a read that
FAILED.** Measured on `lfj_fee_attribution.py`, 2026-10-01, for a **deployed** position:

```
bins held 25   swaps 3825 total, 0 touched OUR bins
⚠️  100.0% of the window EARNED NOTHING     OUR FEES: $0.000000
```

Three separate silent zeros:

1. **A `set()` fallback on a failed read.** `_our_bins_at()` caught every exception and returned an
   EMPTY SET, which downstream read as "capital out of the pool". The RPC served only **~125 blocks
   (~2.3 min) of archive state** while the docstring asserted the opposite. **Rule: a read that fails
   must return a DISTINCT value (None / raise), never the same value as a read that succeeds and finds
   nothing. "Could not read" and "read it, it is zero" are different measurements.**
2. **A best-block read treated as current.** `_our_bins_at(head)` returned 0 bins while `head-50`
   returned 25 — an uncommitted tip read as an empty position. **Pin the analysis a few blocks behind
   the tip.**
3. **A probe with a hard-coded scope.** `_our_bins()` scans `active ± 300`. Widen the probe before
   believing either route when two disagree — a scope-bounded probe that misses the position reports
   ZERO, not an error.

**MEASURE the node's archive depth; never assume it** (`_archive_floor()` doubles then bisects). If
coverage is partial, **REFUSE the daily rate and name the coverage** — a refusal beats a second wrong
number. **Report `unreadable` hours as a THIRD quantity beside deployed and idle; a two-way
deployed/idle split silently converts "we could not look" into "it earned nothing."**

**Before quoting any LP rate, check the position is IN RANGE.** An out-of-range position accrues zero,
so an estimator conditional on in-range capital can be right about the VENUE and wrong about the
POSITION. Measured: spot $10.9314 above a range ceiling of $10.9096 — 15 bins, OUT, earning nothing,
while the estimator's headline read $0.1754/day and 47–100.5%. **In-range status is readable when the
rate is not — prefer gating on the condition you can measure.**

## A DERIVED BOUNDARY CANNOT BE VALIDATED BY THE VALUE MEASURED AGAINST IT

**If an instrument computes a position's bounds FROM THE DATA IT MANAGED TO READ, and then tests the
market price against those bounds, an incomplete read does not merely under-report the position — it
SHRINKS THE BOUNDS and flips the verdict.** Measured on one wallet inside fifteen minutes:

```
45 bins enumerated  ->  range ceiling 11.2641   ->  spot 10.93 is IN
15 bins enumerated  ->  range ceiling 10.9096   ->  spot 10.93 is OUT
 0 bins enumerated  ->  "no position"           ->  reported as ABSENT
```

**Both ranges share the FLOOR and differ only at the ceiling, by `11.2641/10.9096 = 1.032494` =
3.249%. At binStep 10 that is **32 bins** — `1.001^32 = 1.032494`, EXACT. (`1.001^30 = 1.030439` =
3.044% is a NEAR-match: same direction, same ~3% scale, and it was published in this file as an
IDENTITY with the ratio. A near-match stated as an identity is the defect this whole section is
about, and it sat inside the proof for a day. Solve for the span, do not recall it:**
`log(1.032494)/log(1.001) = 31.99`.**) So the ceiling was not read; it was
`min_bin`, `max_bin` of whatever the enumeration returned. **The instrument's output feeds its own input,
and the resulting verdict cannot be checked against the instrument that produced it.**

**Rules that follow:**
- **A position's bounds must come from the position — its mint/rebalance parameters, or a COMPLETE bin
  set — never from a probe that may return a subset.** If the enumeration can be partial, the bounds are
  a guess with the appearance of a measurement.
- **An incomplete enumeration must REFUSE, not define the bounds it will then be judged against.**
- **A reader with more than one discovery path must NAME WHICH PATH ANSWERED in its output.** Three paths
  behind one output format produce 45, 15 and 0 for the same wallet, and nothing in the output says why.
  **"Two routes agree" is the acceptance standard — and it is meaningless unless each route is named.**
- **A FALSE ABSENCE is worse than a wrong number**: "no position" reads downstream as withdrawn or
  exited. A reader that can report an existing position as absent must never carry a gate.

## Pool-level receipts are not our income

A ledger that records only geometry is a ledger that cannot falsify a shape decision. It can show
the book is deployed, in range, and structurally healthy while giving no number for what that
deployment earned. When the user asks "how much income are we actually making?", the answer must be
a measured figure for **our share**, not the pool's total receipts.

**Three rules for recording it:**
1. **Key the income to the shape in force.** A curve window and a bid-ask window are different
   measurements; averaging them across a shape change manufactures a number that belongs to neither.
2. **Reset the baseline after a rebuild.** `fee_factor` is cumulative fees **per unit of liquidity**,
   and a rebuild changes the liquidity. A naive delta across a rebuild measures the rebuild, not the
   earnings.
3. **Never interpolate across a shape change.** If a window contains a rebuild or a shape switch,
   write `null` with the reason; a derived number across the boundary is worse than no number.

**Acceptance test:** a ledger whose every snapshot carries `fees_usd: null` is an unmeasured
position. A position whose income cannot be stated is an experiment and must be labelled one.
