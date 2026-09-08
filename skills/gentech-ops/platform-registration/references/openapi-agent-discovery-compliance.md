# OpenAPI Agent-Discovery Compliance (AgentCash & OpenAPI-indexed directories)

**Proven Aug 20, 2026.** Getting listed on demand-side, OpenAPI-indexed directories
(AgentCash distributes to Claude/Cursor/Codex + every x402/MPP agent) requires the
`/openapi.json` spec to be per-endpoint complete. A generic catch-all
`/v1/{service}/{path}` path fails their probe.

## Why it matters
AgentCash discovery precedence (agentcash.dev/docs/discovery):
1. `/openapi.json` (primary index source)
2. Correct 402 header response (fallback)

So we already pass precedence #2 (correct 402 + `www-authenticate`). But a
spec that fails #1 means no pricing/discovery in the directory.

## The failure mode we hit
Our `/openapi.json` was a single generic `/v1/{service}/{path}` path with ONE
`x-payment-info`. AgentCash's probe then reports:
- **"Input/Output Schema Missing"** — no per-endpoint input/output schema
- **"No Payment Modes Detected"** — only one generic payment block
- **`x-discovery.ownershipProofs` missing**

## The compliant shape (rebuild openapi from the bazaar manifest)
Generate one path entry per paid service from the live bazaar manifest
(`SERVICES`), not a catch-all. Each paid path needs:
- `x-payment-info`: `{ price: { mode: "fixed", currency: "USD", amount: "<6dp>" }, protocols: [{ x402: {} }] }`
- `responses.402` (Payment Required) AND `responses.200`
- input `parameters` for path params (`{address}`, `{symbol}`, ...)
- a `requestBody` with a working `example` for body-based services (fixes
  "Expected 402, got 400")
- top-level `x-discovery: { ownershipProofs: [...] }` (e.g. `gentechlabs-erc8004-1770`)
- `openapi: "3.1.0"` (not 3.0.0)
- `info.title` / `info.contact.email` / `info.x-guidance` populated

## Implementation
In `x402-gateway/server.py`, the `/openapi.json` handler should loop `SERVICES`
and build one path per service with its real `price_usd`, stripped query params,
and extracted `{path_params}`. Skip services with no listed price
(treasury_defender has `price_usd: null`).

Verified result: **10 paid endpoints** each with `x-payment-info`, correct prices,
`x-discovery` present, openapi 3.1.0, and the 402 challenge still intact.

## General rule
When targeting ANY OpenAPI-indexed agent directory, check that `/openapi.json`
is per-endpoint and carries `x-payment-info` + input/output schema + `402`
response. If it's a generic catch-all, rebuild it from the manifest before
submitting. This is the difference between being priced-and-discoverable vs a
probe failure.
