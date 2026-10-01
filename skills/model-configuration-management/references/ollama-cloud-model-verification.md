# Ollama Cloud Model Verification

Reusable probe for verifying which models on your Ollama Cloud subscription actually respond with usable content.

## Core rule

The catalog endpoint (`https://ollama.com/v1/models`) lists every model on the platform. Your subscription plan may include only a subset. The only reliable verification is a real `POST /v1/chat/completions` probe against each candidate model.

## The small-`max_tokens` trap

Reasoning models (`glm-5.3-flash`, `glm-5.2`, `kimi-k3`, the `nemotron-3-*` family) emit a `reasoning` or `reasoning_content` field before `content`. If `max_tokens` is too small, the budget is consumed by reasoning and `content` is empty with `finish_reason: length`. This looks like a broken model but is a broken test. Use `max_tokens >= 512` for probes.

## Script: verify every catalog model for a profile

```python
#!/usr/bin/env python3
"""Verify every model in your Ollama Cloud catalog actually returns usable content.
No values are printed; only model names and response status."""
import json, os, urllib.request, urllib.error

PROFILE_DIR = os.path.expanduser("~/.hermes/profiles/gentech")

def load_key():
    with open(f"{PROFILE_DIR}/.env") as f:
        for line in f:
            if line.lstrip().startswith("#"):
                continue
            if line.startswith("OLLAMA_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("OLLAMA_API_KEY not found")

def post(model, key):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": "Reply exactly: OK"}],
        "max_tokens": 512,
    }).encode()
    req = urllib.request.Request(
        "https://ollama.com/v1/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            d = json.loads(r.read().decode())
            c = (d.get("choices") or [{}])[0].get("message", {})
            content = c.get("content", "").strip()
            reasoning = bool(c.get("reasoning") or c.get("reasoning_content"))
            return (r.status, content[:40], reasoning)
    except urllib.error.HTTPError as e:
        return (e.code, e.read().decode()[:80].replace("\n", " "), False)
    except Exception as e:
        return (f"ERR:{type(e).__name__}", str(e)[:80], False)

def catalog(key):
    req = urllib.request.Request(
        "https://ollama.com/v1/models",
        headers={"Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read().decode())
        return [m["id"] for m in d.get("data", [])]

if __name__ == "__main__":
    key = load_key()
    models = catalog(key)
    print(f"catalog: {len(models)} models")
    for m in models:
        status, content, reasoning = post(m, key)
        ok = status == 200 and content
        print(f"{'OK ' if ok else 'FAIL'} {m:40} status={status} content={content!r} reasoning={reasoning}")
```

## Interpreting results

| Status | Content | Meaning | Action |
|---|---|---|---|
| 200 | non-empty | Model works and emits content | Candidate for use |
| 200 | empty | Reasoning consumed the budget or the model really returned nothing | Re-test with `max_tokens >= 512` and inspect `reasoning` |
| 429 | — | Weekly subscription exhausted | Not a model problem — wait for reset or route elsewhere |
| 401 | — | Key invalid or missing | Check `.env` key |
| 403/Cloudflare 1010 | — | WAF block (rare for Ollama; common for OpenCode Go) | Test with `curl` from the host; do not trust urllib's first error |

## Error code 1010 is a Cloudflare bot-block, not a quota

If an OpenAI-compatible endpoint returns `HTTP 403 error code: 1010` (especially on OpenCode Go), that is Cloudflare's bot management — it is NOT a usage limit. `curl` from the host may reveal the real provider error, and a browser session may work even when urllib is blocked. Do not conclude "plan exhausted" from a 1010 alone.
