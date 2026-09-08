---
name: hermes-model-routing
description: Cost-optimized model routing for Hermes cron jobs and agent workflows. Local vs paid model selection based on task complexity.
tags: [hermes, cost-optimization, model-selection, cron, ollama]
---

# Hermes Model Routing

**Strategy:** Route each task to the most cost-effective model that can handle it. Local models for simple/repetitive tasks. Paid models for complex reasoning.

---

## Session-Level Routing — Manual Model Switching (Jul 9, 2026)

Jordan explicitly requests model switches mid-session. When he says "switch to OpenCode Go" or "use OpenCode Go":

1. **Set the active session model** via `hermes config set model "opencode-go"` — this changes the current session immediately
2. **Keep DeepSeek Flash V4 as the fallback** — do NOT change the default or remove DeepSeek. Jordan explicitly wants both available.
3. **Document the session default** so you know what to revert to:
   - Default daily driver: `deepseek/deepseek-v4-flash` via Nous
   - Build/coding session: `opencode-go` (stronger reasoning for active building)
   - Revert when session switches back to daily ops: run `hermes config set model "deepseek/deepseek-v4-flash"`

**Pattern:**
```
Normal ops → `hermes config set model "deepseek/deepseek-v4-flash"`
Build session → `hermes config set model "opencode-go"`
```

**Why this pattern:** Jordan doesn't want to change the permanent default. He wants the ability to flip between models for the current session as tasks change. The session-level `hermes config set model` overrides the default without changing it.

## Fleet Model Sync Tool (Aug 30, 2026 — "switch once, all follow")

**Tool:** `python3 /root/vaults/gentech/00-System/agent-profiles/fleet_model_sync.py`
Companion to fleet_update.py (which syncs CODE); this syncs MODEL WIRING. Reads the source
profile (default gentech) and pushes model.default / model.provider / model.base_url /
fallback_model to ALL profiles, then repins every cron job pinned to a dead-provider marker
(default: `opencode`). Flags: `--check` (dry-run), `--provider X --model Y --base-url Z`
(explicit), `--from-profile P`, `--dead-providers a,b`, `--restart` (bounce gateways after).

**Verified pitfalls (Aug 30, 2026):**
- **⚠️ THE SYNC IS MANUAL — NEVER AUTOMATIC.** `fleet_model_sync.py` is a deliberate step
  you must run after changing any model/provider config. It does NOT cascade automatically
  when you change a profile's default. Each cron job also locks its own `provider_snapshot`
  at creation time — even after a sync, jobs created before it may remain pinned to the old
  provider until the sync repins them. If you change the HQ model and expect other agents and
  cron jobs to "follow," they will not — you get stale cron jobs still hitting an exhausted
  provider while the correct config sits unused on disk. **Required sequence after ANY
  model/provider change:**
  1. Change the source profile config (`hermes config set model.default ...` etc.)
  2. Run `fleet_model_sync.py --check` to see what's drifted
  3. Run `fleet_model_sync.py` (apply) to push to all profiles + repin stale jobs
  4. Run `fleet_update.py --restart-only` to bounce gateways so they pick up new config
  5. Verify each gateway's PID/timestamp is fresh
  Skipping steps 2–4 is how 46 cron jobs stayed on an exhausted OpenCode Go while the HQ
  profile was already on Nous — config correct on disk, jobs never got the memo because the
  sync was never run. **When in doubt, always run `--check` first.**

- **Gateways read config at STARTUP.** Config edits + cron repins made while gateways are
  up do NOT reach running sessions/jobs — jobs keep failing with the OLD provider's error
  (e.g. OpenCode `GoUsageLimitError` 429) even though disk config is correct. After any
  fleet model change: run `fleet_update.py --restart-only`, then verify each gateway's
  ExecMainStartTimestamp is fresh.
- **`HERMES_PROFILE=<p>` env var does NOT scope `config set`** — writes land on the calling
  profile. Use the CLI flag: `hermes --profile <p> config set key value` (verified working).
- **⚠️ Sync output can lie about fallback_model — verify the RAW file, not the sync's report (Sep 7, 2026).**
  After changing HQ's `fallback_model` to a new provider, `fleet_model_sync.py` printed
  `updated: none needed` for the other 3 profiles — yet their raw `config.yaml` still had the
  OLD `fallback_model.provider` (e.g. `ollama-cloud`). The sync's per-profile diff only compares
  `model.default/provider/base_url` (the primary block), NOT `fallback_model`; it reported
  "none needed" because the primary block already matched, silently skipping the fallback
  that was still pointed at the old provider. **Fix: after any fleet sync, read the raw file
  for EVERY profile** (`sed -n '/^fallback_model:/,/^[a-z]/p' ~/.hermes/profiles/<p>/config.yaml`)
  and set `fallback_model` directly per profile if it drifted:
  ```bash
  for p in gentech gentech-treasury gizmo pixel; do
    hermes --profile $p config set fallback_model.provider nous --force
    hermes --profile $p config set fallback_model.model deepseek/deepseek-v4-flash --force
  done
  ```
  Do NOT trust the sync's own "updated: none needed" line — verify the raw file. This is the
  same class of trap as the stale-`base_url` cron repin: the tool reports success while disk
  config is still wrong.
- **Provider naming:** Ollama Cloud = provider `ollama-cloud` (Hermes built-in), base_url
  `https://ollama.com/v1`, key `OLLAMA_API_KEY` (per-profile .env). Z.AI's GLM-5.3-flash is
  served THROUGH it. OPENCODE_GO_API_KEY is invalid on ollama.com (401); OpenCode Go rail
  (opencode.ai/zen/go/v1) is a separate suffocated provider (429 weekly) — never a default.

## Current Routing Directive (Sep 7, 2026 — Jordan: Ollama Cloud primary, Hermes portal fallback, OpenCode Go retired)

**Fleet-wide model wiring as of Sep 7, 2026:** All 4 profiles on `deepseek-v4-flash:0731` via `ollama-cloud` (primary). Fallback is `deepseek/deepseek-v4-flash` on `nous` (Hermes portal). OpenCode Go is RETIRED — do not route to it.

**The routing picture today:**

```
Ollama Cloud (primary) — deepseek-v4-flash:0731    90-95% of work
    ↓ AUDIT pair (same provider)
GLM-5.3-flash / Kimi K2.7-code (Ollama Cloud)       code audit, review
    ↓ fallback (different provider, free)
Hermes portal (Nous) — deepseek/deepseek-v4-flash   when Ollama Cloud is down/exhausted
    ↓ second fallback
Hermes portal (Nous) — upstage/solar-pro4:free      free, output-cap limited
```

