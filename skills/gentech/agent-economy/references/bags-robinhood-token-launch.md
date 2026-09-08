# BAGS — Robinhood Chain Token Launch via Agents

## Overview
BAGS is a pump.fun-style token launch protocol deployed on Robinhood Chain (Arbitrum Orbit L2, chain ID 4663). Unlike the Solana BAGS REST API, the Robinhood Chain integration is fully on-chain — launch, trade, and claim fees by calling contracts directly with viem/ethers.

## Key Facts
| Detail | Value |
|--------|-------|
| Chain | Robinhood Chain (Arbitrum Orbit L2) |
| Chain ID | 4663 (0x1237) |
| Native currency | ETH (18 decimals) |
| RPC | `https://rpc.mainnet.chain.robinhood.com` (rate-limited) |
| BagsFactory | `0xe8Cc4431adF8b5A847C113EF0c6af9043219Cb37` |
| BagsLens | `0xC82Db941dAf90B754aecb5F7D14c683dc608d595` |
| Explorer | https://robinhoodchain.blockscout.com |
| Block time | ~100ms (first-come-first-served sequencer) |

## Token Lifecycle
1. **Creation** — `BagsFactory.create()` or `createAndBuy()` deploys token, bonding curve, fee share
2. **Bonding curve** — Trades on virtual `x*y=k` AMM. 830M of 1B supply sold here
3. **Graduation** — When curve reserves hit threshold, migrates to Uniswap v4 with locked liquidity
4. **Uniswap v4** — Trades through Robinhood-modified UniversalRouter

## Partner Revenue
Pass a **partner address** at launch to earn 25% of the protocol fee (0.25% of all trading volume). This is passive income from every trade of tokens launched through our referral.

| Portion | Rate | Who Gets It |
|---------|------|-------------|
| Creator half | 1% of volume | Token creator (fee claimers) |
| Protocol half | 1% of volume | Split: Partner (25%) + BagsVault (75%) |

## Launch Parameters
```typescript
interface LaunchParams {
  name: string;          // Token name
  symbol: string;        // Token symbol
  metadataURI: string;   // IPFS URI with token metadata
  partner: address;      // GenTech wallet = passive revenue
  claimers: address[];   // Fee recipients (1-100)
  bps: uint16[];          // Basis points per claimer (sum = 10000)
}
```

## Integration Code
Plugin lives at `plugins/bags/` in the Agent Kit:
- `addresses.ts` — Chain config + contract addresses
- `abi.ts` — Factory/bonding curve/fee share ABIs
- `launch.ts` — `launchToken()` and `launchWithGenTechPartner()` helpers
- `README.md` — Setup + usage

## Requirements
- ETH on Robinhood Chain for creation fee (default 0.02 ETH)
- RPC access to Robinhood Chain
- Sign up at dev.bags.fm for partner dashboard + API key (Solana side)

## Connections to Our Stack
- **GOAT x402** — Payment rail for launch fees
- **Q402** — USDG support on Robinhood Chain
- **Agent Kit** — Plugin architecture already supports this
- **Bootcamp submission** — Agent that launches tokens on Robinhood via BAGS

## BAGS Hackathon — $4,000,000

**Status:** 🔴 Active — rolling applications, apply now.
**Link:** https://bags.fm/hackathon

| Detail | Value |
|--------|-------|
| Prize Pool | **$4M** ($1M grants + $3M fund) |
| Winners | 100 teams ($10k-$100k each) |
| Category | **AI Agents** ✅, DeFi, Payments |
| Deadline | Rolling — no close date |
| Bonus | Every winner gets a Mac Mini |
| Requirement | Must use Bags (token/API/fee share) |
| Referral | Refer builders → share of pool |

### Why We Win Here
- Plugin already built (`plugins/bags/`)
- AI Agents is a dedicated category
- Rolling applications — no deadline pressure
- Partner address earns 0.25% of volume on every token launched through our agent

### Application Strategy
1. Apply under AI Agents: "GenTech Launch Agent — AI agent that launches tokens on Robinhood Chain via BAGS"
2. Launch a real token via our agent to prove traction
3. Partner address set to GenTech wallet for passive revenue
4. Refer other builders from our network → share of the pool

### Prerequisites
- Sign up at dev.bags.fm (Jordan)
- Bridge ETH to Robinhood Chain (chain ID 4663) for launch fees
