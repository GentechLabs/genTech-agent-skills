---
name: agent-fleet-health-audit
category: autonomous-ai-agents
description: Systematic health checks across Hermes agent fleets — detect systemic vs agent-specific failures, orchestrate recovery, and maintain fleet reliability at scale.
trigger:
  - health check
  - fleet audit
  - agent status
  - watchdog alert
  - systemic failure
  - multiple agents failing
  - incident response
  - service degradation
  - agent tool failure
  - vision tools error
  - 404 error
  - telegram connection failure
  - "Refresh session has been revoked"
  - "Firecrawl client initialization failed"
  - "Copilot ACP command failed"
  - "cron daemon not running"
  - "cron execution pipeline dead"
  - "agent: unknown in session files"
  - "agent: MISSING in session files"
  - "session routing failure"
  - ElevenLabs quota exceeded
  - Model not supported (401 from provider)
  - Model not found (404 from OpenRouter/Nous API)
  - Invalid model identifier across fleet
  - Nous Portal OAuth revoked (fleet-wide)
  - Gateway cascade restart (≥3 agents within 2 minutes)
purpose: >
  Provide a repeatable, comprehensive protocol for diagnosing health across a multi-agent Hermes deployment.
  Distinguishes fleet-wide infrastructure issues (shared libraries, cron orchestration, disk pressure) from
  per-agent problems (credentials, config errors, process crashes). Establishes clear escalation paths
  and recovery sequences.
