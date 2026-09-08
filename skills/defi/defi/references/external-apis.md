# External APIs & Integrations (Full)

> Absorbed from `defi` skill §5-11. External DeFi execution layers and integrations.

## Arsenal API (Sumplus)

**Base URL:** `https://arsenal.sumplus.xyz`
**Auth:** `Authorization: Bearer $ARSENAL_API_KEY`

70+ skills across Ethereum, Solana, Sui, Base, Arbitrum, Optimism, BSC.

**Verified Skills:**
- ✅ Jupiter Aggregator (Solana) — quote, build_tx, price
- ✅ DefiLlama — TVL, yields, chain TVL
- ⚠️ No LFJ/Trader Joe integration

## GOAT SDK

200+ plugins (Jupiter, Uniswap, Orca, Meteora, DeBridge, CoinGecko, DexScreener).
MIT license. MCP support. TypeScript/Python.

**Best fit:** MCP integration, cross-chain operations.
**Insight:** They handle plumbing, we handle identity and trust.

## Krexa Credit Infrastructure (Solana)

| Feature | AAE Mapping |
|---------|-------------|
| Krexit Score | Agent reputation |
| Revenue Router | Auto-repayment |
| Tranches | Borrow limits by rank |
| PDA Wallets | Agent wallets |
| x402 Payments | Strategy marketplace |
| Token Launch | Top strategy monetization |

**Don't build credit from scratch.** Krexa has it — we build the game layer on top.

## Circle Arc (Stablecoin-Native L1)

- USDC as native gas (~$0.01/tx)
- Sub-second finality (350ms)
- Atomic DvP for lending
- Built-in FX engine
- EVM-compatible (Solidity works)

**⚠️ Still testnet as of Jun 2026.** Don't commit architecture to testnet-only features.

## Oracle Strategy

| Data Type | Best Oracle | Why |
|-----------|-------------|-----|
| Trading prices | Pyth | Native Solana, first-party, low-latency |
| Agent reputation | Switchboard | Custom permissionless feeds |
| RWA valuation | RedStone | Sub-20ms, institutional-grade |
| Social sentiment | API3 | Direct API providers |
| Cross-chain | Band | Cosmos SDK, multi-chain |

**Don't default to Chainlink.** Use the right oracle for each data type.

## Travala MCP Integration

MCP Server: `https://travel-mcp.travala.com/mcp`
2.2M+ hotels, USDC payments, ~$0.01/tx on Base.
Agent registration: 8004scan.io/agents (ERC-8004) → earn cbBTC rewards.

## Smart Money Rotation

**Buy Zone System:** Deep Value → Accumulate → Watch → Extended
**Narrative Strength:** Monitor which crypto narratives outperform
**Dry Powder Vault:** Cross-chain idle USDC rotation (Base → Avalanche → Solana)

## AAE DeFi Milestone Visual Editions

7 dashboard templates: Milestone Ladder, Yield Farm Detail, Agent Performance, Squad Dashboard, Celebration, Alert, Weekly Summary.

Path: `03-Strategies/Defi-Monitor/`
