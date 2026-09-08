---
name: hermes-auxiliary-config
description: "Hermes auxiliary configuration troubleshooting — vision, compression, web_extract, approval, MCP, skills_hub, triage_specifier, curator, session_search. Systematic audit and conflict resolution."
version: 1.0.0
author: Gentech Labs
tags: [hermes, config, auxiliary, vision, troubleshooting, audit]
trigger: "When auxiliary tools (vision_analyze, compression, web_extract) fail with 'model unknown' or 'provider unknown', when hermes config check shows warnings, or when setting up auxiliary models."
---

# Hermes Auxiliary Configuration Troubleshooting

Hermes auxiliary operations (vision, compression, web_extract, etc.) have a complex configuration system with multiple override layers. This skill provides systematic audit and resolution patterns for when they break.

## When to Use

- vision_analyze, web_extract, compression tools fail with "model unknown" or "provider unknown" errors
- `hermes config check` shows warnings for auxiliary operations
- Setting up new auxiliary providers or models
- After hermes updates that changed config structure
- When auxiliary tools seem to ignore config changes

## Auxiliary Tools

These tools use the `auxiliary:` config section:

1. **vision_analyze** → `auxiliary.vision`
2. **Context compression** → `auxiliary.compression`
3. **Web page extraction** → `auxiliary.web_extract`
4. **Dangerous command approval** → `auxiliary.approval`
5. **MCP server calls** → `auxiliary.mcp`
6. **Skills hub operations** → `auxiliary.skills_hub`
7. **Triage specifier** → `auxiliary.triage_specifier`
8. **Curator operations** → `auxiliary.curator`
9. **Session search** → `auxiliary.session_search`
10. **Gemini TTS audio tags** → `auxiliary.tts_audio_tags`

## Configuration Architecture (The Problem Zone)

**THREE LAYERS that can conflict**:

1. **Root-level overrides (DEPRECATED, causes conflicts)**:
   ```yaml
   vision_provider: zai           # ❌ OLD, BAD
   vision_model: glm-5.2          # ❌ OLD, BAD
   ```

2. **Auxiliary section (CORRECT)**:
   ```yaml
   auxiliary:
     vision:
       provider: zai              # ✅ CORRECT
       model: glm-5.2             # ✅ CORRECT
   ```

3. **Provider-level overrides (WRONG)**:
   ```yaml
   # This at root level is WRONG:
   zai:
     api_key: ${ZAI_API_KEY}      # ❌ WRONG HERE
     base_url: ...
   
   # Providers MUST be under providers: section:
   providers:
     zai:
       api_key: ${ZAI_API_KEY}    # ✅ CORRECT HERE
   ```

**Duplicate provider definitions** also cause issues. You might find `zai:` defined in BOTH:
- `providers.zai` (correct)
- Root-level `zai:` (duplicate, breaks things)

## Systematic Audit Workflow

### Step 1: Full Configuration Audit

Use Python (execute_code) to read and analyze the config structure. Do NOT rely on grep/sed alone.

```python
import yaml

config_path = "/root/.hermes/profiles/gentech/config.yaml"

with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Check auxiliary section
auxiliary = config.get('auxiliary', {})
print("=== AUXILIARY SECTION ===")
print(yaml.dump(auxiliary, default_flow_style=False))

# Check root-level overrides
print("\n=== ROOT-LEVEL OVERRIDES (BAD) ===")
for key in config:
    if any(x in key for x in ['vision_provider', 'vision_model', 'web_extract_provider', 'approval_provider']):
        print(f"{key}: {config[key]}")

# Check for duplicate providers
print("\n=== PROVIDER DUPLICATES CHECK ===")
providers = config.get('providers', {})
duplicate_providers = []
for name in ['nous', 'zai', 'opencode-go']:
    if name in config and name in providers:
        duplicate_providers.append(name)
        print(f"DUPLICATE: {name} exists at both root level and providers section")

if not duplicate_providers:
    print("CLEAN: No duplicate providers found")
```

### Step 2: Verify Target Tool Configuration

