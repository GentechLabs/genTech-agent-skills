# x402 Foundation — Ecosystem Overview

**Date:** 2026-07-19
**Source:** x402.org, Cloudflare blog, GitHub, YouTube analysis
**Reference for:** ecosystem-intelligence skill

## Structure
- Official **Linux Foundation** project (LF Projects, LLC)
- Open standard for internet-native payments
- Zero protocol fees, zero wait, zero friction, zero centralization, zero restrictions
- HTTP-native — payment embedded in existing request/response cycle

## Members (40+ orgs at operational launch)
**Premier:** Coinbase, Ripple
**General:** Cloudflare, NEAR, Quant, AWS, Amex, Mastercard, Stripe, Visa, Circle, Google, Shopify, Solana Foundation, Stellar, Adyen, Fiserv, Monad, MoonPay
**Ecosystem:** Nansen, Alchemy, Messari, QuickNode, Vercel, World

## Key Stats (30 days)
- 75.41M transactions
- $24.24M volume
- 94.06K buyers
- 22K sellers

## Core Repo
- `github.com/x402-foundation/x402` — 6.4k⭐, 1.8k forks, 309 contributors
- Languages: TypeScript (41%), Python (33%), Go (25%), Solidity, JS, Java
- Has `.agents/skills` directory — skill-based integrations
- 895 dependents

## Key Players

### Cloudflare
- Agents SDK has `withX402()` for MCP tool payment gating
- Proposed "deferred" payment scheme for batch/delayed settlement
- X402 playground at playground.x402.cloudflare.com
- Pay-per-crawl private beta
- Jordan already on Gateway waitlist, has DNS via Cloudflare

### Ripple / XRPL
- XRPL AI Starter Kit (Jun 9, 2026) — x402-powered payments via XRP + RLUSD
- XRPL Agent Wallet Skill + XRPL Payments Skill for Claude
- XRPL is supported x402 chain (via t54.ai contribution)
- Deterministic finality (3-5s), predictable costs, native DEX
- RLUSD = regulated stablecoin, enterprise-grade
- 14 years of secure operation, no smart contract risk
- Repos: XRPLF/xrpl-dev-portal (skills), xrpl.org docs

### NEAR
- Settlement layer for agentic AI
- $38.4M revenue, trending deflationary
- NEAR Intents for agent settlement
- AI co-founder (co-authored "Attention is All You Need")

### Quant
- Overledger API — connects 30+ platforms
- "Internet of Trust" — conduit between all payment networks
- Connects to Alibaba Cloud, AWS, Azure, OpenAI, Slack, etc.

## Integration Opportunities for GenTech
1. **Contribute to x402 core repo** — Add x402 agent patterns based on our production gateway
2. **Port x402 gateway to XRPL** — Support XRP and RLUSD settlement
3. **Join foundation Slack** (slack.x402.org) — Network with 40+ member orgs
4. **Cloudflare Gateway beta** — Deploy x402 gateway on Cloudflare Workers

## Relevant Links
- x402.org — Official site
- github.com/x402-foundation/x402 — Core protocol
- blog.cloudflare.com/x402/ — Cloudflare launch blog
- ripple.com/insights/xrpl-ai-starter-kit/ — Ripple AI Starter Kit
- xrpl.org/docs/agents/getting-started-with-agentic-transactions — XRPL x402 tutorial
