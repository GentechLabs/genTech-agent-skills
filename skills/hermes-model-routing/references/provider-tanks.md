---
name: Provider Tank Inventory
description: How to check each model provider's "tank" — balance, subscription status, reset cycles — before routing a job there. Tank exhaustion is silent until you hit a 429; check first.
---

# Provider Tank Inventory

Every model provider is a **tank** with its own:
- **Balance type:** free tier / monthly subscription / weekly subscription / pre-funded wallet / pay-per-token credit
- **Exhaustion signal:** HTTP 429, timeout, or "usage limit reached"
- **Reset cycle:** when the tank refills
- **How to check:** what you can query *before* routing a job

## Tank Table

| Provider | Tank Type | Current Models (active) | Exhaustion Signal | Reset Cycle | How to Check | Status (Sep 5, 2026) |
|----------|-----------|------------------------|-------------------|-------------|--------------|----------------------|
| **Nous Research portal** | Free models (+ $0.46 pay-per-token credit, persistent) | `upstage/solar-pro4:free`, `deepseek/deepseek-v4-flash` | HTTP 429 only on paid models (free models don't burn credit) | Free models: persistent (no reset cycle); credit: persistent until spent | `curl` a free model with a tiny request; 200 = tank open | **Open** — Solar Pro 4 + DeepSeek free, $0.46 credit remains (free models don't spend it) |

**Current fleet wiring (Sep 5, 2026):**
- **Nous portal** = primary tank. Solar Pro 4 free is the default on 64 cron jobs across 4 profiles. DeepSeek V4 Flash on Nous is the same-provider drop-in when Solar's output cap would truncate (e.g. PA Suite). $0.46 credit persists and is NOT spent by free models — it's a backup buffer only touched by paid Nous models, of which none are currently in use.
- **OpenCode Go** = exhausted (monthly subscription). 0 cron jobs assigned. Fleet switched off it on Sep 5. Resets ~Sep 6-7.
- **Ollama Cloud** = exhausted (weekly subscription). 0 cron jobs assigned. Resets ~Sep 6.
- **Z.AI** = unusable since Jul 4 (all tiers 429 / timeout). Phantom burn suspected. Do not route here without confirming health first.
- **BlockRun Kimi** = pre-funded wallet. Unknown balance — check before routing heavy Kimi jobs.
- **Local Ollama** = free, self-hosted. Verify service + model availability before routing.
- **OpenAI Codex** = US-only hard fallback in all 4 profiles. GPT-5.x. No Chinese-origin dependency.

**Double-subscription-exhaustion scenario (happened Sep 5):** when OpenCode Go monthly AND Ollama Cloud weekly are both down simultaneously, the only healthy tanks are Nous portal free models, local Ollama (if running), Groq free tier (if configured), and a funded BlockRun Kimi wallet. This is the default-no-subscription state — route to Nous free models unless a specific task needs a paid model or a US-only fallback.
| **OpenCode Go** | Monthly subscription (~$10/mo) | `glm-5.3-flash`, `glm-5.2`, `deepseek-v4-flash`, `kimi-k2.7-code`, `qwen3.6-plus`, `mimo-v2.5` | `GoUsageLimitError: Monthly usage limit reached` (HTTP 429) | **Monthly** — expires in ~4 days (workspace `wrk_01KNS65MGSRVHWMXY4WDA77QEV`) | Error message includes reset link: `https://opencode.ai/workspace/<workspace_id>/go` | **Exhausted** until monthly reset (~Sep 6-7, 2026) |
| **Ollama Cloud** | Weekly subscription | `glm-5.3-flash`, `glm-5.2`, `deepseek-v4-flash`, `kimi-k2.7-code`, `gpt-oss:120b`, `nemotron-3-super` | HTTP 429: "weekly usage limit" | **Weekly** — expires in ~1 day | API returns 429 on any model in the subscription | **Exhausted** until weekly reset (~Sep 6, 2026) |
| **Z.AI** | Pay-per-token / subscription | `glm-4.7`, `glm-5`, `glm-5.2`, `glm-5.3-flash` | HTTP 429: "Insufficient balance" | Weekly quota (with peak/off-peak multipliers) | API call returns 429 or timeout (glm-4.7-flash broken since Jul 4) | **Unusable** as of Jul 4, 2026 (all tiers 429); phantom burn suspected |
| **BlockRun (Kimi)** | Pre-funded wallet | `kimi-k2.7-code`, `kimi-k3` | HTTP 429 or payment-required | Refills when Jordan funds the wallet | Check wallet balance via BlockRun MCP or dashboard | **Unknown** — check before routing heavy jobs |
| **Local Ollama** | Free (self-hosted) | `llama3.1:8b`, `llama3.1:70b`, `qwen2.5-coder:7b` | Service down or model not pulled | N/A (your hardware) | `curl http://localhost:11434/api/tags` + `systemctl is-active ollama` | **Unknown** — verify before routing |

