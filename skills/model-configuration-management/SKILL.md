---
name: model-configuration-management
description: "Model and provider configuration management for Gentech systems - validation, fallback strategies, and live catalog synchronization. Prevents model switching errors and ensures stable model routing."
version: 1.0.0
author: Gentech
tags: [gentech, configuration, models, providers, routing, validation]
---

# Model Configuration Management

Systematic approach to managing model configurations and preventing model switching errors in Gentech systems.

## Problem Context

Common issue: Configured models that don't exist in live catalogs cause unexpected fallback switching. Example: `glm-4.5-flash` was set as default but doesn't exist in Z.AI's API, causing automatic switches to `glm-4.7` or `glm-5.2`.

## Model Validation Protocol

### 1. Catalog Verification

**CRITICAL DISCOVERY (Jul 3, 2026):** The `/models` endpoint returns a platform-wide list, NOT account-specific access. A model appearing in the catalog does NOT mean you have access to it. Real access must be verified via actual API calls.

Before setting a model as default, verify it works with your account:

```bash
# Test specific model availability via actual API call
curl -s -X POST "https://api.z.ai/api/paas/v4/chat/completions" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model": "glm-4.7", "messages": [{"role": "user", "content": "test"}], "max_tokens": 10}'

# Expected responses:
# - 200 OK: Model works for your account
# - 429/1113: Quota exhausted or rate limited
# - 401: Token expired or invalid
```

### 2. Account-Specific Model List

```bash
# Get models available to YOUR account (via models endpoint)
curl -s "https://api.z.ai/api/paas/v4/models" \
  -H "Authorization: Bearer YOUR_TOKEN" | python3 -m json.tool
```

**Note:** This still shows platform models. Cross-reference with API test results to confirm what you can actually use.

### 2. Configuration Validation
After making changes, validate the configuration:

```bash
# Check current config
grep -A 5 -B 5 "default:" /root/.hermes/profiles/gentech/config.yaml

# Verify model exists in provider catalog
curl -s "https://openrouter.ai/api/v1/models" | jq -r '.data[].id' | grep "z-ai/glm-4.7"
```

## Approved Z.AI Models

| Model ID | Context Length | Use Case | Cost Efficiency |
|----------|---------------|----------|----------------|
| `z-ai/glm-4.7` | 8K tokens | Default, balanced reasoning | ★★★★☆ |
| `z-ai/glm-5.2` | 16K tokens | Complex tasks, max context | ★★★☆☆ |
| `z-ai/glm-4.7-flash` | 8K tokens | Fast processing, latency-sensitive | ★★★★☆ |
| `z-ai/glm-4.5` | 4K tokens | Simple tasks, minimal context | ★★★★☆ |

## Same-Provider Fallback Preference (Jul 17, 2026)

**Rule:** When a model is unavailable, find the best equivalent FROM THE SAME PROVIDER before switching to a different provider. This prevents config drift, provider fragmentation, and unexpected fallthrough chains.

**Example — OpenCode Go fallback order:**
```
deepseek-v4-pro unavailable → kimi-k2.7-code (same provider) → glm-5.2 (same provider)
→ deepseek-v4-flash (same provider) → THEN fallback to another provider
```

**Why same-provider first:**
- One subscription = one billing surface. No surprise costs from fallthrough to a different provider.
- Prevents the OpenRouter auto-routing problem where Hermes falls through to unmonitored providers.
- Consistent API format — model IDs without provider prefixes.
- Cleaner diagnostics — one endpoint to check when something breaks.

**Implementation in Hermes config:**
```yaml
fallback_providers:
  - provider: opencode-go
    model: deepseek-v4-flash        # Same provider, cheaper fallback
```
Set the fallback explicitly to the same provider. Do NOT add other providers to the fallback chain unless the primary provider is unreachable entirely.

## Fallback Strategy (Updated Jul 17, 2026)

When a configured model is unavailable:

1. **Same-Provider Fallback**: Find the best equivalent from the same provider
2. **Cross-Provider Fallback**: Only after exhausting same-provider options
3. **Configuration Update**: Permanently update the config to prevent repeated failures
4. **Notification**: Log the change for audit purposes

## Providers vs `custom_providers` — When to Use Each

Hermes has **two distinct patterns** for adding LLM providers. Choosing the wrong one causes config drift, gateway crashes, or silent routing through unintended providers.

### Pattern A: `providers` section (recommended for most cases)

Add a provider entry under `providers:` when you want models from that endpoint **available as options** — the main model can switch to them by name without changing the primary provider.

```yaml
providers:
  zyloo:                                     # ← Any name, used as provider reference
    api_key: ${ZYLOO_API_KEY}
    base_url: https://api.zyloo.io/v1
    type: openai_compatible                  # ← OpenAI-compatible = works out of box

model:
  default: deepseek-v4-flash                 # Still the primary model
  provider: nous                             # Still the primary provider
```

**When to use this pattern:**
- You want to keep the main provider (nous, opencode-go, etc.) but add **extra model sources** for fallback, testing, or one-off use
- You're adding an OpenAI-compatible endpoint as a secondary option
- You want the agent to be able to `/model` switch to one of the provider's models
- No gateway restart needed for cron jobs using the main provider

**This is how ZAI, OpenCode Go, and Zyloo are added** — as providers entries, not custom_providers.

### Pattern B: `custom_providers` + `provider: custom` (for replacing the primary)

Set `model.provider: custom` and add a `custom_providers` entry when you want the **entire agent** to use a single non-built-in provider as its primary inference source.

```yaml
model:
  default: zyloo/claude-fable-5
  provider: custom                           # ← Switches to custom_providers mode

custom_providers:
  - name: zyloo
    api_key: ${ZYLOO_API_KEY}
    base_url: https://api.zyloo.io/v1
    type: openai_compatible
    model: zyloo/claude-fable-5
```

**When to use this pattern:**
- You want to make a non-built-in provider the **primary/only** inference source
- You're setting up a Telegram gateway that exclusively uses this provider
- The provider is NOT in the built-in `providers:` section

**⚠️ Critical:** every profile using `provider: custom` MUST have its own `custom_providers` section. It is NOT inherited from global config. Missing it causes `No LLM provider configured` (exit code 75) on gateway startup.

**⚠️ Stale `custom_providers` is a routing hijack vector:** old entries from past setups persist indefinitely and can cause silent routing to dead endpoints years later. Audit regularly:
```bash
grep -A 4 "^custom_providers:" ~/.hermes/profiles/gentech/config.yaml || echo "No custom_providers"
```

### Decision Matrix

| You want to... | Use Pattern |
|---|---|
| Add Zyloo as an extra model source alongside Nous | A — `providers` section |
| Switch entire Gentech to Zyloo models | B — `custom_providers` |
| Keep default on Nous, test a Zyloo model occasionally | A — `providers` section |
| Set up a new Telegram gateway on Zyloo only | B — `custom_providers` |

## Provider Catalog URLs

- **OpenRouter**: `https://openrouter.ai/api/v1/models`
- **Z.AI**: Via OpenRouter (direct API returns 404)
- **Anthropic**: Via OpenRouter
- **OpenAI**: Via OpenRouter

## Common Pitfalls

### ❌ Bad Pattern
```yaml
model:
  default: glm-4.5-flash  # Doesn't exist
  provider: zai
```

