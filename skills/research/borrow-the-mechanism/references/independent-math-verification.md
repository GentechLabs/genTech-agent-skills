# Independent math verification for borrowed code

When a borrowed repo computes numbers (finance, risk, rates, percentages, APR, runway, PnL,
fees), passing its own test suite is not enough. Its tests prove the author believed their
own code. A separate probe proves the code actually conserves the invariants the docstrings
promise.

## The workflow

1. **Read the implementation and the tests until you can write the formula from memory.**
   If you cannot state the expected formula in plain language, you are not ready to verify.
2. **Write your own formula independently**, using only the docstrings and any explicit
   units — not the source code. This is the "red team" formula.
3. **Write a sweep probe** in the repo's language (or via shell if it exposes a CLI) that:
   - exercises the public API across a broad random parameter cloud,
   - includes adversarial edge cases (near-zero values, 10× and 1/10,000× marks, max leverage),
   - compares the returned value to your independent formula,
   - checks conservation invariants (`maxLoss == margin`, `value >= 0`, `fee <= notional`).
4. **Report case count and mismatch count.** Zero mismatches means the math is correct on the
   sampled domain. Any mismatch is a stop — debug the units first, then the sign.
5. **Check units across sibling modules.** Two functions called `apr` in the same org can return
   a fraction (0.876) in one module and a percent (87.6) in another. A green test suite will not
   catch this; a cross-module unit comparison will.

## Output for the borrow report

Include a short section:
```
Independent verification: 6,000 randomized cases incl. wicks to 1/10,000x and 10x.
- maxLoss == margin: exact (0 mismatches)
- settlement >= 0: exact (0 negative values)
- runway formula: 0 mismatches vs docstring-derived formula
```

## Common unit traps

- **APR vs APY** — compounding converts between them. A rate called `apr` may be APR or
  may be the annualized multiple with no compounding; say which it is.
- **Fraction vs percent** — `0.02` vs `2` in the same codebase often lives in adjacent files.
- **Hourly vs daily vs annual** — premium streams by the hour but users think in days; check
  the divisor (`3600`, `24`, `24*365`, `24*365*100`).
- **Session/off-hours multipliers** — verify the multiplier actually applies to the closed/pre/
  post sessions and *not* to `open` or `24/7`.

## Pitfall

**Do not trust the test suite's numbers unless you have re-derived at least one of them from
first principles.** A test like `expect(runwaySeconds(50, 500, 0.0001)).toBeCloseTo(1000 * 3600)`
proves only that the author wrote the same formula twice. Your own probe, derived from the
docstring alone, catches the case where both the code and the test share the same wrong
assumption.