**The rule going forward:**
- **Ollama Cloud** = primary for everything. `deepseek-v4-flash:0731` default; GLM-5.3-flash / Kimi K2.7-code for the AUDIT pair.
- **Hermes portal (Nous)** = fallback only. `deepseek/deepseek-v4-flash` first, `upstage/solar-pro4:free` second. Free, US infra.
- **OpenCode Go = RETIRED.** Do NOT route to it. Its provider block remains in config but no routing surface points at it.
- **Tank awareness still required:** primary (Ollama Cloud, weekly reset) and fallback (Nous, free) are on different providers with different reset cycles — never set both to the same exhausted provider.

---

## Rate Limit Escalation Pattern (CRITICAL)

**When rate limited, ALWAYS escalate WITHIN the same provider first before falling back to other providers.** But note: on Nous portal (our primary), free models don't have rate limits in the traditional sense — they have capability limits (Solar Pro 4 output cap). The escalation pattern for Nous is model-switching, not tier escalation.

## Nous Portal Model Switching (Primary Provider)

**Our primary provider is Nous Research portal. Free models on Nous don't burn credit and have no rate limits — they have different capability profiles. When a Nous free model hits a limitation, switch to a different free model on the same provider:**

```
Solar Pro 4 free hits output cap (trunctated response)
    ↓ SAME PROVIDER, DIFFERENT MODEL
DeepSeek V4 Flash on Nous (no output cap observed, same base_url, still free)
    ↓ for vision tasks
tencent/hy3:free on Nous (vision model, if needed)
    ↓ paid model on Nous is needed (rare)
Paid Nous model (if available) → use credit balance
    ↓ all Nous options exhausted or wrong capability
Different provider tank (OpenCode Go, BlockRun, OpenAI Codex, local Ollama)
```

**Key distinction from Z.AI pattern:** Z.AI escalation is tier-by-tier within one provider (glm-4.7 → glm-5 → glm-5.2). Nous escalation is model-by-model within one provider (solar-pro4 → deepseek-v4-flash → hy3 → paid). Both follow the "same provider first" rule — but Nous has more free models to switch between than Z.AI does.

### When NOT to use Solar Pro 4 Free (output cap issues)

See `references/solar-pro4-nous-limits.md` for full symptoms, data, and workarounds. Summary:
- Solar Pro 4 on Nous (`upstage/solar-pro4:free`) has a per-response output cap that truncates long responses mid-generation
- Fine for: chat, short answers, coordination, summaries under ~500 tokens, code snippets
- Switch to DeepSeek V4 Flash on Nous when you need long-form output in a single response
- This is the SAME provider (no billing impact, same base_url) — instant switch, no waiting

## Z.AI Escalation Hierarchy (Historical — CURRENTLY UNUSABLE)

**⚠️ Z.AI has been unusable since Jul 4, 2026.** All tiers return 429 or timeout. Do NOT route jobs to Z.AI without first confirming current health via a live API call. The escalation ladder below is preserved for reference but is NOT operational.

```
Rate Limited on (if Z.AI were healthy):
glm-4.7 (standard, cheapest Z.AI tier)
    ↓ ESCALATE TO
glm-5 (premium, complex analysis, higher rate limits)
    ↓ ESCALATE TO
glm-5.2 (coding powerhouse, Labs tasks only)
    ↓ FALLBACK TO
Nous portal free models (our primary — same-provider switch)
    ↓ if Nous can't handle it
OpenCode Go / GLM-5.2 (when billing resets)
    ↓ pure US fallback
OpenAI Codex (GPT-5.x, US infra)
```

**Note: glm-4.5-flash is deprecated.** Z.AI tiers now start at glm-4.7. If you see a job or config referencing glm-4.5-flash, replace it — but Z.AI is currently broken across all tiers anyway, so the real fix is to route to Nous.

### Model Tiers (Light → Heavy) — Sep 5, 2026

**Our model hierarchy is now Nous-first. Free Nous models handle the vast majority of work. Paid tiers (OpenCode Go, BlockRun Kimi) are reserved for specific capability needs, not general usage.**

| Tier | Model | Provider | Cost | Best For | Notes |
|------|-------|----------|------|----------|-------|
| 0 | `upstage/solar-pro4:free` | Nous | Free | Default daily driver, 90% of work | Has per-response output cap — switch to DeepSeek for long-form |
| 0b | `deepseek/deepseek-v4-flash` | Nous | Free | Long-form output, coding, general work | No output cap observed; same provider as Solar (instant switch) |
| 1 | `glm-5.3-flash` / `glm-5.2` | OpenCode Go | $10/mo sub | Heavy builds, complex analysis (when billing resets) | Exhausted until ~Sep 6; fleet switched off it Sep 5 |
| 2 | `kimi-k2.7-code` / `kimi-k3` | BlockRun | $3/1M in, $15/1M out | Audit, coding powerhouse, 1M ctx (K3) | Pre-funded wallet — check balance before routing |
| 3 | `gpt-5.x` family | OpenAI Codex | US-only fallback | Pure-US fallback, no Chinese-origin dependency | Configured in all 4 profiles as hard fallback |
| — | `tencent/hy3:free` | Nous | Free | Vision tasks | Vision provider, not for text work |

---

**When Hermes returns `RateLimitError` (HTTP 429):**

1. **Check current model tier:**
   ```python
   # Model tiers by capability (lightest → heaviest)
   Z_AI_TIERS = [
       # NOTE: glm-4.5-flash is deprecated. Z.AI tiers start at glm-4.7.
       "glm-4.7",        # Level 1: Cheapest Z.AI tier
       "glm-5",          # Level 2: Premium
       "glm-5.2",        # Level 3: Coding powerhouse (Labs only)
   ]

   DEEPSEEK_FALLBACK = "deepseek-v4-flash"

   def find_current_tier(model):
       try:
           return Z_AI_TIERS.index(model)
       except ValueError:
           return -1  # Not a Z.AI tier, use DeepSeek fallback
   ```

2. **Escalate within the same provider first:**

**For Nous portal (our primary — free models):**
```python
# Nous free models don't have rate limits — they have capability differences
# Switch model within the same provider for different capabilities

NOUS_MODEL_SWITCH = {
    "output cap / truncation": "nous/deepseek/deepseek-v4-flash",  # same provider, no cap
    "vision task needed": "nous/tencent/hy3:free",                   # vision model
    "general work on Solar hits cap": "nous/deepseek/deepseek-v4-flash",
}

# Pattern: stay on Nous, swap model
if provider == "nous" and issue == "output truncation on solar":
    return provider="nous", model="deepseek/deepseek-v4-flash"
```

