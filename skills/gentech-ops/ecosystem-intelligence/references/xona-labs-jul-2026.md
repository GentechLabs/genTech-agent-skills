# Xona Labs / xPay — Codebase Analysis (Jul 29, 2026)

**Repo:** github.com/xona-labs/xpay
**npm:** @xona-labs/xpay v0.2.22
**License:** MIT
**Stars:** 1 (early stage)
**Commits:** 83

## What It Is

Agentic-commerce wallet for Solana. Multi-network USDC wallet, x402 payments, AgenC marketplace hires, and discovery across 20,000+ services — as a CLI, SDK, and MCP server.

## Stack

- **Privy custody** — wallet management
- **x402 payment rails** — same protocol GenTech uses
- **PayAI discovery** — 21K service catalog
- **AgenC marketplace** — hire on-chain agents via SOL escrow
- **Jupiter swaps** — token swapping inside the wallet
- **Token discovery** — find any Solana token by ticker or mint
- **Balance reports** — daily/weekly/monthly via OrbitX402

## Discovery Mechanism (How Agents Find Services)

The `xpay_discover` tool pulls from two sources:

1. **OrbitX402** (api.orbitx402.com) — aggregates its own probed resources + PayAI catalog + pay.sh catalog. Server-side search and ranking. Returns ~50KB of ranked results instead of multi-MB catalog download.

2. **AgenC** (agenc.ag) — on-chain agent services priced in SOL, executed as escrow hires. Small catalog, fetched whole and filtered locally.

One source failing never kills discovery — errors are stashed in `lastDiscoverWarnings()` and the other source's results are returned.

## How Payment Works

Services price calls in USDC over x402 (fractions of a cent to a few cents per call). `xpay_use` / `xpay_do` settle the payment and call the service in one round-trip. A small platform fee ($0.01 USDC) applies per paid call.

When a service accepts more than one network (e.g. Base AND Solana), xPay routes automatically to a funded network — pays from the first one whose balance covers the cost.

## Key Source Files Analyzed

| File | Purpose |
|------|---------|
| `src/discover/index.ts` | Discovery orchestration — merges OrbitX402 + AgenC results, local filtering, network matching |
| `src/discover/orbitx402.ts` | OrbitX402 client — paginated fetch from api.orbitx402.com |
| `src/x402/evm-payment.ts` | EIP-3009 gasless payment header builder (EVM chains) |
| `src/tools/index.ts` | Claude tool definitions — 20+ tools (discover, use, do, transfer, balance, swap, etc.) |
| `SKILL.md` | MCP server documentation — zero-config setup, tool reference, payment flow |

## How GenTech Gets Listed

**Path 1 — PayAI Bazaar (easiest):**
PayAI has a Bazaar marketplace at facilitator.payai.network with a `/discovery/resources` endpoint. Register our x402 endpoints there. They automatically flow into OrbitX402 → xPay discovery.

**Path 2 — x402-list.com:**
Web form at x402-list.com/submit. Auto-probes for HTTP 402, then manual review. Already submitted Jul 29 (pending review).

**Path 3 — Direct Xona outreach:**
Once we're in the catalogs, reach out to Xona Labs to let them know.

## What We'd List

| Service | Endpoint | Price |
|---------|----------|-------|
| Token Security Score | api.gentechlabs.net/v1/security/score | $0.01 |
| Wallet Portfolio | api.gentechlabs.net/v1/wallet/portfolio | $0.02 |
| Agent Discovery | api.gentechlabs.net/v1/agents/search | $0.01 |
| Market Intelligence | api.gentechlabs.net/v1/market/price | $0.005 |
| DeFi LP Analytics | api.gentechlabs.net/v1/defi/lp | $0.02 |
| NFT Search | api.gentechlabs.net/v1/nft/search | $0.01 |

## GenTech vs Xona — Complementary, Not Competitive

| Dimension | GenTech | Xona |
|-----------|---------|------|
| Focus | DeFi yield / treasury management | E-commerce / service discovery |
| Primary chain | Multi-chain (Base, Avalanche, Solana) | Solana-first |
| Payment protocol | x402 | x402 (same!) |
| Distribution | Self-hosted gateway | xPay MCP + CLI + SDK |
| Service catalog | 6 DeFi/security APIs | 21K+ services via PayAI |
| Wallet model | Self-custody via Q402/BlockRun | Privy custody |

**Integration is straightforward** — both use x402. List our endpoints in their discovery catalog, and any agent using xPay can find and pay for GenTech's DeFi intelligence.
