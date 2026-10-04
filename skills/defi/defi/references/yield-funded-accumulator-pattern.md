# Yield-Funded Accumulator Pattern

When the operator wants a recurring buy funded by the farm itself (e.g. "take $5 out of the LP and put it into COQ"), do not model it as a weekly allowance of new capital. Build a **credit ledger** that accrues only what the fee ledger can actually measure, fires at a threshold, funds the swap from the LP's own idle capital, and preserves the existing weekly-dip fallback.

## Design rules

1. **Credit only measured proceeds.** Advance the ledger by the drift-adjusted fee accrual the fee ledger reports. If the window contains a re-center and the ledger returns `fees_usd=None` ("churn in window"), credit **nothing** for that window; churn is not profit. Move the measure cursor forward regardless so the churn window can never be counted twice.
2. **Threshold + cooldown.** Fire when realized credit crosses the operator target (e.g. $5.00). Stamp a cooldown (e.g. 20h) so a churning book cannot rinse the same strength through the buy leg repeatedly.
3. **Trigger order.** Dip timing still wins (`COQ -X%`) → realized proceeds → Sunday fallback. The fallback stays so the leg can never silently skip forever.
4. **Two separate pots.** A weekly-allowance buy and a yield-funded buy are not the same budget. Spending one must not debit the other. Log which pot paid (`funded: weekly|lp_proceeds`).
5. **Debit on spend.** When a yield-funded buy executes, reduce the credit ledger by the deployed amount and stamp `last_yield_buy_ts`. Do not let the credit float above reality.
6. **Fund from the LP path that is already wired.** If the accumulator has a `--source lp` mode that withdraws idle capital and swaps, use it; the only new behavior is the trigger.

## Reference implementation

```python
YIELD_CREDIT_USD = 5.0       # buy when this much realized LP yield has accrued
YIELD_COOLDOWN_H = 20        # at most one yield-funded buy per N hours
MIN_CREDIT_STEP = 0.001      # ignore noise below a tenth of a cent

def _ledger_fees_since(ts_epoch):
    """Returns (fees_usd, note). None fees means 'unmeasurable', not zero."""
    import steward_fee_ledger as L
    d = L.load()
    snaps = d.get("snapshots", [])
    if not snaps:
        return None, "no snapshots yet"
    cur = snaps[-1]
    r = L.fees_since(ts_epoch, snaps, cur)
    if r.get("fees_usd") is None:
        return None, r.get("note") or "unmeasurable"
    return float(r["fees_usd"]), f"measured over {r.get('window_h')}h"

def accrue_yield_credit(st):
    now = time.time()
    last = float(st.get("last_measure_ts") or 0.0)
    if not last:
        st["last_measure_ts"] = now
        return st.get("yield_credit_usd", 0.0), "cursor established"
    fees, note = _ledger_fees_since(last)
    st["last_measure_ts"] = now
    if fees is not None and fees > MIN_CREDIT_STEP:
        st["yield_credit_usd"] = round(
            float(st.get("yield_credit_usd") or 0.0) + fees, 4)
    return float(st.get("yield_credit_usd") or 0.0), note

def yield_ready(st):
    credit = float(st.get("yield_credit_usd") or 0.0)
    if credit < YIELD_CREDIT_USD:
        return False, credit, f"credit ${credit:.2f} of ${YIELD_CREDIT_USD:.2f}"
    last_y = float(st.get("last_yield_buy_ts") or 0.0)
    if last_y and (time.time() - last_y) < YIELD_COOLDOWN_H * 3600:
        hrs = (time.time() - last_y) / 3600.0
        return False, credit, f"credit ready, cooldown {hrs:.1f}h of {YIELD_COOLDOWN_H}h"
    return True, credit, "realized LP proceeds"
```

## State schema additions

```json
{
  "yield_credit_usd": 0.0,
  "last_measure_ts": 0.0,
  "last_yield_buy_ts": 0.0
}
```

## Verification

- Plant a credit above the threshold in the state file and run dry. Expect the trigger to fire and stage a swap from the LP path.
- Restore the state afterward; the ledger must not have been debited.
- Confirm an unmeasurable window (e.g. right after a re-center) advances the cursor without changing the credit.
