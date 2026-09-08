# Vision Analyzer Workaround — ClawRouter Direct Proxy Call

When `vision_analyze` is broken (e.g., UTF-8 decode errors from misconfigured `auxiliary.vision`), call the ClawRouter proxy directly via `execute_code` as a session-hotfix.

## Prerequisites
- ClawRouter proxy running on localhost:8402 (systemd: `clawrouter-proxy.service`)
- Image must be accessible from the VPS filesystem

## Recipe

```python
import base64, json, urllib.request

# Load the image
with open("/path/to/image.jpg", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode("ascii")

# Build the vision request
body = json.dumps({
    "model": "blockrun/auto",
    "max_tokens": 400,
    "messages": [{
        "role": "user",
        "content": [
            {"type": "text", "text": "DESCRIBE_THIS_IMAGE_PROMPT"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
        ]
    }]
}).encode("utf-8")

# Call the proxy
req = urllib.request.Request(
    "http://127.0.0.1:8402/v1/chat/completions",
    data=body,
    headers={"Content-Type": "application/json"}
)
resp = urllib.request.urlopen(req, timeout=120)
data = json.loads(resp.read().decode("utf-8"))

# Print the vision result
print(f"Model used: {data.get('model')}")
print(data["choices"][0]["message"]["content"])
```

## Why This Works
- ClawRouter's `blockrun/auto` model correctly routes to vision-capable models (observed: `google/gemini-2.5-flash`, `moonshot/kimi-k2.7`)
- The base64-encoded image in OpenAI-compatible chat format is processed correctly by the proxy
- The issue is ONLY in Hermes' internal `vision_analyze` tool path when configured with `clawrouter` provider — the proxy itself handles vision fine

## When to Use
- `vision_analyze` is stuck on a broken provider (returns UTF-8 decode errors consistently)
- You need to analyze an image mid-session and cannot restart the agent
- The proper config fix (`auxiliary.vision.provider: nous` + `model: google/gemini-3.6-flash`) is pending

## Related
- `hermes-auxiliary-config` skill — permanent vision config fix
- `hermes-agent` skill — auxiliary vision configuration docs