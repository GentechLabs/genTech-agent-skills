# Agent Marketplace Revenue Listing Map

> Compiled Aug 9, 2026 — every platform GenTech can list on to drive traffic and revenue.

## Already Listed (revenue incoming)

| Platform | Status | Revenue Model | Action Needed |
|----------|--------|---------------|---------------|
| **OKX.AI** | 4 agents under review | $0.30-0.50/call (A2MCP + A2A) | Monitor for approval; daemon must stay healthy |
| **Agentic.Market** | Auto-indexed via Bazaar extension | Discovery → traffic | None — auto |
| **Hive** | Registered | Agent task bounties | Update services list |
| **x402-list.com** | Listed | Agent directory traffic | Verify listing is current |

## Registered, Needs Listing Update (30 min each)

| Platform | What We Have | What's Needed |
|----------|-------------|---------------|
| **Atelier** | Agent ID `ext_1783295225717_09ms3exvh`, API key `atelier_ebab...` | Update listing with x402 endpoints + pricing |
| **Swarms** | Listed as `gentech/agent-discovery` | Add x402 pricing tiers + new service endpoints |
| **AgentScan** | Profile live, metadata v1.3.0, 7 endpoints indexed | Verify auto-indexing, add any missing endpoints |

## High Priority — Not Listed Yet (biggest revenue upside)

| Platform | Time to List | Why It Matters | How |
|----------|-------------|----------------|-----|
| **x402scan** | Auto-indexes from `/openapi.json` | Largest x402 discovery engine — agents search here first | Ensure OpenAPI spec has `x-x402` extension |
| **OpenDexter** | 30 min | x402 marketplace MCP — agents discover AND pay through it | Register services via MCP tools |
| **pay-skills registry** | 1 hr (PR) | Solana Foundation — agents discover paid skills on Solana | Submit PAY.md PR to `solana-foundation/pay-skills` |
| **Wurk.fun** | 1 hr | Agent-to-human microtask marketplace — direct bounties | Register agent profile + services |
| **earn.fi** | 1 hr | Agent economy platform — earn per completed task | List agent + services |

## Secondary Priority

| Platform | Time | Notes |
|----------|------|-------|
| **EvoMap** | 30 min | GenTech marketplace — list SDK, gateway, agent services as assets |
| **Monid** | 30 min | Agent directory — profile + service listing |
| **Syra** | 30 min | Agent directory — profile + service listing |
| **Brickken ERC-8004** | 1 hr | On-chain agent identity registration — prerequisite for many marketplaces |

## What We're Listing

| Asset | Description | Pricing | URL |
|-------|-------------|---------|-----|
| **x402 Gateway** | 7 pay-per-call API endpoints (token security, wallet analysis, DeFi LP, agent discovery, market intel, NFT search, treasury defense) | $0.001-0.05/call | `api.gentechlabs.net` |
| **ArcAgentWallet** | Autonomous AI agent wallet SDK on Arc — 3 lines to add payments | Open source (MIT) | `github.com/Gentech-Labs/programmable-money-x402` |
| **OKX Agent Services** | Yield Signal Scanner, LP Shape Detector, Auto-Rebalancing Strategy | $0.30-0.50/call | OKX.AI marketplace |
| **Arc x402 Playground** | Interactive demo of programmable money flow | Free | `demo.gentechlabs.net/arc/` |

## Quick Submission Checklist

Before submitting to any platform:
- [ ] OpenAPI spec live at `/openapi.json` with `x-x402` extension
- [ ] `/.well-known/x402` discovery endpoint returns valid v2 manifest
- [ ] `/.well-known/x402-bazaar` lists all services with pricing
- [ ] `/health` endpoint returns 200
- [ ] CORS enabled (allow all origins for discovery)
- [ ] Code examples in Python, TypeScript, and curl in docs

## Post-Listing Monitoring

After each listing:
- Track referrer in gateway logs → which platform sends traffic
- Monitor conversion: visits → API calls → paid calls
- First 7 days are highest signal — platforms boost new listings
