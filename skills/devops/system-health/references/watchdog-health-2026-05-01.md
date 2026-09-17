# Watchdog Session Reference — 2026-05-01

## Session Context
- **Watchdog**: Gentech Watchdog cron (every 5 minutes)
- **Profiles scanned**: gentech, dmob, desmond, yoyo
- **Method**: session_search + cron job list + log tail + process check
- **Gateways confirmed running**: all 4 profiles ✅

## Failure Signatures Observed

### 1. Corrupted Bytecode — gemini_native_adapter.pyc

**Error:**
```
EOFError: marshal data too short
  File "${INSTALL_DIR}/agent/auxiliary_client.py", line 1895, in _to_async_client
    from agent.gemini_native_adapter import GeminiNativeClient, AsyncGeminiNativeClient
```

**Affected agents:** gentech, yoyo (recurring in agent.log)

**Impact:** Breaks session summarization and LLM calls that attempt to import the corrupt module. Recovery possible after gateway restart once bytecode is regenerated; persistent corruption suggests filesystem or package install issue.

**Diagnostic:**
```bash
# Find corrupt .pyc files in hermes installation
find ${INSTALL_DIR} -name "*.pyc" -exec python3 -m py_compile {} \; 2>&1 | grep -i "marshal\|EOFError"

# Or attempt manual import test
python3 -c "from agent.gemini_native_adapter import GeminiNativeClient" 2>&1
```

**Fix:**
```bash
# Find and delete the corrupt .pyc, then restart gateway
find ${INSTALL_DIR} -name "gemini_native_adapter.pyc" -delete
hermes gateway run --profile gentech --replace
hermes gateway run --profile yoyo --replace
```

**Notes:** May reappear if package is re-installed from corrupted wheel; check `pip cache` or reinstall hermes-agent cleanly.

---

### 2. Session Database Corruption

**Error:**
```
sqlite3.DatabaseError: file is not a database
  File "${INSTALL_DIR}/tools/session_search_tool.py", line 363, in session_search
    raw_results = db.search_messages(...)
```

**Impact:** `session_search` tool fails; transcript-based diagnostics are impaired. Cron execution otherwise unaffected.

**Location:** likely `~/.hermes/sessions/sessions.db` or profile-specific session index (varies by Hermes version).

**Fix:**
```bash
# Stop gateways, delete/rename corrupted DB, restart to rebuild from raw session files
mv ~/.hermes/sessions/sessions.db ~/.hermes/sessions/sessions.db.bak
# restart all gateways
```

---

### 3. YAML Syntax Error in Profile Config

**Error (observed in yoyo cron status output):**
```
Warning: Failed to load config: mapping values are not allowed here
  in "${PROFILES_DIR}/yoyo/config.yaml", line 130, column 13
```

**Impact:** Gateway may fail to start or load incomplete configuration; jobs may crash on startup.

**Diagnostic:**
```bash
python3 -c "import yaml; yaml.safe_load(open('${PROFILES_DIR}/yoyo/config.yaml'))"
```

**Repair:** Edit the file at the indicated line. Common causes:
- Missing colon after key
- Incorrect indentation (tabs vs spaces; nested mapping not indented)
- Bare value without quotes containing special characters

---

### 4. Credential Cascade Failures (Multiple Providers)

**Errors observed (April 22–24):**
```
RuntimeError: Refresh session has been revoked
  → Run `hermes model` to re-authenticate.

RuntimeError: No Anthropic credentials found.
  → Set ANTHROPIC_TOKEN or ANTHROPIC_API_KEY, run 'claude setup-token', or authenticate with 'claude /login'.

ApiError: status_code: 401, body: {'detail': {'status': 'invalid_api_key', 'message': 'Invalid API key'}}
  → ElevenLabs TTS API key invalid.
```

**Pattern:** Multiple distinct credential failures within a short window (days) across:
- OpenRouter (via `hermes model` refresh token)
- Anthropic (via `claude /login` or ANTHROPIC_TOKEN)
- Third-party APIs (ElevenLabs, GitHub Copilot PAT)

**Root cause hypothesis:** Token expiry, environment variable cleanup, or profile migration/reset. Affected jobs become stuck in `error` state until credentials are restored and jobs re-run.

**Fix checklist:**
```bash
# OpenRouter
hermes model  # re-authenticate via OAuth

# Anthropic
export ANTHROPIC_TOKEN=<token>
# or
claude /login

# ElevenLabs
export ELEVENLABS_API_KEY=<key>  # check profile env or config

# GitHub (Copilot)
gh auth login  # produces gho_* token (fine-grained PAT also acceptable)
```

---

### 5. Systemic Provider Outage — Clustered Empty Responses (April 30 Event)

