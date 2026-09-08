# Cron Job Model Routing

## Provider Stack (Updated June 27, 2026)

| Provider | Cost | Models | Strategy |
|----------|------|--------|----------|
| **Ollama (Local)** | **FREE** | qwen2.5-coder:7b | **LOCAL FIRST** — simple tasks |
| **Z.AI (zai)** | Pro plan | GLM-5.2, GLM-5, GLM-4.7, GLM-4.7-Flash | Complex tasks only |
| **Script-only** | **FREE** | None (no_agent=True) | No LLM needed |

## Job Classification Rules

| Job Type | Model | Provider | Example Jobs |
|----------|-------|----------|--------------|
| **Script-only** (no_agent=True) | None | — | CMC Watchlist, Fed Event Reminder, LP Reader, AAE Monitor |
| **Simple** (script + post-process) | qwen2.5-coder:7b | ollama | Vault Maintenance, Hub Sync, Gaming Hub Sync, Morning To-Do, Build Standup, Context Snapshot, Skills Update, Cron Health Monitor |
| **Medium** (analysis, multi-step) | glm-4.7 | zai | Daily Digest, Tradesta Signal, Revenue Monitor, GenTech Shop jobs |
| **Complex** (research, deep reasoning) | glm-5 | zai | FOMC Summary, Sunday Review, API Marketplace Scout, Multi-Marketplace Scanner |

## Adding Ollama to Hermes Config

**Config location:** `~/.hermes/profiles/gentech/config.yaml`

Add under `providers:` section:
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

## Updating Cron Jobs

```python
# Route to local Qwen (free)
cronjob(
    action="update",
    job_id="JOB_ID",
    model={"model": "qwen2.5-coder:7b", "provider": "ollama"}
)

# Route to Z.AI GLM-4.7 (complex)
cronjob(
    action="update",
    job_id="JOB_ID",
    model={"model": "glm-4.7", "provider": "zai"}
)

# Route to Z.AI GLM-5 (very complex)
cronjob(
    action="update",
    job_id="JOB_ID",
    model={"model": "glm-5", "provider": "zai"}
)
```

## Model Availability (Verified June 27, 2026)

### Ollama (Local)
- `qwen2.5-coder:7b` ✅ — 4.7GB, ~8-15 tokens/sec on CPU

### Z.AI
- `glm-5.2` ✅ — Best coding model, 1M context
- `glm-5` ✅ — Strong reasoning
- `glm-4.7` ✅ — Best value
- `glm-4.7-flash` ✅ — Free tier

## Current Cron Job Distribution (38 jobs)

- 4 script-only (no model)
- 9 simple → qwen2.5-coder:7b (Ollama Local)
- 10 medium/complex → glm-4.7/glm-5 (Z.AI)
- 15 paused (not running)

## Cost Impact

**Before (All Z.AI):** 38 jobs → ~$0.15/day → ~$4.50/month

**After (Local First):**
- 9 jobs → Local Qwen = **$0.00**
- 10 jobs → Z.AI = ~$0.05/day = ~$1.50/month
- 4 jobs → Script-only = **$0.00**
- 15 jobs → Paused = **$0.00**

**Monthly savings:** ~$3.00/month (67% reduction)

## Pitfalls

1. **Ollama must be running** — Check with `curl http://localhost:11434/api/tags`
2. **Local Qwen is CPU-only** — ~8-15 tokens/sec, fine for simple tasks, too slow for complex
3. **Config path varies** — Main config at `~/.hermes/config.yaml`, profile-specific at `~/.hermes/profiles/gentech/config.yaml`
4. **Provider name is `ollama`** — Not `ollama-local` or `local`
5. **Test before assigning** — Verify Ollama works: `echo "Say hi" | ollama run qwen2.5-coder:7b`
