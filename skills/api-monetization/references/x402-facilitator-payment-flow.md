# x402 Facilitator Payment Flow — Working Reference

> Verified against x402 v2 spec (Jul 5, 2026) and SDK v2.17.0.

## The Correct Architecture

```
Client (agent)          Resource Server (your API)         Facilitator
    │                          │                               │
    │── GET /api/data ────────►│                               │
    │                          │ (no X-PAYMENT header)         │
    │◄── 402 + accepts[] ──────┤                               │
    │                          │                               │
    │ (signs EIP-3009 auth)    │                               │
    │── GET /api/data ────────►│                               │
    │   Header: X-PAYMENT      │── POST /verify ──────────────►│
    │                          │◄── 200 (valid signature) ─────┤
    │                          │                               │
    │                          │ (process request)             │
    │                          │── POST /settle ──────────────►│
    │                          │◄── 200 (txHash, payer) ───────┤
    │◄── 200 + data ───────────┤                               │
```

**DO NOT** call a "Bazaar API" for payment. Bazaar = discovery only.

## The `accepts[]` Object (What Goes in Your 402 Response)

This is the contract between you and the client. Every field matters:

```python
ACCEPTS_BASE_USDC = {
    "scheme": "exact",                # or "upto", "batch-settlement"
    "network": "eip155:8453",         # CAIP-2 chain ID (8453 = Base)
    "asset": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",  # USDC on Base
    "amount": "10000",                # ATOMIC UNITS — 10000 / 1e6 = $0.01
    "payTo": "0x209693Bc6afc0C5328bA36FaF03C514EF312287C",
    "maxTimeoutSeconds": 60,
    "extra": {
        "name": "USDC",
        "version": "2",
    },
}
```

### Atomic Units Cheat Sheet (USDC, 6 decimals)

| Price | `amount` value |
|-------|----------------|
| $0.001 | `"1000"` |
| $0.01 | `"10000"` |
| $0.025 | `"25000"` |
| $0.05 | `"50000"` |
| $0.10 | `"100000"` |
| $1.00 | `"1000000"` |

### Common USDC Addresses

| Chain | CAIP-2 | Address |
|-------|--------|---------|
| Base | `eip155:8453` | `0x036CbD53842c5426634e7929541eC2318f3dCF7e` |
| Polygon | `eip155:137` | `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359` |
| Ethereum | `eip155:1` | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` |
| Arbitrum | `eip155:42161` | `0xaf88d6aE45CfbD88d3BF7fAa005373adDE66045B` |
| Optimism | `eip155:10` | `0x0b2C639c533813f4Aa9D7837CAf624AcD0296267` |

## Using Official SDK Middleware (Recommended)

### Python (FastAPI / ASGI)

```python
# pip install x402
from x402.python.middleware import x402_middleware
from fastapi import FastAPI

app = FastAPI()

# One-line middleware: handles 402 responses, header parsing, facilitator calls
x402_middleware(
    app,
    pay_to="0xYOUR_WALLET",
    facilitator_url="https://x402.org/facilitator",  # testnet
    # For production: use CDP, Corbits, Dexter, or self-host
)

@app.get("/api/data")
async def paid_data():
    # Middleware already verified + settled payment before reaching here
    return {"data": "your result"}
```

### TypeScript (Express)

```typescript
// npm install @x402/core @x402/evm @x402/express
import express from "express";
import { paymentMiddleware } from "@x402/express";

const app = express();

app.use(
  paymentMiddleware(
    {
      payTo: "0xYOUR_WALLET",
      facilitatorUrl: "https://x402.org/facilitator",  // testnet
    },
    {
      "GET /api/data": {
        accepts: [{ scheme: "exact", network: "eip155:8453", asset: "0x036CbD53842c5426634e7929541eC2318f3dCF7e", amount: "10000" }],
        description: "Token risk data",
      },
    }
  )
);

app.get("/api/data", (req, res) => {
  // Payment already verified + settled
  res.json({ data: "your result" });
});
```

## Manual Integration (When You Need Custom Logic)

See the `payment.py` and `server.py` code in the main SKILL.md — it shows the raw `/verify` + `/settle` calls without SDK middleware.

## Client Side: How an Agent Pays

If you're building the client (agent) that pays for x402 resources:

```python
# pip install x402 @x402/evm  (or use the Python x402 fetch wrapper)
from x402.python.fetch import wrap_fetch
import asyncio

# This wraps fetch/httpx to automatically handle 402 → pay → retry
fetch = wrap_fetch(
    account="0xYOUR_AGENT_WALLET_PRIVATE_KEY",
    network="eip155:8453",  # Base
)

async def call_paid_api():
    response = await fetch("https://api.example.com/api/data")
    # The wrapper automatically: got 402, signed payment, retried with X-PAYMENT
    return response.json()
```

Or manually with `@x402/axios` (TypeScript):
```typescript
import { axios as x402axios } from "@x402/axios";
// Same auto-pay behavior — intercepts 402, signs, retries
```

## MCP Transport (For Paid MCP Tools)

If your API is exposed as MCP tools instead of HTTP:

1. Client calls tool without payment → server returns `isError: true` + `structuredContent` with PaymentRequired
2. Client signs payment, retries tool call with payment in `_meta["x402/payment"]`
3. Server verifies via facilitator, executes tool, returns result with settlement in `_meta["x402/payment-response"]`

**Important (Jul 3 fix, PR #2774):** The MCP transport now matches against the client's selected `accept` entry, not `accepts[0]`. If you have custom MCP middleware that uses `accepts[0]` matching, upgrade to `@x402/mcp` v2.17.0+.

## Self-Hosting a Facilitator

For full control (no third-party dependency):

```bash
# Docker
docker run -p 3000:3000 \
  -e PRIVATE_KEY=0xYOUR_FACILITATOR_WALLET_KEY \
  ghcr.io/x402-foundation/facilitator:latest

# Or from source
git clone https://github.com/x402-foundation/x402
cd x402/typescript
pnpm install
pnpm --filter @x402/facilitator start
```

The facilitator exposes:
- `GET /supported` — lists supported networks/chains/tokens
- `POST /verify` — off-chain signature validation
- `POST /settle` — on-chain transfer execution

## Debugging Payment Failures

| Error | Cause | Fix |
|-------|-------|-----|
| `authorization_value_mismatch` | Client signed for wrong asset/amount | Check `accepts[]` matches what client received |
| 402 after payment | Facilitator `/settle` failed (insufficient gas, allowance) | Check facilitator wallet has ETH for gas; check Permit2 approval |
| DNS error on facilitator | Using dead `facilitator.x402.org` URL | Switch to `x402.org/facilitator` (testnet) or production facilitator |
| `null` field errors in MCP | Pre-v2.17.0 SDK emitting nulls | Upgrade `@x402/mcp` to 2.17.0+ (PR #2774) |

## References

- **Facilitator directory:** https://docs.x402.org/dev-tools/facilitators
- **Spec (v2):** https://github.com/x402-foundation/x402/blob/main/specs/x402-specification-v2.md
- **HTTP transport spec:** https://github.com/x402-foundation/x402/blob/main/specs/transports-v2/http.md
- **MCP transport spec:** https://github.com/x402-foundation/x402/blob/main/specs/transports-v2/mcp.md
- **Default assets (USDC addresses):** https://github.com/x402-foundation/x402/blob/main/DEFAULT_ASSETS.md
- **Market data + facilitator versions:** See `references/x402-market-data.md` under `strategic-resource-integration` skill
