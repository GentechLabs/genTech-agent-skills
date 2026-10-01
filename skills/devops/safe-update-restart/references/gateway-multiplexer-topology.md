# Gateway multiplexer topology — one unit, all seats

Some VPS hosts run a **single user-scope systemd unit** for all Hermes profiles instead of one
unit per profile. Restarting that unit takes every seat down at once, and scripts that still name
the retired per-profile units silently restart nothing.

## How to tell which topology a host uses

```bash
export XDG_RUNTIME_DIR=/run/user/0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/0/bus

# single multiplexer unit (new)
systemctl --user is-active hermes-gateway.service

# retired per-profile units (old)
for p in default gentech gentech-treasury gizmo pixel; do
  printf '%-22s %s\n' "$p" "$(systemctl --user is-active hermes-gateway-$p.service 2>/dev/null)"
done
```

Only one of these shapes can be live on a host. Do not assume based on which script you read last.

## Scope trap: `--user` units read as `inactive` from system scope

The gateway runs under the root user's `--user` manager. A bare `systemctl is-active
hermes-gateway.service` (system scope, the default for root) answers `inactive` even when the
gateway is perfectly healthy. Always set both environment variables when probing or restarting:

```bash
export XDG_RUNTIME_DIR=/run/user/0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/0/bus
systemctl --user is-active hermes-gateway.service
```

Scripts invoked from cron or from an automated session must pass these explicitly; cron has
neither variable by default.

## Liveness under the multiplexer

Per-profile `pgrep -f 'profile <seat> gateway run'` matches nothing — there is only one gateway
process. Read liveness from the gateway's own files instead:

| Source | Path | What it tells you |
|---|---|---|
| pid file | `/root/.hermes/gateway.pid` | JSON with `pid` and `start_time` (jiffies) |
| state file | `/root/.hermes/gateway_state.json` | `gateway_state`, `platforms` with per-seat bindings |

A robust liveness probe asserts:

1. the unit is `active`
2. the pid from `gateway.pid` is alive and its `/proc/<pid>/stat` start tick matches the file
   (catches pid reuse)
3. `gateway_state == running` and every platform is `connected`
4. the process did not start before the newest install source mtime (catches stale-code runs)

## Pitfalls

- **Script names retired units.** A script that loops `hermes-gateway-$seat.service` on a
  multiplexed host produces non-zero exit codes and restarts nothing. A loop that then checks
  `is-active` on the same retired units reports every seat as down, forever.
- **Restarting the single unit is fleet-wide.** Rule 7c applies to the whole host. Get checkpoint
  ACKs from every VPS seat first.
- **Per-platform state lives in one JSON file.** A disconnected `gentech-treasury:telegram` binding
  is a real problem even though the systemd unit still says `active`.

## Related

- `gateway-unit-vs-process-desync.md` — when unit state and process state disagree
- `fleet-update-self-kill.md` — how the fleet updater must survive its own restart
- The main SKILL.md — safe-update-restart procedure and checkpoint protocol
