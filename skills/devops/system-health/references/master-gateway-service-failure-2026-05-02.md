# Session Reference: Master Gateway Service Failure (hermes-gateway.service)
**Date detected:** April 27 – May 2, 2026  
**Profiles affected:** Gentech, YoYo, DMOB, Desmond (fleet-wide)  
**Skill: system-health §3i — Master Gateway Service Failure (Systemd)**

## Symptom Summary

- `systemctl --user status hermes-gateway.service` → `Active: failed (Result: exit-code) since Mon 2026-04-27 22:18:36 UTC; 4 days ago`
- Exit code `203/EXEC` (executable path failure)
- `journalctl` output: `Main process exited, code=exited, status=203/EXEC` followed by `Failed with result 'exit-code'`
- All cron jobs across ALL agents show `last_run_at: null` (never executed)
- `/root/.hermes/cron/output/` directory empty for >24h
- Agent gateways individually running (Gentech) or stopped (YoYo/DMOB/Desmond) but **no cron dispatch occurring**

## Root Cause

Systemd unit file `/root/.config/systemd/user/hermes-gateway.service` contained incorrect `ExecStart` path:

```
ExecStart=/root/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main ...
```

Path did not exist. Correct path is:

```
ExecStart=${INSTALL_DIR}/venv/bin/python -m hermes_cli.main ...
```

## Impact Scope

This service is the **global cron dispatcher** Daemon. When it fails:
- No scheduled job executions across any profile
- Individual agent gateways may run (accepting Telegram messages) but cron ticker does not fire
- `hermes cron status` reports daemon not running even if gateways appear up
- Jobs sit in `jobs.json` indefinitely with `next_run_at` advancing but never triggering

## Detection Checklist

```bash
# 1. Check systemd status
systemctl --user status hermes-gateway.service --no-pager

# 2. Inspect ExecStart path
grep ExecStart /root/.config/systemd/user/hermes-gateway.service

# 3. Verify Python venv exists at expected location
ls -la ${INSTALL_DIR}/venv/bin/python

# 4. Query cron daemon state
hermes cron status  # should say "daemon running" — if not, master service down

# 5. Check cron output age
find /root/.hermes/cron/output -type f -mmin -60 | wc -l  # should be ≥1 if healthy
```

**Key insight**: Always check master service FIRST when all agents report cron starvation. Individual gateway health is secondary if the global cron dispatcher is down.

## Recovery Steps

1. Edit unit file: `sudo nano /root/.config/systemd/user/hermes-gateway.service`
2. Replace incorrect `ExecStart` line:

   ```
   ExecStart=${INSTALL_DIR}/venv/bin/python -m hermes_cli.main --profile gentech cron-daemon
   ```

   (Profile choice determines default for unbound jobs; `gentech` is typical)

3. Reload systemd user manager: `systemctl --user daemon-reload`
4. Start service: `systemctl --user start hermes-gateway.service`
5. Verify: `systemctl --user status hermes-gateway.service` → `Active: active (running)`
6. Confirm cron flights: `hermes cron list --json | python3 -c "import json,sys; print(min(j.get('last_run_at') for j in json.load(sys.stdin)['jobs'] if j.get('last_run_at')))"` — should be within last hour
7. Restart all agent gateways to refresh their cron daemon connections:
   ```bash
   systemctl --user restart hermes-gateway-yoyo.service
   systemctl --user restart hermes-gateway-dmob.service
   systemctl --user restart hermes-gateway-desmond.service
   systemctl --user restart hermes-gateway-gentech.service
   ```

## Prevention Notes

- Deployments that touch `${INSTALL_DIR}/` may overwrite venv path; verify systemd unit after updates
- Document correct venv path in deployment runbook: `${INSTALL_DIR}/venv/bin/python`
- Consider adding a health-check cron that runs `systemctl --user is-active hermes-gateway.service` and alerts on non-active status
- Monitor `/root/.hermes/cron/output/` file creation rate; stall >2× max schedule interval = incident

## Related Patterns

- **Cron job orphaning** (`system-health §3c`) — jobs with `profile: null` never loaded even if master service is up
- **CLI cache divergence** (`system-health §1`) — `hermes gateway status` may show stale PID; cross-check with `ps`
- **Gateway restart bypass** (`system-health §3k`) — `Restart=on-failure` won't revive clean exits; manual intervention needed if master service itself exits cleanly

## Session Evidence

```
May 02 06:55 Watchdog run #1 detected: `systemctl --user status hermes-gateway.service` → failed since Apr 27, exit 203/EXEC
May 02 09:45 Watchdog run #2 confirmed: ExecStart path mismatch verified via `cat` of unit file
May 02 16:10 Live check: service still failed; all cron jobs `last_run_at: null`
```

**Resolution status (as of May 2 19:22 UTC):** Unresolved — manual fix required.