**For Z.AI (unusable since Jul 4 — do not route here without confirming health):**
```python
if error_type == "RateLimitError" and provider == "zai":
    # Any Z.AI model is dead right now — fall through to Nous
    return provider="nous", model="deepseek/deepseek-v4-flash"
```

3. **Fall back to a DIFFERENT provider when the current one is fully exhausted:**

**Our current fallback path (Sep 7, 2026):**
```python
# Primary: Ollama Cloud
# When Ollama Cloud can't handle the task → Hermes portal (Nous) fallback
# OpenCode Go is RETIRED — never route to it

FALLBACK_CHAIN = [
    ("ollama-cloud", "deepseek-v4-flash:0731"),        # primary
    ("ollama-cloud", "glm-5.3-flash"),                 # same provider, AUDIT pair
    ("nous", "deepseek/deepseek-v4-flash"),           # Hermes portal fallback, free
    ("nous", "upstage/solar-pro4:free"),              # second Nous fallback, free
]

# NEVER set fallback to the same exhausted provider — that's the stuck-agent trap
# PRIMARY (Ollama Cloud, weekly reset) and FALLBACK (Nous, free) are on different
# providers with different reset cycles
```

### Why This Matters

**❌ Wrong behavior (what we saw historically):**
- Rate limited on `glm-4.5-flash` (deprecated) → Routed to OpenRouter (external)
- Result: Cost blowup, untested provider, no hierarchy

**✅ Correct behavior (current):**
- Rate limited on a provider → Escalate within the same provider first
- If Z.AI exhausted → Fall back to DeepSeek Flash (not external proxies)
- DeepSeek is the safe free/cheap fallback for all tiers

### Cron Job Auto-Escalation

For cron jobs hitting rate limits:

```python
# In cron job prompt, add:
from hermes_tools import terminal

try:
    # Run task with current model
    result = run_task()
except RateLimitError:
    # Switch to DeepSeek as fallback
    terminal("hermes config set default.model deepseek-v4-flash --profile gentech")
    # Retry task
    result = run_task()
```

### Provider Priority Order (Jul 2026+)

**Default path: DeepSeek Flash first, escalate to paid when needed.**

| Priority | Provider | Model | Cost | Use |
|----------|----------|-------|------|-----|
| 1 | DeepSeek | `deepseek-v4-flash` | Free/Cheap | Default — 90% of work |
| 2 | OpenCode Go | `opencode-go:default` | Paid monthly | Heavy builds, complex analysis |
| 3 | Z.AI | `glm-4.7` | Paid (token) | Cron jobs, routine paid tasks |
| 4 | Z.AI | `glm-5` | Paid (premium) | Analysis, audits |
| 5 | Z.AI | `glm-5.2` | Paid (premium) | Labs, code audits only |

Local Ollama, Groq, Cloudflare Workers AI, NVIDIA NIM are available free alternatives but no longer default fallbacks — DeepSeek covers the free/cheap role better.

---

## Task Classification Rules

### Route to Local Qwen (Free)

**Use when:**
- Simple read/write operations (file sync, vault maintenance)
- Status checks and health monitoring
- Simple summarization with structured input
- Repetitive automation (every X minutes/hours)
- Tasks that don't require deep reasoning or synthesis

**Examples:**
- Nightly vault maintenance
- Hub data sync (JSON file operations)
- Cron health monitor
- Gaming hub sync (build data → GitHub Pages)
- Morning to-do list (simple status report)

---

### Ollama Cloud — model ladder on exhausted usage (verified Aug 30, 2026)
Same key/models list works from any profile. Ladder when glm-5.3-flash hits usage:
1. Swap model within `ollama-cloud` (same provider): `deepseek-v4-flash:0731` (proven), `nemotron-3-super` (light), `nemotron-3-ultra` (heavy), `nemotron-3-nano:30b` (cheap burst).
2. True overflow = different PROVIDER (caps are per-provider): NVIDIA NIM free hosted (build.nvidia.com, OpenAI-compatible ~40 RPM), Nous free (`tencent/hy3:free`), local Ollama `llama3.1:8b`.
3. **Reasoning-model trap (verified):** nemotron-3-* and glm-5.3-flash put reasoning in a separate `reasoning` field and content AFTER it. With small `max_tokens` you get EMPTY content + `finish_reason: length`. Give ≥300 tokens for simple replies.
4. Full sync anytime: `fleet_model_sync.py` → `fleet_update.py --restart-only` (see error-runbook E-01/E-02).

### Route to Ollama Cloud (Subscription)

**Base URL:** `https://ollama.com/v1` (OpenAI-compatible)
**Auth:** `Authorization: Bearer <key>` — key format is `<id>.<secret>`

**Available models include** `deepseek-v4-flash`, `deepseek-v4-pro`, `glm-5.2`, `kimi-k2.7-code`, `mistral-large-3:675b`, `qwen3.5:397b`, `gemma4:31b`, and more.

**Note:** `api.ollama.com` returns 403 for chat — use `ollama.com` as the base URL. Models list works on both. See `references/ollama-cloud-setup.md` for full model list and curl example.

### Route to Groq (Free, Ultra-Fast)

**Use when:**
- Need ultra-fast response (<500ms)
- Simple classification or routing decisions
- Quick text generation (non-critical)
- Tasks that don't need complex reasoning

**Rate limits:** 30 RPM, 6,000 TPM, 14,400 req/day

**Examples:**
- Email routing/classification
- Quick text summaries
- Simple Q&A
- Tag extraction

---

### Route to Nous Portal (Free)

**Base URL:** `https://inference-api.nousresearch.com/v1`
**Auth:** OAuth (client_id: `nous-research`, client_secret empty) — configured in profile `.env` as `NOUS_CLIENT_ID` / `NOUS_CLIENT_SECRET` or handled by Hermes.

**Available free models include:**
- `upstage/solar-pro4:free` — Upstage flagship, free on Nous
- `deepseek/deepseek-v4-flash` — DeepSeek Flash, free on Nous
- `tencent/hy3:free` — Tencent vision model, free on Nous

**Note:** Solar Pro 4 free has a per-response output token cap that truncates long responses. See `references/solar-pro4-nous-limits.md` for symptoms, workarounds, and when to switch to DeepSeek Flash instead.

**Switch pattern when a Nous free model hits a limit:** stay on the same provider (same base_url, no billing impact), swap to a different free model. E.g. Solar Pro 4 output cap → DeepSeek V4 Flash (same provider, still free). Revert when desired.

