---
name: model-routing
description: "Model routing V3 — three-tier model selection. DeepSeek V4 Flash (T1, default). Kimi K2.7 (T2, medium). Kimi K3 (T3, big boy). Jordan's directive Jul 27, 2026."
version: 7.0.0
author: gentech
tags: [hermes, model-routing, tiered-routing, cost-optimization, deepseek, kimi]
---

# Model Routing V3 — July 27, 2026

## Three-Tier System

**Default to DeepSeek V4 Flash.** Escalate only when the task justifies the cost.

| Tier | Model | Cost | Use For |
|------|-------|------|---------|
| **T1 — Default** | DeepSeek V4 Flash | ~$0.15/M in · ~$0.60/M out | Everything unless it fits T2 or T3 |
| **T2 — Medium** | Kimi K2.7 | ~$2/M (13x Flash) | Complex debugging, code review, retry on Flash failure |
| **T3 — Big Boy** | Kimi K3 | ~$15/M out (100x Flash) | Architecture, security audits, design reviews, full-codebase |

## When to Use Each

### T1 — DeepSeek V4 Flash (default, 80%+ of work)
- Cron jobs and daily brain audits
- Quick code generation and boilerplate
- Content drafting and summaries
- Routine terminal work
- Build queue tick and handoff
- Most Telegram replies
- Anything you're not sure about — start here

### T2 — Kimi K2.7 (when Flash isn't reliable enough)
- Complex debugging across multiple files
- Code review of non-trivial PRs
- Data analysis and pattern detection
- Retry after Flash fails or produces wrong output

### T3 — Kimi K3 (when the answer matters)
- Architecture decisions and design reviews
- Smart contract security audits
- Full-codebase analysis (1M context)
- Design audits (portfolio, UI, branding)
- Strategic planning and competitive analysis
- Any task where failure cost > $15

## K3 Thinking Config (Required for Deep Reasoning)

Kimi K3 needs explicit thinking configuration for complex tasks. Without it, K3 may spend its entire max_tokens budget on internal reasoning and produce no visible answer.

```python
# Correct — with thinking
blockrun_chat(
    message="...",
    model="moonshot/kimi-k3",
    max_tokens=8192,
    thinking={"type": "enabled", "budget_tokens": 2048}
)

# Wrong — no thinking, may return empty
blockrun_chat(message="...", model="moonshot/kimi-k3")
```

For very large outputs (full HTML pages, long code), raise max_tokens to 16384 and budget_tokens to 4096.

## K3 Compressed Variant (0.18B)

On July 28, 2026, a community member (@0x0SojalSec) claimed to have compressed Kimi K3 from 2.8T MoE down to **0.18B parameters, 0.10B activated, 700MB** — same architecture, same attention design. This is ~1000x smaller than the original.

**Reality check:** A 0.18B model won't match the full model's quality for architecture decisions or security audits. What it *could* do is run as a local fallback or for simple classification tasks on a VPS or Raspberry Pi. Worth watching — if someone distills a 7B or 13B version that runs on a single GPU, the cost picture changes entirely. For now, the API is still the right call for real work.

## Implementation

### In blockrun_chat calls
```python
# T1 — Default: omit model param
blockrun_chat(message="...")

# T2 — Medium
blockrun_chat(message="...", model="moonshot/kimi-k2.7")

# T3 — Big boy
blockrun_chat(
    message="...",
    model="moonshot/kimi-k3",
    max_tokens=8192,
    thinking={"type": "enabled", "budget_tokens": 2048}
)
```

### In cron jobs
```yaml
# Default: no model override = DeepSeek V4 Flash
# T2: model: { provider: "openrouter", model: "moonshot/kimi-k2.7" }
# T3: model: { provider: "openrouter", model: "moonshot/kimi-k3" }
```