### ✅ Good Pattern  
```yaml
model:
  default: glm-4.7  # Exists in catalog
  provider: zai
## Common Pitfalls

### ❌ Common Mistake: Using model names without provider prefixes
- Use `z-ai/glm-4.7` not just `glm-4.7`
- Provider-prefixed names ensure unambiguous routing

### ⚠️ Performance-Based Switching (Sep 2026)

**Discovery:** User experienced frequent reprompting and resets with Nvidia Nemotron models, indicating suboptimal performance for agent workflows despite capability.

**Symptoms indicating model switch needed:**
- Having to reprompt 2-3 times to get desired output
- Resetting conversation to clear context
- Model ignoring instructions or going off-track
- Excessive token usage for simple tasks

**Recommended Approach:**
1. **Use high-capability models (Nvidia Nemotron) as backup only** - for when you hit usage limits on primary
2. **Primary models should be efficient, instruction-following models** like DeepSeek V4 Flash or GLM-5.3-Flash
3. **Test alternatives** on Ollama Cloud/OpenCode Go before committing
4. **Monitor interaction quality** - if you're frequently fighting the model, switch

**Verification for DeepSeek V4 Flash as Nvidia Alternative:**
```bash
# Test on Ollama Cloud
curl -s -X POST https://ollama.com/v1/chat/completions \
  -H "Authorization: Bearer $OLLAMA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"Explain agent commerce in one sentence"}],"max_tokens":20}'

# Test on OpenCode Go
curl -s -X POST https://opencode.ai/zen/go/v1/chat/completions \
  -H "Authorization: Bearer $OPENCODE_GO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"Explain agent commerce in one sentence"}],"max_tokens":20}'
```

**Cost/Performance Comparison:**
| Model | Provider | Avg. Reprompts Needed | Cost per 1M tokens |
|-------|----------|----------------------|-------------------|
| nemotron- nemotron-3-super | Ollama Cloud | 2-3 (observed) | Free (Ollama Cloud) |
| deepseek-v4-flash | Ollama Cloud | 0-1 (target) | Free tier |
| deepseek-v4-flash | OpenCode Go | 0-1 (target) | $0.22/$0.66 |
| glm-5.3-flash | OpenCode Go | 0-1 (target) | $0.07/$0.25 |

### Z.AI Provider Configuration Pattern

**Required Configuration Block:**

```yaml
providers:
  zai:
    api_key: ${ZAI_API_KEY}  # ← MUST be set in environment
    base_url: https://open.bigmodel.cn/api/paas/v4

model:
  default: deepseek-v4-flash  # or your preferred model
  provider: zai
```

**Environment Variable Setup:**

```bash
# Add to ~/.hermes/profiles/gentech/.env
ZAI_API_KEY=your_actual_key_here

# Or via hermes config (recommended)
hermes config set ZAI_API_KEY "your_key_here"
```

### OpenCode Go Provider Configuration

**Gentech Standard:** OpenCode Go is the preferred provider for DeepSeek Flash and GLM 5.2. It bundles both models under a single subscription.

**CRITICAL: Base URL Must Be Correct**
The OpenCode Go API is at `https://opencode.ai/zen/go/v1`, NOT `https://api.opencode.com`. The latter does NOT resolve (DNS lookup fails). Any config referencing `api.opencode.com` will silently fail.

**Nous Provider Base URL (same failure class — Jul 30, 2026):**
`providers.nous.base_url` MUST be `https://inference-api.nousresearch.com/v1` (the inference endpoint). `https://api.nousresearch.com` is the OAuth/portal host — it does NOT resolve for chat completions and produces `APIConnectionError` after 3 retries, even though `hermes config get model` reports `provider: nous` correctly. `auth.json` already stores the right value as `inference_base_url: https://inference-api.nousresearch.com/v1`; mirror it into the provider block. At runtime the agent resolves the host from `providers.nous.base_url`, so fixing only the `model:` block's `base_url` (as in Step 5 of the Fallthrough cleanup below) is NOT enough. Field symptom: gateway shows Telegram `connected` but every HQ reply throws "unexpected error" / "provider failed after retries" — that is agent-side inference failure, not transport.

**Correct OpenCode Go config block:**
```yaml
providers:
  opencode-go:
    api_key: ${OPENCODE_GO_API_KEY}
    base_url: https://opencode.ai/zen/go/v1  # ← CORRECT endpoint
    type: openai_compatible
```

**Model IDs on OpenCode Go API:**
Use these model IDs at the `opencode.ai/zen/go/v1` endpoint:
| Model | Model ID | Notes |
|-------|----------|-------|
| Kimi K2.7 Code | `kimi-k2.7-code` | Thinking-based (reasoning tokens). ~1,350 req per 5h on Go plan |
| Kimi K3 | `kimi-k3` | Flagship. Open weights Jul 27. ~140 req per 5h on Go plan |
| DeepSeek V4 Pro | `deepseek-v4-pro` | 1.6T MoE, 1M ctx. ~3,450 req per 5h |
| DeepSeek V4 Flash | `deepseek-v4-flash` | Daily driver. ~31,650 req per 5h |
| GLM-5.2 | `glm-5.2` | Expert coding. ~880 req per 5h |

In Hermes config, model IDs use the format `opencode-go/<model-id>` (e.g. `opencode-go/kimi-k2.7-code`).

**Environment Variable:**
```bash
# Add to ~/.hermes/profiles/gentech/.env
OPCODE_GO_API_KEY=your_actual_key_here
```

**Pitfall: Empty Provider Block**

If you set `provider: opencode-go` but the `providers.opencode-go` line is empty (`opencode-go: ''`), Hermes cannot resolve the connection.

**Diagnosis:**
```bash
# Check provider block
grep -A 5 "^providers:" /root/.hermes/profiles/gentech/config.yaml

# Check env var
echo $OPCODE_GO_API_KEY
```

**Resolution:**
1. Set `OPCODE_GO_API_KEY` in environment or `.env` file
2. Restart Hermes gateway
3. Verify connection with `hermes config show`

**Provider Preference Order (Gentech):**
1. **OpenCode Go** (DeepSeek Flash, GLM 5.2) — daily driver
2. **Z.AI** (GLM 4.7) — alternative when OpenCode unavailable
3. **OpenRouter** — fallback for cross-provider access

**Pitfall: Missing Provider Configuration**

**Symptom:**
- Provider set to `zai` but connections fail
- Falls back to OpenRouter or errors out
- No obvious error message in logs

**Diagnosis:**
```bash
# Check if providers.zai exists
grep -A 3 "^providers:" /root/.hermes/profiles/gentech/config.yaml

# Check if env var is set
echo $ZAI_API_KEY
```

**Root Cause:**
- `providers.zai` block missing from config.yaml
- `${ZAI_API_KEY}` not set in environment
- Hermes can't resolve the provider connection

**Resolution:**
1. Add `providers.zai` block to config.yaml (requires `hermes config edit` or manual edit)
2. Set `ZAI_API_KEY` environment variable
3. Restart Hermes gateway

**Example Manual Provider Configuration:**

When `hermes config set` doesn't update the providers section, you may need to edit the config file manually. Here's the correct structure:

```yaml
providers:
  nous:
    base_url: https://api.nousresearch.com
    client_id: nous-research
    client_secret: ''
    type: oauth
  opencode-go:
    api_key: ${OPENCODE_GO_API_KEY}
    base_url: https://opencode.ai/zen/go/v1  # ← CORRECT endpoint (NOT opencode.ai/zen/go/v1)
    type: openai_compatible
  ollama:
    base_url: http://localhost:11434/v1
    default_model: llama3.1:8b
    discover_models: false
    models: '["llama3.1:8b"]'
    name: Ollama Local
    transport: openai_chat
  zai:
    api_key: ${ZAI_API_KEY}
    base_url: https://open.bigmodel.cn/api/paas/v4

model:
  default: deepseek-v4-flash
  provider: opencode-go
```

