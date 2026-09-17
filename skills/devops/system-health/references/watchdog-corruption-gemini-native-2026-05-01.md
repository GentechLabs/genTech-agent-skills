# Reference: 2026-05-01 Watchdog Health Sweep — Corrupted .pyc Incident

**Date:** 2026-05-01  **Trigger:** Repeated `marshal data too short` errors in Gentech, YoYo, DMOB, Desmond agent logs.  **Root Cause:** Corrupted `gemini_native_adapter.cpython-311.pyc` at `${INSTALL_DIR}/agent/__pycache__/`.  **Secondary Factor:** Earlier `SessionDB` disk-full warning on 2026-05-01 10:17:45 (`database or disk is full`).

---

## Error Pattern Timeline

| Timestamp | Agent | Error |
|-----------|-------|-------|
| 2026-05-01 10:17:45 | Gentech | `WARNING cli: Failed to initialize SessionDB — session will NOT be indexed for search: database or disk is full` |
| 2026-05-01 10:17:45 | (System) | `gemini_native_adapter.pyc` modified (16KB written) |
| 2026-05-01 23:10:18-23:16:16 | Gentech & YoYo | `ERROR: Model 'minimax/minimax-m2.5:free' not found` (OpenRouter 404) |
| 2026-05-01 23:50:52+ | YoYo & Gentech | `WARNING: Session summarization failed after 3 attempts: marshal data too short` (×120 in errors.log.1 across cron job `cron_9ecfada01952`) |

---

## Extended Recovery Timeline (2026-05-02)

| Timestamp | Event |
|-----------|-------|
| 2026-05-01 17:15:07 | First marshal error logged (Gentech) — degradation begins |
| 2026-05-01 23:25:31 | Repeated import failures across all agents (PIDs 899618, 899631, 899554, 899540) |
| 2026-05-02 00:01:36–00:01:39 | Final marshal errors logged (Gentech PID 899618, YoYo PID 899631) |
| 2026-05-02 00:02:14 | `gemini_native_adapter.cpython-311.pyc` regenerated (size: 47KB, timestamp updated) |
| 2026-05-02 00:02+ | No further marshal errors; session summarization restored across all profiles |

**Total degradation window:** ≈ 7 hours (17:15 → 00:02).

---

## Key Diagnostic Commands Used

```bash
# Count marshal errors per agent
grep -c "marshal data too short" ${PROFILES_DIR}/*/logs/errors.log*

# Check agent process health
ps aux | grep hermes | grep -v grep

# Inspect .pyc size and timestamp for gemini adapter
ls -lh ${INSTALL_DIR}/agent/__pycache__/gemini_native_adapter*.pyc

# Attempt import to reproduce marshal error (verifies corruption)
python3 -c "import importlib; importlib.invalidate_caches(); import agent.gemini_native_adapter"

# Verify source vs .pyc modification times
stat ${INSTALL_DIR}/agent/gemini_native_adapter.py
stat ${INSTALL_DIR}/agent/__pycache__/gemini_native_adapter.cpython-311.pyc

# Check gateway connection status for all agent profiles
tail -15 ${PROFILES_DIR}/yoyo/logs/gateway.log
tail -15 ${PROFILES_DIR}/dmob/logs/gateway.log
tail -15 ${PROFILES_DIR}/desmond/logs/gateway.log
```

---

## Corrupted File Evidence

```
File: ${INSTALL_DIR}/agent/__pycache__/gemini_native_adapter.cpython-311.pyc
Initial size: 16384 bytes (16KB)  — written 2026-05-01 10:17:45
Regenerated size: 47000+ bytes (47KB) — written 2026-05-02 00:02:14
Source .py: 33820 bytes, modified Mon Apr 27 22:52:12 2026

Import attempt output (from corrupted .pyc):
EOFError: marshal data too short
  File "${INSTALL_DIR}/agent/auxiliary_client.py", line 1895, in _to_async_client
    from agent.gemini_native_adapter import GeminiNativeClient, AsyncGeminiNativeClient
```

**Correction:** The `__pycache__` directory **was** present throughout at `${INSTALL_DIR}/agent/__pycache__/`. The earlier note about invisibility was inaccurate — the directory was accessible via `ls -la` and contained the corrupted `.pyc`.

