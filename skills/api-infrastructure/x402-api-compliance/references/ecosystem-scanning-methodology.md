# x402 Ecosystem Scanning Methodology

## Reference implementation: Syra (api.syraa.fun)

The compliance gold standard. Both `/.well-known/x402` and 402 responses are fully V2-compliant.

**Well-known structure:**
```json
{
  "version": 1,
  "resources": ["https://api.syraa.fun/brain", "..."],
  "resourceDetails": [{"url": "...", "name": "...", "description": "...", "price": 0.005}],
  "metrics": "https://api.syraa.fun/api/metrics",
  "liveFeed": "https://api.syraa.fun/api/live/calls",
  "freeTier": { "pillars": "...", "assets": "...", "prices": "...", "dossierBasic": "..." },
  "baseGateway": {
    "enabled": true, "network": "eip155:8453", "networkLabel": "Base Mainnet",
    "asset": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913", "assetLabel": "USDC",
    "payTo": "0xF9dcBFF7EdDd76c58412fd46f4160c96312ce734",
    "gatewayUrl": "https://api.syraa.fun",
    "discoveryUrl": "https://api.syraa.fun/.well-known/x402",
    "openapiUrl": "https://api.syraa.fun/openapi.json",
    "facilitators": ["coinbase-cdp", "payai", "thirdweb"]
  },
  "ownershipProofs": ["0x..."],
  "instructions": "# SYRA API Documentation..."
}
```

**402 Response (decoded from `Payment-Required` header):**
```json
{
  "x402Version": 2,
  "error": "Payment required",
  "resource": { "url": "...", "description": "...", "mimeType": "application/json", "serviceName": "Syra", "tags": ["x402", "crypto"] },
  "accepts": [{
    "scheme": "exact",
    "network": "eip155:8453",
    "amount": "1000",
    "asset": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
    "payTo": "0xF9dcBFF7EdDd76c58412fd46f4160c96312ce734",
    "maxTimeoutSeconds": 60,
    "extra": { "name": "USD Coin", "version": "2", "eip712": { "name": "USD Coin", "version": "2" } }
  }],
  "extensions": { "bazaar": { ... }, "builder-code": { ... } }
}
```

Key: Syra supports 9+ chains (Base, Solana, Polygon, Arbitrum, Avalanche, Sei, XRPL EVM, BNB, Algorand).

## Batch testing script

```python
import subprocess, json

endpoints = [
    ("name", "https://target.example.com/protected-endpoint"),
]

for name, url in endpoints:
    # Layer 1: well-known
    r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", url.replace("/protected", "/.well-known/x402")])

    # Layer 2-4: 402 response
    r = subprocess.run(["curl", "-s", "-D", "/tmp/h.txt", "-o", "/tmp/b.json", url],
                       capture_output=True, text=True, timeout=10)

    # Check headers
    with open("/tmp/h.txt") as f:
        headers = f.read()
    has_pr = "payment-required" in headers.lower()
    has_xp = "x-payment" in headers.lower()

    # Decode Payment-Required header
    for line in headers.split("\n"):
        if "payment-required" in line.lower() and ":" in line:
            b64 = line.split(":", 1)[1].strip()
            decoded = base64.b64decode(b64)
            payload = json.loads(decoded)
            print(f"x402Version: {payload.get('x402Version')}")
            print(f"accepts[0].network: {payload['accepts'][0]['network']}")

    # Read body
    with open("/tmp/b.json") as f:
        body = f.read()
    try:
        d = json.loads(body)
        # Check body format compliance
    except:
        pass
```

## July 2026 scan results: implementations ranked

### Tier 1: Fully V2-compliant
- **Syra** (api.syraa.fun) — Gold standard. Everything matches the spec.

### Tier 2: Near-compliant (1-2 issues)
- **JarvisClaw** (api.jarvisclaw.ai) — V2 headers, CAIP-2 networks, x402Version: 2. Minor: missing `instructions` block in body, `maxTimeoutSeconds` only in header payload.
- **twit.sh** (x402.twit.sh) — V2 format correct. Issue: still exposes deprecated `X-PAYMENT` header alongside `PAYMENT-REQUIRED`, well-known is missing `resourceDetails` + `baseGateway`.
- **x402-rs SDK** — Middleware generates V2-compliant `Payment-Required` header. Design choice: V2 returns empty body.
- **mark3labs/x402-go** (Go SDK) — Dual-package layout (v1 root, v2/ subdirectory). V2 passes all tests. Missing: `/.well-known/x402` route; ships checksummed asset addresses instead of lowercase hex.

### New Discoveries — July 2026
- **circlefin/arc-nanopayments** — Surprisingly V2-compliant. Uses `x402Version: 2`, `scheme: "exact"`, CAIP-2, proper `payTo` and `maxTimeoutSeconds`. Notable: uses Circle Gateway batching with `extra.verifyingContract`. Arc testnet only.
- **brave-experiments/private-x402-gateway** — TypeScript. Uses OHTTP relay + Privacy Pass + Solana devnet. Privacy-focused architecture. 2 stars, 18 commits.
- **t54-labs/x402-secure** — Python risk layer for x402 (Trustline integration). 28 stars. Has protocol-spec/ dir with OpenAPI.
- **aws-samples/sample-secure-agentic-payments-on-aws-x402** — AWS reference architecture with x402 payment adapter abstraction. 4 stars.
- **fardinvahdat/x402trace** — x402 debugger CLI. Probe, validate, explain, reconcile on Base. 4 stars.
- **Merit-Systems/x402email** — Pay-per-send email via x402 protocol.
- **0xsupremedev/solwave-x402-adk** — Agent Development Kit with x402 support.
- **mark3labs/mcp-go-x402** — MCP Go transport. Still on v1 (X402Version: 1, MaxAmountRequired, base-sepolia). Not migrated to v2 yet.

