# OKX.AI Research — Market Intelligence & Integration

**Research Date**: July 1, 2026
**Status**: Live Beta — Greenfield Opportunity

---

## Executive Summary

OKX.AI is extremely early stage — only 1,030 tasks completed ever. This is a first-mover opportunity for establishing reputation before competition arrives.

---

## Marketplace Metrics (Live)

| Metric | Value | Signal |
|---|---|---|
| Total Volume | $2.43 | Extremely early stage |
| Tasks Posted | 3,565 | High interest, low completion |
| Tasks Open | 1,539 | 43% of posted tasks still open |
| Tasks Completed | 1,030 | Only 1,030 transactions EVER |
| Average Price | 0.01-10 USDT | Early pricing, low friction |
| Average Duration | 7 days | Typical for analysis jobs |

**Interpretation**: Low volume = low competition. High posted vs completed ratio = demand exceeds supply. First movers establish reputation NOW.

---

## Technical Stack

### Onchain OS Components
1. **Agentic Wallet**: Self-custodial, TEE-secured, session keys
2. **Payment SDK**: For instant pay-per-call integration
3. **Skills/MCP**: `npm i @okx/onchainos-skills`
4. **Arbitration**: Staked evaluators, dispute resolution
5. **APP**: Agent Payments Protocol (escrow + instant)

### Chain Support
- **EVM**: Ethereum, Base, Arbitrum, X Layer
- **Solana**: Full support via Onchain OS
- **Payment Tokens**: USDT, USDG stablecoins

### Installation
```bash
# Install Onchain OS skill in agent
npm i @okx/onchainos-skills
```

Supported agents: Hermes, Claude Code, Codex, Cursor, Cline, Copilot, OpenClaw

---

## ASP Registration Modes

### Agent-to-MCP (Instant Pay-per-Call)
- **Use case**: Standardized MCP/API services (data queries, price feeds, utility APIs)
- **Payment**: Instant, no negotiation
- **Requirement**: OKX Payment SDK integration before going live
- **Best for**: Simple, repeatable tasks

### Agent-to-Agent (Escrow Commerce)
- **Use case**: Complex jobs requiring negotiation (analysis, strategy, development)
- **Payment**: Escrow → release on delivery → dispute arbitration if needed
- **Requirement**: Agentic Wallet, identity setup
- **Best for**: High-value, complex work

---

## Competition Analysis — Finance Category

### Existing Agents (as of Jul 1, 2026)

| Agent | Rating | Sales | Price | Service | Gap for Gentech |
|---|---|---|---|---|---|
| FundingArb | 5.0 (100%) | 4 | 1 USDT | Funding rate arbitrage across 7 exchanges (Binance, OKX, Bybit, Gate, Bitget, Hyperliquid, dYdX) | ✅ We can do better — cross-chain EVM + Solana |
| Stable Auto Earn | 5.0 (100%) | 3 | 1 USDT | Stablecoin yield optimizer (Aave, Morpho, Compound, Spark, Fluid, Ethereum, Base, Arbitrum, Solana) | ⚠️ Direct competitor — we need differentiation |
| WorldCupCaller | 4.8 (96%) | 133 | 0.5 USDT | World Cup predictions + Polymarket links | N/A (different vertical, high volume but niche) |

### Competitive Intelligence

**FundingArb patterns**:
- Scans 7 exchanges for funding rate spreads
- Returns ranked opportunities with annualized returns
- Excludes absurd rates and all-negative markets
- Buyers pay 1 USDT per scan
- 4 sales total (early traction)

**Stable Auto Earn patterns**:
- Scans multiple chains for best stablecoin APY
- Calculates break-even for cross-chain moves (gas vs yield)
- Manual wallet signature required for every action
- Buyers pay 1 USDT per scan
- 3 sales total

**Market gaps**:
- No LP strategy analysis (Curve/Bid-Ask, Gamma, Range, Stable)
- No automated rebalancing (all agents are one-off reports)
- No cross-chain yield arbitrage execution (mostly analysis, not action)
- No reputation management tools

---

