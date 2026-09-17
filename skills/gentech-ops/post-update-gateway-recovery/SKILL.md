---
name: post-update-gateway-recovery
description: Use when gateways fail after Hermes update. Detect, restart.
category: devops
tags: [hermes, update, gateway, recovery, telegram, cron]
---

# Post-Update Gateway Recovery

After a Hermes update, running gateways hold stale pre-update code in memory. They crash on inbound messages with import errors until restarted. Covers detection, safe restart, and cleanup across a multi-profile fleet.

## When to Use

- Multiple agents stop replying simultaneously after an update
- Gateway logs show `ImportError` / `AttributeError` near `Flushing text batch`
- Cron jobs fail with `No module named` errors after an update
- Double gateway processes detected after attempted restarts

## Diagnostic Order

### 1. Check for stale gateways

```bash
for pid in $(ps aux | grep 'gateway run' | grep -v grep | awk '{print $2}'); do
  echo "PID $pid started: $(ps -o lstart= -p $pid)"
done
hermes --version
```

Any gateway started BEFORE the install date has stale code.

### 2. Scan for import errors

```bash
grep -E '(ImportError|AttributeError|cannot import|No module named)' <profile>/logs/gateway.log | tail -20
```

The signature: `Flushing text batch` then `Error handling message: cannot import name '<symbol>' from 'tools'`.

### 3. Check for double gateways

```bash
ps aux | grep '<profile>.*gateway run' | grep -v grep
```

Two instances = systemd `Restart=on-failure` spawned alongside a manual restart.

### 4. Check for post-update cron breakage

```bash
hermes --profile <name> cron list | grep -B1 'error:'
```

## Fix: Stale Gateway Restart

1. Identify the owning profile (see `telegram-group-ownership-diagnostic`)
2. Kill: `kill <pid>` (use `-9` if needed)
3. Restart: `hermes --profile <name> gateway run` (or let systemd handle it)
4. Verify: `tail -10 <profile>/logs/gateway.log` — look for `✓ telegram connected`
5. Smoke test with a direct API send to the group

## Fix: Double Gateway

1. Identify systemd-managed (parent PID = 1) vs nohup instance
2. Kill the nohup one: `kill <nohup_pid>`
3. Verify: `ps aux | grep '<profile>.*gateway run' | grep -v grep | wc -l` → 1

## Planned Bounce with Queued Fixes (fleet model/provider changes)

A running gateway serves the model/fallback chain it read at STARTUP — config edits on disk
(`model`, `fallback_model`, `fallback_providers`) do not reach a live gateway until restart.
When a fix requires bouncing shared gateways:

1. **Apply every fix on every affected profile FIRST.** Before bouncing, sweep for anything
   else that would force a second restart (cron pins, delegation config, aux slots). List-valued
   keys (e.g. `fallback_providers`) don't round-trip through `config set` — edit the yaml
   directly, then re-parse it to prove the file still loads.
2. **Collect a READY ACK from each affected agent** (peer DM to wake them): nothing
   state-changing mid-flight, bounce is clear. Then restart ONCE.
3. **Verify serving end-to-end, not the registry.** `/v1/models` lists the gateway REGISTRY,
   not which upstream the fallback rides. Fire one minimal live chat completion and read the
   `model` field of the response (and note the absence of fallback warnings). A structured
   401 to a dummy key is itself a liveness proof — a dead gateway times out instead of erroring.
4. Sequential fix→restart→fix cycles multiply downtime and re-verification — batch fixes,
   one bounce, one verification pass.

## Fix: Post-Update Cron Breakage

Common failures: `No module named 'tools.send_message_tool'`, `No module named 'run_agent'`.

Pause broken jobs immediately:
```bash
hermes --profile <name> cron pause <job_id>
```

## Pitfalls

- Don't restart gateways blindly — verify group ownership first
- systemd `Restart=on-failure` creates ghost double-instances on manual restart
- Main profile gateway may be fine (started post-update) while workers are stale
- Import errors are silent — messages received, never answered
- `from tools import X` working interactively does NOT mean the running gateway has it
