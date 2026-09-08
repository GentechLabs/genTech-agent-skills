# Circle Arc — Infrastructure Research (May 2026)

Condensed knowledge bank from deep-dive research session. Sources: Circle blog, QuickNode, Eco.com support, Arc community forum, GitHub repos.

## Key Sources

| Source | URL | Content |
|--------|-----|---------|
| Circle blog (introduction) | circle.com/blog/introducing-arc-an-open-layer-1-blockchain-purpose-built-for-stablecoin-finance | Full architecture overview, use cases, Malachite consensus |
| Arc official site | arc.network | Feature summary, lending/borrowing builder pitch |
| Arc community post | community.arc.io/home/externals/how-arc-supports-lending-and-borrowing-or-arc-blueprints-2026-05-15 | Lending/borrowing blueprint deep-dive (JS-heavy, needs browser) |
| QuickNode announcement | blog.quicknode.com/quicknode-supports-arc-by-circle/ | Infrastructure partner perspective, feature list |
| Eco.com explainer | eco.com/support/en/articles/12160003 | Technical deep-dive: Malachite, FX engine, privacy, EVM compat |
| Circle pressroom | circle.com/pressroom/circle-launches-arc-public-testnet | Testnet launch, 100+ participants, ecosystem map |
| GitHub sample app | github.com/circlefin/arc-defi-lending-and-borrowing | cirBTC → USDC lending reference implementation |
| Testnet details | bitkan.com (Arc whitepaper summary) | Chain ID 5042002, faucet, testnet setup |

## Arc Testnet Setup

- Chain ID: `5042002`
- Faucet: `faucet.circle.com` (20.0 USDC)
- EVM-compatible: use MetaMask, Hardhat, Foundry with standard RPC config

## Malachite Consensus (Deep)

- Based on Tendermint BFT algorithm
- 20 geographically distributed validators
- 3,000 TPS throughput
- 350ms finality (deterministic, not probabilistic)
- Acquired from Informal Systems by Circle (Aug 2025)
- Open-source under permissive license

## FX Engine (Deep)

- Request-for-quote (RFQ) system for onchain stablecoin conversion
- Market makers compete to fill orders
- 24/7 PvP settlement (no business hours)
- Native protocol feature (not an external DEX integration)
- Supports USDC, EURC, and other stablecoins launching on Arc
- Enables: automated treasury management, multi-currency invoicing, programmatic hedging

## Privacy Model (Deep)

- **Phase 1 (current):** Confidential transfers — amounts encrypted, addresses visible
- **Phase 2 (roadmap):** Privacy states + confidential computing
  - Verify collateral position without revealing specific assets
  - Confirm payment obligations without exposing pricing terms
- Regulators can still trace funds (selective disclosure, not full privacy)

## Ecosystem Participants (Testnet Launch)

### Borrow/Lend Protocols
- Aave, Maple, Morpho

### DEXs
- Curve, Aerodrome/Velodrome, Euler Finance, Fluid, Uniswap Labs

### Stablecoin Issuers (non-USDC)
- AUDF (Australia), BRLA (Brazil), JPYC (Japan), KRW1 (Korea), MXNB (Mexico), PHPC (Philippines), QCAD (Canada)

### Banks/Institutions
- Apollo, BNY, ICE, State Street, BlackRock, Goldman Sachs, HSBC, Deutsche Bank, Standard Chartered, Société Générale

### Infrastructure
- QuickNode, Chainlink, Alchemy, Blockdaemon, Fireblocks, MetaMask, Ledger

## Circle Blocklist Enforcement

Unique to Arc: Circle maintains a blocklist that is enforced at two levels:
1. **Pre-execution** — transactions to blocklisted addresses rejected before mempool entry
2. **Post-execution** — transactions that attempt transfers to blocklisted addresses reverted

This is enterprise-grade compliance infrastructure. No other L1 has this natively.

## Strategic Relevance to GenTech

### Direct Use Cases
1. **DeFi lending products** — deploy on Arc for native stablecoin economics
2. **Multi-currency lending** — leverage built-in FX engine
3. **Institutional products** — privacy + compliance + predictable fees
4. **Cross-chain USDC plays** — CCTP integration is native

### Considerations
- Arc is testnet only (May 2026). Mainnet timeline unclear.
- EVM-compatible means existing Solidity code ports easily from Ethereum
- Not a replacement for Solana stack — complements it for different use cases
- Circle's blocklist enforcement is a feature for institutional products, a limitation for permissionless DeFi
- 100+ participants at launch signals ecosystem momentum

### Architecture Decision
Don't commit to Arc over Solana or vice versa. They serve different markets:
- **Solana** = speed, low cost, mature DeFi ecosystem, consumer-facing
- **Arc** = institutional, compliance-ready, native stablecoin economics, enterprise

---

*Last updated: 2026-05-22*
*Research session: Jordan asked to deep-dive Circle docs on Arc Blueprints for lending/borrowing*
