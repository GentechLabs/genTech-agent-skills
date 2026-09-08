# brave-experiments/private-x402-gateway — x402 v2 Compliance Audit

**Date:** 2026-07-14
**Repo:** https://github.com/brave-experiments/private-x402-gateway
**Architecture:** Monorepo with 4 packages (gateway, facilitator, shared, cli)
**`@x402/core` version:** `^2.9.0`

## Architecture

```
┌──────────────┐    OHTTP      ┌──────────────┐    OHTTP     ┌──────────────┐
│  CLI (3000)  │ ──────────→  │   Relay      │ ──────────→  │  Gateway     │
│              │               │  (OHTTP      │               │  (:3001)     │
│  buy-tokens  │               │   proxy)     │               │  auth MW     │
│  request     │               └──────────────┘               │  /api/weather│
│  client.ts   │                                              │  /api/quote  │
│  payment.ts  │                                              └──────┬───────┘
└──────────────┘                                                     │
                                                                     │ OHTTP
                                                                     ▼
                                                              ┌──────────────┐
                                                              │ Facilitator  │
                                                              │  (:3002)     │
                                                              │              │
                                                              │ /issue       │
                                                              │ /token-key   │
                                                              │ payment.ts   │
                                                              │ issuer.ts    │
                                                              └──────────────┘
```

The Gateway issues 402s + verifies Privacy Pass tokens. The Facilitator settles payments on Solana. The CLI routes all requests through an OHTTP relay for privacy. The Shared package contains VOPRF/crypto primitives and type re-exports.

## Critical Findings

### HIGH — Client uses V1 scheme with V2 version stamp

**Location:** `packages/cli/src/services/payment.ts:49-50`

```typescript
const scheme = new ExactSvmSchemeV1(signer);               // V1 client class
const result = await scheme.createPaymentPayload(2, reqs);  // claims version 2
```

`ExactSvmSchemeV1` (`@x402/svm/dist/cjs/exact/v1/client/index.d.ts`) produces a V1-shaped payload:

```typescript
// V1 shape (what's actually sent):
{ x402Version: 2, scheme: "exact", network: "solana:...", payload: { ... } }

// V2 shape required by spec:
{ x402Version: 2, accepted: { scheme, network, amount, asset, payTo, ... }, payload: { ... } }
```

The V2 payload requires an `accepted: PaymentRequirements` envelope field. V1's flat `scheme`/`network` at top level is structurally different. A v2 facilitator will reject this payload because `accepted` is missing.

**Fix:** Use `ExactSvmScheme` (v2, from `@x402/svm/exact/client`) instead of `ExactSvmSchemeV1`.

### HIGH — Default `payTo` is the Solana system program

**Location:** `packages/gateway/src/config.ts:13`

```typescript
pricePayTo: process.env.PRICE_PAY_TO || "11111111111111111111111111111111"
```

`11111111111111111111111111111111` is the Solana system program — it cannot receive SPL USDC transfers. Every 402 response generated without explicit `PRICE_PAY_TO` contains a dead receiver address.

### HIGH — Gateway/facilitator default network mismatch

| Component | Default network | File |
|-----------|----------------|------|
| Gateway | `solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp` (mainnet) | `config.ts:11` |
| Facilitator | `solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1` (devnet) | `payment.ts:41` |

Gateway advertises mainnet requirements but facilitator verifies on devnet. Payment always fails without explicit env overrides.

### HIGH — Gateway/facilitator default asset mismatch

| Component | Default asset | File |
|-----------|--------------|------|
| Gateway | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` (mainnet USDC) | `config.ts:12` |
| Facilitator | `4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU` (unknown/other token) | `payment.ts:42` |

Different token mints. If the gateway demands payment in asset A but the facilitator verifies against asset B, verification always fails.

### MEDIUM — `X-Payment-Required` instead of `Payment-Required`

**Locations:**
- `packages/gateway/src/middleware/auth.ts:71` — sets header
- `packages/cli/src/commands/request.ts:132` — reads header
- `packages/cli/src/commands/buy-tokens.ts:50` — reads header

The v2 spec uses `Payment-Required` (no `X-` prefix, per RFC 6648).

### MEDIUM — Client normalizes v2 fields back to v1

**Location:** `packages/cli/src/commands/request.ts:143-147`

```typescript
maxAmountRequired: raw.amount || raw.maxAmountRequired,
extra: { ...raw.extra, feePayer: raw.extra?.feePayer || raw.payTo },
```

The client decodes the v2 `Payment-Required` header, then converts `amount` → `maxAmountRequired` (v1 field) and `payTo` → `extra.feePayer` (v1 convention). The internal `PaymentClient` then receives v1-normalized requirements, so even if the server sent correct v2, the client downgrades it internally.

### MEDIUM — No `/.well-known/x402` endpoint

The repo has `/.well-known/private-token-issuer-directory` (Privacy Pass) and `/ohttp-keys`, but no `/.well-known/x402` for scheme discovery.

### LOW — Locally redefined `PaymentRequired` type

**Location:** `packages/gateway/src/middleware/auth.ts:18-24`

```typescript
export interface PaymentRequired {
  x402Version: number;
  error?: string;
  resource: { url: string; description?: string; mimeType?: string };
  accepts: PaymentRequirements[];
  extensions?: Record<string, unknown>;
}
```

Matches v2 shape now, but drifts silently if `@x402/core` updates. The shared package re-exports `PaymentRequirements` and `PaymentPayload` from `@x402/core/types` but not `PaymentRequired`.

### LOW — Facilitator reconstructs requirements from env

**Location:** `packages/facilitator/src/services/payment.ts:39-47, 71-79`

The facilitator's `verifyPayment` and `settlePayment` methods build a fresh `PaymentRequirements` object from env vars instead of using the fields in the client's payment payload. This means even if the client correctly echoes back the gateway's `PaymentRequired.accepts[0]`, the facilitator compares against its own hardcoded values — silently dropping the client's chosen network, asset, and payTo.

## Summary

| # | Severity | Issue | Effort |
|---|----------|-------|--------|
| 1 | HIGH | V1 scheme class producing V2 payload (missing `accepted`) | MEDIUM |
| 2 | HIGH | `payTo` defaults to system program | LOW |
| 3 | HIGH | Gateway/facilitator network mismatch (mainnet vs devnet) | LOW |
| 4 | HIGH | Gateway/facilitator asset mismatch (different tokens) | LOW |
| 5 | MEDIUM | Uses `X-Payment-Required` instead of `Payment-Required` | LOW |
| 6 | MEDIUM | No `/.well-known/x402` endpoint | LOW |
| 7 | MEDIUM | Client normalizes v2→v1 fields internally | MEDIUM |
| 8 | LOW | Locally redefined `PaymentRequired` type | LOW |
| 9 | LOW | Facilitator reconstructs requirements from env | MEDIUM |
