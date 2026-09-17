# Model Resolution Failures — Fleet-Wide 404 Errors

**Date:** May 4, 2026  
**Session:** Gentech Watchdog health check (cron_9ecfada01952_20260504_212035)  
**Agents affected:** YoYo, DMOB, Desmond, Gentech (all profiles using `nousresearch/trinity-large-thinking`)

---

## Error Signature

```
RuntimeError: Error code: 404 - {'status': 404, 'message': "Model 'nousresearch/trinity-large-thinking' not found. The requested model does not exist in our configuration or OpenRouter catalog."}
```

Stack trace pattern:
```
File "${INSTALL_DIR}/agent/auxiliary_client.py", line 3782, in async_call_llm
  await client.chat.completions.create(**kwargs), task)
File "${INSTALL_DIR}/venv/lib/python3.11/site-packages/openai/_base_client.py", line 1698, in request
  raise self._make_status_error_from_response(err.response) from None
openai.NotFoundError: Error code: 404
```

Secondary variant (session summarization failure):
```
WARNING [cron_<session_id>] root: Session summarization failed after 3 attempts: Error code: 404
```

---

## Fleet-Wide Impact Pattern

- All agents configured with the same invalid model identifier fail simultaneously
- Cron jobs fail at the LLM call stage; gateway remains running and Telegram-connected
- Error appears in `errors.log` with timestamp matching cron execution
- `hermes cron list` shows recent jobs with `error: RuntimeError` status
- Fallback chain exhausted (Nous OAuth → OpenRouter 404 → Ollama/OpenAI not configured)

**Detection:**

```bash
# Check for 404 model errors across all agents
for agent in yoyo dmob desmond gentech; do
  echo "=== $agent ==="
  grep -E "Model '.*' not found|nousresearch/trinity-large-thinking" \
    ${PROFILES_DIR}/$agent/logs/errors.log | tail -5
done
```

If all agents show the same 404 model error within the last hour → systemic model configuration failure.

---

## Root Causes

1. **Stale model identifier** — Model name changed or deprecated on provider side
   - Observed: `nousresearch/trinity-large-thinking` (invalid)
   - Valid Nous models on OpenRouter: `nousresearch/hermes-2-pro-llama-3-8b`
   - Global config uses `arcee-ai/trinity-large-thinking` (different provider)

2. **OPENROUTER_API_KEY not loaded per agent** — Fallback to OpenRouter fails silently because key exists globally but not in agent `.env` files

3. **Fallback providers not configured** — Ollama/OpenAI keys missing, so fallback chain terminates at 404

---

## Recovery Procedure

### Step 1 — Validate current configuration

```bash
# Check which model each agent is configured to use
for agent in yoyo dmob desmond gentech; do
  echo "=== $agent ==="
  grep -A2 '^model:' ${PROFILES_DIR}/$agent/config.yaml
done

# Verify OPENROUTER_API_KEY presence in agent environments
for agent in yoyo dmob desmond gentech; do
  echo "=== $agent ==="
  grep 'OPENROUTER_API_KEY' ${PROFILES_DIR}/$agent/.env 2>/dev/null || echo 'MISSING'
done
```

### Step 2 — Choose replacement model

**Option A:** Switch to valid OpenRouterNous model
```yaml
model:
  default: nousresearch/hermes-2-pro-llama-3-8b
  provider: openrouter  # Change provider to openrouter
```

**Option B:** Use global config's model (arcee-ai provider)
```yaml
model:
  default: arcee-ai/trinity-large-thinking
  provider: arcee-ai   # Must configure arcee-ai credentials
```

**Option C:** Enable fallback chain (ensure OPENROUTER_API_KEY present)
- Keep current config but add `OPENROUTER_API_KEY` to each agent's `.env`
- Fallback will route to `llama3.1-nemotron-70b-instruct` on OpenRouter

### Step 3 — Apply configuration changes

```bash
# Update config.yaml for each agent (example for YoYo)
cat > ${PROFILES_DIR}/yoyo/config.yaml << 'EOF'
model:
  default: nousresearch/hermes-2-pro-llama-3-8b
  provider: openrouter
fallback_providers:
  - provider: ollama
    model: llama3.1:70b
  - provider: openai
    model: gpt-4o-mini
EOF

# Ensure OPENROUTER_API_KEY in .env
echo 'OPENROUTER_API_KEY=***' >> ${PROFILES_DIR}/yoyo/.env

# Repeat for dmob, desmond, gentech
```

### Step 4 — Restart gateways

```bash
for agent in yoyo dmob desmond gentech; do
  hermes -p $agent gateway restart
done
```

### Step 5 — Validate recovery

```bash
# Check error logs for 404 patterns
grep -r "Model '.*' not found" ${PROFILES_DIR}/*/logs/errors.log

# Verify cron jobs executing
hermes cron list

# Watch for successful run confirmation
tail -f ${PROFILES_DIR}/gentech/logs/errors.log
```

Expected: No new 404 model errors; cron jobs reporting `ok` status.

---

## Provider Model Catalog Queries

**OpenRouter models:**
```bash
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  "https://openrouter.ai/api/v1/models" | jq '.data[].id' | grep nous
```

**Nous Research inference API:**
```bash
curl -H "Authorization: Bearer $NOUS_ACCESS_TOKEN" \
  "https://inference-api.nousresearch.com/v1/models"
```

---

## Prevention

- Pin model identifiers to specific versions (avoid `:latest` aliases)
- Maintain a `models.allowed` list in config to prevent accidental invalid model selection
- Schedule quarterly model catalog validation across all agents
- Ensure OPENROUTER_API_KEY is injected into agent `.env` during provisioning

---

**Related skills:** `agent-fleet-health-audit`, `hermes-auth-incident-response`  
**Incident classification:** Systemic configuration drift — model identifier invalidated across fleet
