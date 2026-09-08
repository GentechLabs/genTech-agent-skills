# July 2026 — Agent Economy Ecosystem Developments

> New platforms, peers, and infrastructure discovered in the first half of July 2026. Add to `agent-marketplace-integration` for marketplace positioning.

---

## 1. After-Hours Oracle — Peer x402 Endpoint

**URL:** https://afterhoursoracle.xyz/
**Type:** Independent x402 data feed
**Status:** Live, generating real revenue

### What It Does
Sells after-hours stock price data via x402. Payments in USDC (Base) or USDG (Robinhood Chain). Also supports MPP (Stripe/Tempo Machine Payments Protocol).

### Live Metrics
- **Quotes sold:** 30
- **Earned:** $1.50
- **Price per quote:** $0.05
- **Tickers:** NVDA, AAPL, AMD, SNDK, MU, QQQ

### Key Technical Details
- **Self-hosted x402 facilitator** — sponsors gas on both Base and Robinhood Chain
- **Dual protocol:** x402 + MPP — one endpoint, two agent-payment standards
- **Signal-only vs buyable:** Some tickers have price data but no liquid buy route
- **Fee tier:** 5% on stock/ETH pools

### Why It Matters
This is a direct peer — they're doing exactly what we proposed for multi-asset rotation. Proof that the model works: $1.50 in revenue from 30 quotes. They also validate Robinhood Chain + USDG as a payment rail alongside Base USDC.

### Key Takeaway
After-Hours Oracle proves the x402 data-feed model generates real revenue, even at small scale. The dual-protocol approach (x402 + MPP) is worth watching — if MPP gains traction, we should support it too.

---

## 2. VibeKit — Algorand Agent CLI

**URL:** https://getvibekit.ai
**GitHub:** `gabrielkuettel/vibekit`
**Type:** Algorand agent development CLI
**Version:** v0.1.8 (as of Jul 2026)

### What It Does
CLI tool for building on Algorand through AI agents. Creates accounts, deploys contracts, queries the chain — all via MCP.

### Key Features
- **MCP server** — agents can interact with Algorand via standard MCP protocol
- **Account management** — create, fund, list, rekey accounts
- **HashiCorp Vault integration** — secrets management for agent keys
- **TestNet dispenser** — get test ALGO for development
- **Docker-based LocalNet** — local Algorand sandbox for testing

### Installation
```bash
curl -fsSL https://getvibekit.ai/install | sh
# Requires: AlgoKit CLI (pip install algokit)
# Then: vibekit init → vibekit mcp
```

### Prerequisites
- Docker (for LocalNet)
- AlgoKit CLI (`pip install algokit`)
- Node.js (for MCP server)

### Why It Matters
VibeKit is the official Algorand agent development toolkit for the Global x402 Challenge. It's how builders deploy x402 endpoints on Algorand. Our Agent Kit can integrate with VibeKit's MCP server to add Algorand support.

### Key Takeaway
VibeKit + GoPlausible + Algorand x402 Challenge = the full Algorand agent stack. VibeKit handles chain ops, GoPlausible handles payments, and the Challenge provides the prize pool.

---

## 3. Circle Agent Stack — Starter Kits

**URL:** https://github.com/circlefin/agent-stack-starter-kits
**Type:** Open-source starter kits for Circle Agent Stack
**License:** Apache 2.0
**Age:** 2 days old (Jul 7, 2026)

### What It Is
Circle (USDC issuer) released starter kits that wire their Agent Stack into popular AI agent frameworks:
- **LangChain** Deep Agents
- **Claude Agent SDK**
- **OpenAI Agents SDK**
- **Vercel AI SDK**
- **Google ADK**

### The Flow
1. Bootstrap with Circle Agent Skill + CLI
2. Create a wallet (agent wallet)
3. Fund it with USDC
4. Discover services on Circle Agent Marketplace (`agents.circle.com`)
5. Pay for them via agent nanopayments (x402)

### Key Components
- **Circle CLI** — `circle login`, `circle wallet create`, `circle wallet fund`
- **Circle Agent Skill** — installed via `npx skills add`
- **Agent Wallets** — gasless USDC across chains
- **Agent Nanopayments** — `@circle-fin/x402-batching` SDK
- **Agent Marketplace** — `agents.circle.com/services` — 41 services, 640 endpoints

