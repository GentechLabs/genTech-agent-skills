# x402 v2 Reference — Format Comparison

## Syra's canonical Payment-Required header (known working)

Decoded from `api.syraa.fun`:

```json
{
  "x402Version": 2,
  "error": "Payment required",
  "resource": {
    "url": "https://api.syraa.fun/news",
    "description": "Curated crypto news articles...",
    "mimeType": "application/json",
    "serviceName": "Syra",
    "tags": ["agents", "x402", "crypto", "trading", "analytics"],
    "iconUrl": "https://api.syraa.fun/favicon.ico"
  },
  "accepts": [{
    "scheme": "exact",
    "network": "eip155:8453",
    "amount": "5000",
    "asset": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
    "payTo": "0xF9dcBFF7EdDd76c58412fd46f4160c96312ce734",
    "maxTimeoutSeconds": 60,
    "extra": {
      "name": "USD Coin",
      "version": "2",
      "eip712": { "name": "USD Coin", "version": "2" }
    }
  }],
  "extensions": {
    "bazaar": {
      "info": { "input": { ... }, "output": { ... } },
      "schema": { ... }
    }
  }
}
```

Key observations:
- `extra` block contains token metadata (name, version, eip712)
- `extensions.bazaar` carries OpenAPI-style input/output schemas
- `maxTimeoutSeconds: 60` is present on every accept entry
- Multiple networks in accepts[] — Syra supports 9+ chains

## Our fix (api.gentechlabs.net)

After the fix session on 2026-07-14, the header matches this structure with:
- `x402Version: 2`
- `scheme: "exact"`
- `payTo: "0x7EBff1DbD34172C5b55697654006C9642b5236a3"`
- `asset: lowercase hex`
- `maxTimeoutSeconds: 60`

## x402scan error progression

1. **"No valid x402 response found"** → 402 response format was wrong (v1 style)
2. **"Missing input schema"** → 402 format accepted, but OpenAPI params lacked details
3. **0 valid resources** → OpenAPI params need `required: false` + `default` values

The scanner caches results per URL. To force a fresh scan, navigate to the register page fresh.

## Syra marketplace registration

Email `support@syraa.fun` with template:

```
Service name: GenTech Labs API Suite
Website / API base URL: https://api.gentechlabs.net
Short description: AI agent infrastructure — token risk scoring, agent credit scores, gaming intelligence...
Category: DeFi / AI / Analytics
Pricing per call: $0.001-$0.10/call
Supported networks: Base, Solana
```
