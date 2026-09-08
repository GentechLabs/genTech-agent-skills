---
name: reasoning-model-harness
description: "Use when OpenCode Go reasoning models return empty content."
version: 1.0.0
author: gentech
category: gentech-ops
hermes:
  tags: [harness, reasoning, kimi-k3, glm-5.2, opencode-go, generation]
  trigger: "When generating large content (HTML, code, docs) via OpenCode Go reasoning models and getting empty content / finish:length"
---

# Reasoning-Model Harness — Don't Burn the Tank in Neutral

## The Problem (proven Aug 16, 2026)
Reasoning-first models (Kimi K3, GLM 5.2) on OpenCode Go spend their ENTIRE
`max_tokens` budget on `reasoning_content` before emitting any `content`.
Result: `finish_reason: "length"`, `content: ""`, 40-56K chars of reasoning,
zero output. This is a HARNESS mismatch, not a broken model.

## Symptoms
- HTTP 200, `cost: 0`, but `content` is empty
- `usage.completion_tokens` == your `max_tokens` (all burned)
- `message.reasoning_content` is huge (tens of thousands of chars)
- `finish_reason: "length"`

## Fixes (in order of reliability)

### 1. Use a code-specialized model for generation
`kimi-k2.7-code` is tuned to write code directly. But it can ALSO reason long
on big tasks — if it hangs >5 min, kill it and build manually.

### 2. Try `thinking: {type: "disabled"}`
Works reliably on SHORT queries (verified: instant reply, no reasoning burn).
On COMPLEX generation tasks the model may still reason anyway. Worth one try.

```json
{"model":"glm-5.2","messages":[...],"max_tokens":16000,"thinking":{"type":"disabled"}}
```

### 3. Build it yourself (most reliable)
For a full artifact (landing page, dashboard), don't fight the API. You have
the baseline + requirements — write the file directly. The model is for
reasoning/audit, not for one-shot large generation through this harness.

## Ollama Cloud AUDIT access (verified Sep 8 2026 — "models down" was a false alarm)
All audit models are LIVE on Ollama Cloud: `glm-5.2`, `glm-5.3-flash`, `kimi-k2.7-code`, `kimi-k3`, `gpt-oss:20b/120b` etc (19 total, verify via `/v1/models`). Two false "can't audit" symptoms:
1. **EmptyStreamError** (log: `provider=ollama-cloud ... Stream drop ... EmptyStreamError ... via=Google Frontend`, HTTP 200, empty body) is an upstream SSE hiccup, NOT a dead model — retry clears it.
2. **Reasoning models return `content:""` + `finish:"length"` on small budgets** (the harness trap below) — give AUDIT calls ≥500 tokens (1000-4000 real audits). Verified both glm-5.3-flash + kimi-k2.7-code return real content at max_tokens:500.
Workaround curl (shared OLLAMA_API_KEY, no new creds): `curl -s -X POST https://ollama.com/v1/chat/completions -H "Authorization: Bearer $KEY" -d '{"model":"glm-5.3-flash","messages":[...],"max_tokens":2000}'`.

## The Lesson (Jordan's insight)
> The model is the engine. The harness is the transmission. Same engine, wrong
> gear = burn the whole tank in neutral.

This is why harnesses are "the next big thing" — a reasoning model called wrong
is useless; the same model called right is a weapon. Match the model to the
task: reasoning models for hard problems, code models for generation, and
manual build when the harness fights you.

## Pitfalls
- Don't retry the same reasoning model with a bigger budget — it just reasons longer.
- `thinking: disabled` is not a guarantee on complex tasks.
- Check `reasoning_content` length before assuming the model is broken.
- OpenCode Go reports `cost: 0` — free, but don't waste time on it.