steps:
  - name: Scope the fleet
    goal: "Identify which agents are affected and whether the failure is systemic or isolated"
    actions:
      - "Enumerate all agent profiles from vault/team-roster or `hermes profile list`"
      - "Check if failures span ≥3 agents → jump to Systemic Failure Protocol"
      - "If 1–2 agents affected → proceed with Per-Agent Diagnostics"
  - name: Per-Agent Diagnostics (isolated failures)
    goal: "Gather agent-specific health signals without assuming shared causation"
    actions:
      - "Inspect recent error logs: `~/.hermes/profiles/<agent>/logs/errors.log` (last 2h, last 50 lines)"
      - "Quantify error patterns: count occurrences of key types (marshal, 401, YAML parse, connection refused) to classify failure mode"
      - "Check gateway process: `ps aux | grep hermes_cli.main --profile <agent>` THEN verify uptime: `ps -p <pid> -o lstart,etime` — recent start (<5m) may indicate restart; correlate with update.log to distinguish scheduled vs crash-induced"
      - "Verify Telegram connectivity: review gateway.log for connect/disconnect cycles and sent/received messages; transient 'Bad Gateway' with 'polling resumed' within 30s is self-recovering"
      - "Check cron registration: `hermes cron list` and cross-reference with `~/.hermes/cron/jobs.json`; validate actual execution via brain-backup.log mtime or `find ~/.hermes/cron/output -mmin -60`"
      - "Scan session transcripts via `session_search` for agent name + keywords: error, crash, failed, exception, marshal"
      - "Flag patterns: repeated 401s (credentials), EOFError/marshal (bytecode), YAML parse errors (config)"
      - "If session_search itself fails with marshal errors, agent is affected by shared bytecode corruption"
      - "Guard against false positives: errors referencing old session IDs (session_id date < today) are cleanup artifacts — ignore unless error appears in current session context"
  - name: Systemic Failure Protocol (multiple agents affected)
    goal: "Diagnose shared infrastructure before per-agent details to avoid wasted effort"
    actions:
      - "Inspect shared library bytecode: check `${INSTALL_DIR}/**/__pycache__/` for corruption; flag files with size 16–48 KB and modtime <24h that contain module names: copilot_acp_client, gemini_native_adapter, moonshot_schema, context_engine, title_generator"
      - "Check disk pressure: `df -h` — if ≥80%, session database and bytecode writes at risk; prioritize cleanup"
      - "Verify master orchestration service: `systemctl --user status hermes-gateway.service` — inspect ActiveEnterTimestamp to detect long-duration failures (days)"
      - "Validate systemd unit ExecStart path: `systemctl --user cat hermes-gateway.service` and confirm venv path matches actual (`${INSTALL_DIR}/venv/bin/python` vs `/root/.hermes/...`) — mismatch requires immediate fix"
      - "Cross-check gateway process reality: run `ps aux | grep hermes_cli.main` to detect MANUAL gateway processes running outside systemd; these bypass auto-restart and need explicit termination before systemd repair"
      - "Detect orphaned gateways post-update: if profiles exist on disk but systemd units are inactive (dead) with exit code 0/SIGTERM, AND no manual processes found, check for recent update.log entries — update restart may have killed gateways without respawning them if profile directories went missing"
      - "Verify profile directory integrity: `ls -la ~/.hermes/profiles/<agent>` — absence of config.yaml/auth.json/secrets indicates profile deletion or incomplete profile sync; check gateway.log for \"profile dir deleted\" or \"profile does not exist\" errors"
      - "Validate cron registry health: check `~/.hermes/cron/jobs.db` filesize — if 0 bytes, the active registry is corrupted; cross-check `hermes cron list --all` against raw `jobs.json` to recover counts and statuses"
      - "Review active cron registry: `hermes cron list` vs raw `~/.hermes/cron/jobs.json` parsing; look for orphaned jobs (profile: null, active: null, last_run_at: null) that will never execute"
      - "Detect cron profile orphaning: scan global jobs.json for entries with `profile: ?` or `profile: null` — these jobs are blocked from dispatch; see `references/cron-profile-orphaning.md`"
      - "Check for cross-contamination in agent-level cron files: jobs belonging to other agents will fail; validate each job's `origin` field matches the agent profile"
      - "Quantify per-agent error totals from errors.log — flag agents with >500 total errors as critically degraded; correlate with recent error frequency (last 2h) to distinguish stale from active failures"
      - "Check for fleet-wide credential failures (ElevenLabs, Anthropic, OpenAI, Firecrawl) across all agents via `grep -h 'status_code: 401' ~/.hermes/profiles/*/logs/errors.log | wc -l` and `grep -h 'Firecrawl client initialization failed' ~/.hermes/profiles/*/logs/errors.log | wc -l`"
      - "Check cron execution evidence: `find ~/.hermes/cron/executions -type f -mmin -90` — zero files means no jobs actually executed despite 'active' status. Also validate `~/.hermes/cron/output/` recency if executions dir empty"
      - "Validate cron database integrity: inspect `~/.hermes/cron/cron.db` and `jobs.db` — if filesize 0 bytes or SQLite reports 'no such table'/'empty', the active registry is corrupted. Scheduler will skip all jobs"
      - "Verify cron daemon process presence: `ps aux | grep hermes.*cron` or `systemctl --user status hermes-cron.service`. If no daemon process found, cron dispatch is non-functional regardless of registry state. Also check `~/.hermes/cron/jobs.json` structure — it may be a dict with 'jobs' key, not a direct list"
      - "Detect session routing failure: scan recent session files with `session_search` or direct file inspection; if majority report `agent: unknown` or `profile: unknown`, the session identification pipeline is broken. Correlate with gateway.log for 'agent tag' parsing errors"
      - "Run `hermes cron list --all` to expose jobs hidden by filtering; compare total count against sum of per-agent expected jobs"
  - name: Model Resolution Validation
    goal: "Detect and diagnose systemic model configuration failures across the fleet"
    actions:
      - "Verify model identifier validity: Check agent config.yaml for `model.default` field — validate against provider's model catalog (OpenRouter `/models` or provider API) to confirm model exists"
      - "Test OpenRouter API key accessibility: Ensure `OPENROUTER_API_KEY` is present in each agent's environment (check `.env` file and running process environment via `/proc/<pid>/environ`)"
      - "Validate fallback chain configuration: Confirm `fallback_providers` are properly defined and credentials available for each fallback (openai, anthropic, ollama keys as needed)"
      - "Check provider-specific model availability: Query provider APIs directly with access tokens to confirm model exists and is accessible to this account"
      - "Compare global vs agent config drift: Cross-check `~/.hermes/config.yaml` model settings against per-agent `config.yaml` to identify misalignment"
  - name: Correlate and classify
    goal: "Categorize each finding as Systemic or Agent-Specific to prioritize remediation"
    actions:
      - "SYSTEMIC if present in ≥3 agents: bytecode corruption, master hermes-gateway.service down, disk pressure ≥80%, revoked master Telegram sessions"
      - "AGENT-SPECIFIC if isolated: missing env vars, YAML syntax errors, profile misconfiguration, agent-only gateway crashes"
      - "ORPHANED CRON if job exists in jobs.json but not in active registry (profile: None, active: None)"
  - name: Report with escalation clarity
    goal: "Communicate severity, root cause, and required actions unambiguously"
    template: |
      🚨 Watchdog Alert: [one-sentence systemic summary]

      Agents affected: [list]
      Systemic issues: [shared infrastructure problems]
      Per-agent blockers: [credential gaps, config errors, orphaned cron]

      Required actions:
      1. [urgent infrastructure fix]
      2. [per-agent remediation]
      3. [validation step]

      Next check: [time]
