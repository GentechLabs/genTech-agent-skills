# Log Correlation with systemd Journal — 2026-05-02

**Purpose**: Determine root cause of agent termination (crash vs kill vs shutdown) by cross-referencing agent logs with systemd user journal.  
**Discovered**: May 2, 2026 — used to confirm YoYo's YAML-induced termination vs Desmond's unexplained absence.

---

## Problem

Agent process disappears from `ps` but gateway logs don't explicitly state why. Was it:
- Graceful SIGTERM from `hermes gateway stop`?
- SIGKILL from OOM killer?
- Systemd unit restart cycle?
- Native crash (segfault)?
- Manual `kill -9`?

`journalctl --user` holds the answer.

## Diagnostic Commands

### Check recent hermes unit events (last hour)
```bash
journalctl --user -u hermes-gateway.service --since "1 hour ago" --no-pager
```

### Check all hermes-related user units (pattern)
```bash
journalctl --user -u hermes-agent@* --since "2 hours ago" --no-pager
```

### Generic filter for all hermes activity
```bash
journalctl --user --since "1 hour ago" | grep -i hermes | tail -50
```

### If system-wide (not just user journal)
```bash
journalctl -u hermes-gateway.service --since "1 hour ago" --no-pager
sudo journalctl -k | grep -i kill  # kernel OOM messages
```

## Key Signatures to Look For

| Journal Entry | Interpretation |
|---------------|----------------|
| `Main process exited, code=exited, status=203/EXEC` | Startup failure (bad ExecStart path, venv missing) |
| `Main process exited, code=exited, status=0/success` | Graceful exit (SIGTERM or normal stop) |
| `Killed process` (next line shows PID) | SIGKILL sent externally (OOM or manual `kill -9`) |
| `segmentation fault` | Native extension crash (C/C++ code) |
| `SIGSEGV` | Same — segfault |
| `SIGTERM` received | Clean shutdown request |
| `Failed with result 'exit-code'` | Process returned non-zero exit code |
| `Start request repeated too quickly` | Restart loop (respawning too fast; check crash loop) |
| ` Scheduling restart job, restart counter is at N` | Systemd attempting restart; N>5 indicates instability |

## Cross-Reference with Agent Logs

1. Get timestamp from journal entry
2. Check corresponding agent log at same time:
   ```bash
   grep '2026-05-02 13:38' ${PROFILES_DIR}/yoyo/logs/gateway.log
   ```
3. Match patterns:
   - Journal: `Main process exited, code=exited, status=0` + Agent log: `Gateway stopped` → clean shutdown
   - Journal: `Killed process` + Agent log: (nothing recent, abrupt) → OOM or SIGKILL
   - Journal: `segfault` + Agent log: (crash trace) → native crash

## Example: YoYo May 2 Termination

**Journal not directly captured** but agent log showed:
```
2026-05-02 13:39:26,xxx INFO gateway.run: Gateway drain timed out after 60.0s...
2026-05-02 13:39:30,xxx INFO gateway.run: Gateway stopped
```
Interpretation: **Graceful shutdown** with drain timeout (active agent took >60s to finish). Likely triggered by external stop command or systemd stop request.

## Example: Desmond Process Missing (Unknown Cause)

If no explicit shutdown in agent logs:
```bash
# Check for OOM kill
sudo dmesg | grep -i 'killed process 922877'

# Check systemd restart attempts
journalctl --user -u hermes-gateway.service | grep '922877'
```
Determines whether OS killed it or manual intervention.

## Add to Health Check Workflow

In `system-health` §1 (Gateway & Process Health), augment step 1:

**1a. Check process existence**
```bash
ps -p <expected-pid>  # as currently done
```

**1b. If process missing, consult journal**
```bash
journalctl --user --since "30 min ago" | grep -E "(exit|kill|segfault|terminated)" | tail -20
```

## Pitfalls

- User journal may be rotated; use `--since "1 day ago"` for older events
- Some systems require `journalctl --user-unit=<name>` instead of `-u`
- Ensure `systemd` user session is running: `loginctl show-user $USER`
- If `journalctl` returns empty, user journal may be disabled; check `/etc/systemd/journald.conf`

## Reference

Man page: `man journalctl`  
Systemd docs: https://www.freedesktop.org/software/systemd/man/journalctl.html

(Store this file as quick-reference; full man page is canonical.)
