# Z.AI Quota Troubleshooting

## Error Codes

| Error | Message | Meaning |
|-------|---------|---------|
| 1113 | "Insufficient balance or no resource package. Please recharge." | Paid quota exhausted |
| 429 | Rate limit | API rate limit exceeded |
| 401 | "令牌已过期或验证不正确" (token expired or invalid) | Token expired or invalid |

## Testing Model Availability

```bash
# Test model via API
python3 << 'EOF'
import requests

zai_key = "YOUR_KEY_HERE"

response = requests.post(
    "https://api.z.ai/api/paas/v4/chat/completions",
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {zai_key}"
    },
    json={
        "model": "glm-4.7-flash",
        "messages": [{"role": "user", "content": "test"}],
        "max_tokens": 5
    },
    timeout=10
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
EOF

# Get account-specific model list
curl -s https://api.z.ai/api/paas/v4/models \
  -H "Authorization: Bearer YOUR_KEY_HERE" | python3 -m json.tool
```

## GLM-4.7-flash Discovery (Jul 3, 2026)

**Key Insight:** The `/models` endpoint returns a platform-wide list, NOT account-specific access. You must test models via actual API calls to confirm they work for your account.

**What works when paid quota exhausted:**
- ✅ `glm-4.7-flash` — FREE tier, 200K context, 128K max output
- ❌ All paid models (GLM-4.7, GLM-4.7-flashx, GLM-5 series) — 429/1113 errors

**Available models to account (verified via API):**
- glm-4.5
- glm-4.5-air
- glm-4.6
- glm-4.7 (paid, exhausted)
- glm-5 (paid, exhausted)
- glm-5-turbo (paid, exhausted)
- glm-5.1 (paid, exhausted)
- glm-5.2 (paid, exhausted)

## Quick Fix: Switch to GLM-4.7-flash

```bash
# Immediate fallback to free tier
hermes config set model glm-4.7-flash
hermes config set provider zai

# Or use existing fallback provider
hermes config set model deepseek-v4-flash
hermes config set provider opencode-go
```

## Long-term Fix: Recharge Z.AI Account

If paid access is needed, recharge the Z.AI subscription through the dashboard.

## Prevention

Monitor Z.AI usage before hitting quota limits. When paid models return 1113, switch immediately to GLM-4.7-flash or DeepSeek Flash to prevent tasks from blocking.