**Bytecode size expectation:** Valid `gemini_native_adapter` bytecode is ~47KB (consistent with 33.8KB source). A size <20KB is a strong indicator of truncation/corruption.

---

## Systemic Impact Confirmation

All four agent gateways exhibited identical stack traces because they **share a single Hermes installation** at `${INSTALL_DIR}/`. The corrupted `.pyc` resides in the shared `agent/__pycache__/`, so any process importing `agent.gemini_native_adapter` fails, regardless of profile.

**Affected PIDs (2026-05-02 00:01):**
- Gentech: 899618
- YoYo: 899631
- DMOB: 899554
- Desmond: 899540

**Impact:** Session search and summarization disabled for all agents; other tools unaffected. Cron jobs continued to run but any task invoking `session_search` produced un-summarized results (`[Raw preview — summarization unavailable]`).

---

## Secondary Issues Discovered (Non-Cron)

| Agent | Error Count | Primary Error |
|-------|-------------|---------------|
| YoYo | 777 (50+ marshal) | Corrupted `.pyc` causing session summarization failures. |
| DMOB | 230 (6 Anthropic) | `No Anthropic credentials found.` Claude models unavailable. |
| Desmond | 191 (186 TTS) | ElevenLabs TTS `401 Invalid API key`. |
| Gentech | 130+ marshal | Same `.pyc` corruption root cause. |

---

## Recovery Steps (Applied)

1. **Verify corruption scope** — confirmed `gemini_native_adapter.cpython-311.pyc` fails import.
2. **Remove corrupted bytecode** — `rm -f ${INSTALL_DIR}/agent/__pycache__/gemini_native_adapter.cpython-311.pyc`
3. **Restart all agent gateways** — triggers fresh `.pyc` regeneration from source:
   ```bash
   hermes gateway run --profile yoyo --replace
   hermes gateway run --profile dmob --replace
   hermes gateway run --profile desmond --replace
   hermes gateway run --profile gentech --replace
   ```
4. **Clear session summarization backpressure** — monitor `errors.log` for continued marshal warnings; should drop to zero within 1-2 cron cycles after restart.

---

## Lessons Learned

1. **`.pyc` corruption is not just a local profile issue** — a single corrupted core adapter in the shared install affects all agent profiles. Always check site-packages `agent/__pycache__` if multiple profiles show identical marshal errors.
2. **Disk-full warnings precede `.pyc` corruption** — the `SessionDB: database or disk is full` message on 2026-05-01 10:17:45 coincided with the 16KB `.pyc` write. Correlated timing suggests disk pressure caused partial write / truncation.
3. **Small `.pyc` sizes are a red flag** — valid `gemini_native_adapter` bytecode is ~47KB; <20KB indicates truncation. Use `find /path/to/package -name "*.pyc" -size -20k` for quick scan.
4. **Import test is the definitive validator** — `python3 -c "import module.path"` reproduces marshal error exactly as the agent sees it, confirming corruption vs transient import issue.
5. **Restart scope** — when core adapters are corrupted, restart **all** gateways (not just the failing profile) because the bad `.pyc` persists in shared Python process memory and filesystem cache across processes until each process restarts.
6. **Session_search coupling** — The `session_search` tool depends on the Gemini adapter for summarization, so its failure degrades session search across all agents even if they aren't using Gemini as their primary model. Core adapter dependencies create hidden coupling points.

---

## Watchdog Decision Log (2026-05-01 → 2026-05-02)

- **YoYo:** 777 total errors (50+ marshal) — active corruption, session summarization degraded.
- **DMOB:** 230 errors, 6× Anthropic auth — missing credentials, separate issue.
- **Desmond:** 191 errors, 186 ElevenLabs 401 — TTS service revoked/invalid key, separate issue.
- **Gentech:** 130+ marshal — same corruption pattern.
- **Connectivity:** All gateways running, Telegram connected. No missed cron runs detected.
- **Verdict:** **ALERT** — `.pyc` corruption is a systemic runtime failure requiring immediate file-system intervention.
