# OpenCode Go — Cost Model & Economics

Verifiable from https://opencode.ai/docs/go/ (Sep 2026). Use this to value the $10/mo
subscription against alternatives and to route work to the cheapest rail.

## The headline: 6× multiplier
"You pay $10/month and we aim to give you **6x that in usage**" ≈ **$60 worth of
usable model throughput per month**. For most models the 6x comes from bulk discounts +
reserved GPU. A few newer/cheaper models carry a lower multiplier because their public
price is already low.

## Real per-month request estimates (typical Go usage — verified table)
| Model | per 5-hr | per week | per month |
|---|---|---|---|
| DeepSeek V4 Flash | 7,600 | 18,900 | **37,800** |
| DeepSeek V4 Flash Vision Exp | 3,800 | 9,450 | 18,900 |
| DeepSeek V4 Pro | 1,050 | 2,600 | 5,200 |
| GLM-5.3-Flash | 1,580 | 3,950 | 7,900 |
| GLM-5.3 | 220 | 540 | 1,080 |
| Kimi K2.7 Code | 1,350 | 3,380 | **6,750** |
| Min-Max M3 | 3,200 | 8,000 | 16,000 |
| Qwen3.8 Flash | 5,400 | 13,500 | 27,000 |
| Qwen3.7 Plus | 4,300 | 10,800 | 21,600 |

## Key per-token prices (to pick the cheap rail)
- **DeepSeek V4 Flash** off-peak: $0.22 in / $0.66 out per 1M (peak $0.44/$1.32)
- **GLM-5.3-Flash**: $0.15 / $0.50 — cheapest of the GLM family, near-MiMo cost
- **Kimi K2.7 Code**: $0.95 / $4.00 (but high monthly usage bucket = good auditor value)
- MiMo-V2.5: $0.14 / $0.28 — the bargain rail, 150K requests/mo

## Peak vs off-peak (DeepSeek family)
Peak = **01:00–04:00 and 06:00–10:00 UTC, Mon–Fri**; all other hours + weekends are
off-peak (≈60% cheaper input, 50% cheaper output for Flash). Heavy DeepSeek jobs should
be queued into off-peak windows.

## When you hit the cap
- Free models remain usable after the Go limit (doesn't hard-block).
- Optionally enable **"Use balance"** in the console → falls back to Zen credits after
  the Go limit instead of blocking.
- Tracking: https://opencode.ai/auth (Jordan's console).

## Value vs alternatives (the pivot that made this worth it)
- $10/mo OpenCode Go = ~$60 usable output (6×), includes **our exact stack**:
  deepseek-v4.1-flash (primary), glm-5.3-flash (vision), kimi-k2.7-code (auditor).
- Nous/Hermes portal: drained by the persist-glitch; wider model list but **no usable
  balance until recharged** — OpenCode Go now the reliable backup rail.
- ollama-cloud: primary, resets weekly (~84% used mid-Sep 15), pay-as-you-go credits.
  OpenCode Go (monthly reset) desyncs naturally as the gap-filler.

## Operator notes (verified live Sep 15)
- **Every request MUST send `x-opencode-session`** header or it 400s (MissingSessionID).
- **Do NOT send a broad user-agent** (e.g. Python-urllib/3.x) → 403 abusive-traffic,
  account-flagging risk. Use a specific UA like `GentechLabs-Hermes/1.0`.
- Model ids are bare (`deepseek-v4.1-flash`); config uses `opencode-go/<model-id>`.
- Probe model: `minimax-m3` (non-China-hosted, reliable liveness check).
