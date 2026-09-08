# Session: Vision Configuration Troubleshooting

**Date**: July 5, 2026  
**Issue**: vision_analyze repeatedly failing with "model unknown" error  
**Root Cause**: Three conflicting configuration layers

## Error Pattern

```
User: run hermes skills check
[Aux config check shows 1 update available]
User: also fix the auxiliary model
[vision_analyze called]
User: it says model unknown
User: still not working find a model using nours research sub
User: Lol still not working
User: still getting an error, can we get a audit and fix with glm 5.2
```

## Debugging Path

### Attempt 1: Manual sed deletion (failed)
- Tried to delete auxiliary.vision section with sed
- Created broken YAML structure (config went from 803 lines to 410 lines)
- Missing lines created gaps in the file

### Attempt 2: hermes config set (partial success)
- Used `hermes config set auxiliary.vision.provider zai`
- Used `hermes config set auxiliary.vision.model glm-4.7`
- Created duplicate zai provider definitions

### Attempt 3: YAML Python audit (discovered the real problem)
```python
import yaml

with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Found:
# 1. auxiliary.vision was correctly set
# 2. BUT root-level vision_provider and vision_model existed (DEPRECATED)
# 3. AND zai was defined in BOTH providers section AND root level (DUPLICATE)
```

### Attempt 4: Systematic fix (success)
1. Removed root-level vision overrides (lines 764-767)
2. Removed duplicate zai at root level
3. Fixed zai provider base_url in providers section
4. Updated auxiliary.vision.model to glm-5.2
5. Updated auxiliary.vision.timeout to 180s

## Key Learnings

### 1. The Three-Layer Conflict Problem

Hermes auxiliary configuration has THREE potential config locations:

**Layer 1 - Auxiliary Section (CORRECT)**:
```yaml
auxiliary:
  vision:
    provider: zai
    model: glm-5.2
```

**Layer 2 - Root-Level Overrides (DEPRECATED, CAUSES CONFLICTS)**:
```yaml
vision_provider: zai        # ❌ OLD, BAD
vision_model: glm-5.2       # ❌ OLD, BAD
```

**Layer 3 - Provider Duplicates (BREAKS PROVIDER RESOLUTION)**:
```yaml
# In providers section (correct):
providers:
  zai:
    api_key: ${ZAI_API_KEY}

# At root level (duplicate, wrong):
zai:
  api_key: ${ZAI_API_KEY}   # ❌ DUPLICATE
```

**Why it breaks**: Hermes looks for providers in `providers:` section. Finding `zai:` at root level confuses the provider resolution logic.

### 2. sed/patch Is Dangerous for YAML Changes

YAML is whitespace-sensitive. Deleting lines with sed can:
- Create indentation gaps
- Break parent-child relationships
- Leave orphaned sections

**When sed is safe**:
- Single-line replacements where you're 100% sure of format
- Removing entire clearly-delimited sections

**When to use Python YAML**:
- Structural changes (moving sections)
- Multi-field updates
- Removing duplicates
- Any change where structure matters

### 3. grep Alone Misses Context

Running `grep "vision" config.yaml` found 125 matches but didn't show:
- Which were correct (auxiliary.vision)
- Which were wrong (root-level vision_provider, vision_model)
- Structural relationships

**Better approach**: Use Python YAML to load and inspect the structure.

### 4. hermes config set Can Create Duplicates

`hermes config set` blindly adds keys. If a key already exists (even in wrong location), it creates duplicates.

**Example**: After running `hermes config set auxiliary.vision.model glm-5.2`:
- auxiliary.vision.model was correctly set to glm-5.2
- BUT root-level vision_model still existed from before
- Confusion: which one wins? (auxiliary section wins, but root-level pollutes namespace)

## Verification Pattern

After ANY auxiliary config change, run:

1. **Config check**:
```bash
hermes config check
```

2. **Python audit**:
```python
import yaml

config = yaml.safe_load(open("/root/.hermes/profiles/gentech/config.yaml"))
vision = config.get('auxiliary', {}).get('vision', {})
print(f"Provider: {vision.get('provider')}")
print(f"Model: {vision.get('model')}")
```

3. **Check for conflicts**:
```python
# Root-level overrides
overrides = [k for k in config if 'vision_provider' in k or 'vision_model' in k]
print(f"Root-level overrides: {overrides}")

# Duplicate providers
duplicates = [k for k in config if k in ['nous', 'zai', 'opencode-go'] and 'providers' in config and k in config['providers']]
print(f"Duplicate providers: {duplicates}")
```

## Correct Vision Config for Gentech

```yaml
auxiliary:
  vision:
    provider: zai
    model: glm-5.2
    base_url: ''
    api_key: ''
    timeout: 180
    download_timeout: 30
    max_concurrency: 8

providers:
  zai:
    api_key: ${ZAI_API_KEY}
    base_url: https://open.bigmodel.cn/api/paas/v4/
    type: openai_compatible
```

## Related Tool Output

From this session's config audit:
```
=== AUXILIARY SECTION AUDIT ===
vision:
  provider: zai
  model: glm-5.2
  base_url: ''
  api_key: ''
  timeout: 180
  download_timeout: 30

=== ROOT-LEVEL OVERRIDES ===
vision_provider: opencode-go
vision_model: deepseek-v4-flash

=== PROVIDER DUPLICATES ===
DUPLICATE: zai exists at both root level and providers section
```

This was the smoking gun - all three conflict patterns present.