## Checking Each Tank

### Nous Research portal (free + credit)
```bash
# Test a free model — if it responds, the free tier is open
curl -s --max-time 15 https://inference-api.nousresearch.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $NOUS_TOKEN" \
  -d '{"model":"upstage/solar-pro4:free","messages":[{"role":"user","content":"test"}],"max_tokens":5}'
```
- 200 = tank open
- 429 = credit exhausted (only on paid models; free models like `solar-pro4:free` don't burn credit)

### OpenCode Go (subscription)
- Error message from any API call tells you directly: `GoUsageLimitError` with workspace ID + reset link.
- Check the workspace dashboard: `https://opencode.ai/workspace/<workspace_id>/go`
- No pre-check API — the 429 *is* the check. Route there only if you can tolerate a failed first call + retry.

### Ollama Cloud (weekly subscription)
- Same as OpenCode Go — 429 is the signal. No pre-check.
- Distinguish from OpenCode Go by provider name in the error metadata.

### Z.AI
- `glm-4.7-flash` times out (broken since Jul 4, 2026) — do not use.
- `glm-4.7`, `glm-5`, `glm-5.2` return 429 when quota exhausted.
- Check: `curl` any model with a 15s timeout; 429 = exhausted, timeout = broken model.

### BlockRun Kimi
- Check wallet balance via BlockRun dashboard or MCP.
- Pricing: $3/1M input, $15/1M output. Estimate before routing: `(input_tokens/1M)*3 + (output_tokens/1M)*15`.

### Local Ollama
```bash
systemctl is-active ollama          # must be active
curl http://localhost:11434/api/tags  # must list the model you want
free -h                              # enough RAM for the model (8B = ~8GB, 70B = ~31GB+)
```

## Routing Rules with Tanks

1. **Always route to the cheapest healthy tank first.** Free tanks (Nous free models, local Ollama, Groq free tier) before any paid tank.
2. **Primary and fallback must be on different providers with different reset cycles.** If primary is a subscription (OpenCode Go, Ollama Cloud), the fallback must be a different tank (Nous free, DeepSeek, local). Never set `fallback_model` to the same exhausted provider — that's the stuck-agent trap (see skill body).
3. **When a tank goes dry mid-session:** don't retry the same model. Escalate tier within the same provider (Z.AI: glm-4.7 → glm-5 → glm-5.2) OR switch to a different provider's tank (Nous, DeepSeek, local).
4. **Log the tank state** with every routing decision so the cost ledger reflects reality: which provider, which model, whether the tank was healthy at route time.

## Reset Calendar (Sep 2026)

| Tank | Exhausted? | Reset estimate |
|------|-----------|----------------|
| Nous portal credit ($0.46) | No (open) | N/A (persistent) |
| OpenCode Go monthly | **Yes** | ~Sep 6-7, 2026 |
| Ollama Cloud weekly | **Yes** | ~Sep 6, 2026 (1 day) |
| Z.AI weekly | **Yes** (all tiers) | Unknown — regenerate key after reset |
| BlockRun Kimi wallet | Unknown | When funded |
| Local Ollama | N/A | N/A |

**If both OpenCode Go AND Ollama Cloud are down** (both subscription tanks empty), the only healthy tanks are:
- Nous portal free models (Solar Pro 4, DeepSeek V4 Flash)
- Local Ollama (if running)
- Groq free tier (if configured)
- BlockRun Kimi (if wallet funded)

This is the **double-subscription-exhaustion** scenario — everything paid is down, only free tanks remain. Route accordingly.
