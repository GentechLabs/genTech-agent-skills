---
name: gateway-silent-failure-recovery
description: Gateway up but agent silent — fix stale code, import errors.
version: 1.1.0
author: Gentech
license: Apache-2.0
category: devops
tags: [hermes, gateway, recovery, telegram, silent-failure, stale-code]
metadata:
  hermes:
    category: operations
    tags: [hermes, gateway, recovery, telegram, silent-failure, stale-code]
---

# Gateway Silent Failure Recovery

When a gateway process is up (visible in `ps aux`), connected to Telegram (`✓ telegram connected` in logs), but the agent **never replies** to messages in its group — the gateway is silently failing on every message. This skill covers diagnosis and recovery.

## When to Use

- User reports "agent isn't replying in group X"
- Gateway process is running but group is silent
- Gateway up and green on `/health` (and `/v1/models`) but agent turns are refused with 503 `gateway_draining` OR 429 `rate_limit_exceeded` / `Too many concurrent runs` — that is drain / pending-marker / concurrency territory, NOT stale code; use the drain-and-concurrency sections of the verify-after-every-action skill before running the stale-code procedure below
- Cron jobs to that group succeed but live replies never come

## Diagnostic order

### 1. Confirm bot owns the group (one command)

```bash
curl -s "https://api.telegram.org/bot<TOKEN>/getChat?chat_id=<GROUP_ID>" | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK:', d.get('ok'), '|', d.get('description',''))"
```

- `ok: true` → bot is in the group, proceed to step 2
- `ok: false, "bot was kicked"` → bot was removed — re-invite it
- `ok: false, "chat not found"` → wrong ID or never added

### 2. Check gateway logs for the smoking gun

```bash
tail -50 ${PROFILES_DIR}/<PROFILE>/logs/gateway.log | grep -E '(ERROR|Error handling message)'
# HTTP-surface symptoms (POST /v1/* refusals, 429s, 503s) live in agent.log, not gateway.log:
tail -50 ${PROFILES_DIR}/<PROFILE>/logs/agent.log | grep -a 'POST /v1/'
```

**The stale-code signature** — an import error that happens on every inbound message:
```
ERROR gateway.platforms.base: [Telegram] Error handling message: cannot import name '<X>' from 'tools'
```

This means the gateway process was started before a Hermes update that changed the `tools` module API. The running process has the old code in memory.

### 3. Verify the import works in current venv

```bash
${INSTALL_DIR}/venv/bin/python -c "from tools import <MISSING_NAME>; print('OK')"
```

- Prints `OK` → the import exists NOW, confirming stale code in the running gateway
- Fails with same error → the import genuinely doesn't exist (different problem — check Hermes version/installation)

### 4. Confirm gateway start time vs update time

```bash
ps -o lstart= -p <GATEWAY_PID>
```

If the gateway started before the Hermes update that changed the API, it has stale code.

## Fix: restart the gateway

```bash
# Kill the stale process
kill -9 <GATEWAY_PID>

# Restart via the unit's supervisor — on this fleet gateways are systemd USER units
# (journalctl shows systemd starting hermes-gateway-<profile>.service). A nohup-spawned
# gateway runs OUTSIDE systemd alongside the real unit and fights it for platform polling.
systemctl --user restart hermes-gateway-<PROFILE>.service
```

Verify after restart:
```bash
# Confirm the unit actually cycled (fresh ActiveEnterTimestamp, bumped NRestarts)
systemctl --user show hermes-gateway-<PROFILE>.service -p ActiveEnterTimestamp -p NRestarts
ps aux | grep '<PROFILE>.*gateway run' | grep -v grep

# Smoke test — send a test message to the group
curl -s -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": <GROUP_ID>, "text": "🔄 Gateway restarted — back online."}' | python3 -c "import sys,json; print('OK' if json.load(sys.stdin).get('ok') else 'FAIL')"
```

**An agent cannot restart its own unit — route the restart outside.** Restarting the unit an
agent session runs inside means SIGTERM'ing your own process; agent-side restart helpers refuse
that (correctly). A self-seat restart goes to an outside shell: a peer seat's terminal, the
desktop agent, or the user. (The updater-side mirror of this trap: it must skip its own unit and
record the skip in a dedicated `skipped: [reason]` field — never in the success list.)

To measure how long a wedged seat keeps refusing, run the timestamped poller
`scripts/recovery_watch.sh <host> <port> <profile> [max_polls] [interval_s]` — appends one line
per probe to `/tmp/<port>_recovery.log`, exits 0 the moment a POST is admitted, exit 1 if still
refusing after the last poll.

## Pitfalls

- **Don't trust process liveness alone.** A gateway can be running, connected, and polling Telegram successfully while silently crashing on every message — the process never exits, it just logs the error and moves on.
- **`from X import Y` vs `X.Y` access can mislead.** In Python, `from tools import slash_confirm` can succeed while `tools.slash_confirm` fails because the import path resolved through a submodule. Always test the exact import path from the error message.
- **Don't restart before confirming bot membership.** If the bot was kicked, restarting won't help — re-invite it first.
- **Multi-profile setups:** each profile runs its own gateway. When multiple gateways show the same error, they were likely all started before the same Hermes update.
- **Don't load-test a gateway from inside itself.** An in-flight agent turn already occupies a concurrency slot on that server; POSTing a burst of test turns to its own API doubles occupancy and can wedge the seat so every external request is refused with 429 while `/health` stays 200 — a state only a cross-shell restart clears. Probe one request at a time, and never through the seat's own turn path.

## Real case (Aug 9, 2026)

Two gateways (gizmo and gentech-treasury) started at 00:36. Hermes updated sometime after, changing the `tools` module. The main gentech gateway, started at 01:30, picked up the new code and worked fine. The two earlier gateways hit `cannot import name 'slash_confirm' from 'tools'` on every message until restarted at 21:50.
