#!/bin/bash
# recovery_watch.sh — measure how long a wedged Hermes API-server seat keeps refusing POSTs.
# One probe per interval, timestamped, appended to /tmp/<port>_recovery.log so the wedge's
# duration is MEASURED, not guessed. Exits 0 the moment a POST is admitted; exit 1 if still
# refusing after the last poll (restart required from OUTSIDE the seat).
#
# Usage: recovery_watch.sh <host> <port> <profile> [max_polls=40] [interval_s=60]
#   e.g. recovery_watch.sh 100.126.236.51 8642 gentech 40 60
#
# Notes:
# - Safe to run from the wedged seat itself: refused probes occupy no run slot. Once the seat
#   recovers, each successful probe briefly occupies one — keep interval >= 60s.
# - Probes POST /v1/chat/completions deliberately: GET /health stays 200 on a wedged seat and
#   proves nothing about admission.

HOST=${1:?host}; PORT=${2:?port}; PROFILE=${3:?profile}
MAX=${4:-40}; INTERVAL=${5:-60}
KEY=$(python3 -c "import yaml;print(yaml.safe_load(open('/root/.hermes/profiles/'$PROFILE'/config.yaml'))['gateway']['api_server']['key'])")
LOG=/tmp/${PORT}_recovery.log
: > "$LOG"
START=$(date +%s)
echo "$(date -u +%H:%M:%S) watch started (POST /v1/chat/completions every ${INTERVAL}s)" >> "$LOG"
for i in $(seq 1 "$MAX"); do
  C=$(curl -s -o /tmp/rw_body.txt -w '%{http_code}' -m 30 -X POST "http://$HOST:$PORT/v1/chat/completions" \
      -H 'Content-Type: application/json' -H "Authorization: Bearer $KEY" \
      -d '{"model":"hermes","messages":[{"role":"user","content":"say READY"}],"max_tokens":8}')
  EL=$(( $(date +%s) - START ))
  echo "$(date -u +%H:%M:%S) t+${EL}s attempt=$i code=$C $(head -c 60 /tmp/rw_body.txt | tr -d '\n')" >> "$LOG"
  if [ "$C" = "200" ]; then
    echo "RECOVERED at t+${EL}s (attempt $i)"
    exit 0
  fi
  sleep "$INTERVAL"
done
echo "STILL REFUSING after $MAX polls / $(( $(date +%s) - START ))s — needs restart from OUTSIDE the seat"
exit 1
