# Fleet Model Migration — Sep 2, 2026 (nemotron → glm-5.3-flash on Ollama Cloud)

Session record backing the "Sep 2 Fleet Migration — Verified Refinements" section in SKILL.md.

## What was done (verified end-to-end)
- Jordan greenlight: fleet-wide primary `glm-5.3-flash` on Ollama Cloud; `nemotron-3-super` demoted to backup-only (use when usage runs out); heavy/audit work = GLM-5.3 full (not flash).
- Rail live-tested BEFORE flipping anyone (probe below returned HTTP 200 + 'OK' at adequate max_tokens).
- All 4 profiles set: default=glm-5.3-flash / provider=ollama-cloud / base_url=https://ollama.com/v1 — verified via `--profile` config gets.
- Cron sweep: gentech had 39 enabled LLM jobs; 4 nemotron stragglers re-pinned via direct jobs.json edit (Daily Session Reset `c00b01c74988`, Tailscale reminder `b14fe104bd1d`, Council Publish `8c8d133f59d7`, PA Suite `3f523dff7d1a`). Treasury (10), Labs (2), Entertainment (4) already clean. 37 no-agent jobs untouched (no model, skip).
- Handoffs sent to gizmo/pixel/treasury/forge lanes; all return lanes verified by 16:27 UTC (Labs config-check + live probe, Pixel jobs.json pins, Steward 10 cron pins on-disk + live smoke). Forge handoff initially unacked — picked up by next sweep.

## Straggler sweep pattern (the reusable part)
One execute_code pass, before touching anything:
1. For each profile: read `~/.hermes/profiles/<P>/cron/jobs.json`, classify enabled jobs into LLM vs `no_agent`.
2. Print every LLM job with its current provider/model — stragglers (old model) stand out immediately.
3. Batch re-pin ONLY the stragglers (set provider+model), back up jobs.json first.
4. Read back and verify each target job on the new provider/model.

Key lesson: you CANNOT assume uniformity from a global config change — jobs keep their baked-in pins until individually re-pinned. Sep 2 found stragglers hiding in gentech while the other 3 profiles were already clean.

## Live-test probe evidence (reasoning-model max_tokens gotcha)
glm-5.3-flash on Ollama Cloud, prompt "Reply with the single word: OK":
- max_tokens=8 → HTTP 200, content="", finish_reason=length
- max_tokens=64 → HTTP 200, content="", finish_reason=length
- max_tokens=512 → HTTP 200, content="OK", reasoning field populated, finish_reason=stop

The reasoning budget consumes small caps before any content is emitted. Probe reasoning models with max_tokens ≥ 512 and check `choices[0].message.reasoning` to distinguish thinking-past-cap from returning-nothing. Cron prompts already use generous limits — this bites only quick curl probes.

## Restart scope after a model flip (verified)
- Cron jobs: NO restart — the scheduler reads jobs.json each tick; cron/agent sessions read config fresh at spawn.
- Gateway restart is ALWAYS guard-blocked from inside a gateway-hosted agent session (systemctl restart, even via terminal background=true, is refused: "gateway would kill this command"). Must come from a separate shell outside the gateway.
- Interactive sessions that act stale: a fresh session picks up new config — try that before any restart.
