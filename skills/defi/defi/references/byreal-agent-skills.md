# Byreal Agent Skills — Solana CLMM DEX

## Overview
**Repo:** https://github.com/byreal-git/byreal-agent-skills ⭐137
**What:** Agent skills for [Byreal](https://byreal.io) — a concentrated liquidity (CLMM) DEX on Solana
**Install:** `npx skills add byreal-git/byreal-agent-skills` or `npm install -g @byreal-io/byreal-cli`

## Features
- **Pools** — List, search, inspect CLMM pools. K-line charts, Est. APR (fee + reward breakdown), TVL, volume, comprehensive pool analysis (risk, volatility, range recommendations)
- **Tokens** — List tokens, search by symbol/name, real-time prices
- **Swap** — Preview and execute token swaps with slippage control and price impact estimation
- **Positions** — Open, close, manage CLMM positions. Claim fees and rewards. Analyze position performance. Copy top farmers' positions
- **Wallet** — View address and balances, manage keypairs
- **Config** — Configure RPC URL, slippage tolerance, priority fees

## Key Commands
```bash
# First-time setup
byreal-cli setup

# View top pools by APR
byreal-cli pools list --sort-field apr24h

# Analyze a pool
byreal-cli pools analyze <pool-address>

# Swap 0.1 SOL → USDC (preview)
byreal-cli swap execute \
  --input-mint So11111111111111111111111111111111111111112 \
  --output-mint EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v \
  --amount 0.1 --dry-run

# Copy a top farmer's position
byreal-cli positions copy --position <address> --amount-usd 100 --confirm
```

## Agent Integration
- All commands support `-o json` for structured output
- Install as agent skill: `npx skills add byreal-git/byreal-agent-skills`
- AI agents can discover and use all capabilities automatically

## Relevance to AAE
- **Solana-native** — aligns with AAE architecture
- **CLMM expertise** — could enhance YoYo's LFJ/AAE LP strategies
- **CopyFarmer** — copy top Solana LP positions (potential strategy source)
- **Agent skills format** — compatible with Hermes skill system
- **Hackathon potential** — could integrate with HeyGen hackathon or future Solana projects

## Pool Analysis Capabilities
- Risk assessment (volatility, impermanent loss projection)
- Range recommendations for CLMM positions
- APR breakdown (trading fees + incentive rewards)
- K-line/candlestick chart data

---
*Discovered by Gentech — May 7, 2026*