```python
# Example for vision
vision = config.get('auxiliary', {}).get('vision', {})

print("=== VISION CONFIG ===")
print(f"Provider: {vision.get('provider')}")
print(f"Model: {vision.get('model')}")
print(f"Base URL: {vision.get('base_url') or 'Using provider default'}")
print(f"API Key: {'Using env var' if not vision.get('api_key') else 'Hardcoded'}")

# Check provider exists
provider_name = vision.get('provider')
provider = config.get('providers', {}).get(provider_name, {})

if provider:
    print(f"\n{provider_name.upper()} PROVIDER:")
    print(f"  Base URL: {provider.get('base_url')}")
    print(f"  Type: {provider.get('type')}")
    print(f"  API Key: {'[SET]' if provider.get('api_key') else 'MISSING'}")
else:
    print(f"\nERROR: Provider '{provider_name}' not found in providers section")
```

### Step 3: Fix Conflicts

**A. Remove root-level overrides**:
```bash
# Use sed to delete the bad lines
sed -i '/^vision_provider:/d' config.yaml
sed -i '/^vision_model:/d' config.yaml
sed -i '/^web_extract_provider:/d' config.yaml
sed -i '/^approval_provider:/d' config.yaml
```

**B. Remove duplicate providers at root level**:
```python
import yaml

with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Remove root-level provider duplicates
duplicate_names = ['nous', 'zai', 'opencode-go']
for name in duplicate_names:
    if name in config and 'providers' in config and name in config['providers']:
        del config[name]
        print(f"Removed root-level duplicate: {name}")

# Write back
with open(config_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)
```

**C. Set auxiliary configuration**:
```bash
hermes config set auxiliary.vision.provider zai
hermes config set auxiliary.vision.model glm-5.2
hermes config set auxiliary.vision.timeout 180
```

### Step 4: Re-Verify

Run the audit script again to confirm all conflicts are resolved.

## Common Patterns by Tool

### Vision (vision_analyze)

**Correct config**:
```yaml
auxiliary:
  vision:
    provider: zai              # or opencode-go, nous, etc.
    model: glm-5.2             # must support vision
    base_url: ''               # empty = use provider default
    api_key: ''                # empty = use provider env var
    timeout: 180               # seconds, vision needs generous timeout
    download_timeout: 30       # seconds for HTTP download
    max_concurrency: 8         # optional, defaults to CPU count
```

**Vision-capable models**:
- GLM-5.2 (ZAI) - preferred
- GLM-4.7 (ZAI) - backup
- GPT-4o (OpenRouter/OpenAI)
- Claude Sonnet 4 (Anthropic)
- Gemini 2.5 Flash (Google)

### Web Extract (web_search, browser_navigate)

**Correct config**:
```yaml
auxiliary:
  web_extract:
    provider: opencode-go      # common choice
    model: deepseek-v4-flash   # or gemini-2.5-flash
    timeout: 360               # 6 minutes for long pages
```

### Compression (context compression)

**Correct config**:
```yaml
auxiliary:
  compression:
    provider: opencode-go
    model: deepseek-v4-flash
    timeout: 120               # 2 minutes
```

## Pitfalls

### ❌ `hermes config set` can create a duplicate under the WRONG section (Aug 2026)

**Symptom**: You run `hermes config set gateway.channel_prompts.-1002916759037 "..."` to update a Telegram group prompt, but the change lands in a DIFFERENT section than the one the gateway actually reads. The real prompt lives under `telegram.channel_prompts`, not `gateway.channel_prompts`. Result: a duplicate key appears in the wrong block, and the value the gateway reads is unchanged.

**Root cause**: `hermes config set` writes to the dotted path you give it verbatim. If you guess the section wrong (or the key exists under a different parent), it ADDS a new entry rather than replacing the existing one. It also warns `'...' is not a recognized config key — it was saved anyway` for unknown paths.

**Fix**:
1. Find the correct parent section first — don't guess. Check which top-level key owns the value:
   ```bash
   awk 'NR<=<line> && /^[a-z_]+:/{last=$0} END{print last}' config.yaml
   ```
2. Set the correct path:
   ```bash
   hermes config set 'telegram.channel_prompts.-1002916759037' 'You are in Treasury — ...'
   ```
3. Remove the stray duplicate you created:
   ```bash
   hermes config unset 'gateway.channel_prompts.-1002916759037'
   ```
