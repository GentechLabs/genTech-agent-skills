# Agentic Finance Landscape — Competitive Intelligence

**Source:** @CambrianNetwork via @MiloOnChains (June 4, 2026)
**Full file:** `${VAULT_DIR}/03-Strategies/agentic-finance-landscape.md`

## The Four Categories

### I. DeFi Copilots
HeyAnon, TrueNorth, AIWayfinder, Bankr ⚠️, Glider ⬆️ (now a VENUE — see below), Velvet, SurfAI, Elsa, Symphony, Cod3x, **Olas (HIGH integration potential)**, Fere, Mode, Minara, milo, Ecliptica, Beepit, Sorin, Autodotfun

> **⬆️ 2026-09-25 — Glider moved from copilot to VENUE.** Launched the **Glider Developer Platform**: a gated
> B2B REST API (v2.0.0, OpenAPI 3.1.0) that lets a **strategy provider** publish a strategy and a **distributor**
> enroll users into it. Non-custodial (ZeroDev Kernel EVM / Swig SVM smart accounts, session-key automation,
> two-stage user-signed enrollment); **EIP-155 EVM + Solana; Arc absent.** $4M a16z/Coinbase/Uniswap.
> **It is the infrastructure for a "strategy provider" — i.e. the Agency of Traders.** Their pitch: *"turn
> differentiated investment theses into monetizable Direct-to-Wallet strategies."*
> **🔴 Unresolved and behind the gate:** provider **revenue share is not published anywhere** (zero "revenue"
> mentions in `llms-full.txt`). Also **Glider's offchain systems decide allocations and Glider holds the signing
> key** — execution/distribution infrastructure, not decision infrastructure.
> **Read:** study and copy the pattern (session keys, two-stage signed enrollment, non-custodial portfolios);
> **do not absorb the dependency.** Routed to Treasury. Full note: `00-HQ/glider-developer-platform-2026-09-25.md`

### II. Yield Agents
AFI Protocol, Almanak, ARMA, **Arrakis (HIGH)**, Axal, **Kamino (HIGH)**, **Infinit (HIGH)**, **Lulo (HIGH)**, Mamo, **Pendle (HIGH)**, RFL, Sail, **Superform (HIGH)**, Surf Liquid, Zyfai

### III. Informational Agents
**AIXBT (HIGH)**, DeepFortyTwo, Messari, **LlamaAI (HIGH)**, LanaAI

### IV. TradFi Copilots
Composer, Public

## Strategic Principles (Jordan, June 4, 2026)

1. **Don't compete — integrate.** These aren't competitors, they're potential integration partners.
2. **Track open source skills.** Any useful open source tools they release → adapt for our stack.
3. **Build for interoperability.** Users can use our agents OR bring their own skills.
4. **Modular architecture.** Our platform should accept external skills, not just our own.

## Priority Integrations (Research Needed)

1. **Olas** — Open source agent infrastructure
2. **Kamino/Lulo** — Solana yield strategies for AAE
3. **Pendle** — Yield tokenization primitive
4. **Superform** — Cross-chain yield
5. **AIXBT** — Market intelligence feed
6. **LlamaAI** — Protocol data layer

## Watch List

- **Bankr:** Security incident May 2026 (14 wallets compromised). Monitor.
- **Infinit Labs:** Mantle challenge we analyzed. Track progress.
- **Arrakis:** LP automation aligns with LFJ/Meteora work.