### Route to DeepSeek (Free → Paid)

**Use when:**
- Strong coding capabilities needed
- Complex reasoning within 5M token budget
- Audit-level analysis while budget lasts
- General-purpose coding tasks

**Rate limits:** 5M free tokens (one-time), 60 RPM, then paid

**Examples:**
- Code generation and refactoring
- Bug diagnosis and fixes
- Technical documentation
- Code reviews (when budget allows)

---

### Route to Cloudflare Workers AI (Free, Edge)

**Use when:**
- Edge deployment needed (geo-distributed)
- User-facing features requiring low latency
- Simple inference at the edge
- No GPU infrastructure available

**Rate limits:** 10K-100K req/day (neuron-based)

**Examples:**
- User-facing chat widgets
- Real-time content moderation
- Simple classification at edge
- Geo-aware features

---

### Route to NVIDIA NIM (Free, Enterprise)

**Use when:**
- Enterprise-grade models needed
- Complex analysis with large context
- Multiple concurrent inferences needed
- High throughput required

**Rate limits:** 15,000 TPM, 14,400 req/day (phone verification required)

**Examples:**
- Enterprise document analysis
- Large-scale data processing
- Multi-agent orchestration
- Complex decision-making

---

### Route to Z.AI GLM-4.7-flash (FREE TIER) — BROKEN as of Jul 4

**⚠ DEPRECATED — glm-4.7-flash times out (read timeout) on all API calls as of Jul 4, 2026.**

Previously free (worked when paid quota exhausted), but now completely unresponsive.  
**Fix:** Replace all cron job model assignments from `glm-4.7-flash` → `deepseek-v4-flash` with `opencode-go` provider.

**How to verify (current state):**
```bash
# Test via actual API call
curl -s --max-time 15 -X POST https://api.z.ai/api/paas/v4/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ZAI_API_KEY" \
  -d '{"model": "glm-4.7-flash", "messages": [{"role": "user", "content": "test"}], "max_tokens": 5}'

# Timeout = BROKEN (no longer available)
# 429 = "Insufficient balance" → No access (glm-4.7 standard)
# 200 = Works → Has access
```

**Current Z.AI status (Jul 4, 2026):**
- `glm-4.7-flash` — TIMEOUT (broken, do not use)
- `glm-4.7` — 429 insufficient balance (paid quota exhausted)
- `glm-5` — 429 insufficient balance
- `glm-5.2` — 429 insufficient balance
- All Z.AI tiers effectively unusable until account is recharged

**Fallback: deepseek-v4-flash via opencode-go** is the current daily driver and works reliably.

---

### Route to Z.AI GLM-4.7 (Standard Paid)

**Use when:**
- Complex reasoning required
- Multi-step analysis
- Summarization of unstructured content
- Daily/weekly recurring complex tasks
- Free providers exhausted

**Examples:**
- Daily Digest (summarize and synthesize)
- Market analysis signals (Tradesta)
- Revenue Monitor (financial analysis)
- POE2 Build Health (game analysis)

---

### Route to Z.AI GLM-5 (Premium Paid)

**Use when:**
- Heavy analysis or audit
- Critical decision-making
- Multi-repo or large-scale code review
- Complex strategic assessment
- Free and cheaper models insufficient

**Examples:**
- Sunday Review (weekly deep dive)
- FOMC Summary (Fed analysis)
- API Marketplace Scout (comprehensive scan)
- Production code audits

---

## Cron Job Configuration

### Setting Model per Job

**NOTE:** The `cronjob action=update` syntax shown below is a Python-level Hermes agent tool, NOT a CLI command. The CLI (`hermes cron edit`) does NOT support `--model` or `--provider` flags. For the actual working approach to change provider/model on cron jobs, see the `model-configuration-management` skill's `references/cron-jobs-bulk-provider-switch.md` — the canonical method is editing `~/.hermes/profiles/gentech/cron/jobs.json` directly.

```bash
# Local Qwen (free, unlimited)
cronjob action=update job_id=<job_id> model='{"model": "qwen2.5-coder:7b", "provider": "ollama"}'

# Groq (free, 30 RPM, 6K TPM, 14.4K req/day)
cronjob action=update job_id=<job_id> model='{"model": "llama-3.1-8b-instant", "provider": "groq"}'

# DeepSeek (5M free tokens, then paid, 60 RPM)
cronjob action=update job_id=<job_id> model='{"model": "deepseek-v4-flash", "provider": "deepseek"}'

# Cloudflare Workers AI (free, 10K-100K req/day)
cronjob action=update job_id=<job_id> model='{"model": "@cf/meta/llama-3.1-70b-instruct", "provider": "cloudflare"}'

# NVIDIA NIM (free, 15K TPM, 14.4K req/day)
cronjob action=update job_id=<job_id> model='{"model": "meta/llama-3.1-405b-instruct", "provider": "nvidia_nim"}'

# Z.AI (paid)
cronjob action=update job_id=<job_id> model='{"model": "glm-4.7", "provider": "zai"}'
```

### Enable Toolsets

Always enable only the toolsets needed:
```bash
cronjob action=update job_id=<job_id> enabled_toolsets='["terminal", "file"]'
```

### Script-Only Jobs (No LLM)

For pure scripts that don't need an LLM:
```bash
cronjob action=update job_id=<job_id> no_agent=true script=<script_path>
```

---

## Ollama Local Setup

### Critical: Context Window Requirement

**Hermes Agent requires 64K+ context window.** Do not use models with smaller context.

| Model | Context | Status |
|-------|---------|--------|
| llama3.1:8b | 128K | ✅ Recommended |
| llama3.1:70b | 128K | ✅ Works (higher RAM) |
| qwen2.5-coder:7b | 32K | ❌ Too small - Hermes will reject |
| mistral:7b | 32K | ❌ Too small - Hermes will reject |

### Install and Configure

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull model with 64K+ context (llama3.1:8b = 128K context, 4.9GB)
ollama pull llama3.1:8b

# Verify running
systemctl is-active ollama
curl http://localhost:11434/api/tags
```

### Hermes Config

Add to `~/.hermes/profiles/<profile>/config.yaml`:

```yaml
providers:
  ollama:
    base_url: "http://localhost:11434/v1"
    default_model: "llama3.1:8b"
    discover_models: false
    models:
      - llama3.1:8b
    name: Ollama Local
    transport: openai_chat