4. Verify only ONE reference remains and it's in the right section:
   ```bash
   grep -n '<chat_id>' config.yaml
   ```

**Pitfall**: The config file is **protected from direct `patch`/`write_file` edits** — the agent gets `Refusing to write to Hermes config file`. You MUST use `hermes config set`/`unset` (or `hermes config`), never patch the YAML directly. And always verify the section after setting, because `hermes config set` won't tell you if you hit the wrong parent.

### ❌ Using sed/patch for complex YAML changes

YAML is whitespace-sensitive and structure matters. Use `execute_code` with `yaml.safe_load()`/`yaml.dump()` for any changes involving:
- Moving sections
- Removing duplicates
- Structural changes
- Multi-field updates

Sed/patch is ONLY safe for single-line replacements where you're certain of the exact format.

### ❌ Forgetting to check all three layers

When auxiliary tools fail, check ALL THREE:
1. `auxiliary.<tool>` section (correct place)
2. Root-level overrides (deprecated, conflicts)
3. Provider duplicates (can break provider resolution)

Missing layer #2 or #3 is the #1 cause of "model unknown" errors.

### ❌ Hardcoding API keys in auxiliary section

Do NOT do this:
```yaml
auxiliary:
  vision:
    api_key: sk-abc123...     # ❌ BAD
```

Do this instead:
```yaml
auxiliary:
  vision:
    api_key: ''               # ✅ GOOD - uses provider env var

providers:
  zai:
    api_key: ${ZAI_API_KEY}   # ✅ GOOD - centralized
```

### ❌ Not verifying with hermes config check

After ANY config change, run:
```bash
hermes config check
```

It will show:
- Missing environment variables
- Deprecation warnings
- Configuration conflicts

### ❌ Nous Portal OAuth requires interactive TTY

Nous Portal uses OAuth (`type: oauth`). The `hermes model` command that initiates or refreshes the OAuth flow **requires an interactive terminal (TTY)** and refuses to run in:
- Non-interactive subprocesses (`Error: 'hermes model' requires an interactive terminal`)
- PTY-mode tools (even Hermes' own PTY support doesn't satisfy it)
- Cron jobs or background scripts
- Pipe/redirect contexts

**Symptom**: `vision_analyze` fails with "Unknown Model" (code 1211) even when `auxiliary.vision.provider` and `model` are correctly set to Nous Portal values.

**Root cause**: The Nous OAuth token doesn't exist or expired, and there's no non-interactive way to refresh it. The model lookup fails because the API rejects unauthenticated requests.

**Fix**: Have the user run `hermes model` in their native terminal (Windows Terminal, iTerm, etc.) to complete the OAuth device-code flow. After that, vision_analyze works for the duration of the token's lifetime.

**Workaround**: Switch to an API-key-based vision provider (no OAuth needed):
```bash
# Use Z.AI
hermes config set auxiliary.vision.provider zai
hermes config set auxiliary.vision.model glm-5.2

# Or OpenCode Go (if they have a vision-capable model)
hermes config set auxiliary.vision.provider opencode-go
hermes config set auxiliary.vision.model gpt-4o
```

### ❌ Z.AI GLM-4.7 / GLM-5.2 text-only limitation (Z.AI specific)

**Symptom**: Chinese error message: `messages.content.type 参数非法，取值范围 ['text']` ("content.type parameter illegal, only 'text' allowed").

**Cause**: GLM-4.7 and GLM-5.2 on Z.AI's API do NOT support image content. The API explicitly rejects any content type other than `text`.

**Fix**: Use a different provider for vision. GLM-4.7 and GLM-5.2 are text-only on this provider.

**Note**: Z.AI may have vision-capable models (e.g., GLM-4V or GLM-5V variants). Check their model catalog for vision-supporting model IDs.

### ❌ OpenCode Go deepseek-v4-flash does not support vision

**Symptom**: `Error from provider (Console Go): Upstream request failed` — no specific model error, just upstream failure.

**Cause**: `deepseek-v4-flash` on OpenCode Go is a text-only model. It doesn't process image inputs.

**Fix**: Use a different vision provider or a vision-capable model on OpenCode Go (e.g., `gpt-4o`, `gpt-4o-mini`).

### ❌ Model name guessing on new providers

