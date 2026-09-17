# Cron Registry Corruption — `jobs.db` Zero-Byte Recovery

## Symptom

- `hermes cron list` shows jobs but `last_run_at: null` for all entries
- `~/.hermes/cron/output/` is empty or stale
- Cron logs show "cron ticker started" but no dispatch messages
- `~/.hermes/cron/jobs.db` filesize is **0 bytes**

## Root Cause

The SQLite active job registry (`jobs.db`) is unreadable, typically due to:
- Abrupt shutdown during write (power loss, SIGKILL during cron dispatch)
- Disk pressure causing write truncation
- Manual deletion or corruption during cleanup

## Diagnosis

```bash
# Check registry size
ls -lh ~/.hermes/cron/jobs.db
# If 0 bytes → corrupted

# Try reading raw SQLite
sqlite3 ~/.hermes/cron/jobs.db ".tables"
# Likely error: "file is not a database"

# Cross-check source-of-truth
cat ~/.hermes/cron/jobs.json | jq '.jobs | length'
```

`jobs.json` is the canonical definition file. `jobs.db` is the runtime registry built from it at daemon start.

## Recovery Sequence

### 1. Stop cron dispatcher
If a hermes cron daemon is running:
```bash
# Find cron subprocess (spawned by gateways)
ps aux | grep hermes | grep -i cron
# Kill gracefully; gateways will respawn with fresh registry
kill -TERM <pid>
```
If no standalone daemon, gateways will rebuild automatically on next tick.

### 2. Rebuild registry from source-of-truth
```bash
# Remove corrupted db
rm ~/.hermes/cron/jobs.db

# Force gateway restart (any agent gateway rebuilds registry on tick)
systemctl --user restart hermes-gateway-gentech  # or any running agent
```

The gateway's embedded cron ticker:
1. Detects missing/invalid `jobs.db`
2. Reads `jobs.json`
3. Recreates SQLite registry with all enabled jobs
4. Resets `last_run_at` / `last_status` to null (historical runs lost, but schedule restarts)

### 3. Verify rebuild
```bash
# Wait 60s for first tick, then:
hermes cron list  # should show all jobs with next_run_at populated
ls -lh ~/.hermes/cron/jobs.db  # now > 0 bytes
```

If `jobs.db` remains 0 bytes after restart, `jobs.json` may be malformed. Validate:
```bash
python -c "import json; json.load(open('~/.hermes/cron/jobs.json'))"
```

## Preventative Measures

- Enable cron daemon resilience: set `StartLimitBurst` high enough in systemd units (already configured)
- Monitor `jobs.db` health: alert if size < 100 bytes
- Regular brain backups: `~/.hermes/cron/output/` and `~/.hermes/sessions/` periodic snapshots