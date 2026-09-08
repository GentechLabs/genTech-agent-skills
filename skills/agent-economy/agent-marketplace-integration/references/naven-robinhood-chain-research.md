# Naven Network & Robinhood Chain Research

**Date:** 2026-07-10
**Trigger:** Atelier x402 live on Robinhood Chain via Naven Network
**Source:** https://x.com/useAtelier/status/2075728472635330950

---

## Robinhood Chain

| Property | Value |
|----------|-------|
| Chain ID | 4663 (mainnet), 46630 (testnet) |
| Type | EVM-compatible (OP Stack) |
| RPC | `https://rpc.mainnet.chain.robinhood.com` |
| Explorer | `https://robinhoodchain.blockscout.com` |
| Native gas | ETH |
| USDG contract | `0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168` |

**Tokenized Stocks (native contracts):**
- AAPL: `0xaF3D76f1834A1d425780943C99Ea8A608f8a93f9`
- NVDA: `0xd0601CE157Db5bdC3162BbaC2a2C8aF5320D9EEC`
- TSLA: `0x322F0929c4625eD5bAd873c95208D54E1c003b2d`
- MSFT: `0xe93237C50D904957Cf27E7B1133b510C669c2e74`
- META: `0xc0D6457C16Cc70d6790Dd43521C899C87ce02f35`
- GOOGL: `0x2e0847E8910a9732eB3fb1bb4b70a580ADAD4FE3`
- AMZN: `0x12f190a9F9d7D37a250758b26824B97CE941bF54`
- SPCX (S&P 500): `0x4a0E65A3EcceC6dBe60AE065F2e7bb85Fae35eEa`
- SPY (ETF): `0x117cc2133c37B721F49dE2A7a74833232B3B4C0C`
- QQQ (ETF): `0xD5f3879160bc7c32ebb4dC785F8a4F505888de68`

Full contract list: https://docs.robinhood.com/chain/contracts/

---

## Naven Network

**Profile:** "Frictionless payments for the autonomous economy"
**Site:** https://naven.network
**X:** @NavenNetwork (662 followers, verified)

### Facilitator

- **Endpoint:** `https://facilitator.naven.network`
- **Standard endpoints:** `/verify` and `/settle` (x402 protocol)
- **Supported tokens:**
  | Network | Token | Address |
  |---------|-------|---------|
  | Robinhood Chain | USDG | `0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168` |
  | X Layer | USDC | `0x74b7f16337b8972027f6196a17a631ac6de26d22` |
  | KiteAI Testnet | USDC | `0x4c2ED1F2a22d61bF7FfF18DA4A8E80d97cC80aBb` |

### Live Demo Endpoint

```bash
# Without payment — triggers 402 Payment Required
curl -i https://api.naven.network/x402-test/ping

# With payment — returns "paid pong"
# Include x402 payment signature header
```

| Field | Value |
|-------|-------|
| Endpoint | `https://api.naven.network/x402-test/ping` |
| Network | `eip155:4663` |
| Token | USDG |
| Asset | `0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168` |
| Price | `$0.0001` |
| Receiver | `0xb9A67f59bcfd3b45fe1ca2c55A55C19B2b35B58f` |
| Facilitator | `https://facilitator.naven.network` |

### First Live Transaction
https://robinhoodchain.blockscout.com/tx/0xf7180c33598a6f5887262a59c5f1fad1877d3e6317c1dd44259463e54a8be8a6

### Product Pillars (from naven.network)
1. **x402 payment infrastructure** — Metered API access, pay-per-call settlement, facilitator routing
2. **Strategy execution layer** — Agents evaluate signals, budget risk, trigger trading workflows
3. **Guarded brokerage actions** — Human-defined permissions, spend limits, audit trails, compliance hooks

Point 3 overlaps directly with GenTech's HITL Layer and Guardrail Plugin concepts.

### Token
- $NAVEN token with native claim and burn feature
- 4.08% of supply incinerated since launch (Jul 10, 2026)
- x402 Genesis Mint on Robinhood Chain

---

## GenTech Integration Points

| What | Status | Action |
|------|--------|--------|
| Atelier agent credentials | ✅ In .env | Already registered |
| Agent Kit Robinhood Chain plugin | 📝 Scoped | In `09-Green Room/` |
| Naven facilitator integration | 🔲 Pending | Match GoPlausible pattern |
| USDG settlement for Agent Kit | 🔲 Pending | Via Naven `/settle` |

### Plugin Architecture (Scoped)
File: `09-Green Room/robinhood-chain-x402-plugin-scope.md`

Proposed tools:
- `rh_info()` — Robinhood Chain + Naven status
- `rh_verify_payment(proof)` — x402 payment verification via Naven
- `rh_get_quote(symbol)` — Crypto price quote ($0.001 USDG)
- `rh_get_stock(symbol)` — Tokenized stock price ($0.005 USDG)
- `rh_list_stocks()` — Available tokenized stocks (free)

Build effort: ~3.5 hours. Dependencies: httpx, pydantic, mcp (all already in Agent Kit).

---

## Strategic Significance

1. **New distribution channel** — Robinhood's millions of users can now hire agents via Atelier
2. **USDG stablecoin** — Paxos-issued, regulated. Enterprise-friendly payment rail
3. **Naven's guarded brokerage** — They're building the same HITL/guardrail layer we want. Worth integrating or learning from
4. **Tokenized stocks market** — Native AAPL, NVDA, TSLA price data for agent trading strategies
5. **x402 multi-chain** — Our agents now span Algorand (GoPlausible) + Robinhood (Naven) + Base (Q402)
