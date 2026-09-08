#!/usr/bin/env bash
# reverify-row-probe.sh — is a published receipt actually reproducible?
#
# Usage:  bash reverify-row-probe.sh evolve-42 [/path/to/harness]
#
# Sources the SHIPPED _reverify_published_metrics + _metric_compare out of
# execution-loop.sh and runs them against a COPY of facts/execution-log.md, so
# the probe can never annotate the real ledger. Use this to tell a LOGIC bug
# ("the function is wrong") from a REACHABILITY bug ("the function is right but
# never ran on this row") before changing any code — the evolve-51 lesson.
#
# rc=0 -> every published metric in that row still reproduces
# rc=1 -> at least one METRIC DRIFT (printed below)
set -uo pipefail

CYCLE="${1:?usage: reverify-row-probe.sh evolve-N [harness_dir]}"
HARNESS_DIR="${2:-${HERMES_HOME:-$HOME/.hermes}/harness}"
cd "$HARNESS_DIR" || { echo "no harness at $HARNESS_DIR"; exit 2; }

LOOP="scripts/execution-loop.sh"
[[ -f "$LOOP" ]] || { echo "no $LOOP"; exit 2; }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
cp facts/execution-log.md "$TMP/log.md"

log()       { :; }
log_warn()  { echo "SHIFT: $*"; }
log_error() { echo "DRIFT: $*"; }

EXECUTION_LOG="$TMP/log.md"
# shellcheck disable=SC1090
source <(awk '/^_metric_compare\(\)/,/^}/' "$LOOP")
source <(awk '/^_reverify_published_metrics\(\)/,/^}/' "$LOOP")

_reverify_published_metrics "$CYCLE" "$TMP/log.md"
rc=$?
echo "---"
echo "rc=$rc  (0 = receipts reproduce, 1 = phantom receipt in $CYCLE)"
grep -F "METRIC DRIFT ${CYCLE}" "$TMP/log.md" || true
exit $rc
