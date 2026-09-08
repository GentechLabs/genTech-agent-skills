# Model Access Verification Pattern

## Core Principle

**Discovery ≠ Access**

The `/models` endpoint returns a platform-wide catalog of ALL models. A model appearing in this list does NOT guarantee your account has access to it. You must verify via actual API calls.

## Verification Protocol

### Step 1: Get Model List (Catalog)

```bash
curl -s "https://api.z.ai/api/paas/v4/models" \
  -H "Authorization: Bearer YOUR_TOKEN" | python3 -m json.tool
```

This returns a list like:
```json
{
  "object": "list",
  "data": [
    {"id": "glm-4.5", "object": "model", "created": 1753632000, "owned_by": "z-ai"},
    {"id": "glm-4.7", "object": "model", "created": 1766332800, "owned_by": "z-ai"},
    {"id": "glm-4.7-flash", "object": "model", "created": 1766332800, "owned_by": "z-ai"}
  ]
}
```

**This list does NOT reflect your subscription quota or access.**

### Step 2: Test Actual Access

```python
import requests

zai_key = "YOUR_TOKEN_HERE"

models_to_test = ["glm-4.7", "glm-4.7-flash", "glm-5", "glm-5.2"]

for model in models_to_test:
    response = requests.post(
        "https://api.z.ai/api/paas/v4/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {zai_key}"
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 5
        },
        timeout=10
    )

    status_code = response.status_code
    if status_code == 200:
        print(f"✅ {model}: Available")
    elif status_code == 429:
        print(f"⚠️  {model}: Rate limited or quota exhausted")
    elif status_code == 401:
        print(f"❌ {model}: Token expired/invalid")
    else:
        print(f"❓ {model}: {status_code} - {response.text[:50]}")
```

### Step 3: Map Error Codes

| Status | Error Code | Meaning | Action |
|--------|------------|---------|--------|
| 200 | None | Model works | Use this model |
| 429 | 1113 | Quota exhausted | Switch to free tier or recharge |
| 429 | - | Rate limited | Wait or switch to another model |
| 401 | - | Token expired | Regenerate token |

## Common Misconceptions

### ❌ Wrong: "The model is in the list, so I can use it"

```bash
# This only shows what EXISTS on the platform
curl "https://api.z.ai/api/paas/v4/models" | grep "glm-4.7"
# Output: {"id": "glm-4.7", ...}  ← Doesn't mean YOU can use it
```

### ✅ Right: "The model passed an API test, so I can use it"

```bash
# This proves YOU have access
curl -X POST "https://api.z.ai/api/paas/v4/chat/completions" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model": "glm-4.7", "messages": [{"role": "user", "content": "test"}], "max_tokens": 10}'
# Output: 200 OK + completion data  ← Confirms access
```

## Discovery Case Study: GLM-4.7-flash (Jul 3, 2026)

**Situation:** User couldn't find GLM-4.7-flash in their model list

**Wrong diagnosis:** "GLM-4.7-flash isn't available to my account"

**Correct diagnosis:**
1. The `/models` endpoint shows ALL platform models (platform-wide catalog)
2. User tested via API call: GLM-4.7-flash returned 200 OK
3. GLM-4.7 (paid) returned 429/1113 (quota exhausted)

**Lesson:** Always verify via API calls. The catalog is just a menu — you still need to "pay" for access (either via subscription or free tier allocation).

## Implementation Pattern

When updating model configurations:

```bash
# 1. Get candidate model from catalog
models=$(curl -s "https://api.z.ai/api/paas/v4/models" \
  -H "Authorization: Bearer $TOKEN" | jq -r '.data[].id')

# 2. Test each candidate
for model in $models; do
  if test_model_access "$model"; then
    echo "✅ $model works"
    # 3. Update config ONLY after verification
    hermes config set model "$model"
    break
  fi
done
```

Never assume catalog availability = account access.