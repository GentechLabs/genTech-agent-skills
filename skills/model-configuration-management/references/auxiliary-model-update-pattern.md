# Auxiliary Model Update Pattern

## Problem

When you update the primary model (e.g., `hermes config set model deepseek-v4-flash`), the auxiliary models in the `auxiliary:` section do NOT update automatically. They remain on their old configuration.

## Symptoms

- Primary model shows `deepseek-v4-flash` via `opencode-go`
- Web extract, compression, and other aux tasks still use `glm-4.7` via `zai`
- Mixed model usage across the system
- Inconsistent performance and billing

## Quick Check

```bash
# See what Hermes thinks you have
hermes config show | grep "Auxiliary Models" -A 10

# See what's actually in the config
sed -n '/^auxiliary:/,/^[a-z]/p' /root/.hermes/profiles/gentech/config.yaml | grep -E "(provider|model):" | head -20
```

## Update Pattern

Update BOTH model AND provider for each auxiliary model:

```bash
# Web extract
hermes config set web_extract_model deepseek-v4-flash
hermes config set web_extract_provider opencode-go

# Compression
hermes config set compression_model deepseek-v4-flash
hermes config set compression_provider opencode-go

# Skills hub
hermes config set skills_hub_model deepseek-v4-flash
hermes config set skills_hub_provider opencode-go

# Approval
hermes config set approval_model deepseek-v4-flash
hermes config set approval_provider opencode-go

# MCP
hermes config set mcp_model deepseek-v4-flash
hermes config set mcp_provider opencode-go

# Triage specifier
hermes config set triage_specifier_model deepseek-v4-flash
hermes config set triage_specifier_provider opencode-go

# Curator
hermes config set curator_model deepseek-v4-flash
hermes config set curator_provider opencode-go

# Session search
hermes config set session_search_model deepseek-v4-flash
hermes config set session_search_provider opencode-go
```

## Batch Update Script

If you need to update all auxiliary models at once:

```bash
#!/bin/bash
# update-all-auxiliary-models.sh

NEW_MODEL="deepseek-v4-flash"
NEW_PROVIDER="opencode-go"

for model in web_extract compression skills_hub approval mcp triage_specifier curator session_search; do
  echo "Updating $model..."
  hermes config set ${model}_model $NEW_MODEL
  hermes config set ${model}_provider $NEW_PROVIDER
done

echo "Done. Verifying..."
sed -n '/^auxiliary:/,/^[a-z]/p' /root/.hermes/profiles/gentech/config.yaml | grep -E "(provider|model):" | head -20
```

## Verification

After updating, verify all auxiliary models are consistent:

```bash
# Check the auxiliary section structure
sed -n '/^auxiliary:/,/^[a-z]/p' /root/.hermes/profiles/gentech/config.yaml | head -60
```

Expected output should show all auxiliary models using the same provider:

```yaml
auxiliary:
  vision:
    provider: ollama          # Exception: vision uses Ollama
    model: llava:7b
    # ...
  web_extract:
    provider: opencode-go      # Should match your choice
    model: deepseek-v4-flash   # Should match your choice
  compression:
    provider: opencode-go      # Should match your choice
    model: deepseek-v4-flash   # Should match your choice
  # ... all others should be consistent
```

## Manual Config File Update

If `hermes config set` commands fail to update the auxiliary section (as seen in Jul 2026), you can manually edit the config file:

1. Find the auxiliary section start line:
```bash
grep -n "^auxiliary:" /root/.hermes/profiles/gentech/config.yaml
```

2. Find the next top-level section after auxiliary:
```bash
# Assuming auxiliary starts at line 201
sed -n '202,$p' /root/.hermes/profiles/gentech/config.yaml | grep -n "^[a-z]" | head -1
```

3. Reassemble: lines 1-N (before auxiliary) + new auxiliary block + lines M-EOF (after auxiliary)

## Auxiliary Model Reference

| Auxiliary Model | Default Use | Vision Exception |
|----------------|-------------|------------------|
| `web_extract` | Web content extraction | — |
| `compression` | Context compression | — |
| `skills_hub` | Skills catalog queries | — |
| `approval` | Approval prompts | — |
| `mcp` | MCP tool routing | — |
| `triage_specifier` | Task triage | — |
| `curator` | Skill curation | — |
| `session_search` | Session FTS5 queries | — |
| `vision` | Image understanding | Uses Ollama (`llava:7b`) |

## Key Insight

Vision is the **only** auxiliary model that should use a different provider (Ollama). All other auxiliary models should use the same provider as the primary model for consistency and billing.

## Recovery After Failed Update

If you attempted a bulk update and the config got corrupted:

1. Restore from backup: `cp ~/.hermes/profiles/gentech/config.yaml.backup ~/.hermes/profiles/gentech/config.yaml`
2. Re-run the update pattern
3. Verify with `hermes config show`

Always backup before bulk config operations:

```bash
cp ~/.hermes/profiles/gentech/config.yaml ~/.hermes/profiles/gentech/config.yaml.backup-$(date +%Y%m%d-%H%M%S)
```