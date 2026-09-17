# Profile Integrity Verification

## Problem

After an update-triggered restart or system maintenance, agent gateways may fail to restart despite systemd units being "enabled". Common symptom: `systemctl status hermes-gateway-<agent>` shows `inactive (dead)` but `ps aux | grep hermes` shows no running gateway process for that agent. `last_run_at: null` persists in cron jobs.

## Diagnostic Steps

### 1. Confirm profile directory exists
```bash
ls -la ~/.hermes/profiles/<agent>/
```
Expected contents: `config.yaml`, `.env`, `auth.json`, `secrets/`, `logs/`, `sessions/`.

**Missing or empty profile** ⇒ gateway cannot start. Exit logs will show:
```
profile does not exist
profile dir deleted
```

### 2. Verify systemd unit reality
```bash
systemctl --user status hermes-gateway-<agent>
```
States:
- `active (running)` — healthy
- `inactive (dead)` with no recent PID — either never started or exited
- `failed` — inspect `journalctl -u hermes-gateway-<agent>` for reason

**Critical**: Even if `inactive (dead)`, a MANUAL gateway process might still exist via `ps`. That process is NOT managed by systemd and won't auto-restart.

### 3. Check for orphaned manual gateways
```bash
ps aux | grep 'hermes_cli.main --profile <agent>'
```
If a process exists but systemd shows inactive, it's a leftover manual gateway. Kill it:
```bash
kill -TERM <pid>  # or kill -9 if necessary
```
Then let systemd restart:
```bash
systemctl --user restart hermes-gateway-<agent>
```

### 4. Review update logs for recent restarts
```bash
# Most profiles have an update.log
tail -20 ~/.hermes/profiles/<agent>/logs/update.log
# Or check gateway.log for shutdown messages
grep -E "Shutdown|restart|update|exit" ~/.hermes/profiles/<agent>/logs/gateway.log | tail -10
```

Synchronous exits from multiple agents within milliseconds + gateway.log "update" chatter = **update-triggered restart** (normal). If they don't relaunch within 120s, profile deletion is likely.

## Recovery

**If profile directory is missing**:
- Restore from backup: `cp -r /backup/profiles/<agent> ~/.hermes/profiles/`
- Or recreate via `hermes init --profile <agent>` (loses all state & sessions)
- Ensure systemd unit is enabled: `systemctl --user enable --now hermes-gateway-<agent>`

**If profile exists but gateway won't start**:
```bash
# Watch real-time logs
tail -f ~/.hermes/profiles/<agent>/logs/gateway.log
# Then restart
systemctl --user restart hermes-gateway-<agent>
```

Common post-restart errors to fix in order:
1. **YAML syntax error** in `config.yaml` — validate with `python -c "import yaml; yaml.safe_load(open('config.yaml'))"`
2. **Missing secrets** — `secrets/` directory absent or key files empty
3. **Auth failures** — `auth.json` corrupted or `auth.lock` stale; remove lock if no other process running

## Prevention

- Set all gateways as systemd managed (`systemctl --user enable hermes-gateway-<agent>`)
- Never run manual `hermes gateway run` alongside systemd; use one management method
- Ensure profile directory has correct ownership (root:root, 700 perms typically)
- After any `hermes update`, verify all systemd units restart automatically within 2 minutes