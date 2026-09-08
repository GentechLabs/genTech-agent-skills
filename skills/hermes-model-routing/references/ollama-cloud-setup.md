# Ollama Cloud — Subscription API

**Base URL:** `https://ollama.com/v1` (OpenAI-compatible)
**Auth:** `Authorization: Bearer <api_key>`
**Format:** Key is `<id>.<secret>` — pass as Bearer token.

## Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/chat/completions` | POST | Chat completions (OAI-compatible) |
| `/v1/models` | GET | List available models |

## Available Models (Jul 2026 subscription)

- `deepseek-v4-flash` — current daily driver ✓
- `deepseek-v4-pro`
- `glm-5.1`, `glm-5.2`
- `kimi-k2.5`, `kimi-k2.6`, `kimi-k2.7-code`
- `nemotron-3-ultra`, `nemotron-3-super`, `nemotron-3-nano:30b`
- `minimax-m2.5`, `minimax-m3`, `minimax-m2.7`
- `gpt-oss:20b`, `gpt-oss:120b`
- `mistral-large-3:675b`
- `qwen3.5:397b`
- `gemma4:31b`

## Auth Note

- `api.ollama.com` returns 403 (error code 1010) for chat — use `ollama.com` base URL instead.
- Models listing works on `api.ollama.com/v1/models` with Bearer auth.
- Chat completions only work on `ollama.com/v1/chat/completions`.

## curl Example

```bash
curl -s https://ollama.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OLLAMA_CLOUD_KEY" \
  -d '{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"hello"}],"stream":false}'
```
