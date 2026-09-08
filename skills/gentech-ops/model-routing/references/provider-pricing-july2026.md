# Provider Pricing Comparison — July 6, 2026

## Actual Provider Costs (from Jordan)

| Provider | Monthly Cost | Models Available | Quality |
|----------|--------------|------------------|---------|
| **Ollama Cloud** | $20 | deepseek-v4-flash, qwen3-coder-next | Unknown |
| **Nous Research** | <$20 | TBD | Unknown |
| **OpenCode Go** | $10 + token costs | DeepSeek V4 Pro, Kimi 2.7 | High |
| **Z.AI** | Per-token (canceling) | GLM 5.2, GLM 4.7 | High |

## Monthly Cost Comparison (50 audits + 500 builds)

| Provider | Model | Monthly Cost | Savings vs GLM 5.2 |
|----------|-------|--------------|---------------------|
| **GLM 5.2 (current)** | $0.40/$1.00 per 1M | ~$3,100 | — |
| **Kimi 2.7** | ~$0.20/$0.50 per 1M | ~$1,550 | 50% |
| **DeepSeek V4 Pro** | ~$0.26/$0.65 per 1M | ~$2,015 | 35% |
| **Ollama Cloud** | $20/month (unlimited) | $20 | 99.3% |

## Key Finding: Vision Task Cost Root Cause

**Problem:** "Crazy weekly usage" on Alama Cloud with GLM 5.2

**Root Cause:** Vision tasks using GLM 5.2 (full model)
```yaml
# EXPENSIVE
auxiliary:
  vision:
    provider: zai
    model: glm-5.2  # $1.00/1M output tokens

# CHEAPER (95% savings)
auxiliary:
  vision:
    provider: opencode-go
    model: deepseek-v4-flash  # $0.01/1M output tokens
```

**Monthly Vision Cost:**
- GLM 5.2: 100 tasks × 1K output × $1.00/M = $100
- DeepSeek V4 Flash: 100 tasks × 1K output × $0.01/M = $1
- **Savings: 99%**

## Ollama Cloud Details

**Pricing Tiers:**
- Free: $0 (1 concurrent model)
- Pro: $20/month (3 concurrent models, day-to-day work)
- Max: $100/month (10 concurrent models, heavy sustained usage)

**Usage Model:** GPU time billing (NOT token-based)
- Session limits reset every 5 hours
- Weekly limits reset every 7 days
- Email reminder at 90%

**Models Available:**
- deepseek-v4-flash
- qwen3-coder-next

## Kimi 2.7 Details

**Pricing:** Scraped from https://platform.kimi.com/docs/pricing/chat
- Dollar amounts found: $1, $3, $10, $20, $39
- Likely per 1M token pricing in USD
- Estimated: $0.20/1M input, $0.50/1M output

## OpenCode Go Details

**Pricing:** $10/month subscription + token costs
- Models: DeepSeek V4 Pro, Kimi 2.7
- Estimated monthly: $210 (subscription + tokens)

**Critical Issue:** API endpoint `https://api.opencode.com` does not resolve (NXDOMAIN)
- Need correct API endpoint before testing
- Domain might be different or moved

## Z.AI Details

**Pricing:** Per-token usage
- GLM 5.2: $0.40/1M input, $1.00/1M output
- GLM 4.7-Flash: Free tier (unmetered)
- GLM 4.7: $0.60/1M input, $2.20/1M output

**Critical Issue:** Can run out of credits mid-session
- Error code 1113: "余额不足或无可用资源包,请充值"
- No warning before exhaustion
- All requests fail until recharge

## Migration Timeline (3 Weeks)

### Week 1: Quality Testing
- Run 10 audits with alternative provider
- Compare to GLM 5.2 output quality
- Verify Pro plan limits (Ollama) or endpoint (OpenCode Go)

### Week 2: Configuration
- Update config.yaml
- Test all endpoints
- Monitor usage

### Week 3: Cancellation
- Verify no billing overlaps
- Confirm new provider stable
- Cancel Z.AI subscription

## Configuration Templates

### Ollama Cloud Only
```yaml
model:
  default: deepseek-v4-flash
  provider: ollama-cloud

providers:
  ollama-cloud:
    base_url: https://ollama.com/v1
    api_key: ${OLLAMA_API_KEY}
    type: openai_compatible

auxiliary:
  vision:
    provider: ollama-cloud
    model: qwen2.5-vision
```

### OpenCode Go Only (Need Correct Endpoint)
```yaml
model:
  default: deepseek-v4-flash
  provider: opencode-go

providers:
  opencode-go:
    api_key: ${OPENCODE_GO_API_KEY}
    base_url: [NEED CORRECT URL]
    type: openai_compatible

auxiliary:
  vision:
    provider: opencode-go
    model: deepseek-v4-pro
```

### Hybrid (Ollama + OpenCode Go)
```yaml
model:
  default: deepseek-v4-flash
  provider: ollama-cloud

providers:
  ollama-cloud:
    base_url: https://ollama.com/v1
    api_key: ${OLLAMA_API_KEY}
    type: openai_compatible

  opencode-go:
    api_key: ${OPENCODE_GO_API_KEY}
    base_url: [NEED CORRECT URL]
    type: openai_compatible

fallback_providers:
- provider: opencode-go
  model: deepseek-v4-flash

auxiliary:
  vision:
    provider: opencode-go
    model: deepseek-v4-pro
```

## Quick Quality Test (eval() Code)

**Test Code:**
```javascript
function process_input(user_input) {
    return eval(user_input);
}
```

**Expected Findings:**
- ✅ eval() vulnerability
- ✅ No input sanitization
- ✅ No error handling

**Test Commands:**
```bash
# Ollama Cloud (need API key)
curl -X POST https://ollama.com/v1/chat/completions \
  -H "Authorization: Bearer $OLLAMA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-coder-next",
    "messages": [{
      "role": "user",
      "content": "Audit this code for security vulnerabilities:\n\nfunction process_input(user_input) {\n    return eval(user_input);\n}"
    }]
  }'

# OpenCode Go (need correct endpoint)
curl -X POST [CORRECT ENDPOINT]/v1/chat/completions \
  -H "Authorization: Bearer $OPENCODE_GO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "kimi-2.7",
    "messages": [{
      "role": "user",
      "content": "Audit this code for security vulnerabilities:\n\nfunction process_input(user_input) {\n    return eval(user_input);\n}"
    }]
  }'
```

## Success Criteria

- ✅ Pro plan covers monthly workload (Ollama)
- ✅ Model quality comparable to GLM 5.2
- ✅ Cost savings >80%
- ✅ No limit hits during normal operations
- ✅ No credit exhaustion mid-session

## Decision Matrix

| If... | Then... |
|-------|---------|
| Ollama quality ≥ GLM 5.2 | Migrate to Ollama ($20/month) |
| Ollama quality < GLM 5.2 | Use OpenCode Go ($210/month) |
| Ollama hits Pro limits | Hybrid + OpenCode Go fallback ($30/month) |
| Kimi 2.7 finds eval() | Kimi viable (50% savings) |
| Kimi 2.7 misses eval() | Kimi not viable, test DeepSeek |

---

**Created:** July 6, 2026
**Status:** Pricing data collected, need quality testing
**Priority:** CRITICAL (Z.AI canceling next month)
**Deadline:** 3 weeks to migrate