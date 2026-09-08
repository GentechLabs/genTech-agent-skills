# Vision Model Selection — qwen3-vl:235b-instruct

**Decision (Jun 28, 2026):** Use qwen3-vl:235b-instruct (Ollama Cloud) as the primary vision model for Gentech Local.

## Why qwen3-vl:235b-instruct

| Feature | qwen3-vl:235b-instruct | llava:7b | gemma4-vision |
|---------|------------------------|----------|---------------|
| **Size** | 235B parameters | 7B | 9B |
| **OCR (code)** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Good | ⭐⭐⭐ Good |
| **Screenshots** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Good | ⭐⭐⭐⭐ Good |
| **Charts/Graphs** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐ Fair | ⭐⭐⭐⭐ Good |
| **Math from photos** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐ Poor | ⭐⭐⭐ Fair |
| **Context window** | 262K | ~32K | ~32K |
| **Architecture** | Mixture of Experts (MoE) | Standard | Standard |
| **Instruction-following** | ✅ Best | ⚠️ Good | ⚠️ Good |

## qwen3-vl:235b-instruct Variants

| Variant | Purpose | When to use |
|---------|---------|-------------|
| **qwen3-vl:235b** | General multimodal | Daily vision tasks |
| **qwen3-vl:235b-instruct** | Instruction-following | **Use this** — follows prompts perfectly |

## Why Not Local Vision?

| Aspect | Local (llava:7b) | Cloud (qwen3-vl:235b-instruct) |
|--------|------------------|---------------------------------|
| **RAM usage** | 4.7GB | 0GB ✅ |
| **VRAM usage** | 4GB (RTX 3070) | 0GB ✅ |
| **Quality** | Good | Excellent ✅ |
| **Context** | ~32K | 262K ✅ |
| **Speed** | Fast (local) | Fast (cloud) |

**For your use case (preserve RAM for Unreal Engine):**
- Local vision wastes 4.7GB RAM
- Cloud vision = 0GB RAM
- qwen3-vl:235b-instruct > llava:7b in quality

## Configuration

**Desktop app config:**

```yaml
auxiliary:
  vision:
    provider: ollama
    model: qwen3-vl:235b-instruct
```

**Environment variable:**
- `OLLAMA_CLOUD_API_KEY`: Your Ollama Cloud API key ($20/mo subscription)

**Alternative (if Ollama Cloud unavailable):**

```yaml
auxiliary:
  vision:
    provider: ollama
    model: llava:7b  # Fallback to local model
```

**Note:** This uses 4.7GB RAM, not recommended if Unreal Engine is running.

## Use Cases

| Task | Model | Why |
|------|-------|-----|
| **Debug screenshots** | qwen3-vl:235b-instruct | Best OCR, reads error messages |
| **Code screenshots** | qwen3-vl:235b-instruct | Extracts code accurately |
| **Market charts** | qwen3-vl:235b-instruct | Best at interpreting graphs |
| **Handwritten math** | qwen3-vl:235b-instruct | Recognizes formulas |
| **UI screenshots** | qwen3-vl:235b-instruct | Understands layout/context |

## Alternatives Considered

| Model | Decision | Reason |
|-------|----------|--------|
| **llava:7b** | ❌ | Local model, uses 4.7GB RAM |
| **qwen3-vl:8b** | ❌ | Lower quality than 235B |
| **gemma4-vision** | ❌ | Lower quality, limited context |
| **Z.AI glm-4v** | ❌ | Not supported (400 error) |

## Migration from llava:7b to qwen3-vl:235b-instruct

**Before:**
```yaml
auxiliary:
  vision:
    provider: ollama
    model: llava:7b
```

**After:**
```yaml
auxiliary:
  vision:
    provider: ollama
    model: qwen3-vl:235b-instruct
```

**Verification:**
```python
# Test vision
vision_analyze("path/to/screenshot.png", question="What do you see?")
# Should respond with high-quality analysis
```

*Documented: Jun 28, 2026*
*Context: Discord desktop app setup, 0GB RAM goal*