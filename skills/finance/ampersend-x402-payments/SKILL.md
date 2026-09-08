---
name: ampersend-x402-payments
description: "Ampersend x402 payment integration for Hermes agents — MCP proxy setup, CLI usage, agent identity, spend guardrails"
version: 1.0.0
author: Gentech
license: MIT
tags: [x402, payments, ampersend, mcp, base, stablecoin, agent-payments]
---

# Ampersend x402 Payments

Ampersend enables autonomous agent payments via the x402 protocol. Agents make stablecoin payments within user-defined spending limits without requiring human approval per transaction.

## When to Use

- Agent needs to pay for API calls, data, or compute (x402 endpoints)
- Setting up or managing agent payment identity
- Configuring spend limits for autonomous agents
- Making paid HTTP requests via CLI or MCP tools

## Prerequisites

- `ampersend` CLI v0.0.16+: `npm install -g @ampersend_ai/ampersend-sdk@0.0.16`
- `ampersend-hermes` MCP proxy (built from source — npm package not published separately)
- Node.js 20+ for MCP proxy

## Agent Setup

### Existing Agent (manual config)

If you already have an agent key and account address:

```bash
ampersend config set "0xagentKey:::0xagentAccount"
# Returns: { "ok": true, "data": { "agentKeyAddress": "0x...", "agentAccount": "0x...", "status": "ready" } }
```

### New Agent (automated flow)

```bash
# Step 1: Generate key, request approval
ampersend setup start --name "my-agent" [--daily-limit "1000000"] [--auto-topup]
# Returns user_approve_url — show to user for approval

# Step 2: Poll for approval and activate
ampersend setup finish
```

### Verify Status

```bash
ampersend config status
```

## MCP Proxy Setup

The MCP proxy must be built from source (npm package not published):

```bash
cd /root/repos
git clone https://github.com/edgeandnode/ampersend-hermes.git
cd ampersend-hermes
npm install
npx tsc  # build
```

### Register in Hermes Config

Add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  ampersend:
    command: "node"
    args: ["/root/repos/ampersend-hermes/dist/mcp/proxy-cli.js"]
    env:
      AMPERSEND_AGENT_KEY: "0x..."
      AMPERSEND_AGENT_ACCOUNT: "0x..."
      AMPERSEND_NETWORK: "base"
    timeout: 120
    connect_timeout: 60
```

### Activate

After config changes, run `/reload-mcp` in Hermes chat (no full restart needed).

## CLI Commands

### fetch — Make paid HTTP requests

```bash
ampersend fetch <url>
ampersend fetch -X POST -H "Content-Type: application/json" -d '{"key":"value"}' <url>
```

**Always inspect before paying:**
```bash
ampersend fetch --inspect <url>
# Returns payment requirements and cost without charging
```

### config — Manage configuration

```bash
ampersend config status                                    # Show current status
ampersend config set --network base                        # Set network (base, base-sepolia)
ampersend config set --clear-api-url                       # Revert to production API
ampersend config set "0xkey:::0xaccount" --network base    # Set both at once
```

## Spend Guardrails

Set limits during setup or via dashboard:
- `--daily-limit <amount>` — atomic units (1000000 = 1 USDC)
- `--monthly-limit <amount>`
- `--per-transaction-limit <amount>`
- `--auto-topup` — auto-topup from main account

## Key Details

- **Network:** Base mainnet (default). Use `--network base-sepolia` for testing.
- **API:** Production at `https://api.ampersend.ai`. Sandbox at `https://api.sandbox.ampersend.ai`.
- **ERC-8004 Registry:** Agent can be published as discoverable on-chain.
- **Agent identity:** Each agent gets a key address (session key) and account address (smart account).

## x402B Escrow Awareness

The x402 ecosystem now has two payment modes:

- **Vanilla x402 (`exact` scheme)** — Push-only, pay-first. Buyer pays, payment is final. Fine for micropayments, API calls, low-trust transactions. **This is what Ampersend handles.**
- **x402B (`escrow` scheme)** — Boson Protocol's non-custodial escrow extension. Funds enter a Boson Diamond escrow at commit time; release after buyer signals delivery or dispute window expires. For high-value, deferred delivery, physical goods, pseudonymous sellers. **Ampersend does NOT support escrow — vanilla x402 clients see "unsupported scheme" and fail safely.**

When building agent commerce flows:
- Use Ampersend for x402 push payments (APIs, data, compute)
- Use x402B for anything requiring escrow, dispute resolution, or fulfillment guarantees
- Boson packages: `@bosonprotocol/x402-client`, `@bosonprotocol/x402-server`, `@bosonprotocol/x402-facilitator`
- x402B is an open standard contributed to the Linux Foundation x402 series (not a Boson silo)
- Testnet live on Base Sepolia; mainnet audit pending

## Building x402-Protected Endpoints

When you need to **serve** x402-protected APIs (not just consume them), return a proper x402 v2 402 response:

