# Hermes Provider Configuration

## Config File Locations

| Config Type | Path |
|-------------|------|
| Main config | `~/.hermes/config.yaml` |
| Profile-specific | `~/.hermes/profiles/gentech/config.yaml` |
| Environment/secrets | `~/.hermes/profiles/gentech/.env` |

**Note:** Profile-specific config overrides main config for that profile.

## Adding Custom Providers

### Ollama (Local)

```yaml
providers:
  ollama:
    base_url: http://localhost:11434/v1
    default_model: qwen2.5-coder:7b
    discover_models: false
    models:
      - qwen2.5-coder:7b
    name: Ollama Local
    transport: openai_chat
```

### OpenCode Go

```yaml
providers:
  opencode-go:
    default_model: glm-5.2
    discover_models: false
    models:
      - mimo-v2.5
      - glm-5.2
      - qwen3.6-plus
    name: OpenCode Go
    transport: openai_chat
```

### Custom OpenAI-Compatible

```yaml
custom_providers:
  - api_key: YOUR_API_KEY
    base_url: https://your-api.com/v1
    model: model-name
    name: Custom Provider Name
```

## Setting Model on Cron Jobs

### Via cronjob tool

```python
# Set model + provider
cronjob(
    action="update",
    job_id="JOB_ID",
    model={"model": "model-name", "provider": "provider-name"}
)

# For script-only jobs (no LLM needed)
cronjob(
    action="update",
    job_id="JOB_ID",
    no_agent=True
)
```

### Via CLI

```bash
hermes cron edit <job_id> --model <model> --provider <provider>
```

## Provider Name Format

| Provider Type | Format | Example |
|---------------|--------|---------|
| Built-in (Z.AI) | `zai` | `zai` |
| Built-in (Google) | `google` | `google` |
| Custom (OpenAI-compatible) | `custom:<name>` | `custom:Token-plan-sgp.xiaomimimo.com` |
| Ollama | `ollama` | `ollama` |

**Common mistake:** Using `custom:XiaomiMega` when actual name is `custom:Token-plan-sgp.xiaomimimo.com`

**Always verify first:**
```bash
grep -A3 "custom_providers" ~/.hermes/profiles/gentech/config.yaml
```

## Checking Provider Status

```bash
# List all providers
hermes config show

# Check Ollama is running
curl http://localhost:11434/api/tags

# Test Ollama model
echo "Say hi" | ollama run qwen2.5-coder:7b
```

## Troubleshooting

### "Unknown provider" error
- Check provider name matches config exactly
- Verify provider is in `providers:` or `custom_providers:` section
- Run `hermes config show` to see active providers

### Ollama not responding
- Check service: `systemctl status ollama`
- Restart: `systemctl restart ollama`
- Verify: `curl http://localhost:11434/api/tags`

### Model not found
- Check model name matches exactly
- For Ollama: `ollama list` to see installed models
- For Z.AI: Check model is in supported list
