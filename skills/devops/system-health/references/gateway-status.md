# Hermes Gateway Status Verification

## Purpose
Verify each agent's gateway process is running, connected to its platforms (Telegram, etc.), and not in a degraded/stuck state.

## Quick Check
```bash
ps aux | grep hermes | grep 'gateway run'
```
Expected: one line per agent profile:
```
root  899631  ... python -m hermes_cli.main --profile yoyo gateway run --replace
root  899618  ... python -m hermes_cli.main --profile gentech gateway run --replace
root  899554  ... python -m hermes_cli.main --profile dmob gateway run --replace
root  899540  ... python -m hermes_cli.main --profile desmond gateway run --replace
```

## Detailed Status

**Gateway log location:**
```
${PROFILES_DIR}/<agent>/logs/gateway.log
```

**Check for connection indicators:**
```bash
tail -20 ${PROFILES_DIR}/<agent>/logs/gateway.log | grep -i "telegram\|connected\|disconnect\|polling"
```

**Healthy gateway shows:**
- `Telegram: connected` or `WebSocket connection established`
- `Polling for updates` (Telegram polling mode)
- Periodic `Ping/pong` or heartbeat messages

**Degraded gateway shows:**
- `Telegram: disconnected` with no reconnect
- `Read timeout` repeated errors
- `Flood wait` errors (rate limiting)
- `Auth key` errors → credentials invalid
- Process CPU at 0% for extended time → stuck
- Multiple gateway processes for same profile → zombie/duplicate

## Common Gateway States

| Observation | Meaning | Action |
|-------------|---------|--------|
| No gateway process | Agent down / not started | `hermes -p <agent> gateway start` |
| Multiple gateway processes for same profile | Stale process not cleaned up | Kill all, start fresh (`pkill -f "profile <agent>"`) |
| Gateway running but Telegram "disconnected" | Auth/network issue | Check `ELEVENLABS_API_KEY`, `TELEGRAM_BOT_TOKEN`, network |
| Gateway CPU 0% for >5min | Thread deadlock or infinite sleep | Check error log; restart gateway |
| Gateway memory growing continuously | Memory leak in loaded tools/skills | Restart gateway; report to dev team |

## Restart Procedures

**Safe restart (preserve sessions):**
```bash
hermes -p <agent> gateway restart
```

**Hard reset (kill + start):**
```bash
hermes -p <agent> gateway stop
sleep 2
hermes -p <agent> gateway start
```

**Systemd user service:**
```bash
systemctl --user restart hermes-gateway-<agent>
journalctl -u hermes-gateway-<agent> -f  # follow logs
```

## Platform-Specific Checks

**Telegram:**
- Bot token set in env (`TELEGRAM_BOT_TOKEN`)
- Chat ID configured correctly in deliver target
- No `403 Forbidden` → bot blocked by user or removed from group

**Slack/WhatsApp/Webhook:**
- Webhook URL reachable
-Bearer token valid (if authenticated)

## Troubleshooting Flow

1. Process exists? → No → Start it.
2. Process exists but CPU/memory 0? → Stuck → Check error log → restart.
3. Telegram disconnected? → Check credentials + network → fix → restart.
4. Repeated reconnects? → Rate limiting or IP ban → wait or rotate credentials.
5. Multiple processes? → Kill all → start single instance.

## Automation

Use this snippet in health checks:
```bash
for agent in gentech yoyo dmob desmond; do
  if pgrep -f "hermes.*--profile $agent.*gateway run" > /dev/null; then
    echo "$agent: UP"
  else
    echo "$agent: DOWN"
  fi
done
```

## Reference
- Hermes gateway docs: https://hermes-agent.nousresearch.com/docs/gateway
- Platform integrations: https://hermes-agent.nousresearch.com/docs/integrations
