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

## ⚠️ Counting graded blocks: glob by NAME PREFIX, never by `.md` extension

This reference's due-date logic was right; the **denominator** was wrong for ~6 weeks.
Prior cycles computed "N/N blocks graded" with `glob('facts/history/prediction-outcomes*.md')`.
That pattern silently skipped `facts/history/prediction-outcomes.md-archive-20260808T041001Z` —
an archive whose name ends in `Z`, not `.md`, so `*.md` never matched it. The Gardener writes
archives as `<original-name>-archive-<ts>` sometimes and `<stem>-archive-<ts>.md` other times;
both forms live in `facts/history/`. Cost: 5 graded blocks (#38, #42, #46, #47, #48) were
excluded from every tally, so the harness reported "75/75 graded, 7 FALSIFIED" when file truth
was **80 blocks, 11 FALSIFIED, 2 PARTIALLY**. The Critic's entry-75 finding caught it.

**Rule — enumerate the corpus by name prefix over BOTH directories, then print the file list:**
```python
files = sorted(glob.glob('facts/prediction-outcomes*')) \
      + sorted(glob.glob('facts/history/prediction-outcomes*'))
```
Never emit "N/N graded" without the exact file list it was computed over. A glob that *looks*
correct and matches 3 of 4 files is the failure mode; printing the list is the cheap defense.

**Count IDs, not blocks.** Two prediction numbers carry two blocks each in the Aug-8 archive
(#38: primary FALSIFIED + second-claim FULFILLED; #42: early + final adjudication, both
FALSIFIED), so raw block count (82) exceeds distinct-id count (80). Report the distinct-id union,
and disclose any pid whose blocks DISAGREE rather than letting the tie-break hide it.

**Match BOTH `Status:` styles when extracting**, and match the Useful marker on both phrasings —
`Useful?` (newer) and `Was the prediction useful?` (older). A one-phrasing regex undercounts and
makes a present verdict look missing. A block whose archive copy was truncated mid-compaction
(#140: Status + f1 + f2 only) legitimately has no Useful marker — say "no marker, block
truncated", never infer N.

**Distinguish "ungraded" from "never authored."** Before reporting a number in a claimed range
as ungraded, `grep -rn 'PREDICTION #<N>'` the whole harness tree (all `predictions*`, current +
archived). #109–#112 and #117 have no grade because the producer authored no prediction for those
cycles — a hole in the *numbering sequence*, not a missing verdict. Reporting them as "ungraded"
would send a future reader chasing phantom falsifications.

## Pitfall: a MALFORMED block header silently drops a pid from the corpus

The corpus scan must tolerate header noise. `#37` is recorded only under
`### PRED#37` (not `### PREDICTION #37`), so a strict
`^#+ (PREDICTION|OUTCOME) #N` matcher returns 110 pids + no `#37` while file truth
is 111 pids. The 111th pid is exactly the one carrying the `OPEN` grade, so the
error presents as "a pid vanished" rather than "a regex missed". Always reconcile
the derived count against the standing header before publishing it, and when the
two disagree, look for a header the author mangled — do not adjust the header.

## Pitfall: the LOCATION of a grading block drifts when the Gardener archives it

A blocked pid's verdict stays true while its *file* changes. After a Gardener
compaction the live `prediction-outcomes.md` holds **zero** `### PREDICTION #N`
grading blocks — every #135–#146 verdict lives in `facts/history/` only. Cycle
entries that kept asserting "6 FULFILLED in current file (#141–#146)" were
repeating a file state that no longer existed. Grades were never wrong; the
stated location was stale, and a stale location is how a future reader concludes
a verdict is missing. Re-resolve where each block lives every cycle, and when the
location has moved, correct the record rather than repeating the old sentence.

## Pitfall: don't trust the `.cycle-highwater` file for due-date logic

`facts/.cycle-highwater` tracks the evolve-N id counter, NOT prediction due
dates. It is useful for confirming the ledger is current (max evolve-N row id
in execution-log.md should match it), but it tells you nothing about which
predictions are due. Keep the two concerns separate.
