# Operational Patterns: Transient vs Persistent Errors, Process Audits, and Cron Health

## Quick Decision Matrix

| Observation | Check | Conclusion |
|---|---|---|
| Process started <5 min ago | `ps -o lstart,etime -p <pid>` | Likely scheduled update or manual restart — correlate with update.log |
| Single isolated error with old session ID | Cross-reference error timestamp vs session ID date (e.g., `20260501_` in session_id) | Cleanup artifact, NOT current failure |
| Telegram "Bad Gateway" once, no recurrence | Scan last 100 lines of errors.log for duplicate pattern | Transient network blip — monitor only |
| Repeated same error ≥3 times in 10 min | Count occurrences in last 200 lines | Persistent failure — investigate root cause |
| "SessionDB — database or disk is full" | Check `/root` disk usage; check `df -h` | Resource exhaustion — immediate action required |
| No cron.log or brain-backup updates in 1h | Check file mtimes; verify `hermes cron list` shows active jobs | Orphaned or broken cron pipeline |

## Process Uptime & Restart Pattern Analysis

**Goal:** Distinguish crash loops from expected restarts (updates, maintenance).

```bash
# Step 1: Get PIDs and start times for all agent gateways
ps aux | grep hermes_cli.main | grep -E 'yoyo|dmob|desmond|gentech'

# Step 2: For each PID, extract start time and elapsed
ps -p <PID> -o lstart,etime,cmd
# Example output:
#   Sat May  2 00:55:16 2026   0:49  ... --profile dmob ...
#   Sat May  2 00:55:11 2026   0:37  ... --profile desmond ...
```

**Interpretation:**
- **All agents started within 1–2 min window** → Likely coordinated update or system restart (expected)
- **Single agent restarted alone, recently** → Possible crash; check errors.log around that time
- **Agent with uptime < 2 min AND multiple recent error entries** → probable crash loop
- **Agent with uptime > 1h steady** → healthy baseline

**When update-driven:** Confirm via `~/.hermes/profiles/<agent>/logs/update.log` — last entry should show successful completion.

## Transient vs Persistent Error Classification

### Transient (self-recovering, ignore unless Pattern repeats)
- **Telegram network errors**: `Bad Gateway`, `Network error (attempt 1/10)` — if followed by `polling resumed` within 30s → monitor, don't escalate
- **Rate limits**: `Flood control exceeded` with automatic retry → expected behavior under load
- **API 429**: `too many concurrent requests` with credential rotation → system handling it
- **Markdown parse fallback**: `MarkdownV2 parse failed, falling back to plain text` → non-fatal formatting degradation

### Persistent (requires action)
- **Repeated same error ≥3× in 10 min window** — e.g., `Model 'minimax/minimax-m2.5:free' not found` every cron run → misconfiguration
- **Credential exhaustion**: `credential pool: no available entries (all exhausted or empty)` — API key quota hit
- **SessionDB failures**: `Failed to initialize SessionDB — database or disk is full` — disk or DB issue
- **Invalid API key**: `401 — Your API key is invalid, blocked or out of funds` — immediate key rotation needed
- **FileNotFoundError**: `Failed to send media: File file not found` — broken path, needs path fix

### Stale/Cleanup Artifacts (safe to ignore)
- **Errors referencing old session IDs**: Look at session_id in brackets `[20260501_...]` when today is 2026-05-02 → post-restart session cleanup
- **Shutdown diagnostics**: `Shutdown diagnostic — other hermes processes running` during update restart → normal coordination message
- **Old error log entries** (pre-dating latest gateway restart) — review `gateway.log` for restart timestamp; errors before that are historical

## Cron Health Verification Beyond Registry

`hermes cron list` only shows registered jobs. Confirm they actually run:

### Method 1: brain-backup.log (most reliable)
```bash
# Each agent should have a brain-backup.log syncing from DMOB
ls -lt ~/.hermes/profiles/*/logs/brain-backup.log
# Last modified within expected cron interval (e.g., 1h for hourly job)?
```

### Method 2: job-specific output directories
```bash
# Check ~/.hermes/cron/output/ for recent files
find ~/.hermes/cron/output -type f -mmin -60
# Empty directory OR files older than expected interval → jobs not executing
```

### Method 3: session_search for cron markers
```bash
session_search "cron tick" --from "1 hour ago"
# Should see inbound cron message per active job
```

**If cron appears registered but not executing:**
1. Verify master gateway is running: `systemctl --user status hermes-gateway`
2. Check `~/.hermes/cron/jobs.json` for `profile: null` or `active: null` entries → orphaned
3. Rebuild registry: `hermes cron sync` or manual edit + gateway restart

## Gateway Log Connectivity Patterns

Telegram disconnects are normal; watch for:

| Pattern | Meaning | Action |
|---|---|---|
| `Connected to Telegram (polling mode)` → `Disconnected from Telegram` within 5 min | Routine reconnect (network, Telegram-side) | Monitor if frequent |
| `Telegram network error, scheduling reconnect: Bad Gateway` + `polling resumed` within 30s | Transient API gateway issue | OK |
| `Telegram flood control` with 15–30s waits | Rate limit hit — system backing off | OK; consider reducing message bursts |
| Repeated `ERROR gateway.run: Agent error in session…` with no `response ready` | Agent crash during turn | Investigate agent errors.log |
| `MarkdownV2 parse failed` repeated across many messages | Agent generating invalid Markdown | Patch agent formatting logic |

## Quick Health Checklist (per run)

- [ ] All 4 agent gateway processes present (`pgrep -f hermes_cli.main --profile <agent>`)
- [ ] No agent has >3 identical ERROR entries in last 50 lines of errors.log
- [ ] No agent with recent restart (<5 min) AND >5 errors in last 50 lines → crash loop suspected
- [ ] Telegram: last 24h shows only transient disconnects, no permanent `403/401` auth failures
- [ ] Disk usage <80% on `/` and `~/.hermes` partition
- [ ] Cron: brain-backup.log updated within expected interval; `hermes cron list` shows all jobs active
- [ ] No `SessionDB — database or disk is full` warnings in any errors.log
- [ ] No `No session matched` cascade errors (indicates session store corruption)

## False Positive Guardrails

- **Old session IDs in error brackets** → check if session_id date < today's date → skip
- **Single pre-restart error** → locate gateway restart time in gateway.log; ignore errors predating it
- **Isolated 404 from vision tool** → verify session ID; if old, ignore; if current, check image path
- **Warnings from title_generator** → if isolated and non-repeating, often non-critical
