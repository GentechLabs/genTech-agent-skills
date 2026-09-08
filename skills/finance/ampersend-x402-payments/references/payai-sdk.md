# PayAI Agent Payments SDK — Tested Reference

**Repo:** `github.com/PayAINetwork/agentic-payments`
**Local clone:** `/root/repos/agentic-payments/`
**Status:** Tested May 22, 2026 — SDK builds, 402 responses work across all testnets

## What It Is

Protocol-agnostic seller-side middleware. One integration accepts both **x402** (EVM + Solana) and **MPP** (Tempo) payments. Express middleware drops in with one line.

## Monorepo Layout

```
agentic-payments/
├── typescript/          ← @payai/agentic-payments (only shipping SDK)
├── examples/typescript/ ← runnable servers + clients + smoke tests
├── python/              ← placeholder (empty)
├── go/                  ← placeholder (empty)
```

**Key:** Python and Go are empty scaffolding. TypeScript is the only usable SDK.

## Build & Run

```bash
# 1. Build the SDK first (examples reference it via file:)
cd /root/repos/agentic-payments/typescript
npm install && npm run build    # tsup, ~2s

# 2. Install examples
cd /root/repos/agentic-payments/examples/typescript
npm install

# 3. Run any example (testnet by default, no real funds)
npx tsx 01-basic-express/server.ts
# → listening on :4000

# 4. Probe — unauthenticated request returns 402
curl -s -i http://localhost:4000/weather
```

## 402 Response Structure

Server returns **both** protocol challenges simultaneously:

- `PAYMENT-REQUIRED` header → base64 JSON (x402 v2 format)
- `WWW-Authenticate: Payment ...` header → MPP challenge (Tempo)

Decode x402 challenge:
```bash
curl -s -i http://localhost:4000/weather \
  | grep "PAYMENT-REQUIRED" \
  | sed 's/.*PAYMENT-REQUIRED: //' | tr -d '\r' \
  | base64 -d | python3 -m json.tool
```

## Testnet Chains (verified working)

| Chain | CAIP-2 | USDC Contract |
|-------|--------|---------------|
| Base Sepolia | eip155:84532 | 0x036CbD53842c5426634e7929541eC2318f3dCF7e |
| Avalanche Fuji | eip155:43113 | 0x5425890298aed601595a70AB815c96711a31Bc65 |
| Sei testnet | eip155:713715 | 0x4E4a29f76cD0dFf2A4e5E56d7a065E0aF33f32e2 |
| Polygon Amoy | eip155:80002 | 0x41E94Eb019C0762f9Bfcf9Fb1E58725BfB0e7582 |
| X Layer testnet | eip155:1952 | 0xcb8bf24c6ce16ad21d707c9505421a17f2bec79d |
| Rialo testnet | eip155:324705682 | 0x2e08028E3C4c2356572E096d8EF835cD5C6030bD |
| SKALE | eip155:2368 | 0x38129cf4CE5E183eFF248F42A7D345Bb1B47621A |
| Solana devnet | solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1 | 4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU |

Amounts: 10000 atomic units = $0.01 (6-decimal USDC). SKALE uses 18-decimal bridged USDC.

## Agent Arena Integration Patterns

### Basic middleware
```typescript
app.use(agentPayments({
  live: false,  // testnet until ready
  payTo: { evm: "0x...", solana: "..." },
  assets: ["USDC", "pathUSD"],
  endpoints: {
    "POST /agent/execute": { price: "$0.01", description: "Execute agent action" },
    "GET /agent/marketplace": { price: "$0.005", description: "Browse marketplace" },
  },
}));
```

### Dynamic pricing (tiering)
```typescript
endpoints: {
  "POST /agent/execute": {
    price: (ctx) => ctx.query.tier === "pro" ? "$0.02" : "$0.01",
    description: "Execute action — tiered pricing",
  },
}
```

### Marketplace (per-seller routing)
```typescript
endpoints: {
  "GET /marketplace/:seller": {
    price: "$0.01",
    description: "Pay seller directly",
    payTo: (ctx) => SELLERS[ctx.path.split("/").pop()],
  },
}
```

### Lifecycle hooks (game state integration)
```typescript
hooks: {
  onPaymentVerified: (ctx) => { /* log, validate game state */ },
  onPaymentSettled: (ctx) => { /* trigger inventory update, reputation */ },
  onPaymentFailed: (ctx) => { /* retry logic, deny action */ },
  onRequest: (ctx) => {
    if (ctx.request.headers["x-internal-key"] === KEY) return { grant: true };
  },
}
```

## Pitfalls

1. **Must build SDK before examples** — examples use `"file:../../../typescript"` dependency. Run `npm run build` in typescript/ first.
2. **Solana payTo needs ATA** — the `payTo` Solana address must have an existing USDC Associated Token Account. Default address `H32Ynqbz...` has ATAs pre-created on devnet/mainnet.
3. **Default is testnet** — `live: false` (or omitted) means no real funds. Must set `live: true` explicitly for mainnet.
4. **SKALE uses 18 decimals** — different from standard 6-decimal USDC. The SDK handles this via the asset registry, but be aware if custom-pricing.
5. **Express 5 compatible** — works with both Express 4 and 5.
