# Agentic Treasury — Cross-Chain Capital Routing Agent

**Named:** July 18, 2026 — Jordan coined "Agentic Treasury"
**Full spec:** `00-HQ/agentic-treasury-spec.md`
**For:** Arc Programmable Money Hackathon + Circle Developer Grant

**Product class:** An autonomous agent that manages capital across chains — holding dry powder (USDC), routing payments via cheapest chain, deploying surplus to yield or spot, redistributing when conditions change.

## Core Concept

```
User gives agent: wallet addresses + desired chains (Base, Solana, AVAX, Arc)
         ↓
Agent holds capital in DRY POWDER (USDC yielding position)
         ↓
Monitors entry conditions across chains
         ↓
Routes payments via cheapest settlement chain
         ↓
Deploys surplus to yield pools or spot buys
         ↓
Reacts to stop-loss / take-profit triggers
         ↓
Routes capital back to dry powder or new position
         ↓
Cycle repeats autonomously
```

## Three Pillars

### 1. Yield Brain (ex-AAE)
- Auto-detects best yield pools across chains
- Holds dry powder in USDC until conditions align
- Stop-loss triggers: if pool APY drops below threshold, pull and redistribute
- Rebalances across Base, Solana, AVAX, Arc

### 2. Payment Router (x402 Mesh)
- Routes agent API payments to cheapest chain
- Arc = ultimate settlement layer ($0.001 USDC gas)
- Agents don't care which chain — router decides
- Aggregates small payments into batch settlements

### 3. P2P Causes (Social Capital)
- Users create a cause: story + photos + funding goal
- **GenTech Hub generates posters/banners/flyers** from user-provided data
- Anyone can browse, rate, fund
- Agents can auto-fund based on reputation scores
- Trust graph: wallet history, ratings, past distributions
- Same infra as prediction markets — betting on *people* not *events*
- Queued as build item #56: GenTech Hub P2P Causes + Flyer Factory

## Where It Fits in Our Stack

| Component | Existing Asset | New for Agentic Treasury |
|-----------|---------------|--------------------------|
| x402 payments | ✅ API Safety Suite, 15 endpoints | Multi-chain routing logic |
| DeFi yield analysis | ✅ Strategies knowledge, LP analysis | Autonomous deployment |
| Stop-loss triggers | ✅ LP Tactical Retreat (Phase 1 built) | Agent-managed exit conditions |
| P2P funding layer | 🏗️ GenTech Hub Flyer Factory (#56) | User creates cause → agents/lenders fund |
| Arc integration | 🏗️ Arc x402 Gateway (#63) | First x402 gateway on Arc |
| Lens AI data source | 🏗️ Lens AI Integration (#64) | Get paid for citations |
| Agentic Treasury as product | 🏗️ Arc Hackathon (#65) | Umbrella for all of the above |

## Why Arc

- **USDC as native gas** — $0.001/tx, no volatility risk
- **Programmable Money Hackathon** — Encode Club, started Jul 13, 7 weeks left
- **Lens AI** — ERC-8004 agent #842439, ALREADY supports x402
- **First x402 on Arc** — zero competitors
- **Circle Grant #1 focus** — "Agentic economic activity"
- **302 projects** on Arc ecosystem — ready distribution surface

## Build Queue Items

- #56: GenTech Hub P2P Causes + Flyer Factory
- #63: Arc x402 Gateway — deploy first endpoint on Arc testnet
- #64: Lens AI Integration — register as verified data source
- #65: Arc Programmable Money Hackathon submission — Agentic Treasury MVP
- #66: Circle Developer Grant application — tiered USDC funding
