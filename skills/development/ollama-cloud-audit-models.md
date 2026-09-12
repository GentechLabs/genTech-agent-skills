# Ollama Cloud Audit Models — Access Guide (verified Sep 8 2026)

**The 1-line truth:** The audit models are NOT down and NOT removed. `glm-5.2`,
`glm-5.3`, `glm-5.3-flash`, `kimi-k2.7-code`, `kimi-k3` are ALL live on Ollama
Cloud (verified via `/v1/models` + direct API calls today). The "can't audit"
symptoms are two **call-pattern** failures, both fixable:

## Failure 1 — EmptyStreamError (the glitch that faked "models down")
Symptom in logs:
```
provider=ollama-cloud ... Stream drop on attempt 2/3 ... EmptyStreamError
(error_type=EmptyStreamError ... http_status=200 ... upstream via=Google Frontend)
```
This is an **upstream SSE hiccup** (HTTP 200, empty body, `via Google Frontend`
= some Ollama infra hop returned nothing) — NOT a dead model or bad key.
- **Fix:** retry. Hermes auto-retries (2/3, 3/3) — it usually clears. If it
  keeps failing, wait 30-60s and retry; the model is reachable.

## Failure 2 — reasoning models return empty content on a tiny token budget
Symptom: HTTP 200, `content: ""`, `finish_reason: "length"`, `completion_tokens
== your max_tokens`. This is the `reasoning-model-harness` trap: glm/kimi are
**reasoning-first** — they exhaust the whole `max_tokens` budget on
`reasoning_content` before emitting any `content`. A low cap makes them look
broken.
- **Fix A (recommended):** give audit models a REAL budget (≥500 tokens, use
  1000-4000 for real audits). Verified: with `max_tokens:500`, glm-5.3-flash
  returned `"audit passed"`; kimi-k2.7-code returned `"audit passed"`.
- **Fix B:** on short queries, `{"thinking":{"type":"disabled"}}` returns
  instantly without the reasoning burn.

## The verified working call (curl)
```bash
KEY=$(grep OLLAMA_API_KEY /root/.hermes/profiles/gentech/.env | cut -d= -f2)
curl -s -X POST "https://ollama.com/v1/chat/completions" \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"model":"glm-5.3-flash","messages":[{"role":"user","content":"<audit task>"}],"max_tokens":2000}'
```

## Currently available Ollama Cloud models (19, verified live)
`deepseek-v4-flash:0731` · `deepseek-v4-pro:0813` · `gemma4:31b` · `glm-5.1` ·
`glm-5.2` · `glm-5.3` · `glm-5.3-flash` · `gpt-oss:120b` · `gpt-oss:20b` ·
`kimi-k2.6` · `kimi-k2.7-code` · `kimi-k3` · `minimax-m2.7` · `minimax-m3` ·
`mistral-large-3:675b` · `nemotron-3-nano:30b` · `nemotron-3-super` ·
`nemotron-3-ultra` · `qwen3.5:397b`

## The AUDIT pair (per develop-and-verify skill)
| Phase | Model | Notes |
|-------|-------|-------|
| AUDIT | `glm-5.3-flash` (or `glm-5.2`) | fast audit, reasoning-first — give ≥500 tokens |
| AUDIT (deep) | `kimi-k2.7-code` | code-specialized audit — give ≥1000 tokens |
| BIG | `kimi-k3` | heavy architecture/security review — worth the tokens |

> **⚠️ Sep 12, 2026:** `glm-5.3-flash` via **Z.AI is dead** (`1113`) and **Ollama Cloud is
> weekly-capped** (429). AUDIT second-opinion now = **Kimi K2.7-code via Nous** (live). Re-check
> `/v1/models` on the live provider before assuming any glm model is reachable.

## What all 4 agents (gentech/gizmo/pixel/gentech-treasury) + Forge share
- **No new credentials needed** — all use the shared `OLLAMA_API_KEY` in each
  profile's `.env` (already present + valid, verified). Nothing to install.
- **Why treasury was blocked:** if a treasury cron called an audit model with a
  low `max_tokens` (or hit EmptyStream during a retry storm), it got
  `content:""` and logged a failure → looked like the model was gone. It
  wasn't. Give a real budget and it works.

## See also
- `reasoning-model-harness` skill — full harness-mismatch playbook ("same engine,
  wrong gear = burn the tank in neutral").
- `develop-and-verify` skill — the DEV→AUDIT pipeline that uses these models.