### Why It Matters
This is the first time a major fintech company (Circle, $USDC issuer) has released production agent tooling. It validates the entire x402/agent-economy thesis. More importantly, it's a distribution channel — our services can be listed on their marketplace and discovered by agents using their SDK.

### Key Takeaway
Circle made it easy for any agent framework to discover and pay for x402 services. This is net positive for us — more agents with USDC wallets means more potential buyers for our services.

---

## 4. Circle Agent Marketplace — Updated Stats

**URL:** https://agents.circle.com/services
**Type:** Curated service catalog for AI agents
**Status:** Live, actively onboarding sellers

### Service Categories
| Category | Count | Examples |
|----------|-------|---------|
| Creative | 3 | AgentMail, StableDomains, StableEmail |
| Financial Analysis | 5 | Arrays, CoinGecko, Messari, Surf, vaults.fyi |
| Infrastructure | 4 | Alchemy, BlockRun, QuickNode, Modal Sandbox |
| Prediction Markets | 2 | Kalshi, Polymarket |
| Social Intelligence | 3 | Reddit, Twitter (X), YouTube |
| Web Search Research | 5 | Exa, Firecrawl, Parallel, Perplexity, Tavily |
| Other | 19 | Bland.ai, Clado, dFlow, DripStack, EMC2 AI, etc. |

### Marketplace Stats
- **Total services:** 41
- **Total endpoints:** 640
- **1P (first-party):** 19 providers
- **3P (third-party):** 22 providers
- **Pricing:** x402 nanopayments, $0.001-$0.05 per call

### Seller Application
- **Form:** https://forms.gle/7YFzvdmMcn1JH5tF6 (Google sign-in required)
- **SDK:** `@circle-fin/x402-batching` server middleware
- **Docs:** https://developers.circle.com/gateway/nanopayments/quickstarts/seller

### Competitive Gap
**0 merchants on Base mainnet** as of Jul 2026. All existing services are on Algorand. This is a first-mover opportunity for anyone listing on Base.

---

## 5. GoPlausible Facilitator — Bazaar Stats

**URL:** https://facilitator.goplausible.xyz/docs
**Type:** x402 payment facilitator with Bazaar discovery
**License:** Apache 2.0

### Bazaar Stats (as of Jul 2026)
| Metric | Value |
|--------|-------|
| Resources cataloged | 41 |
| Merchants listed | 12 |
| Facilitators | 1 (GoPlausible) |
| Base mainnet merchants | 0 |
| Verifications last 24h | 32 |
| Settlements last 24h | 30 |

### Supported Networks
- **x402 v2:** eip155:8453 (Base), solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp, algorand mainnet
- **x402 v1:** base, solana, algorand (legacy naming)
- **Gasless:** Facilitator pays network fees (feePayer addresses provided)

### Key Endpoints
```bash
GET /discovery/all        # Aggregated discovery data
GET /discovery/resources  # List cataloged resources
GET /discovery/merchants  # List merchants
GET /verify              # Verify x402 payment
GET /settle             # Settle verified payment
```

### Why It Matters
The Algorand Global x402 Challenge requires all payments to route through GoPlausible for leaderboard tracking. It's the competition's official facilitator. Resources auto-discover when payment verifications happen — no manual listing needed.

### Key Takeaway
GoPlausible is the mandatory payment rail for the $100K USD + 500K ALGO challenge. Understanding their Bazaar discovery system is table stakes for the competition.

---

## 6. Robinhood Chain — New Payment Rail

**URL:** https://robinhood.com/chain (inferred)
**Type:** EVM-compatible L2 chain by Robinhood
**Token:** USDG (Paxos Global Dollar, regulated stablecoin)

### Why It Matters
After-Hours Oracle accepts USDG on Robinhood Chain alongside USDC on Base. This is the first real-world example of multi-asset x402 payments. If Robinhood Chain gains traction, supporting USDG could be a distribution advantage.

### Chain Details
- **CAIP-2:** `eip155:4663` (Robinhood Chain)
- **Token:** USDG (6 decimals, regulated by NYDFS)
- **x402 v2:** Supported via GoPlausible and After-Hours Oracle's self-hosted facilitator

### Key Takeaway
Robinhood Chain + USDG is a new payment rail for x402. It's early but worth monitoring — if Robinhood's user base starts using it for agent payments, it could be a significant distribution channel.