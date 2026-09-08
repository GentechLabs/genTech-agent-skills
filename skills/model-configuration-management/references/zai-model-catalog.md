# Z.AI Model Catalog Reference

Live model catalog for Z.AI via OpenRouter API. Updated from actual API responses.

## Available Models (as of July 2026)

### Core Models
- `z-ai/glm-5.2` - Max context (16K tokens), complex reasoning
- `z-ai/glm-4.7` - Balanced reasoning (8K tokens), default recommended
- `z-ai/glm-4.7-flash` - Fast variant (8K tokens), low latency
- `z-ai/glm-4.5` - Basic model (4K tokens), simple tasks
- `z-ai/glm-4.5v` - Vision model, image processing

### Verification Commands
```bash
# Check all Z.AI models
curl -s "https://openrouter.ai/api/v1/models" | jq '.data[] | select(.id | contains("z-ai")) | {id: .id, provider: .provider}'

# Filter specific models
curl -s "https://openrouter.ai/api/v1/models" | jq '.data[] | select(.id | contains("glm")) | {id: .id, provider: .provider}'
```

## Common Issues
- `glm-4.5-flash` does NOT exist in live catalog
- Direct Z.AI API returns 404, use OpenRouter instead
- Provider-prefixed names required for unambiguous routing