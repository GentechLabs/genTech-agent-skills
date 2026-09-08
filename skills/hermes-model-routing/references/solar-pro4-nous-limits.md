# Solar Pro 4 on Nous Portal — Known Limits

**Model:** `upstage/solar-pro4:free`  
**Provider:** `nous`  
**Base URL:** `https://inference-api.nousresearch.com/v1`  
**Cost:** Free (no known billing limits as of Sep 2026)

## Observed Behavior (Sep 5, 2026)

Solar Pro 4 free on Nous has a **per-response output token cap** that truncates long responses mid-generation. The model stops producing output partway through, often after a few hundred tokens, even when the input context is large (50K-70K tokens seen in testing).

### Symptoms

- Agent produces a response that appears to start normally but stops mid-sentence or mid-paragraph
- Low output token counts (89-200 tokens) on calls where a long response was expected
- Session logs show normal input tokens (50K+) but disproportionately small output
- No 429 or rate-limit error — the model just stops
- Telegram shows "typing..." then a short or incomplete message appears

### What it looks like in session data

From a treasury session (2026-09-05, 34 API calls with Solar Pro 4 free):
- Output range: 89 → 6,642 tokens
- Average: ~713 tokens
- 12/34 calls came back under 200 output tokens
- Very low output calls (89, 92, 104, 130, 150, 159, 165, 167, 168, 234, 250, 268 tokens) cluster below the apparent cap
- Higher output calls (566, 597, 612, 6642, 672, 757, 768, 895, 1162, 1364, 1599, 2047, 2345, 3495) suggest the cap may be around 2,000-3,500 tokens, with variability

### What it means in practice

- **Fine for:** short answers, chat, coordination, summaries under ~500 tokens, code snippets, quick analysis
- **Problematic for:** long-form reports, full code dumps in one shot, detailed analysis that needs to be comprehensive in a single response, any task where the model would naturally want to write 1K+ tokens

### Workarounds

1. **Chunk the request** — ask for part 1, get the response, then "continue" for part 2. More turns but stays under the cap.
2. **Switch models for long-form work** — when you need a long comprehensive response, use a model without this cap (DeepSeek V4 Flash on Nous also free, or GLM-5.2 on OpenCode Go when billing resets).
3. **Design prompts for brevity** — ask for bullet lists, structured output, or "key points only" rather than prose dumps.

## Model Switch Pattern (Same Provider, Different Model)

When a model on a free provider hits a limitation (output cap, quality issue, etc.), switching to a different free model on the **same provider** is faster and safer than waiting for a paid provider to reset:

```
Problem: Solar Pro 4 free hits output cap
    ↓
Switch: nous/upstage/solar-pro4:free → nous/deepseek/deepseek-v4-flash
    ↓
Both free on Nous, same base_url, no billing impact
    ↓
When paid provider resets (tomorrow): switch back to GLM-5.2 if desired
```

This is preferable to waiting because:
- Same provider = same base_url, no config rewrite needed
- Both free = no cost risk
- Immediate — no waiting for billing reset
- Reversible — switch back when the better model is available

## Comparison: Nous Free Models

| Model | Provider | Cost | Output Cap? | Best For |
|-------|----------|------|-------------|----------|
| `upstage/solar-pro4:free` | nous | Free | Yes (per-response cap) | Chat, short answers, coordination |
| `deepseek/deepseek-v4-flash` | nous | Free | Not observed | General work, coding, longer responses |
| `tencent/hy3:free` | nous | Free | Unknown | Vision tasks (used as vision provider) |

## When to Avoid Solar Pro 4 Free

- Tasks that require long comprehensive output in a single response
- Code generation that produces large files (split into smaller pieces or use DeepSeek)
- Any task where truncated output would break downstream processing
- Audit/review work that needs to see the full picture at once
