---
name: cron-model-routing
description: "Cron job model routing V2 — tiered provider routing. OpenCode Go (primary, unlimited) for daily crons. Ollama Cloud (weekly cap) reserved for weekly-only jobs. Script-only (no_agent) jobs skip LLM entirely. V2 routing document at 11-Mess Hall/references/model-routing-v2.md"
version: 3.0.0
author: gentech
tags: [cron, model-routing, tiered-routing, cost-optimization, opencode-go, ollama-cloud]
---

# Cron Model Routing V2 — July 2026

## ⚠️ Reference Document

The full V2 routing specification is at **`11-Mess Hall/references/model-routing-v2.md`**. This skill covers cron-specific implementation details.

## Principle

Cron jobs specify provider + model explicitly in `jobs.json`. Bulk edits via `skill_manage(action='patch', replace_all=true)` on the JSON file pick up immediately — the gateway reads the file fresh on every tick and does NOT need a restart.

## Current Provider Split (Sep 4, 2026 — All on OpenCode Go / glm-5.3-flash)

| Provider | Crons Assigned | Usage | Status |
----------|--------------|-------|--------|
| **OpenCode Go** 🥇 | All ~50 LLM jobs (gentech 35, treasury 19, gizmo 2, pixel 4) | glm-5.3-flash | ✅ Live-tested HTTP 200 Sep 4; no cap on Go plan |
| **Ollama Cloud** ☠️ | none | — | DOWN Sep 2–4 (HTTP 429, 2-day outage). Was still pinned on 30+ jobs during the outage — fleet-wide silent failures. Sep 4: configs + jobs re-pinned to OpenCode Go via cron-provider-sync.py |
| **Z.AI** ☠️ | none | — | Empty balance (1113) |
| **Script-only (no_agent)** | ~19 jobs (never use LLM) | No provider needed | ✅ Unaffected by provider outages |

**Sep 4 outage lesson:** when a provider dies, everything still pinned to it fails on EVERY tick until re-pinned — and `Portfolio Health Check` was showing a real HTTP 429 in last_error as the only visible symptom. The sync script (`cron-provider-sync.py`) re-pins all 4 profiles in one run; no gateway restart needed for crons. Interactive sessions on other profiles pick up config at their next session start.

