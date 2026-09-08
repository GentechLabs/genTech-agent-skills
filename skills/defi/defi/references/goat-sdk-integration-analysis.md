# GOAT SDK — Integration Analysis (Jun 17, 2026)

## What It Is

GOAT (Great Onchain Agent Toolkit) — "largest agentic finance toolkit" for AI agents. MIT licensed. Sponsored by Crossmint.

- **GitHub:** github.com/goat-sdk/goat (997 stars, 303 forks, 689 commits)
- **Languages:** TypeScript + Python
- **Plugins:** 200+ on-chain tools

## Chains Supported

EVM (Ethereum, Base, Arbitrum, Optimism, Polygon, BSC, Avalanche), Solana, Cosmos, Fuel, Radix, Starknet, Zilliqa, Chromia, Zetrix

## Agent Frameworks

LangChain, LlamaIndex, MCP (Model Context Protocol), Vercel AI, Mastra, OpenAI GPT (REST), Eliza, GAME (Virtuals), CrewAI, OpenAI Agents SDK, AG2, ZerePy

## Key Plugins (Relevant to GenTech)

| Plugin | Relevance |
|--------|-----------|
| Jupiter | Solana swaps (we already use this) |
| Uniswap | EVM swaps |
| Polymarket | Prediction markets |
| DeBridge | Cross-chain bridging |
| Balancer | Liquidity pools |
| Orca | Solana CLMM positions |
| Meteora | Solana liquidity pools |
| DexScreener | Token data (we already use this) |
| CoinGecko | Price data (we already use this) |
| Rugcheck | Token safety checks |
| Pump.fun | Token launches |
| Farcaster | Social protocol |
| Superfluid | Streaming payments |
| ERC721 | NFT interactions |

## Wallet Support

Crossmint Smart Wallets, Crossmint Custodial, Lit, Safe

## HyperMove (GOAT Network Builder Grant)

- Bitcoin-backed agent payments — agents pay for APIs using BTC as collateral
- No private key exposure needed
- Working app: @0xkinetic10
- Part of GOAT Network AI Builder Grants Program

## Integration Assessment for GenTech

### Could Replace
- Building individual DEX adapters (Jupiter, Uniswap, Orca already in GOAT)
- Building individual price feed integrations (CoinGecko, DexScreener already in GOAT)
- Building individual bridge integrations (DeBridge already in GOAT)

### What We'd Still Build
- ERC-8004 identity layer (not in GOAT)
- Agent enforcement/reputation (not in GOAT)
- Dashboard/visualization (not in GOAT)
- LFJ-specific position management (not in GOAT)

### Architecture Option
GOAT SDK as middleware → we wrap their 200+ tools + add our identity/enforcement layer on top. They handle plumbing, we handle identity and trust.

### Effort
- TypeScript integration: Medium (SDK is well-documented)
- Python integration: Medium (Python SDK available)
- MCP integration: Low (GOAT already supports MCP)

### Risk
- Dependency on Crossmint-backed project (stable but centralized)
- MIT licensed — can fork if needed
- 10 months since last commit (check activity before deep integration)

## Action Items
- [ ] Test GOAT SDK Python package with Hermes
- [ ] Evaluate if GOAT MCP server works with our stack
- [ ] Compare GOAT's Jupiter integration vs our existing approach
- [ ] Decide: integrate as middleware or keep building custom
