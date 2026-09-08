# Poster Text Removal via GPT-Image-2 Edit

## When to Use
The user explicitly requested text/logos be removed from the KAGEKŌ poster (2026-07-12) for a cleaner looping GIF. The poster had:
- "KONO SORA NO SHITA" / "UNDER THIS SKY" title text at top
- Vertical Japanese text on left edge
- "KAGEKŌ" logos on stage monitors
- "KAGEKŌ" crest/branding on banners

## Verified Command
```python
# Via BlockRun MCP:
result = blockrun_image(
    action="edit",          # edit mode, not generate
    image="<poster_url>",   # parameter is 'image', NOT 'image_url' for edit
    model="openai/gpt-image-2",
    prompt="Remove all text from this image. Remove 'KONO SORA NO SHITA', 'UNDER THIS SKY', all Japanese characters, and all logos... Keep everything else exactly the same.",
    size="1536x1024"        # keep the original widescreen proportion
)
```

## Critical Detail
- The `action="edit"` uses the `image` parameter (URL or base64), NOT `image_url`
- GPT-Image-2 fills in removed areas by matching the surrounding style — it does NOT change character positions, lighting, or art style
- Cost: ~$0.12 per edit
- The edit model may slightly alter character jacket details (e.g., KAGE's coat silhouette). This is acceptable since the animation step will reframe the image anyway

## Result
The cleaned poster is at: `scenes/poster-no-text.png` on the hub
