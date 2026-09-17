# Monid — Agent-Native Tool Router & Provider Platform

## Overview
Monid is "OpenRouter for agent tools" — one integration gives agents access to **1,300+ tools across 13+ providers**. Pay-per-call, no subscriptions, one balance. Supports Claude, Codex, Cursor, **Hermes** (listed in their "works with" section), and others.

**Website:** https://monid.ai
**Docs:** https://monid.ai/docs
**App:** https://app.monid.ai
**Status:** v0.1.0, Delaware C-Corp, San Francisco

## Key Features
- **Discover** — agents search the registry with natural language, get ranked candidates with pricing
- **Run** — execute tools directly, no per-provider sign-up needed
- **Pay per call** — one balance, debited per call (~$0.0013 typical)
- **$1 free credit** to start

## Integration Methods
1. **Skill** — one-line setup into agent's chat (`set up https://monid.ai/skill.md`)
2. **MCP** — remote MCP server (Streamable HTTP)
3. **CLI** — terminal-based
4. **API** — direct HTTP calls
5. **x402 Payments** — pay with crypto wallet (USDC) via x402 protocol instead of prepaid balance

## Becoming a Tool Provider
Monid has a "Become a tool provider" program:
- **Apply:** https://forms.gle/NLPchCCwnTP6zQhV8
- They route agent traffic to your API, meter every call, share revenue
- No per-tool sign-ups for users, no subscriptions

## Why This Matters for GenTech

### As a Consumer
- Context.dev (web scraping) is a Firecrawl replacement — pay-per-call, no credits to exhaust
- Already lists Blockrun — they're in our ecosystem
- Could replace or supplement Agent Reach for certain data sources

### As a Provider
- Our x402 gateway services (yield data, arb monitor, narrative scanner) could be listed in their 1,300+ tool catalog
- Agents using Monid would discover and pay for GenTech's DeFi intelligence automatically
- They already support x402 — our gateway speaks the same protocol
- Revenue share model — we get paid when agents use our tools

## API Reference
- **Base URL:** `https://api.monid.ai`
- **Discover:** `POST /v1/discover` with `{query, limit}`
- **Run:** `POST /v1/run` with tool selection + input
- **Auth:** Bearer token from app.monid.ai

## Competitive Landscape
| Feature | Monid | Agent Reach | PayAI |
|---------|-------|-------------|-------|
| Tool count | 1,300+ | 60K⭐ (scraping) | 21K services |
| Payment model | Pay-per-call | Free (MIT) | x402 |
| Agent frameworks | Claude, Codex, Cursor, Hermes | CLI-based | MCP |
| Provider listing | Google Form | N/A | Bazaar marketplace |

## Next Steps
1. Sign up at app.monid.ai for $1 free credit
2. Test Context.dev for web scraping (Firecrawl replacement)
3. Apply as tool provider via Google Form
4. List our x402 endpoints in their catalog