## Provider Notes
- **DeepSeek Official API** — live in public beta as of Jul 31, 2026 (see `references/deepseek-v4-flash-official-api.md`). Native Responses API, Codex-adapted, massively upgraded agent benchmarks (DeepSWE 54.4 vs 12.8 Pro-Preview). DeepSeek docs list Hermes as an official agent integration. Open decision: evaluate switching from Nous to direct DeepSeek (api.deepseek.com).
- **Ollama Cloud** — PRIMARY provider as of Sep 7, 2026 (Jordan directive). All 4 profiles on `deepseek-v4-flash:0731`. AUDIT pair: GLM-5.3-flash / Kimi K2.7-code.
  - **API endpoint:** `https://ollama.com/v1` (NOT `ollama.cloud` — that domain is a fake/scam site that returns a warning page. Confirmed Jul 27, 2026.)
  - **Model name format:** bare names only — `deepseek-v4-flash:0731`, `glm-5.3-flash`, `kimi-k2.7-code`. No slash prefix.
  - **Reset cadence is WEEKLY (7 days).** This is why Ollama is the primary subscription: it refills every week.
  - **`/v1/usage` and `/v1/plan` endpoints do NOT exist** on the live API (return `path not found`). To check real state, live-test the inference endpoint (`POST /v1/chat/completions`) or read the dashboard at `ollama.com/settings`.
- **Hermes portal (Nous)** — FALLBACK provider as of Sep 7, 2026. `deepseek/deepseek-v4-flash` first, `upstage/solar-pro4:free` second. Free, US infra. `GET https://inference-api.nousresearch.com/v1/models` lists 291 models including `moonshotai/kimi-k2.7-code` and `moonshotai/kimi-k3`. Direct API calls need a browser User-Agent header (Cloudflare 403 otherwise) — full recipe in `references/nous-inference-api-direct.md`.
  - **⚠️ Sep 12 correction:** `glm-5.3-flash` is **dead as an AUDIT model** (Z.AI `1113`; Ollama Cloud weekly-capped 429). AUDIT second-opinion now = **Kimi K2.7-code via Nous** (`moonshotai/kimi-k2.7-code`, live). Same for the Critic slot — keep it off glm until Z.AI is re-funded. See E-17 in the error runbook.
- **OpenCode Go — RETIRED + FULLY DETACHED (Sep 7, 2026).** Do NOT route to it. **Full detachment is NOT just pointing routing surfaces away** — the provider def block, the `.env` API key, dead scripts, and active probes all keep a retired provider alive and can silently burn usage. When retiring a provider, remove ALL of: (1) the `providers.<name>:` block from every profile config, (2) the `<NAME>_API_KEY` from every profile `.env`, (3) dead scripts that reference it (e.g. an auto-failover script that would flip the fleet back to it), (4) active cron probes that ping its catalog. Verify with a fleet-wide sweep for the provider name across configs/.env/crons/scripts — zero refs outside harmless comments. A dormant auto-switch script is a landmine: if ever run it re-engages the retired provider. Previously the fallback; superseded by Hermes portal (Nous).
- **ClawRouter (BlockRun)** — NEW fallback provider, installed + enabled Aug 7, 2026. Local proxy on `127.0.0.1:8402/v1`, 71 models/12 labs behind ONE provider, wallet-signature auth, USDC per-request via x402 on Base/Solana. By BlockRun (same as blockrun wallet). **Run as durable systemd service `clawrouter-proxy.service` (NOT a session background process — that dies on restart and kills the provider for all 4 groups).** Wallet `0xf5f99007...9280D` (Base USDC, default chain) + Solana `BX9ELMCG...`. Default pinned to `free/deepseek-v4-flash` (exact id — `free` alias routes to gpt-oss-120b). All 4 TG groups share one Hermes config, so the provider propagates automatically. Setup + pitfalls in `references/clawrouter-provider.md`.
  - **Free-tier congestion is the #1 failure mode.** `free/deepseek-v4-flash` is hammered by everyone; a slow upstream stalls the shared provider and ALL 4 groups go silent at once (looks like "Entertainment is down" but it's global). Symptom in clawrouter journal: `All models in fallback chain failed` + `Socket timeout, destroying connection`; gateway logs `httpx.ReadTimeout`. **Fix: configure a paid fallback** so a free stall auto-routes instead of going silent — see `references/clawrouter-provider.md` §Fallback chain config.
  - **Fallback chain config (Aug 2026):** `fallback_providers` is a LIST of `{provider, model, base_url}` dicts. The legacy single-dict `fallback_model` key is deprecated — `hermes config set fallback_model.*` warns "not a recognized config key". **PITFALL: `hermes config set fallback_providers '[...]'` stores the list as a QUOTED STRING that `get_fallback_chain` does NOT parse** — `hermes fallback list` then reports "No fallback providers configured". Write a real YAML list via the config module (recipe in reference). Verify with `hermes fallback list`, not grep.