**Aug 29 migration facts:**
- DeepSeek V4 flash+pro are REGION-BLOCKED on OpenCode Go (HTTP 403 RegionError — "only available hosted in China, requires explicit opt in" at Jordan's workspace). RIP DeepSeek until Jordan opts in at https://opencode.ai/workspace/.../go
- Working OCG models (live-tested Aug 29): glm-5.3-flash, glm-5.2, glm-5.3, kimi-k2.7-code, kimi-k3, minimax-m2.5, minimax-m3, qwen3.7-plus, qwen3.8-flash, qwen3.8-max, mimo-v2.5, longcat-2.0, hy3. Broken: grok-4.5 (503), gpt-5.6-luna (500)
- All 4 profiles' config.yaml (model block + fallback_providers[0]) switched to glm-5.3-flash, fallback glm-5.2. Gateway restart required for interactive sessions; jobs.json picks up on next tick without restart.
- jobs.json `model_snapshot`/`provider_snapshot` fields must match the new global config or Hermes fails the job closed (drift protection). Sync them when re-pinning.
- PA Suite (`ac736cacf5e5`) now enforces handoff accountability: runs handoff-watcher every run, escalates stalls >6h to Jordan, tracks repeat offenders per agent.

**Why this changed (Jul 27):** Jordan instructed switch back to ollama-cloud. All 29 LLM-using cron jobs moved from `opencode-go` → `ollama-cloud`. Model names normalized from `deepseek/deepseek-v4-flash` (OpenCode Go format) to `deepseek-v4-flash` (ollama-cloud format). Verified all 29 on target; confirmed 10 no-agent script jobs were NOT touched.

**Kimi K3 note:** Available on Ollama Cloud but requires extra usage credits (not in base plan). Do NOT set Kimi K3 on any cron until Jordan adds credits.

**Harness Critic model:** As of Jul 28, 2026, the Critic uses `deepseek-v4-flash` on ollama-cloud (same model as Evolution). The original plan was to use `kimi-k2.7-code` for anti-collusion, but the Critic's prompt was 6.5KB of detailed workflow instructions that were already documented in the `harness-critic.md` skill file. This caused massive input token consumption (960K per run) on ollama-cloud, exhausting the free tier. The fix (evolve-9): trimmed the prompt to 1.3KB by moving the detailed workflow to the skill file. The Critic now uses the same model as Evolution with a lean prompt. If anti-collusion is desired, use a different model family but keep the prompt lean.

**Key technique:** Direct `jobs.json` edit via Python JSON manipulation (not `cronjob` MCP tool, not `hermes cron edit` CLI — neither supports `--model`/`--provider` flags). The gateway picks up changes on the next tick — no restart needed.

**Model name format by provider:**
- **Ollama Cloud:** `deepseek-v4-flash` (no slash, no prefix)
- **OpenCode Go:** `deepseek/deepseek-v4-flash` (slash between org/name)
- Wrong format = 400 error at inference time. Always verify after a batch switch.

## Cron Tiers

| Tier | Frequency | Primary Provider | Emergency Fallback | Examples |
|------|-----------|-----------------|-------------------|---------|
| **Critical** | Multiple daily | OpenCode Go | → Ollama Cloud → Skip | Morning Digest, PR Maintainer, Revenue Monitor |
| **Standard** | Daily | OpenCode Go | → Ollama Cloud → Skip | Nightly Build, Build Queue, Hub Sync, Brain Backup |
| **Weekly** | Weekly or less | OpenCode Go | → Ollama Cloud → Skip | FOMC Summary, Marketplace Scout, GenTech Shop, Game Release, GitHub Crunch |
| **Harness** | Every 4h | OpenCode Go | → Skip (read-only self-eval) | Evolution, Critic, Verifier, Gardener |
| **Background** | No LLM needed | Script-only (no_agent) | Never uses LLM | API Safety Suite, Vault Watcher, CMC Watchlist, Fed Reminder |

## Provider Model

Every cron specifies its provider and model in `jobs.json`. There is no runtime routing tier — the model field is what the job uses. A job on `opencode-go` with `deepseek/deepseek-v4-flash` stays there until edited.

```
Critical/Standard/Weekly/Harness → OpenCode Go (primary) → Ollama Cloud (emergency fallback only)
Background → No provider needed (no_agent scripts)
```

## Auto-Sync: Make Crons Follow the Session Provider/Model (Aug 4, 2026)

Cron jobs are pinned per-job in `jobs.json` and do NOT follow the session's
`config.yaml` model/provider. When Jordan switches the session provider/model,
every LLM cron stays on the old one — so if the old provider rate-limits (e.g.
nous 429), the whole fleet fails while the session runs fine elsewhere.

**Fix (built Aug 4, upgraded to v2 Aug 29):** `scripts/cron-provider-sync.py` (v2) reads each profile's `config.yaml` (`model.default` + `model.provider`) and syncs the ENTIRE fleet in one run across all 4 profiles (gentech, gentech-treasury, gizmo, pixel):
1. Re-pins every LLM cron job (`no_agent=False`) in each profile's `cron/jobs.json` — including `model_snapshot`/`provider_snapshot` (drift-protection fields, must match or Hermes fails the job closed)
2. Re-pins ALL auxiliary slots (web_extract, compression, skills_hub, approval, mcp, triage_specifier, curator, session_search) via `hermes config set` — never direct config.yaml writes
3. Re-pins `auxiliary.vision` ONLY to models in the script's `VISION_CAPABLE` set (live-tested; glm-5.3-flash confirmed vision-capable Aug 29) — otherwise warns and preserves the current vision pairing
4. Rewrites `fallback_providers[0]` if it references a blocked model (e.g. region-locked deepseek-v4), preserving clean secondary fallbacks

It backups `jobs.json` before writing, NEVER touches `no_agent` script jobs, and is idempotent (safe to run repeatedly). The sync is an **on-demand action** — run it manually whenever Jordan switches providers/models:
```bash
python3 ~/.hermes/profiles/gentech/scripts/cron-provider-sync.py
```
No gateway restart needed for crons/jobs.json — they pick up on the next tick. Gateway restart only refreshes interactive sessions (must be run by Jordan from a separate shell — agents cannot restart their own gateway).

## Switch-Back Runbook — Ollama Cloud (planned ~Aug 31, DECIDED by Jordan)

> **⚠️ UPDATE Aug 29, 2026 — DO NOT blindly switch back to DeepSeek.** After the DeepSeek nationalization scare + OCG region-block (403), Jordan decided: keep **glm-5.3-flash primary**; when Ollama billing clears, reassess with **diversification** — add gpt-oss-120b + nemotron-3-super as fallbacks (live-test first), demote DeepSeek to cheap booster. Reasoning + decision chain: `00-HQ/brain-snapshots/brain-snapshot-2026-08-29.md` + `09-Green Room/specs/model-strength-score.md` (v2 — sovereignty is now a product factor). The fleet's diverse fallback chain is itself Phase 0 of the Sovereign Model Router build (#71).

When Ollama Cloud billing is fixed, the ORIGINAL plan was to return the fleet to `ollama-cloud / deepseek-v4-flash:0731`. Superseded by the diversification decision above — verify billing, then run the fallback live-tests before any re-pin. Order of operations (kept for reference):

1. **Verify billing is live FIRST** (don't switch onto a dead provider):
```bash
source ~/.hermes/profiles/gentech/.env
curl -s -o /dev/null -w "HTTP %{http_code}\n" --max-time 60 -X POST "https://ollama.com/v1/chat/completions" \
  -H "Authorization: Bearer $OLLAMA_API_KEY" -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4-flash:0731","messages":[{"role":"user","content":"Say OK"}],"max_tokens":8}'
```
HTTP 200 = go. HTTP 403 "past due" = wait.
2. **Flip each profile's primary** (4 profiles: gentech, gentech-treasury, gizmo, pixel):
```bash
for p in gentech gentech-treasury gizmo pixel; do
  hermes config set --profile $p model.default "deepseek-v4-flash:0731"
  hermes config set --profile $p model.provider ollama-cloud
  hermes config set --profile $p model.base_url "https://ollama.com/v1"
done
```
3. **Run the sync:** `python3 ~/.hermes/profiles/gentech/scripts/cron-provider-sync.py` — re-pins all crons + aux slots fleet-wide. NOTE: ollama-cloud model format has NO slash (`deepseek-v4-flash:0731`), unlike OCG's.
4. **Fallback chain:** keep `fallback_providers[0]` = opencode-go/glm-5.2 — the sync won't touch it (OCG models aren't in BLOCKED_PATTERNS). This is the reverse of the Aug 29 direction: Ollama primary, OpenCode Go safety net.
5. **Vision:** the sync's VISION_CAPABLE guard keeps vision on opencode-go/glm-5.3-flash by design (keeps vision load off Ollama). To move vision to ollama's qwen3.5:397b instead, live-test it with an image first, then add to VISION_CAPABLE in the sync script.
6. **24h health watch:** Jul 26 lesson — Ollama caps hard under fleet load. If 429s appear in cron health, move the highest-frequency crons back to OpenCode Go individually.

**Automation (REMOVED Aug 17, 2026):** The cron job `c1540853dd1d` "Cron Provider Auto-Sync" was **removed** at Jordan's direction. We now keep most usage on Ollama Cloud and switch to OpenCode Go only occasionally, managing the two subscriptions manually. The sync is now an **on-demand action** — run the script manually whenever Jordan switches providers/models:
```bash
python3 ~/.hermes/profiles/gentech/scripts/cron-provider-sync.py
```
No gateway restart needed — jobs.json is read fresh each tick.

**Why this matters:** the manual "switch all jobs by hand" pattern keeps
repeating on every provider change. This is the durable mechanism — edit
`config.yaml` once and the cron fleet follows on the next sync tick. Run the
script manually anytime: `python3 ~/.hermes/profiles/gentech/scripts/cron-provider-sync.py`

**Caveat from the Jul 26 lesson:** blanket-pinning every job to ollama-cloud
can exhaust its free tier fast. If the sync points the whole fleet at a
rate-limited-cap provider, expect 429s — keep an eye on cron health after any
provider switch.

## When to Migrate a Cron

- If a cron errors with HTTP 429 → it's hitting a rate limit. Move it to OpenCode Go.
- If a cron runs daily but is on ollama-cloud → move to OpenCode Go. Ollama free tier cannot sustain daily usage.
- OpenCode Go is the daily driver. Ollama Cloud is fallback-only for weekly jobs when OC is having issues.

## Script-Only Jobs (no_agent=True)

These never need LLM routing. They remain unpinned (model: null, provider: null):
- CMC Bullish Watchlist
- Tradesta Leverage Trading Signal
- Fed Event Reminder
- LP Monitor v2
- V4 Nightly Maintenance
- Gaming Hub Sync (both)
- [Jordan] POE2 Build Health
- Rate Limit Monitor
- Vault Watcher Health Check
- API Safety Suite
- Build Queue Overnight Maintenance

## Batch Switchover — Moving Cron Jobs Between Providers

### Approach A: Direct `jobs.json` Edit (Preferred for 6+ jobs)

The `cronjob` MCP tool and `hermes cron edit` CLI do NOT support `--model` or `--provider` flags. For bulk switches, edit `jobs.json` directly with Python:

```python
import json

with open('/root/.hermes/profiles/gentech/cron/jobs.json') as f:
    data = json.load(f)

target_ids = ['list-of-job-ids']

for job in data['jobs']:
    if job['id'] in target_ids:
        job['provider'] = 'new-provider'
        job['model'] = 'new-model'

with open('/root/.hermes/profiles/gentech/cron/jobs.json', 'w') as f:
    json.dump(data, f, indent=2)
```

**CRITICAL: Exclude no-agent script jobs.** Jobs with `no_agent: true` don't use an LLM — changing their provider/model is unnecessary and creates confusion. Verify after the switch that no no-agent jobs were accidentally modified.

**No gateway restart needed** — the Hermes gateway reads `jobs.json` fresh on every tick.

### Approach B: `skill_manage(action='patch', replace_all=true)` (Fast bulk string swaps)

The fastest bulk-switch method: use the `patch` tool (accessed via `skill_manage`) with `replace_all=true` to swap string values in `jobs.json`:

```
skill_manage(
    action='patch',
    name='cron-model-routing',
    old_string='"provider": "ollama-cloud"',
    new_string='"provider": "opencode-go"',
    replace_all=true
)
```

Same for model names when the format changes (e.g. `"deepseek-v4-flash"` → `"deepseek/deepseek-v4-flash"`). This works because simple JSON string values are safe text replacements. Do NOT use this for structural JSON changes (adding/removing fields, reordering) — use Python `json` lib for that.

**No gateway restart needed** — the Hermes gateway picks up `jobs.json` changes on every tick.

### Approach B: Python JSON manipulation

For complex changes (rewriting whole job objects, adding fields), edit `jobs.json` with Python's `json` module:

```python
import json
with open('/root/.hermes/profiles/gentech/cron/jobs.json') as f:
    data = json.load(f)
for job in data['jobs']:
    if job['id'] in TARGET_IDS:
        job['provider'] = 'opencode-go'
with open('/root/.hermes/profiles/gentech/cron/jobs.json', 'w') as f:
    json.dump(data, f, indent=2)
```

### Approach C: `cronjob` MCP tool (Preferred for individual jobs)

The `cronjob` MCP tool updates individual jobs cleanly:

```python
cronjob(action="update", job_id="JOB_ID", model={"model": "deepseek/deepseek-v4-flash", "provider": "opencode-go"})
```

This is the preferred approach for switching 1-5 jobs. The tool exists in active sessions — use it directly.

### Approach D: `delegate_task` for large batch switches

When switching 6+ jobs, dispatch a subagent via `delegate_task` to parallelize:

```python
delegate_task(
    goal="Switch these cron jobs to opencode-go",
    context="For each: cronjob(action='update', job_id='...', model={'provider':'opencode-go','model':'deepseek/deepseek-v4-flash'})"
)
```

Each subagent handles 6-10 jobs and completes in ~2 minutes.

### Provider format rules

| Provider | Model Format in jobs.json | Example |
|----------|--------------------------|---------|
| OpenCode Go | `deepseek/deepseek-v4-flash` | Slash between org/name |
| Ollama Cloud | `deepseek-v4-flash` | No slash |
| Nous | `deepseek/deepseek-v4-flash` | Same as OpenCode Go |

Wrong prefix = 400 error at inference time.

## Pitfalls

- **Don't pin no_agent=True jobs** — their model field is ignored
- **Don't pin to Nous Research** — $20/mo emergency only
- **Ollama Cloud free tier caps hard** — Jul 26 lesson: 24 jobs on ollama-cloud hit HTTP 429 within 2 hours. All were reverted to opencode-go same session. The free tier cannot sustain daily usage — weekly-only fallback use only.
- **Unpinned crons fail silently** — LLM-powered crons without a model/provider set skip with "Skipped to prevent unintended spend." Always pin LLM crons.
- **Provider prefix matters in model field** — OpenCode Go uses `deepseek/deepseek-v4-flash` (with slash). Ollama Cloud uses `deepseek-v4-flash` (no slash). Wrong prefix = 400 error.
- **`patch()` with `replace_all` is safe for simple JSON string values** but NOT for structural changes (adding/removing fields, reordering). Use Python `json.load` + `json.dump` for structural edits.
- **The `cronjob` MCP tool may not exist** in your Hermes context. Always have Approach A (patch replace_all) or B (Python json) ready as a fallback.
- **Overgrown cron prompts exhaust free tier.** A cron job's prompt is loaded fresh every run. If the prompt contains detailed workflow instructions that are already documented in a skill file, the redundant text inflates input tokens on every tick. The Harness Critic (evolve-9) had a 6.5KB prompt that consumed 960K input tokens per run on ollama-cloud, exhausting the free tier. Fix: trim the prompt to essential instructions and reference the skill file for the full workflow. Target: <2KB for cron prompts that reference a skill.

## Real-World Failure: Jul 26 Provider Overload

**Event:** All 24 LLM-powered cron jobs were switched from opencode-go → ollama-cloud in one batch.
**Result:** Within 2 hours, the first jobs returning HTTP 429. By hour 3, every agent-executed cron was failing.
**Root cause:** Ollama Cloud free tier has a strict weekly usage cap (~100 sessions/week). 24 jobs firing multiple times/day exhausts this in hours.
**Fix:** Split across providers — 18 user-facing jobs on ollama-cloud, 12 internal jobs on opencode-go. Then within hours of that split, ollama-cloud was still hitting limits → all jobs reverted to opencode-go.
**Lesson:** OpenCode Go is the daily driver. Ollama Cloud is emergency fallback only until a paid tier is purchased.
