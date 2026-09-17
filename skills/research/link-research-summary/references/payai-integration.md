# PayAI Facilitator — Integration Reference

## What It Is
PayAI is the #2 x402 facilitator by volume with native Solana settlement. No API key needed.

## Key Facts
- Website: https://payai.network/
- Docs: https://docs.payai.network/
- npm: `@payai/x402-express`, `@payai/x402-axios`, `@payai/x402-solana`
- GitHub: https://github.com/PayAINetwork/x402-solana

## Comparison

| Feature | PayAI | Coinbase CDP | Q402 |
|---------|-------|--------------|------|
| Solana | ✅ Native | ❌ | ❌ |
| EVM chains | 8 | 1 (Base) | 11 |
| API key | None needed | Required | Required |
| Per-tx fee | ~$0.001 | ~$0.001 | Subscription |
| Settlement | Sub-second Solana | ~2-13s Base | Varies |

## Python Integration (no SDK)
Since PayAI has no Python SDK, we built `payai_facilitator.py`:
- REST API verification against `https://facilitator.payai.network/v1/verify`
- Dual-facilitator: PayAI (Solana) + CDP (Base) as fallback
- Endpoint pricing configured for all APIs

## JavaScript Integration
```bash
npm install @payai/x402-express
```
```typescript
import { x402ExpressMiddleware } from "@payai/x402-express";
app.get("/api", x402ExpressMiddleware({
  price: "$0.005",
  network: "solana",
  facilitator: "payai",
}), handler);
```

## When to Use PayAI vs CDP
- **PayAI:** Solana-native payments, no API key, fast settlement
- **CDP:** Base-only, deeper Coinbase ecosystem integration
- **Both:** Dual-facilitator for maximum chain coverage

## Build Queue Item
Added to build queue as "PayAI Facilitator — Solana x402 v2 integration"
Built: June 25, 2026. Module at `deal-tracker-api/api/payai_facilitator.py`

## Dual-Protocol (x402 + MPP) — Aug 6, 2026
PayAI's `agentic-payments` SDK accepts BOTH x402 and MPP on one endpoint (dual-challenge 402). MPP = IETF draft-httpauth-payment-00 (Tempo Labs + Stripe), payment-method agnostic. Our gateway is x402-only — adding MPP is a real capability gap. **Full research:** `11-Mess Hall/payai-mpp-dual-rail.md` · **Build queue #47.**