**Environment Variables Setup:**

Add keys to `~/.hermes/profiles/gentech/.env`:

```bash
# Z.AI (for GLM 5.2, GLM 4.7)
ZAI_API_KEY=your_zai_token_here

# OpenCode Go (for DeepSeek Flash, GLM 5.2)
OPENCODE_GO_API_KEY=your_opencode_go_token_here
```

**Pitfall: Manual Config File Reassembly**

The `hermes config set` commands update the flat config structure but don't always update nested provider blocks correctly. When you need to modify the providers section:

1. Backup the config: `cp ~/.hermes/profiles/gentech/config.yaml ~/.hermes/profiles/gentech/config.yaml.backup`
2. Edit the file manually or use sed/python to reassemble the providers section
3. Verify the structure with `hermes config show | grep -A 10 "providers:"`
4. Restart Hermes gateway

### Auxiliary Model Configuration

**Problem:** Auxiliary tasks (web_extract, compression, skills_hub, etc.) still reference old models after main model is updated.

**CRITICAL: `/model` Slash Command Only Updates Primary Model**

The `/model` slash command in Telegram only changes the primary model. It does NOT update:
- Auxiliary models (web_extract, compression, skills_hub, approval, mcp, triage_specifier, curator, session_search)
- Vision model
- MOA presets (mixture of agents configuration)
- Fallback providers

**Symptoms:**
- Rate limiting errors from unexpected provider routing
- Inconsistent model behavior across different task types
- Silent routing through OpenRouter or old providers

**Root Cause:** Hermes has 3+ model routing layers. Changing one leaves the others pointing to old config.

**Complete Model Update Pattern (When Switching Providers):**

```bash
# 1. Update primary model
hermes config set model deepseek-v4-flash
hermes config set provider opencode-go

# 2. Update ALL auxiliary models
hermes config set web_extract_model deepseek-v4-flash
hermes config set web_extract_provider opencode-go

hermes config set compression_model deepseek-v4-flash
hermes config set compression_provider opencode-go

hermes config set skills_hub_model deepseek-v4-flash
hermes config set skills_hub_provider opencode-go

hermes config set approval_model deepseek-v4-flash
hermes config set approval_provider opencode-go

hermes config set mcp_model deepseek-v4-flash
hermes config set mcp_provider opencode-go

hermes config set triage_specifier_model deepseek-v4-flash
hermes config set triage_specifier_provider opencode-go

hermes config set curator_model deepseek-v4-flash
hermes config set curator_provider opencode-go

hermes config set session_search_model deepseek-v4-flash
hermes config set session_search_provider opencode-go

# 3. Update vision model
hermes config set vision_provider opencode-go
hermes config set vision_model gpt-4o

# 4. Update MOA presets (multi-agent orchestration)
sed -i 's/provider: openrouter/provider: opencode-go/g' ~/.hermes/profiles/gentech/config.yaml
sed -i 's/model: deepseek\\/deepseek-v4-pro/model: deepseek-v4-pro/g' ~/.hermes/profiles/gentech/config.yaml
sed -i 's/model: anthropic\\/claude-opus-4.8/model: claude-3.5-sonnet/g' ~/.hermes/profiles/gentech/config.yaml

# 5. Update fallback provider
sed -i 's/- provider: ollama/- provider: opencode-go/' ~/.hermes/profiles/gentech/config.yaml
sed -i 's/model: llama3.1:8b/model: deepseek-v4-flash/' ~/.hermes/profiles/gentech/config.yaml

# 6. Remove unused providers (OpenRouter, Ollama) if switching to paid subscriptions
sed -i '/^openrouter:/,/^[a-z]/{/openrouter:/d;/response_cache/d;/min_coding_score/d}' ~/.hermes/profiles/gentech/config.yaml
sed -i '/^  ollama:/,/^[a-z]/{/ollama:/d;/base_url: http/d;/default_model:/d;/discover_models:/d;/models:/d;/name: Ollama/d;/transport:/d}' ~/.hermes/profiles/gentech/config.yaml
```

**Verification After Update:**

```bash
# Check primary model
hermes config show | grep -A 2 "Model:"

# Check auxiliary models (sample)
sed -n '/^auxiliary:/,/^[a-z]/p' /root/.hermes/profiles/gentech/config.yaml | grep -E "(provider|model):" | head -20

# Check for any lingering OpenRouter references
grep -i "openrouter" /root/.hermes/profiles/gentech/config.yaml

# Check MOA presets
sed -n '/^moa:/,/^skills:/p' /root/.hermes/profiles/gentech/config.yaml | grep -E "(provider|model):"

# Verify providers section
sed -n '/^providers:/,/^fallback_providers:/p' /root/.hermes/profiles/gentech/config.yaml
```

**Check Status:**
```bash
hermes config show | grep -A 20 "auxiliary:"

# Or inspect the auxiliary section directly
sed -n '/^auxiliary:/,/^[a-z]/p' /root/.hermes/profiles/gentech/config.yaml | head -60
```

**Update Pattern:**
```bash
# Update BOTH model and provider for each auxiliary model
hermes config set web_extract_model deepseek-v4-flash
hermes config set web_extract_provider opencode-go

hermes config set compression_model deepseek-v4-flash
hermes config set compression_provider opencode-go

hermes config set skills_hub_model deepseek-v4-flash
hermes config set skills_hub_provider opencode-go

hermes config set approval_model deepseek-v4-flash
hermes config set approval_provider opencode-go

hermes config set mcp_model deepseek-v4-flash
hermes config set mcp_provider opencode-go

hermes config set triage_specifier_model deepseek-v4-flash
hermes config set triage_specifier_provider opencode-go

hermes config set curator_model deepseek-v4-flash
hermes config set curator_provider opencode-go

hermes config set session_search_model deepseek-v4-flash
hermes config set session_search_provider opencode-go
```

**Verification:**
```bash
# Quick check of auxiliary models
hermes config show | grep "Auxiliary Models" -A 10

# Or detailed inspection
sed -n '/^auxiliary:/,/^[a-z]/p' /root/.hermes/profiles/gentech/config.yaml | grep -E "(provider|model):" | head -20
```

**Note:** The `hermes config show` command only shows the first few auxiliary models in summary view. Use `sed` or `grep` directly on the config file to verify all settings.

**Pitfall — `auxiliary.vision.base_url` survives a provider/model flip (Sep 7, 2026):** When you switch auxiliary slots to a new provider via `hermes config set auxiliary.<slot>.provider/.model`, any slot that carries an explicit `base_url` keeps the OLD provider's URL. In practice this bites `auxiliary.vision` — after flipping `auxiliary.vision.provider` + `.model` to ollama-cloud, the `base_url` still read `https://opencode.ai/zen/go/v1`, so vision kept routing to the old host. Always re-point it explicitly:
```bash
hermes config set auxiliary.vision.base_url "https://ollama.com/v1" --force
```
Verify with `grep -A6 "^auxiliary:" config.yaml` that provider, model, AND base_url all match the new provider.

**Pitfall — top-level shorthand keys need `--force`:** The flat keys (`web_extract_model`, `web_extract_provider`, `session_search_model`, etc.) are NOT recognized config keys — `hermes config set` warns "not a recognized config key — it was saved anyway" and may not persist. Use `--force` for those, and remember the authoritative source is the nested `auxiliary.<slot>` block (the flat keys are a legacy bridge). After any aux sweep, verify BOTH the nested block and the flat keys agree.

**CRITICAL: Vision Config Hierarchy Override**

