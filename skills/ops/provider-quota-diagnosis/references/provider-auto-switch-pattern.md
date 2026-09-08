# Provider Auto-Switch Pattern (Ollama Cloud ↔ OpenCode Go)

Reusable pattern for automatically failing over between two LLM providers based on
live usage, so the user never hits a dead provider mid-work. Built Aug 7, 2026.

## Strategy (Jordan's directive)
- **Ollama Cloud = PRIMARY** — resets **weekly** (~7 days). Fresh tank every week.
- **OpenCode Go = GAP-FILLER** — resets **monthly** (~30 days). Deep reserve.
- Flip to OpenCode Go when Ollama weekly crosses ~90%; flip back when Ollama resets below ~20%.
- The weekly-vs-monthly cadence naturally desyncs the two over time, so the loop works
  long-term even if they happen to be aligned on any given day.

## The script
`/root/.hermes/scripts/provider-auto-switch.py` (also copied to the profile scripts dir).
Runs as a `no_agent=True` cron job (daily at 12:00) — silent when no switch needed
(watchdog pattern), prints a report only when it flips.

## Key mechanics
1. **Read Ollama usage** via `GET https://ollama.com/api/usage` (NOT `/v1/usage` — 404s).
   `limits.weekly.usage` is the binding fraction.
2. **Detect OpenCode Go state** by live-testing a model call. `GoUsageLimitError` in the
   error body = exhausted. Use `minimax-m3` as the probe (non-China-hosted; `deepseek-v4-flash`
   hits a `RegionError` opt-in gate instead).
3. **Flip config.yaml** — rewrite the `model:` block (default/provider/base_url) to the target.
4. **Sync cron jobs** — run `cron-provider-sync.py` so all LLM cron jobs follow the new provider.
5. **Save context bridge BEFORE restart** — run `context-save.py` so no session work is lost.
6. **Restart the gateway** via `systemctl --user restart hermes-gateway-gentech.service`.
7. **Report** — print the switch reason + a resume cue: "reply **continue** when I'm back."

## Pitfalls
- **The cron tool rejects absolute script paths** — it wants a bare filename resolved under
  `~/.hermes/scripts/`. Copy the script there and reference it by filename only.
- **Gateway restart drops session context** — always run `context-save.py` first, and tell the
  user to reply "continue" to resume from the bridge. This was Jordan's explicit concern.
- **Both providers can be exhausted simultaneously** — if Ollama is high AND OpenCode Go is
  exhausted, there's no flip possible; report the gap and point at Nous Research as the rescue path.
- **Model name format differs per provider** — Ollama uses bare names (`deepseek-v4-flash:0731`),
  OpenCode Go uses bare names too but the exact model string must match its `/v1/models` list.