pitfalls:
  - "Do not report 'STATUS:OK' unless ALL agents have no active errors and cron jobs are executing"
  - "If systemic failure detected, STOP per-agent deep dives and repair infrastructure first"
  - "Orphaned cron jobs (profile: null, active: null in jobs.json) will never execute — they are not 'just misconfigured', they are blocked by the scheduler pipeline"
  - "Jobs with profile literally set to '?' (question mark) are also orphaned — this indicates missing assignment during creation"
  - "Corrupted bytecode deleted from disk remains in memory — gateway RESTART required after cleanup"
  - "Master hermes-gateway.service failure blocks ALL cron dispatch regardless of per-agent gateway state"
  - "Always verify ExecStart path in systemd unit: `systemctl --user cat hermes-gateway.service` — mismatch between configured venv path and actual location is a common cause of silent service failure"
  - "401 errors from ElevenLabs indicate expired API key — affects ALL agents using TTS, not just one. When quota_exceeded appears, key is invalid or out of funds"
  - "Single errors referencing old session IDs (session_id date precedes latest gateway restart) are cleanup artifacts — do not treat as active failures"
  - "Telegram 'Bad Gateway' or network errors that self-recover within 30 seconds are transient infrastructure blips — monitor but do not escalate unless pattern repeats"
  - "All agents restarting in same 2-minute window usually means scheduled update — verify update.log completion before diagnosing as crash loop"
  - "Process list may show MANUAL gateway processes even when systemd units appear inactive — check BOTH `ps aux | grep hermes_cli.main` AND `systemctl --user status hermes-gateway-<agent>`; manual processes bypass systemd and won't auto-restart"
  - "Jobs.db corruption signature: `~/.hermes/cron/jobs.db` or `cron.db` filesize of 0 bytes OR SQLite 'no such table' errors means the active registry is unreadable. Cron dispatcher will skip all jobs; recover by rebuilding from jobs.json"
  - "Profile deletion cascade: after an update-triggered restart, if systemd units are enabled but gateways fail to come back up, verify `~/.hermes/profiles/<agent>/` still contains `config.yaml`, `auth.json`, `secrets/`. If missing, gateway watchers cannot relaunch; systemd will not create a profile from nothing"
  - "Do not trust 'process running' alone: ElevenLabs TTS `401` errors in ALL agents point to a fleet-wide credential expiration, not per-agent misconfiguration. Check `~/.hermes/profiles/*/secrets/` or shared config for common TTS provider key"
  - "DMOB-specific blocker: missing `ANTHROPIC_TOKEN` or `ANTHROPIC_API_KEY` in `.env` produces `RuntimeError: No Anthropic credentials found` and blocks any agent run using Claude models. Verify with `grep -E 'ANTHROPIC_(TOKEN|API_KEY)' ~/.hermes/profiles/dmob/.env`"
  - "Manual vs systemd process distinction: a running `python -m hermes_cli.main --profile <agent>` found via `ps` does NOT guarantee systemd management. Check `systemctl --user status hermes-gateway-<agent>` — if 'inactive (dead)' while process exists, it's a manual/leftover gateway not under systemd; these won't auto-restart on failure or updates"
  - "Update restart signature: all manual gateways exiting simultaneously with exit code 0 within milliseconds of each other, followed by gateway.log entries about 'update' or '.update_check', indicates a coordinated update restart — not a crash. If they don't relaunch within 120s, investigate profile directory presence and watcher process cleanup"
  - "Error accumulation thresholds: agents with >500 total historical errors (especially >100 recent) are critically degraded; prioritize credential rotation and gateway restart before investigating individual job failures"
  - "Cron execution pipeline dead signature: `hermes cron list` shows jobs as 'active' but `~/.hermes/cron/executions/` is empty (0 files) AND cron daemon process absent (`ps aux | grep hermes.*cron` returns nothing). Indicates the cron dispatcher daemon is not running — a different failure mode than just an orphaned job. Fix: ensure cron daemon is launched (usually bundled in gateway service or run separately)"
  - "Cron DB empty/0-byte filesize: `~/.hermes/cron/cron.db` or `jobs.db` size 0 bytes means registry corruption; `sqlite3` will report 'no such table'. Scheduler cannot dispatch any jobs. Rebuild active registry from `~/.hermes/cron/jobs.json` after repairing DB"
  - "Do not trust `pgrep` alone for process liveness: temporary hermes subprocesses (sandbox scripts, timeouts, drain handlers) can return matching PIDs. Always validate PID via `ps -p <pid> -o stat,cmd` and cross-check with gateway.log last-entry timestamp"
  - "Master service 'disabled' flag: `systemctl --user status` showing 'disabled' means the unit won't auto-restart on failure or reboot even if loaded — run `systemctl --user enable --now hermes-gateway.service` after fixing ExecStart"
  - "Cron job 'last_run_at: null' combined with 'enabled: true' and 'state: scheduled' indicates the job never executed — not just overdue. Check cron daemon process presence (`ps aux | grep hermes.*cron`) and executions directory for any output files"
  - "Bytecode corruption signature: recently modified (<24h) `.pyc` files with sizes 16–100 bytes in `${INSTALL_DIR}/agent/__pycache__/` and `tools/__pycache__/` bearing module names `copilot_acp_client`, `gemini_native_adapter`, `moonshot_schema`, `context_engine`, `title_generator` — these are high-risk; purge entire `__pycache__` tree and restart gateways"
  - "If `hermes cron list` returns empty, verify the cron daemon is running (`ps aux | grep hermes.*cron` or `systemctl --user status hermes-cron.service`); empty output often indicates the cron process is down rather than no jobs registered"
  - "Master service 'disabled' flag: `systemctl --user status` showing 'disabled' means the unit won't auto-restart on failure or reboot even if loaded — run `systemctl --user enable --now hermes-gateway.service` after fixing ExecStart"
  - "Cron job 'last_run_at: null' combined with 'enabled: true' and 'state: scheduled' indicates the job never executed — not just overdue. Check cron daemon process presence (`ps aux | grep hermes.*cron`) and cron.log existence per agent"
  - "Jobs.db corruption signature: `~/.hermes/cron/jobs.db` filesize of 0 bytes means the SQLite registry is unreadable. Cron dispatcher will skip all jobs; recover by rebuilding from jobs.json"
  - "Profile deletion cascade: after an update-triggered restart, if systemd units are enabled but gateways fail to come back up, verify `~/.hermes/profiles/<agent>/` still contains `config.yaml`, `auth.json`, `secrets/`. If missing, gateway watchers cannot relaunch; systemd will not create a profile from nothing"
  - "Do not trust 'process running' alone: ElevenLabs TTS `401` errors in ALL agents point to a fleet-wide credential expiration, not per-agent misconfiguration. Check `~/.hermes/profiles/*/secrets/` or shared config for common TTS provider key"
  - "DMOB-specific blocker: missing `ANTHROPIC_TOKEN` or `ANTHROPIC_API_KEY` in `.env` produces `RuntimeError: No Anthropic credentials found` and blocks any agent run using Claude models. Verify with `grep -E 'ANTHROPIC_(TOKEN|API_KEY)' ~/.hermes/profiles/dmob/.env`"
  - "Manual vs systemd process distinction: a running `python -m hermes_cli.main --profile <agent>` found via `ps` does NOT guarantee systemd management. Check `systemctl --user status hermes-gateway-<agent>` — if 'inactive (dead)' while process exists, it's a manual/leftover gateway not under systemd; these won't auto-restart on failure or updates"
  - "Update restart signature: all manual gateways exiting simultaneously with exit code 0 within milliseconds of each other, followed by gateway.log entries about 'update' or '.update_check', indicates a coordinated update restart — not a crash. If they don't relaunch within 120s, investigate profile directory presence and watcher process cleanup"
  - "Error accumulation thresholds: agents with >500 total historical errors (especially >100 recent) are critically degraded; prioritize credential rotation and gateway restart before investigating individual job failures"
  - "Update restart signature: all manual gateways exiting simultaneously with exit code 0 within milliseconds of each other, followed by gateway.log entries about 'update' or '.update_check', indicates a coordinated update restart — not a crash. If they don't relaunch within 120s, investigate profile directory presence and watcher process cleanup"
  - "If `hermes cron list` returns empty, verify the cron daemon is running (`ps aux | grep hermes.*cron` or `systemctl --user status hermes-cron.service`); empty output often indicates the cron process is down rather than no jobs."
