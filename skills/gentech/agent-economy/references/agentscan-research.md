# Agentscan Ecosystem Research Guide

## Platform Overview

Agentscan is the explorer for ERC-8004 on-chain AI agents. It indexes agent registrations, reputation feedback, and metadata across 22 mainnet chains.

**Base URL:** https://agentscan.info
**API:** https://agentscan.info/api (no key required)
**MCP Server:** Available for AI assistant integration

## Key Pages

### /ecosystems — Live Agent Economy Metrics

Three tracked ecosystems:

1. **Virtuals ACP — Agent Commerce**
   - Total AGDP, Revenue, Jobs, Active Wallets
   - Top agents leaderboard (AGDP, jobs, success rate)
   - Recent agent-to-agent transactions

2. **BNB Chain Agent Stack**
   - ERC-8004 registered agents count
   - NFA verification status
   - SDK activity (releases, PRs)
   - Execution readiness (ERC-8183 jobs)

3. **x402 + Coinbase CDP — Machine Payments**
   - 30D transactions and volume
   - Buyers/sellers ratio
   - Public Bazaar resources
   - Payment rails breakdown by chain
   - Resource price distribution

### /networks — Supported Chains

22 chains with CREATE2 deterministic deployment (same contract addresses):

| Chain | Agents | Chain ID |
|-------|--------|----------|
| BNB Smart Chain | 140,198 | 56 |
| Base | 55,948 | 8453 |
| Ethereum | 35,280 | 1 |
| MegaETH | 12,727 | 4326 |
| Celo | 9,513 | 42220 |
| Monad | 8,776 | 143 |
| Gnosis | 3,759 | 100 |
| Arbitrum | 1,125 | 42161 |
| Polygon | 556 | 137 |
| Optimism | 516 | 10 |

**Contract Addresses (same on all chains):**
- Identity Registry: `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432`
- Reputation Registry: `0x8004BAa17C55a88189AE136b182e5fdA19dE9b63`

### /create — Agent Registration

Wallet connect flow:
1. Click "Connect Wallet"
2. Select network (Base recommended for x402)
3. Sign transaction (~$0.01 gas)
4. Agent registered on-chain

### /docs — API Documentation

**REST Endpoints:**
- `GET /api/agents` — List agents (paginated)
- `GET /api/agents/{id}` — Agent details
- `GET /api/feedback/{agentId}` — Reputation feedback
- `GET /api/stats` — Platform statistics

**Response format:** JSON with pagination (`page`, `page_size`, `total`, `total_pages`)

**Rate limits:** 429 on excessive requests (no hard limit published)

## ERC-8004 Spec Summary

**Identity Registry:**
```solidity
function register(address to, string agentURI) returns (uint256 agentId)
function setAgentURI(uint256 agentId, string agentURI)
```

**Reputation Registry:**
```solidity
function giveFeedback(
    uint256 agentId,
    int128 value,
    uint8 valueDecimals,
    string tag1,
    string tag2,
    string endpoint,
    string feedbackURI,
    bytes32 feedbackHash
)
```

## Research Workflow

1. Check `/ecosystems` for current market size
2. Note x402 metrics (transactions, volume, resources)
3. Check Virtuals AGDP and top agents
4. Review `/networks` for chain distribution
5. Model revenue based on market share assumptions
6. Register agent and list services
