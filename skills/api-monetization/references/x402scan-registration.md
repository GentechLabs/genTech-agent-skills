# Registering on x402scan — Discovery & Registration Flow

x402scan (x402scan.com) is the block explorer, analytics dashboard, and marketplace for x402 services. Registration requires a properly annotated OpenAPI spec — the scanner discovers paid endpoints by reading `x-payment-info` on each operation.

## Discovery Requirements

The scanner probes for an OpenAPI spec at these paths in order:
- `GET /openapi.json`
- `GET /.well-known/x402`

If neither exists with valid x402 annotations, the scanner reports "No discovery document found" and skips unprotected endpoints.

## Required OpenAPI Annotations

### Top-level fields (info)

```yaml
info:
  title: "Your API Name"
  description: "Description for agents"
  contact:
    email: "you@example.com"
  x-guidance: |
    High-level guidance explaining to an agent how to use your API.
```

### Per-endpoint x-payment-info

Each paid operation MUST include:

```yaml
paths:
  /v1/your-endpoint:
    get:
      x-payment-info:
        price:
          mode: "fixed"             # or "dynamic"
          currency: "USD"
          amount: "0.01"            # Decimal USD — display price
        protocols:
          - x402: {}
      responses:
        "402":
          description: "Payment Required"
```

**CRITICAL — amount units differ:**
- `x-payment-info.price.amount` = decimal USD (e.g., `"0.01"`)
- Runtime x402 v2 `accepts[].amount` = token atomic units (e.g., `"10000"` for $0.01 USDC)
- These are DIFFERENT units. The scanner compares consistency.

## Probe Behavior

When x402scan probes an endpoint:
1. Request WITHOUT payment → **HTTP 402** with valid challenge headers
2. The 402 must come BEFORE body/query validation rejects the request
3. `payment-required` header must contain valid base64 challenge
4. Runtime 402 behavior must match static OpenAPI metadata

## Registration Options

### A: Web UI
Go to x402scan.com → "Add your API" → enter origin URL. If annotations are correct, "Add" activates.

### B: API (agentcash MCP)
```bash
npx agentcash install
# Use fetch_with_auth to POST:
# POST https://x402scan.com/api/x402/registry/register-origin
# Body: { "origin": "https://api.yourdomain.com" }
```

### C: Validation CLI
```bash
npx -y @agentcash/discovery@latest discover "https://api.yourdomain.com"
npx -y @agentcash/discovery@latest check "https://api.yourdomain.com/v1/endpoint"
```

## Validation Checklist

- [ ] `GET /openapi.json` returns HTTP 200
- [ ] `info.contact.email` is present
- [ ] Every paid endpoint has `x-payment-info` + `responses.402`
- [ ] Runtime probe returns HTTP 402 with valid `payment-required` header
- [ ] Static amounts (USD decimal) match runtime amounts (atomic units)
- [ ] SIWX-only routes have NO `x-payment-info`