```typescript
// x402 v2: PAYMENT-REQUIRED header is base64-encoded JSON
function encodePaymentRequired(obj: Record<string, unknown>): string {
  return Buffer.from(JSON.stringify(obj)).toString('base64');
}

// In your middleware or route handler (HTTP 402):
const paymentRequired = {
  x402Version: 2,
  error: 'Payment required',
  accepts: [{
    scheme: 'exact',
    network: 'eip155:8453',  // Base mainnet
    payTo: '0xYourAddress',
    price: '1000000',         // atomic units (1 USDC)
    maxPrice: '1000000',
    description: 'Pay 1 USDC to access this API',
    mimeType: 'application/json',
  }],
};

return new Response(JSON.stringify({ error: 'Payment required' }), {
  status: 402,
  headers: {
    'Content-Type': 'application/json',
    'PAYMENT-REQUIRED': encodePaymentRequired(paymentRequired),
  },
});
```

**v1 vs v2:** x402 v1 put payment requirements in the response body as JSON. v2 moved everything to the `PAYMENT-REQUIRED` header (base64). Ampersend/fetch clients only parse v2 format — v1 body returns "Invalid payment required response".

**Payment signature header:** When a client retries with payment, they send a `payment-signature` header. Your server should forward this to the ampersend facilitator for verification, or trust it if you're running your own facilitator.

## Pitfalls

- **npm package doesn't exist:** `ampersend-mcp-proxy` is not published. Must build from `edgeandnode/ampersend-hermes` repo.
- **Sandbox vs mainnet:** `ampersend config set --network base-sepolia` points to sandbox. Always verify with `ampersend config status` and check `apiUrl` field.
- **Stale pending approvals:** Old expired approvals remain in config. They don't affect functionality but look messy.
- **Key format:** Config requires `0xagentKey:::0xagentAccount` — both the session key (private key) and the smart account address.
- **MCP proxy restart:** After config changes, run `/reload-mcp` in Hermes — don't restart the full gateway.
- **500 instead of 402:** When serving x402-protected endpoints with `@x402/hono` or `@x402/express`, missing payment headers cause unhandled exceptions → HTTP 500 instead of expected 402. Wrap payment middleware in error handler:
  ```typescript
  app.use("*", async (c, next) => {
    try {
      await next();
    } catch (error) {
      if (error.message.includes("x402") || error.message.includes("CDP") || error.message.includes("payment")) {
        return c.json({ error: "payment_required", message: "x402 payment required", pricing_url: "/pricing" }, 402);
      }
      return c.json({ error: "internal_error", message: error.message }, 500);
    }
  });
  app.use("*", paymentMiddleware(x402Routes, resourceServer));
  ```

## Buyer-Side vs Seller-Side

Ampersend is **buyer-side** — it lets our agents *pay* for APIs and compute. When we need to *accept* payments on our own endpoints, we use seller-side middleware:

- **PayAI Agent Payments SDK** — protocol-agnostic (x402 + MPP), Express middleware, dynamic pricing, lifecycle hooks. Best for Agent Arena marketplace. Repo: `PayAINetwork/agentic-payments`, tested at `/root/repos/agentic-payments/`. See `references/payai-sdk.md`.
- **Circle Gateway** — batched x402 settlement, gas-free micropayments. Best for high-frequency API monetization.
- **@x402/express** — open-source x402-only seller middleware.

## x402 Data Providers (Pay Catalog)

When agents need to pay for crypto market data, the Pay catalog has x402 alternatives:

| Provider | Data | Price | Endpoints |
|----------|------|-------|-----------|
| **StableCrypto** | CoinGecko prices, DefiLlama yields, Alchemy token data | $0.01/call | 105 |
| **CoinGecko Onchain DEX** | Token prices, trending pools, pool search | Free | 4 |
| **Nansen API** | On-chain analytics, smart money tracking | Varies | 56 |

**Note:** CoinMarketCap (CMC) has x402 support ($0.01/call) but is NOT yet in the Pay catalog. StableCrypto covers the same use case via CoinGecko data.

**Setup:** Run `pay setup` to configure the Pay account, then fund with USDC on Base or Solana.

## x402scan Discovery (Getting Your API Listed)

x402scan (x402scan.com) discovers APIs automatically by probing endpoints and parsing OpenAPI specs. To get listed:

1. **Return 402** for paid endpoints (see "Building x402-Protected Endpoints" above)
2. **Add `x402` annotations** to your OpenAPI spec for each paid endpoint
3. **Add `"security": []`** to free endpoints so x402scan skips them
4. **Add `info.contact`** to your OpenAPI spec (name, email, url)
5. **Override `app.openapi`** — FastAPI's built-in overwrites custom annotations if you don't override the function directly

Enter your API URL at x402scan.com/add — it auto-discovers everything.

**Full implementation guide:** `references/x402scan-compatibility.md` — includes FastAPI pattern, OpenAPI spec structure, common pitfalls, and verified working config.

## Related
- **ampersend-hermes repo:** `/root/repos/ampersend-hermes/`
- **AGENTS.md:** Security rules and usage patterns for the ampersend workspace
- **Hermes native-mcp skill:** MCP server configuration patterns
- **x402 ecosystem landscape:** `references/x402-ecosystem.md` — full mapping of x402 vs x402B, packages, competitive landscape
- **Agent Kit x402 Commerce Layer:** `references/agent-kit-x402-commerce-pattern.md` — payment + revenue + gateway three-module pattern for agent-to-agent commerce
- **PayAI SDK reference:** `references/payai-sdk.md` — tested patterns for Agent Arena integration
- **x402scan compatibility:** `references/x402scan-compatibility.md` — getting listed on the x402 block explorer
