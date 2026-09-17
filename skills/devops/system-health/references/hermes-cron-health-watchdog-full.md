---
name: hermes-cron-health-watchdog
description: "Systematic health diagnostics for multi-agent Hermes cron deployments. Inspects session transcripts, cron metadata, and per-agent output logs to detect stuck jobs, provider failures, and execution anomalies across all profiles."
tags: [hermes, cron, health-check, watchdog, devops, monitoring, multi-agent]
---

**See also:** `references/watchdog-health-2026-05-01.md` — session-specific error transcripts, reproduction recipes, and provider-quirk compendium from the 2026-05-01 health sweep. `references/watchdog-corruption-gemini-native-2026-05-01.md` — detailed diagnostic and recovery for the corrupted `gemini_native_adapter.pyc` systemic failure. `references/jobs-missing-from-active-daemon.md` — diagnostic and recovery for jobs present in snapshot but absent from the active cron daemon. `references/watchdog-health-2026-05-02.md` — cron dispatch failure pattern (ticker running but jobs not executing), credential cascades (ElevenLabs 401, Anthropic missing), model 404s, and gateway restart loops observed across all profiles.

# Hermes Cron Health Watchdog

Run a systematic diagnostic sweep across all Hermes agent profiles to detect cron job failures, stuck executions, missed runs, and provider errors before they become outages.

## When to Use

- You are a scheduled watchdog cron job checking on YoYo, DMOB, Desmond, Gentech, or other agent profiles.
- Cron jobs appear to have stopped firing or are producing stale output.
- An agent hasn't reported in longer than its schedule interval.
- You need to distinguish between "silent because healthy" and "silent because broken."
- Post-incident: verify which jobs recovered and which are still stuck after a restart/fix.

## What This Workflow Detects

1. **Stuck `next_run_at`** — job timestamps frozen in the past (scheduler/gateway zombie).
2. **`error` state / failed jobs** — `last_status: error` with `last_run_at` frozen.
3. **Missed executions** — `last_run_at` older than the schedule interval by a large margin.
4. **Provider rate limits** — `HTTP 429: too many concurrent requests` or similar in output logs.
5. **Connection failures** — gateway or Telegram delivery errors in `last_delivery_error`.
6. **Paused / disabled jobs** — `enabled: false` or `state: paused` unexpectedly.
7. **Execution loops** — rapid-fire execution output files (minutes apart) suggest a stuck loop.
8. **Configuration file syntax errors** — YAML (`config.yaml`) or Python (`auxiliary_client.py`) parse errors that prevent gateway startups or crash jobs mid-run. Validate config files with `python3 -m py_compile` / `yaml.safe_load`.
9. **Corrupted `jobs.json`** — file is a bare `[]` list instead of `{"jobs": [...]}` structure, or contains extra data / duplicate JSON objects, causing `json.JSONDecodeError: Extra data` on read.

## Quick-Start Diagnostic Flow

### Step 1: Query Recent Session Transcripts

Search for known error indicators in recent sessions across all agents:

```python
# In Hermes, this is done via session_search tool
# Keywords: agent names, "error", "crash", "timeout", "failed"
# Also check: "mapping values", "was never closed" (YAML/Python syntax errors in config or core files)
```

Look for:
- Repeated `AttributeError`, `ValueError`, `OSError`
- Gateway disconnect / reconnect loops
- Provider 429 / 502 / 503 responses
- Tool execution failures (e.g. `cronjob`, `browser`)

### Step 2: Inspect Cron Metadata

Run `cronjob list` or inspect raw `jobs.json` for every profile:

```bash
# Raw inspection across all profiles
for p in yoyo dmob desmond gentech; do
  echo "=== $p ==="
  python3 -c "
import json, os
path = f'${PROFILES_DIR}/{p}/cron/jobs.json'
if not os.path.exists(path): print('MISSING'); exit()
with open(path) as f: data = json.load(f)
for j in data.get('jobs', []):
    if not j.get('enabled'): continue
    print(f\"{j['id'][:12]} | {j['name'][:40]:<40} | next={j.get('next_run_at','?')} | last={j.get('last_run_at','?')} | status={j.get('last_status','?')}\")
"
done
```

**Red flags in cron metadata:**
- `last_status: error` — investigate immediately.
- `next_run_at` older than now by more than 1 interval — scheduler is stuck.
- `last_run_at` is more than 2× the schedule interval old — missed executions.
- `state: paused` or `enabled: false` without an explicit pause reason.

### Step 3: Check Cron Output Directories

Each firing creates a file under `~/.hermes/profiles/<profile>/cron/output/<job_id>/`:

```bash
for p in yoyo dmob desmond gentech; do
  echo "=== $p ==="
  ls -lt ~/.hermes/profiles/$p/cron/output/ | head -10
done
```

Look for:
- Jobs with recent `last_run_at` but **no new output files** → job ran but produced no artifact (possible silent fail).
- Jobs with **very old newest file** → not executing.
- Jobs with **hundreds of files in the last hour** → stuck in a run loop.

### Step 4: Search Output Logs for Error Keywords

```bash
for p in yoyo dmob desmond gentech; do
  find ~/.hermes/profiles/$p/cron/output/ -name "*.md" -mtime -1 \
    -exec grep -l -i -E "error|fail|crash|timeout|exception|too many concurrent" {} \;
done
```

For each matching file, read the first and last 20 lines to classify the error:
- **HTTP 429** → provider rate limit; backoff will usually clear it.
- **HTTP 502/503** → transient gateway/provider issue.
- **Tool execution error** (e.g. `cronjob` tool returned malformed data) → investigate tool state.
- **Timeout / hung** → last line is `[SILENT]` with no content before it → job may have been killed.

### Step 5: Correlate Findings

Build a summary table:

| Agent | Job Name | Job ID | Schedule | Last Run | Status | Issue |
|-------|----------|--------|----------|----------|--------|-------|
| YoYo | Crypto Watchlist | faed4f588aef | 4×/day | Apr 28 | ok | **STALE** — no runs since Apr 28 (~2 days missed) |
| YoYo | Mess Hall Pre-Shift | a9880f234c2b | daily | Apr 29 | error | **ERROR STATE** since Apr 22 |
| YoYo | Mess Hall Post-Shift | cd3a275dbae3 | daily | Apr 29 | error | **RATE LIMIT** HTTP 429 on latest run |

### Step 6: Report

If **all agents healthy** → output exactly `STATUS:OK` and nothing else. No verbosity.

If **issues found** → output structured alert, one per line:

```
🚨 Watchdog Alert: Agent <Name> job '<Job Name>' (<job_id>) — <short description>
🚨 Watchdog Alert: Agent <Name> job '<Job Name>' (<job_id>) — <short description>
```

## Target Paths and Files

| Path | Purpose |
|------|---------|
| `~/.hermes/profiles/<profile>/cron/jobs.json` | Canonical job definitions and next-run timestamps |
| `~/.hermes/profiles/<profile>/cron/output/<job_id>/` | Per-job execution artifacts (`.md` logs) |
| `~/.hermes/profiles/<profile>/cron/output/<job_id>/<timestamp>.md` | Single execution log with full prompt + response |

## Common Failure Signatures

### Corrupted `jobs.json`
- File is a bare `[]` list instead of `{"jobs": [...]}` structure, or `json.JSONDecodeError: Extra data` / `Extra data: line 1 column 7` when read, or multiple root JSON objects (`...}{...`).
- Causes `cronjob list` to fail with: `'list' object has no attribute 'get'`.
- Fix: manually restructure the file and backfill with `"jobs": []` wrapper.

### Config Syntax Error (YAML / Python)
- `config.yaml` parse failure at gateway start: `yaml.scanner.ScannerError: mapping values are not allowed here`.
- Python core file parse failure: `'{' was never closed` in `auxiliary_client.py` or similar, causing jobs to crash with `SyntaxError` / `IndentationError`.
- Validate before restart: `python3 -m py_compile <file>` or `python3 -c "import yaml; yaml.safe_load(open('${PROFILES_DIR}/<profile>/config.yaml'))"`.
- Fix: inspect the file around the reported line and correct indentation / close braces.

### Stale `next_run_at`
- `next_run_at` is hours/days in the past.
- Fix: recalculate timestamps via Python + `croniter`, then restart gateway.
- See `hermes-agent` skill section "Cron jobs stuck — next_run_at in the past."

### Gateway Zombie (process alive, scheduler dead)
- `last_run_at` hasn't updated for days despite valid `next_run_at`.
- `ps aux | grep hermes` shows PID.
- Fix: `hermes gateway run --profile <profile> --replace`
- See `hermes-agent` skill section "Cron zombie."

### Provider Rate Limit (HTTP 429)
- Output response ends with: `API call failed after 3 retries: HTTP 429 ...`
- Usually self-healing on next interval. If persistent across 3+ runs, consider lowering frequency or switching provider.

### Model-Level Empty Response (No Content)
- `last_status: error` with message: `Agent completed but produced empty response (model error, timeout, or misconfiguration)`.
- Indicates the provider returned an empty completion (not a rate limit or crash). Check provider health / model availability.
- Often coincides with high load or model switches.
- Fix: verify model is available; if transient, next run usually clears it.

