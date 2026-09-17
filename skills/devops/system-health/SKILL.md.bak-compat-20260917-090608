---
name: system-health
description: "System-wide health diagnostics for Hermes deployments: gateway/anomaly detection, error log scanning, cron job verification, failure pattern detection, session database health, and post-incident recovery across multi-agent profiles."
tags: [health, monitoring, devops, cron, gateway, multi-agent, incident-response]
trigger: "When checking Hermes system health — daily/weekly audits, after agent restarts or deployments, when users report missed cron notifications or Telegram connection problems, investigating degradation patterns, or recovering from bytecode/corruption incidents. Use this umbrella for end-to-end health-check workflows."
related_skills:
  - hermes-cron-health-watchdog  # (this skill is now a section inside this umbrella; kept as deprecated alias via redirect — see below)
  - agent-health-monitoring   # (deprecated sibling; see §1 & §2)
  - defi  # if performing DeFi LP health checks
version: 1.0.0
author: Gentech
---

# System Health (Umbrella)

Comprehensive health-check framework for Hermes multi-agent deployments. Covers gateway process & log freshness, error pattern classification, cron job execution verification, failure root-cause analysis, and systematic recovery procedures (bytecode corruption, credential cascades, job misassignment, ticket zombie detection).

> **Consolidated skills:** `agent-health-monitoring`, `hermes-cron-health-watchdog`.

## User Reporting Protocol

When executing health checks for the user, adhere strictly to their preferred reporting style:

- **SILENCE RULE**: If all agents are healthy and no issues detected, respond with exactly `STATUS:OK` and nothing else. Do NOT report "all systems nominal" or any health summary.
- **REPORT RULE**: Only deliver a message if you detect a real problem — error, crash, or anomaly. Format: `🚨 Watchdog Alert: [what's wrong]` with a brief bullets-style summary of the detected issues.
- **Be quiet**: Only speak up when something breaks.

This protocol minimizes noise and respects the user's preference for signal-only communications.

## Quick Decision Table

| User Intent | Go To Section |
|-------------|---------------|
| "Check gateway status across all agents" | [1. Gateway & Process Health](#1-gateway--process-health) |
| "Cron jobs not firing — what's wrong?" | [2. Cron Job Execution Diagnostics](#2-cron-job-execution-diagnostics) |
| "Errors in agent logs — why?" | [3. Error Log Pattern Classification](#3-error-log-pattern-classification) |
| "Repeated model timeouts / empty responses" | [3d. Systemic Provider Outage] |
| "Telegram bot not responding / can't reach channels" | [3e. Telegram Connection Health](#3e-telegram-connection-health) |
| "Certificate / auth failures" | [3e. Credential Cascade Failures] |
| ".pyc marshal errors — how to fix?" | [4. Corrupted Python Bytecode Recovery](#4-corrupted-python-bytecode-recovery) |
| "How to verify health after a fix?" | [7. Verification Checklist](#7-verification-checklist) |
| "Token usage / cost audit this week" | [5. Token Usage & Cost Auditing](#5-token-usage--cost-auditing) |

---

## 1. Gateway & Process Health

**Original skill:** `agent-health-monitoring` → gateway status checklist and anomaly detection.

### Quick Check Sequence

**⚠️ CLI status can be misleading**: `hermes gateway status` may report a stale cached PID (e.g., `1118093` for all profiles) even when processes are stopped. **Always verify with raw process inspection.**

**1. Gateway process status per agent (TRUE STATE)**
```bash
# Preferred: direct process check
ps aux | grep hermes | grep 'gateway run'
# Count lines per profile: should see one distinct process per active agent

# Cross-check against per-profile CLI (may be stale)
for agent in gentech yoyo dmob desmond; do
  echo "=== $agent ==="
  hermes -p $agent gateway status 2>&1 | head -3
done
```
**Red flags**:
- `ps` shows zero matching processes but CLI reports `Gateway is running (PID: ...)` → **stale state file**, gateway is actually down
- All agents report the **same PID** → CLI cache corruption; trust `ps` output instead
- `gateway.lock` or `gateway.pid` files exist but no process → unclean shutdown, delete lock files before restart

**2. Log freshness check**
```bash
for agent in gentech yoyo dmob desmond; do
  log="${PROFILES_DIR}/$agent/logs/agent.log"
  if [ -f "$log" ]; then
    age=$(( ( $(date +%s) - $(stat -c %Y "$log") ) / 60 ))
    echo "$agent: last updated ${age}min ago"
  fi
done
```
- <5 min = fresh
- 5–30 min = stale (possible network lag)
- >30 min = inactive

**3. Error log scan (last 50 lines)**
```bash
tail -50 ${PROFILES_DIR}/<agent>/logs/errors.log
```
Look for: `EOFError: marshal data too short`, `401`, `database or disk is full`, `Connection error`, `Refresh session has been revoked`.

**4. Cron ticker verification**
```bash
hermes cron status
```
Should indicate gateway running and ticker active.

**5. Gateway internal state verification**
```bash
# Check gateway_state.json for active_agents value
for agent in gentech yoyo dmob desmond; do
  state_file="${PROFILES_DIR}/$agent/gateway_state.json"
  if [ -f "$state_file" ]; then
    active=$(python3 -c "import json; print(json.load(open('$state_file')).get('active_agents', 'unknown'))")
    echo "$agent: active_agents=$active"
  fi
done
```
- `active_agents > 0` = healthy (agent sessions loaded)
- `active_agents = 0` while process is running = **degraded** — gateway process alive but no agent profiles loaded, often due to startup error or credential failure

### Reference Locations

- Gateway processes: `ps aux | grep hermes`
- Agent logs: `${PROFILES_DIR}/<agent>/logs/{errors.log,agent.log,gateway.log}`
- Cron jobs file: `/root/.hermes/cron/jobs.json`
- Cron output: `/root/.hermes/cron/output/`
- Config: `/root/.hermes/config.yaml`
- Cron health snapshot: `/tmp/cron_health.txt` (if collected)

### Full Diagnostic Sweep

For the systematic multi-agent health sweep across cron metadata, session transcripts, output directories, error-keyword grep, and the `STATUS:OK` reporting format: see [2. Cron Job Execution Diagnostics](#2-cron-job-execution-diagnostics), which is the comprehensive `hermes-cron-health-watchdog` workflow.

> **Full original content,** including detailed error pattern reference, `2026-05-02 Watchdog Findings`, corrupted bytecode investigation steps, and empty-response pattern analysis: `references/agent-health-monitoring-full.md`

---

## 2. Cron Job Execution Diagnostics

**Original skill:** `hermes-cron-health-watchdog`

Systematic diagnostic sweep across all profiles to detect stuck jobs, provider failures, and execution anomalies.

### What This Workflow Detects

1. Stuck `next_run_at` (scheduler/gateway zombie)
2. `error` state / failed jobs
3. Missed executions
4. Provider rate limits (HTTP 429)
5. Connection / delivery failures
6. Unexpected paused/disabled jobs
7. Execution loops (runaway jobs)
8. Config/YAML syntax errors blocking gateway start
9. Corrupted `jobs.json` structure
10. Corrupted Python bytecode (`.pyc` import failures)
11. SessionDB corruption
12. Model/catalog unavailability (HTTP 404)

### Quick-Start Diagnostic Flow

#### Step 1: Query Recent Session Transcripts
Search across all profiles for `error`, `crash`, `timeout`, `failed`, `mapping values`, `was never closed`.

#### Step 2: Inspect Cron Metadata
```bash
for p in yoyo dmob desmond gentech; do
  echo "=== $p ==="
  python3 -c "import json; data=json.load(open('${PROFILES_DIR}/$p/cron/jobs.json')); [print(f\"{j['id'][:12]} | {j['name'][:40]:<40} | next={j.get('next_run_at','?')} | last={j.get('last_run_at','?')} | status={j.get('last_status','?')}\") for j in data.get('jobs',[]) if j.get('enabled')]"
done
```
Red flags: `last_status: error`, `next_run_at` in the past more than one interval, `last_run_at` >2× schedule interval.

#### Step 3: Check Cron Output Directories
```bash
for p in yoyo dmob desmond gentech; do
  ls -lt ~/.hermes/profiles/$p/cron/output/ | head -10
done
```
Look for: recent `last_run_at` but no output, very old newest file, hundreds of files in the last hour (stuck loop).

#### Step 4: Search Output Logs for Error Keywords
```bash
for p in yoyo dmob desmond gentech; do
  find ~/.hermes/profiles/$p/cron/output/ -name "*.md" -mtime -1 \
    -exec grep -l -i -E "error|fail|crash|timeout|exception|too many concurrent" {} \;
done
```

#### Step 5: Correlate & Build Summary Table

| Agent | Job Name | Job ID | Schedule | Last Run | Status | Issue |
|-------|----------|--------|----------|----------|--------|-------|

#### Step 6: Report

If all healthy: output exactly `STATUS:OK`. If issues: one alert per line:

```
🚨 Watchdog Alert: Agent <Name> job '<Job Name>' (<job_id>) — <short description>
```

### 2. Temporal Correlation for Mass Cron Failures

When diagnosing mass cron failures (many jobs erroring simultaneously), the fastest technique is **temporal correlation**: compare each job's `last_run_at` against the provider error window in `gateway.log`.

**Pattern:**
1. Extract the error window from gateway.log: `grep -i "error\|provider\|401\|revoked" ${PROFILES_DIR}/<agent>/logs/gateway.log`
2. Note the start/end timestamps of the provider outage
3. Cross-reference against each job's `last_run_at`
4. Jobs that ran **during** the window = systemic failure (provider issue)
5. Jobs that ran **before/after** = may have independent issues (prompt/config)

**Why this works:** Provider outages affect ALL jobs running during the window. If a job's `last_run_at` falls within the outage window and shows `error`, the root cause is the provider, not the job. If a job's `last_run_at` falls outside the window but still shows error, investigate per-job.

**Example:**
```
Provider error window: 2026-05-05 06:00 – 12:15 UTC
- Brain Review: last_run=05:00 → error = per-job issue (ran before window)
- Sync Check: last_run=06:00 → error = systemic (ran during window)
- Watchdog: last_run=13:52 → ok = provider recovered
```

This technique avoids the common pitfall of chasing per-job fixes when the actual problem is a provider outage affecting all jobs.

### Common Failure Signatures (Condensed)

| Signature | Typical Cause | Fast Fix |
|-----------|---------------|----------|
| **Corrupted `jobs.json` (bare `[]`)** | Manual edit mishap | Restructure to `{\"jobs\": [...]}`; restart gateways |
| **Cron registry file MISSING entirely (`cron.json` not found)** | Dispatch pipeline broken / gateway cache desync / systemd service failure cascade | 1) Check main `/root/.hermes/cron/jobs.json` for job definitions; 2) Recreate per-agent `cron.json` from global registry: `hermes cron sync --profile <agent>`; 3) Restart gateways; 4) If jobs defined globally but not synced, verify gateway started with `--cron` flag |
| Config YAML parse error | Indent/colon mistake | Validate with `python3 -c \"import yaml; yaml.safe_load(open(...))\"`; fix line |
| Stale `next_run_at` | Scheduler/gateway zombie | Restart gateway: `hermes gateway run --profile <p> --replace` |
| Gateway zombie (process alive, scheduler dead) | Scheduler thread crash | Same as above |
| HTTP 429 rate limit | Provider quota | Backoff; lower frequency; switch provider |
| Model 404 | Model retired/catalog change | Update model string; `hermes models` to check |
| Empty response cluster | Systemic provider outage | Check provider status; reroute to alternate model |
| Auth revoked / missing credentials | Token expiry / env loss | Re-authenticate: `hermes model` / `claude /login`; set env vars |
| .pyc marshal corruption | Disk I/O issue / compilation race | Delete `.pyc` caches; restart all gateways |
| Cron dispatch stasis (ticker running, not firing) | Cache desync / TZ jump / cron module missing | Restart all gateways; verify UTC; ensure `--cron` flag |
| Execution loop | Job triggering itself/webhook loop | `hermes cron pause <id>`; inspect prompt |
| Job auto-removed | Repeated failures | Fix root cause; recreate job |
| Script missing/path drift | Filesystem move | Restore script or patch job config |
| **Job defined in `jobs.json` but NOT loaded into active daemon** | Cron daemon cache corruption / missing `\"profile\"` binding / gateway started without `--cron` flag | 1) `hermes cron status` to verify daemon; 2) Check `jobs.json` has `\"profile\"` field; 3) Restart ALL gateways with `--replace`; 4) If persists, inspect cron daemon logs at `/root/.hermes/logs/cron.log` |
| **Fleet-wide TTS failure (all agents 401 from ElevenLabs)** | Invalid/expired API key across all profiles | Rotate `ELEVENLABS_API_KEY` in each agent's `.env` independently; credentials are NOT shared |
| **Cron job orphaning (profile: null/empty)** | Jobs defined without explicit `\"profile\"` binding → never loaded into active registry | Add `\"profile\": \"<agent>\"` to each job in `jobs.json`; restart gateways; verify jobs appear in `hermes cron list` |
| **Master gateway service failing (exit 203/EXEC)** | Systemd unit `ExecStart` path points to non-existent Python venv | Correct path to actual venv (`${INSTALL_DIR}/venv/bin/python`); `systemctl --user daemon-reload`; restart service |
| **Persistent marshal errors after .pyc cleanup** | Corrupted bytecode retained in running process memory | After deleting `.pyc` caches, **restart ALL gateway processes** — in-memory cache does not auto-flush |
| **Telegram flood control (21s+ retry backoff)** | Rate limit exceeded; messages sent too rapidly | Implement exponential backoff; reduce message frequency; stagger job execution times |
| **Disk pressure >80%** | Space exhaustion causing SessionDB corruption & .pyc corruption cascade | Clean disk space immediately; check `/var/log` and vault archives; monitor before restarts |
| **YAML syntax error blocking gateway startup** | Invalid YAML in config.yaml (often `mapping values are not allowed here` at specific line) | Validate with `python3 -c \"import yaml; yaml.safe_load(open('config.yaml'))\"`; fix indentation/colon; check line number from error; restart gateway |
| **Gateway drain timeout during shutdown** | Active agent sessions didn't complete within 60s drain period | Usually benign if intermittent; if recurring, check for stuck agent sessions or long-running tool calls; may indicate deeper agent lockup |
| **Agent process terminated without graceful shutdown** | SIGKILL/SIGTERM from external process or systemd restart cycle | Check `journalctl --user` for kill events; examine `/var/log/syslog` for OOM/killed messages; correlate with systemd unit failures |
| **Mass cron failures after provider outage** | Jobs with `model: null` inherit broken provider chain | Pin model+provider on all jobs: `cronjob(update, model={"model": "mimo-v2.5", "provider": "custom:<name>"})`. CLI `hermes cron edit` has no `--model` flag — use cronjob tool API. |
| **`No LLM provider configured` in cron jobs** | Cron daemon execution context lacks the provider config that the interactive gateway has. Especially common with custom endpoint models (e.g. mimo-v2.5) — `hermes status` shows provider working interactively, but cron-spawned jobs fail. Jobs may also lack model pinning. | 1) Verify provider works interactively via `hermes status`; 2) Check agent `config.yaml` for `llm:` section; 3) Pin model+provider on failing cron jobs; 4) Restart gateways after config changes; 5) Note: standalone cron scripts (not agent runs) write errors to `cron.log` not `gateway.log` |

