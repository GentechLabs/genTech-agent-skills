#!/usr/bin/env bash
# find-live-source.sh — resolve the directory a running service ACTUALLY runs from.
#
# Usage:
#   ./find-live-source.sh <port>
#   ./find-live-source.sh <port> <candidate-file>   # also diff-checks a candidate
#
# Exit codes: 0 resolved, 1 no listener found, 2 candidate mismatch warning.

set -uo pipefail

PORT="${1:-}"
CANDIDATE="${2:-}"

if [[ -z "$PORT" ]]; then
    echo "usage: $0 <port> [candidate-file]" >&2
    exit 1
fi

echo "=== Listener on port $PORT ==="
LISTENER="$(ss -lptn "sport = :$PORT" 2>/dev/null | tail -n +2)"
if [[ -z "$LISTENER" ]]; then
    echo "No listener found on port $PORT" >&2
    exit 1
fi
echo "$LISTENER"

# Extract the first pid from ss output: users:(("python3",pid=219465,fd=8))
PID="$(printf '%s' "$LISTENER" | grep -oP 'pid=\K[0-9]+' | head -1)"
if [[ -z "$PID" ]]; then
    echo "Could not parse pid from ss output; falling back to ps" >&2
    PID="$(ps aux | grep -i "$PORT" | grep -v grep | awk '{print $2}' | head -1)"
fi
[[ -z "$PID" ]] && { echo "No pid resolved" >&2; exit 1; }

echo
echo "=== PID $PID ==="
ps -p "$PID" -o pid,etime,cmd --no-headers 2>/dev/null

echo
echo "=== AUTHORITATIVE source directory (/proc/$PID/cwd) ==="
LIVE_DIR="$(readlink "/proc/$PID/cwd" 2>/dev/null)"
if [[ -z "$LIVE_DIR" ]]; then
    echo "Could not read /proc/$PID/cwd (permissions?)" >&2
    exit 1
fi
echo "$LIVE_DIR"

echo
echo "=== systemd unit (intent — may disagree with /proc) ==="
UNIT="$(systemctl list-units --type=service --no-legend 2>/dev/null \
        | awk '{print $1}' \
        | while read -r u; do
              if systemctl show "$u" -p MainPID --value 2>/dev/null | grep -qx "$PID"; then
                  echo "$u"; break
              fi
          done)"
if [[ -n "$UNIT" ]]; then
    echo "unit: $UNIT"
    systemctl show "$UNIT" -p WorkingDirectory -p ExecStart --value 2>/dev/null
    WD="$(systemctl show "$UNIT" -p WorkingDirectory --value 2>/dev/null)"
    if [[ -n "$WD" && "$WD" != "$LIVE_DIR" ]]; then
        echo "WARNING: unit WorkingDirectory ($WD) != running cwd ($LIVE_DIR)"
        echo "         trust /proc for what IS running; fix the unit before next restart"
    fi
else
    echo "(no matching systemd unit — likely started manually)"
fi

echo
echo "=== Other copies on disk (potential stale mirrors) ==="
BASENAME="$(basename "$LIVE_DIR")"
find /root /opt -maxdepth 5 -type d -name "$BASENAME" 2>/dev/null \
    | while read -r d; do
          if [[ "$d" == "$LIVE_DIR" ]]; then
              echo "  [LIVE]   $d"
          else
              echo "  [mirror] $d"
          fi
      done

RC=0
if [[ -n "$CANDIDATE" ]]; then
    echo
    echo "=== Candidate check ==="
    CAND_ABS="$(readlink -f "$CANDIDATE" 2>/dev/null)"
    echo "candidate: $CAND_ABS"
    if [[ "$CAND_ABS" == "$LIVE_DIR"/* ]]; then
        echo "OK — candidate is inside the live source directory"
    else
        echo "MISMATCH — candidate is NOT under $LIVE_DIR"
        echo "           you are about to edit a mirror; editing it ships nothing"
        RC=2
    fi
fi

echo
echo "=== Next steps ==="
echo "  1. cd $LIVE_DIR"
echo "  2. curl -s http://127.0.0.1:$PORT/status   # confirm file matches reality"
echo "  3. grep -n '<claimed-capability>' <file>   # verify assumptions before scoping"

exit $RC
