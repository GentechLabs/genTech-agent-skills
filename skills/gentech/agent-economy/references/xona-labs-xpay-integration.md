# Xona Labs / xPay — Agent Commerce Wallet

**Researched:** Jul 29, 2026
**Status:** Complementary — not competitor. Potential collaborator.

## What They Are

**xPay** (`@xona-labs/xpay`) — "Agentic-commerce wallet" for Solana. Multi-network USDC wallet, x402 payments, and discovery across 20,000+ services. MIT licensed, 83 commits, 1 star, 0 forks — early stage.

**GitHub:** https://github.com/xona-labs/xpay
**Website:** https://xpay.xona-agent.com
**Docs:** https://xpay.xona-agent.com/docs
**X/Twitter:** @xona_agent

## Their Stack

| Component | Detail |
|-----------|--------|
| **Wallet** | Privy custody — auto-generated on first run, persists across restarts |
| **Payments** | x402 v2 (EIP-3009 gasless on EVM, SPL on Solana) |
| **Discovery** | OrbitX402 API (aggregates PayAI + pay.sh catalogs) |
| **Marketplace** | AgenC — hire on-chain agents via SOL escrow |
| **Swaps** | Jupiter integration (Solana only) |
| **CLI** | `xpay init`, `xpay discover`, `xpay pay`, `xpay swap`, `xpay transfer` |
| **MCP** | Full MCP server — 20+ tools for agents |
| **Networks** | Solana (primary), Base, Ethereum, Arbitrum, Optimism, Robinhood |

## Key Tools (from their MCP surface)

| Tool | What It Does | Price |
|------|-------------|-------|
| `xpay_discover` | Find paid services across 21k+ catalog | Free |
| `xpay_use` | Pay for and call a specific service | $0.01 platform fee |
| `xpay_do` | One-step discover + call | $0.01 platform fee |
| `xpay_transfer` | Send USDC/SPL tokens directly | Guardrail-gated |
| `xpay_swap` | Swap via Jupiter (Solana) | Guardrail-gated |
| `xpay_balance` | Wallet balance per network | Free |
| `xpay_report` | Spending/income report | Free |
| `xpay_x_user` | X/Twitter profile lookup | ~$0.01 (at cost) |
| `xpay_x_posts` | Recent X posts with engagement | ~$0.06 (at cost) |
| `xpay_shop_search` | Product search (Google/Amazon/eBay) | ~$0.02 |
| `xpay_token_find` | Find Solana tokens by ticker/mint | Free |
| `xpay_rwa_find` | List tradable RWA tokens on Solana | Free |
| `xpay_zauth_reposcan` | Repo security scan | ~$0.05 |

## How Discovery Works

xPay pulls from **OrbitX402** (`api.orbitx402.com`) which aggregates:
1. Its own probed resources
2. **PayAI catalog** (docs.payai.network)
3. **pay.sh catalog**

When an agent calls `xpay_discover "yield farm"`, it searches this combined catalog and returns ranked results. The agent then calls `xpay_use` with the resource, and xPay handles the x402 payment automatically.

## How We Get Listed

**Path 1 — PayAI Bazaar (fastest):**
Register our x402 endpoints with PayAI's facilitator at `facilitator.payai.network`. Their `/discovery/resources` endpoint feeds into OrbitX402 → xPay discovery automatically.

**Path 2 — x402-list.com:**
Submit at `x402-list.com/submit`. Already submitted (Jul 29, 2026) — pending review. **Pitfall:** Endpoint paths must NOT contain `{param}` curly braces.

**Path 3 — Direct outreach to Xona Labs:**
Once we're in the catalogs, reach out to @xona_agent about cross-promotion.

## Where We Fit Together

| GenTech | Xona Labs | Integration |
|---------|-----------|-------------|
| DeFi yield infrastructure | Wallet + commerce rail | Our yield data as x402-payable service in their catalog |
| GTA arbitrage detection | Service discovery (21k APIs) | GTA listed as discoverable service for xPay agents |
| Narrative rotation | Agent marketplace (AgenC) | Our intelligence feeds their commerce layer |
| x402 gateway (6 chains) | x402 payments (Solana + EVM) | Same protocol — no bridging needed |
| Treasury management | Spending/income reports | Agents earn with us, spend through them |

## Key Insight

Both on **x402** — same payment protocol means integration is straightforward. No bridging, no custom adapters. Just list our endpoints in their catalog.

They solve "how does an agent find and pay for things." We solve "how does an agent grow its treasury." A full agent economy needs both.

## Action Items

- [ ] Register on PayAI Bazaar (facilitator.payai.network)
- [ ] Monitor x402-list.com submission status
- [ ] Reach out to Xona Labs once listed
- [ ] Consider listing our DeFi Intelligence API as a discoverable service
