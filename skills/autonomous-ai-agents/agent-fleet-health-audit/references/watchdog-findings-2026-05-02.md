# Incident: 2026-05-02 — Multi-Agent Fleet Degradation

**Summary**: Systemic failure affecting all four agents (Gentech, YoYo, DMOB, Desmond) requiring manual intervention. No automated recovery despite enabled systemd units.

## Timeline

- **13:25–13:39** — YoYo, Desmond, DMOB gateways encounter repeated ElevenLabs TTS `401` errors, continue operating with degraded TTS.
- **15:38–15:39** — A coordinated update/restart event triggers. All three non-Gentech gateways (running as manual processes, not systemd) exit cleanly (exit code 0) within 4ms of each other.
- **Immediately after** — Profile directories for YoYo, DMOB, Desmond appear deleted or moved. Watcher processes attempt to relaunch but fail due to missing profiles.
- **15:39:40** — Gentech (systemd-managed) respawns automatically and remains running.
- **20:17** — Manual intervention starts YoYo, DMOB, Desmond systemd services successfully; all four agents operational but degraded.

## Root Causes

1. **Master orchestration service down** — `hermes-gateway.service` FAILED since Apr 27 (exit 203/EXEC) due to incorrect ExecStart path (`/root/.hermes/hermes-agent/venv/bin/python` instead of `${INSTALL_DIR}/venv/bin/python`). This blocks cron job dispatch fleet-wide.
2. **Cron registry corruption** — `/root/.hermes/cron/jobs.db` is 0 bytes. Active cron registry empty; no jobs executing despite definitions in `jobs.json`.
3. **Fleet-wide TTS failure** — Shared invalid ElevenLabs API key (`ff52c5f015c3490da49adf12513a6d55`) in agent secrets/tool configs produces `ApiError: status_code: 401` across all agents.
4. **Agent-specific credential gap** — DMOB missing `ANTHROPIC_TOKEN`/`ANTHROPIC_API_KEY`, blocking Anthropic model usage (`RuntimeError: No Anthropic credentials found`).
5. **Profile directory exposure** — YoYo, DMOB, Desmond profiles were on disk but systemd units were inactive; update restart killed manual gateways but watchers couldn't relaunch because profile directories were missing post-cleanup. Systemd units existed but were disabled from auto-start after clean exit.

## Confirmed Error Signatures

```text
elevenlabs.core.api_error.ApiError: status_code: 401, body: {'detail': {'status': 'invalid_api_key', 'message': 'Invalid API key'}}
RuntimeError: No Anthropic credentials found. Set ANTHROPIC_TOKEN or ANTHROPIC_API_KEY...
systemctl status hermes-gateway.service → Active: failed (Result: exit-code) since ...; Main PID: ... (code=exited, status=203/EXEC)
~/.hermes/cron/jobs.db: 0 bytes (corrupted active registry)
```

## Recovery Steps Taken

1. Manually started systemd units:
   ```bash
   systemctl --user start hermes-gateway-yoyo.service
   systemctl --user start hermes-gateway-dmob.service
   systemctl --user start hermes-gateway-desmond.service
   ```
2. Verified all four gateway processes running via `ps aux | grep hermes_cli.main`.

## Current State (as of 2026-05-02 20:47 UTC)
- All gateways running (PIDs: yoyo 1130047, dmob 1130064, desmond 1130066, gentech 1118093)
- TTS failures last seen: YoYo 13:38, DMOB 15:37, Desmond 13:27, Gentech 13:20 — no new attempts
- DMOB Anthropic credentials still missing
- No active cron executions due to master service failure; orphaned jobs still in `jobs.json` but not in active registry
- Master `hermes-gateway.service` still FAILED since Apr 27
- Disk pressure resolved (cleanup occurred; now 26% used)

## Diagnostic Checklist (Derived)

- [ ] Check `systemctl --user status hermes-gateway-<agent>` **AND** `ps aux` — both must show active process; inactivity despite running process means manual/unmanaged gateway
- [ ] If all agents show same error pattern (e.g., ElevenLabs 401), treat as fleet-wide credential failure first
- [ ] Validate `jobs.db` filesize > 0; if 0 bytes, cron dispatcher is non-functional
- [ ] After any update restart, verify profile directories exist before assuming auto-recovery
- [ ] Always inspect `gateway.log` for exit reason: `code=exited, status=0/SUCCESS` indicates clean shutdown (update-triggered); `code=killed, signal=HUP` indicates external termination; uncaught tracebacks indicate crash