When switching vision to a new provider (e.g., Nous Portal), models like `claude-3.5-sonnet`, `hermes-3-vision` may fail with "Unknown Model" (code 1211). 

**Cause**: Model naming conventions vary by provider. A model name that works on one provider doesn't necessarily work on another, even if the provider hosts the same base model.

**Fix**: 
1. Check the provider's model list API directly:
```bash
curl -s <provider_base_url>/v1/models \
  -H "Authorization: Bearer $API_KEY" | python3 -m json.tool
```
2. For OAuth providers (Nous Portal), this may not work until OAuth is completed.
3. Ask the user which model names the provider supports.

### ❌ Assuming vision_model in providers section works

Some legacy configs had:
```yaml
providers:
  zai:
    vision_model: glm-5.2     # ❌ IGNORED
```

This field is IGNORED. Use `auxiliary.vision.model` instead.

### ❌ Using provider "auto" without understanding fallbacks

```yaml
auxiliary:
  vision:
    provider: "auto"          # Uses fallback chain
```

"auto" works, but you need to verify your fallback chain is configured:
```yaml
fallback_providers:
  - provider: opencode-go
    model: deepseek-v4-flash
```

**🚨 CRITICAL: `auto` can silently drain Nous Portal subscription credits.** When `auxiliary.*.provider: auto` is set and a Nous Portal OAuth provider is configured, auxiliary services route through Nous for every call — consuming subscription credits without any visible indicator. This was the root cause of Jordan's Nous subscription slowly draining: 9 auxiliary services (vision, web_extract, compression, skills_hub, approval, mcp, triage_specifier, curator, session_search) were all on `auto`, silently routing every auxiliary operation through Nous.

**Fix:** Pin every auxiliary service explicitly (batch command — verified Jul 15, 2026):
```bash
for service in vision web_extract compression skills_hub approval mcp triage_specifier curator session_search; do
  yes | hermes config set auxiliary.$service.provider opencode-go
  yes | hermes config set auxiliary.$service.model deepseek-v4-flash
done
```

**Verify:**
```bash
grep -A 2 "provider:" ~/.hermes/profiles/gentech/config.yaml | grep -v "auto"
# Should show NO "auto" entries under auxiliary section
```

**Pitfall:** The `hermes config set` command may produce harmless `bash: [pid: 1 (255)] tcsetattr: Inappropriate ioctl for device` errors in background processes — these are terminal-control errors, not config failures. Always verify with `grep` after setting.

### ❌ Gateway dependency without gateway server

When `browser.use_gateway = true` or `web.use_gateway = true` but NO gateway server is running, Telegram vision fails silently. The tool tries to route through a nonexistent gateway.

**Symptoms**:
- vision_analyze works in CLI but fails in Telegram
- "model unknown" or timeout errors in gateway sessions
- Config looks correct but tool still fails

**Fix**:
```python
import yaml

config_path = "~/.hermes/profiles/gentech/config.yaml"

with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Disable gateway when gateway server not running
if 'browser' in config:
    config['browser']['use_gateway'] = False

if 'web' in config:
    config['web']['use_gateway'] = False

# Write back
with open(config_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)
```

**When to enable gateway**:
- Gateway server IS running (`hermes gateway serve`)
- You want centralized tool routing
- Multi-agent setup with shared gateway

**When to disable gateway**:
- Single-agent setup (VPS, desktop)
- No gateway server running
- Direct provider access works fine

**After Hermes update, check for malformed auxiliary.vision**

Updates sometimes create auxiliary sections that override root-level config, sometimes with models that don't support the requested feature (e.g., text-only models for vision).

**Symptoms**:
- Vision ignores root-level `vision_provider`/`vision_model` settings
- Settings in auxiliary.vision persist even after clearing them
- `hermes config set` appears to work but vision still uses old provider/model
- Vision fails with "model unknown" or provider-specific errors (Chinese: `模型不存在` or `messages.content.type 参数非法，取值范围 ['text']`)
- Error explicitly states model only accepts text, not images

**Cause**:
The auxiliary section overrides root-level config and may be configured with a model that doesn't support the feature (e.g., `zai/glm-5.2` for vision when GLM-5.2 is text-only).

