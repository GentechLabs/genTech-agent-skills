# Vision Echo-Back Failure — ClawRouter out of balance (Aug 22, 2026)

## Symptom
`vision_analyze` returns the **prompt text echoed back** plus a claim like "no image was
provided" or "I cannot see any image" — even though a real image WAS passed. The response
looks like the model is hallucinating or the image was dropped.

## Root cause
`auxiliary.vision.provider: clawrouter` with `model: blockrun/auto`. The ClawRouter proxy
(`127.0.0.1:8402`) was **out of balance ($0.01)**. When the paid vision model
(`google/gemini-2.5-flash`) is out of funds, the proxy silently falls back to
`free/gpt-oss-120b` — a **text-only model**. A text-only model can't see the image, so it
echoes the prompt text back and claims no image was provided.

This is a DIFFERENT failure mode from the existing "binary encoding error" ClawRouter pitfall
(which is a response-encoding issue). This one is a **silent free-model fallback** that produces
plausible-looking but wrong output.

## How to confirm
Test the proxy directly with a real image and watch the `model` field in the response:
```python
import base64, json, urllib.request
from PIL import Image
import io
img = Image.new('RGB', (64, 64), (0, 128, 255))
buf = io.BytesIO(); img.save(buf, 'PNG')
b64 = base64.b64encode(buf.getvalue()).decode()
payload = {'model':'blockrun/auto','messages':[{'role':'user','content':[
  {'type':'text','text':'What color is this image? One word.'},
  {'type':'image_url','image_url':{'url':f'data:image/png;base64,{b64}'}}]}]}
req = urllib.request.Request('http://127.0.0.1:8402/v1/chat/completions',
  data=json.dumps(payload).encode(),
  headers={'Content-Type':'application/json','Authorization':'Bearer <CLAWROUTER_API_KEY>'})
r = json.loads(urllib.request.urlopen(req, timeout=60).read().decode())
print("model:", r['choices'][0]['message'].get('model') or r.get('model'))
print("content:", r['choices'][0]['message']['content'][:200])
```
If the response `model` is `free/gpt-oss-120b` (or any `free/...`) and the content echoes the
prompt, the proxy is out of balance and falling back to a text-only model.

## Fix
Point vision at a provider that has balance AND a real vision model. Match the main stack's
provider when possible. Verified working (Aug 22): **Ollama Cloud + `qwen3.5:397b`** — same
provider as the main model, and it correctly answered "Blue" for a blue test square.

```bash
hermes config set auxiliary.vision.provider ollama-cloud
hermes config set auxiliary.vision.model qwen3.5:397b
hermes config set auxiliary.vision.base_url "https://ollama.com/v1"
# Clear legacy root-level overrides that shadow auxiliary.vision:
hermes config set vision_provider ""
hermes config set vision_model ""
hermes config set vision.provider ""
hermes config set vision.model ""
```

Ollama Cloud needs `OLLAMA_API_KEY` in `.env` (already set on GenTech). Verify the model sees
images before trusting it:
```bash
# curl the ollama-cloud /v1/chat/completions with a base64 image + OLLAMA_API_KEY
```

## Pitfalls
- **The echo-back is a silent fallback, not a hallucination.** Don't re-analyze or re-send the
  image — the model literally can't see it. Check the proxy's balance / response `model` first.
- **`auxiliary.vision` may still carry a stale `base_url`** pointing at the broke proxy even
  after you change provider/model. Set `auxiliary.vision.base_url` explicitly to the new
  provider's endpoint.
- **Root-level `vision:`, `vision_provider:`, `vision_model:` shadow `auxiliary.vision`.** Clear
  them all (they're legacy/deprecated).
- **Config changes to `auxiliary.vision` take effect live** (no restart needed) — test
  immediately after setting.
- **`.env` is protected from the `patch` tool** — edit it via a Python script (read, replace,
  write), not patch.
