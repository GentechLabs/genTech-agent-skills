# x402 v1 → v2 Protocol Migration

> Verified against `itublockchain/hackmoney-router402` PR #9 (Jul 15, 2026).  
> An ETHGlobal HackMoney 2026 Finalist — OpenRouter-compatible AI gateway.

## Problem

The auto-payment service was sending x402 v1 format to the facilitator, but the server was already v2-compliant (using `@x402/core/server`, CAIP-2, `payTo`, `scheme: exact`). This caused protocol mismatch: the client-side payment payload and the facilitator settle/verify call both used the old envelope.

## What Changed

| Aspect | v1 (old) | v2 (new) |
|--------|----------|----------|
| Outer envelope key | `paymentRequirements` | `accepted` |
| Amount field | `maxAmountRequired` | `amount` |
| Version field | `x402Version: 1` | `x402Version: 2` |
| Payment payload format | Flat `{scheme, network, payload}` | Nested `{accepted: {...}, payload: {...}}` |
| Network format | Short name (`base`) | CAIP-2 (`eip155:8453`) |
| Header name | `X-Payment` | `X-PAYMENT` (canonical) |

## Migration Steps

### Step 1: Update the facilitator settle/verify request body

**Before (v1):**
```typescript
const body = {
  x402Version: 1,
  paymentPayload,
  paymentRequirements: {
    scheme: requirements.scheme,
    network: requirements.network,
    maxAmountRequired: requirements.amount,
    asset: requirements.asset,
    payTo: requirements.payTo,
    maxTimeoutSeconds: requirements.maxTimeoutSeconds,
    extra: requirements.extra,
  },
};
```

**After (v2):**
```typescript
const body = {
  x402Version: 2,
  paymentPayload,
  accepted: {
    scheme: requirements.scheme,
    network: requirements.network,
    amount: requirements.amount,          // was maxAmountRequired
    asset: requirements.asset,
    payTo: requirements.payTo,
    maxTimeoutSeconds: requirements.maxTimeoutSeconds,
    extra: requirements.extra,
  },
};
```

### Step 2: Update the payment payload (client-side signed payload)

**Before (v1):**
```typescript
const paymentPayload = {
  x402Version: 1 as const,
  scheme: "exact",
  network: requirements.network,
  payload: { signature, authorization },
};
```

**After (v2):**
```typescript
const paymentPayload = {
  x402Version: 2 as const,
  accepted: {
    scheme: "exact",
    network: requirements.network,
    asset: requirements.asset,
    amount: requirements.amount,
    payTo: requirements.payTo,
    maxTimeoutSeconds: requirements.maxTimeoutSeconds,
  },
  payload: { signature, authorization },
};
```

### Step 3: Update the facilitator server validation schema

Make the server accept both v1 (`paymentRequirements`) and v2 (`accepted`) for backward compatibility.

**Before (v1-only):**
```typescript
const verifyRequestSchema = z.object({
  x402Version: z.number().optional(),
  paymentPayload: z.union([z.string(), z.object({}).passthrough()]),
  paymentRequirements: paymentRequirementsSchema,  // required
});
```

**After (v1 + v2):**
```typescript
const verifyRequestSchema = z.object({
  x402Version: z.number().optional(),
  paymentPayload: z.union([z.string(), z.object({}).passthrough()]),
  // v1: paymentRequirements envelope
  paymentRequirements: paymentRequirementsSchema.optional(),
  // v2: accepted envelope
  accepted: paymentRequirementsSchema.optional(),
}).refine(
  (data) => data.paymentRequirements !== undefined || data.accepted !== undefined,
  { message: 'Either paymentRequirements (v1) or accepted (v2) must be provided' }
);
```

Add a normalization helper:
```typescript
function getPaymentRequirements(data: { paymentRequirements?: any; accepted?: any }): any {
  return data.accepted ?? data.paymentRequirements ?? {};
}
```

Replace every `const { paymentRequirements } = parsed.data;` with:
```typescript
const paymentRequirements = getPaymentRequirements(parsed.data);
```

### Step 4: Update the OpenAPI spec

Change the header name to canonical casing:
```yaml
x402Payment:
  type: apiKey
  in: header
  name: X-PAYMENT          # was X-Payment
  description: x402 payment proof header
```

## Verification Checklist

- [ ] Auto-payment service sends `x402Version: 2` (not 1)
- [ ] Facilitator body uses `accepted` key (not `paymentRequirements`)
- [ ] Payload uses `amount` field (not `maxAmountRequired`)
- [ ] Facilitator schema accepts both envelopes (backward compat)
- [ ] OpenAPI spec uses `X-PAYMENT` header name
- [ ] All existing tests pass (v1 clients still work via backward compat)

## Rollout Order

1. **Facilitator first** — update schema to accept both `paymentRequirements` and `accepted` (backward compatible, no breaking change)
2. **Client second** — update auto-payment service and any other clients to send v2
3. **Spec last** — update documentation headers

This order ensures no window where a v2 client talks to a v1-only facilitator.