### Pitfalls

- Don't rely solely on `cronjob list` metadata — always verify output files exist.
- `[SILENT]` last line is OK if earlier content shows healthy "nothing to do" state.
- Cross-profile duplicate job IDs — qualify alerts with profile name.
- Paused jobs shouldn't alert unless pause was unexpected.
- **After `.env` file changes, gateways MUST be restarted** — environment variables are loaded once at process start; live edits have no effect. Use `hermes gateway run --profile <agent> --replace` to reload.
- **After `.pyc` cleanup, wait 2–3 schedule intervals before confirming recovery** — old in-memory bytecode can persist in running gateways even after files are deleted.
- **Disk pressure (>80%) can cascade into SessionDB failures AND predispose bytecode corruption** — clean disk space *before* restarting gateways after corruption fix; monitor with `df -h /`.

### Post-Incident Verification

- After any fix, wait one schedule interval and confirm new output files appear.
- Confirm no new error-keyword matches in last hour.

> **Full original content,** including step-by-step diagnostic commands, per-symptom detection logic, and 2026-05-02 observed patterns in full detail: `references/hermes-cron-health-watchdog-full.md`

---

## 3. Error Log Pattern Classification

> **Also see:** [8. Git Repository Health & Sync Validation](#8-git-repository-health--sync-validation) — for backup/mirror infra health checks and recovery.


### 3a. Corrupted Python Bytecode (`.pyc` `marshal data too short`)

Symptom: `EOFError: marshal data too short` during any module import.

Detection:
```bash
python3 -c "import struct, glob;
for pyc in glob.glob('${INSTALL_DIR}/**/__pycache__/*.pyc', recursive=True):
    with open(pyc,'rb') as f: h=f.read(16)
    if len(h)>=16:
        sz=struct.unpack('<I', h[8:12])[0]
        if sz > 50_000_000: print(f'{pyc}: header_source_size={sz}')"
```
### Immediate Remediation (Mandatory Sequence)

**⚠️ Do NOT skip step 5 (gateway restart) — in-memory bytecode cache persists even after files are deleted and errors will continue.**

1. STOP all gateways across ALL profiles (corruption often spreads via shared library paths):
   ```bash
   hermes gateway stop --profile yoyo
   hermes gateway stop --profile dmob
   hermes gateway stop --profile desmond
   hermes gateway stop --profile gentech
   ```

2. Identify and delete ALL corrupt `.pyc` caches:
   ```bash
   rm -rf ${INSTALL_DIR}/agent/__pycache__
   rm -rf ${INSTALL_DIR}/tools/__pycache__
   ```

3. (Optional) Verify with detection script `scripts/detect-bytecode-corruption.py` — should report zero files with `header_source_size > 50MB`.

4. Check disk pressure BEFORE restart: `df -h /` — if usage >80%, clean space first. **Disk pressure is an early-warning signal** — `SessionDB` warnings ("database or disk is full") frequently appear within minutes BEFORE `.pyc` corruption spikes.

5. Restart ALL gateways fresh (critical — in-memory cache flush required):
   ```bash
   hermes gateway run --profile <agent> --replace
   ```

6. Verify recovery: tail `errors.log` of each profile for 5 minutes; run `python3 -c "import agent.copilot_acp_client"` in a fresh shell.

### If Corruption Returns Within 24h

Suspect underlying disk health or concurrent deployment race. Upgrade hermes-agent to latest (includes bytecode write safeguards) and schedule deployments during low-usage windows. Review `dmesg` for I/O errors.

Correlation: `SessionDB` ("database or disk is full") warnings often precede `.pyc` corruption within minutes.

---

### 3b. Cron Jobs Not Firing (Never Executed)

Symptoms: `last_run_at: null` (never executed), `hermes cron status` says gateway running, but no output in `/root/.hermes/cron/output/`.

**Detection:**
```bash
hermes cron list --json | python3 -c "import json,sys; data=json.load(sys.stdin); 
[print(f\"{j['name']}: last_run={j.get('last_run_at')}\") for j in data.get('jobs',[]) 
 if j.get('enabled') and not j.get('last_run_at')]"
```

**Common causes:**
1. Job defined in jobs.json but never loaded into active daemon (missing `"profile"` field)
2. Cron daemon cache desync after gateway restart
3. Gateway started without `--cron` flag (non-fatal but prevents dispatch)
4. Syntax error in job YAML/JSON blocks scheduler
5. `next_run_at` in the past but scheduler ticker stalled

**Fixes:**
- Run `hermes cron tick` to force execution check
- Verify each profile's jobs.json includes `"profile": "<agent>"` binding
- Restart gateway with `--replace` to refresh cron daemon
- Check `/root/.hermes/logs/cron.log` for parsing errors

---

### 3c. Job Misassignment / Missing Profile Assignment

Jobs appear globally but not under any agent's cron dir → missing `"profile"` field.

Detection scan (see full skill §Job Misassignment for precise Python snippet). Fix: recreate job with `--profile <agent>` or edit `jobs.json` manually; restart gateways.

---

### 3g. YAML Configuration Syntax Errors

**Symptoms**: Gateway fails to start or YAML parse error in agent logs; error message `mapping values are not allowed here` with a line/column reference.

**Rapid detection** (from 2026-05-02 incident):
```bash
# Extract exact line number and column from error log
grep 'mapping values are not allowed' ${PROFILES_DIR}/<agent>/logs/errors.log
# Example output: "2026-05-02 13:38:26,975 ERROR ... config.yaml at line 130, column 13"

# Validate YAML directly (shows first error)
python3 -c "import yaml; yaml.safe_load(open('${PROFILES_DIR}/<agent>/config.yaml'))"

# Pinpoint problematic line
sed -n '130p' ${PROFILES_DIR}/<agent>/config.yaml | cat -A  # show invisible chars
```
**Most common cause**: Missing space after colon (`key:value` instead of `key: value`), or tab character used for indentation. YAML requires spaces-only indentation and space after colon in key-value pairs.

**Fix workflow**:
1. Read the specific line: `sed -n '130p' ${PROFILES_DIR}/<agent>/config.yaml`
2. Validate entire file: `python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"` — will point to first error
3. Use `yamllint` if available or fix manually (replace tabs with spaces, add missing colon-space)
4. After fix, restart gateway: `hermes gateway run --profile <agent> --replace`

**YAML quick-reference rules**:
- Indentation: spaces only (no tabs), consistent 2-space levels
- Key-value: always `key: value` (colon MUST be followed by space)
- Lists: `- item` with space after dash
- Strings with special chars: quote them `"value:with:colons"`
- Yamllint config: `yaml[ "{extends": "default", "rules": { "truthy": "disable", "line-length": { "max": 120 } } }" ]`

**Verification**: After restart, gateway log should show `cron ticker started` without YAML parse errors. Process should appear in `ps` and systemd `active (running)`.

---

### 3h. Telegram Flood Control & Rate Limiting

**Symptoms**: Gateway logs show repeated warnings:
```
[Telegram] Telegram flood control on send (attempt 1/3), retrying in 17.0s: Flood control exceeded
```

**Detection**:
```bash
grep 'Telegram flood control' ${PROFILES_DIR}/<agent>/logs/gateway.log | tail -20
```

**Root causes**:
- Sending too many messages to same chat within short window (Telegram limit ~30 messages/sec per bot per chat)
- Multiple concurrent jobs targeting same chat/group
- No backoff between retries

**Mitigations**:
1. Stagger job schedules (use `--cron "*/5 * * * *"` instead of `"*/1 * * * *"` for high-frequency jobs)
2. Implement exponential backoff in job logic (already in gateway; ensure `retry_after` values are respected)
3. Consolidate multiple small messages into single larger response when possible
4. If persistent, add `--rate-limit` flag to gateway or use `hermes cron pause` on lower-priority jobs

**Recovery**: Flood control is automatic — gateway will retry with backoff. If stuck in loop for >10 minutes, restart gateway to reset retry state.

---

### 3q. Systemd Service Collision (Restart=always vs Existing Gateway)

**Symptoms**:
- `errors.log` floods with thousands of lines per hour (5,991+ errors in one incident)
- Error messages like `"Gateway already running"` or `"Port already in use"` repeating endlessly
- `mcp-stderr.log` grows to 100MB+ due to repeated stderr captures
- Disk usage climbs from log bloat

**Root cause**: A systemd service with `Restart=always` tries to start a new gateway while an existing gateway process (started independently, e.g. via `hermes gateway run`) is already running. The service keeps restarting and colliding, creating an error loop.

**Detection**:
```bash
# Check for collision errors in errors.log
wc -l ~/.hermes/logs/errors.log 2>/dev/null
grep -c "already running\|port.*in use\|Gateway.*running" ~/.hermes/logs/errors.log 2>/dev/null

# Check systemd services
systemctl status hermes-gateway.service 2>&1
systemctl list-units --type=service | grep hermes

# Check actual running processes
ps aux | grep "gateway run" | grep -v grep
```

**Red flags**:
- `errors.log` line count in thousands (normal: <50/day)
- `errors.log` file size >10MB
- `systemctl status hermes-gateway.service` shows `active (running)` AND `ps` shows a separate gateway process
- Multiple gateway processes for the same profile

**Fix**:
```bash
# 1. Stop the systemd service (this stops the collision loop)
systemctl stop hermes-gateway.service

# 2. Verify the real gateway is still running (should be — it was started independently)
ps aux | grep "gentech.*gateway" | grep -v grep

# 3. If the service keeps respawning, disable it
systemctl disable hermes-gateway.service

# 4. Clean up the bloated logs
rm -f ~/.hermes/logs/errors.log  # will regenerate fresh
rm -f ~/.hermes/logs/mcp-stderr.log  # if >100MB

# 5. Verify disk recovered
df -h / | tail -1
```

**Prevention**:
- Don't mix `hermes gateway run` (manual start) with systemd services that have `Restart=always`
- If using systemd, let systemd manage the lifecycle entirely
- If using manual starts, disable or remove the systemd service unit
- Monitor `errors.log` size — sudden bloat is an early indicator

**Pitfall**: The gateway process started manually (`hermes gateway run --profile gentech`) is usually the healthy one. The systemd service is the intruder. Don't kill the manual process to "fix" the collision — kill the service instead.

**Observed**: Jun 14, 2026 — gentech gateway running since Jun 13 via manual start. `hermes-gateway.service` (Restart=always) kept trying to restart, generating 5,991 collision errors and bloating logs to 195MB. Fixed by `systemctl stop hermes-gateway.service`.

---

### 3r. Systemd Services for Non-Hermes API Servers (uvicorn/FastAPI)

**Pattern:** When adding API servers (FastAPI, uvicorn, etc.) as systemd services alongside Hermes, the `ExecStart` must use the **Hermes venv python**, not `/usr/bin/python3`.

**Why:** The system python (`/usr/bin/python3`) does not have uvicorn, FastAPI, or other project dependencies. The Hermes venv (`${INSTALL_DIR}/venv/bin/python3`) has them all.

**Example service file:**
```ini
[Unit]
Description=Rugcheck API v2.1.0
After=network.target

[Service]
Type=simple
WorkingDirectory=/root/rugcheck/api
ExecStart=${INSTALL_DIR}/venv/bin/python3 -m uvicorn server:app --host 0.0.0.0 --port 8088
Restart=always
RestartSec=5
EnvironmentFile=${PROFILES_DIR}/gentech/.env

[Install]
WantedBy=multi-user.target
```

**Key details:**
- `ExecStart` uses full venv path: `${INSTALL_DIR}/venv/bin/python3`
- `EnvironmentFile` points to profile `.env` for API keys and config
- `Restart=always` ensures survival across reboots
- `WorkingDirectory` must match where the server expects to run

**Verification after creation:**
```bash
systemctl daemon-reload
systemctl enable <service-name>   # auto-start on boot
systemctl start <service-name>    # start now
systemctl is-active <service-name>  # confirm running
curl -s http://localhost:<port>/ | head -1  # confirm responding
```

**Pitfall:** Creating the service with `/usr/bin/python3 -m uvicorn` will fail silently — systemd keeps restarting, and `journalctl -u <service>` shows "No module named uvicorn". Always verify the python path has the needed packages: `${INSTALL_DIR}/venv/bin/python3 -c "import uvicorn; print('ok')"`

**Observed**: Jun 23, 2026 — rugcheck-api and x402-api services created. Initial version used `/usr/bin/python3` (no uvicorn), caused restart loop. Fixed by switching to venv python path.

---

### 3i. Master Gateway Service Failure (Systemd)

**Symptoms**: 
- `systemctl --user status hermes-gateway.service` shows `Active: failed (Result: exit-code)` with exit code `203/EXEC`
- All cron jobs across ALL agents show `last_run_at: null` (never executed)
- `hermes cron status` reports daemon not running despite gateway processes alive
- No cron output files in `/root/.hermes/cron/output/`

**Diagnostic sequence**:
```bash
# 1. Check service status
systemctl --user status hermes-gateway.service --no-pager -l

# 2. Inspect systemd unit file for wrong path
cat /root/.config/systemd/user/hermes-gateway.service | grep ExecStart

# 3. Verify correct Python venv exists
ls -la ${INSTALL_DIR}/venv/bin/python

# 4. Check for recent unit changes
systemctl --user status hermes-gateway.service --no-pager -l | grep -A5 'since'
```

**Typical failure signature** (April 27–May 2, 2026 incident):
```
Active: failed (Result: exit-code) since Mon 2026-04-27 22:18:36 UTC; 4 days ago
...
hermes-gateway.service: Failed with result 'exit-code'.
```
Cause: `ExecStart=/root/.hermes/hermes-agent/venv/bin/python` (non-existent path) instead of `${INSTALL_DIR}/venv/bin/python`.

**Impact scope**: This single service coordinates cron dispatch for all agents. When it fails, NO scheduled jobs execute across the entire fleet, regardless of individual agent gateway health.

**Recovery steps**:
1. Edit unit file: `nano /root/.config/systemd/user/hermes-gateway.service`
2. Correct `ExecStart` line to: `ExecStart=${INSTALL_DIR}/venv/bin/python -m hermes_cli.main --profile gentech cron-daemon` (or other default profile)
3. Reload systemd: `systemctl --user daemon-reload`
4. Start service: `systemctl --user start hermes-gateway.service`
5. Verify: `systemctl --user status hermes-gateway.service` should show `active (running)`
6. Confirm cron execution: `hermes cron list` should show recent `last_run_at` timestamps within one schedule interval

**Related pattern**: Cron jobs defined with `profile: null` in `jobs.json` are never loaded into any agent's active daemon. After restoring master service, verify each job has explicit `"profile"` field bound.


---

### 3j. Fleet-Wide Credential Cascade (Shared Invalid Key)

**Pattern**: All agents exhibit same authentication error simultaneously (e.g., 401 Invalid API Key from ElevenLabs), indicating a shared credential source or manual propagation error.

**Detection across fleet**:
```bash
for agent in yoyo dmob desmond gentech; do
  echo "=== $agent ==="
  grep -c 'status_code: 401' ${PROFILES_DIR}/$agent/logs/errors.log
done
```
If counts are similar magnitude across all agents (e.g., ~200 each), suspect shared credential.

**Investigation**:
1. Check `.env` files in each profile: `cat ${PROFILES_DIR}/<agent>/.env | grep ELEVENLABS`
2. Compare values — if identical, likely propagated together
3. Verify actual key validity via provider dashboard or `curl` test

**Recovery**:
- **Do NOT** fix one agent only — rotate the key at the source and update all profiles independently.
- Generate new ElevenLabs API key from dashboard
- Update each agent's `.env` individually: `echo "ELEVENLABS_API_KEY=<newkey>" >> ${PROFILES_DIR}/<agent>/.env`
- Restart affected gateways (or wait for next cron restart)
- Verify: `grep -c '401' errors.log` should stop increasing

**Prevention**: Use secret management (Vault, 1Password) or environment-specific keys per agent to avoid single point of failure.

---

### 3k. Process Uptime & Restart Verification

After remediation, confirm processes are running fresh (not stale pre-fix instances):

**Check process start times**:
```bash
ps -eo pid,etimes,cmd | grep hermes | grep gateway
```
- `etimes` = elapsed time in seconds
- `< 60s` = just restarted (good — post-fix)
- `> 3600s` = old process (may still hold corrupted state)

**Systemd restart policy nuance**:
Hermes gateway systemd units use `Restart=on-failure`. This means:
- Non-zero exit (crash) → auto-restart after `RestartSec=30`
- **Clean exit (code=0) → NO auto-restart** (by design)
- Exit signal `SIGTERM` → treated as clean if gateway initiated it; manual restart required

**Coordinated shutdown pattern** (observed May 2 2026):
Multiple gateways stopped simultaneously within seconds via explicit `systemctl --user stop hermes-gateway-<profile>.service`. Logs showed `Received SIGTERM as a planned --replace takeover — exiting cleanly`. Gentech auto-restarted because its exit code was `1` (signal-initiated shutdown); YoYo, DMOB, Desmond exited `0/SUCCESS` and stayed dead until manually restarted.

**Detection of planned vs crash termination**:
```bash
# Check gateway.log for stop reason
grep -E 'SIGTERM|exiting cleanly|stopping gateway' ${PROFILES_DIR}/<agent>/logs/gateway.log | tail -5

# Check systemd status line for exit code
systemctl --user status hermes-gateway-<agent>.service | grep -i 'code='
```
- `code=exited, status=0/SUCCESS` or `signal=HUP` with clean shutdown log → planned stop
- `code=exited, status=1/FAILURE` or no clean shutdown message → crash

**Force restart all gateways** (recommended after any systemic fix):
```bash
hermes gateway stop --profile yoyo
hermes gateway stop --profile dmob
hermes gateway stop --profile desmond
hermes gateway stop --profile gentech
# Wait 5s
hermes gateway run --profile yoyo --replace &
hermes gateway run --profile dmob --replace &
hermes gateway run --profile desmond --replace &
hermes gateway run --profile gentech --replace &
```

**Verify uptime**:
```bash
ps -eo pid,etimes,cmd | grep hermes | grep gateway | awk '{print $2/60 " min: " $4}'
```
All should show `< 5 min` after restart.

**When gateways won't auto-restart**: Consider changing unit `Restart=always` ONLY if business logic requires continuous uptime and you accept restarts during maintenance. Otherwise, keep `on-failure` and implement external watchdog (cron health check → alert → manual intervention).

---

### 3l. Cron Job Orphaning (Null Profile Binding)

**Symptom**: Jobs appear in `/root/.hermes/cron/jobs.json` but NEVER execute (`last_run_at: null`). `hermes cron list` shows `profile: unknown` or empty.

**Root cause**: Job definition missing required `"profile": "<agent>"` field. The cron dispatcher requires explicit profile binding to route execution; jobs without it are parsed but never loaded into any agent's active daemon.

**Detection scan**:
```bash
python3 -c "
import json
with open('/root/.hermes/cron/jobs.json') as f:
    data = json.load(f)
for job in data.get('jobs', []):
    if not job.get('profile'):
        print(f\"ORPHANED: {job['id']} | {job['name']} | deliver={job.get('deliver')}\")
"
```

**Fix workflow**:
1. Edit `/root/.hermes/cron/jobs.json`
2. Add `"profile": "<agent>"` to each job based on naming convention:
   - `YoYo — *` → `"profile": "yoyo"`
   - `DMOB — *` → `"profile": "dmob"`
   - `Desmond — *` → `"profile": "desmond"`
   - `Gentech — *` → `"profile": "gentech"`
3. After editing, restarts ALL gateways to refresh cron daemon caches:
   ```bash
   systemctl --user restart hermes-gateway-yoyo.service
   systemctl --user restart hermes-gateway-dmob.service
   systemctl --user restart hermes-gateway-desmond.service
   systemctl --user restart hermes-gateway-gentech.service
   ```
4. Verify: `hermes cron list --profile yoyo` should now show the job with proper binding

**Prevention**: When creating jobs via `hermes cron create`, always specify `--profile <agent>`. The CLI usually sets this automatically from context, but double-check with `hermes cron list --json | python3 -m json.tool`.

---

### 3m. Disk Pressure as Leading Indicator

**Early-warning signal**: `/dev/sda1` usage >80% frequently precedes corruption cascades within hours.

**Correlation chain** (observed 2026-05-02):
1. Disk pressure crosses 80% threshold
2. Within minutes: `SessionDB` errors appear (`database or disk is full`, `sqlite3.DatabaseError: file is not a database`)
3. Within 1–2 hours: `.pyc` marshal corruption spikes (`EOFError: marshal data too short`)
4. Gateways crash or become unresponsive

**Detection**:
```bash
# Quick check
df -h /dev/sda1

# Set monitoring threshold (alert if >80%)
df -h /dev/sda1 | awk '/dev\/sda1/ {if ($5+0 > 80) print "ALERT: Disk usage", $5}'
```

**Immediate mitigation when pressure detected**:
1. Clean large/old files (`/var/log/*.gz`, old vault archives, temp directories)
2. Rotate and compress logs: `find ${PROFILES_DIR} -name "*.log" -size +100M -exec gzip {} \;`
3. Remove stale sandboxes: `rm -rf /tmp/hermes_sandbox*`
4. Clean Docker/container cache if present
5. **DO NOT** restart gateways immediately after cleanup — wait 10–15 minutes for disk I/O to stabilize

**Prevention**: Schedule periodic disk usage checks via cron; set alerts at 75% usage; clean before reaching 85%.

### 3m-b. Proactive Disk Cleanup (Hermes-Level)

**Trigger:** Disk usage >75%, or user asks "why is storage full?" / "do we need to clean up?"

**Unlike §3m emergency response**, this is a calm, systematic audit — not an urgent reaction to corruption.

#### Step 1: Overview
```bash
df -h / && echo "---" && du -sh /root/.hermes/ /root/vaults/ /tmp/ 2>/dev/null
```

#### Step 2: Find offenders
```bash
# Per-profile breakdown (biggest dirs first)
du -sh ${PROFILES_DIR}/gentech/* 2>/dev/null | sort -rh | head -20

# /tmp/ build artifacts
du -sh /tmp/*/ 2>/dev/null | sort -rh | head -10

# State snapshots
du -sh /root/.hermes/state-snapshots/ && ls /root/.hermes/state-snapshots/ | wc -l
```

#### Step 3: Safe cleanup targets (no data loss)

| Target | Typical Size | Command | Safe? |
|--------|-------------|---------|-------|
| `/tmp/cargo-install*` | 2-4GB each | `rm -rf /tmp/cargo-install*` | ✅ Rebuilt on next install |
| `/tmp/portfolio-site`, `/tmp/ampersend-*`, `/tmp/camoufox-*` | 500MB-1GB each | `rm -rf /tmp/<dir>` | ✅ Old build dirs |
| `state-snapshots/` (all but latest) | 100-300MB each | `cd /root/.hermes/state-snapshots && ls -dt */ | tail -n +2 | xargs rm -rf` | ✅ Keep latest only |
| `audio_cache/` (>7 days) | Varies | `find ${PROFILES_DIR}/gentech/audio_cache/ -type f -mtime +7 -delete` | ✅ Old generated audio |
| Old sessions (>14 days) | ~1GB per 2K sessions | `hermes sessions prune --older-than 14 --yes` | ✅ DB history only |

#### Step 4: Aggressive cleanup (if still tight)

```bash
# Prune sessions more aggressively
hermes sessions prune --older-than 7 --yes

# VACUUM the session DB (requires no active gateways)
sqlite3 /root/.hermes/state.db "VACUUM;"
# NOTE: VACUUM may fail if gateways are running (WAL lock). If so, it'll
# compact on next restart — don't force it.
```

#### Step 5: Verify
```bash
df -h / | tail -1
du -sh /root/.hermes/ /tmp/
```

#### What NOT to clean
- `home/portfolio/` — active vault content
- `state.db` — main database (only VACUUM to reclaim dead space)
- `sessions/` files directly — use `hermes sessions prune` to stay consistent with DB
- `skills/`, `plugins/`, `cron/` — active Hermes config
- Anything under `/root/vaults/` — user data

#### Pitfalls
- **`hermes sessions prune` only deletes from the DB** — the `/sessions/` directory files may linger. The prune command handles DB consistency; leftover files are harmless.
- **VACUUM needs exclusive lock** — fails silently if gateways are running. Don't force; it compacts on next restart.
- **`/tmp/` rebuilds are expected** — cargo installs, npm builds, etc. will recreate on next use. This is free space, not "lost" space.
- **audio_cache cleanup won't affect active TTS** — files in use are held open; deleting old files is safe.

---

### 3m-c. Full VPS Infrastructure Audit (Beyond Hermes)

**Trigger:** User says "audit the stack", "clean up everything", "what are we actually using?", or disk >80%.

This is broader than §3m-b (which focuses on Hermes internals). This audits the entire VPS: Docker containers, systemd services, installed binaries, /tmp cruft, and vault hygiene.

#### Step 1: Survey Everything

```bash
# Docker containers + status + ports
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}"

# Docker images (find unused)
docker images --format "table {{.Repository}}\t{{.Size}}\t{{.CreatedSince}}"

# Docker volumes
docker volume ls

# Systemd services (custom, not system)
systemctl list-units --type=service --state=running --no-pager | grep -v -E "systemd|ssh|docker|cron|getty|dbus|network|udev|journal|login|polkit|rsyslog|snap|unattended"

# Port usage
ss -tlnp | grep LISTEN | awk '{print $4}' | sort

# Disk: top offenders
du -sh /root/*/ 2>/dev/null | sort -rh | head -15
du -sh /tmp/*/ 2>/dev/null | sort -rh | head -10
```

#### Step 2: Classify Each Service

For each Docker container / systemd service / installed binary, answer:

| Question | If No → Action |
|----------|---------------|
| Is it actively used by the user? | Candidate for removal |
| Does it back another running service? | Keep (e.g., RSSHub Redis) |
| Does it need paid API keys we don't have? | Kill (e.g., Framedeck needed ElevenLabs) |
| Is it a local fallback for something cloud does better? | Kill unless user explicitly wants local (e.g., Ollama small models) |
| Is it duplicated by something else running? | Kill the weaker one |

#### Step 3: Get User Confirmation Before Killing

**Always present the kill list before executing.** Group by:
- **KILL** — clearly unused, no dependencies
- **QUESTION MARK** — may be useful, needs user input
- **KEEP** — actively serving a purpose

User preference: "If it's not pulling its weight, kill it." But confirm before deleting code/data (Docker images, cloned repos).

#### Step 4: Execute Kills

```bash
# Docker: stop + remove container + image + volumes
docker stop <name> && docker rm <name>
docker rmi <image>
docker volume rm <volume>  # if associated

# Systemd: stop + disable + remove
systemctl stop <service> && systemctl disable <service>
rm /etc/systemd/system/<service>.service
systemctl daemon-reload

# Cloned repos: just rm -rf
rm -rf /root/<repo-dir>
```

#### Step 5: Clean Cruft

```bash
# /tmp — old build artifacts, debug dirs, tarballs
du -sh /tmp/*/ 2>/dev/null | sort -rh | head -10
# Remove anything >30 days or clearly old

# Vault hygiene
find ${VAULT_DIR}/ -maxdepth 3 -name ".git" -type d  # nested repos to remove
find ${VAULT_DIR}/ -maxdepth 3 -type f -size +1M -not -path "*/.git/*"  # large files
find ${VAULT_DIR}/ -name ".edreams_chrome_data" -type d  # browser junk
find ${VAULT_DIR}/ -maxdepth 3 -type f -mtime +30 -not -path "*/.git/*" -not -path "*/.obsidian/*"  # stale files
```

#### Step 6: Report Before/After

| Metric | Before | After |
|--------|--------|-------|
| Disk used | X | Y |
| Disk free | X | Y |
| RAM available | X | Y |
| Docker containers | N | N |
| Docker images | N | N |

#### Pitfalls

- **RSSHub Browserless occupies port 3000** — if you need 3000 for something else, reconfigure RSSHub or use a different port.
- **Docker images are lazy-pulled** — `docker pull` caches layers; removing an image saves disk but re-pull is fast.
- **MinIO is often paired with apps** — if you kill Framedeck, also kill MinIO (it was only serving Framedeck's S3 emulation).
- **Ollama models live in `~/.ollama/`** — the binary removal doesn't auto-delete models. Remove `~/.ollama/` separately.
- **`/tmp/` contents are ephemeral by design** — safe to nuke anything old, but check for active processes first (`lsof +D /tmp/<dir>`).

#### VPS Services Reference (as of Jun 7, 2026)

| Service | Port | Purpose | Backed by |
|---------|------|---------|-----------|
| CloakBrowser | 8080 | Browser automation | Docker |
| RSSHub | 1200 | RSS feed aggregation | Docker (Redis + Browserless) |
| Hermes Dashboard | 3071 | Web UI | systemd |
| TREK | 3002 | Travel planner | Docker (mauriceboe/trek) |

**Removed (Jun 7 audit):** Framedeck, MinIO, Ollama — reclaimed ~10GB disk + 5.6GB RAM.

---

### 3l. Log Correlation with Systemd Journal

To determine why an agent terminated (crashed vs killed vs graceful shutdown):

**Check user journal for hermes units**:
```bash
journalctl --user -u hermes-gateway.service --since "1 hour ago" --no-pager
journalctl --user -u hermes-agent@* --since "1 hour ago" --no-pager
```

**Look for**:
- `Main process exited, code=exited, status=203/EXEC` → startup failure (bad path/venv)
- `Killed process` → OOM killer or manual SIGKILL
- ` segmentation fault` → native extension crash
- `SIGTERM` → graceful stop request
- `Failed with result 'exit-code'` → process returned non-zero

**Cross-reference with agent logs**: Match timestamps to narrow cause. Use `ps -eo pid,lstart,cmd` to get process start time if PID unknown.

---

### 3f. Multi-Provider Credential Health Check

### 3f. OAuth Token Management & Refresh Workflows

**Proactive OAuth Refresh Script**
The primary automated tool for token maintenance is `${PROFILES_DIR}/gentech/scripts/refresh_nous_oauth.py`.

**Execution:**
```bash
python3 ${PROFILES_DIR}/gentech/scripts/refresh_nous_oauth.py
```

**Output Interpretation:**
- **Success (success: true)**: Tokens are fresh and valid
- **Needs Reauth (success: false, needs_reauth: true)**: Token fully revoked, requires manual intervention
- **Critical Error (success: false, critical: true)**: Unexpected script failure

**Exit Codes:**
- `0` - Tokens fresh OR re-auth needed (expected maintenance state)
- `1` - Unexpected critical error

The script is designed to return 0 even when re-auth is needed to avoid false positive alerts in monitoring systems.

**Handling Revoked Sessions**
When the refresh script returns `needs_reauth: true`, the OAuth session has been fully revoked and requires manual re-authentication via `hermes model`.

**Required Action:**
Run the following command in an **interactive terminal**:
```bash
hermes model
```

This initiates the device flow authentication process:
1. Generates a device code
2. Saves pending flow state to `pending_nous_device_flow_latest.json`
3. Displays verification URL and user code
4. User completes authentication in browser
5. Tokens are saved to `auth.json`

**Important Notes:**
- The `hermes model` command **requires** an interactive terminal
- Cannot be executed in cron jobs or non-interactive contexts
- After running `hermes model`, wait for user authentication to complete
- Then run the device flow completion script

**Device Flow Completion**
After initiating device flow via `hermes model` and completing browser authentication, the pending device flow file must be processed to obtain the actual tokens.

**Completion Script:**
```bash
python3 ${PROFILES_DIR}/gentech/scripts/complete_nous_device_flow.py
```

**Prerequisites:**
- The `pending_nous_device_flow_latest.json` file must exist in the scripts directory
- The user must have visited the verification URL and completed authentication
- The device code must not have expired (typically 10-15 minutes validity)

**Script Behavior:**
- Polls the OAuth token endpoint until tokens are obtained
- Saves tokens to `auth.json`
- Removes the pending flow file upon success
- Handles errors like expiration, authorization pending, and slow_down

**Monitoring Output:**
The script provides real-time feedback:
```
Nous OAuth Device Flow Completion
==================================
Verify at: https://portal.nousresearch.com/manage-subscription
Expires: 2026-05-06 13:30 UTC

Polling for token completion...
```

**Auth File Structure Reference**
Understanding `auth.json` is crucial for troubleshooting:

```json
{
  "credential_pool": {
    "nous": [
      {
        "access_token": "eyJhbG...",
        "refresh_token": "rt_u0u55a4Uyu8dpMEH8VK3L7FtPtldLqwvz2VaJ805xGNOigHY3OABeYdtGDseEoiI",
        "expires_at": "2026-05-06T12:38:54.268608+00:00",
        "agent_key": "sk-nou...",
        "expires_in": 900
      }
    ]
  },
  "providers": {
    "nous": {
      "access_token": "...",
      "refresh_token": "...",
      "expires_at": "...",
      "agent_key": "..."
    }
  }
}
```

**Key fields to monitor:**
- `expires_at` - When the access token expires
- `refresh_token` - Present for refresh capability
- `needs_reauth` flag from refresh script output

**Troubleshooting Common Issues**
- **Script not found errors**: Ensure you're in the correct Hermes profile directory
- **Device flow file missing**: Run `hermes model` first to initiate device flow
- **Token refresh fails repeatedly**: The session may be permanently revoked. Full re-authentication required.
- **Script permissions**: Scripts should be executable. Fix with `chmod +x ${PROFILES_DIR}/gentech/scripts/*.py`
- **Python path issues**: The refresh script adds `${INSTALL_DIR}` to Python path. Ensure Hermes is installed there.

**Best Practices**
- Run the refresh script regularly via cron (it's designed for this)
- Monitor logs for `needs_reauth: true` conditions
- Keep `hermes model` command available for manual re-authentication
- Document the verification URL and user code when initiating device flow
- Test the workflow periodically to ensure it works when needed

**Integration with Monitoring**
The refresh script is designed for monitoring systems:
- Exit code 0 prevents false alerts
- JSON output contains `needs_reauth` flag for manual review
- Check logs or parse JSON for maintenance conditions
- Consider pairing with `hermes status` checks for comprehensive monitoring

---

### 3d. Systemic Provider Outage (Clustered Empty Responses)

Multiple jobs across agents fail with "Agent completed but produced empty response (model error, timeout, or misconfiguration)".

Indicates provider-side outage or model deployment issue — not per-job misconfiguration. Check status page; if transient, next run recovers; if persistent, switch provider/model.

### 3d-b. "API call failed after retries" — Full Diagnostic Pattern

**Trigger:** User reports seeing "The model provider failed after retries" in Telegram or CLI. Hermes deliberately strips provider details from the user-facing message — you MUST check gateway logs for the actual error.

**Step 1: Get the real error from journalctl**
```bash
journalctl --user -u hermes-gateway-gentech --since "15 min ago" --no-pager 2>&1 | \
  grep -i "error\|fail\|521\|525\|retry\|api call" | tail -20
```
Key fields in log lines: `provider=`, `model=`, `summary=`, `error_type=`.

**Step 2: Classify the error**

| Error signature | Root cause | Fix |
|----------------|------------|-----|
| HTTP 521 (`origin_down`) | Cloudflare can't reach upstream origin server | Wait — transient upstream outage. Check provider status page. |
| HTTP 525 (`ssl_handsh`) | SSL/TLS handshake failed between Cloudflare and origin | Wait — transient. Origin SSL config issue on provider side. |
| HTTP 400 + "model has been deprecated" | Model removed from catalog | Switch to recommended replacement (e.g., `mimo-v2-pro` → `mimo-v2.5-pro`) |
| HTTP 404 + model name | Model not found in provider catalog | Check `hermes models` or `curl` test; pick an available model |
| HTTP 401/403 | Auth failure | Check `.env` API key, re-authenticate |
| HTTP 429 | Rate limit / quota | Back off; check provider credits; switch provider |

**Step 3: Check for session-level model overrides**

Config default may be correct, but an active session can override it via `/model`. This override persists across turns until the session is reset. The gateway log will show `provider=opencode-go model=<deprecated>` even when config says `provider: custom model: mimo-v2.5`.

Detection:
```bash
# Find which model is actually being used in recent errors
journalctl --user -u hermes-gateway-gentech --since "1 hour ago" --no-pager 2>&1 | \
  grep "model=" | grep -oP 'model=\S+' | sort | uniq -c | sort -rn
```

Fix: In the affected session, run `/model` and select a current model. Or `/reset` to start fresh with config defaults.

**Pitfall:** The user-facing error message says "check gateway logs for diagnostics" — this is by design. Hermes intentionally hides provider details from chat to avoid leaking API endpoints and model routing info. The agent must always check logs to diagnose.

---

### 3e. Telegram Connection Health

Symptoms: `[Telegram] Telegram network error, scheduling reconnect: Bad Gateway` or repeated connection drops, or bot not responding in specific channels.

#### End-to-End Connectivity Verification

Full workflow for verifying a Hermes Telegram bot can reach all configured channels. Run these steps in order:

**Step 1: Check env vars are set**
```
grep TELEGRAM_BOT_TOKEN ~/.hermes/profiles/<agent>/.env
grep TELEGRAM_ALLOWED_USERS ~/.hermes/profiles/<agent>/.env
grep TELEGRAM_HOME_CHANNEL ~/.hermes/profiles/<agent>/.env
```
All three must be present. Missing vars means the gateway loads empty credentials.

**Step 2: Verify bot token via Telegram API**
```
TOKEN=$(grep TELEGRAM_BOT_TOKEN ~/.hermes/profiles/<agent>/.env | cut -d= -f2-)
curl -s "https://api.telegram.org/bot${TOKEN}/getMe" | python3 -m json.tool
```
Expected: `"ok": true` with bot `id`, `username`, `first_name`. If false, token is invalid or revoked — generate a new one from BotFather.

**Step 3: Verify each configured channel is accessible**
```
TOKEN=$(grep TELEGRAM_BOT_TOKEN ~/.hermes/profiles/<agent>/.env | cut -d= -f2-)
for chat in "-1003863540828" "-1003872552815" "-1002916759037" "-1003893562036"; do
  result=$(curl -s "https://api.telegram.org/bot${TOKEN}/getChat?chat_id=$chat" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'OK: {d[\"result\"].get(\"title\",\"?\")} ({d[\"result\"][\"type\"]})' if d.get('ok') else f'ERR: {d.get(\"description\",\"unknown\")}')")
  echo "$chat → $result"
done
```
- **OK** = bot is a member and can read/send
- **ERR: "Bad Request: chat not found"** = bot is not a member, chat ID is wrong, or bot was removed. Add the bot to the group via Telegram.
- **ERR: "Forbidden: bot was kicked"** = bot was banned from the group. Re-invite.

**Step 4: Cross-reference channel prompts against config**
```
grep -A2 "channel_prompts:" ~/.hermes/profiles/<agent>/config.yaml
grep "chat_id:" ~/.hermes/profiles/<agent>/config.yaml
```
Ensure every channel prompt's chat ID matches a channel the bot can actually access. Mismatches cause silent routing failures — the message dispatches but never arrives.

**Step 5: Verify gateway has loaded Telegram**
```
hermes status | grep -i telegram
```
Expected: `Telegram ✓ configured (home: <chat_id>)`. If not configured, check `display.platforms.telegram` section in config.yaml.

**Step 6: Verify gateway process is running**
```
hermes gateway status
```
Expected: `active (running)`. If down, restart: `hermes gateway run --profile <agent> --replace`.

#### Known Pitfalls

- **Bot handle/name is cosmetic** — The bot's Telegram username (e.g. `@ProtoJaybot`) has no effect on channel routing. Chat IDs are what matter. A bot named "Gentech" with an unrelated handle works identically to a bot named "Gentech Labs".
- **Bot must be a member of each channel** — Being configured in config.yaml is not enough. The bot must physically be added to each Telegram group by an admin. Use `getChat` to verify membership.
- **Bot naming limitation** — If the desired bot name (`@GentechLabs_bot`) is unavailable, any valid handle works. The bot's `first_name` (display name) can be set to anything in BotFather regardless of username availability.
- **Home channel vs routing** — The home channel is where unclassified messages land. Specialist channels (Labs, Strategies, Entertainment) require `channel_prompts` in config AND the bot must be a member of each. The home channel can be a routing group (e.g. HQ) — not a separate "inbox."
- **Reactions setting** — Set `telegram.reactions: false` in config.yaml to disable reaction handling. The default is `false` for Gentech.
- **Allowed users** — `TELEGRAM_ALLOWED_USERS` is a comma-separated list of Telegram user IDs. If set, only those users can interact with the bot. Omitting it (or setting empty) allows all users in the channel. Use `getUpdates` or `getChatAdministrators` to verify user IDs.

#### Recovery

- **Restart gateway** to force fresh connection: `hermes gateway run --profile <agent> --replace`
- **If persistent connection drops**: Check HTTP 502/503/504 in gateway logs — may be Telegram API regional outage. Wait and retry.
- **If bot can't reach a specific channel**: Most likely bot was removed or channel ID changed. Re-invite bot and verify with `getChat`.
- **If token was revoked**: Generate new token in BotFather, update `.env`, restart gateway.

---

## 4. Corrupted Python Bytecode Recovery

**Observed pattern (2026-05-02):** Corruption of `gemini_native_adapter.cpython-311.pyc` recurred across two watchdog cycles; deleted `.pyc` files were regenerated corrupted, indicating the root cause (disk I/O pressure or concurrent writer) was still active.

**Full recovery sequence:**

```
1. STOP all gateways across ALL profiles (corruption often spreads via shared library paths)
2. Identify all corrupt .pyc files:
   find ${INSTALL_DIR} -name '__pycache__' -type d -exec rm -rf {} +
   # Alternative: detect via header_source_size > 50MB as shown in §3a
3. CLEAR caches system-wide:
   rm -rf ${INSTALL_DIR}/agent/__pycache__
   rm -rf ${INSTALL_DIR}/tools/__pycache__
4. Check disk pressure: `df -h /` — if >80%, clean space before proceeding
5. Restart ALL gateways fresh (critical — in-memory cache flush required)
6. Verify: tail errors.log of each profile for 5 min; run `python3 -c "import agent.copilot_acp_client"` in a new shell
```

**If corruption returns within 24h:** Suspect underlying disk health or concurrent deployment race. Upgrade hermes-agent to latest (includes bytecode write safeguards) and schedule deployments during low-usage windows.

**Correlation:** `SessionDB` "database or disk is full" warnings frequently appear within minutes *before* `.pyc` corruption spikes — treat disk pressure as an early-warning signal.

---

## 5. Token Usage & Cost Auditing

Query the Hermes state database (`~/.hermes/state.db`) for token consumption, cost tracking, and week-over-week comparison.

### Schema Reference

The `sessions` table has these key columns for auditing:

| Column | Type | Description |
|--------|------|-------------|
| `model` | TEXT | Model name (e.g. `mimo-v2.5`, `arcee-ai/trinity-large-thinking`) |
| `source` | TEXT | `cron` or `cli` — distinguishes automated vs interactive |
| `billing_provider` | TEXT | Provider key: `nous`, `custom`, `opencode-go`, `gemini`, etc. |
| `input_tokens` | INTEGER | Total input tokens consumed |
| `output_tokens` | INTEGER | Total output tokens generated |
| `cache_read_tokens` | INTEGER | Tokens read from prompt cache |
| `estimated_cost_usd` | REAL | Estimated cost in USD (from provider pricing) |
| `tool_call_count` | INTEGER | Number of tool calls in session |
| `message_count` | INTEGER | Total messages (user + assistant + tool) |
| `end_reason` | TEXT | `completed`, `cli_close`, `cron_complete`, `compression`, etc. |
| `started_at` | REAL | Unix timestamp |

### Weekly Audit Query

```python
import sqlite3
from datetime import datetime

conn = sqlite3.connect('/root/.hermes/state.db')
cursor = conn.cursor()

# Define week boundaries (Monday 00:00 UTC)
this_week_start = datetime(2026, 5, 4, 0, 0, 0).timestamp()
this_week_end = datetime(2026, 5, 11, 0, 0, 0).timestamp()

# Totals by model
cursor.execute("""
    SELECT model, source,
        COUNT(*) as sessions,
        SUM(input_tokens) as input_tok,
        SUM(output_tokens) as output_tok,
        SUM(estimated_cost_usd) as cost
    FROM sessions 
    WHERE started_at >= ? AND started_at < ?
    GROUP BY model, source
    ORDER BY cost DESC
""", (this_week_start, this_week_end))

for row in cursor.fetchall():
    model, source, sess, inp, out, cost = row
    print(f"[{source}] {model}: {sess} sess, {inp:,} in, {out:,} out, ${cost:.4f}")
```

### Anomaly Detection Queries

**High tool-call sessions (potential loops):**
```sql
SELECT model, source, tool_call_count, input_tokens, estimated_cost_usd,
       datetime(started_at, 'unixepoch') as started
FROM sessions 
WHERE started_at >= ? AND started_at < ?
  AND tool_call_count > 20
ORDER BY tool_call_count DESC
```

**Sessions with unusual token patterns (zero input, non-zero output):**
```sql
SELECT model, source, message_count, input_tokens, output_tokens
FROM sessions 
WHERE started_at >= ? AND started_at < ?
  AND (input_tokens = 0 OR input_tokens IS NULL)
  AND output_tokens > 0
```

### Cost Attribution

Paid models that generate costs:
- `xiaomi/mimo-v2-flash` — ~$0.297/1M input tokens (via Nous)
- `stepfun/step-3.5-flash` — ~$0.08/1M input tokens (via Nous)
- `openai/gpt-5.4-nano` — ~$1.12/1M input tokens (via Nous)

Free-tier models (no cost tracked):
- `mimo-v2.5` — via `custom` or `opencode-go` providers
- `arcee-ai/trinity-large-thinking` — via `nous` provider (free tier)
- `gemini-3-flash-preview` — via `gemini` provider

### Post-Consolidation Validation

After Option 1 consolidation (May 7, 2026), compare pre/post:
```sql
-- Pre-consolidation: May 4-6
SELECT source, model, COUNT(*), SUM(input_tokens), SUM(estimated_cost_usd)
FROM sessions WHERE started_at >= 1746326400 AND started_at < 1746585600
GROUP BY source, model

-- Post-consolidation: May 7-10
SELECT source, model, COUNT(*), SUM(input_tokens), SUM(estimated_cost_usd)
FROM sessions WHERE started_at >= 1746585600 AND started_at < 1746931200
GROUP BY source, model
```

### Report Format

Weekly audit reports should include:
- Total sessions, input/output tokens, cost (this week vs last week)
- % change (green if down, red if up)
- Top 3 consumers by tokens and by cost
- Anomaly flags (high tool-call sessions, paid-model loops)
- Recommendations (keep/adjust/pause specific jobs)

---

## 6. Related Umbrellas

- **`defi`** — DeFi LP health checks, position monitoring, on-chain reads (often integrated)
- **`agent-coordination`** — department routing and multi-agent orchestration (sometimes cross-referenced)

---

## 7. Verification Checklist

After any health-check + remediation cycle:

- [ ] Gateway processes confirmed running for all agents (Gentech, YoYo, DMOB, Desmond)
- [ ] Agent log file timestamps <5min old
- [ ] No `marshal data too short` errors in `errors.log` of any profile
- [ ] Cron ticker active (`hermes cron status`)
- [ ] Every profile's `jobs.json` `next_run_at` advancing (or intermittent schedule is acceptable)
- [ ] Output directories contain recent `.md` files (within last interval)
- [ ] No `last_status: error` jobs unfixed
- [ ] No credential 401/revoked errors outstanding
- [ ] If `.pyc` corruption was found: ALL gateways restarted (not just the affected profile)
- [ ] If config syntax issues were fixed: verified with `yaml.safe_load` / `py_compile`

---

## 9. Remote VPS Access (SSH Key Path Workaround)

**Problem:** Hermes runs under a non-standard HOME directory (`${PROFILES_DIR}/gentech/home/`), but the SSH client looks for keys in `/root/.ssh/`. Generated keys land in the Hermes HOME, not where SSH expects them.

**Detection:** `ssh root@VPS_IP` returns `Permission denied (publickey,password)` even after adding the public key to `~/.ssh/authorized_keys` on the remote.

**Fix sequence:**
```bash
# 1. Generate key (if none exists)
mkdir -p ~/.ssh && ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N "" -q

# 2. Copy to standard SSH location
mkdir -p /root/.ssh
cp ~/.ssh/id_ed25519 /root/.ssh/
cp ~/.ssh/id_ed25519.pub /root/.ssh/
chmod 700 /root/.ssh
chmod 600 /root/.ssh/id_ed25519

# 3. Add public key to remote VPS
# (run on VPS or ask user to run)
echo "ssh-ed25519 AAAAC3... root@hostname" >> ~/.ssh/authorized_keys

# 4. Test
ssh -o ConnectTimeout=10 root@VPS_IP "echo connected"
```

**Why this happens:** `~` resolves to `HERMES_HOME` (profile-specific), not `/root/`. SSH client uses `/root/.ssh/` (system-wide). The key exists but SSH can't find it.

**Pitfall:** Don't create an SSH config with `IdentityFile` pointing to the Hermes HOME path — it works but creates a fragile dependency on the profile path. Copying to `/root/.ssh/` is the stable fix.

**Verified:** Jun 4, 2026 — SSH into VPS (100.73.143.15) for Multica cleanup. Key generated in Hermes HOME, copied to `/root/.ssh/`, SSH worked immediately.

---

## References (Session-Specific Detail)

The following files preserve the complete original SKILL.md content of each absorbed skill, plus their linked reference documents:

- `references/agent-health-monitoring-full.md`
- `references/hermes-cron-health-watchdog-full.md`
- `references/cloudflare-api-diagnostics.md` — API subdomain triage chain: local → nginx → Cloudflare → error 1003 → DNS-only → Let's Encrypt fix
- `references/gateway-status.md`
- `references/jobs-not-executing.md`
- `references/elevenlabs-401.md`
- `references/watchdog-health-2026-05-01.md`
- `references/watchdog-corruption-gemini-native-2026-05-01.md`
- `references/jobs-missing-from-active-daemon.md`
- `references/watchdog-health-2026-05-02.md`
- `references/bytecode-corruption.md`
- `references/bytecode-corruption-2026-05-02.md`
- `scripts/detect-bytecode-corruption.py`

- `references/token-audit-state-db.md` — state.db schema, pricing reference, and audit query patterns

- `references/hermes-dashboard-deployment-2026-06-05.md` — Hermes Web Dashboard deployment on self-hosted VPS: `dashboard_auth` module stub fix, `--insecure` flag, systemd persistence
- `references/gateway-port-conflict-jun-2026.md` — June 26, 2026 incident: multiple gateway processes binding to same port, resolution sequence, and prevention strategies

See also: `hermes-agent` skill for cron job configuration, gateway lifecycle, and session management fundamentals (pinned bundled skill). Specifically, see `hermes-agent` §Cron Job Model Pinning for the provider resilience pattern and `references/cron-model-pinning-session-2026-05-05.md` for the full incident timeline.

### Related Recent Incidents
- **Gateway Port Conflict (Jun 26, 2026)**: Multiple processes binding to same port - see `references/gateway-port-conflict-jun-2026.md` for full resolution sequence
- **Model Catalog Cleanup**: Removal of non-existent `glm-4.5-flash` causing fallback switching
- **Ollama Cloud Strategy**: Implementation of tiered model selection for cost optimization

### 3n. Vision Tool / Auxiliary Model Mismatch
<!-- existing content -->

### 3p. web_extract Silent Degradation (Empty extract_backend)

**Symptom**: `web_extract` tool calls consistently fail with:
```json
{"success": false, "error": "DuckDuckGo (ddgs) is a search-only backend and cannot extract URL content. Set web.extract_backend to firecrawl, tavily, exa, or parallel."}
```

**Root cause**: `web.extract_backend` is empty or unset in `config.yaml`. The tool silently falls back to DuckDuckGo, which is search-only and cannot extract content from URLs.

**Detection**:
```bash
grep extract_backend /root/.hermes/config.yaml
# If empty string or missing: extract_backend is not configured
```

**Impact**: Any cron job or interactive session using `web_extract` for URL content extraction will fail silently — the tool doesn't crash, it returns an error dict. Jobs that depend on scraping pages, fetching docs, or extracting web content will appear to complete but produce no useful output.

**Fix**: Set `web.extract_backend` to a supported provider: `firecrawl`, `tavily`, `exa`, or `parallel`. Requires API key for the chosen provider.

### 3p. Gateway Port Conflicts & Model Routing Issues

**Symptoms**: Multiple gateway instances failing to bind to same port, "address already in use" errors, model switching/fallback behavior.

**Root Causes**:
1. **Multiple gateway processes** trying to bind to same port (8088, 8089, etc.)
2. **Stale PID files** from previous crashes causing false "already running" states
3. **Non-existent model configurations** causing fallback switching
4. **Background scripts** spawning gateways without coordination

**Detection**:
```bash
# Check for port conflicts
netstat -tlnp | grep :8088

# Verify actual running processes (not stale CLI cache)
ps aux | grep "python.*gateway.*run" | grep -v grep

# Check for gateway lock files
find ${PROFILES_DIR} -name "gateway.lock" -o -name "gateway.pid"
```

**Fix Sequence**:
1. **Identify conflicting processes**:
   ```bash
   lsof -ti:8088  # Get PID of process using port
   kill -9 <PID>   # Force kill conflicting process
   ```

2. **Clean stale lock files**:
   ```bash
   find ${PROFILES_DIR} -name "gateway.*" -delete
   ```

3. **Verify model availability**:
   ```bash
   # Check if configured models actually exist
   curl -s "https://openrouter.ai/api/v1/models" | jq '.data[] | select(.id | contains("glm"))'
   
   # Test direct provider access if using cloud services
   curl -s "https://api.z.ai/v1/models"  # Check Z.AI models
   ```

4. **Update model configuration** - Remove non-existent models from config.yaml:
   ```bash
   # Remove deprecated models like glm-4.5-flash
   sed -i '/glm-4.5-flash/d' ${PROFILES_DIR}/<agent>/config.yaml
   ```

**Prevention**:
- Use unique ports per gateway instance
- Implement process coordination before starting new gateways
- Validate model availability before configuration
- Monitor for background script spawning conflicts

**Observed**: Jun 26, 2026 - Multiple gateway instances on port 8088 causing conflicts. Root cause: Background scripts (`open_gateway.py`) spawning without coordination. Fixed by killing conflicting PID (2034195) and cleaning stale lock files.

### 3q. Model Catalog Management & Provider Strategy

**Symptom**: Model switching behavior, "model not found" errors, fallback to wrong models.

**Root Cause**: Configuration includes models that don't exist in provider's live catalog, causing automatic fallback.

**Detection**:
```bash
# Check model availability in provider catalog
curl -s "https://openrouter.ai/api/v1/models" | jq '.data[] | select(.id | contains("glm-4.5"))'

# Check current model configuration
grep "default:" ${PROFILES_DIR}/<agent>/config.yaml
```

**Provider-Specific Patterns**:
- **Z.AI**: Models prefixed with `z-ai/` (e.g., `z-ai/glm-5.2`, `z-ai/glm-4.7`)
- **Ollama Cloud**: Direct model names (e.g., `glm-5.2`, `qwen3.5`)
- **Olamah Cloud**: May have different naming conventions

**Strategic Model Selection**:
```bash
# Optimized strategy for cost/performance balance
NORMAL_TASKS="deepseek"        # Low cost for routine operations
COMPLEX_TASKS="glm-5.2"        # Maximum context for coding
```

**Configuration Best Practices**:
- Remove deprecated/non-existent models from catalog
- Keep only models available in provider's live API
- Implement tiered model strategy based on task complexity
- Consider Ollama Cloud subscription for home continuity

**Observed**: Jun 26, 2026 - `glm-4.5-flash` model caused fallback switching. Fixed by removing from AVAILABLE_MODELS in gateway configuration and updating user config to use `glm-4.7` as default.

**Why this matters**: The Gentech Watchdog is itself a cron job (`Gentech Watchdog` on profile `gentech`). If this job fails, the system becomes blind to all agent failures. **Always verify the watchdog runs successfully** as part of any health check.

**Detection**: Check the watchdog's last run status and error logs.

```bash
# Check Gentech Watchdog cron job status
hermes cron list --profile gentech | grep -i "watchdog"

# Or directly inspect the job
hermes cron list --profile gentech --json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for job in data.get('jobs', []):
    if 'watchdog' in job.get('name', '').lower():
        print(f\"Job: {job['name']}\")
        print(f\"ID: {job['id']}\")
        print(f\"Schedule: {job.get('schedule')}\")
        print(f\"Last run: {job.get('last_run_at')}\")
        print(f\"Status: {job.get('last_status', 'unknown')}\")
        print(f\"Error: {job.get('last_error', 'none')}\")
"
```

**Red flags**:
- `last_run_at` is older than expected (watchdog missed runs)
- `last_status: error` with messages like:
  - `"Hermes is not logged into Nous Portal. Run \`hermes model\` to re-authenticate."`
  - `"HTTP 429: quota exhausted"`
  - `"Refresh session has been revoked"`
- No recent output files in `${PROFILES_DIR}/gentech/cron/output/`

**Root causes identified in 2026-05-06 incident**:
1. **Nous OAuth token revocation** - Refresh tokens expired, requiring manual re-authentication via `hermes model`
2. **API quota exhaustion** - ElevenLabs and other providers hit rate limits (HTTP 429)
3. **Missing LLM provider configuration** - Agents lack fallback provider setup
4. **Credential cascade failures** - Invalid/expired API keys across multiple services

**Recovery sequence**:
1. **Re-authenticate all agents** with Nous Portal:
   ```bash
   hermes model --profile yoyo
   hermes model --profile dmob
   hermes model --profile desmond
   hermes model --profile gentech
   ```
   (Each profile requires interactive login)

2. **Rotate API keys** for exhausted providers (ElevenLabs, etc.):
   - Generate new keys from provider dashboards
   - Update each agent's `.env` file independently
   - Restart gateways to load new credentials

3. **Configure LLM fallback providers** for agents missing them:
   ```bash
   hermes model --profile <agent> --set default <provider>
   ```

4. **Restart all gateways** to apply changes:
   ```bash
   hermes gateway stop --profile yoyo
   hermes gateway stop --profile dmob
   hermes gateway stop --profile desmond
   hermes gateway stop --profile gentech
   # Wait 5 seconds
   hermes gateway run --profile yoyo --replace &
   hermes gateway run --profile dmob --replace &
   hermes gateway run --profile desmond --replace &
   hermes gateway run --profile gentech --replace &
   ```

5. **Verify watchdog recovery**:
   ```bash
   # Wait one schedule interval (5 minutes)
   sleep 300
   # Check watchdog ran successfully
   hermes cron list --profile gentech | grep -A2 "Gentech Watchdog"
   # Should show recent `last_run_at` and `ok` status
   ```

**Prevention**: 
- Monitor watchdog health as a leading indicator
- Set up separate alerts for watchdog failures (external monitoring)
- Regularly check Nous Portal token expiration dates
- Implement API key rotation policies
- Maintain fallback LLM providers configured for all agents

**Correlation with systemic failures**: When the watchdog fails, all agents continue operating but without monitoring. This creates a "blind spot" where failures go undetected. The 2026-05-06 incident showed that watchdog failure often precedes broader agent failures by days, making it an early warning sign.

**Related patterns**: See §3e (Telegram Flood Control), §3f (Credential Health), and §3d (Provider Outage) for related systemic issues.

---

## 8. Session-Anomaly Reference (2026-05-02 Watchdog Findings)

**Incident**: Multi-agent fleet failure — systemic infrastructure collapse across all four profiles.

**Detected patterns** (newly documented, added to skill):

- **A. CLI status divergence** — `hermes gateway status` reported `PID 1118093` for all agents (stale cache), but `ps` showed only Gentech running. YoYo, DMOB, Desmond gateways stopped. **Detection**: always cross-check with `ps aux | grep hermes`; do not trust per-agent CLI alone.

- **B. Cron registry files missing fleet-wide** — no `cron.json` existed in any agent profile (`${PROFILES_DIR}/*/cron.json` missing). Cause: systemd master service failure since April 27 prevented cron daemon initialization and job sync. **Detection**: run `scripts/check-cron-registry-integrity.py`. **Fix**: `hermes cron sync --profile <agent>` per agent after service restored.

- **C. Master gateway service dead** — `hermes-gateway.service` failed April 27 with exit code `203/EXEC` due to `ExecStart=/root/.hermes/hermes-agent/venv/bin/python` (wrong path). This single service coordinates cron dispatch fleet-wide; its failure blocked all scheduled jobs across all agents. **Fix**: correct `ExecStart` to `${INSTALL_DIR}/venv/bin/python`; `systemctl --user daemon-reload`; start service.

- **D. Active agents count zero despite gateway running** — Gentech gateway process alive but `gateway_state.json` showed `active_agents: 0`. Indicates agent loader failed or credentials blocked profile initialization. Check gateway logs for early startup errors; restart gateway after fixing underlying issue (often missing/invalid API keys or YAML config errors).

- **E. Environment variable not loaded despite .env being correct** — `.env` files contained valid `ELEVENLABS_API_KEY` but running Gentech process environment lacked it. Cause: process started before `.env` update; environment loaded only at process start. **Fix**: restart gateway to pick up changes.

- **F. Fleet-wide TTS 401 errors with valid key** — Historical errors showed `elevenlabs.core.api_error.ApiError: Invalid API key` across all agents, yet the key in `.env` was valid. Root cause: gateways stopped before key propagation; restart required. Key was already correct but not in active process memory.

- **G. Cron daemon not running despite gateway running** — `hermes cron status` indicated daemon was down. Disconnected from individual agent gateway health; cron dispatch is a separate subsystem. **Detection**: `hermes cron status`; **Fix**: `hermes cron start` or restart master service.

**Key learning**: Do not treat agent health as per-profile independent. Always check:
1) Systemd master service (if used)
2) Cron daemon status (global)
3) Cron registry file presence per agent
4) Process list vs CLI-reported status divergence
5) `active_agents` field in `gateway_state.json`
6) Environment loaded from `.env` (process `/proc/<pid>/environ` if uncertain)
