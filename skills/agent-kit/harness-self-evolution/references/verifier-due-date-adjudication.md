# Harness Verifier — due-date window adjudication (2026-08-08)

The Verifier cron reads `facts/predictions.md`, finds predictions whose DUE date
falls between the last Verification cycle and now, checks whether they came true
via the METRIC field, and appends the outcome to `facts/prediction-outcomes.md`.
This is the working recipe for doing that correctly — the failure modes below
each cost a wrong [SILENT]/report decision.

## The due-date window is the whole job

The single most important step is deciding WHICH predictions are due. Get this
wrong and you either (a) report when nothing is due (noise), or (b) stay silent
when a prediction is overdue (missed falsification). The correct flow:

1. Read the LAST Verification cycle timestamp from the tail of
   `prediction-outcomes.md` (the most recent `## Verification cycle — <ts>` or
   `## OUTCOME`/`## PREDICTION` header).
2. Read `date -u` for "now".
3. A prediction is DUE iff its due date is in `(last_cycle, now]`.
4. A prediction is OVERDUE iff its due date is `< now` AND it has no recorded
   outcome.

## Parse each prediction block INDIVIDUALLY — never a whole-file regex

A naive `re.finditer(r'## PREDICTION #(\d+).*?due\s+(\S+)', pred, re.S)` is
WRONG: the `.*?` spans across `## PREDICTION` headers, so a due date from a
LATER block gets mis-attributed to an EARLIER block that has no due date of its
own. In this session it produced garbage like `#19: due 2026-08-09T04:00Z`
(#19 has no due date) and `#33: due 2026-08-09T08:00Z` (that's #34's date).

Correct approach — split on the header, then parse each body:

```python
blocks = re.split(r'(?m)^## PREDICTION #(\d+)', pred)
# blocks[0] is preamble; then pairs of (num, body)
for i in range(1, len(blocks), 2):
    num, body = blocks[i], blocks[i+1]
    m = re.search(r'(?:due|Due|DUE|Adjudicate)[:\s]+'
                  r'([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:]+Z)', body)
    due = m.group(1) if m else None
```

Note the due-date field is inconsistent across blocks: some use `due
2026-08-09T04:00Z`, some `Due:  2026-08-08T22:00:00Z`, some `Adjudicate:
2026-08-04T00:00Z`. Match all four spellings. Predictions with NO due date
(older blocks like #19–#29, #39–#41, #71) are typically already adjudicated
under an `## OUTCOME #N` header — see next section.

## Outcomes use TWO header shapes — count both

`prediction-outcomes.md` records adjudications under BOTH
`## OUTCOME #N` (older cycles) AND `## PREDICTION #N` (newer cycles). When
checking whether a prediction is already recorded, match
`^#{2,3} (OUTCOME|PREDICTION) #(\d+)` — a grep for only `PREDICTION #N` will
falsely report #27/#28/#29/#30 as unrecorded when they were actually closed
under `OUTCOME #N`. Also cross-check `evolve-N` references in the outcomes body:
a prediction may be adjudicated inline (e.g. #39/#40/#41 appear only as
`evolve-39`/`evolve-40`/`evolve-41` mentions inside other blocks, not as their
own header).

## The due-epoch rule (Constitution Article V)

Never grade a prediction FULFILLED while any of its falsifiers is still OPEN /
NOT YET DUE. A forward-looking falsifier (e.g. "the next cycle does not
misdispatch") cannot be graded until that cycle has run. The correct status for
a partially-due prediction is PARTIAL with the open clauses listed, not
FULFILLED. This is what the `due epoch` guard in `prompts/verifier.md` enforces.

## [SILENT] decision

Return `[SILENT]` ONLY when:
- every prediction due since the last cycle is verified (FULFILLED and useful), AND
- no prediction is overdue (due date passed with no recorded outcome).

If ANY prediction is falsified, unverifiable, or overdue → report. In this
session the earliest genuinely-due-and-unadjudicated prediction (#31, due
2026-08-08T22:00Z) was still ~22h in the future, so [SILENT] was correct.

## Pitfall: don't trust the `.cycle-highwater` file for due-date logic

`facts/.cycle-highwater` tracks the evolve-N id counter, NOT prediction due
dates. It is useful for confirming the ledger is current (max evolve-N row id
in execution-log.md should match it), but it tells you nothing about which
predictions are due. Keep the two concerns separate.
