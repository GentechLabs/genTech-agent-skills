---
name: agent-health-monitoring
description: System health checks for Hermes multi-agent deployments — gateway status, error log analysis, cron job execution verification, and failure pattern detection
triggers:
  - keyword: health check
  - keyword: watchdog
  - keyword: agent status
  - keyword: cron check
  - keyword: system health
  - context: multiple-agent monitoring
outputs:
  - Gateway status per agent (up/down)
  - Error pattern counts with locations
  - Cron job execution status (last run timestamps)
  - Silently return OK if no issues found
---

# Agent Health Monitoring

Systematic health checks for Hermes Agent deployments across multiple profiles. Use this skill to diagnose operational issues, verify scheduled job execution, and detect degradation patterns before they cause outages.

## When to Use

- Daily/weekly system health audits
- After agent restarts or deployments
- When users report missed notifications or failures
- Investigating performance degradation
- Cron jobs not firing as expected

## Quick Check Sequence

**1. Gateway Process Status**
```bash
ps aux | grep hermes | grep 'gateway run'
```
Confirm each agent (gentech, yoyo, dmob, desmond) has a running gateway process. Should see one `python -m hermes_cli.main --profile <agent> gateway run --replace` per agent.

**2. Agent Log Freshness Check**
```bash
for agent in gentech yoyo dmob desmond; do
  log="${PROFILES_DIR}/$agent/logs/agent.log"
  if [ -f "$log" ]; then
    age=$(( ( $(date +%s) - $(stat -c %Y "$log") ) / 60 ))
    echo "$agent: last updated ${age}min ago"
  fi
done
```
**Why**: A running gateway process doesn't guarantee it's actively processing. Check log file modification timestamps to confirm recent activity (<5min = fresh, 5-30min = stale, >30min = inactive). Missing log files indicate profile corruption or misconfigured log paths.

**3. Error Log Scan (last 50 lines)**
```bash
tail -50 ${PROFILES_DIR}/<agent>/logs/errors.log
```
Look for:
- `EOFError: marshal data too short` → corrupted Python bytecode (.pyc)
- `status_code: 401` → API credential invalid/expired (ElevenLabs, etc.)
- `database or disk is full` → disk space issue
- `Connection error` → network/service outage
- `Refresh session has been revoked` → stale auth token

**4. Cron Job Execution Check**
```bash
cat /root/.hermes/cron/jobs.json | jq '.jobs[] | {id, name, last_run_at, state}'
```
Any job with `last_run_at: null` has never executed. Compare `created_at` to current time to see how long it's been stuck.

**5. Cron Ticker Verification**
```bash
hermes cron status
```
Should report "Gateway is running — cron jobs will fire automatically" and show the gateway PIDs. If gateway is running but ticker inactive → internal scheduler deadlocked.

**6. Sandbox/Runaway Task Detection**
```bash
ps aux --sort=-%cpu | grep 'python /tmp/hermes_sandbox' | grep -v grep
```
**Why**: Individual sandbox tasks can consume excessive CPU without affecting gateway processes. Flag any sandbox process with >50% CPU for >3min as a potential infinite loop or stuck computation. These do not self-terminate and must be killed manually.
**Red flags**:
- Single sandbox process using 70%+ CPU for 5+ consecutive minutes
- Multiple sandbox processes from same agent running simultaneously (should be serial)
- Sandbox elapsed time shows unreasonibly high values (e.g., "29628027 min") indicating process clock corruption or zombie state
**Fix**: `kill -9 <PID>` followed by agent gateway restart if new sandbox tasks fail to spawn cleanly.

## Error Pattern Reference\n\n### 2026-05-02 Watchdog Findings\n**YoYo & Gentech shared jobs** — April 30 empty response cascade:\n- 12 jobs failed with: `Agent completed but produced empty response (model error, timeout, or misconfiguration)`\n- Pattern: Cluster around 03:00–09:00 UTC window; likely upstream provider/model outage\n- Affects YoYo directly and Gentech through shared job ownership (9ecfada01952 is Gentech Watchdog itself)\n\n**DMOB auth errors** — April 22–24:\n- `RuntimeError: Refresh session has been revoked` → run `hermes model` to re-authenticate\n- `RuntimeError: No Anthropic credentials found` → set ANTHROPIC_TOKEN/ANTHROPIC_API_KEY or run `claude /login`\n\n**Data source**: `/tmp/cron_health.txt` combined with ownership mapping from `yoyo_cron.txt`, `dmob_cron.txt`, `desmond_cron.txt`, `gentech_cron.txt`\n\n### Corrupted Python Bytecode (marshal data too short)

**Symptom**: Repeated `EOFError: marshal data too short` tracebacks in agent logs during session_search, summarization, or any module import. Traceback stack shows failure in `importlib._bootstrap_external` while reading bytecode. Errors persist even with `python -B` (bytecode cache disabled) if the corrupted module is already in memory.