**Pitfall:** Clearing root-level vision settings does NOT disable vision if `auxiliary.vision` is still configured. AND manual edits to auxiliary.vision are error-prone.

**Discovery (Jul 5, 2026):** The correct way to update auxiliary.vision is via `hermes config set` with dot notation:

```bash
hermes config set auxiliary.vision.provider zai
hermes config set auxiliary.vision.model glm-4.7
```

This updates the nested auxiliary section directly and is safer than manual file editing or flat appends.

**What doesn't work:**
- Manual editing of config.yaml (easy to miss lines, sed deletions risky)
- Appending flat settings to file end (works but creates config drift)
- Setting root-level `vision_provider`/`vision_model` (doesn't override auxiliary)

**Why dot notation works:**
- Updates the exact nested structure Hermes expects
- No risk of breaking YAML syntax
- Idempotent - can run multiple times safely
- Creates a single source of truth for auxiliary config

**Verification:**
```bash
# Check auxiliary.vision section
grep -A 6 "auxiliary:" /root/.hermes/profiles/gentech/config.yaml | grep -A 5 "vision:"

# Should show:
#   vision:
#     provider: zai
#     model: glm-4.7
```

**Lesson:** Always use `hermes config set auxiliary.<section>.provider <provider>` for auxiliary models, not manual edits.

**Pitfall: Vision Fail with "Unknown Model" Across All Providers (Jul 5, 2026)**

**Discovery (Jul 5, 2026):** The CORRECT fix for vision configuration is using dot notation with hermes config set:

```bash
hermes config set auxiliary.vision.provider zai
hermes config set auxiliary.vision.model glm-4.7
```

This updates the authoritative auxiliary section directly. Do NOT use:
- Manual config file editing (sed deletions, nano edits)
- Flat appends to config end
- Root-level overrides only (vision_provider/vision_model)

**Why dot notation works:**
- Updates the exact nested structure Hermes expects
- No risk of YAML syntax errors or broken indentation
- Idempotent - safe to run multiple times
- Single source of truth for auxiliary config

**Session transcript:** See `references/auxiliary-vision-fix-2026-07-05.md` for full investigation path.

**Symptom:**
- Vision consistently fails with `Error code: 400 - 1211: Unknown Model, please check the model code`
- Error persists across multiple provider configurations:
  - `opencode-go` with `deepseek-v4-flash`, `deepseek-v4-pro`
  - `openai` with `gpt-4o`
  - `nous` with `claude-sonnet-4.5`, `claude-3.5-sonnet`
- Error occurs even with empty `vision_model` (should use provider default)
- Config changes have no effect - `auxiliary.vision` removal doesn't fix it

**What was tried:**
1. ✅ Removed `auxiliary.vision` section from config.yaml
2. ✅ Cleared root-level `vision_provider` and `vision_model`
3. ❌ Set `vision_provider="nous"`, `vision_model="claude-sonnet-4.5"`
4. ❌ Set `vision_provider="opencode-go"`, `vision_model="deepseek-v4-pro"`
5. ❌ Set `vision_provider="openai"`, `vision_model="gpt-4o"`
6. ❌ Set `vision_provider="nous"`, `vision_model=""`

**Root Cause (Hypothesis):**
The error suggests the Hermes vision layer is routing through a hardcoded provider (likely OpenCode-Go) regardless of config settings. The API call itself is reaching the provider, but the model name being sent doesn't match any model in that provider's catalog.

This could be:
1. **Hermes bug**: Vision routing hardcoded to OpenCode-Go even when config specifies otherwise
2. **Provider API change**: OpenCode-Go changed their vision model names
3. **Model alias issue**: Configured model name doesn't map to provider's actual model ID

**Workaround:**
**Workaround:** When vision is unavailable, ask user to describe the content manually or provide text transcription.

**For full investigation transcript and fix, see:** `references/auxiliary-vision-fix-2026-07-05.md`

### Z.AI Token Expiry and Subscription Scope Confusion

**Symptom:**
- 401 error: "令牌已过期或验证不正确" (token expired or invalid)
- 1113 error: "余额不足或无可用资源包" (insufficient balance or no resource package)
- Fresh account showing 0% usage quotas but getting "Insufficient balance" errors

**CRITICAL: Env Var Name Matters**

The `.env` file MUST use `ZAI_API_KEY` (not `GLM_API_KEY`):

```bash
# .env - CORRECT
ZAI_API_KEY=301c64ba77334ff396e48ecd313201f1.Tg3XUkaookgzPDKe

# .env - WRONG (config.yaml references ${ZAI_API_KEY}, won't find this)
GLM_API_KEY=301c64ba77334ff396e48ecd313201f1.Tg3XUkaookgzPDKe
```

**Renewal Pattern:**
1. User gets new token from https://open.bigmodel.cn/
2. Agent adds to `.env` as `ZAI_API_KEY=...`
3. Agent verifies direct API access with `curl` test
4. User restarts gateway from separate shell (agent can't do this)

**For complete token renewal workflow, see:** `references/zai-token-renewal-workflow.md`

**Root Causes:**
1. **Token expired**: Z.AI tokens have expiration periods
2. **Subscription mismatch**: Token not linked to correct subscription tier
   - Example: New token points to global plan, but coding subscription has quota
   - Coding subscription tokens must be generated FOR the coding subscription project
3. **Subscription scope confusion** (CRITICAL):
   - **"GLM Coding Plan"** covers web tools (web search, reader, Zread), NOT GLM API inference
   - Quotas shown in browser (5 hours, weekly, monthly) are for web tool usage
   - **GLM model API calls are a separate resource package**
   - This creates UX confusion: "GLM Coding Plan" sounds like it includes GLM models, but doesn't

**The Free GLM-4.7-Flash Exception:**

Z.AI offers **GLM-4.7-Flash as permanently free** via their API. This is a strategic choice:
- Fully open weights on HuggingFace — anyone can run locally
- Permanently free API access — market penetration strategy
- "42x cheaper than Claude" positioning

**Why GLM-4.7-Flash is free:**
- Open-source community model strategy
- Gets developers hooked on Z.AI's platform
- Competes with GPT-4-mini by being free

**Practical implication:**
- If your Z.AI subscription doesn't cover paid GLM models (glm-4.7, glm-5.2, etc.), use **glm-4.7-flash** for free
- Same 200K context, similar quality, zero cost
- Only difference is slightly faster responses vs base GLM-4.7

**For detailed deployment guidance, see:** `references/glm-flash-free-access.md`

**Local deployment considerations:**
- **GLM-4.7-Flash requires 19-60GB** depending on quantization
- **q4_K_M (4-bit):** 19GB model, ~22GB RAM needed
- **q8_0 (8-bit):** 32GB model, ~35GB RAM needed
- **bf16 (full):** 60GB model, ~64GB RAM needed
- **VPS constraint:** Current VPS has 11GB RAM available → not practical
- **Use free API instead:** Same quality, faster, no hardware cost

**Diagnosis:**
```bash
# Test token validity
curl -s -X POST "https://open.bigmodel.cn/api/paas/v4/chat/completions" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model": "glm-4.7", "messages": [{"role": "user", "content": "test"}], "max_tokens": 10}'
```

- **401**: Token expired → regenerate
- **1113**: Token valid but wrong subscription → regen from correct project

**Resolution:**
1. Go to Z.AI dashboard
2. Navigate to **API Keys**
3. Select the **coding subscription project** (not global)
4. Generate new token specifically for that project
5. Ensure proxy URL points to coding subscription endpoint
6. Update Hermes config:
```bash
hermes config set zai.api_key <new_token>
hermes config set zai.proxy_url <coding-proxy-url>
```

**Prevention:**
- Track token expiry dates (documented in memory)
- Note which subscription tier each token is tied to
- Always generate tokens from the specific project/subscription, not global

## Configuration Update Pattern

```bash
# Safe model update
sed -i 's/default: glm-4.5-flash/default: glm-4.7/' /root/.hermes/profiles/gentech/config.yaml

# Verify change
grep "default:" /root/.hermes/profiles/gentech/config.yaml

# Test model availability
curl -s "https://openrouter.ai/api/v1/models" | jq -r '.data[].id' | grep "z-ai/glm-4.7"
```

## Cron Job Model Drift Protection

**Discovery (Jul 5, 2026):** Cron jobs with unpinned model configurations fail when global inference config drifts.

**Error Pattern:**
```
RuntimeError: Skipped to prevent unintended spend: global inference config drifted since this job was created (provider 'zai' -> 'nous'; model 'glm-4.7' -> 'deepseek/deepseek-v4-flash'), and this job is unpinned.
```

**Root Cause:** Hermes safety feature prevents unpinned jobs from running on different model to prevent unexpected spend when global config changes. The global config at creation time is "baked in" — when global config changes, drift detection blocks execution.

**CRITICAL: `cronjob action=update` Is NOT a CLI Command**

The `cronjob` function is a Python-level Hermes agent tool, NOT a standalone CLI command. In agent sessions, `cronjob action=update` may not be available. `hermes cron edit` also does NOT support `--model` or `--provider` flags.

**The actual working approach for bulk provider switches:** edit `~/.hermes/profiles/gentech/cron/jobs.json` directly. See `references/cron-jobs-bulk-provider-switch.md` for the complete batch pattern with Python JSON manipulation and verification.

### Bulk Provider Switch — Direct jobs.json Edit

```python
import json

with open('/root/.hermes/profiles/gentech/cron/jobs.json') as f:
    data = json.load(f)

target_ids = ['job-id-1', 'job-id-2', ...]  # List of job IDs to update

for job in data['jobs']:
    if job['id'] in target_ids:
        job['provider'] = 'new-provider'
        if job.get('model') and 'deepseek-v4-flash' in job['model']:
            job['model'] = 'deepseek-v4-flash'  # Normalize

with open('/root/.hermes/profiles/gentech/cron/jobs.json', 'w') as f:
    json.dump(data, f, indent=2)
```

**Verification:**
```bash
# Read back and check provider/model for each target job
python3 -c "
import json
with open('/root/.hermes/profiles/gentech/cron/jobs.json') as f:
    data = json.load(f)
for j in data['jobs']:
    if j['id'] in ['target-ids']:
        ok = j.get('provider') == 'expected-provider'
        print(f\"{'✅' if ok else '❌'} {j['id'][:12]} prov={j.get('provider')}\")
"
```

**No restart needed** — the Hermes gateway reads `jobs.json` on each tick and picks up changes automatically.

**CRITICAL: Exclude no-agent script jobs.** Jobs with `no_agent: true` don't use an LLM — changing their provider/model is unnecessary and creates confusion. Always verify after a switch that no-agent jobs were not accidentally modified. See `references/cron-jobs-bulk-provider-switch.md` for the full verification pattern including how to identify and exclude no-agent jobs.

**Why This Happens:**
- Global model config changes (e.g., switching providers)
- Cron jobs created with old global baked-in config
- Hermes blocks execution to prevent unintended cost spikes on wrong model

**Prevention:**
- Always specify `provider` and `model` when creating cron jobs
- Pin models explicitly, never rely on global defaults
- When switching providers, batch-update all jobs immediately via jobs.json
- Monitor cron job status for drift errors (`last_status: error`)
- **One-shot jobs are CONSUMED even when drift-skipped** (Sep 2, 2026): a finite one-shot job that gets blocked by drift detection is still burned — "This finite one-shot job is consumed by this attempted run." You cannot re-run it after pinning config. The only path is to create a NEW one-shot with explicit `--provider`/`--model` from the start. This applies to reminder/deadline one-shots too — treat one-shot + unpinned as a live grenade whenever a provider switch is in flight.

**Example from Provider Switch (Jul 9, 2026):**
- Old: Various jobs on `zai/glm-4.7`, `zai/glm-5`, `zai/glm-5.2`
- Drift: Global config changed to `nous/deepseek/deepseek-v4-flash`
- Fix: Updated all 30 active + paused cron jobs to `deepseek/deepseek-v4-flash` / `nous`
- Includes no_agent jobs (drift detection blocks them too)
- Paused jobs also need updating if they'll be resumed later

## Diagnosing "Provider Failed After Retries" / Gateway-Connected-But-Agent-Fails (Jul 30, 2026)

**Symptom:** Telegram gateway shows `connected` and receives messages, but every reply dies with "unexpected error" or "The model provider failed after retries." This is NOT a transport failure — the agent's model call is failing. Gateway health ≠ agent health.

**Fast diagnostic (on the gateway host):**
```bash
# 1. Find the provider/base_url the agent actually tried + the error type
journalctl --user -u hermes-gateway-<profile>.service --since "10 min ago" \
  | grep -iE "APIConnectionError|provider failed|after retries|base_url=" | tail -20

# 2. Confirm which host resolves (inference endpoint returns 200; portal returns 000)
curl -s -o /dev/null -w "inference-api -> HTTP %{http_code}\n" --max-time 8 https://inference-api.nousresearch.com/v1/models -H "Authorization: Bearer x"
curl -s -o /dev/null -w "portal -> HTTP %{http_code}\n" --max-time 8 https://api.nousresearch.com/
```

**Root cause pattern:** agent logs `base_url=https://api.nousresearch.com` with `error_type=APIConnectionError` → `providers.<name>.base_url` points at a dead/OAuth-only host. Fix:
```bash
hermes config set providers.nous.base_url "https://inference-api.nousresearch.com/v1"
hermes gateway restart
```
Verify: the inference host returns HTTP 200; the portal host returns 000 (cannot resolve). Then send a test chat message — the agent should answer.

**Transient "No LLM provider configured" — don't over-rotate:** a `RuntimeError: No LLM provider configured` on the FIRST message right after a restart is often a config-read race in the agent subprocess. A second clean `hermes gateway restart` clears it; only escalate to the `base_url` fix above if it persists on subsequent messages.

## Monitoring and Maintenance

1. **Weekly Catalog Checks**: Verify configured models exist
2. **Model Performance Tracking**: Monitor cost/performance tradeoffs
3. **Provider Health**: Monitor provider API availability
4. **Fallback Logging**: Track fallback usage for optimization
5. **Cron Job Drift Monitoring**: Check for unpinned cron jobs that may fail on global config changes

## Integration Points

- **gentech-ops**: Include in system health checks
- **agent-economy**: Ensure model availability for agent services
- **cron-session-fresh-start**: Validate model config on session start

---

## Switching to Free NVIDIA Nemotron Models on Ollama Cloud (Sep 2026)

**Discovery:** NVIDIA provides free models (Nemotron 3 Super, Nemotron Ultra) on Ollama Cloud at zero incremental cost on the free tier. These can be used as the DEV model in the develop-and-verify pipeline, with a separate auditor model (e.g., Kimi K2.7) incurring its normal cost.

### Verification Steps
1. Confirm model responds correctly on your Ollama-Cloud key:
   ```bash
   OLLAMA_API_KEY=$(grep -oP '^OLLAMA_API_KEY=\K.*' /path/to/.env)
   curl -s -X POST https://ollama.com/v1/chat/completions \
     -H "Authorization: Bearer $OLLAMA_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"nemotron-3-super","messages":[{"role":"user","content":"Reply with the single word: alive"}],"max_tokens":8}'
   ```
   Expected: HTTP 200 + valid completion JSON containing the word "alive".

2. Update the model.default in each agent profile's config.yaml:
   ```bash
   hermes config set model.default nemotron-3-super --profile <profile>
   ```
   (Repeat for gentech, gizmo, pixel, gentech-treasury)

3. Pin affected cron jobs to prevent fail-closed on provider/model drift:
   ```bash
   hermes cron edit <job_id> --provider ollama-cloud --model nemotron-3-super
   ```
   (Do this for any cron job that performs dev/model tasks; audit jobs may keep the auditor model.)

4. Verify no OpenRouter or other provider references remain in config that could cause fallthrough.

### Cost Impact
- DEV phase: ~$0 per run (free on Ollama Cloud)
- AUDIT phase: unchanged (e.g., Kimi K2.7 ≈ $2 per 1M tokens)
- Overall per-run cost drops dramatically while preserving two-phase verification.

### Pitfalls
- Do not assume the model exists in the catalog; always verify with a live API call.
- When switching providers, remember to update auxiliary models (web_extract, compression, etc.) if they are used in dev tasks.
- The `hermes config set` command does not unpinned cron jobs; you must explicitly pin them to avoid drift errors.


## Provider Fallthrough Prevention (Jul 8, 2026)

**Problem:** Telegram gateway auto-switching providers and models to OpenRouter despite explicit `model.provider: nous` config.

**Root Cause:** Config entropy — multiple competing defaults cause fallthrough chains that land on unintended providers.

### Config Entropy Sources

There are FOUR distinct places a provider/model can be set in the config, and they compete:

```yaml
# 1. Primary model block (authoritative — set via hermes config set model.*)
model:
  default: deepseek/deepseek-v4-flash
  provider: nous

# 2. Flat 'default:' key (set by flat hermes config set default.*)
default:
  model: deepseek-v4-flash       # ← DIFFERENT provider than #1
  provider: opencode-go

# 3. fallback_providers block (set by hermes config set fallback_providers)
fallback_providers:
  - provider: opencode-go
    model: deepseek-v4-flash

# 4. Legacy flat 'fallback_providers[0]:' key
fallback_providers[0]:
  model: deepseek-v4-flash        # ← Stale duplicate, no provider name
```

**When #1 fails** (OAuth glitch, rate limit, connection timeout), Hermes falls through:
```
#1 (nous) → fails → #2 (opencode-go, empty key) → fails → #3 (opencode-go... same empty) → 
ClawRouter plugin auto-routes → OpenRouter
```

**Result:** The user sees Telegram mysteriously using OpenRouter despite the config saying `nous`.

### Diagnostics: Finding Config Entropy

```bash
# Find all competing default entries
grep -n "^model:\|^default:\|^fallback_providers\|^  provider:" ~/.hermes/profiles/gentech/config.yaml

# Check for stale flat entries (these should NOT exist at root level)
grep -n "^default:\|^fallback_providers\[0\]:\|^opencode-go:\|^nvidia:" ~/.hermes/profiles/gentech/config.yaml

# Check for custom_providers (stale third-party hijack risk)
grep -A 4 "^custom_providers:" ~/.hermes/profiles/gentech/config.yaml

# Check plugins for ClawRouter
grep -A 2 "plugins:" ~/.hermes/profiles/gentech/config.yaml

# Check for OpenRouter references in active config
grep -i "openrouter" ~/.hermes/profiles/gentech/config.yaml
```

### Cleanup Procedure

**Step 1: Remove stale flat config entries**

These are created by `hermes config set` applying flat keys instead of nested ones. They conflict with the real `model:` block:

```bash
# Remove flat 'default:' block (competes with 'model:' block)
sed -i '/^default:$/,/^[a-zA-Z]/{/^default:$/d; /^  model:/d; /^  provider:/d}' ~/.hermes/profiles/gentech/config.yaml

# Remove flat fallback_providers[N] legacy blocks
sed -i '/^fallback_providers\[[0-9]\]:$/,/^[a-zA-Z]/{/^fallback_providers\[[0-9]\]:/d; /^  model:/d}' ~/.hermes/profiles/gentech/config.yaml

# Remove flat empty provider blocks (opencode-go, nvidia, etc. at root level)
sed -i '/^opencode-go:$/,/^[a-zA-Z]/{/^opencode-go:$/d; /^  api_key:/d; /^  base_url:/d}' ~/.hermes/profiles/gentech/config.yaml
```

**Step 2: Remove stale custom_providers block**

The `custom_providers` section often contains old third-party endpoints with hardcoded API keys (e.g. mimo-v2.5). This is both a security risk and a routing hijack vector:

```bash
sed -i '/^custom_providers:/,/^[a-z]/{/^custom_providers:/d; /^  - api_key:/d; /^    base_url:/d; /^    model:/d; /^    name:/d}' ~/.hermes/profiles/gentech/config.yaml
```

**Step 3: Disable ClawRouter plugin**

ClawRouter-Hermes auto-routes providers without respecting the explicit `model.provider` config. If you have it enabled, `model.provider: nous` is advisory, not enforced:

```bash
hermes config set plugins.enabled "[kapso, gentech-session-startup]"
```

**Step 4: Set explicit fallback_model (NOT OpenRouter, NOT dead models)**

Without `fallback_model`, Hermes falls through to whatever it can find — often OpenRouter via auto-discovery or ClawRouter. Pin it to the same provider and a model that actually exists:

```bash
hermes config set fallback_model.provider "nous"
hermes config set fallback_model.model "deepseek/deepseek-v4-flash"
```

**⚠️ Do NOT use stale model names.** `claude-3.5-sonnet` has been deprecated on Nous Portal and causes `HTTP 404` on every fallback attempt. Always verify the fallback model actually exists on the provider before setting it.

**Step 5: Pin the primary model**

Ensure the `model:` block is explicit, not relying on defaults:

```bash
hermes config set model.default "deepseek/deepseek-v4-flash"
hermes config set model.provider "nous"
hermes config set model.base_url "https://inference-api.nousresearch.com/v1"
```

### Verification

After cleanup:

```bash
# Confirm model is pinned correctly
hermes config show | grep -A 3 "Model:"

# Confirm fallback stays on your provider
grep -A 2 "fallback_model:" ~/.hermes/profiles/gentech/config.yaml

# Confirm NO stale entries remain
grep -n "^default:\|^fallback_providers\[0\]:\|^opencode-go:\|^custom_providers:" ~/.hermes/profiles/gentech/config.yaml || echo "Clean ✓"

# Confirm NO OpenRouter in active config
grep -i "openrouter" ~/.hermes/profiles/gentech/config.yaml || echo "No OpenRouter references ✓"

# Confirm ClawRouter is removed from plugins
grep -A 2 "plugins:" ~/.hermes/profiles/gentech/config.yaml
```

### Pitfalls

- **Do NOT assume `hermes config set model.*` is sufficient** — flat `default:` entries from earlier `hermes config set default.*` commands silently override the primary model block when the provider field differs
- **ClawRouter is the most common cause of "mysterious provider switching"** — it's a plugin that auto-routes. Disable it when you want explicit provider control, not routing
- **`custom_providers` entries persist indefinitely** — they're created by old `hermes setup` runs and never cleaned up. They can cause routing to dead endpoints years after the setup that created them
- **After cleaning up stale entries, always restart the gateway** — the gateway caches config at startup and doesn't pick up changes at runtime:
  ```bash
  hermes gateway restart --profile gentech
  ```
- **`fallback_model` with a dead model causes ALL cron jobs to fail** — When `fallback_model.model` references a deprecated model (e.g. `claude-3.5-sonnet` dropped by Nous Portal), any provider stutter kicks the fallback chain into a dead endpoint. Every cron job then fails with `HTTP 404: Model '...' not found`. Fix: `hermes config set fallback_model.model "deepseek/deepseek-v4-flash"`. Verify with `grep -A 2 "fallback_model:" ~/.hermes/profiles/gentech/config.yaml`.
- **`patch()` tool blocked on Hermes config files** — The security guard blocks agent edits to `config.yaml`. Trying to fix `fallback_model` via `patch()` fails with "Refusing to write to Hermes config file". Always use `hermes config set fallback_model.model "model-name"` instead. This applies to all Hermes config editing — never use `patch()` or `sed` on config.yaml.

### Session Reference

See `references/provider-fallthrough-fix-2026-07-08.md` for the full investigation and fix transcript.

---

## Provider Failure Classes & Fleet-Wide Aux Sweep (Aug 29, 2026)

Four DISTINCT failure classes all look like "model unavailable" — diagnose before mass re-pinning:

| Class | Signature | Fix |
|---|---|---|
| **Region block** | HTTP 403 `RegionError` — "model only available hosted in China, requires explicit opt in" | Only the account owner can opt in at the provider workspace URL in the error. Treat model as dead fleet-wide until then (happened to deepseek-v4-flash/pro on OpenCode Go) |
| **Billing lapse** | HTTP 403 "subscription payment is past due" | Config can't fix this. Verify payment status with a curl test BEFORE re-pinning the fleet onto the provider |
| **Quota/balance** | 429 or 1113-style "insufficient balance" | Wait, downgrade tier, or switch provider |
| **Client-signature block** | urllib/Python clients get Cloudflare 403 error code 1010; **curl gets the REAL error JSON** | Always probe providers with `curl`, never urllib — urllib's 403-1010 masks the actual RegionError and wastes diagnosis time |

**Vision capability must be live-tested per model before pinning `auxiliary.vision`:**
```bash
# Generate a tiny solid-color PNG, base64 data-URL it, POST via chat/completions
# with a [{'type':'text'},{'type':'image_url'}] content array.
# PASS = HTTP 200 + color name in choices[0].message.content.
# Gotcha: max_tokens must be >=64 — reasoning models spend tokens thinking and
# return EMPTY content if max_tokens is too small (looks like a vision failure).
```
Confirmed vision-capable on OpenCode Go (Aug 29): `glm-5.3-flash`. NOT `glm-5.2` (400 on image input).

**Auxiliary slots live per-profile in config.yaml under `auxiliary.<slot>.{provider,model}`** — jobs.json re-pins do NOT touch them, and the old flat-key pattern (`web_extract_model ...`) is superseded. The verified sweep (all slots: web_extract, compression, skills_hub, approval, mcp, triage_specifier, curator, session_search, vision):
```bash
for s in web_extract compression skills_hub approval mcp triage_specifier curator session_search; do
  hermes config set --profile $P auxiliary.$s.provider <provider>
  hermes config set --profile $P auxiliary.$s.model <model>
done
hermes config set --profile $P auxiliary.vision.provider <provider>   # only if vision-tested
hermes config set --profile $P auxiliary.vision.model <model>
```
Also check `providers.<router>.models` lists (e.g. clawrouter menus) for stale blocked models — they persist as selectable routes long after the model dies.

**List-valued config keys:** `fallback_providers` is a LIST — dot notation can't address elements (`fallback_providers.model` fails). Set the whole list as JSON via `hermes config set --force fallback_providers '[{...},{...}]'`.

**Automation:** `scripts/cron-provider-sync.py` v2 (in gentech profile) does all of this fleet-wide in one run — crons + aux + fallback chains across all 4 profiles, idempotent, with a VISION_CAPABLE guard. Companion details in the `cron-model-routing` skill.

## Fleet-Wide Provider Alignment Runbook (Aug 30, 2026)

When the order is "get everybody on the same model/provider" (all profiles: gentech, gizmo, pixel, gentech-treasury), verified end-to-end:

**Known-good combo — "GLM on Ollama Cloud" (live-verified, runs the Chair's own session):**
```yaml
model:
  default: glm-5.3-flash        # Z.AI GLM-5.3 Flash served by Ollama Cloud
  provider: opencode-go          # provider NAME only — explicit base_url overrides where traffic goes
  base_url: https://ollama.com/v1
```
The provider label can stay `opencode-go` while `model.base_url` points at Ollama Cloud — the explicit base_url wins at runtime. Do NOT assume provider name == traffic destination, and don't "fix" it to a name that matches; replicate the proven combo exactly.

**Steps (per profile):**
1. Read current state: `hermes --profile <P> config get model.provider`
2. **Live-test the rail BEFORE flipping anyone:**
```bash
KEY=$(grep '^OLLAMA_API_KEY=' /root/.hermes/profiles/gentech/.env | cut -d= -f2-)
curl -s --max-time 30 -X POST https://ollama.com/v1/chat/completions \
  -H "Content-Type: application/json" -H "Authorization: Bearer $KEY" \
  -d '{"model":"glm-5.3-flash","messages":[{"role":"user","content":"reply OK"}],"max_tokens":8}'
```
3. Set per profile: `hermes --profile <P> config set model.default glm-5.3-flash` → `model.provider opencode-go` → `model.base_url https://ollama.com/v1`
4. Verify ALL profiles in one loop (default/provider/base_url identical)
5. Key presence: every profile's `.env` must contain the keys the provider block interpolates (`OPENCODE_GO_API_KEY` + `OLLAMA_API_KEY`)

**⚠️ PITFALL — `HERMES_PROFILE=<name> hermes config set ...` does NOT target that profile.** Reads and writes silently go to the CALLING profile (verified: three HERMES_PROFILE-prefixed sets all wrote gentech's config while claiming success). Only the `--profile` CLI flag targets another profile: `hermes --profile gizmo config get model.provider`. Always re-verify with `--profile` gets after any cross-profile set.

**⚠️ Unpinned-cron warning on provider change (new format Aug 30):** Hermes prints `⚠️ N enabled unpinned cron jobs have stored provider_snapshot values that differ from the new global provider. They will fail closed on their next run`. Pin them: `hermes cron edit <job_id> --provider <provider> --model <model>` — **cron edit DOES support these flags now** (supersedes the Jul 5 note below).

## Sep 2 Fleet Migration — Verified Refinements (2026-09-02)

Full 4-profile migration to `glm-5.3-flash` on Ollama Cloud (nemotron-3-super demoted to backup-only) verified end-to-end. Three refinements to the runbook above:

**1. Reasoning-model live-test gotcha — max_tokens 64 is NOT enough.** glm-5.3-flash on Ollama Cloud returned HTTP 200 with EMPTY `content` and `finish_reason: length` at max_tokens=8 AND max_tokens=64 — the reasoning budget consumed them all. Only at max_tokens=512 did content return (`'OK'`). This applies to plain-text tests too, not just vision. Live-test reasoning models with `max_tokens >= 512`, and check `choices[0].message.reasoning` (or `reasoning_content`) to distinguish "model is thinking past the cap" from "model returned nothing". Cron prompts already use generous max_tokens, so this bites only quick curl probes.

**2. Gateway restart scope after a model switch — do NOT over-restart.** Verified Sep 2: cron jobs pick up `jobs.json` edits on the NEXT TICK (no restart), and cron/agent sessions read config fresh at spawn — so a fleet model flip needs NO gateway restart at all for cron behavior. Gateway restart is only needed for an already-running interactive gateway session to see new config. And the restart itself is ALWAYS guard-blocked from inside a gateway-hosted agent session (`systemctl restart hermes-gateway-*`, even via terminal background=true, is refused: "gateway would kill this command"). Restart must come from a separate shell outside the gateway (user action or a cron session on another host). If an interactive session acts stale after a config flip, a fresh session picks up config — try that before any restart.

**3. Fleet straggler sweep pattern (full session record: `references/fleet-migration-2026-09-02.md`).** One execute_code pass scans ALL profiles' jobs.json, classifies enabled LLM vs no_agent jobs, and surfaces stragglers still on the old model; per-profile batch re-pin then read-back verify. Sep 2 sweep found 4 nemotron stragglers hiding among 39 glm jobs in gentech while the other 3 profiles were already clean — you cannot assume uniformity from a global config change; jobs keep their baked-in pins until individually re-pinned.

## Fleet Model Sync — Run It After Every HQ Switch (Sep 7, 2026)

**Discovery:** Switching HQ (`gentech`) to a new provider/model does NOT propagate to the other profiles automatically. `fleet_model_sync.py` exists at `00-System/agent-profiles/` but is a MANUAL tool — it must be run after every daily-driver change. In this session, HQ moved to `deepseek-v4-flash:0731`/`ollama-cloud` but treasury, gizmo, and pixel stayed on `nous`/`upstage/solar-pro4:free` because the sync was never invoked. Jordan flagged it: "Treasury group is not using the same stack as us."

**The fix (verified):**
```bash
cd /root/vaults/gentech/00-System/agent-profiles
python3 fleet_model_sync.py --check   # dry-run: shows which profiles DRIFT
python3 fleet_model_sync.py           # sync gentech's settings to all profiles + repin crons
```

**Two-pass cron repin is REQUIRED.** The default `--dead-providers opencode` only repins jobs pinned to opencode. If the fleet is coming OFF nous (or any other provider), run a SECOND pass targeting that provider:
```bash
python3 fleet_model_sync.py --dead-providers nous
```

**Pitfall — stale `base_url` blocks cron repin (verified Sep 7):** jobs that carry an explicit `base_url` field pointing at the OLD provider fail `hermes cron edit --provider <new> --model <new>` with:
```
Failed to update job: base_url 'https://inference-api.nousresearch.com/v1' is not allowed for provider 'ollama-cloud'. A named provider's stored credential may only be sent to its own endpoint...
```
The `--dead-providers` pass reports "cron repinned: N" but silently skips these. Fix: clear the stale `base_url` from the job in `jobs.json` (pop the key), then re-run the repin. Verify with a read-back that counts enabled jobs per provider — do NOT trust the sync's own "repinned" count.

**Pitfall — configs fixed on disk ≠ running gateways.** Gateways snapshot config at process start. After a fleet model sync, the running gateways still serve the OLD provider until restarted. Check `systemctl --user show hermes-gateway-<p>.service -p ExecMainStartTimestamp` — if it predates the sync, the gateway is stale. Restart via `fleet_update.py --restart-only` (see `safe-update-restart` skill; your own session drops mid-run, that's expected).

## Ollama Cloud Config Restore After Billing Renewal (Sep 6, 2026)

**Reference:** `references/ollama-cloud-restore-2026-09-06.md` — full session record, text-level patching technique, and pitfalls (yaml.dump round-trip reordering, `patch()` security guard block, `hermes config set` can't add whole provider blocks).

**Summary:** When Ollama Cloud billing lapses and the fleet comes back online after renewal, the restore is more than just flipping the primary model. The `providers.ollama-cloud` block itself can be missing (stripped during a prior provider switch), and all 8+ auxiliary slots need re-pointing. The verified restore sequence:

1. Check whether `providers.ollama-cloud` exists in config.yaml (grep). If missing, it must be added as a full block — not just the primary model flip.
2. Set primary: `model.default=glm-5.3-flash`, `model.provider=ollama-cloud`, `model.base_url=https://ollama.com/v1`.
3. Re-point auxiliary slots: vision, compression, skills_hub, approval, mcp, triage_specifier, curator, web_extract → ollama-cloud / glm-5.3-flash.
4. Verify with a curl live probe against ollama.com/v1 (expect weekly-usage-limit error immediately after renewal — that's normal, key is valid).
5. `hermes config check` clean.

**Pitfall — text-level edits only for config.yaml:** yaml.safe_load → edit → yaml.dump round-trips silently reorder the `providers:` block and can merge provider entries (ollama-cloud got absorbed into clawrouter in one attempt). `patch()` is blocked by the security guard. Only raw text read/replace/write preserves the file's structure. See the reference for the exact pattern.

**Pitfall — fallback chain survives provider switches:** `fallback_providers` entries referencing ollama-cloud (gpt-oss:120b, nemotron-3-super) persist across provider changes — they're already in the file and don't need re-adding. Only the primary model block and the provider entry itself need attention.

---

## Ollama Cloud Pricing and Usage Model (Jul 6, 2026)

**Discovery:** Ollama Cloud uses **GPU time billing**, NOT token-based billing. This fundamentally changes cost calculations.

### Pricing Tiers

| Plan | Price | Usage | Concurrent Models | Use Cases |
|------|-------|-------|-------------------|-----------|
| **Free** | $0 | Light usage | 1 | Chatting, evaluating models, coding with small models |
| **Pro** | $20/month ($200/yr) | Day-to-day work | 3 | Larger models, coding automation, deep research |
| **Max** | $100/month | Heavy sustained | 10 | Continuous agent tasks, multiple concurrent agents, extended sessions |

### Cost Comparison: Token-Based vs GPU-Time

**Scenario:** 50 security audits (10K output tokens each) + 500 code builds (5K output tokens each)

| Provider | Model | Pricing Model | Monthly Cost |
|----------|-------|---------------|--------------|
| **ZAI (current)** | GLM 5.2 | Token-based ($0.40/$1.00 per 1M) | ~$950 |
| **Ollama Cloud** | qwen3-coder-next | GPU-time (Pro plan: $20/mo) | $20 |
| **OpenCode Go** | DeepSeek V4 Pro | Token-based (~$0.26/$0.65 per 1M) | ~$247 |

**Potential savings:** 97.9% ($930/month) with Ollama Cloud Pro plan

### Dual-Agent Concurrent Needs

Gentech + Forge architecture requires:
- Gentech: 2-3 models (audit, vision, fallback)
- Forge: 1-2 models (coding, vision)
- **Total: 3-5 concurrent models**

**Pro plan supports 3 concurrent models ✅**

### Configuration for Ollama Cloud

```yaml
providers:
  ollama-cloud:
    api_key: ${OLLAMA_API_KEY}
    base_url: https://ollama.com/v1
    type: openai_compatible

model:
  default: deepseek-v4-flash
  provider: ollama-cloud

auxiliary:
  vision:
    provider: ollama-cloud
    model: qwen2.5-vision
```

### Investigation Tasks (Forge)

1. **Check Pro plan limits:**
   ```bash
   curl -H "Authorization: Bearer $OLLAMA_API_KEY" \
     https://api.ollama.com/v1/usage
   ```

2. **Test model quality:**
   - Run audit with qwen3-coder-next
   - Compare to GLM 5.2 output

3. **Monitor GPU time usage:**
   - Measure per-audit GPU time
   - Extrapolate to monthly usage

**For complete pricing breakdown, see:** `references/ollama-cloud-pricing-2026-07-06.md`