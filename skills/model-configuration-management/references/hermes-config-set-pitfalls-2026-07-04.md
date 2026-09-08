# Hermes `hermes config set` CLI Pitfalls

**Date:** 2026-07-04  
**Context:** Attempted to add provider fields to Hermes config using CLI commands, but commands added entries at root level instead of within the `providers:` section.

---

## The Problem

Using `hermes config set` to add nested provider fields creates root-level entries instead of properly nesting them within the `providers:` section.

### What We Tried

```bash
hermes config set zai.base_url "https://open.bigmodel.cn/api/paas/v4/"
hermes config set zai.type "openai_compatible"
hermes config set nvidia.api_key "\${NVIDIA_API_KEY}"
hermes config set nvidia.base_url "https://integrate.api.nvidia.com/v1"
hermes config set nvidia.type "openai_compatible"
```

### What Happened

The CLI added entries at the **bottom of the file** (lines 765-798) as root-level entries:

```yaml
# Lines 12-13 (providers section - BROKEN)
  zai:
    api_key: ${ZAI_API_KEY}
# Missing base_url and type!

# Lines 765-798 (root level - DUPLICATE)
zai:
  api_key: 301c64ba77334ff396e48ecd313201f1.Tg3XUkaookgzPDKe
  base_url: https://open.bigmodel.cn/api/paas/v4/
  type: openai_compatible

nvidia:
  api_key: ${NVIDIA_API_KEY}
  base_url: https://integrate.api.nvidia.com/v1
  type: openai_compatible
```

---

## Why This Fails

Hermes config structure requires nested provider entries within the `providers:` block:

```yaml
model: glm-4.7-flash
providers:
  nous:
    base_url: https://api.nousresearch.com
    type: oauth
  opencode-go:
    api_key: ${OPENCODE_GO_API_KEY}
    base_url: https://api.opencode.com
    type: openai_compatible
  zai:                     # ← Provider entries go HERE
    api_key: ${ZAI_API_KEY}
    base_url: https://open.bigmodel.cn/api/paas/v4/
    type: openai_compatible
  nvidia:                  # ← NOT at root level
    api_key: ${NVIDIA_API_KEY}
    base_url: https://integrate.api.nvidia.com/v1
    type: openai_compatible
fallback_providers:
  - provider: opencode-go
    model: deepseek-v4-flash
```

The `hermes config set` CLI command does NOT support nested key paths like `providers.zai.base_url`. It treats `zai.base_url` as a root-level key, creating a duplicate `zai:` block at the end of the file.

---

## The Fix: Manual Edit Required

Hermes blocks `patch` tool from editing config files for security reasons:

```
Refusing to write to Hermes config file: /root/.hermes/profiles/gentech/config.yaml
Agent cannot modify security-sensitive configuration. Edit ~/.hermes/config.yaml directly or use 'hermes config' instead.
```

**Manual steps required:**

1. Open `~/.hermes/profiles/gentech/config.yaml`
2. Find the broken `zai:` entry (line 12-13)
3. Add missing fields:
```yaml
  zai:
    api_key: ${ZAI_API_KEY}
    base_url: https://open.bigmodel.cn/api/paas/v4/
    type: openai_compatible
  nvidia:
    api_key: ${NVIDIA_API_KEY}
    base_url: https://integrate.api.nvidia.com/v1
    type: openai_compatible
```
4. Delete duplicate entries at bottom (lines 765-798)
5. Save and restart Hermes

---

## When to Use `hermes config set`

✅ **Works for:**
- Simple top-level keys: `model`, `max_live_sessions`
- Single-value config changes

❌ **Does NOT work for:**
- Nested provider fields
- Adding new providers to `providers:` section
- Complex nested structures

---

## Alternative: `hermes config edit`

Try `hermes config edit` to open the config file in an editor:

```bash
hermes config edit
```

This opens the file in `$EDITOR` and allows proper manual editing.

---

## Detection Pattern

To check if this problem exists:

```bash
# Search for duplicate provider blocks
grep -n "^  zai:" ~/.hermes/profiles/gentech/config.yaml
grep -n "^zai:" ~/.hermes/profiles/gentech/config.yaml

# If both return results, you have duplicates
```

---

## Related Skills

- `hermes-agent` — Hermes Agent configuration and troubleshooting
- `env-key-propagation` — API key management across profiles

---

## Session Context

**Date:** 2026-07-04  
**Task:** Add NVIDIA GLM-5.2 provider and fix broken Z.AI provider  
**Blocker:** CLI cannot add nested provider entries  
**Resolution:** Manual edit required by user  
**Affected:** `zai` provider (incomplete), `nvidia` provider (duplicate at root)