```

### Fallback Chain

Primary fallback is DeepSeek Flash (free/cheap backup when default is unavailable):
```yaml
fallback_providers:
  - provider: deepseek             # Free/cheap backup
    model: deepseek-v4-flash
  - provider: zai                  # Paid (only when DeepSeek can't handle it)
    model: glm-4.7
```

Old default (Ollama local + zai:glm-4.7) is **superseded** — DeepSeek Flash covers both the free backup role (replacing Ollama) and the paid mid-tier role (replacing zai:glm-4.7 for routine work).

---

## Default Fallback Pattern

Set default to DeepSeek Flash (daily driver), with Nous as fallback provider:

```bash
# Use model.default, NOT default.model — flat default: competes with model: block
hermes config set model.default deepseek/deepseek-v4-flash
hermes config set model.provider nous
hermes config set model.base_url https://inference-api.nousresearch.com/v1

# Pin fallback to same provider to prevent OpenRouter fallthrough
hermes config set fallback_model.provider nous
hermes config set fallback_model.model upstage/solar-pro4:free  # free, currently healthy; do NOT set to a deprecated model
```

⚠ **CRITICAL: Always use `model.default`, never `default.model`** — `hermes config set default.model` creates a flat `default:` block at root level that competes with the real `model:` block. When the provider field differs between them, the gateway falls through to unintended providers on failure.

Z.AI (`zai:glm-4.7`) as default is **no longer correct** — Z.AI has phantom burn issues (40%+ unexplained weekly usage) and should be reserved for explicitly assigned heavy tasks only.

---

## Troubleshooting

### Cron Job Fails with "provider weekly usage limit"

**Cause:** Job is set to provider with limits, not local model.

**Fix:**
1. Check job's model provider: `cronjob action=list`
2. Update to local or alternative provider: `cronjob action=update job_id=... model='{"model":"qwen2.5-coder:7b","provider":"ollama"}'`
3. If local model fails, verify Ollama is running: `systemctl is-active ollama`

### Ollama Connection Refused

**Cause:** Ollama service not running or wrong port.

**Fix:**
```bash
# Start Ollama
systemctl start ollama

# Verify
curl http://localhost:11434/api/generate -d '{"model":"qwen2.5-coder:7b","prompt":"test","stream":false}'
```

---

## Peak-Hour Optimization (Z.AI)

**Z.AI Quota Multipliers (Beijing UTC+8):**
- Peak: 14:00-18:00 = 3x quota cost
- Off-peak: All other = 1x quota cost (promo through Sept 2026)

**Converted to Jordan's ET:**
- Peak: 1:00 AM - 5:00 AM = 3x quota cost (Jordan sleeping)
- Off-peak: 5:00 AM - 1:00 AM = 1x quota cost (Jordan awake)

**Routing Rule:**
```python
from datetime import datetime
import pytz

et = pytz.timezone('America/New_York')
current_hour = datetime.now(et).hour

if 1 <= current_hour < 5:
    # Peak hours (3x quota) → defer to local models
    routing = "ollama"  # or other free providers
else:
    # Off-peak (1x quota) → GLM-5.2 available
    routing = "zai"
```

**Cron Job Example:**
```python
# In prompt, add quiet hours check for peak-hour deferral
import pytz
et = pytz.timezone('America/New_York')
current_hour = datetime.now(et).hour

if 1 <= current_hour < 5:
    print("Quiet hours — peak quota (3x), deferring to off-peak")
    # Skip or defer task
```

---

## Cost Optimization Patterns

### Pattern 1: Free Tier Maximization (80% Savings)

```
Task → Classify → Route to best free provider
─────────────────────────────────────────────
Simple/ultra-fast → Groq (30 RPM, free)
Coding/reasoning → DeepSeek (5M free tokens)
Edge/geo → Cloudflare Workers AI (10K-100K req/day)
Enterprise → NVIDIA NIM (15K TPM, 14,400 req/day)
Local only → Local Qwen (no cost, no rate limit)
```

**Estimated savings:** 80% of costs for simple/coding tasks. Only pay when free tier exhausted.

---

### Pattern 2: Junior + Senior Workflow (Build → AUDIT + FIX)

**Current Standard (Jul 5, 2026):**

```
Phase 1: BUILD (Junior - GLM-4.7/DeepSeek V4 Flash, paid quota first → free fallback)
   → Execute task: code, docs, integration
   → Get it working
   → Basic error handling
   → Output: draft artifact

Phase 2: AUDIT + FIX (Senior - GLM-5.2, coding powerhouse)
   → Review quality
   → FIX issues in the same session (not just report)
   → Add missing: error handling, edge cases, type hints, docs
   → Verify fixes work
   → Output: final, production-ready artifact

Phase 3: Deploy
```

**Cost Impact:**
- Build with GLM-4.7/DeepSeek: ~$0.00-0.07 (paid quota first, then free/cheap)
- Audit + Fix with GLM-5.2: ~$0.10-0.30 (review + fix in one session)
- Total per project: ~$0.10-0.37 (vs $0.40-1.00 full GLM-5.2)
- **Savings: 70-75%**

**Why This Works:**
- ✅ Cheap model handles heavy lifting (paid quota first, then free)
- ✅ GLM-5.2 ensures production quality (audit + fix in one session)
- ✅ No manual back-and-forth (fix happens immediately)
- ✅ Single GLM-5.2 session covers both audit and fix
- ✅ 70% cost savings (cheap default + targeted audit)

**Forge Compliance:**
- BUILD: DeepSeek V4 Flash (or GLM-4.7 if DeepSeek unavailable)
- AUDIT: GLM-5.2 (big boy for quality assurance)
- Protocol documented in: `00-HQ/build-queue.md` (Build Queue Execution Protocol)

**Previous Pattern (Deprecated):**
```
Phase 1: Build (Junior - Local Qwen, free)
Phase 2: Audit (Senior - GLM-5.2 or DeepSeek, paid/free)
```
Still works, but DeepSeek V4 Flash is now the preferred default (cloud, no local setup).

---

### Pattern 3: Parallel Pipeline with Free Tiers

```
Time 0:  Local Qwen builds Project A
Time 5:  Local Qwen builds Project B | Groq audits Project A
Time 10: Local Qwen builds Project C | DeepSeek audits Project B | Fix Project A
```

3x throughput through parallelism + free tier optimization.

---

## Migration Checklist

When migrating cron jobs to optimized routing:

1. List all jobs: `cronjob action=list`
2. Classify each job by complexity
3. Update model per job:
   - **Routine/monitoring** → DeepSeek Flash (default)
   - **Heavy analysis/coding** → OpenCode Go (GLM)
   - **Highest priority/audit** → Z.AI GLM-5 or 5.2
4. Pause jobs hitting rate limits
5. Set default model to DeepSeek Flash via Nous:
   ```bash
   hermes config set model.default deepseek/deepseek-v4-flash
   hermes config set model.provider nous
   hermes config set model.base_url https://inference-api.nousresearch.com/v1
   ```
6. Run test: `cronjob action=run job_id=<job_id>`

---

## Provider Balance Awareness (Tank Model)

**The insight:** every provider has a "tank" — a balance, subscription, or free tier that can run dry independently of every other provider. Smart routing checks the tank *before* sending a job there, not after it hits a 429.

**Why it matters:** without tank awareness, the routing chain is: pick model → send → 429 → fallback → 429 → retry loop. The agent spins until the turn times out or the user sees "typing..." forever. Tank-aware routing prevents the fallthrough-to-dead-provider trap and lets you give honest cost/balance quotes before committing.

**Routing decision with tank awareness:**

```
For each incoming job:
  1. Classify task complexity (simple / medium / heavy / audit)
  2. List candidate models for that complexity tier
  3. For each candidate, check:
     a. Is the provider's tank healthy? (not exhausted, not rate-limited)
     b. What's the marginal cost from the remaining balance?
  4. Pick cheapest candidate with a healthy tank
  5. If no healthy tank exists at the needed tier, escalate tier or flag to user
