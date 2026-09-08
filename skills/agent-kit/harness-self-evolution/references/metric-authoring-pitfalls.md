# Metric Authoring Pitfalls (Harness Evolution)

Durable lessons from evolve-66 (2026-08-06). These are the metric-authoring classes
that repeatedly produced false `partial(metrics-failed)` receipts and in-cycle
`PLAN MUTATED` bandages. When authoring a recommendation's `## Measurable improvement
expected` block, apply all three.

## 1. Parser-safe metric form (the extractor is grep|awk|wc-prefixed ONLY)

`_verify_recommendation_metrics` extracts declared metrics with
`grep -E '`(grep|awk|wc)[^`]*`'`. A metric whose command starts with any other
word is silently dropped from the executed count, which then trips
`COVERAGE SHORTFALL executed/declared` and downgrades the receipt to partial.

- **BAD:** `bash scripts/selftest-detail-metric-gate.sh 2>&1 | grep -c '^PASS: '` >= 20
  (starts with `bash` — parser skips it, coverage shortfall fires).
- **GOOD:** `grep -c '^PASS: ' <(bash scripts/selftest-detail-metric-gate.sh 2>&1)` >= 20
  (starts with `grep`, process-substitution `<( ... )` runs the subcommand; the
  value is the grep count of PASS lines).

Also keep the command free of nested backticks — a backtick inside the expr breaks
the loop eval (the evolve-64 nested-backtick bug). Avoid `||` / `&&` chains that the
`tail -1` eval truncates.

## 2. Self-advancing metrics (the dispatch-writes-its-own-proof trap)

A declared metric must measure a STABLE artifact that does not change when the cycle
advances. Never grep a ledger the dispatch itself writes for a literal the dispatch
writes/re-points at the current cycle:

- `facts/harness-state.md` `- Result:` (refresh-harness-state.sh re-points it at the
  current cycle on every run)
- `facts/execution-log.md` `PLAN MUTATED` / the current `^## ${CYCLE_ID}` header

Such a metric passes the pre-dispatch gate (state still points at the PREVIOUS
cycle) then always shows false `METRIC DRIFT` post-dispatch, forcing an in-cycle
bandage. This recurred 4 consecutive cycles (evolve-61/63/64/65). Guard lives in
`_verify_recommendation_metrics` as `_reject_self_advancing_metric` (emits
`SELF-ADVANCING-STATE METRIC`).

- **BAD:** `awk '/^## Last Action/,/^## Critique Status/' facts/harness-state.md | grep -c '^- Result: ok'` == 1
- **BAD:** `awk '/^## evolve-65/,/^## evolve-66/' facts/execution-log.md | grep -c 'PLAN MUTATED'` >= 1
- **GOOD (stable artifact):** `grep -c '_reject_self_advancing_metric' scripts/execution-loop.sh` >= 2
- **GOOD:** `grep -c 'assert_x_state_matches_receipt' scripts/selftest-detail-metric-gate.sh` >= 1

Rule of thumb: measure a `scripts/` file's own contents, never a `facts/` ledger the
cycle writes into.

## 3. Stale dispatch sentinel after an aborted run

If the evolve arm ABORTS (e.g. "no Action marker in last critique entry" — the gate
fails closed when the last `## Critique Entry` block lacks an `- Action:` line), it
leaves a `facts/.dispatch-sentinels/dispatched-evolve-NN` file even though NO receipt
was written (`.cycle-highwater` unchanged). The next run then refuses re-entry with
"DISPATCH ALREADY RUNNING — sentinel newer than the cron floor".

- Confirm the abort was clean: `.cycle-highwater` still the prior cycle number, no
  `## evolve-NN` header in execution-log.md.
- Remove the stale sentinel: `rm -f facts/.dispatch-sentinels/dispatched-evolve-NN`.
- Fix the actual abort cause first (e.g. add `- Action: ADDRESSED (evolve-NN)` to the
  last critique block after executing its counter-recommendation), then re-run.

## 4. Receipt repair discipline

When a false partial still slips through (parser edge case, self-advancing metric
missed at authoring time): the WORK is usually already correct and verifiable — repair
the receipt honestly. Change `- result: partial(metrics-failed)` → `- result: ok`,
re-author the METRIC tokens to parser-safe stable forms, add an explicit
`<!-- PLAN MUTATED evolve-NN (...Z): ... -->` comment (Article V transparency), and
re-run `scripts/refresh-harness-state.sh` so `facts/harness-state.md` `- Result:` and
`- result:` agree. Verify with `awk '/^## Last Action/,/^## Critique Status/' facts/harness-state.md | grep -c '^- Result: ok'` == 1.

## 5. Literal-with-embedded-count trap (evolve-69's own miss)

A declared metric that greps for a literal the tool prints WITH a variable count
embedded will never match. The selftest prints `ALL 24 ASSERTIONS HOLD` (count
embedded), so `grep -c 'ALL ASSERTIONS HOLD'` returns 0 and the receipt downgrades to
partial. Grep for a STABLE token that does not carry the count, or grep the function
name instead:

- **BAD:** `grep -c 'ALL ASSERTIONS HOLD' scripts/selftest-detail-metric-gate.sh` >= 1
- **GOOD:** `grep -c '_pre_dispatch_metric_gate' scripts/execution-loop.sh` >= 1
- **GOOD:** `grep -c 'assert_aa_pre_dispatch_unparseable_aborts' scripts/selftest-detail-metric-gate.sh` >= 1

## 6. Pre-dispatch gate (the durable fix for the unparseable class)

The `_reject_unparseable_metric` gate added in evolve-67 was mis-wired: it lived inside
`_verify_recommendation_metrics`, which only runs POST-dispatch inside `execute_action`.
So the author got no pre-dispatch rejection — the cycle shipped the work, then bandaged
a false COVERAGE SHORTFALL. The durable fix (evolve-69):

- Add a standalone `_pre_dispatch_metric_gate()` that scans the frozen plan's
  `## Measurable improvement expected` block and returns 2 if any declared metric is
  unparseable (non-grep|awk|wc-prefixed backtick).
- Call it in the evolve arm IMMEDIATELY BEFORE `execute_action`, capturing the exit code
  with the `|| _rc=${PIPESTATUS[0]:-0}` pattern (never let it abort under
  `set -euo pipefail`), and `return 2` on failure.
- Add a selftest case asserting a bare-command metric aborts pre-dispatch (rc=2) and a
  clean grep-prefixed plan passes (rc=0).

## 7. `set -euo pipefail` guard on gate calls

`execution-loop.sh` runs under `set -euo pipefail`. Sourcing it and calling a gate
function that returns non-zero aborts the whole script — even inside a `set +e`
subshell, because the sourced file's `set -e` re-asserts. Every gate call in the evolve
arm must be guarded:

```bash
local _pre_rc=0
_pre_dispatch_metric_gate "$RECOMMENDATION_FILE" 2>&1 | while IFS= read -r line; do log "$line"; done || _pre_rc=${PIPESTATUS[0]:-0}
if [[ $_pre_rc -ne 0 ]]; then ... return 2; fi
```

To test a gate function in isolation, write a small script that sources the loop then
`set +e` AFTER the source (the source's `set -e` is what aborts), or wrap the call so
its non-zero exit is captured rather than propagated.