- **VPS (local)** — last resort, $0.

## YouTube Skills
YouTube Skills for AI Agents (432⭐, MIT) installed at `youtube-full`. Gives agents access to YouTube transcripts, video search, channel browsing, and playlist extraction. Free tier with 100 credits. Install command: `hermes skills install skills-sh/ZeroPointRepo/youtube-skills/skills/youtube-full`

## Version History

**BREAKING CHANGE:** Moonshot released Kimi K3 open-weight on July 28, 2026. 2.8 trillion parameters MoE (104B active), multimodal, agentic — free to download. Previously locked behind Ollama Cloud extra credits.

**What this means:**
- K3 is no longer gated by Ollama Cloud credits — it's open-weight and downloadable
- Self-hosting is now an option (VPS, BlockRun Modal, or local)
- New providers may offer it without the previous credit wall
- This is the world's first open 3T-class model — bigger than anything OpenAI has released publicly

**Current status (Jul 28):**
- Open-weight release confirmed via Moonshot/X (Nahid @nahid_pro09)
- Not yet evaluated on Ollama Cloud or OpenCode Go as a provider option
- Harness Critic still uses `kimi-k2.7-code` for anti-collusion — evaluate K3 as a Critic upgrade once a provider makes it available at reasonable cost or we self-host
- **Do NOT switch cron jobs to K3 yet** — wait until provider availability and pricing are confirmed

**Action items:**
1. Investigate which providers now offer K3 (Ollama Cloud, OpenCode Go, BlockRun)
2. Evaluate self-hosting on VPS or BlockRun Modal
3. If available at T2 pricing (~$2/M), upgrade Harness Critic from kimi-k2.7-code to K3
4. Update this section once provider availability is confirmed

**Kimi K3 IS available on Nous inference API.** Confirmed Aug 2, 2026 via `GET /v1/models` (291 models; includes `moonshotai/kimi-k3` and `moonshotai/kimi-k2.7-code`). The earlier "NOT available on Nous Portal" note (Jul 27) is stale — the portal UI and the inference API are different surfaces. When Ollama Cloud is rate-limited or you need the Critic family from a direct script, use `https://inference-api.nousresearch.com/v1` with the browser-UA recipe in `references/nous-inference-api-direct.md`.

**Current Harness setup (anti-collision):**
- Evolution → `deepseek-v4-flash` (ollama-cloud)
- Critic → `kimi-k2.7-code` (ollama-cloud) — different model family from Evolution for anti-collusion
- Verifier → `deepseek-v4-flash` (ollama-cloud)
- Gardener → `deepseek-v4-flash` (ollama-cloud)

## PITFALL: Cron Jobs Don't Auto-Follow Interactive Model Switches

**Symptom:** User switches models interactively (e.g., `hermes model` → picks deepseek-v4-pro), interactive session works fine, but cron jobs start failing with HTTP 429 ("Free model capacity exhausted") or provider errors. User is confused — "I switched to the paid model, why are crons still failing?"

**Root cause:** Cron jobs carry their OWN `model`/`provider` binding in `jobs.json`, independent of the session's `config.yaml`. An interactive model switch updates `config.yaml` but does NOT touch `jobs.json`. The `cron-provider-sync` job (runs 06:00 + 18:00 UTC) catches this twice daily, but manual switches between those windows leave all LLM cron jobs pinned to the OLD model — sometimes for hours.

**Fix (one command):**
```bash
python3 /root/.hermes/profiles/gentech/scripts/cron-provider-sync.py
```
This reads the session's current `model.default` + `provider` from `config.yaml`, then re-pins every LLM cron job in `jobs.json` to match. Takes ~2 seconds. After the sync, re-run any jobs that failed during the stale window.