```

**User-facing transparency:** when a user asks "what will this cost?", quote model + provider + estimated tokens + balance remaining. Example: "Solar Pro 4 (Nous, free): $0. GLM-5.2 (OpenCode Go): $0 marginal (subscription active, resets tomorrow). Kimi K2.7-code (BlockRun): ~$3-5 for this job size."

**See:** `references/provider-tanks.md` — full tank inventory, how to check each provider's balance, exhaustion signals, and reset cycles.

## Pitfalls

- **Don't assume "local default"** — route by task complexity, not just cost
- **Fallback chain validity — dead fallback = stuck agent.** When `fallback_model.provider` points at a provider that is ALSO exhausted, the agent enters a retry loop: primary fails → fallback fails → retries every 600s → never completes the turn. User sees "typing..." indefinitely, never gets a reply. **(Sep 5, 2026 incident: OpenCode Go monthly limit hit; `fallback_model` was also set to `opencode-go / glm-5.2` — the same exhausted provider. Treasury bot stuck until the fallback was re-pointed at Nous.)** 
  - **Fix:** before relying on a fallback, verify the fallback provider's tank is healthy. Primary and fallback should never share the same exhaustion axis — if primary is a subscription provider (OpenCode Go, Ollama Cloud), the fallback should be a *different* provider (Nous free models, DeepSeek, local Ollama), not the same subscription on a different model.
  - **After any provider exhaustion event:** audit ALL fallback references — `fallback_model`, any cron-job-level model pins, and the skill's rate-limit escalation targets — for that provider and swap them. A single exhausted provider can silently trap multiple jobs if they all share the same fallback chain.
  - **Routing rule of thumb:** primary and fallback must be on different providers with different reset cycles. Same-provider fallback only works within a provider's own tier ladder (e.g. Z.AI glm-4.7 → glm-5 → glm-5.2), never across the primary→fallback boundary.
- **Don't set local model for audits** — audits need strong reasoning, use GLM-5.2
- **Always verify Ollama is running** — local jobs fail silently if Ollama is down
- **Watch rate limits** — even Z.AI has limits; distribute paid tasks across GLM-4.7 and GLM-4.7-flash
- **Scripts don't need LLMs** — use `no_agent=true` for pure script execution
- **Delegation fallback** — delegation without explicit model falls back to config default; ensure default is set
- **Ollama model size vs. RAM** — 70B+ models require 31GB+ RAM; 15GB systems max out at 8B models. Check `free -h` before pulling large models. llama3.1:70b fails with "ggml_aligned_malloc: insufficient memory" on 15GB systems.
- **Config editing rules** — Cannot `patch` or `write_file` Hermes config directly due to security guard. Use `hermes config set key value` or `hermes config edit` instead.
- **Z.AI phantom burn detection** — If Z.AI weekly usage shows 35-40%+ burn without corresponding work, assume an unknown caller is draining quota. Symptoms: usage graph shows steady consumption during idle hours, actual dev work can't account for the burn rate. Response: (1) Switch main model to DeepSeek Flash immediately, (2) Keep Z.AI/GLM reserved for explicitly assigned heavy tasks only, (3) Regenerate API key after next quota reset to kill any stray caller, (4) Audit cron jobs for unexpected Z.AI model assignments. Do not assume the burn is legitimate just because the dashboard shows it.
- **ClawRouter plugin overrides explicit routing** — If ClawRouter-Hermes is in `plugins.enabled`, the explicit `model.provider` setting becomes advisory, not enforced. ClawRouter auto-routes across providers when the primary fails, often landing on OpenRouter. If you want `model.provider: nous` to be enforced, disable ClawRouter: `hermes config set plugins.enabled "[kapso, gentech-session-startup]"`
- **Config entropy from competing flat defaults** — `hermes config set` creates flat root-level keys (`default:`, `fallback_providers[0]:`, `opencode-go:`) that compete with the real nested `model:` block. These accumulate over time and cause routing fallthrough chains that land on OpenRouter. Run `grep -n "^default:\|^fallback_providers\[0\]:\|^opencode-go:\|^custom_providers:" ~/.hermes/profiles/gentech/config.yaml` to check. Remove them with `sed -i '/^default:$/,/^[a-zA-Z]/{...}'`
- **`fallback_model` must be set explicitly** — Without `fallback_model`, Hermes falls through to auto-discovery when the primary provider fails, often routing to OpenRouter. Always pin it: `hermes config set fallback_model.provider nous` + `hermes config set fallback_model.model upstage/solar-pro4:free` (free, currently healthy; do NOT set to a deprecated model like `claude-3.5-sonnet` — a dead endpoint crashes all cron jobs that hit the fallback).
- **`custom_providers` is a stale routing hazard** — The `custom_providers:` section from old `hermes setup` runs persists indefinitely and creates unintended routing targets. Check with `grep -A 4 "^custom_providers:"` and remove stale entries

---

## Verification

### Test Local Model

```bash
curl -s http://localhost:11434/api/generate \
  -d '{"model":"qwen2.5-coder:7b","prompt":"What is 2+2?","stream":false}' \
  | head -5
```

### Test Cron Job Routing

```bash
# Run a local job
cronjob action=run job_id=<local_job_id>

