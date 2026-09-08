# Nous Portal Vision Models (Verified Jul 30, 2026)

Full model list from Nous Portal API:

```
google/gemini-3.6-flash          ✅ Best choice for vision
google/gemini-3.5-flash          ✅ Good
google/gemini-3.5-flash-lite     ✅ Fast, cheaper
google/gemini-3.1-flash-lite     ✅ Fast, cheaper
google/gemini-3-pro-image        ✅ Image specialized
google/gemini-3-flash-preview    ✅ Preview model
moonshotai/kimi-k3               ✅ 1M context, vision + reasoning
moonshotai/kimi-k2.7-code        ✅ Code + vision
qwen/qwen3.7-plus                ✅ Vision capable
qwen/qwen3.7-max                 ✅ Vision capable
qwen/qwen3.7-flash               ✅ Fast vision
qwen/qwen3.5-plus-20260420       ✅ Vision capable
qwen/qwen3.6-flash               ✅ Vision capable
```

## Failed models
```
tencent/hy3:free                  ❌ 404 - no vision support
```

## Usage in config.yaml
```yaml
auxiliary:
  vision:
    provider: nous
    model: google/gemini-3.6-flash
    base_url: ''           # empty = use Nous Portal default
    api_key: ''            # empty = use OAuth agent_key from auth.json
```

## Gentech default
Per Jordan (Jul 30, 2026): "Use nous research portal for auxiliary."
`auxiliary.vision.provider: nous` with `model: google/gemini-3.6-flash` is the official default.
