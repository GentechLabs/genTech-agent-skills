# x402 Ecosystem Landscape (May 20, 2026)

## Payment Modes

### Vanilla x402 (`exact` scheme)
- **Model:** Push-only, pay-first. Buyer pays, payment is final on delivery.
- **Use case:** Micropayments, API calls, data access, compute — low-trust, instant delivery.
- **Key players:** Coinbase (protocol maintainer), Ampersend (agent payment layer), Vercel, Cloudflare, Google A2A.
- **Adoption:** 6,000+ GitHub stars, Linux Foundation x402 series.

### x402B (`escrow` scheme)
- **Model:** Non-custodial escrow. Funds enter Boson Diamond escrow at commit time; release after buyer signals delivery or dispute window expires. Third-party dispute resolvers can split funds and slash seller bonds.
- **Use case:** High-value transactions, deferred delivery, physical goods, pseudonymous sellers.
- **Key player:** Boson Protocol (8-year-old, $30M+ raised, WEF Technology Pioneer).
- **Repos:** `bosonprotocol/x402B` (reference implementation), `bosonprotocol/x402-escrow-schema` (spec).
- **Status:** Testnet live on Base Sepolia; mainnet audit on separate cadence.
- **Compatibility:** Drop-in — x402 servers add `"escrow"` to `accepts[]` alongside `"exact"`. Vanilla x402 clients fail safely (unsupported scheme error).
- **Open standard:** Contributed to Linux Foundation x402 series.

## Boson x402B Package Map

All packages publish under `@bosonprotocol/`:

| Package | Purpose |
|---|---|
| `@bosonprotocol/x402-core` | Escrow scheme JSON schemas, TS types, EIP-712 builders, exchange state machine |
| `@bosonprotocol/x402-evm` | EVM implementation — calldata builders for commit/redeem, meta-tx envelope |
| `@bosonprotocol/x402-server` | Framework-agnostic resource server (Express adapter: `x402-server-express`) |
| `@bosonprotocol/x402-client` | Framework-agnostic client (fetch adapter: `x402-client-fetch`) |
| `@bosonprotocol/x402-facilitator` | Reference verify + settle service (Express adapter: `x402-facilitator-express`) |
| `@bosonprotocol/x402-fulfillment` | Pluggable fulfillment channels: atomic, email, XMTP, webhook, IPFS-pointer |
| `@bosonprotocol/x402-actions` | Channel registry, nextActions envelope builder, state-machine transitions |

## Circle Gateway Nanopayments

Circle Gateway adds **batched settlement** to x402, making sub-cent payments economically viable.

- **Model:** Buyers sign offchain payment authorizations (zero gas). Gateway batches thousands into a single onchain settlement.
- **Seller SDK:** `@circle-fin/x402-batching` — Express middleware (`createGatewayMiddleware`) + direct `BatchFacilitatorClient`
- **Open alternative:** `@x402/express` — open-source Express middleware with `paymentMiddleware()`, uses `https://facilitator.x402.org`

## Stripe Link CLI (buyer-side, Aug 23 2026)

Stripe's official **buyer-side agentic-commerce** tool. Lets an agent get **one-time-use payment credentials** from a Link wallet to spend on your behalf — real card never exposed, **you approve every purchase** (push → approve/deny).

- **Two credential types:**
  - **Virtual card (PAN)** — works at any web checkout, not just Stripe sellers
  - **Shared Payment Token (SPT)** — for sellers accepting **MPP** (Machine Payments Protocol, HTTP 402)
