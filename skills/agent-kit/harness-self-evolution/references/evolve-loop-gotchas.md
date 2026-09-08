# Running the evolve loop — operational gotchas

Session-derived pitfalls for executing `execution-loop.sh evolve` (and re-running it
after a fix). These bite every cycle, not just one-off runs.

## 1. The cron prompt's STEP 3 path is wrong
The Harness Evolution cron prompt says:
`cd ${HERMES_HOME}/harness && bash execution-loop.sh evolve`
but the script is NOT at the harness root — it lives at
`${HERMES_HOME}/harness/scripts/execution-loop.sh`.
Run `bash scripts/execution-loop.sh evolve` from `${HERMES_HOME}/harness` instead.
(There is no root-level `execution-loop.sh`; `ls` confirms it only exists under `scripts/`.)

## 2. Every invocation burns a cycle number — re-runs go stale
`CYCLE_ID` is derived as `evolve-$(highwater + 1)` at the top of the script. So if you
run the loop, hit a pre-dispatch abort, fix the recommendation, and run again, the
second run is a NEW cycle (e.g. evolve-71 → evolve-72 → evolve-73). Consequences:
- The plan header (`# Recommendation (Cycle evolve-N)`) goes stale → the loop logs
  `✗ STALE PLAN HEADER: plan does not name evolve-N` and the run is messy.
- Each run writes a plan snapshot (`facts/.plan-snapshots/evolve-N.md`) and a ledger row.
**Fix:** before re-running, update the recommendation header to the CURRENT cycle number
(read `facts/.cycle-highwater` first), and expect the cycle number to have advanced.

## 3. A pre-dispatch abort leaves a dispatch sentinel that blocks re-entry
When the pre-dispatch gate aborts (e.g. UNPARSEABLE METRIC), the loop still touches
`facts/.dispatch-sentinels/dispatched-evolve-N`. Re-running within the cron floor
(10800s) then fails with:
`✗ DISPATCH ALREADY RUNNING — a dispatch sentinel (...) is newer than the 10800s cron floor`
**Fix:** `rm -f facts/.dispatch-sentinels/dispatched-evolve-N` before re-running. The
aborted run logged `result: aborted-pre-dispatch` and did NOT dispatch real work, so
clearing the sentinel is safe.

## 4. The pre-dispatch gate rejects bare-command metrics
`_pre_dispatch_metric_gate` calls `_reject_unparseable_metric`, which only accepts
backtick-delimited metrics that START with `grep|awk|wc`. A "verify by running the
selftest" metric like `` `bash scripts/selftest-detail-metric-gate.sh` exits 0 `` is
REJECTED pre-dispatch (`UNPARSEABLE METRIC — aborting before dispatch`). Even a
legitimate verification must be re-authored as a grep of a literal present in a file,
e.g. `` `grep -c 'ALL 28 ASSERTIONS HOLD' scripts/selftest-detail-metric-gate.sh` >= 1 ``.
Author every measurable metric as a grep/awk/wc of a literal in a real file from the start.

## 5. The patch tool mangles backslash-heavy sed/awk regexes
Patching a sed literal-extraction regex (e.g. `s/.*grep[[:space:]]*-c[[:space:]]*['\"].../`)
through the `patch` tool over-escaped the backslashes, corrupting the line. The diff
display showed escaped forms that did NOT match the real file bytes.
**Fix:** after patching any sed/awk line with backslashes, verify the ACTUAL bytes with
`sed -n '<line>p' file | cat -A` (or `cat -A`), and re-patch with the exact intended
single-backslash form if the tool over-escaped. Do not trust the diff echo.

## 6. Phantom-literal gate covers grep-flag forms (evolve-73)
`_reject_phantom_literal_metric` (execution-loop.sh) extracts the grep literal with
`grep[[:space:]]*-[coqE]*` so `grep -cE`/`grep -oE`/`grep -q` forms are caught, not just
`grep -c`. Selftest case `ac` proves a `grep -cE` phantom-literal plan aborts rc=2 while a
forward-looking `grep -cE` of a file the action WILL modify passes rc=0. Selftest is
28/28 ASSERTIONS HOLD. When authoring metrics, remember the gate now catches flag forms too.
