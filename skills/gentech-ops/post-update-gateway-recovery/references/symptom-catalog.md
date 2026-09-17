# Post-Update Symptom Catalog

Known gateway-level failures observed after Hermes updates. The pattern is always the same: gateway started before update → holds stale code → crashes on next inbound message.

## Import Symbol Graveyard

Symbols known to have disappeared across Hermes versions:

| Symbol | Module | Version | Symptom |
|--------|--------|---------|---------|
| `slash_confirm` | `tools` | v0.20.0 (Aug 2026) | Every inbound message crashes, agent never replies |
| `send_message_tool` | `tools` | v0.20.0 (Aug 2026) | No-agent cron scripts can't deliver |
| `run_agent` | (top-level) | v0.20.0 (Aug 2026) | LLM-driven cron jobs fail to execute |

## Signature Log Pattern

```
2026-08-09 21:46:09,743 INFO hermes_plugins.telegram_platform.adapter: [Telegram] Flushing text batch agent:main:telegram:group:<id>:<user> (N chars)
2026-08-09 21:46:09,744 ERROR gateway.platforms.base: [Telegram] Error handling message: cannot import name '<symbol>' from 'tools' (${INSTALL_DIR}/venv/lib/python3.11/site-packages/tools/__init__.py)
```

The `Flushing text batch` line means the message WAS received. The `Error handling message` on the very next line means it was never processed.

## Double Gateway Log Signature

When systemd `Restart=on-failure` fires alongside a manual restart:

```
2026-08-09 21:50:34,565 ERROR gateway.run: Another gateway instance (PID 202109) started during our startup. Exiting to avoid double-running.
```

The first-started instance exits cleanly; the second one continues. Both may appear in `ps` briefly.

## Cron Breakage Patterns

No-agent scripts: `No module named 'tools.send_message_tool'`
→ Script runs fine but delivery to Telegram fails. Job status shows `ok` but delivery error is separate.

LLM-driven jobs: `No module named 'run_agent'`
→ Job status shows `error`. The agent never starts.

Both require the same fix: pause job, update script/prompt, re-enable.

## Detection One-Liner

```bash
# Find all gateways running stale code
for pid in $(pgrep -f 'gateway run'); do
  start=$(ps -o lstart= -p $pid 2>/dev/null)
  echo "PID $pid: $start — $(grep -c 'Error handling message' /proc/$pid/root/*/logs/gateway.log 2>/dev/null || echo 0) import errors"
done
```
