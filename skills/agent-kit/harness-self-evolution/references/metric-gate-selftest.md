# Metric-gate selftest — working script + sourcing traps (evolve-26, 2026-08-01)

Purpose: prove `_verify_recommendation_metrics` (in `scripts/execution-loop.sh`)
is threshold-aware, deterministically and re-runnably, instead of eyeballing the
audit log. Reference it as a metric in `recommendation.md` so the gate self-checks.

## The two traps when sourcing a harness script for a selftest

`execution-loop.sh` (like most harness scripts) does TWO things that break a naive
`source`:

1. **It ends in `main "$@"`** — sourcing it runs a whole cycle as a side effect.
   FIX: guard the entrypoint so `main` only runs on direct execution:
   ```bash
   if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
       main "$@"
   fi
   ```
   This is a one-line, backward-compatible edit — direct `bash script.sh evolve`
   still works, and `source script.sh` becomes side-effect free.

2. **It sets `set -euo pipefail` at the top**, which the sourcing shell INHERITS.
   The function under test returns `rc=1` on a failing metric — that is exactly
   the behaviour you are asserting — but inherited `set -e` makes the selftest
   ABORT the instant the function returns non-zero, producing empty output and a
   misleading rc=1 with no assertions run. FIX: `set +eu` immediately after the
   `source ... || true` line, before calling the function.

Symptom of trap 2: selftest prints nothing and exits 1, non-deterministically at
first (depending on which line trips errexit). Do not chase it as a logic bug —
it's the inherited shell option.

## Working selftest (scripts/selftest-metric-gate.sh)

```bash
#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RECOMMENDATION_FILE=""
# shellcheck disable=SC1090
source "$SCRIPT_DIR/execution-loop.sh" >/dev/null 2>&1 || true
set +eu                       # <-- trap 2: drop inherited errexit

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT; fails=0

# Case 1: metric FAILS its declared threshold -> gate must return rc=1
printf '## Measurable improvement expected\n- `grep -c '\''zzz_absent'\'' /dev/null` >= 1\n## next\n' > "$tmp/fail.md"
RECOMMENDATION_FILE="$tmp/fail.md"; _verify_recommendation_metrics >/dev/null 2>&1; rc1=$?
[ "$rc1" = "1" ] || { echo "FAIL case1: expected rc=1 got $rc1"; fails=1; }

# Case 2: metric SATISFIES its threshold -> gate must return rc=0
printf '## Measurable improvement expected\n- `grep -c '\''root'\'' /etc/hostname` >= 0\n## next\n' > "$tmp/pass.md"
RECOMMENDATION_FILE="$tmp/pass.md"; _verify_recommendation_metrics >/dev/null 2>&1; rc2=$?
[ "$rc2" = "0" ] || { echo "FAIL case2: expected rc=0 got $rc2"; fails=1; }

[ "$fails" = "0" ] && { echo "selftest-metric-gate: PASS (rc1=$rc1 rc2=$rc2)"; exit 0; }
echo "selftest-metric-gate: FAIL"; exit 1
```

Expected: `selftest-metric-gate: PASS (rc1=1 rc2=0)`, exit 0, stable across runs.

## Note on which metrics the gate picks up
The gate only extracts `grep|awk|wc` backticked expressions. A metric written as
`` `bash scripts/selftest-metric-gate.sh` == 0 `` will NOT be auto-run by the gate
(bash isn't in the allowlist) — run the selftest by hand during the cycle and cite
its PASS in the report. Keep at least one `grep -c ... >= 1` style metric so the
in-loop gate has something to verify and the audit entry carries a `[PASS >= 1]`.