**Detection**:
```bash
# Scan for corrupted .pyc files — header source size field shows unrealistic values (e.g., gigabytes)
python3 -c "
import struct, glob
for pyc in glob.glob('${INSTALL_DIR}/**/__pycache__/*.pyc', recursive=True):
    with open(pyc,'rb') as f: h=f.read(16)
    if len(h)>=16:
        sz=struct.unpack('<I',h[8:12])[0]
        if sz > 50_000_000: print(f'{pyc}: header_source_size={sz}')
"
```
**Indicators**:
- `.pyc` file size looks reasonable (5–50 KB) but header's recorded source size is enormous (≥1 GB)
- Direct `.py` import works, but normal Python path import fails with `marshal data too short`
- Multiple modules affected simultaneously across `agent/` and `tools/` packages

**Root causes**:
- Filesystem interruption during `.pyc` write (power loss, disk full, NFS hiccup)
- Concurrent compilation race (multiple processes compiling same module)
- Disk corruption or bad sectors
- Antivirus/security tool interfering with writes
- Abrupt process termination during bytecode serialization

**Immediate remediation**:
```bash
# 1. Clear corrupted bytecode cache (system-wide install)
rm -rf ${INSTALL_DIR}/agent/__pycache__
rm -rf ${INSTALL_DIR}/tools/__pycache__

# (or agent-specific profile path if using per-profile install)
rm -rf ~/.hermes/profiles/<agent>/__pycache__

# 2. Verify clean imports in a fresh interpreter
python3 -c "from agent.copilot_acp_client import CopilotACPClient; print('OK')"

# 3. Restart gateway processes to clear in-memory bytecode cache
# Running processes may have already imported the corrupted module into memory
hermes gateway stop --profile <agent>
hermes gateway run --profile <agent> --replace
```
**Note**: Step 3 is critical. Cleared `.pyc` files only affect future interpreter starts. Already-running gateways must be restarted to drop corrupted bytecode from memory.

**Verification**:
- `tail -50 ${PROFILES_DIR}/<agent>/logs/agent.log` — no new `marshal data too short` within 5min
- Telegram gateway connectivity restored (check for `Connected to Telegram` in logs)
- Cron jobs complete with `completed` status instead of failing

**Post-restart confirmation** (critical):
After clearing `.pyc` caches and restarting gateways, verify the corruption is actually resolved — just checking file headers is insufficient; the running process must be freshly started.
```bash
# Step 1: Clear caches
rm -rf ${INSTALL_DIR}/agent/__pycache__
rm -rf ${INSTALL_DIR}/tools/__pycache__

# Step 2: Restart agents (not just reload)
hermes gateway stop --profile <agent>
hermes gateway run --profile <agent> --replace

# Step 3: Wait 10s, then verify no marshal errors in fresh logs
sleep 10
tail -30 ${PROFILES_DIR}/<agent>/logs/errors.log | grep -i marshal && echo "STILL CORRUPTED" || echo "CLEAN"

# Step 4: Test import in a fresh Python process
python3 -c "from agent.copilot_acp_client import CopilotACPClient; print('BYTECODE OK')"
```
**Still failing after restart?** The corruption may be in the agent-specific `~/.hermes/profiles/<agent>/__pycache__` or the process may not have restarted cleanly. Double-check all gateway processes terminated before restarting.

**Prevention**:
- Ensure sufficient disk space (keep >10% free on root partition)
- Avoid running multiple Hermes gateways from same install simultaneously (shared `.pyc` cache race conditions)
- Regular package integrity checks: `hermes doctor` or `pip verify hermes-agent`
- Monitor for abrupt system shutdowns or disk I/O errors

**Status**: Pattern observed 2026-05-02 across YoYo & Gentech agents; caused complete Telegram gateway stall despite processes showing as "running".

### Cron Jobs Not Firing
**Symptom**: All jobs show `last_run_at: null`, `hermes cron status` says gateway running but no output in `/root/.hermes/cron/output/`.
**Causes**:
- Scheduler thread blocked (check agent.log for "Cron ticker started" but no job dispatch)
- SessionDB corruption blocking job execution
- Configuration `cron_mode: deny` in config.yaml
- Jobs not loaded into agent cron directories (see "Job Misassignment" below)
**Fix**: `hermes cron tick` to force execution check; if silent failure → inspect gateway logs for warnings; consider gateway restart if stuck.

### Job Misassignment and Missing Profile Assignment
**Symptom**: Target jobs defined in global `/root/.hermes/cron/jobs.json` show `last_run_at: null` indefinitely, yet per-agent cron directories contain many other jobs that are executing. Global `jobs.json` may have `"profile": null` or missing `profile` field.

