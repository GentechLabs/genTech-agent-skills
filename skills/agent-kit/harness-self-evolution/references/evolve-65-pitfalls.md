# Harness Evolution — Pitfalls (evolve-65)

Three class-level pitfalls surfaced while executing the evolve-64 DEGRADATION/high
critique's counter-recommendation (A)-(D). All three are about the evolve arm's
self-verification machinery, not about any one cycle's content.

## 1. Self-referential declared metrics → false partial(metrics-failed)

**Symptom:** A plan's declared metrics PASS at authoring time, the dispatch runs and
succeeds, but the post-dispatch reverify flags `METRIC DRIFT` and the receipt is
downgraded to `partial(metrics-failed)` even though the work is correct.

**Root cause:** The declared metrics measured state that the dispatch ITSELF advances.
Concretely, evolve-65 declared:
- `awk '/^## Last Action/,/^## Critique Status/' facts/harness-state.md | grep -c '^- Result: ok'` == 1
- `grep -c 'PLAN MUTATED evolve-64' facts/execution-log.md` >= 1

The dispatch runs `refresh-harness-state.sh`, which re-points the state file's
`## Last Action` at the NEW cycle (evolve-65) and the receipt appends its own
`PLAN MUTATED evolve-65` marker. So the post-dispatch reverify sees the state file
now reading `- Result: ok` for evolve-65 (count 0 for the evolve-64-scoped grep) and
the marker count inflated — both flagged as drift.

**Rule:** Declared metrics must measure the WORK, not the state the dispatch mutates.
Scope them to things the dispatch does NOT advance:
- grep the script for the new call site (`grep -c 'refresh-harness-state' scripts/execution-loop.sh` >= 2)
- count selftest PASS lines (`bash scripts/selftest-detail-metric-gate.sh | grep -c '^PASS: '` >= 19)
- grep for a marker that already exists BEFORE the dispatch (e.g. the PRIOR cycle's
  PLAN MUTATED marker, which the dispatch does not remove)

Avoid metrics that read `facts/harness-state.md`'s `## Last Action` block or grep
`facts/execution-log.md` for a marker the current receipt will add — those are
self-referential and will drift.

## 2. Aborted run leaves a dispatch sentinel that blocks re-entry

**Symptom:** After an abort (e.g. the feedback gate returns `ABORTED: ... unaddressed`),
re-running the evolve arm fails with `DISPATCH ALREADY RUNNING — a dispatch sentinel
(dispatched-evolve-N) is newer than the 10800s cron floor`.

**Root cause:** `_acquire_dispatch_lock` creates `facts/.dispatch-sentinels/dispatched-${CYCLE_ID}`
at lock acquisition (execution-loop.sh:116), BEFORE the feedback gate runs. An abort at
the gate therefore leaves a fresh sentinel even though no real dispatch happened.

**Fix:** Before re-running after an abort, verify no ledger row was written
(`grep -c '^## evolve-N ' facts/execution-log.md` == 0), then remove the stale sentinel:
`rm -f facts/.dispatch-sentinels/dispatched-evolve-N`. Only clear it when the abort
happened before `_append_execution_log` — if a receipt row exists, the cycle already
ran and you must NOT re-dispatch.

## 3. Mark the critique ADDRESSED before re-running the evolve arm

**Symptom:** You execute a critique's counter-recommendation, then re-run the evolve arm
and it aborts again with `ABORTED: DEGRADATION high unaddressed`.

**Root cause:** `read-external-feedback` (execution-loop.sh:277) reads the LAST
`## Critique Entry` block's `- Action:` field. If it still says `PENDING` (or is
absent) and severity is high/critical, the gate fails closed.

**Fix:** After executing the counter-recommendation, update the critique entry's
`- Action: PENDING` → `- Action: ADDRESSED (evolve-N)` in `facts/critique-log.md`
BEFORE re-running. This is the same fail-closed gate that catches genuinely
unaddressed critiques — you must not bypass it, only mark it truthfully once the
work is actually done and verified.

## Repair pattern for a false partial

When a false `partial(metrics-failed)` lands in a receipt (work is actually correct):
1. Fix the receipt's `- result:` to `ok` in `facts/execution-log.md`.
2. Add a `<!-- PLAN MUTATED evolve-N ... -->` marker documenting the metric
   re-authoring, per Article V (Transparency of Influence).
3. Re-run `bash scripts/refresh-harness-state.sh` so the state file's `## Last Action`
   `- Result:` re-syncs to `ok`.
4. Verify with the state-vs-receipt gate:
   `bash -c 'source scripts/execution-loop.sh >/dev/null 2>&1; _assert_state_matches_receipt && echo CONSISTENT || echo MISMATCH'`