references:
  - path: references/systemic-failure-patterns.md
    description: "Canonical signatures of fleet-wide degradation (bytecode corruption, service path mismatches, disk pressure thresholds)"
  - path: references/cron-orphaning.md
    description: "Why jobs.json entries become orphaned (profile: null, active: null) and how to revive them"
  - path: references/cron-profile-orphaning.md
    description: "Detecting jobs with missing profile assignments (profile: ? or null) that block cron dispatch"
  - path: references/bytecode-corruption-recovery.md
    description: "Step-by-step: diagnose marshal errors, clear __pycache__, restart gateway processes"
  - path: references/credential-failure-thresholds.md
    description: "Error count thresholds for escalation (YoYo>2500, DMOB>500, Gentech>1000 total errors) and fleet-wide TTS credential rotation"
  - path: references/operational-patterns.md
  - "Error accumulation thresholds: agents with >500 total historical errors (especially >100 recent) are critically degraded; prioritize credential rotation and gateway restart before investigating individual job failures"
  - "Session routing failure pattern: When the majority of recent session files show `agent: unknown` or `profile: unknown`, the session identification/injection pipeline is broken. Check gateway.log for 'agent tag' parsing errors and verify hermes-cron is injecting agent context correctly"
  - "Cron registry structure: `~/.hermes/cron/jobs.json` may be a dict with a 'jobs' key, not a direct list — parse accordingly. Absence of cron daemon process (`ps aux | grep hermes.*cron`) means no jobs will execute regardless of registry state"
  - path: references/watchdog-findings-2026-05-02.md
    description: "Incident post-mortem: May 02 2026 multi-agent outage — corrupted bytecode signatures, orphaned cron root causes, ExecStart path mismatch, fleet-wide TTS failure, recovery sequence"
  - path: references/fleet-credentials-failure-patterns.md
    description: "Canonical signatures of provider-wide credential expiration (ElevenLabs 401, Anthropic missing token) and remediation recipe"
  - path: references/model-resolution-failures-2026-05-04.md
    description: "Fleet-wide 404 model not found errors — invalid model identifiers, OpenRouter catalog validation, config sync across agents, OPENROUTER_API_KEY per-agent env setup"
  - path: references/agent-routing-cron-failure-2026-05-05.md
    description: "May 05 2026 incident — session routing breakdown (agent: unknown), missing cron daemon, and model 404 errors across fleet"
  - path: references/session-routing-failure-modes.md
    description: "Two severity levels of session routing failure: agent 'unknown' (pipeline broken) vs agent key MISSING entirely (no context injection at all)"
  - path: references/watchdog-execution-pitfalls.md
    description: "Practical execution pitfalls: HOME path trap, security scanner pipe blocks, false clean signals after restart, deduplication notes"
