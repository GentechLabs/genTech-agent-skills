# Watchdog Health Check — 2026-05-02

**Agent**: Gentech (Watchdog)
**Scope**: Full system audit across 4 Hermes agents (Gentech, YoYo, DMOB, Desmond)

## Critical Findings

### 1. Orphaned Cron Jobs — High Severity

Four cron jobs are defined in `/root/.hermes/cron/jobs.json` (created 2026-04-30) but are **not loaded** into the active Hermes cron daemon. They have never executed (`last_run_at: null`).

| Job Name | Job ID | Schedule | First Scheduled | Status |
|----------|--------|----------|-----------------|--------|
| Desmond — Creative Sync | 64cfa447b338 | 0 7,19 * * * | 2026-04-30T07:00:00Z | ❌ Missing from active cron |
| Gentech — HQ Daily Update | c578000c1d4a | 0 9 * * * | 2026-04-30T09:00:00Z | ❌ Missing from active cron |
| YoYo — LP Watchlist Check | a47474bb0f0c | 0 6,12,18 * * * | 2026-04-30T06:00:00Z | ❌ Missing from active cron |
| DMOB — Labs Daily Standup | ec74c26ad123 | 0 8,20 * * * | 2026-04-30T08:00:00Z | ❌ Missing from active cron |

**Evidence:**
- `hermes cron list` shows 29 active jobs, none matching the above names/IDs.
- `hermes cron show <id>` returns "argument cron_command: invalid" (wrong subcommand usage also masks visibility).
- All four `next_run_at` timestamps are in the past; these jobs should have fired on 2026-04-30 and daily thereafter.

**Root Cause Analysis:**
- `jobs.json` is the **legacy format** (pre-Hermes 2.x). The active daemon reads from `state.db`.
- Jobs may have been created before the gateway was started with `--cron` flag, or the cron daemon cache desynced.
- Possible missing `"profile"` field binding in jobs.json preventing per-agent loading.
- Config `cron_mode: deny` (found in `/root/.hermes/config.yaml`, line 351) may block execution unless explicitly overridden per-job.

**Immediate Action Required:**
1. Recreate each missing job via `hermes cron create` using the original prompts from `jobs.json`.
2. Verify each job has `--profile <agent>` binding (Desmond, Gentech, YoYo, DMOB respectively).
3. If `cron_mode: deny` is intentional, use `hermes cron approve <id>` once per job; or change config to `cron_mode: allow` and restart all gateways.

---

### 2. External Service Failures

#### OpenRouter Model Not Found (404)
- **Model**: `minimax/minimax-m2.5:free` — removed from OpenRouter catalog.
- **Impact**: Multiple sessions (2026-05-01 and 2026-05-02) failing with:
  ```
  ERROR [session] Non-retryable client error: Error code: 404 — Model 'minimax/minimax-m2.5:free' not found
  ```
- **Action**: Update all skill configs, script constants, and session prompts to use a currently-valid OpenRouter model slug. Run `hermes model` to refresh active model routing.

#### GitHub Copilot Authentication (Classic PAT Rejection)
- **Error**: `Token from GITHUB_TOKEN is not supported: Classic Personal Access Tokens (ghp_*) are not supported by the Copilot API`
- **Impact**: Copilot integration broken for affected profiles.
- **Fix**: Generate a fine-grained PAT (`github_pat_*`) with `Copilot Requests` permission, or use OAuth flow via `gh auth login`.

#### Rate Limiting (HTTP 429)
- **Interrupt logged**: `Can we fix 429 error too many concurrent requests?`
- **Cause**: Too many concurrent API calls across agents.
- **Remediation**: Implement exponential backoff in skills; reduce parallel agent count; consider upgrading API tier or switching providers for high-volume agents.

---

### 3. Agent Health Summary

| Agent | Gateway Process | Log Freshness | Notable Issues |
|-------|----------------|---------------|----------------|
| **Gentech** | ✅ Running (PID 923094) | Fresh | None detected |
| **YoYo** | ✅ Running (PID 923106) | Fresh | None detected |
| **DMOB** | ✅ Running (PID 922890) | Fresh | None detected |
| **Desmond** | ✅ Running (PID 922877) | Fresh | None detected |

All four agents are operational with no local process errors. The issues are systemic (cron daemon misconfiguration, external API failures), not per-agent crashes.

---

## Configuration Snapshot

- **Hermes config**: `/root/.hermes/config.yaml`
  - `cron_mode: deny` (line 351) — may block automatic job execution.
  - `cron.wrap_response: true`
  - No explicit per-job ACLs visible in config excerpt.
- **Cron daemon**: System `cron` running (`/usr/sbin/cron -f -P`), but Hermes uses its own embedded scheduler within each gateway process.
- **Gateway run command**: All agents started with `--profile <agent> gateway run --replace`.
- **Active cron jobs**: 29 total (system-level Hermes jobs like Watchdog, Morning Digest, etc.). The 4 agent-specific jobs are absent.

---

## Reproduction / Validation Checklist

- [ ] Run `hermes cron list --json` and confirm all expected agent jobs appear with `last_run_at` timestamps within the last 24h.
- [ ] Check `ps aux | grep hermes` — exactly 4 gateway processes (one per agent) plus any sandbox workers.
- [ ] Inspect `/root/.hermes/logs/errors.log` — last 100 lines contain no `ERROR` or `marshal data too short`.
- [ ] Run `df -h /` — root partition <80% used; if >80%, clean space before restarting any gateways.
- [ ] Verify external API access: `hermes model` shows valid OpenRouter models; GitHub Copilot auth fresh.
- [ ] After recreating missing jobs, monitor `/root/.hermes/cron/output/` for new output files at the next scheduled interval.

---

## Lessons for Health-Check Skill Design

1. **Always cross-reference** `jobs.json` (legacy) vs `hermes cron list` (active daemon). A healthy system should have all enabled jobs present in both views.
2. **`cron_mode: deny` needs explicit per-job approval** — the presence of this setting should trigger a pre-check before assuming jobs will fire.
3. **Session files (`session_*.json`) are anonymous** — they do **not** contain agent/profile fields. Agent attribution must come from logs, memory backups, or process inspection.
4. **Orphaned jobs appear as** `next_run_at` in the past + `last_run_at: null` + job name present in `jobs.json` but absent from `hermes cron list`. This triplet is a definitive detection signature.
5. **External API 404s and 429s surface in interrupt_debug.log** before they appear in job output files — always scan `interrupt_debug.log` for rate-limit signals.

---

## Related References

- System Health skill: `devops/system-health`
- See `system-health` references directory for full bytecode corruption recovery, credential cascade troubleshooting, and cron misassignment detection patterns.
- Hermes Cron Internals: `${INSTALL_DIR}/website/docs/developer-guide/cron-internals.md`