### Tier 3: Partial (missing discovery)
- **Marlin Gateway** (marlinprotocol/x402-gateway) — Uses x402-rs middleware so 402 flow is V2 compliant. Missing `/.well-known/x402` route. Config uses human network names (converted internally to CAIP-2). **Crate version gap:** pins x402-rs at 1.3.0 (latest is 2.0.2) — V2 `PaymentRequired` is missing the `extensions` field. Config field named `payment_address` maps correctly to wire field `payTo` via the V2Eip155Exact API. README documents the header as `` `payment-required` `` (lowercase) but the actual header is `Payment-Required` (canonical). See `references/x402-rs-crate-internals.md`.
- **StableEnrich** (stableenrich.dev) — Has `resources[]` in well-known but missing `baseGateway` and `resourceDetails`. Not actually returning 402.
- **agentutility.ai** (x402.agentutility.ai) — Well-known is only `ownershipProofs`. Missing version, resources, baseGateway.

### Tier 4: Custom format
- **2s.io** — Has `x402Version: 2` in well-known but uses custom structure (`service`, `capabilities`, `authentication`) instead of `baseGateway` and `resourceDetails`.

### Tier 5: Not x402-implemented
- **OneSource** (api.onesource.io) — Returns 401 (API key required), not 402. Has well-known description stub but no actual x402 flow.

## Ecosystem stats (from x402scan.com, July 2026)
- Total transactions (30d): 18.64M (growing ~10K/day)
- Total volume (30d): $862.67K
- Buyers (30d): 57.43K
- Sellers (30d): 47K
- Active merchants (24h): 4.52K
- Registered merchants: 54
- Largest seller: BlockRun ($175.16K volume, 15.47M txns))
- Most-used server list: BlockRun → claw402 → Vishwa → Otto AI → twit.sh → Cluster Protocol → Syra

## Key SDKs and their compliance characteristics

| SDK | Middleware | V2 header | V2 well-known | Notes |
|-----|-----------|-----------|---------------|-------|
| x402-rs (Rust) | x402-axum | ✅ header | ❌ Not included | Body empty on V2 |
| x402-foundation (TS) | @x402/express, @x402/hono, @x402/next | ✅ | ✅ via Bazaar ext | Canonical, 6.3k ⭐ |
| x402-foundation (Python) | FastAPI/Flask middleware | ✅ | ✅ via Bazaar ext | Uses `x402ResourceServer` |
| mark3labs/x402-go (Go) | net/http + Gin + MCP | ✅ | ❌ Not included | Ships checksummed asset addrs |
| circlefin/arc-nanopayments (TS) | Next.js | ✅ | ❌ Not included | Uses Circle Gateway batching |
| mark3labs/mcp-go-x402 (Go) | MCP transport | ❌ V1 | ❌ Not included | Not yet migrated to v2 |

## Tools for compliance auditing

- **x402-check** (`github.com/suryast/x402-check`) — CLI + npm library + GitHub Action. Validates any endpoint's `Payment-Required` header. **Known issue (PR #12 pending):** checks deprecated `x-payment-required` header first instead of `payment-required` (v2 canonical). Patch swaps header priority and fixes validator to accept `amount` vs `maxAmountRequired`.
- **x402trace** (`github.com/fardinvahdat/x402trace`) — x402 debugger CLI. Probe, validate, explain, reconcile on Base.

## Common PR fix templates

### Adding /.well-known/x402 (Express)
```typescript
app.get('/.well-known/x402', (req, res) => {
  res.json({
    version: 1,
    resources: ['https://api.example.com/endpoint1'],
    resourceDetails: [{ url: 'https://api.example.com/endpoint1', name: 'My Endpoint', description: '...', price: 0.001 }],
    baseGateway: {
      enabled: true,
      network: 'eip155:8453',
      networkLabel: 'Base Mainnet',
      asset: '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913',
      assetLabel: 'USDC',
      payTo: '0xYourAddress',
      gatewayUrl: 'https://api.example.com',
      discoveryUrl: 'https://api.example.com/.well-known/x402',
      openapiUrl: 'https://api.example.com/openapi.json',
      facilitators: ['coinbase-cdp', 'x402.org']
    }
  });
});
```

### Adding /.well-known/x402 (Rust/Axum)
```rust
use axum::routing::get;
use serde_json::json;

async fn well_known_x402() -> impl IntoResponse {
    Json(json!({
        "version": 1,
        "resources": ["https://api.example.com/endpoint"],
        "resourceDetails": [{"url": "https://api.example.com/endpoint", "name": "...", "description": "...", "price": 0.001}],
        "baseGateway": {
            "enabled": true,
            "network": "eip155:8453",
            "networkLabel": "Base Mainnet",
            "asset": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
            "assetLabel": "USDC",
            "payTo": "0x...",
            "gatewayUrl": "https://api.example.com",
            "discoveryUrl": "https://api.example.com/.well-known/x402",
            "openapiUrl": "https://api.example.com/openapi.json"
        }
    }))
}

// Register: .route("/.well-known/x402", get(well_known_x402))
```
