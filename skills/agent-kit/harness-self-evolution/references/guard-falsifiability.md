# Proving a harness guard can FAIL (evolve-31, 2026-08-01)

A guard that cannot fire is worse than no guard: the audit trail claims coverage
it does not have (Constitution Article V). The Critic caught two generations of
this in a row. This is the working recipe.

## The tautology, concretely

```bash
# execution-loop.sh (evolve-30, BROKEN)
_append_execution_log ...            # :405 appends "## evolve-N" — cycle from $RECOMMENDATION_FILE (:296)
_cyc="${CYCLE_ID:-}"                 # :412 CYCLE_ID defined NOWHERE -> always empty
[[ -z "$_cyc" ]] && _cyc="evolve-$(highest N in $EXECUTION_LOG)"   # reads the row just written
grep -q "Cycle ${_cyc}" "$RECOMMENDATION_FILE"   # plan vs string extracted from plan -> always true
grep -q "^## ${_cyc} " "$EXECUTION_LOG"          # log vs string extracted from log  -> always true
```

Cheap detector for this class: `grep -rn 'VARNAME' scripts/` — if the count of
*assignments* is 0 while references are >0, every `${VAR:-fallback}` in the file
is silently taking the fallback path.

## Fix 1 — define the id upstream, at global scope

Placed immediately after `EXECUTION_LOG=` and before any plan-file parsing:

```bash
CYCLE_ID="${CYCLE_ID:-}"
if [[ -z "${CYCLE_ID:-}" ]]; then
    _cycle_n="$(grep -oE '^## evolve-[0-9]+' "$EXECUTION_LOG" 2>/dev/null \
                | grep -oE '[0-9]+' | sort -n | tail -1)"
    CYCLE_ID="evolve-$(( ${_cycle_n:-0} + 1 ))"
    unset _cycle_n
fi
export CYCLE_ID
```

**Metric gotcha:** the declared falsifier was `grep -c '^CYCLE_ID=' … >= 1`.
An assignment *indented inside* the `if` block does not match `^CYCLE_ID=` and
scores 0. Hence the bare `CYCLE_ID="${CYCLE_ID:-}"` default line at column 0 —
it is both a real env-override hook and what makes the metric honest. Always
run your own declared metric before committing; the anchor may not match the
code you actually wrote.

Then make every consumer read it — `_append_execution_log` becomes
`cycle="${CYCLE_ID:-evolve-unknown}"`, verified by
`grep -n 'cycle=' scripts/execution-loop.sh | grep -c RECOMMENDATION_FILE` == 0.

## Fix 2 — extract the guard so it is callable

```bash
_assert_cycle_trace() {
    local _cyc="$1"
    [[ -n "$_cyc" ]] || return 0
    grep -q "Cycle ${_cyc}" "$RECOMMENDATION_FILE" 2>/dev/null || {
        log_error "STALE PLAN HEADER: plan does not name ${_cyc}"; return 1; }
    grep -q "^## ${_cyc} " "$EXECUTION_LOG" 2>/dev/null || {
        log_error "AUDIT GAP: no execution-log entry for ${_cyc}"; return 1; }
    return 0
}
```
Called from `execute_action` as `_assert_cycle_trace "${CYCLE_ID:-}" || return 1`.

## Fix 3 — the self-test (`scripts/selftest-stale-plan-guard.sh`)

Source the loop, point `RECOMMENDATION_FILE`/`EXECUTION_LOG` at a `mktemp -d`,
and assert BOTH directions:

| fixture | plan header | log row | expect |
|---|---|---|---|
| stale plan | evolve-30 | evolve-31 | rc=1 + `STALE PLAN HEADER` |
| audit gap  | evolve-31 | evolve-30 | rc=1 + `AUDIT GAP` |
| healthy    | evolve-31 | evolve-31 | rc=0 |

### Two sourcing traps (both cost a debug round-trip)

1. **`set -e` leaks in from the sourced script.** `execution-loop.sh` runs
   `set -euo pipefail` at the top; sourcing it applies that to the *test's* own
   shell, so the first deliberate `rc=1` kills the test — it exits 1 with **no
   output at all**, which reads like a sourcing failure. Put `set +e`
   immediately after the `source` line. Symptom to recognise: `rc=1` and an
   empty stdout.
2. Source under the loop's own re-entrancy guard
   (`if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then main "$@"; fi`) so `main`
   does not run, and assert the function exists before testing:
   `declare -F _assert_cycle_trace >/dev/null || { echo FAIL; exit 1; }`.

Verified output:
```
PASS: stale plan header fires (rc=1)
PASS: audit gap fires (rc=1)
PASS: healthy cycle passes (rc=0)
SELFTEST OK
```

## Residual to disclose in the report

AUDIT GAP still greps a log row that the same run wrote via `CYCLE_ID`. That is
intentional (it proves the append happened) but it is **not** an independent
signal. State this in the cycle report — pre-empting the Critic on a known
weakness is cheaper than being caught inflating the score.

## Blocklist note

`grep -c 'x' f && grep -n 'y' f | grep -c z` style `&&`-chains and
`git add -A && git commit -q -m "…"` were rejected with
`BLOCKED (hardline): command parser limit`. Splitting on `;` into one simple
statement per clause, or one command per `terminal` call, went through.
