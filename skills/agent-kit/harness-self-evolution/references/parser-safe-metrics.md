# Authoring parser-safe declared metrics (evolve-64 recipe)

Session 2026-08-06 (evolve-64). Two mis-authored metrics in `## Measurable
improvement expected` caused the loop's `_verify_recommendation_metrics` to
downgrade the cycle receipt to a FALSE `partial(metrics-failed)`. The underlying
work was correct; only the metric expressions were badly written. This is the
recipe for avoiding both failure modes and repairing the receipt if one slips in.

## Failure mode 1 — nested backtick breaks eval

Authoring a metric that counts backtick bullets, e.g. counting the snapshot's
`- ` lines, is tempting to write as:

    - `awk '/^## Measurable improvement expected/,/^## Block terminator/' \
         facts/.plan-snapshots/evolve-63.md | grep -oE '^- \`' | wc -l` == 5

The backtick INSIDE the backticked expression is consumed as a closing backtick
by the parser. The loop runs the expression via `eval` and dies with:

    scripts/execution-loop.sh: eval: line 543: unexpected EOF while looking for matching `'

That `eval` failure yields a `[non-numeric FAIL]` for the metric, and the gate
downgrades the whole receipt to `partial(metrics-failed)`.

**Fix:** never embed a backtick inside a backticked metric expression. Count
`^- ` with a literal-space grep instead of `^- \``:

    - `awk '/^## Measurable improvement expected/,/^## Block terminator/' \
         facts/.plan-snapshots/evolve-63.md | grep -c '^- '` == 5

`grep -c '^- '` counts exactly the `- ` bullets and needs no backtick escape.

## Failure mode 2 — unscoped self-matching grep on a ledger

The loop rejects any metric that greps `facts/execution-log.md` (or the other
ledgers it writes: predictions, critique-log, harness-state,
prediction-outcomes) for a literal with no awk range scoping:

    METRIC: ... [SELF-MATCHING CRITERION on facts/execution-log.md — an
    unscoped grep of the file the criterion is written into measures itself;
    scope it with awk range addressing; FAIL]

**Fix:** always scope ledger greps to a cycle range so the criterion does not
measure the file it is written into:

    # BAD (self-matching)
    - `grep -c 'PLAN MUTATED evolve-63' facts/execution-log.md` >= 1
    # GOOD (awk-range scoped)
    - `awk '/^## evolve-63/,/^## evolve-64/' facts/execution-log.md \
         | grep -c 'PLAN MUTATED evolve-63'` >= 1

## Failure mode 3 — the `grep -oE 'METRIC: '` self-inflating counter

When a metric verifies "the evolve-N receipt publishes K METRIC tokens" via
`awk ... | grep -oE 'METRIC: ' | wc -l`, note that the awk program itself
contains the literal `METRIC: ` (the grep pattern), so the count is
self-inflated by 1 and the number is not a clean count of distinct metrics.
This is cosmetic for a `== 5` vs actual-4 check only if you know the offset;
prefer a non-self-referential counting form (e.g. count `-> [PASS` or
`METRIC: (awk|bash|grep)`) when the exact number must be trustworthy.

## Repairing a false `partial(metrics-failed)` receipt

If a cycle's receipt got downgraded solely because its OWN declared metrics were
mis-authored (eval break / self-match), repair it so a false FAIL does not sit
in the ledger — "a false FAIL is as corrosive as a false PASS":

1. Confirm the underlying action work actually completed and the real facts
   pass live (re-run each metric's intent manually).
2. Rewrite the receipt's `- result:` line to `ok`.
3. Replace the `|| METRIC: ...` emitted portion with parser-safe, scoped
   metrics that reproduce the same intent, and add a
   `<!-- NOTE evolve-N ... -->` comment explaining the repair (per Article V,
   Transparency of Influence).
4. Re-verify: all declared metrics `eval` cleanly (numeric output, no
   `unexpected EOF`), receipt metric set == frozen snapshot declared count,
   `git status --short` clean, selftest still 18/18.
5. Commit with a message that names the cycle and the reconciliation.

## Quick parser-safety self-check before dispatch

Run the loop's exact extraction on the recommendation's metric block and eval
each expression:

    sed -n '/^## Measurable improvement expected/,/^## /p' \
      facts/recommendation.md | grep -oP '(?<=`)(grep|awk|wc)[^`]*(?=`)'

Every extracted expression must `eval` to a digit with no `unexpected EOF` in
stderr. If any is non-numeric or breaks, fix the metric BEFORE running
`execution-loop.sh evolve`.
