# Incident: 2026-05-05 — Session Routing and Cron Dispatch Failure

**Summary**: Watchdog health check revealed fleet-wide execution and routing breakdown. All agent gateways were running, but session identification failed (agent: unknown) and cron jobs for DMOB, Desmond, Gentech were not executing. YoYo's DeFi monitoring cron job crashed with a model 404 error.

## Timeline (May 05, 2026)

- **~02:15–03:20 UTC** — Agent error logs show repeated warnings: "Fallback to openrouter/openai/ollama failed: provider not configured" and "Non-retryable client error: 404 — Model 'nousresearch/trinity-large-thinking' not found".
- **During health check** — Investigation found:
  - All 270+ recent session files report `agent: unknown` / `profile: unknown`
  - No `hermes-cron` daemon process running despite cron registry having jobs
  - DMOB, Desmond, Gentech have no `cron.log` files
  - YoYo cron.log shows only QUIET_HOURS entries past scheduled times

## Root Causes

1. **Session routing pipeline broken** — Session files are being created without agent/profile metadata. Likely hermes-cron not injecting context or session writer failing to tag sessions. Correlates with missing cron daemon (sessions created by cron are typically tagged).
2. **Cron daemon stopped** — `ps aux` shows zero `hermes.*cron` processes. Cron jobs defined in `~/.hermes/cron/jobs.json` are not being dispatched. This explains missing cron logs for DMOB/Desmond/Gentech and stale activity.
3. **Model misconfiguration** — YoYo's script `defi-milestone-tracker.py` uses model `nousresearch/trinity-large-thinking`. OpenRouter returns 404; correct ID is `arcee-ai/trinity-large-thinking`. The error surfaces in the cron log as a runtime exception.
4. **Provider cascade failures** — All agents show fallback provider failures (openrouter, openai, ollama) indicating missing credentials or disabled providers in the global config.

## Confirmed Error Signatures

```text
RuntimeError: Error code: 404 - {'status': 404, 'message': "Model 'nousresearch/trinity-large-thinking' not found..."}
WARNING — Fallback to openrouter failed: provider not configured
WARNING — Fallback to openai failed: provider not configured
WARNING — Fallback to ollama failed: provider not configured
```

Session file header (initial check ~02:15 UTC):
```json
{
  "agent": "unknown",
  "profile": "unknown",
  ...
}
```

Session file header (re-check ~12:58 UTC — more severe variant):
```json
{
  // agent and profile keys ABSENT entirely — not even "unknown"
  // JSON has no agent/profile fields at all
}
```

Note: The initial check found string values "unknown". The re-check found the keys missing entirely — a different, more severe failure mode. See `session-routing-failure-modes.md` for the taxonomy.

## Diagnostic Steps Executed

- `session_search` across recent transcripts — all returned unknown agent
- `ps aux | grep hermes_cli.main` — all four gateways running with PIDs
- `tail -20 ~/.hermes/profiles/<agent>/logs/errors.log` — found 404 model errors and provider fallback warnings
- `tail -5 ~/.hermes/profiles/<agent>/cron.log` — DMOB/Desmond/Gentech missing; YoYo shows only QUIET_HOURS
- `ps aux | grep hermes.*cron` — zero matches (cron daemon down)
- Inspected `~/.hermes/cron/jobs.json` — registry exists (dict with "jobs" array), but no active dispatcher
- Checked latest session files directly — confirmed agent/Profile fields are "unknown"

## Recovery Checklist

- [ ] Restart hermes-cron daemon (`systemctl --user start hermes-cron.service` or bundled gateway restart)
- [ ] Verify cron daemon process appears (`ps aux | grep hermes.*cron`)
- [ ] Fix YoYo model configuration: update `~/.hermes/profiles/yoyo/config.yaml` to use `arcee-ai/trinity-large-thinking` or another valid provider/model
- [ ] Validate OpenRouter API key present in all agent `.env` files
- [ ] Confirm provider configuration for fallbacks (openai, anthropic, ollama) in global or per-agent config
- [ ] After cron daemon restart, verify cron.log creation for DMOB, Desmond, Gentech
- [ ] Validate next session files contain correct `agent` and `profile` fields
- [ ] If session routing remains broken, check gateway.log for "agent tag" injection errors and hermes-cron context propagation

## Status Updates

### May 05, 2026 — 12:58 UTC (Watchdog re-check)
- Session routing STILL BROKEN: all cron sessions show `agent` and `profile` keys MISSING entirely (not "unknown")
- Cron daemon still not found as a separate process; systemd master service dead since 02:16 UTC
- Gateways running as manual processes (restarted 12:44 UTC)
- Desmond missing skills: `cmc-watchlist-scraper`, `crypto-monitoring-cron`
- All error logs empty (fresh restart, false clean signal — re-check in 15-30 min)

## Derived Pitfalls (Added to Skill)

- Session routing failure pattern: When the majority of recent session files show `agent: unknown` or `profile: unknown`, the session identification/injection pipeline is broken. Check gateway.log for 'agent tag' parsing errors and verify hermes-cron is injecting agent context correctly.
- Cron registry structure: `~/.hermes/cron/jobs.json` may be a dict with a 'jobs' key, not a direct list — parse accordingly. Absence of cron daemon process (`ps aux | grep hermes.*cron`) means no jobs will execute regardless of registry state.