# Check it used local model (not paid provider)
# Look in cron output/logs
```

### Check Job Distribution

```bash
cronjob action=list | grep -E "provider|model" | sort | uniq -c
```

---

## References
**References**
- `references/provider-tanks.md` — Provider tank inventory: balance types, exhaustion signals, reset cycles, how to check each provider's tank before routing, double-subscription-exhaustion scenario (Sep 5, 2026).
- `scripts/cron-model-audit.py` — Script to audit and suggest model routing for all cron jobs
- `templates/cron-job-config.yaml` — Template for new cron jobs with optimized routing
- `references/dual-agent-coordination-pattern.md` — Advanced dual-agent workflows and scheduling

## Session Learnings (Jun 28, 2026)

**Rate Limit Escalation Bug (Jun 29, 2026):**

**What went wrong:**
- Rate limited on `glm-4.5-flash` → Routed to OpenRouter (external provider)
- Result: Cost blowup, untested provider, no hierarchy
- **Root cause**: Model routing skill existed but didn't implement escalation logic

**What we fixed:**
1. ✅ Added rate limit escalation pattern to model routing skill
2. ✅ Created `scripts/rate-limit-escalation.py` — auto-escalates within Z.AI before external fallback
3. ✅ Updated skill with Z.AI tier hierarchy (glm-4.5-flash → glm-4.7 → glm-5 → glm-5.2)
4. ✅ Configured fallback to Ollama (llama3.1:8b) — correct per hierarchy

**Correct escalation behavior:**
```
Rate limited on glm-4.5-flash
    ↓ ESCALATE TO (within Z.AI)
glm-4.7 (higher rate limits, better reasoning)
    ↓ IF STILL RATE LIMITED
glm-5 (premium, highest limits)
    ↓ ONLY THEN
External fallback: Norris Research (norrs-v2.5) → Groq → DeepSeek
```

**Script usage:**
```bash
# Monitor and auto-escalate (blocking)
python3 ~/.hermes/profiles/gentech/scripts/rate-limit-escalation.py

# Check current status
python3 ~/.hermes/profiles/gentech/scripts/rate-limit-escalation.py --check

# Reset to base model (when rate limits clear)
python3 ~/.hermes/profiles/gentech/scripts/rate-limit-escalation.py --reset
```

**Automatic Cron Monitoring (Jun 30, 2026):**

The rate limit monitor runs automatically as a cron job:
- **Cron Job ID:** `1a6d403954b9`
- **Name:** "Rate Limit Monitor — Auto-Escalate"
- **Schedule:** Every 5 minutes (`*/5 * * * *`)
- **Mode:** `no_agent=true` (script-only, no LLM needed)
- **Workdir:** `/root/.hermes/profiles/gentech/scripts`

What the cron job does automatically:
1. Scans `/root/.hermes/logs/errors.log` and `/root/.hermes/logs/agent.log` for rate limit patterns
2. If rate limit detected → Escalates to next Z.AI tier within the hierarchy
3. Updates status file at `~/.hermes/profiles/gentech/.rate-limit-status.json`
4. Writes escalation events to logs

**To verify automatic monitoring:**
```bash
# Check cron job exists
cronjob action=list | grep "Rate Limit Monitor"

# Check last run status
# (Look for job_id 1a6d403954b9 in cron list output)

# Manual status check
cd /root/.hermes/profiles/gentech/scripts
python3 rate-limit-escalation.py --check
```

**Status File Format:**
`~/.hermes/profiles/gentech/.rate-limit-status.json`:
```json
{
  "current_tier": 0,
  "last_update": "2026-06-30T18:30:00Z",
  "rate_limit_detected": false,
  "rate_limit_timestamp": null
}
```

**What worked:**
- Rerouting 4 Z.AI quota-exceeded jobs to local Ollama fixed failures immediately
- Converting 2 jobs to script-only (no_agent=true) eliminated LLM cost entirely
- Local Ollama (qwen2.5-coder:7b) handles repetitive tasks without quota limits
- Hybrid setup: Z.AI (GLM-5.2 heavy work) + Ollama (llama3.1:8b daily work) = cost optimization
- Provider consolidation: Removed OpenCode Go ($10/mo saved), kept Z.AI for heavy work only

**What didn't:**
- Z.AI weekly quota limit blocking high-frequency cron jobs
- Using Ollama for complex tasks (context snapshot failed, needed stronger model)
- Pulling llama3.1:70b on 15GB RAM system (failed with "insufficient memory" error)

**Pattern:** When Z.AI quota limit hits:
1. Check if task needs complex reasoning (synthesis, judgment, multi-step)
2. If no → Convert to script-only (no_agent=true)
3. If yes → Reroute to Ollama (qwen2.5-coder:7b)
4. If Ollama fails → Pause job and notify user to increase budget

**Example fixes from this session:**
- `[Jordan] POE2 Build Health` → Z.AI → Ollama (success)
- `[Vanito] Game Release Intelligence` → Z.AI → Ollama (success)
- `Morning To-Do List` → Z.AI → Script-only (morning-todo.py, success)
- `Gaming Hub Sync` → Ollama error → Script-only (gaming-hub-sync.py, success)

**Peak-Hour Discovery (Jun 28, 2026):**
- Z.AI peak hours: 14:00-18:00 Beijing UTC+8 = 1:00-5:00 AM ET (3x quota)
- Z.AI off-peak: 5:00 AM-1:00 AM ET (1x quota, promo through Sept 2026)
- Perfect alignment: Jordan awake = off-peak (1x), sleeping = peak (3x)
- Heavy GLM-5.2 work should run during Jordan's awake hours (5:00 AM-1:00 AM ET)

**Cron Job Fixing Pattern (Jun 28, 2026):**
When Z.AI quota limit hits cron jobs:
1. Check job complexity (simple → script-only, complex → Ollama)
2. Create Python scripts in `~/.hermes/profiles/<profile>/scripts/`
3. Add Git pull-before-push to avoid push conflicts:
   - `git pull --rebase` BEFORE `git add` (for clean repos)
   - Or stash unstaged changes: `git stash` → `git pull --rebase` → `git stash pop`
4. Update cron job with `no_agent=true` for script-only mode
5. Test script manually before cron runs it: `python3 scripts/name.py`

**Routing Gap Pitfall (Jun 28, 2026):**
- Configured model ≠ actual model used (router fallback)
- Example: `API Marketplace Scout` configured for GLM-5, but running with MiMo-V2.5
- When quota burn is unexplained, check: `hermes status` and verify routing
- Fix: Verify provider name matches `custom_providers:` config exactly
- Check: `grep -A3 "custom_providers" ~/.hermes/profiles/<profile>/config.yaml`

**Hybrid Architecture Pattern (Jun 28, 2026):**
- Home laptop: Hermes + Ollama (llama3.1:8b) + Discord = $0 daily coding
- Shared VPS: Hermes + Z.AI (GLM-5.2) = paid heavy work only
- Vault sync: gentech-vault (GitHub) shares skills/memories between systems
- Cron jobs: Run on VPS (24/7 availability), manual work on laptop (when home)
- Savings: $10/mo OpenCode Go removed; daily coding at home is free

**Dual-Agent Coordination Pattern (Jun 29, 2026):**
- **Gentech (VPS)**: 24/7 cron operations, monitoring, simple automation
- **Forge (Desktop)**: Complex coding, quality review, strategic planning  
- **Weekly Scheduling**: Jordan provides availability, Gentech distributes tasks
- **Home Hours**: 5:30 PM+ weekdays for Forge complex work
- **Context Management**: Proactive archiving at 80%/90% capacity, vault preservation
- **DeepSeek Integration**: 5M free tokens for general desktop tasks
- **Context Window**: 128K+ required for Hermes compatibility

---

## Cron Job TLC Pattern (Model Drift Fixes)

When cron jobs fail due to model configuration issues:

**1. Identify Failing Jobs:**
```bash
# List all jobs and check for errors
cronjob action=list