**Detection**:
```bash
# 1. Check global jobs.json for missing profile assignments
python3 -c "
import json
with open('/root/.hermes/cron/jobs.json') as f:
    jobs = json.load(f)['jobs']
for j in jobs:
    if not j.get('profile'):
        print(f'MISSING PROFILE: {j[\"id\"]} - {j[\"name\"]}')
"
# 2. Verify each global job exists in its intended agent's cron directory
for agent in yoyo dmob desmond gentech; do
  grep -q '<JOB_ID>' ${PROFILES_DIR}/\$agent/cron/jobs.json && echo 'FOUND in '\$agent || echo 'NOT in '\$agent
done
```

**Root causes**:
- Job creation via `hermes cron create` without specifying `--profile <agent>`; job stored globally but never dispatched to any agent's cron directory
- Profile field deleted or nulled during job edits
- Cron dispatcher not copying jobs from global store to per-agent directories on startup

**Fix**:
- Recreate job with explicit profile: `hermes cron create --profile <agent> --schedule "..." --name "..." --prompt "..."`
- Or manually edit global `jobs.json` to add `"profile": "<agent>"` then restart all gateway processes to force reload
- Clear per-agent cron lockfiles (`rm ${PROFILES_DIR}/*/cron/.tick.lock`) if executor is stuck

**Cross-contamination indicator**: Jobs appearing in an agent's cron directory that don't belong to that agent's domain (e.g., "Gentech — HQ Update" running under YoYo agent profile). This happens when profile field is missing and the first agent to boot "claims" the job. Check by comparing job names to agent responsibility matrix.

**Verification**:
- `hermes cron list --json` should show correct `profile` field for every job
- Each agent's cron directory should contain only jobs where `job['profile'] == '<agent>'`
- Target `last_run_at` timestamps should update within one schedule interval

### ElevenLabs TTS 401
**Symptom**: `elevenlabs.core.api_error.ApiError: status_code: 401, body: {'detail': {'status': 'invalid_api_key'}}`
**Fix**: Rotate ELEVENLABS_API_KEY in environment. Update in agent profile env or systemd service file. Restart gateway if not picked up.

### SessionDB Disk Full
**Symptom**: `Failed to initialize SessionDB — session will NOT be indexed for search: database or disk is full`
**Fix**: Clean up disk space. SessionDB location is typically `/root/.hermes/session.db` or similar. Check `df -h` on partition containing `/root`.

## Reference Locations\n\n- Gateway processes: `ps aux | grep hermes`\n- Agent logs: `${PROFILES_DIR}/<agent>/logs/{errors.log,agent.log,gateway.log}`\n- Cron jobs file: `/root/.hermes/cron/jobs.json`\n- Cron output: `/root/.hermes/cron/output/`\n- Hermes config: `/root/.hermes/config.yaml`\n- Systemd services: `systemctl status hermes-gateway-*`\n- **Cron health snapshot**: `/tmp/cron_health.txt` (last-run status per job)\n- **Agent cron dump**: `/tmp/<agent>_cron.txt` (job ID ownership per agent)\n\n## Empty Response / Model Timeout Pattern\n\n**Symptom**: `Agent completed but produced empty response (model error, timeout, or misconfiguration)` in cron health.\n\n**Diagnosis**:\n1. Confirm multiple jobs failing with identical empty response within short time window → likely provider/model outage, not per-job misconfig.\n2. Check if affected jobs belong to single agent or span multiple agents → determines scope.\n3. Review agent logs for any upstream API errors or timeout traces.\n\n**Common causes**:\n- Upstream model provider degraded/latency spike\n- Request timeout too low for model response time\n- Rate limit quota exceeded\n- Network connectivity interruption\n\n**Initial mitigations**:\n- Increase model `timeout` in agent's provider config\n- Route failing jobs to alternative provider/model if multi-provider setup\n- Add retry logic in job definition\n- Suspend affected schedule temporarily to prevent backlog\n\n**Status**: Pattern observed 2026-05-02 across 12 YoYo/Gentech jobs.\n\n## Missing / Revoked Credentials Pattern\n\n**Anthropic missing**: `RuntimeError: No Anthropic credentials found` → set `ANTHROPIC_TOKEN`/`ANTHROPIC_API_KEY` env var or run `claude /login`.\n\n**OAuth refresh revoked**: `RuntimeError: Refresh session has been revoked` → run `hermes model` to re-authenticate.\n\nBoth cause scheduled jobs to produce empty response until fixed.\n\n## Watchdog Reporting\n\nPer instructions: report only when anomalies detected. If all gateways up, no error patterns, and cron history shows recent successful runs → respond `STATUS:OK`. Otherwise format as `🚨 Watchdog Alert: [what's wrong]` with concise bullet list.
