# Telegram Flood Control Warnings — 2026-05-02

**Agent**: Gentech (observed), others may occur  
**Pattern**: `[Telegram] Telegram flood control on send (attempt 1/3), retrying in Xs`  
**Frequency**: Multiple consecutive warnings with 14–17 second backoffs  
**Discovery**: May 2, 2026 watchdog health check via gateway.log inspection

---

## Symptom Excerpt

```
2026-05-02 13:24:39,238 WARNING gateway.platforms.telegram: [Telegram] Telegram flood control on send (attempt 1/3), retrying in 14.0s: Flood control exceeded. Retry in 14 seconds
2026-05-02 13:24:53,468 WARNING gateway.platforms.telegram: [Telegram] Telegram flood control on send (attempt 1/3), retrying in 3.0s: Flood control exceeded. Retry in 3 seconds
2026-05-02 13:25:37,745 WARNING gateway.platforms.telegram: [Telegram] Telegram flood control on send (attempt 1/3), retrying in 16.0s: Flood control exceeded. Retry in 16 seconds
```

**Backoff times**: 14s → 3s → 16s (non-linear; Telegram server dictates)

## Root Cause

Telegram bot exceeded per-chat rate limit (~30 messages/second per bot per chat). Multiple factors can trigger:

- Several cron jobs executing simultaneously and all sending to same Telegram group
- Job itself generates many small messages instead of consolidated response
- No throttling between consecutive job runs
- Multiple agents sharing same bot token posting to same chat

## Diagnostic

### Check frequency of Telegram sends
```bash
grep 'Sending response' ${PROFILES_DIR}/gentech/logs/gateway.log | wc -l
# If >50 in last 5 minutes → rate limit likely
```

### Check for overlapping job schedules
```bash
for agent in yoyo dmob desmond gentech; do
  echo "=== $agent cron schedule ==="
  python3 -c "import json; data=json.load(open('${PROFILES_DIR}/$agent/cron/jobs.json'));
  [print(f\"{j['name'][:50]:<50} {j.get('schedule','?')}\") for j in data.get('jobs',[])]"
done
```

Look for jobs with `*/1 * * * *` (every minute) or sub-minute intervals targeting same chat.

## Mitigation Strategies

### 1. Stagger job schedules
Instead of:
```
*/5 * * * *  # Every 5 minutes (5 agents → burst at :00, :05, etc)
```
Use offsets:
```
*/5 * * * *   # Agent A at :00
2-59/5 * * * *  # Agent B at :02, :07, ...
4-59/5 * * * *  # Agent C at :04, :09, ...
```
Or set explicit times:
```
0,15,30,45 * * * *   # Every 15 minutes at quarter-past
3,18,33,48 * * * *   # Offset by 3 minutes
```

### 2. Consolidate messages
If job logic permits, batch multiple updates into single Telegram message instead of several small ones.

### 3. Respect backoff automatically
Gateway already implements exponential retry. **Do not disable flood control** — it protects bot from temporary ban.

### 4. Pause lower-priority jobs during peak activity
```bash
hermes cron pause <job-id>
# Resumes manually or after TTL
```

### 5. Use multiple bot tokens for high-volume setups
If bot must send 100+ messages/hour to same chat, consider:
- Two bots with different tokens, same chat
- Or split chat groups by agent/department

## Recovery

Flood control is **self-correcting**:
- Gateway automatically retries with increasing delays (13s → 31s → etc)
- After ~10–15 minutes of no sends, Telegram resets counter
- If stuck in flood-control loop for >20 min with no successful send, restart gateway to clear retry state:
  ```bash
  hermes gateway restart --profile <agent>
  ```

## Monitoring

Add to regular health checks (§1 of `system-health`):
```bash
# Detect agents in flood-control state
for agent in yoyo dmob desmond gentech; do
  count=$(grep -c 'flood control on send' ${PROFILES_DIR}/$agent/logs/gateway.log | tail -1)
  if [ "$count" -gt 10 ]; then
    echo "WARNING: $agent has $count flood-control warnings in recent history"
  fi
done
```

## Related

- `system-health` §3h (Telegram Flood Control & Rate Limiting)
- Telegram Bot API docs: https://core.telegram.org/bots/api#response-parameters
