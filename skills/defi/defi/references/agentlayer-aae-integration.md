# AgentLayer × AAE Integration

## Overview
AgentLayer is an agent orchestration platform with Uniswap integration. They provide the execution layer; we provide identity + reputation.

## What AgentLayer Provides
- Agent creation, connection, and task routing
- Uniswap Trading API + Universal Router v2.0 integration
- Preview + simulate before execution
- Minimum-output guard (slippage protection)
- 7 open-source AI skills for swaps, liquidity, planning

## What We Provide (AAE)
- ERC-8004 agent identity NFTs
- Agent Credit Score (0-850)
- x402 nano-payments
- On-chain reputation system

## Integration Architecture
```
User → AgentLayer (orchestration) → Uniswap (execution)
                ↓
        AAE Identity Check (ERC-8004)
                ↓
        Credit Score Check (0-850)
                ↓
        Execute Swap (preview + simulate)
                ↓
        Update Credit Score (+2 for success)
```

## 4-Phase Build
1. **Identity Bridge** (1 week) — Export ERC-8004 as AgentLayer credential
2. **Credit Score Integration** (1 week) — AgentLayer checks score before execution
3. **Uniswap Execution** (1 week) — Integrate Uniswap AI Skills
4. **x402 Payments** (1 week) — Agent-to-agent nano-payments

## Why This Matters
Nobody has the full stack:
- We bring: Identity + Reputation (unique)
- They bring: Execution + Orchestration (Uniswap)
- Together = Complete agent economy infrastructure

## Reference
- Spec: `09-Green Room/ideas/agentlayer-integration.md`
- Competitive intel: `references/agentlayer-competitive-intel-2026-05.md`
