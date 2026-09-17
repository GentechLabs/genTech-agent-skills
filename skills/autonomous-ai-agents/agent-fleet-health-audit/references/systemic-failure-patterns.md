# Systemic Failure Patterns

Canonical signatures of fleet-wide degradation observed in Hermes deployments.

## 1. Bytecode Corruption (Marshal Errors)

**Signature:** `EOFError: marshal data too short` during import of `agent.copilot_acp_client` or other modules.

**Root Causes:**
- Disk pressure ≥80% causing incomplete `.pyc` writes
- Interrupted deployment/update while bytecode compilation in progress
- Shared library corruption across `${INSTALL_DIR}/`

**Diagnostic:**
```bash
# Scan for corrupted .pyc files
find ${INSTALL_DIR} -name "*.pyc" -exec python -m py_compile {} \; 2>&1 | grep -i marshal

# Check error logs for pattern
grep -R "marshal data too short" ~/.hermes/profiles/*/logs/errors.log
```

**Remediation:**
1. Stop all agent gateways
2. Delete `__pycache__` directories: `rm -rf ${INSTALL_DIR}/**/__pycache__/`
3. Restart all gateways to force clean recompilation
4. Verify: no new marshal errors in logs after 5 minutes

**Fleet Impact:** All agents importing the corrupted module fail simultaneously. Session summarization, ACP client, and any tool depending on the module break.

---

## 2. Master Orchestration Service Down

**Signature:** `hermes-gateway.service` failed with `status=203/EXEC` and `Start request repeated too quickly`.

**Root Cause:** ExecStart path mismatch — systemd unit points to non-existent Python venv.

**Diagnostic:**
```bash
systemctl --user status hermes-gateway.service
cat ~/.config/systemd/user/hermes-gateway.service | grep ExecStart
which python3  # verify actual venv path
```

**Fix:**
```bash
# Update ExecStart to correct path (typically ${INSTALL_DIR}/venv/bin/python)
sed -i 's|/root/.hermes/hermes-agent/venv/bin/python|${INSTALL_DIR}/venv/bin/python|' ~/.config/systemd/user/hermes-gateway.service
systemctl --user daemon-reload
systemctl --user start hermes-gateway.service
```

**Fleet Impact:** NO cron jobs execute across ANY agent, regardless of per-agent gateway state.

---

## 3. Disk Pressure ≥80%

**Signature:** `df -h` shows `/` or `/var` ≥80% usage. Concurrently, bytecode corruption and session database failures appear.

**Thresholds:**
- 80–90%: Critical — immediate cleanup required
- >90%: Emergency — services degrade rapidly

**Diagnostic:**
```bash
df -h /
du -sh ~/.hermes/sessions/* | sort -rh | head -10  # largest session files
```

**Remediation:**
- Rotate/compress old session logs: `hermes sessions vacuum --days 30`
- Clean Docker overlay cache if applicable
- Remove unused `.pyc` and temporary files

**Fleet Impact:** SessionDB corruption, failed bytecode writes, eventual read-only filesystem errors.

---

## 4. Orphaned Cron Jobs (Registry Desync)

**Signature:** Job exists in `~/.hermes/cron/jobs.json` but `hermes cron list` shows it missing or with `profile: None`, `active: None`, `last_run_at: null`.

**Root Cause:** Cron registry cache out of sync with jobs.json; jobs not loaded into active scheduler.

**Diagnostic:**
```bash
hermes cron list | grep -A3 "<job name>"
grep -A5 "<job name>" ~/.hermes/cron/jobs.json
```

**Recovery:**
```bash
# Option A: Restart master gateway service to reload registry
systemctl --user restart hermes-gateway.service

# Option B: Manually re-add job via hermes CLI if needed
hermes cron add --name "<name>" --schedule "<cron>" --profile <profile>
```

**Fleet Impact:** Affected agents never execute scheduled tasks, creating silent automation gaps.

---

## 5. Fleet-Wide TTS Credential Failure

**Signature:** All agents log `elevenlabs.core.api_error.ApiError: status_code: 401` with `Invalid API key`.

**Root Cause:** Single ElevenLabs API key shared across profiles — expired or revoked.

**Diagnostic:**
```bash
grep -h "ELEVENLABS" ~/.hermes/profiles/*/.env 2>/dev/null | cut -d= -f1 | sort -u
# Check each profile's .env for ELEVENLABS_API_KEY or similar
```

**Remediation:**
1. Obtain new ElevenLabs API key
2. Update ALL agent `.env` files (or central credential store)
3. Restart gateways to pick up new env vars

**Fleet Impact:** All voice output broken; agents can still text-operate but cannot speak.

---

## 6. Coordinated Gateway Restart Cycles

**Signature:** Multiple agent gateways stop/start within same 5-minute window (e.g., all show shutdown diagnostic at identical timestamps).

**Root Cause:** Shared infrastructure failure (bytecode, systemd restart, OOM, disk pressure) triggering coordinated recovery.

**Diagnostic:**
```bash
# Check for simultaneous shutdown messages across agent logs
grep -h "Shutdown diagnostic" ~/.hermes/profiles/*/logs/gateway.log | sort
```

**Action:** Address underlying systemic cause first; per-agent restarts alone won't resolve recurrence.
