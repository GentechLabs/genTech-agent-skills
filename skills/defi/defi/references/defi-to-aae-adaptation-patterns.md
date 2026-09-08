# DeFi → AAE Adaptation Patterns

Reusable technique for mapping DeFi mechanics to agent commerce. When designing new AAE features, scan DeFi protocols for transferable patterns.

---

## Pattern: Limit Orders → Agent Order Book

**Source:** Meteora DLMM Limit Orders (LP Army)

**DeFi mechanics:**
- LPs place limit orders on DLMM pools
- Orders match when bid ≥ ask
- LPs earn fees from fills (instead of paying for execution)

**AAE adaptation:**
- Agents place limit bids ("I'll do X for Y USDC")
- Humans place limit asks ("I need X, paying Y USDC")
- Auto-match on price cross at midpoint
- Agents "stake capacity" as liquidity → earn fees when tasks fill

**The reversal hook:** "Most marketplaces charge you. Ours can pay you." — Agents become liquidity providers, not just workers.

**Revenue layers:**
- 2% platform fee on every match
- 1% liquidity provision fee
- Agent Pass ($15/mo) for priority matching
- $0.001/trade spread capture

**Flywheel:**
```
More agents staking → tighter spreads → more humans place asks
→ more fills → more agent earnings → more agents join → repeat
```

**Reference:** See vault `09-Green Room/lobby-ui-order-book.md` for full design.

---

## Pattern: Liquidity Pools → Agent Capacity Pools

**Source:** Uniswap V3 / Meteora DLMM concentrated liquidity

**DeFi mechanics:**
- LPs provide concentrated liquidity in price ranges
- More concentrated = higher fees but more IL risk
- LPs earn proportional to their share of the pool

**AAE adaptation:**
- Agents define capacity ranges (e.g., "available for research tasks $0.03-$0.10")
- More concentrated = higher match rate but less flexibility
- Agents earn proportional to tasks filled

**Data model:**
```typescript
interface AgentLiquidityPool {
  agent: string;              // ERC-8004 address
  capacity: number;           // total tasks available
  staked_usdc: number;        // USDC staked as guarantee
  rate_per_task: number;      // price per task
  category: string;           // what they do
  reputation: number;         // agent rep score
  filled_24h: number;         // tasks completed today
  earnings_24h: number;       // USDC earned today
  apy_estimate: number;       // projected annual yield
}
```

---

## Pattern: DEX Aggregators → Agent Matching

**Source:** Jupiter Aggregator / 1inch

**DeFi mechanics:**
- Aggregators find best price across multiple DEXes
- Route optimization minimizes slippage
- One-click execution across fragmented liquidity

**AAE adaptation:**
- Match agent bids against human asks across categories
- Route to best-fit agent based on reputation, price, response time
- One-click task execution across fragmented agent capacity

---

## Pattern: Yield Farming → Agent Staking Rewards

**Source:** Convex / Curve gauge system

**DeFi mechanics:**
- Stake LP tokens → earn protocol tokens + fees
- Boost rewards for longer lock periods
- Gauge voting directs rewards to specific pools

**AAE adaptation:**
- Stake agent capacity → earn platform tokens + task fees
- Boost rewards for agents with longer availability commitments
- Reputation score acts as gauge weight (higher rep = more visibility)

---

## Pattern: Flash Loans → Agent Task Loans

**Source:** Aave / dYdX flash loans

**DeFi mechanics:**
- Borrow capital with no collateral
- Must repay within same transaction
- Use case: arbitrage, liquidation, self-liquidation

**AAE adaptation:**
- Agent borrows task capacity (e.g., "take 5 research tasks now, pay later from earnings")
- Must complete tasks within time window
- Use case: scaling up during high-demand periods, reputation building

---

## How to Use This Pattern

1. **Identify the DeFi mechanic** — What problem does it solve? What are the economics?
2. **Map to agent economy** — What's the equivalent for agents? Workers? Tasks?
3. **Find the reversal** — Can we flip the value prop? (e.g., "you pay" → "you earn")
4. **Design the flywheel** — What creates compounding growth?
5. **Layer the revenue** — Platform fee + premium features + spread capture

---

## Pitfalls

- **Don't over-engineer** — Start simple, add DeFi complexity only when needed
- **Watch for regulatory overlap** — If it looks like a security, it might be
- **Test with real users first** — DeFi patterns assume rational actors; agents might behave differently
- **Keep it invisible** — User sees "Finding teammates...", not "Executing limit order match on order book"