### Script Missing / Path Drift
- Cron output shows: `Script not found: /path/to/script.py`.
- Script was deleted, moved, or never created. Also triggered when a profile is rebuilt and scripts directory is not restored.
- Cross-check `~/.hermes/profiles/<profile>/scripts/` — if the expected script is absent, recreate it or update the cron job to point to the correct path.
- Fix: restore script from backup (e.g., vault or GitHub) or update the job's script config.

### Job Removed from List
- Job was present in `jobs.json` yesterday, gone today.
- Hermes auto-removes jobs that fail repeatedly.
- Fix: identify root cause, then recreate via `hermes cron create`.

### Execution Loop (runaway job)
- Same `job_id` directory has new files every minute instead of every N hours.
- Usually caused by a job that triggers itself or a webhook that loops.
- Fix: `hermes cron pause <id>`, investigate prompt for self-triggering patterns.

### Corrupted Python Bytecode (.pyc import failure)
- `EOFError: marshal data too short` when importing compiled modules (e.g., `agent/gemini_native_adapter.pyc`). Breaks core functionality like session summarization and LLM calls.
- Appears in agent logs during runtime import: `from agent.gemini_native_adapter import ...` → marshal error.
- Fix: delete the corrupt `.pyc` file(s) and restart gateway to force recompilation. Typical locations: `${INSTALL_DIR}/agent/__pycache__/*.pyc` or within installed package `site-packages`. If persistent, reinstall/upgrade hermes-agent.
- See also: "Session summarization failed after 3 attempts: marshal data too short."

**Detection technique (from 2026-05-01 incident):**
```bash
# Step 1: Find the specific .pyc by filename (common location)
find ${INSTALL_DIR} -name "*gemini_native_adapter*.pyc" 2>/dev/null

# Step 2: Check if .pyc is suspiciously small (<20KB for core adapters)
find ${INSTALL_DIR}/agent/__pycache__ -name "*.pyc" -size -20k 2>/dev/null

# Step 3: Verify corruption by attempting a direct import (reproduces error)
python3 -c "import importlib; importlib.invalidate_caches(); import agent.gemini_native_adapter"

# Step 4: If confirmed corrupted, remove and let Python regenerate
rm -f ${INSTALL_DIR}/agent/__pycache__/gemini_native_adapter.cpython-311.pyc
# Then restart all gateways: hermes gateway run --profile <profile> --replace
```

**Correlation pattern:** `SessionDB` warnings (`database or disk is full`) often precede `.pyc` corruption events within minutes. Check `errors.log` for both patterns in close temporal proximity to identify root cause (disk pressure → partial writes → corrupted bytecode).

**Impact scope:** A single corrupted core adapter `.pyc` can cascade: session_summarization failures → marshal errors → multiple agent profiles affected simultaneously (YoYo, Gentech, etc.) even if only one profile's gateway is restarted. Restart all gateways after fix.

### Cron Dispatch Stasis — Ticker Running But Jobs Not Executing

**Symptoms:**
- Gateway logs show `Cron ticker started (interval=60s)` and no `Cron ticker stopped`
- `jobs.json` shows enabled jobs with `next_run_at` in the past
- `last_run_at` remains `null` and `last_status` is `null` across all jobs
- `~/.hermes/profiles/<profile>/cron/output/<job_id>/` directories are empty or contain only very old files
- `hermes cron status` reports gateway running but jobs never fire

**Diagnostic sequence:**
```bash
# 1. Confirm cron output absence across all profiles
find ${PROFILES_DIR} -path '*/cron/output/*/*.md' -mmin -120 2>/dev/null

# 2. Inspect live jobs metadata to see if next_run_at is advancing
python3 -c "
import json, glob, datetime
for f in glob.glob('${PROFILES_DIR}/*/cron/jobs.json'):
    with open(f) as fh: data = json.load(fh)
    p = f.split('/')[-3]
    for j in data.get('jobs',[]):
        if not j.get('enabled'): continue
        print(f'{p} | {j[\"id\"][:12]} | {j[\"name\"][:35]:<35} | next={j.get(\"next_run_at\")} | last={j.get(\"last_run_at\")}')
"

# 3. Search gateway logs for execution entries (not just ticker)
grep -E 'running job|job executed|Cron ticker' ${PROFILES_DIR}/*/logs/gateway.log | tail -20
```

