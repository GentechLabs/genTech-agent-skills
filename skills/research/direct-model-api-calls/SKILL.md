---
name: direct-model-api-calls
description: "Call LLM APIs directly (Nous Research inference, other OpenAI-compatible endpoints) when the configured gateway/provider is unavailable or you need a specific model outside routing. Covers auth from nous_auth.json, Cloudflare user-agent fix, reasoning-model response parsing, timeout splitting, and token refresh."
version: 1.0.0
author: Gentech
tags: [llm-api, nous, kimi, reasoning-model, provider]
---

# Direct Model API Calls

Use when: the normal provider (Ollama Cloud, gateway routing) is down/rate-limited,
or you need a model not in the configured routing (e.g. Kimi K2.7 for audits) and the
fastest path is a direct HTTP call.

## Proven case

Aug 2, 2026: Ollama Cloud weekly limit hit mid-session (`"you have reached your
weekly usage limit"`). Kimi 2.7 (`kimi-k2.7-code`) was needed for a code audit.
Nous Research inference API (`inference-api.nousresearch.com/v1`) served it at
~$0.00004/call with no weekly wall. Route the audit model through the primary
provider first — direct calls are the fallback, not the default.

## Auth

Token lives at `/root/.hermes/shared/nous_auth.json`:
```python
import json
d = json.load(open('/root/.hermes/shared/nous_auth.json'))
TOKEN = d['access_token']
```
- Check `d['expires_at']` (ISO string, UTC) against now BEFORE calling — hourly expiry is normal.
- If expired, refresh: `POST https://auth.nousresearch.com/oauth2/token` with
  `grant_type=refresh_token`, `refresh_token=d['refresh_token']`, `client_id=d['client_id']`.
  Save the new `access_token` + recompute `expires_at` (now + `expires_in`).
- Token may be readable but the API still 403s — that's Cloudflare, next section.

## Cloudflare 403 (error code 1010) — browser-signature ban

Bare `urllib`/`curl` get blocked with `HTTP 403 error code: 1010` (Cloudflare bans the
client signature, not the auth). Fix — send a browser User-Agent header:

```python
req = urllib.request.Request(url, data=body, headers={
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36",
})
```

Diagnosis order for 403: (1) check `expires_at` — expired? refresh. (2) add browser
User-Agent — Cloudflare 1010. (3) still failing? check provider catalog for model name.

## Reasoning-model response shape (Kimi K2.7 and similar)

The answer is NOT always in `message.content`:
- Kimi is a reasoning model. With small `max_tokens`, all budget goes to reasoning
  and `content` comes back `null` — the text is in `message.reasoning`.
- Always read: `msg.get("content") or msg.get("reasoning") or ""`.
- Set `max_tokens` generously (4000-12000) or you get truncated reasoning + empty content.

## Timeouts — split, don't retry the same big prompt

- HTTP 524 = Cloudflare origin timeout. A single prompt with 12K+ chars of code +
  long reasoning blows the origin timeout (~2-5 min).
- Fix: split the audit into 2-3 smaller calls (by concern: e.g. "audio+settings",
  "performance+branding"), keep each `max_tokens` ≤ 6000.
- **Capture the first successful output to a file immediately** (`> out.txt`) —
  retries of the same big prompt tend to 524 again. First pass is gold.

## Endpoint + model list

- Base: `https://inference-api.nousresearch.com/v1` (OpenAI-compatible `/chat/completions`)
- Kimi audit model: `moonshotai/kimi-k2.7-code` (also `moonshotai/kimi-k3` exists)
- Other catalog models: deepseek, qwen3.7, gemini, claude-opus variants, tencent/hy3, etc.
- Verify catalog: `GET {base}/models` with the token (200 = auth ok).

## Checklist for a direct-API audit

1. Build the prompt: numbered operator concerns + files joined with `=== name ===` separators (trim each to ~12K chars) + "give SEVERITY, file+line, bug, exact minimal fix".
2. Call with browser UA, max_tokens ≤ 6000.
3. Read content-or-reasoning; capture output to file.
4. Split into multiple calls if prompt is large.
5. Implement the fixes, run the project's own test suite, verify.

See `references/kimi-audit-prompt-pattern.md` for the exact proven prompt shape.