**Timestamp:** 2026-04-30 ~06:00:32 UTC

**Jobs affected (≥8 across gentech + yoyo):**
- Protocol Due Diligence Chain
- Hermes Agent Daily Sync Check
- Weekly Opportunity Scanner
- Mess Hall — Break 1
- Brain Backup → GitHub
- LayerZero DVN Monitor
- Mess Hall — Daily Rotation
- Gentech Watchdog (09:55:39)

**Error message:**
```
last_status: error
error: Agent completed but produced empty response (model error, timeout, or misconfiguration)
```

**Interpretation:** Not a single-job misconfiguration (spread across agents). Indicates provider-side issue (OpenRouter/stepfun outage or load-shedding) at that window. Corroborating evidence: OpenRouter status page showed elevated error rates; model `minimax/minimax-m2.5:free` returned 404 later that evening (model retired/unavailable).

**Recovery:** Jobs re-ran successfully later (e.g., YoYo Crypto Watchlist at 08:18 OK). Self-healing once provider recovered.

**Watchdog implication:** Flag all affected jobs; do NOT attempt per-job fixes unless errors persist beyond 2–3 intervals. Check provider status externally.

---

### 6. Model Catalog Unavailability (HTTP 404)

**Error:**
```
2026-05-01 23:10:18,577 ERROR ... Non-retryable client error: Error code: 404 -
{'status': 404, 'message': "Model 'minimax/minimax-m2.5:free' not found.
The requested model does not exist in our configuration or OpenRouter catalog."}
```

**Profile:** gentech (session 20260501_231017_aa0d51)

**Impact:** Any job explicitly requesting that model fails immediately with empty response. Silent if model string is dynamic but provider returns 404.

**Fix:** Update the model spec in the job's prompt or configuration:
1. Run `hermes models` to list available models on current provider
2. Replace `minimax/minimax-m2.5:free` with a valid model ID (e.g., `stepfun/step-3.5-flash` or another free-tier option)
3. If job is shared across profiles, update in all affected `jobs.json` entries

---

## Cron Status File Inspection (Current Snapshot)

| Status file | Last modified (UTC) | Notes |
|---|---|---|
| yoyo_cron.txt | 2026-04-30 09:59 | Contains 5 `error: Agent completed but produced empty response` entries (April 30 batch) |
| dmob_cron.txt | 2026-04-30 09:59 | Shows 2 stale auth errors (April 22–24) but no recent failures |
| desmond_cron.txt | 2026-04-30 09:59 | Mostly OK; one stale auth error (April 22) |
| gentech_cron.txt | 2026-04-30 09:59 | Shows 7+ `error: Agent completed but produced empty response` entries (April 30) plus older resolved runs |
| cron_health.txt | 2026-04-30 09:59 | Aggregated health table; indicates multiple agents with last_status error at April 30 06:00 window |

**Note:** Cron status files are only regenerated when `hermes cron list` is executed. The last regeneration was April 30 09:59. Current health state should be verified by inspecting live `jobs.json` and agent logs.

---

## Verification Commands (Post-Update)

```bash
# 1. Confirm gateway processes are alive for all 4 profiles
ps aux | grep hermes | grep gateway

# 2. Check for corrupt .pyc files
find ${INSTALL_DIR} -name "*.pyc" -exec python3 -m py_compile {} \; 2>&1 | head -20

# 3. Quick YAML validation for all profiles
for p in yoyo dmob desmond gentech; do
  echo "=== $p ==="
  python3 -c "import yaml; yaml.safe_load(open('${PROFILES_DIR}/$p/config.yaml'))" 2>&1 || echo "FAIL"
done

# 4. Scan agent logs for the error signatures added to this reference
for p in yoyo dmob desmond gentech; do
  echo "=== $p ==="
  grep -E "EOFError|marshal data|sqlite3.DatabaseError|Refresh session has been revoked|No Anthropic|Invalid API key|Model .* not found" \
    ${PROFILES_DIR}/$p/logs/agent.log 2>/dev/null | tail -5
done

# 5. Count recent error-state cron jobs across profiles
python3 -c "
import json, glob
for jobs_file in glob.glob('${PROFILES_DIR}/*/cron/jobs.json'):
    with open(jobs_file) as f: data = json.load(f)
    profile = jobs_file.split('/')[-3]
    for job in data.get('jobs', []):
        if not job.get('enabled'): continue
        if job.get('last_status') == 'error':
            print(f\"{profile} | {job['id'][:12]} | {job['name']} | {job.get('last_run_at')}\")
"
```

---

## Changelog

- **2026-05-01** — Added: corrupted bytecode, session DB corruption, model 404, credential cascade, clustered empty responses, YAML syntax diagnostic. Updated from Gentech Watchdog health sweep.