**Root causes (ranked):**
1. **Gateway zombie** — scheduler thread crashed but process remains. Look for `Cron ticker stopped` in logs without a subsequent `started`. Fix: `hermes gateway run --profile <p> --replace`.
2. **Cron subsystem not initialized** — older Hermes versions require explicit `--cron` flag or the cron module failed to load. Check `errors.log` for `cron.scheduler` import errors. Fix: restart gateway with `--cron` or upgrade.
3. **Job cache desync** — manual edit to `jobs.json` or file corruption left in-memory cache stale. Fix: restart all gateways to force reload.
4. **System clock jump** — NTP adjustment shifted system time causing ticker to skip computed run times. Fix: verify `date`; if recently changed, restart gateway.
5. **Timezone misconfiguration** — `TZ` environment changed; UTC vs local confusion locks `next_run_at` in the future. Fix: standardize UTC across all profiles; restart.

**Immediate recovery:** Restart all agent gateways simultaneously to resync scheduler state:
```bash
hermes gateway run --profile yoyo --replace
hermes gateway run --profile dmob --replace
hermes gateway run --profile desmond --replace
hermes gateway run --profile gentech --replace
```

**Post-restart verification:** Within one schedule interval, new `.md` execution logs should appear under each job's output directory. Confirm with:
```bash
find ${PROFILES_DIR} -path '*/cron/output/*/*.md' -mmin -60 -ls
```

### Session Database Corruption
- `sqlite3.DatabaseError: file is not a database` when session_search or other tools read the session index.
- Distinct from `jobs.json` corruption; affects session history queries only, not cron execution.
- Fix: if session index is rebuilt from history files, delete the corrupted DB and restart Hermes to recreate. Path: `~/.hermes/sessions/sessions.db` or profile-specific session storage.

### Model / Catalog Unavailable (HTTP 404)
- `Error code: 404 - {'status': 404, 'message': "Model 'provider/model:tag' not found. The requested model does not exist in our configuration or OpenRouter catalog."`
- Provider/catalog misconfiguration or model retirement. Affects all jobs using that model simultaneously.
- Fix: update model string to a valid, available model; check provider configuration; run `hermes models` to verify.

### Credential Cascade Failures
- Multiple concurrent auth failures across different providers within a short window: revoked refresh sessions (`Refresh session has been revoked`), missing API keys (`No Anthropic credentials found`), invalid keys (`Invalid API key` from ElevenLabs).
- Often appears after token expiry, profile migration, or environment reset.
- Fix: re-authenticate each provider: `hermes model` (OpenRouter), `claude /login` (Anthropic), `copilot login` (GitHub), reconfigure paid-service keys in environment/config.

### Systemic Provider Outage (Clustered Empty Responses)
- Multiple jobs across multiple agents fail simultaneously with: `Agent completed but produced empty response (model error, timeout, or misconfiguration)`.
- Distinct from isolated empty responses; suggests provider-side load-shedding, outage, or model deployment issue.
- Fix: verify provider status page; if transient, next scheduled run usually recovers; if persistent, switch to alternate provider or model.

### YAML Syntax Error at Gateway Startup
- `yaml.scanner.ScannerError: mapping values are not allowed here` with file/line/column info in config.yaml.
- Prevents gateway from starting or causes repeated crash/restart loops.
- Validate: `python3 -c "import yaml; yaml.safe_load(open('${PROFILES_DIR}/<profile>/config.yaml'))"`.
- Fix: inspect line and preceding lines for incorrect indentation or missing colon; correct YAML structure.

## Pitfalls

- **Don't rely solely on `cronjob list`**. It only shows metadata. Always check `cron/output/` directories to confirm execution actually produced output.
- **Don't conflate "no new output" with "job failed."** Some jobs are designed to return `[SILENT]` when nothing is new. Check the `.md` file content — if the last line says `[SILENT]` and earlier lines show healthy reasoning, it's fine.
- **Cross-profile jobs with same IDs** — some jobs (`9ecfada01952`) exist in multiple profiles. Be explicit about which profile the alert refers to.
- **Disabled / paused jobs** — intentionally paused jobs (`enabled: false`) should NOT trigger alerts unless they were paused unexpectedly.
- **Time zones** — `last_run_at` and `next_run_at` are in ISO 8601 UTC. Always compare against `datetime.now(timezone.utc)`.

## Verification

After running the workflow, confirm:
- [ ] All agent profiles inspected (not just the running profile).
- [ ] Every `last_status: error` flagged in the report.
- [ ] Every stale `next_run_at` flagged in the report.
- [ ] Error-keyword grep results reviewed, not just counted.
- [ ] Report is either exactly `STATUS:OK` or contains actionable alerts with job IDs.
