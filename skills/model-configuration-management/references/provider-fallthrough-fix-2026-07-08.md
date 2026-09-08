# Provider Fallthrough Fix — Telegram Auto-Switching to OpenRouter

**Date:** 2026-07-08
**Context:** Telegram gateway was auto-switching providers and models to OpenRouter despite `model.provider: nous` being set in config.

---

## Symptoms

- Telegram responses would randomly switch to OpenRouter models
- CLI session showed provider as `nous` consistently
- Discrepancy between CLI and Telegram gateway routing

## Root Cause Analysis

### 1. Config Entropy — Competing Defaults

Four separate places in config.yaml were all setting provider/model, and they conflicted:

| Source | Provider | Model | Created By |
|--------|----------|-------|-----------|
| `model.default` (line 2) | nous | deepseek/deepseek-v4-flash | `hermes config set model.*` |
| `default:` (line 758) | opencode-go | deepseek-v4-flash | `hermes config set default.*` |
| `fallback_providers:` (line 19) | opencode-go | deepseek-v4-flash | Explicit block |
| `fallback_providers[0]:` (line 762) | *(none)* | deepseek-v4-flash | Stale legacy key |

**Mechanism:** When the primary `model:` block failed (Nous OAuth glitch or rate limit), Hermes fell through:
```
model (nous) → fails → default (opencode-go, empty API key) → fails → 
fallback_providers (same empty key) → ClawRouter → OpenRouter
```

### 2. ClawRouter-Hermes Plugin

The `ClawRouter-Hermes` plugin in `plugins.enabled` was auto-routing to OpenRouter when the configured provider failed. This made `model.provider: nous` advisory rather than enforced.

### 3. Stale custom_providers Block

The `custom_providers:` section contained a `mimo-v2.5` endpoint with a hardcoded API key. This was a leftover from an old `hermes setup` run months ago. It created an additional routing target Hermes could fall through to.

### 4. Empty opencode-go Provider

The flat `opencode-go:` block at line 783 had `api_key: ''` (empty). When fallback_providers tried routing through opencode-go, the empty key caused silent failure, pushing the chain further to OpenRouter.

## Fix Applied

### What Was Removed

| Entry | Why |
|-------|-----|
| `custom_providers:` (mimo-v2.5) | Stale security risk, hijack vector |
| Flat `default:` block (opencode-go) | Conflicted with `model:` block |
| `fallback_providers[0]:` | Stale legacy duplicate |
| Flat `opencode-go:` block | Empty API key, caused fallthrough |
| ClawRouter-Hermes plugin | Auto-routing bypassed explicit config |

### What Was Added

```yaml
fallback_model:
  provider: nous
  model: claude-3.5-sonnet
```

This keeps the entire fallback chain within the Nous provider instead of falling through to OpenRouter.

## Key Commands Used

```bash
# Set primary model
hermes config set model.default "deepseek/deepseek-v4-flash"
hermes config set model.provider "nous"
hermes config set model.base_url "https://inference-api.nousresearch.com/v1"

# Remove ClawRouter from plugins
hermes config set plugins.enabled "[kapso, gentech-session-startup]"

# Set fallback to stay within Nous
hermes config set fallback_model.provider "nous"
hermes config set fallback_model.model "claude-3.5-sonnet"

# Clean stale entries via sed
sed -i '/^custom_providers:/,/^[a-z]/{...}' config.yaml
sed -i '/^default:$/,/^[a-zA-Z]/{...}' config.yaml
sed -i '/^fallback_providers\[0\]:$/,/^[a-zA-Z]/{...}' config.yaml
sed -i '/^opencode-go:$/,/^[a-zA-Z]/{...}' config.yaml
```

## Verification

```bash
# Check model block
hermes config show | grep -A 3 "Model:"

# Confirm no OpenRouter in active config
grep -i "openrouter" ~/.hermes/profiles/gentech/config.yaml || echo "Clean ✓"

# Confirm no stale flat entries
grep -n "^default:\|^fallback_providers\[0\]:\|^opencode-go:\|^custom_providers:" ~/.hermes/profiles/gentech/config.yaml || echo "Clean ✓"
```

## Lessons

1. **`hermes config set` creates flat keys, not nested ones** — `hermes config set default.model x` creates a competing `default:` block at root level. Always use `hermes config set model.default x` for the primary block.
2. **Config entropy accumulates over time** — every `hermes config set` adds entries at the bottom of the file. Without periodic cleanup, stale entries silently override newer ones.
3. **ClawRouter breaks explicit provider control** — if you want `model.provider: nous` to be enforced, ClawRouter must be disabled.
4. **`custom_providers` is a dead feature** — it was used by old Hermes versions for custom endpoints but now creates stale routing targets.