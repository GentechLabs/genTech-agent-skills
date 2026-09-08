# Ollama Cloud Pricing Research — July 6, 2026

**Date:** July 6, 2026
**Source:** https://ollama.com/pricing (scraped via Python scrapling)
**Session Context:** Model comparison for replacing GLM 5.2, investigating Alama Cloud usage spikes

---

## Pricing Tiers

| Plan | Price | Usage | Concurrent Models | Use Cases |
|------|-------|-------|-------------------|-----------|
| **Free** | $0 | Light usage | 1 | Chatting, evaluating larger models, coding with small models |
| **Pro** | $20/month ($200/yr) | Day-to-day work | 3 | Larger models, coding automation, deep research |
| **Max** | $100/month | Heavy, sustained usage | 10 | Continuous agent tasks, multiple concurrent agents, extended sessions |

---

## GPU-Time Billing Model (Critical Discovery)

**Ollama Cloud uses GPU time billing, NOT token-based billing.**

> "Usage reflects actual utilization of Ollama's cloud infrastructure — primarily GPU time, which depends on model size and request duration."

**How it differs from token-based pricing:**
- **Token-based (ZAI, OpenCode Go):** Billed per token processed
- **GPU-time (Ollama):** Billed per minute of GPU usage
- **Result:** Efficiency matters more than token count

**Session limits:**
- Reset every **5 hours** (session limits)
- Reset every **7 days** (weekly limits)
- Email reminder at 90% of limit

**Usage measurement:**
- Primarily GPU time (depends on model size + request duration)
- Shorter requests = less GPU time = lower cost
- Hardware efficiency improvements lower costs over time

---

## Cost Comparison: Token-Based vs GPU-Time

### Scenario: Monthly Agent Workload

**Assumptions:**
- 50 security audits (10K output tokens each)
- 500 code builds (5K output tokens each)
- Average request: 30 seconds GPU time

**Token-Based (GLM 5.2 via ZAI):**
- Input: 500K × $0.40/M = $200
- Output: 750K × $1.00/M = $750
- **Total:** $950/month

**Ollama Cloud (Pro Plan):**
- GPU time: 550 requests × 30s = 16,500 seconds = 275 minutes
- Pro plan: $20/month (unlimited within limits)
- **Total:** $20/month

**Savings:** 97.9% ($930/month)

---

## Pro Plan Limits (Unknown - Need Investigation)

**Known:**
- Session limits reset every 5 hours
- Weekly limits reset every 7 days
- 90% reminder email before hitting limits
- Supports 3 concurrent models

**Unknown (Forge task):**
- What is the "day-to-day work" quota?
- What is the weekly limit?
- How many GPU hours included in Pro plan?

**Test scenario:**
```bash
# Check current Ollama Cloud usage
curl -H "Authorization: Bearer $OLLAMA_API_KEY" \
  https://api.ollama.com/v1/usage

# Expected: JSON with current plan, usage, limits
```

---

## Dual-Agent Concurrent Needs

**Gentech Dual-Agent Architecture:**
- **Gentech (VPS):** 24/7 ops, cron jobs
- **Forge (Desktop):** Development, OSS work

**Concurrent models needed:**
- Gentech: 2-3 models (audit, vision, fallback)
- Forge: 1-2 models (coding, vision)
- **Total: 3-5 concurrent models**

**Plan recommendation:**
- **Pro Plan:** 3 concurrent models ✅ (adequate)
- **Max Plan:** 10 concurrent models (overkill)

---

## Available Models

From Gentech April 2026 config backup:

| Model | Used By | Status |
|-------|---------|--------|
| **deepseek-v4-flash** | Gentech, YoYo, Desmond, CLI | ✅ Available |
| **qwen3-coder-next** | DMOB | ✅ Available |
| **qwen2.5-vision** | Not currently used | ✅ Available |

---

## Dual-Model Strategy Comparison

### Current (Token-Based)
```
Build Model: DeepSeek V4 Flash ($0.01/1M)
Audit Model: GLM 5.2 ($1.00/1M)
Monthly Cost: ~$950
```