## Gentech Agent Lineup — First 3

### 1. LP Shape Detector
- **Service**: Detect LP strategy shapes (Curve/Bid-Ask, Gamma, Range, Stable)
- **Pricing**: 0.5 USDT per scan OR 5 USDT/month subscription
- **Target**: DeFi traders, yield farmers
- **Mode**: Agent-to-MCP (instant)
- **Advantage**: Deep DeFi knowledge, no competitor has this
- **Status**: ✅ Live (lp-shape-detector skill exists)

### 2. DCA Rebalancing Agent
- **Service**: Automated DCA + rebalancing with efficiency tracking
- **Pricing**: 10 USDT/setup + 2% of yield OR 20 USDT/month subscription
- **Target**: DeFi LPs, long-term holders
- **Mode**: Agent-to-Agent (escrow via Q402 or OKX escrow)
- **Advantage**: Continuous value, not one-off information
- **Status**: ✅ Live (dca-rebalance-handler exists)

### 3. Cross-chain Yield Scanner
- **Service**: Scan chains for best yields (Aave, Morpho, Compound, Spark, Fluid) with cross-chain move recommendations
- **Chains**: Ethereum, Base, Arbitrum, Solana
- **Pricing**: 1 USDT per scan OR 8 USDT/month subscription
- **Target**: Passive stablecoin holders
- **Mode**: Agent-to-MCP (instant)
- **Advantage**: Better coverage than Stable Auto Earn, action-oriented
- **Status**: ⚠️ Needs cross-chain integration work

---

## Competitive Edge Summary

| Feature | Most Agents | Gentech |
|---|---|---|
| Service type | One-off information (report) | Continuous value (ongoing service) |
| Payment rails | OKX SDK only | Multi-protocol (x402 + Q402 + OKX SDK) |
| Chain support | EVM only | EVM + Solana bridge |
| Escrow | Coming or missing | ✅ Q402 ready now |
| Reputation | None (new agents) | 100M+ payment track record |
| Support | Basic (description only) | Premium (examples, updates, customization) |

**Key differentiator**: We don't just sell information — we sell outcomes that compound over time.

---

## Execution Plan

### Week 1: Setup & Registration
- [ ] Install Onchain OS skill: `npm i @okx/onchainos-skills`
- [ ] Create OKX Agentic Wallet
- [ ] Register as ASP (Agent Service Provider)
- [ ] Prepare agent descriptions and examples (2-3 outputs per agent)

### Week 2: First 3 Agents Live
- [ ] LP Shape Detector listed (Agent-to-MCP mode)
- [ ] DCA Rebalancing Agent listed (Agent-to-Agent escrow via Q402)
- [ ] Cross-chain Yield Scanner listed (Agent-to-MCP mode)
- [ ] Test end-to-end payment flows (small test amounts)

### Week 3: Metrics & Optimization
- [ ] Track reputation growth (aim for 95%+ positive)
- [ ] Monitor sales and feedback
- [ ] Optimize pricing based on demand (adjust if 0 sales after 7 days)
- [ ] Expand agent catalog based on demand signals

---

## Strategic Bottom Line

**This is greenfield** — only 1,030 completed tasks ever. First movers establish reputation now. Our advantages:

1. **Continuous value** (rebalancing) vs **one-off information** (most agents)
2. **Dual-protocol support** (x402 + Q402) — others rely solely on OKX SDK
3. **Cross-chain expertise** (EVM + Solana) — emerging market, early edge
4. **100M+ payment track record** — instant credibility

**Play**: Integrate as Tier 1 providers, push x402 as optional payment rail, become reference implementation for cross-protocol agents.

**Risk**: OKX may lock in proprietary ecosystem. Counter by maintaining x402 independence and cross-platform presence.

---

## Links

- OKX.AI homepage: https://www.okx.ai/en
- Task Marketplace: https://www.okx.ai/tasks
- Agent Marketplace: https://www.okx.ai/agents
- Tutorial/Guide: https://www.okx.ai/tutorial
- Onchain OS Docs: https://web3.okx.com/onchainos/dev-docs/home