# Auxiliary Vision Fix — Jul 5, 2026

## Session Context

Skills check revealed Hermes version 258 commits behind. Applied 1 skill update (cuopt-numerical-optimization-formulation). Vision configuration was broken with "model unknown" error.

## Problem

Vision_analyze tool failing with:
```
Error code: 400 - 1211: Unknown Model, please check the model code
```

Tried multiple configurations:
- `opencode-go` with `deepseek-v4-flash` / `deepseek-v4-pro`
- `openai` with `gpt-4o`
- `nous` with `claude-sonnet-4.5` / `claude-3.5-sonnet`

All failed with same error.

## Investigation Path

1. **Removed auxiliary.vision section** (lines 191-247) via sed
   - Removed entire auxiliary block
   - Vision still failed

2. **Checked for root-level vision overrides**
   - Found duplicate `vision:` section at line 764
   - Removed lines 764-767

3. **Attempted various config changes**
   - Flat appends to config end
   - `hermes config set` commands
   - None worked

4. **Restored from backup**
   - `/root/.hermes/profiles/gentech/config.yaml.backup` existed
   - Restored to clean state

5. **Used hermes config set with dot notation**
   ```bash
   hermes config set auxiliary.vision.provider zai
   hermes config set auxiliary.vision.model glm-4.7
   ```
   - This worked correctly

## Solution

**Use `hermes config set auxiliary.<section>.<key>` for nested configuration:**

```bash
hermes config set auxiliary.vision.provider zai
hermes config set auxiliary.vision.model glm-4.7
```

This updates the exact nested structure without manual edits or risky sed operations.

## Why This Works

- Hermes config system supports dot notation for nested keys
- Updates the authoritative source (auxiliary section)
- No risk of YAML syntax errors
- Idempotent and safe to re-run

## What Doesn't Work

1. **Manual config file editing** (nano, sed, etc.)
   - Easy to miss lines or break YAML
   - sed deletions are error-prone with dynamic line numbers

2. **Flat appends to config end**
   - Creates config drift
   - Settings scattered across file
   - Hard to maintain

3. **Root-level overrides only**
   - `vision_provider` / `vision_model` don't override auxiliary
   - Auxiliary evaluated after root, takes precedence

## Verification

```bash
# Check auxiliary.vision section
grep -A 6 "auxiliary:" /root/.hermes/profiles/gentech/config.yaml | grep -A 5 "vision:"

# Expected output:
#   vision:
#     provider: zai
#     model: glm-4.7
#     base_url: ''
#     api_key: ''
#     timeout: 60
#     download_timeout: 30
```

## Related Config Sections

After the fix, auxiliary section shows:

```yaml
auxiliary:
  vision:
    provider: zai
    model: glm-4.7
    base_url: ''
    api_key: ''
    timeout: 60
    download_timeout: 30
  web_extract:
    provider: opencode-go
    model: deepseek-v4-flash
    # ... other auxiliary models
```

Note: Vision uses zai/glm-4.7 while other auxiliary models use opencode-go/deepseek-v4-flash. This is correct — vision is the only auxiliary that should differ.

## Skills Check Results

- Hermes version: v0.18.0 (258 commits behind upstream)
- Hub skills: 20 checked, 1 update applied
- Local skills: 48 active, 0 stale
- Curator: Enabled, last run 1d ago

## Key Takeaway

When updating nested configuration in Hermes, always use `hermes config set <section>.<subsection>.<key>` pattern rather than manual file editing. This is the canonical, safe way to modify auxiliary configs.