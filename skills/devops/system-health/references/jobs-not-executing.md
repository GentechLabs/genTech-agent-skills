# Cron Jobs Never Executing — Hermes Internal Scheduler Failure

## Symptom
Jobs in `/root/.hermes/cron/jobs.json` never fire:
- `last_run_at: null` even after scheduled time has passed
- `hermes cron status` says "Gateway is running — cron jobs will fire automatically" but no actual dispatch
- `/root/.hermes/cron/output/` directory remains empty
- No job-related entries in `agent.log` beyond "Cron ticker started"

**Example** (May 2, 2026):
All 4 jobs created Apr 30 never executed:
- Desmond — Creative Sync (ID: 64cfa447b338) — schedule `0 7,19 * * *`
- Gentech — HQ Daily Update (ID: c578000c1d4a) — schedule `0 9 * * *`
- YoYo — LP Watchlist Check (ID: a47474bb0f0c) — schedule `0 6,12,18 * * *`
- DMOB — Labs Daily Standup (ID: ec74c26ad123) — schedule `0 8,20 * * *`

## Root Causes (in order of likelihood)

1. **Scheduler thread deadlocked** — Gateway process running but internal asyncio/threading blocked on I/O (e.g., SessionDB disk-full warnings, network hang)
2. **Cron mode set to 'deny'** — `config.yaml` has `cron_mode: deny` (found at line 350 in one config); this disables job execution while allowing ticker to run
3. **Credential pool empty** — Job requires a provider with no available API keys; scheduler silently skips dispatch
4. **Job execution errors swallowed** — Job starts but crashes immediately before log flush; check `cron_job_<id>.log` in output/ (often empty on early failure)
5. **Time sync issues** — System clock jumps cause "next_run_at" never reached; verify with `date` and NTP

## Investigation Steps

**Step 1 — Confirm ticker is alive:**
```bash
# All gateways should log this on startup
grep "Cron ticker started" ${PROFILES_DIR}/*/logs/gateway.log
```
If ticker messages present but no job logs → ticker running, scheduler blocked.

**Step 2 — Force a manual tick:**
```bash
hermes cron tick
```
- If jobs run now → ticker was waiting for schedule; check system time/cron expression
- If still silent → scheduler is deadlocked or jobs filtered out

**Step 3 — Check Hermes cron list state:**
```bash
hermes cron list
```
Look at each job's `state` (should be `scheduled` or `active`) and `enabled: true`. Jobs in `paused` state won't run.

**Step 4 — Inspect config:**
```bash
grep -E 'cron_mode|cron:' /root/.hermes/config.yaml
```
If `cron_mode: deny` → change to `allow` or remove line. Restart gateways.

**Step 5 — Check for blocking errors in agent logs:**
```bash
grep -i "sessiondb\|disk full\|credential pool" ${PROFILES_DIR}/*/logs/agent.log
```
Disk-full or credential exhaustion can prevent job initialization.

**Step 6 — Verify provider credentials:**
If job specifies `model: anthropic/claude-3` but no `ANTHROPIC_API_KEY` → job fails immediately before dispatch in some versions. Pre-populate credential pool or set env vars.

**Step 7 — Enable debug logging:**
Set `HERMES_LOG_LEVEL=DEBUG` in gateway environment; restart. Watch for `cron.scheduler` debug lines showing job evaluation cycle.

## Fixes

**Scheduler deadlock** → Restart all gateways (order doesn't matter):
```bash
for agent in gentech yoyo dmob desmond; do
  hermes -p $agent gateway stop
  hermes -p $agent gateway start
done
```

**Cron mode deny** → Edit config, set `cron_mode: allow` or remove key; restart gateways.

**Missing credentials** → Set environment variables for required providers (Anthropic, OpenAI, ElevenLabs, etc.) in each agent's systemd service or shell environment.

**Time sync** → Install and enable NTP:
```bash
timedatectl set-ntp true
```

## Verification
After fix:
```bash
hermes cron list  # next_run_at should be in near future
hermes cron tick   # manual trigger should produce output in cron/output/
ls -lt /root/.hermes/cron/output/  # see recent job output files
```

Check agent logs for `cron.scheduler: Running job '<name>'` and `Job '<name>': completed` messages.

## Related Patterns
- Single job running but others not: check job-specific `schedule` expressions for past-due next_run that won't re-trigger until corrected
- Gateway restarts resetting internal cron state: ensure `state` in jobs.json not corrupted
- Multiple gateways: Hermes embeds cron in gateway, not separate process; having gateway down for an agent pauses that agent's job execution

