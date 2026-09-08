# Atelier Research — Market Intelligence & Integration

**Research Date**: July 4, 2026
**Status**: Live Marketplace — Distribution Opportunity

---

## Executive Summary

Atelier is a live AI agent marketplace (useatelier.ai) with $ATELIER token on Solana. Instead of head-on competition, we leverage their traffic for distribution while building our superior infra (x402 + MCP + taste signals).

---

## Marketplace Snapshot

### Core Features
- **Positioning**: "Hire an AI agent for any kind of work"
- **Value prop**: 10× cheaper, 10× faster than human freelancers
- **Categories**: Image, video, code, research, trading, ops
- **Token**: $ATELIER on Solana

### Live Infrastructure
- Agent marketplace with search/browse
- Job posting system ("Post a Job")
- Skill tags and discovery (meme generator, code review, SEO audit, UGC video, logo design, trading bot)
- API Docs, Litepaper, Launchpad, Bounties
- USDC earning mechanisms for idle funds on Solana

---

## Competitive Gap Analysis

| Feature | Atelier | Gentech | The Gap |
|---|---|---|---|
| **x402 payments** | Not visible | ✅ Gateway live (Cloudflare) | We have payment rails they don't |
| **MCP/Tool Manifest** | Unknown (likely walled) | ✅ GOAT patterns documented | Universal agent discovery |
| **Universal search** | Walled garden | ✅ AgentKit + BlockRun | Cross-platform tooling |
| **Revenue model** | Unknown | ✅ Cloudflare + APIs ready | Clear monetization path |
| **Taste-driven curation** | Basic marketplace | ✅ Renaiss + collector economy | Taste signals as ranking |

---

## Integration Strategy: 3-Phase Rollout

### Phase 1: Piggyback (Short-term, this week)
**Goal**: Get free distribution, learn their patterns, establish presence

**Actions**:
1. Study Atelier's agent listing format and job posting flow
2. Submit 1-2 GenTech agents as premium listings
3. Reference in OKX hackathon submission as "existing market we're upgrading"

**Why**:
- Validate agent marketplace model exists
- Get free traffic without building own marketplace
- Learn from their user behavior patterns

### Phase 2: Upgrade (Mid-term, next 2 weeks)
**Goal**: Make their ecosystem better with our infra

**Actions**:
4. Build x402 payment wrapper for Atelier agents → instant agent-to-agent payments
5. Offer MCP integration to Atelier users → universal tool discovery across frameworks
6. Document the integration pattern for OKX submission

**Why**:
- Atelier agents become MORE valuable with our infra
- Establish ourselves as infra provider, not just another agent
- Test x402/MCP patterns in production before launching Agent Arena

### Phase 3: Compete (Long-term, after OKX)
**Goal**: Ship superior marketplace when infra pieces are ready

**Actions**:
6. Ship Agent Arena with x402 + taste signals → superior marketplace
7. Cross-list Atelier agents with Agent Arena for network effects
8. Position as "Atelier with real money payments + universal discovery"

**Why**:
- By the time Agent Arena ships, x402/MCP are battle-tested
- Taste-driven curation via Renaiss is a unique differentiator
- We can offer migration path for Atelier agents

---

## Strategic Rationale

### The "Eat the Meat, Spit out the Bones" Pattern

Atelier validates the agent marketplace model. We don't need to rebuild from scratch.

**What we take (meat)**:
- Agent marketplace is real demand
- User behavior patterns (what sells, what doesn't)
- Distribution channel for early agents

**What we ignore (bones)**:
- Walled garden approach
- Basic marketplace ranking
- Unknown revenue model

**What we add (upgrade)**:
- x402 payments → agents get paid instantly
- MCP integration → universal tool discovery
- Taste signals → community-driven ranking

### Modular Architecture Enables This

Because we built GenTech as modular layers:
- Payment rails (Q402) → replaceable
- Tool discovery (MCP) → replaceable  
- Curation (Renaiss taste signals) → replaceable

We can plug into Atelier now, unplug later when Agent Arena ships.

---

## Execution Plan

### Week 1 (Jul 4-11)
- [ ] Study Atelier's agent listing format and job posting flow
- [ ] Identify 1-2 GenTech agents best suited for Atelier (LP Shape Detector, DeFi Intelligence)
- [ ] Draft agent descriptions with x402 + MCP differentiation
- [ ] Reference in OKX hackathon submission

### Week 2-3 (Jul 12-25)
- [ ] Build x402 payment wrapper for Atelier agents
- [ ] Document MCP integration pattern for Atelier users
- [ ] Test end-to-end payments on Atelier platform
- [ ] Gather user feedback on payment/discovery pain points

### Post-OKX (after Jul 17)
- [ ] Ship Agent Arena with taste signals
- [ ] Cross-list Atelier agents for network effects
- [ ] Position as upgrade path for Atelier power users

---

## Integration Reference: OKX.AI

### Market Stats (as of Jul 2026)
- Total tasks completed: 1,030
- Tasks posted: 3,565
- Tasks open: 1,539
- Average price: 0.01-10 USDT
- Chain support: EVM (Ethereum, Base, Arbitrum, X Layer) + Solana

---

## Integration Reference: Q402 Escrow (QuackAI)

### Capabilities
- Gasless USDC/USDT escrow for AI agents
- Buyer signs once → Q402 relays → funds lock on-chain
- Release on approval, refund after timeout, dispute arbiter
- Under the hood: EIP-7702 delegated execution, EIP-712 signatures

### Installation
```bash
npm i @quackai/q402-mcp
```

---

## Links
- Atelier: https://useatelier.ai/
- $ATELIER on PumpFun: Linked from homepage
- OKX.AI: https://www.okx.ai/en
- Renaiss Discord: https://discord.com/invite/renaiss