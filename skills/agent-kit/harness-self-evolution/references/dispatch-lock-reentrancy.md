# Dispatch Re-Entrancy Guard — Hardening Lessons (evolve-76)

Class of problem: a self-evolving loop that reads a plan file, dispatches an
action, and must NOT dispatch the same plan twice. The `_acquire_dispatch_lock`
in `scripts/execution-loop.sh` is the reference implementation. These are the
durable pitfalls discovered across evolve-72/73/74/75/76.

## Pitfall 1 — Key the consumed-plan guard to the PLAN'S OWN HEADER ID, not the recomputed CYCLE_ID

The loop derives `CYCLE_ID` as `last+1` from the execution log (line ~64). That
id is ALWAYS ONE AHEAD of the plan's header id in `recommendation.md` (e.g. plan
header `evolve-75`, next recomputed `CYCLE_ID=evolve-76`). A guard that greps
`^## CONSUMED ${CYCLE_ID}$` can therefore NEVER match the `## CONSUMED <plan-id>`
marker the dispatch itself wrote — the guard is dead code and the same plan
re-dispatches.

Correct pattern — extract the plan's own header id and grep for that:

```bash
_plan_id="$(sed -n 's/^# Recommendation (Cycle evolve-\([0-9]*\))/evolve-\1/p' "$RECOMMENDATION_FILE" | head -1)"
if [[ -n "$_plan_id" ]] && grep -q "^## CONSUMED ${_plan_id}$" "$RECOMMENDATION_FILE"; then
    log_error "already consumed for ${_plan_id}; refusing duplicate dispatch"
    return 3
fi
```

Fail-open on a malformed header (empty `_plan_id`) so a legitimate new plan is
never false-blocked.

## Pitfall 2 — A selftest that greps a synthetic file where all ids match is a FALSE POSITIVE

The original selftest case (ad) built a `recommendation.md` with header
`evolve-999`, marker `## CONSUMED evolve-999`, and grepped `^## CONSUMED
evolve-999$` — header/marker/grep ids all coincided, so it passed while the
production guard (keyed to the recomputed id) was broken. A selftest must
exercise the REAL function under the REAL recompute: header id DIFFERS from the
recomputed CYCLE_ID, and the guard must still refuse because the plan's header
id is consumed. Add a control where the plan header is NOT consumed and assert
dispatch proceeds (rc=0).

To run the real function in a selftest, source just the function definition out
of the loop script:

```bash
source <(awk "/^_acquire_dispatch_lock\\(\\)/,/^}/" "$LOOP")
_acquire_dispatch_lock; echo "rc=$?"
```

## Pitfall 3 — Ordering: the consumed-plan check MUST run BEFORE the sentinel write

If a refused duplicate dispatch writes its sentinel first, that sentinel trips
the 3h floor check on the NEXT legitimate dispatch — a refused duplicate poisons
the guard for the real plan. Order in `_acquire_dispatch_lock`:
1. flock + inode check
2. 3h floor check (existing sentinels)
3. **consumed-plan check (return 3 before writing anything)**
4. sentinel write + existence assertion

Assert in the selftest that a refused duplicate writes NO sentinel.

## Pitfall 4 — A run aborted at the feedback gate leaves a STALE sentinel

`execution-loop.sh evolve` aborts (rc=2) at the `read-external-feedback` gate if
the last critique entry's `Action:` field is not `ADDRESSED` — but the abort
happens AFTER the sentinel write, so a stale `dispatched-<id>` is left behind
with no execution-log row. The next real dispatch then fails with "a dispatch
sentinel ... is newer than the 10800s cron floor". Fix: remove the stale sentinel
(verify no execution-log row exists for that id first) before re-running.

## Pitfall 5 — The `must_act` gate reads the LAST critique entry's Action field

The loop refuses to dispatch while the last critique entry is critical/high and
its `Action:` is not `ADDRESSED`. After you ACTUALLY fix the defect (and verify
it), update that entry's `Action:` line to `ADDRESSED (evolve-N) — <what you
did>` so the gate passes. Do this only after the fix is real and verified, not
before — the gate exists to stop you claiming work you haven't done.

## Verification recipe

```bash
bash -n scripts/execution-loop.sh && bash -n scripts/selftest-dispatch-lock.sh
bash scripts/selftest-dispatch-lock.sh   # expect "ALL PASS"
# confirm no stray sentinels for the current cycle id:
ls facts/.dispatch-sentinels/ | grep -E "evolve-7[6-9]" || echo "clean"
```
