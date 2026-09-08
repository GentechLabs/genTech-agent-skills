# GLM-4.7-Flash Free Access and Local Deployment

## Free API Access

GLM-4.7-Flash is **permanently free** via Z.AI's API. This is intentional — Z.AI's market strategy to compete with GPT-4-mini.

### Why It's Free

| Factor | Explanation |
|--------|-------------|
| Open-source model | Weights on HuggingFace, anyone can run locally |
| Market penetration | Get developers hooked on Z.AI platform |
| Competition | "42x cheaper than Claude" positioning |
| UX pattern | Free tier leads to paid upgrades |

### API Verification (Jul 3, 2026)

Tested with Gentech's Z.AI API key:

```bash
curl -s -X POST https://api.z.ai/api/paas/v4/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_KEY" \
  -d '{
    "model": "glm-4.7-flash",
    "messages": [{"role": "user", "content": "test"}],
    "max_tokens": 3
  }'
```

**Result:** ✅ 200 OK — works without any subscription

### Pricing Comparison

| Model | Input | Output | Status |
|-------|-------|--------|--------|
| GLM-4.7 | $0.6 | $2.2 | ❌ Requires resource package |
| GLM-4.7-Flash | Free | Free | ✅ Free API |
| GLM-4.7-FlashX | $0.07 | $0.4 | ❌ Requires resource package |
| GLM-5.2 | $1.4 | $4.4 | ❌ Requires resource package |

### Practical Use

**When to use GLM-4.7-Flash:**
- Your Z.AI subscription doesn't include paid GLM models
- You want free GLM-4.7 quality
- Testing/integration without cost
- Backup when paid models hit quota

**Configuration in Hermes:**

```yaml
model:
  default: glm-4.7-flash
  provider: zai
```

```bash
hermes config set model glm-4.7-flash
hermes config set provider zai
```

---

## Local Deployment Constraints

GLM-4.7-Flash can be run locally via Ollama or vLLM, but hardware requirements are significant.

### Model Sizes (from Ollama)

| Variant | Size | RAM Needed | Use Case |
|---------|------|------------|----------|
| `glm-4.7-flash:q4_K_M` | 19GB | ~22GB | 4-bit quantized, balanced |
| `glm-4.7-flash:q8_0` | 32GB | ~35GB | 8-bit, higher accuracy |
| `glm-4.7-flash:bf16` | 60GB | ~64GB | Full precision, best quality |

### Current VPS Constraints (Gentech)

| Resource | Available | Requirement | Status |
|----------|-----------|-------------|--------|
| Disk | 83GB | 19-60GB | ✅ Plenty of space |
| RAM | 11GB | 22-64GB | ❌ Insufficient |

**Impact:**
- With 11GB RAM, a 19GB model would require constant swapping
- Result: 1-2 tokens per second (vs 50+ tps normal)
- High CPU usage on disk I/O
- Not practical for production use

### Deployment Options

#### Option 1: Free API (Recommended)

```bash
# No deployment needed — just use Z.AI API
hermes config set model glm-4.7-flash
hermes config set provider zai
```

**Pros:**
- Zero hardware cost
- Fast (50+ tps)
- Same quality as local
- No maintenance

**Cons:**
- Depends on Z.AI availability
- Requires internet connection

#### Option 2: Local Deployment (High-Spec Machine)

**Requirements:**
- 24GB+ RAM for q4_K_M (19GB model)
- 32GB+ RAM for q8_0 (32GB model)
- 64GB+ RAM for bf16 (60GB model)

**Commands:**

```bash
# Pull model (2-3 minutes on 1Gbps)
ollama pull glm-4.7-flash

# Run locally
ollama run glm-4.7-flash

# Or configure Hermes to use local Ollama
hermes config set model glm-4.7-flash
hermes config set provider ollama
```

**Pros:**
- No API calls
- Privacy (data stays local)
- No rate limits
- Works offline

**Cons:**
- Requires significant hardware
- Setup complexity
- Maintenance overhead
- Slower than API on modest hardware

### For Home Deployment

When Jordan is home with his laptop, local GLM-4.7-Flash is viable if:

| Laptop Specs | GLM-4.7-Flash Variant |
|--------------|----------------------|
| 24GB RAM | q4_K_M (19GB) ✅ |
| 32GB RAM | q8_0 (32GB) ✅ |
| 64GB RAM | bf16 (60GB) ✅ |

---

## Key Takeaways

1. **GLM-4.7-Flash is free forever** — use the API, don't fight with local deployment
2. **VPS can't run it** — 11GB RAM is insufficient for 19GB+ models
3. **Use free API for now** — same quality, faster, zero cost
4. **Local deployment for home** — viable if laptop has 24GB+ RAM
5. **Platform play** — Z.AI wants you hooked on the platform, Flash is the hook

---

## References

- Z.AI Pricing: https://docs.z.ai/guides/overview/pricing
- GLM-4.7-Flash on HuggingFace: https://huggingface.co/zai-org/GLM-4.7-Flash
- GLM-4.7-Flash on Ollama: https://ollama.com/library/glm-4.7-flash
- Unsloth GGUF Guide: https://unsloth.ai/docs/models/glm-4.7-flash