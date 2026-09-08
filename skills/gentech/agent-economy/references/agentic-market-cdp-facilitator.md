# Agentic.Market & CDP Facilitator — Bazaar Auto-Indexing

Discovered July 10, 2026. Coinbase's Agentic.Market is the primary x402 service discovery marketplace.

## Key Facts

- **TPV:** $52M all-time, 165M+ transactions, 480K+ agents
- **Auto-indexing:** Services appear automatically when the CDP Facilitator **settles** a payment (not on 402 alone). The settlement must include `paymentPayload.resource` to identify which endpoint was called.
- **30-day recency filter:** Resources with no activity for 30 days are excluded. Newly indexed resources with 0 calls are exempt.
- **Quality metrics** (buyer reach, volume, recency) are recomputed every 6 hours — new settlements won't affect ranking immediately.
- **No manual registration:** There is no submit form. Indexing is triggered by payment settlement through the CDP Facilitator at `https://api.cdp.coinbase.com/platform/v2/x402`.

## How Indexing Works

1. Client calls endpoint → server returns 402 with `PAYMENT-REQUIRED` header + `extensions.bazaar` in the JSON body
2. Client signs USDC transfer using EIP-3009 (Base) or appropriate scheme
3. Client sends signed payment to CDP Facilitator → facilitator calls `/verify` then `/settle`
4. On successful settlement, facilitator indexes the resource in Bazaar → appears on Agentic.Market

## Our Gateway Status

- ✅ Returns correct 402 with `payment-required` header (x402 v2 format)
- ✅ `extensions.bazaar` present with input/output schemas
- ❌ **No payments settled yet** — no Bazaar indexing triggered
- ❌ Pay CLI (Solana Foundation) doesn't recognize our header format — it expects MPP/SIWX protocol, not x402. They're separate protocols using the same 402 status code.

## Protocol Format Note

Our gateway uses the x402 v2 format (`PAYMENT-REQUIRED` / `payment-required` header). The Solana Foundation's `pay` CLI speaks MPP/SIWX — a different protocol. Both use HTTP 402 but are not interchangeable.

- **x402 v2 (our gateway):** Correct for Coinbase CDP Facilitator → Agentic.Market
- **MPP/SIWX:** Used by Solana pay CLI → pay-skills catalog

## Next Steps

- **First settled payment** triggers indexing → visible on Agentic.Market
- **x402 Challenge (mid-July)** will drive real traffic through the CDP facilitator
- **Consider updating gateway** to return both x402 AND MPP protocol formats in the 402 response for maximum compatibility

## References

- Agentic.Market: https://agentic.market
- CDP Bazaar docs: https://docs.cdp.coinbase.com/x402/bazaar
- CDP Facilitator: https://api.cdp.coinbase.com/platform/v2/x402
- x402 spec: https://docs.x402.org/core-concepts/http-402