**Detection**:
```bash
# Check auxiliary.vision configuration
cat ~/.hermes/profiles/gentech/config.yaml | grep -A 5 "auxiliary:"

# Check current effective settings
hermes config | grep -i vision
```

If you see:
```yaml
auxiliary:
  vision:
    provider: zai
    model: glm-5.2      # ← Text-only model, doesn't support vision
```

**Proven issue** (Jul 5-6, 2026):
- Hermes was 258 commits behind upstream
- After `hermes update`, auxiliary.vision was set to `zai/glm-5.2` (text-only)
- Error: `messages.content.type 参数非法，取值范围 ['text']` (parameter illegal, only text allowed)
- Tried changing root-level `vision_provider`/`vision_model` — failed
- Tried clearing auxiliary.vision — settings persisted
- The auxiliary section was a hard override with a vision-incompatible model

**Fix - Step 1: Manually edit auxiliary.vision to use vision-capable model**:
```bash
nano ~/.hermes/profiles/gentech/config.yaml

# Find auxiliary section (typically around line 193-196)
# Change from:
auxiliary:
  vision:
    provider: zai
    model: glm-5.2        # ← Text-only, BAD for vision

# Change to:
auxiliary:
  vision:
    provider: nous
    model: claude-3.5-sonnet    # ← Vision-capable, GOOD
```

**Fix - Step 2: Alternative - Delete auxiliary section**:
If you don't use auxiliary operations, delete the entire section:
```bash
# Remove lines 193-196 (or wherever auxiliary.vision is)
# Save and exit
```

**Fix - Step 3: Verify**:
```bash
hermes config | grep -i vision

# Test with a real image
vision_analyze(image_url="path/to/image.jpg", question="What's in this image?")
```

**Prevention**:
After ANY `hermes update`, run:
```bash
cat ~/.hermes/profiles/gentech/config.yaml | grep -A 5 "auxiliary:"
```
Check that auxiliary.vision is either:
1. Empty (deleted)
2. Configured with a model that supports the requested feature
3. Not set to a text-only model for vision operations

### ❌ Mixed indentation breaking YAML structure

After manual edits or sed operations, YAML can develop mixed indentation (2-space, 4-space, tabs). This breaks parsing silently.

**Symptoms**:
- `yaml.safe_load()` succeeds but produces wrong structure
- Settings applied don't take effect
- Duplicate sections appear

**Fix - normalize entire config**:
```python
import yaml

config_path = "~/.hermes/profiles/gentech/config.yaml"

with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Write back with consistent 2-space indentation
with open(config_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False, indent=2, allow_unicode=True)
```

This normalizes the entire file with proper YAML structure.

### ❌ ClawRouter provider breaks vision — binary encoding error (Aug 2026)

**Symptom**: `vision_analyze` fails with `'utf-8' codec can't decode byte 0xb5 in position 1: invalid start byte` for EVERY image — URL, local file, data URI, all produce the same encoding error.

**Cause**: `auxiliary.vision.provider: clawrouter` with `model: blockrun/auto`. The ClawRouter proxy (v0.12.244, localhost:8402) handles text-based LLM routing and paid media generation (image/video) — it does NOT handle vision in the way Hermes' vision_analyze expects. The proxy's response encoding is binary and Hermes' vision client can't decode it.

**Fix**:
```bash
hermes config set auxiliary.vision.provider nous
hermes config set auxiliary.vision.model google/gemini-3.6-flash
```

**Working vision configs (verified Aug 8, 2026)**:
- `nous` + `google/gemini-3.6-flash` — **GENTECH DEFAULT**. This is what the config should be.
- `nous` + `anthropic/claude-sonnet-4-20250514` — ✅ PROVEN, takes effect immediately (no restart needed)
- `clawrouter` + ANY model — ❌ BROKEN (binary encoding), do NOT use for auxiliary.vision

