# Provider Auto-Switch — Ollama Cloud ⇄ OpenCode Go Failover

Fully-automatic provider failover between the two subscriptions. Built Aug 7, 2026 per Jordan's directive. Script: `~/.hermes/scripts/provider-auto-switch.py` (also mirrored at `~/.hermes/profiles/gentech/scripts/`). Cron job `provider-auto-switch` runs daily at 12:00, `no_agent=True` (script-only, zero LLM cost).

## Strategy (Jordan's cadence model)
- **Ollama Cloud = PRIMARY** — resets **weekly** (every 7 days). Fresh tank each week.
- **OpenCode Go = GAP-FILLER** — resets **monthly** (~30 days). Deep reserve, dipped into only when Ollama's weekly tank runs dry mid-cycle.
- The weekly-vs-monthly frequency difference is the whole trick: it naturally **desyncs** the two reset windows so one is always available. (They can temporarily align — e.g. both ~2 days out — but that's a one-time coincidence, not the pattern.)
- Flip to OpenCode Go when Ollama weekly ≥ 90%. Flip back when Ollama weekly resets < 20%.

## Reading usage — the real endpoints
**Ollama Cloud:**
- `GET https://ollama.com/v1/usage` → **404 "path not found"** (does NOT exist).
- `GET https://ollama.com/api/usage` with `Authorization: Bearer $OLLAMA_API_KEY` → **works**. Returns `limits.weekly.usage` (fraction 0-1) and `limits.session.usage`, plus per-model request counts. This is the authoritative programmatic read.
- The dashboard at `ollama.com/settings` shows the same numbers (weekly %, session %, reset countdown).

**OpenCode Go:**
- **No usage endpoint.** `/v1/usage`, `/api/usage`, `/v1/limits`, `/api/me` all return the dashboard HTML (SPA shell), not JSON.
- Detect state via a **live model test**: POST a tiny `chat/completions` to `https://opencode.ai/zen/go/v1`. A `GoUsageLimitError` in the response = exhausted. A completion = usable.
- Model names on OpenCode Go are **bare** (`deepseek-v4-flash`, `minimax-m3`), NOT slash-prefixed (`deepseek/deepseek-v4-flash` returns "Model not supported"). Use `minimax-m3` as the probe — it's non-China-hosted and reliable (some models like `deepseek-v4-flash` return a `RegionError` requiring China opt-in, which is a different gate than quota).

## The switch mechanism (all verified working)
1. **Rewrite config.yaml** `model:` block — set `default`, `provider`, `base_url` to the target. (Minimal YAML parser in the script; no PyYAML dep.)
2. **Sync cron jobs** — run `cron-provider-sync.py` which re-pins all 63 LLM cron jobs to the new provider/model. The gateway reads `jobs.json` fresh each tick — no restart needed for crons.
3. **Restart the gateway** — `systemctl --user restart hermes-gateway-gentech.service`. The gentech gateway runs under the systemd **user** session (not system), so `systemctl --user` is required.
4. **Context-save BEFORE restart** — run `context-save.py` first so no session work is lost. Wake-up reads the bridge after restart.
5. **Resume-cue message** — the ping tells the user: "Gateway is restarting. Progress saved to vault context bridge. Reply **continue** to resume the task." This is the key UX: the user is always in control of whether the agent resumes or starts fresh.

## Pitfalls
- **`/v1/usage` 404 is a trap** — the docs reference it but it doesn't exist. Use `/api/usage`.
- **OpenCode Go model names are bare**, not slash. Slash format returns "Model not supported".
- **`RegionError` ≠ quota exhaustion** — some OpenCode Go models are China-hosted and need opt-in. Probe with `minimax-m3`, not `deepseek-v4-flash`.
- **Gateway restart drops live session context** — always context-save first, and give the user a resume cue. Full-auto restart is a real action on the live system; the context-save makes it safe.
- **Script path for cron** — the cron tool resolves bare filenames under `~/.hermes/scripts/`. Keep the script there (and mirror to the profile scripts dir).
- **Silent when healthy** — the script exits 0 with no output when no switch is needed (watchdog pattern). Only prints when it actually flips or hits a gap (both providers down → suggests Nous as third leg).

## Thresholds (in the script)
- `OLLAMA_HIGH_WATER = 0.90` — flip to OpenCode Go when Ollama weekly ≥ 90%
- `OLLAMA_LOW_WATER = 0.20` — flip back to Ollama when weekly < 20% (post-reset)
- If Ollama is high AND OpenCode Go is exhausted → report the gap, suggest Nous Research (the genuine third leg when both are down).
