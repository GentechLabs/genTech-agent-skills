# ClawRouter Image Generation — Hidden Model Reference

## GPT Image 2 via ClawRouter

`openai/gpt-image-2` works via `clawrouter_image_generate()` even though the tool's documented model list doesn't include it. The parameter passes through to the proxy which routes it correctly.

**Confirmed working (Aug 8, 2026):**
```python
clawrouter_image_generate(
    model="openai/gpt-image-2",
    prompt="...",
    size="1536x1024"
)
```

**Available sizes:** 1024x1024, 1536x1024, 1024x1536
**Observed cost:** $0.126/image at 1536x1024 (GPT Image 2), $0.042/image at 1536x1024 (GPT Image 1)
**Use case:** Character sheets, reference bibles, images with text labels/typography

## Vanito's Model Preference (Aug 2026)
- **Character sheets with text:** GPT Image 2 only ("I want you to use gpt image 2 only")
- **Standalone character portraits (no text):** Seedream 5.0 Pro (not available via ClawRouter; use blockrun_image if available)
- **Character animation:** Seedance 2.0 only — never xAI

## Other Hidden Models
Other models may also work through ClawRouter even if not documented. If a model fails with "Invalid model", try the documented alternatives.