templates: []
scripts:
  - verify_bytecode_integrity.py
validation:
  - "After fixes: `hermes cron list` shows all expected agent jobs (active, with last_run timestamps)"
  - "`ps aux | grep hermes_cli.main` shows all agent gateways running without repeated restarts; process uptime > 5m for stable agents"
  - "Error logs for each agent show zero entries for ≥30 minutes"
  - "Systemd service `hermes-gateway.service` reports active (running) with correct ExecStart path"
  - "brain-backup.log modified within last cron interval; `~/.hermes/cron/output/` contains recent job output files"
  - "No transient errors (Telegram Bad Gateway, rate limits) occurring more than 3× per hour"
  - "Model resolution verified: `grep 'model:' ~/.hermes/profiles/*/config.yaml` shows valid provider/model identifiers matching active provider credentials"
  - "Provider API keys present: `grep 'OPENROUTER_API_KEY' ~/.hermes/profiles/*/.env` returns no empty results for active agents"
---
# Agent Fleet Health Audit

Comprehensive multi-agent health diagnostic and recovery protocol for Hermes deployments.

## Quick Triggers
- Run immediately when ≥2 agents report errors simultaneously
- Use for scheduled watchdog cron jobs (every 5–15 minutes)
- Execute after any system upgrade or infrastructure change

## Decision Tree
```
Multiple agents failing? → Check systemic layer first:
  ├─ hermes-gateway.service up? → Fix path, restart
  ├─ Disk pressure ≥80%? → Cleanup, rotate logs
  ├─ Shared __pycache__ corrupted? → Delete .pyc, restart all gateways
  └─ Cron registry mismatch? → Rebuild from jobs.json
```

## Reference Signals
See `references/systemic-failure-patterns.md` for canonical error patterns and their fleet-wide implications.