**Key insight**: ClawRouter is for text-based LLM routing, image/video generation, and web search. Vision/auxiliary needs a real provider with vision API support (like Nous Portal's Google Gemini proxy). The proxy itself CAN handle vision (direct REST calls with base64 images work fine — `gemini-2.5-flash` returns correct results), but Hermes' vision_analyze tool path through the `clawrouter` provider produces binary encoding errors.

**⚠️ PITFALL: Mistaking the root cause.** When vision_analyze fails with the UTF-8 error, the instinct might be to switch FROM `nous` TO `clawrouter` (thinking the local proxy would be faster/better). This is the OPPOSITE of the fix. The correct provider for vision is `nous`, not `clawrouter`. ALWAYS load the `hermes-auxiliary-config` skill before diagnosing vision failures — it has the correct answer.

### ✅ Session-hotfix: direct ClawRouter proxy call when vision_analyze is stuck

When the in-session vision_analyze tool is broken (config fix pending), call the ClawRouter proxy directly via `execute_code` with base64-encoded images. Works immediately, no restart needed, uses the same proxy that handles our text/LLM routing.

```python
import base64, json, urllib.request

with open("/path/to/image.jpg", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode("ascii")

body = json.dumps({
    "model": "blockrun/auto",
    "max_tokens": 400,
    "messages": [{"role": "user", "content": [
        {"type": "text", "text": "Describe this image in detail."},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
    ]}]
}).encode("utf-8")

req = urllib.request.Request(
    "http://127.0.0.1:8402/v1/chat/completions",
    data=body,
    headers={"Content-Type": "application/json"}
)
resp = urllib.request.urlopen(req, timeout=120)
data = json.loads(resp.read().decode("utf-8"))
print(data["choices"][0]["message"]["content"])
```

**Why this works**: The ClawRouter proxy's `blockrun/auto` model correctly routes to vision-capable models (observed: `google/gemini-2.5-flash`, `moonshot/kimi-k2.7`). The base64-encoded image in the standard OpenAI chat format is processed correctly. The issue is ONLY in Hermes' internal vision_analyze tool path, not in the proxy itself.

**When to use**: 
- vision_analyze is stuck on a broken provider
- You need to analyze an image mid-session and can't restart
- Cross-reference this with the config fix — after fixing `auxiliary.vision`, vision_analyze should work again

### ❌ CRITICAL: Config changes to auxiliary.vision DO take effect live (correction Aug 2026)

**Previous version of this pitfall claimed config changes need restart.** That is WRONG for vision provider/model changes. The running Hermes process DOES hot-reload `auxiliary.vision.*` changes from `hermes config set`. Test immediately after the config change — no restart needed.

**What DOES need restart**: MCP server reconnection (parked servers), provider chain changes deeper than the auxiliary section, profile-level tool registration.

### ❌ Nous Portal tencent/hy3:free → 404 "Couldn't find that, sorry" for vision

**Symptom**: `vision_analyze` fails with `Error code: 404 - {'status': 404, 'message': "Couldn't find that, sorry."}` for EVERY input — local file, http URL, extracted video frame, all 404. `browser_vision` fails identically.

**Cause**: `auxiliary.vision` was set to `nous` + `tencent/hy3:free`. Nous Portal's vision endpoint returns 404 for this model. This is a provider-side vision backend failure, NOT an image problem.

**Fix**: Switch providers. Do NOT waste time re-extracting frames or retrying with different image paths — the 404 is provider-side.
**Working vision providers (verified GenTech)**:

- `nous` + `google/gemini-3.6-flash` — **GENTECH DEFAULT (per Jordan).** Use Nous Portal for ALL auxiliary operations. The Hermes vision tool routes through Nous Portal's internal proxy. Do NOT switch away from Nous unless the user explicitly asks. Models that work on Nous Portal for vision: `google/gemini-3.6-flash` (best), `google/gemini-3.5-flash`, `google/gemini-3-pro-image`, `moonshotai/kimi-k3`, `qwen/qwen3.7-plus`, `qwen/qwen3.7-max`, `anthropic/claude-sonnet-4-20250514` (proven Aug 2026).
- `opencode-go` + `kimi-k3` — Kimi K3 has native vision, 1M context, strong reasoning. Fallback if Nous Portal has issues.
- `gemini` + `gemini-2.5-flash` — Direct Google Gemini API. Needs `GOOGLE_API_KEY` in `.env`. Set `auxiliary.vision.base_url: https://generativelanguage.googleapis.com/v1beta/models`. Model `gemini-2.0-flash` is NOT supported — use `gemini-2.5-flash`.
- `opencode-go` + `gpt-4o` — if available on that provider.

**WRONG final choice** (text-only, will fail on restart): `opencode-go` + `deepseek-v4-flash`. deepseek-v4-flash is text-only (see existing pitfall). Never leave vision set to this.

### ❌ `provider: nous` with non-Nous base_url + direct API key causes 404 on every image

**Symptom**: `vision_analyze` fails with `Error code: 404` for EVERY image — local cached files, fresh URLs, generated FAL images. Image download succeeds externally (curl returns 200) but the Hermes vision tool returns 404 consistently.

**Root cause**: `auxiliary.vision.provider: nous` configures the provider framework with Nous OAuth (`type: oauth` in `providers.nous`). When `base_url` is overridden to a non-Nous endpoint (e.g. Google Gemini API) with a direct API key instead of an OAuth token, the image download/caching layer expects the Nous OAuth infrastructure and fails.

**Config that triggers this:**
```yaml
auxiliary:
  vision:
    provider: nous           # ← OAuth-based provider
    model: google/gemini-3.6-flash
    base_url: https://generativelanguage.googleapis.com/v1beta/models  # ← Google endpoint
    api_key: sk-...          # ← Direct API key, conflicts with OAuth
```

**Diagnosis**: the `provider` value must match the actual authentication mechanism:
- `nous` = OAuth (`type: oauth` in `providers.nous`) — no `api_key` in auxiliary.vision, uses OAuth token
- `opencode-go`, `zai`, `gemini` = API-key-based (`type: openai_compatible`) — `api_key` IS used

Mixing OAuth provider name with a direct API key + foreign endpoint breaks the image download/caching pipeline.

**Fix — Switch provider to match the endpoint's auth type:**
```bash
# Google Gemini endpoint → use provider: gemini
hermes config set auxiliary.vision.provider gemini
hermes config set auxiliary.vision.model gemini-2.5-flash
hermes config set auxiliary.vision.base_url "https://generativelanguage.googleapis.com/v1beta/models"
hermes config set auxiliary.vision.api_key "${GOOGLE_API_KEY}"
```

**Rule of thumb**: the `provider` in `auxiliary.*` must match the corresponding `providers.<name>` entry. Never set `provider: nous` with a non-Nous endpoint — the OAuth mismatch breaks image download.

### ✅ Session-hotfix: direct Gemini REST call when vision_analyze is broken

When the in-session vision tool is stuck on a broken provider (config fix pending restart), call Gemini's vision API directly. Works immediately, no restart needed.

```python
import base64, json, os, urllib.request
# Source .env first: set -a; source /root/.hermes/profiles/gentech/.env; set +a
img_b64 = base64.b64encode(open('/tmp/frame.png','rb').read()).decode()
url = (f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash'
       f':generateContent?key={os.environ["GOOGLE_API_KEY"]}')
payload = {'contents':[{'parts':[
    {'text':'Describe this image in detail.'},
    {'inline_data':{'mime_type':'image/png','data':img_b64}}
]}]}
req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                             headers={'Content-Type':'application/json'})
resp = json.loads(urllib.request.urlopen(req, timeout=60).read().decode())
print(resp['candidates'][0]['content']['parts'][0]['text'])
```

### ❌ Nous Portal agent_key returns 403 Cloudflare (error 1010)

**Symptom**: Direct API call to `https://inference-api.nousresearch.com/v1/chat/completions` with the `agent_key` JWT from `auth.json` returns HTTP 403 with `error code: 1010`. The agent_key is a JWK-format JWT, not a static API key, and is rejected by Cloudflare's direct-access gate.

**Cause**: The Nous Portal `agent_key` is designed for Hermes' internal OAuth-based routing, not for direct REST access. Hermes the tool uses a different auth path (OAuth device-code flow + session cookie) than a raw curl request with the agent_key.

**Fix**: Use `vision_analyze()` (Hermes' own tool) instead of direct API calls. The Hermes auxiliary client knows how to authenticate with Nous Portal correctly. If the tool returns 404, the model `tencent/hy3:free` doesn't support vision — switch the configured model to `google/gemini-3.6-flash` or `moonshotai/kimi-k3`.

**Workaround for current session** (when config change needs restart): Use the direct Gemini REST call above instead of trying to hit Nous Portal's API directly.

### ❌ ${GOOGLE_API_KEY} env var not resolved by vision client in fresh session

**Symptom**: You set `auxiliary.vision.api_key: ${GOOGLE_API_KEY}` but vision still fails. The running session's environment doesn't have `GOOGLE_API_KEY` exported — only the wakeup script sources `.env`, and the auxiliary client may run without it.

**Fix**: Either (a) hardcode the literal key in config (acceptable here — key already lives in `.env`), or (b) `source /root/.hermes/profiles/gentech/.env` in the terminal before the direct-API workaround. For `hermes config set auxiliary.vision.api_key`, prefer the literal key over the `${VAR}` form to avoid resolution gaps.

## Verification Steps

After fixing auxiliary config:

1. **Run config check**:
   ```bash
   hermes config check
   ```

2. **Audit with Python script** (see Step 1)
3. **Test the tool**:
   ```bash
   # Test vision with a simple image
   # (Vision will fail gracefully if config is wrong)
   ```

4. **Check logs**:
   ```bash
   tail -50 ~/.hermes/profiles/gentech/logs/*.log | grep -i "vision\|auxiliary"
   ```

## Provider Setup Reference

### ZAI (Zhipu AI) - Gentech's choice

```yaml
providers:
  zai:
    api_key: ${ZAI_API_KEY}
    base_url: https://open.bigmodel.cn/api/paas/v4/
    type: openai_compatible

# .env file:
ZAI_API_KEY=your_key_here
```

Models:
- glm-5.2 (best for vision, coding, complex tasks)
- glm-5 (good for finance, general)
- glm-4.7 (backup)
- glm-4.7-flash (fast, cheap, trivial tasks)

### OpenCode-Go

```yaml
providers:
  opencode-go:
    api_key: ${OPENCODE_GO_API_KEY}
    base_url: https://api.opencode.com
    type: openai_compatible

# .env file:
OPENCODE_GO_API_KEY=your_key_here
```

Models:
- deepseek-v4-flash (fast, cheap)
- deepseek-v4-pro (better quality)
- gpt-4o (vision)

### Nous Research

```yaml
providers:
  nous:
    base_url: https://api.nousresearch.com
    client_id: nous-research
    client_secret: ''        # Leave empty for OAuth
    type: oauth
```

Uses Nous Portal authentication via `hermes auth login nous`.

## When Configuration Is Correct But Tool Still Fails

If config looks correct but tool fails:

1. **Check environment variables**:
   ```bash
   grep ZAI_API_KEY ~/.hermes/.env
   ```

2. **Test provider directly**:
   ```bash
   curl -H "Authorization: Bearer $ZAI_API_KEY" \
     https://open.bigmodel.cn/api/paas/v4/models
   ```

3. **Check tool-specific logs**:
   ```bash
   tail -100 ~/.hermes/profiles/gentech/logs/agent.log | grep -i vision
   ```

4. **Verify model supports the feature**:
   - Not all models support vision
   - Check provider docs for model capabilities

## Related Skills

- `model-optimized-cron-config` - Model routing patterns
- `hermes-agent` - General Hermes configuration
- `preflight` - Config validation before sessions

## Session History

This skill was created from a session where vision_analyze repeatedly failed with "model unknown" despite multiple configuration attempts. The root cause was three conflicting configuration layers (root-level override, auxiliary section, duplicate provider definitions). The systematic audit pattern resolved the issue.

## Support Files

- **scripts/aux_config_audit.py** - Automated audit script with --fix capability. Usage:
  ```bash
  python3 aux_config_audit.py                    # Full audit
  python3 aux_config_audit.py --tool vision       # Audit specific tool
  python3 aux_config_audit.py --fix               # Auto-fix common issues
  ```

- **references/vision-troubleshooting-session.md** - Detailed session transcript with error patterns, debugging attempts, and successful resolution path. Use as reference when encountering similar issues.
- **references/direct-gemini-vision.py** - Session-hotfix script: calls Gemini vision API directly when vision_analyze is stuck on a broken provider (no restart needed). Usage: `source /root/.hermes/profiles/gentech/.env && python3 references/direct-gemini-vision.py <image> [question]`.