**NOTE (Aug 17, 2026):** The `cron-provider-sync` cron job was **removed** at Jordan's direction — we now keep most usage on Ollama Cloud and switch to OpenCode Go only occasionally, managing the two subscriptions manually. Run the script above **on demand** whenever Jordan switches providers/models. It is no longer scheduled.

**Detection:** `hermes config get model` shows the NEW model, but `cronjob list` shows jobs still on the OLD model/provider. If you see 429 errors on cron jobs while the interactive session works, this is almost certainly the cause.

**Observed:** Aug 9, 2026 — Jordan switched from V4 Flash to V4 Pro. Three cron jobs (Hub Nightly Sync, Revenue Monitor, Harness Evolution) hit 429 within the hour. All 41 LLM cron jobs were still on V4 Flash. Ran `cron-provider-sync.py` → all green.

## Rule of Thumb
If you're not sure, use Flash. If Flash fails or the output is clearly wrong, retry on K2.7. Only reach for K3 when the answer matters enough that you'd pay $15 for it.

## Version History
- **7.7.0** (Aug 9, 2026) — Added PITFALL: interactive model switches don't auto-sync cron jobs. Documented the symptom chain (429 on crons after user switches models), root cause (cron jobs carry their own model/provider in jobs.json), and the one-command fix (`cron-provider-sync.py`).
- **7.6.0** (Aug 8, 2026) — Documented ClawRouter free-tier congestion as the #1 failure mode (stalls ALL 4 groups at once; proxy healthy but upstream slow). Added correct `fallback_providers` list schema (legacy `fallback_model` deprecated; `hermes config set` stores the list as a quoted string that isn't parsed — write via config module). Added recipe to clear a per-session `/model` override. Detail in `references/clawrouter-provider.md`.
- **7.5.0** (Aug 7, 2026) — Made ClawRouter proxy a durable systemd service (`clawrouter-proxy.service`) — a session background process dies on restart and kills the provider for all groups. Documented that all 4 TG groups share one Hermes config (provider propagates automatically). Reference file `references/clawrouter-provider.md` now includes the full systemd unit + enable/verify steps.
- **7.4.0** (Aug 7, 2026) — Added ClawRouter (BlockRun) as a new fallback provider. Installed + enabled `hermes-plugin-clawrouter`, local proxy on 127.0.0.1:8402. Key pitfalls documented: `free` alias routes to gpt-oss-120b (not DeepSeek) — pin exact id `free/deepseek-v4-flash`; free tier is congested (fund wallet for paid); config.yaml is write-guarded (use `hermes config set`); no OpenClaw needed to setup. Full detail in `references/clawrouter-provider.md`.
- **7.3.0** (Aug 7, 2026) — Added the fully-automatic provider auto-switch (Ollama ⇄ OpenCode Go): script `~/.hermes/scripts/provider-auto-switch.py`, daily cron, context-save-before-restart, resume-cue message. Full mechanism in `references/provider-auto-switch.md`. Also documented the real usage endpoints: Ollama `GET /api/usage` (NOT `/v1/usage` which 404s), and OpenCode Go has NO usage endpoint (detect via live model test with `minimax-m3`).
- **7.2.0** (Aug 7, 2026) — Corrected OpenCode Go model format: BARE names, not slash (slash returns "Model not supported"). Documented that OpenCode Go's binding constraint is the MONTHLY cap (weekly/rolling can read 0% while monthly is 100%). Documented Ollama Cloud's WEEKLY reset cadence as the reason it's primary, the two-subscription flip strategy (works only when reset windows are desynced), and that `/v1/usage` + `/v1/plan` don't exist on the live API.
- **7.1.0** (July 27, 2026) — Added Kimi K3 reality check: requires extra credits, not in base plan. Harness Critic uses kimi-k2.7-code instead. Provider notes updated: Ollama Cloud is now primary, OpenCode Go is fallback.
- **7.0.0** (July 27, 2026) — V3 three-tier system. DeepSeek V4 Flash as default. Kimi K2.7 for medium. Kimi K3 for big jobs. Added K3 thinking config requirement. Jordan's directive.