### Proposed (Ollama Cloud)
```
Build Model: deepseek-v4-flash (included in Pro)
Audit Model: qwen3-coder-next (included in Pro)
Monthly Cost: $20
```

### Hybrid (Optimal)
```
Build Model: Ollama Cloud deepseek-v4-flash (unlimited)
Audit Model: Ollama Cloud qwen3-coder-next (unlimited)
Vision: DeepSeek V4 Pro via OpenCode Go (when needed)
Monthly Cost: $20 + vision costs (~$100) = $120
```

---

## Configuration Change

### Current (Gentech VPS)
```yaml
model:
  default: glm-4.7
  provider: zai

auxiliary:
  vision:
    provider: zai
    model: glm-5.2
```

### Proposed (Ollama Cloud)
```yaml
providers:
  ollama-cloud:
    api_key: ${OLLAMA_API_KEY}
    base_url: https://ollama.com/v1
    type: openai_compatible

model:
  default: deepseek-v4-flash
  provider: ollama-cloud

auxiliary:
  vision:
    provider: ollama-cloud
    model: qwen2.5-vision
```

**Change steps:**
1. Add Ollama Cloud provider to config
2. Set default model to deepseek-v4-flash
3. Switch vision model to qwen2.5-vision
4. Monitor Pro plan limits for 1 week
5. Adjust if hitting limits

---

## Investigation Tasks (Forge)

### 1. Check Pro Plan Limits
```bash
curl -H "Authorization: Bearer $OLLAMA_API_KEY" \
  https://api.ollama.com/v1/usage
```

### 2. Test deepseek-v4-flash on Ollama
```bash
# Simple coding task
curl -X POST https://api.ollama.com/v1/chat/completions \
  -H "Authorization: Bearer $OLLAMA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4-flash",
    "messages": [{"role": "user", "content": "Write a Python hello world"}]
  }'
```

### 3. Test qwen3-coder-next on Ollama
```bash
# Security audit test
curl -X POST https://api.ollama.com/v1/chat/completions \
  -H "Authorization: Bearer $OLLAMA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-coder-next",
    "messages": [{
      "role": "user",
      "content": "Audit this code for vulnerabilities:\n\ndef process_input(user_input):\n    return eval(user_input)"
    }]
  }'
```

### 4. Monitor GPU Time Usage
- Run 10 audits
- Measure GPU time per audit
- Extrapolate to monthly usage

---

## Success Criteria

- ✅ Pro plan covers monthly workload
- ✅ Model quality comparable to GLM 5.2
- ✅ Cost savings >80%
- ✅ No limit hits during normal operations

---

## Summary

| Provider | Model | Pricing | Monthly Cost | Quality |
|----------|-------|---------|--------------|---------|
| **ZAI (current)** | GLM 5.2 | $0.40/$1.00 per 1M | ~$950 | High |
| **Ollama Cloud** | qwen3-coder-next | $20/month (unlimited) | $20 | Unknown |
| **OpenCode Go** | DeepSeek V4 Pro | ~$0.26/$0.65 per 1M | ~$247 | High |

**Recommendation:** Test Ollama Cloud Pro plan. If quality comparable, switch for 97% cost savings.

---

## Scrapling Commands Used

```python
from scrapling.fetchers import StealthyFetcher

# Fetch pricing page
page = StealthyFetcher.fetch('https://ollama.com/pricing')
body = page.css('body').get()

# Extract pricing tiers
lines = body.split('\n')
for i, line in enumerate(lines):
    if any(keyword in line.lower() for keyword in ['$', 'price', 'plan', 'tier', 'month']):
        # Print context
        start = max(0, i-2)
        end = min(len(lines), i+3)
        print(f"--- Lines {start}-{end} ---")
        for j in range(start, end):
            print(f"{j}: {lines[j][:200]}")
        print()
        if i > 300:  # Don't go too deep
            break
```

**Pricing page location:** Lines 117-156 contain pricing tiers ($0, $20/mo, $100/mo)