- **MPP-native:** SPT works with MPP sellers — including our own gateway (we ship MPP dual-rail #47). A Stripe Link agent could pay our gateway via MPP.
- **Install:** `npm i -g @stripe/link-cli` or `npx @stripe/link-cli`; skill via `npx skills add stripe/link-cli`; MCP server via `--mcp` or `serve` (HTTP).
- **Approval model:** `--request-approval` → push to user, polls until approved/denied. The "human approves every spend / no blank check" pattern (same as OpenAI×AWS AgentCore).
- **Caveats:** US Link accounts only for now; buyer tool (lets agents spend), not a revenue tool — complements, doesn't replace, our seller-side gateway.
- **Status:** Installed into Hermes (gentech profile) as `create-payment-credential` + `financial-insights` skills (Aug 23 2026).
- **Key benefit:** Gas-free for both parties, sub-cent minimums ($0.000001), crosschain withdrawal for sellers
- **Testnet:** Arc Testnet (chain ID 5042002), `https://gateway-api-testnet.circle.com`
- **Production:** `https://gateway-api.circle.com`
- **Payment validity:** Signatures require 7+ days validity window or Gateway rejects

## Live x402 Ecosystem Signals (May 2026)

The x402 agent economy moved from theory to production in May 2026. Here's what's shipping:

### Hyre Agent — Revenue Flywheel in Production
- **#3 on x402 by volume (24h):** 3,600 settlements, 150 buyers, $163 volume
- **Token buyback loop:** Used revenue to buy back 1M $HYRE tokens
- **Pattern:** Agents earn → revenue flows → tokens get bought back → supply shrinks
- **Significance:** First live proof that autonomous agents can earn real money and deploy it on-chain without human intervention

### AgentLayer — x402 Wallet Integration (Solana + Base)
- **Integration:** x402 payments built directly into AgentLayer wallet
- **Features:** Agents discover paid services automatically, pay from Solana + Base wallets with near-zero USDC fees
- **Impact:** Agents become real economic actors — not just consumers of data, but autonomous buyers and sellers
- **No extra setup:** APIs work with x402 out of the box

### Circle Arc Testnet — API Storefronts
- **What:** Circle published walkthrough for turning any API into an agent-accessible paid service using x402 + USDC nanopayments on Arc Testnet
- **Seller flow:** Publish paid endpoint → Accept USDC from agents automatically → Track revenue in Gateway Balance → Withdraw to payout wallet
- **Relevance:** Most production-ready path for charging for API access (e.g., Aegis risk reports, LP Monitor alerts)

### Swarms Marketplace — x402 Filter Category
- **Feature:** Swarms Marketplace has an `x402` filter button for agents/prompts
- **Significance:** x402 is becoming a discoverability filter — agents that accept x402 payments are categorized separately
- **Categories on marketplace:** All, Non x402, x402, Healthcare, Education, Finance, Research, Public Safety, Marketing, Sales, Customer Support, Other
- **Agent types:** AGENT (executable) and PROMPT (behavior definition)
- **Vendor flow:** "Become a Vendor" page → "List your agent" → fast publishing, revenue generation, discovery and accessibility

## Competitive Landscape

| Project | Focus | Chain(s) | Notes |
|---|---|---|---|
| **Circle Gateway** | Batched x402 settlement, seller middleware | Multi-chain | Our new seller-side integration. Gas-free, sub-cent. |
| **Ampersend** | Agent x402 payments, MCP proxy | Base | Our buyer-side integration. Push-only, no escrow. |
| **pay.sh** | x402/MPP payments, CLI + MCP | Solana | Our buyer-side integration. Local wallet approval. |
| **Boson (x402B)** | Escrow + disputes + fulfillment | Base (testnet), multi-chain planned | Protocol-level standard. Linux Foundation. |
| **UltravioletaDAO** | AI↔human task marketplace, escrow | 9 chains (incl. Base) | Live. ERC-8004 registry. |
| **MCPay** | x402 + MCP tool monetization | Solana | $25K stablecoins. |
| **CORBITS** | x402 API proxy + merchant dashboard | Solana | $20K infra. |
| **PayAI** | Protocol-agnostic seller middleware (x402 + MPP) | 7 EVM testnets + Solana | Express middleware, dynamic pricing, lifecycle hooks. Best for Agent Arena. |
| **Private-Escrow x402** | Progressive escrow schemes | ETHGlobal showcase | Privacy-focused. |
| **Hyre** | Autonomous agent earning + token buybacks | Multi-chain | **Live revenue: $163/24h, 3.6K settlements** |
| **AgentLayer** | x402 wallet integration for agents | Solana, Base | Agents auto-discover and pay for services |

## Our x402 Stack (Complete)

| Side | Tool | Chain | Role |
|------|------|-------|------|
| Buyer | Ampersend | Base | Our agents **paying** for APIs |
| Buyer | pay.sh | Solana | Our agents **paying** for APIs |
| Buyer | Circle Gateway Client | Multi-chain | Our agents **paying** with batched settlement |
| **Seller** | **PayAI** | **Multi-chain (x402 + MPP)** | **Protocol-agnostic seller middleware. AAE marketplace.** |
| Seller | Circle Gateway | Multi-chain | **Our endpoints **charging** for access** |
| Seller | @x402/express | EVM | Open-source alternative seller middleware |
| Escrow | x402B (Boson) | Base | High-value, deferred delivery, disputes |

## Our Positioning

- **AgentEscrow.sol** — Custom Solidity escrow (Kite AI testnet). Still works for non-x402 use cases but **superseded by x402B for x402-native commerce**.
- **Ampersend integration** — Handles x402 push payments for agent API/compute spending. Complementary to x402B, not competing.
- **Circle nanopayments** — Seller-side payment walls on our Express endpoints. Completes the buyer→seller loop.
- **Strategic shift:** Build ON TOP of x402B for escrow flows, not parallel escrow contracts. Use Circle Gateway for high-frequency micropayments. Focus on application layer: agent workflows, UX, integrations.

## Key Dates

- May 9, 2026: Boson publishes "x402B finds Agent Market Fit"
- May 16, 2026: x402B repo at 285 commits, 13 branches, 3 PRs open — active development
- May 20, 2026: Hyre live revenue ($163/24h), AgentLayer x402 wallet, Circle API storefronts, Swarms x402 filter
- Mainnet audit timeline: TBD
