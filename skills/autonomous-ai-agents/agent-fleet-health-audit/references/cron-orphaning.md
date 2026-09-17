# Cron Job Orphaning — Why Jobs Disappear from the Active Registry

## Symptom
Job defined in `~/.hermes/cron/jobs.json` but `hermes cron list` shows it as:
- Not present at all, OR
- Present with `profile: None`, `active: None`, `last_run_at: null`

**Examples from this session:**
```json
{
  "name": "YoYo — LP Watchlist Check",
  "profile": null,
  "active": null,
  "last_run_at": null
}
```

## Why This Happens

1. **Jobs JSON is source-of-truth but not auto-loaded** — The Hermes cron system reads `jobs.json` at service start. If `hermes-gateway.service` is failed or the process hasn't been restarted after jobs.json changes, new jobs remain orphaned.

2. **Profile assignment missing** — Each job must reference a valid profile ID. `profile: null` means the job was created without a `--profile` flag or the profile was deleted.

3. **Scheduler pipeline blocked** — If the master `hermes-gateway.service` is down, even valid jobs can't be dispatched; they appear inactive.

4. **Registry cache corruption** — The cron registry (in-memory or SQLite) can desync from `jobs.json` after a crash.

## Diagnosis Checklist

- [ ] `grep -A5 "<job name>" ~/.hermes/cron/jobs.json` — does `profile` field contain a valid profile name (e.g., `yoyo`, `dmob`)?
- [ ] `hermes cron list` — is the job visible? Does it show `[active]`?
- [ ] `systemctl --user status hermes-gateway.service` — is the master service running?
- [ ] `ps aux | grep hermes_cli.main` — are agent gateway processes alive?

## Revival Procedure

### Case A — Master service down (systemic)
1. Fix `hermes-gateway.service` ExecStart path if incorrect
2. `systemctl --user daemon-reload && systemctl --user start hermes-gateway.service`
3. Wait 10s; re-check `hermes cron list` — job should appear active

### Case B — Job has `profile: null`
1. Identify correct profile name from `~/.hermes/profiles/` or vault `team-roster.md`
2. Edit `~/.hermes/cron/jobs.json` to set `"profile": "desired-profile"`
3. Restart master service: `systemctl --user restart hermes-gateway.service`

### Case C — Job not in jobs.json at all
```bash
hermes cron add --name "Agent — Task" --schedule "0 6 * * *" --profile <agent>
```

### Case D — Registry cache corrupted
```bash
# Stop all gateways, delete cron DB, restart master
systemctl --user stop hermes-gateway.service
rm -f ~/.hermes/cron/jobs.db
systemctl --user start hermes-gateway.service
```

## Validation
After recovery:
```bash
hermes cron list | grep -A3 "<job name>"
# Should show:
#   <job-id> [active]
#     Name:      ...
#     Schedule:  ...
#     Last run:  <timestamp> ok
```

## Prevention
- Always create cron jobs with explicit `--profile` flag
- After adding jobs to `jobs.json` manually, run `systemctl --user restart hermes-gateway.service`
- Monitor `hermes cron list` in periodic health audits (see `agent-fleet-health-audit` skill)