# Look for: last_status=error, model=null, outdated models (mimo-v2.5, opencode-go, glm-4.5-flash)
```

**2. Categorize by Task Complexity:**
- **High-frequency jobs** (daily, every 6 hours) → GLM-4.7 for cost efficiency
- **Complex jobs** (opportunity scanning, social media, GitHub contributions) → GLM-5.2 for quality
- **Script-only jobs** → No LLM needed (no_agent=true)

**3. Update Model Configuration:**
```bash
# Roll back routine jobs to GLM-4.7
cronjob action=update job_id=<job_id> model=glm-4.7 provider=zai

# Keep complex jobs on GLM-5.2
cronjob action=update job_id=<job_id> model=glm-5.2 provider=zai

# Fix null models
cronjob action=update job_id=<job_id> model=glm-4.7 provider=zai
```

**4. Remove Outdated Models:**
- Replace `glm-4.5-flash` → `glm-4.7` (model likely doesn't exist)
- Replace `glm-4.7-flash` → `glm-4.7` (outdated flash variant)
- Remove traces of `mimo-v2.5`, `opencode-go` (old providers)

## Session Learnings (Jul 1, 2026)

**Cron Job TLC Pattern:**

**Problem:** Multiple cron jobs failing due to model configuration drift after provider changes (opencode-go → zai, mimo-v2.5 → glm-4.7).

**Root Causes:**
1. Jobs with null model specifications (no model assigned)
2. Outdated/invalid models (glm-4.5-flash, glm-4.7-flash, mimo-v2.5)
3. Old provider references (opencode-go)

**User Preference Insight:**
Jordan emphasized using GLM-5.2 for **creating/configuring** cron jobs (since it's a "coding beast"), but the actual jobs should run cost-effectively on GLM-4.7 to save usage. This was a critical distinction.

**Solution Applied:**
1. **Fixed 16 failing cron jobs** by updating model configurations
2. **Strategic model distribution:**
   - GLM-5.2 (2 jobs): Social Media Engine, API Marketplace Scout (complex tasks worth premium)
   - GLM-5 (3 jobs): Sunday Review, FOMC Summary, Multi-Marketplace Scanner (premium analysis)
   - GLM-4.7 (most jobs): Routine monitoring, daily tasks, standard automation
3. **Eliminated outdated models:** Replaced all glm-4.5-flash and glm-4.7-flash with glm-4.7
4. **Fixed null model issues:** Added model specifications to jobs with missing models

**Results:**
- Fixed 5 actively failing jobs (Vault Maintenance, API Scout, Game Intelligence jobs)
- Enhanced 6 jobs with null models
- Cost optimization: Only 2 jobs on GLM-5.2, everything else on GLM-4.7
- Eliminated MIMO 2.5 and opencode-go traces

**Key Learning:**
When rebuilding/fixing cron jobs, use GLM-5.2 for the configuration work itself, but route the actual execution to the most cost-effective model that can handle the task. This optimizes both development quality and operational costs.

---

## Session Learnings (Jul 5, 2026)

**Model Drift Detection Error:**

**Problem:** Cron job fails with:
```
RuntimeError: Skipped to prevent unintended spend: global inference config drifted since this job was created (model 'glm-4.7' -> 'stepfun/step-3.7-flash:free'), and this job is unpinned.
```

**Root Cause:**
- Cron job was created with a specific model (`glm-4.7`)
- Global inference config changed (new default: `stepfun/step-3.7-flash:free`)
- Job was **unpinned** (no explicit model/provider saved)
- Hermes safety: Refused to run unpinned job on different model to prevent unintended spend

**Fix Pattern:**
1. Pin the model explicitly:
   ```bash
   cronjob action=update job_id=<job_id> provider=<provider> model=<model>
   ```
   Example: `cronjob action=update job_id=71d5c3e3b245 provider=zai model=glm-5.2`
2. Verify the fix by running the job:
   ```bash
   cronjob action=run job_id=<job_id>
   ```
3. Check status shows `last_status=ok` and `execution_success=true`

**Why This Happens:**
- When global config changes (e.g., switching providers), unpinned jobs inherit the new default
- Hermes blocks execution to avoid running on unexpected models (cost control)
- Pinning explicitly declares "this job must use THIS model"

**When to Pin Models:**
- All cron jobs should pin their model/provider explicitly
- Jobs created during a session with a specific global config should be pinned before that config changes
- Complex jobs (GLM-5.2) must be pinned to ensure they always run on the intended model
- Cost-sensitive jobs should be pinned to avoid accidental upgrades

**Example Fix:**
- Job: `5-Star Opportunity Scanner` (job_id: `71d5c3e3b245`)
- Original: `glm-4.7` (unpinned)
- Fixed: `provider: zai, model: glm-5.2` (explicitly pinned)
- Result: Job runs successfully, no more drift errors

**Verification:**
```bash
# Check job is pinned
cronjob action=list | grep "<job_id>"

# Should show:
# model: glm-5.2
# provider: zai
# base_url: null  (null means pinned, not inheriting global config)
```

**Related to:** Rate limit escalation pattern (different issue — that's about hitting provider limits, not config drift)

**First Created:** June 28, 2026
**Last Updated:** July 1, 2026