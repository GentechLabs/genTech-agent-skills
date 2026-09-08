# x402 Multi-Chain Implementation Reference

**Source:** Pay.sh research + x402 protocol analysis (2026-06-03)
**Vault:** `09-Green Room/pay-sh-multi-chain.md`

---

## x402 Supported Chains (June 2026)

| Chain | Type | USDC | Gas | Settlement | Best For |
|-------|------|------|-----|------------|----------|
| **Base** | Ethereum L2 | ✅ Native | ~$0.001 | Instant | Cheapest, Coinbase native, most x402 support |
| **Ethereum** | L1 | ✅ | Variable | ~15s | Most secure, institutional trust |
| **Polygon** | Sidechain | ✅ | ~$0.001 | 2s | Low cost, user-friendly for humans |
| **Arbitrum** | Ethereum L2 | ✅ | ~$0.01 | Instant | Balanced speed/cost |
| **Optimism** | Ethereum L2 | ✅ | ~$0.01 | Instant | Fast, low cost |
| **Solana** | SVM | ✅ | ~$0.001 | 400ms | Pay.sh native, 50+ APIs |

---

## Facilitator Network

Facilitators validate and settle x402 payments:

| Facilitator | Chains | Notes |
|-------------|--------|-------|
| **Coinbase CDP** | Base, ETH, Polygon, Arbitrum, Optimism | Official, most reliable |
| **Dexter** | Polygon, Arbitrum, Optimism, Avalanche | Community, EVM-focused |
| **x402-open** | EVM + SVM | Open-source, self-hostable |
| **B3 AnySpend** | All EVM + Solana | Multi-chain, cross-chain |

---

## Smart Chain Routing Strategy

| Use Case | Best Chain | Why |
|----------|------------|-----|
| Agent-to-API payments | Base | Cheapest gas, Coinbase native |
| Agent-to-agent payments | Avalanche | AAE home chain, ERC-8004 native |
| Human-to-agent payments | Polygon | Low cost, user-friendly |
| High-value settlements | Ethereum | Most secure |
| Pay.sh integration | Solana | Native support, 50+ APIs |

---

## Implementation Pattern

```typescript
interface ChainRouter {
  route(payment: PaymentRequest): ChainConfig;
}

class SmartRouter implements ChainRouter {
  route(payment: PaymentRequest): ChainConfig {
    if (payment.amount < 0.01) return { chain: 'base', reason: 'cheapest' };
    if (payment.speed === 'fast') return { chain: 'solana', reason: '400ms' };
    if (payment.chain === 'avalanche') return { chain: 'avalanche', reason: 'AAE native' };
    return { chain: 'base', reason: 'default' };
  }
}
```

---

## Pay.sh API (Solana)

```bash
# Discover APIs
GET https://pay.sh/api/v1/catalog

# Get pricing
GET https://pay.sh/api/v1/catalog/{api_id}

# Pay + access API
POST https://pay.sh/api/v1/pay
{
  "api": "google-gemini",
  "chain": "base",
  "amount": 0.001,
  "currency": "USDC"
}
```

---

## Pitfall

x402 is chain-agnostic but **facilitator availability varies by chain**. Always check if a facilitator supports your target chain before routing. Coinbase CDP covers the most chains; x402-open is the self-hostable fallback.
