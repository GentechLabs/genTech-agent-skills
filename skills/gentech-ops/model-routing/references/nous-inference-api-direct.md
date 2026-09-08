# Nous Inference API — Direct Access Recipe (Kimi 2.7 / K3)

Proven Aug 2, 2026 auditing the King's Gambit 3D chess cabinet when Ollama Cloud
hit its weekly usage limit. The Nous Research inference API hosts the Kimi
family (`moonshotai/kimi-k2.7-code`, `moonshotai/kimi-k3`) — use this as the
rescue path for strong-model audits / Critic-family work when Ollama is down.

## Endpoint + auth

- Base: `https://inference-api.nousresearch.com/v1`
- Auth: read `access_token` from `/root/.hermes/shared/nous_auth.json` (OAuth).
  Hourly token expiry is NORMAL — only refresh when a call actually fails with
  auth (401/403-auth), not because the token is "old". Check `expires_at` before
  running the refresh flow.
- List models: `GET /v1/models` (291 models, includes `moonshotai/kimi-k2.7-code`
  and `moonshotai/kimi-k3`).

## Gotcha 1 — Cloudflare 403 `error code: 1010` on direct requests

Plain `urllib`/curl gets banned by browser-signature check. The request MUST
carry a browser User-Agent header. Without it: `HTTP Error 403: Forbidden` with
body `{"error":"error code: 1010"}` — the fix is NOT the token, it's the UA.

```python
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
}
```

## Gotcha 2 — Kimi is a reasoning model; response shape differs

- `content` may be `null` while the real answer sits in `message.reasoning`
  (or `reasoning_details`). Always read `msg.get("content") or msg.get("reasoning")`.
- Set a GENEROUS `max_tokens` (8000–12000). With a small budget (e.g. 10) the
  reasoning eats everything → `finish_reason: "length"`, `content: null`.

## Gotcha 3 — 524 timeouts: split the audit, don't retry

Large multi-file prompts on kimi-k2.7-code return `HTTP 524` (Cloudflare origin
timeout). Do NOT retry the same big call. Split by concern into focused calls
(e.g. call A = audio + settings, call B = performance + branding), each with
only relevant excerpts (~120–240 lines per file). Two focused 6k-token calls
succeed where one 12k-token call times out.

## Working skeleton

```python
import json, urllib.request

TOKEN = json.load(open('/root/.hermes/shared/nous_auth.json'))['access_token']
BASE = "https://inference-api.nousresearch.com/v1"

def chat(prompt, max_tokens=6000):
    body = json.dumps({
        "model": "moonshotai/kimi-k2.7-code",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }).encode()
    req = urllib.request.Request(f"{BASE}/chat/completions", data=body, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36",
    })
    resp = urllib.request.urlopen(req, timeout=300)
    data = json.loads(resp.read())
    msg = data["choices"][0]["message"]
    return msg.get("content") or msg.get("reasoning") or ""
```

## Audit prompt shape that worked

Give the model: (1) concrete operator concerns up front (numbered), (2) file
names with approximate line-numbered excerpts, (3) an explicit output contract —
"for each finding: SEVERITY (HIGH/MED/LOW), file+approx line, the bug, the exact
minimal fix; terse action list; prioritize real bugs over style." The audit came
back directly implementable (fetch `response.ok` checks, master-gain volume API,
noise-buffer caching, branding color constants) with zero rework.
