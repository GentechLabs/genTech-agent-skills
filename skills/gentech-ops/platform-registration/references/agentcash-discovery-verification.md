# AgentCash / x402 Discovery Compliance — End-to-End Verification

**Proven Aug 20, 2026.** AgentCash is the primary "big boy" demand channel
(distributes to Claude, Cursor, Codex + every x402/MPP agent; 959K+ paid
calls). It has NO registration form — it is discovery-based.

## The definitive verification probe

```bash
cd /tmp && timeout 30 npx -y agentcash@0.17.0 discover "https://api.gentechlabs.net"
```

Returns the real end-to-end discovery result (same engine agents use). Read
`data`:
- `found: true` — origin discoverable
- `source: openapi` — picked up from `/openapi.json`
- `trustTier: ownership_verified` — highest tier (because `x-discovery.ownershipProofs` is read)
- `endpoints[]` with `authMode` — count paid endpoints (authMode != `unprotected`)
- `proofs: ["gentechlabs-erc8004-1770"]` — ownership proof read correctly

**A clean pass = `found:true, source:openapi, trustTier:ownership_verified`, all paid endpoints listed.** Any other result means the OpenAPI contract is not fully met.

> NOTE: `@agentcash/cli` (the scoped web-auth CLI) is NOT the probe — it only
> does login/whoami. Use the legacy `agentcash@0.17.0` package for discovery.

## Why the legacy OpenAPI spec failed (and the fix)

AgentCash's discovery precedence is ① `/openapi.json` ② correct 402 response.
Our old spec was a generic `/v1/{service}/{path}` catch-all with one
`x-payment-info` — AgentCash's probe fails that with **"Input/Output Schema Missing"**.

Fix: build `/openapi.json` **dynamically from the bazaar manifest** so each paid
service gets its own path entry with:
- real `x-payment-info.price.amount` (from `price_usd`, formatted `:.6f`)
- `x402` protocol
- `responses.402` (Payment Required)
- input `parameters` for path params (`{address}`, `{symbol}`, ...)
- a request body example for body-taking services (fixes "Expected 402, got 400")
- top-level `x-discovery.ownershipProofs`
- skip services with `price_usd: null`

Set `openapi` to `3.1.0`. See `01-HANDOFFS/agentcash-openapi-discovery.md`.

## The treasury-payTo monitoring rule (revenue MUST be scanned)

Buyer x402 settlements land in the **`payTo` address carried in the 402
challenge** — which is the TREASURY wallet, distinct from the signer/ops wallet.
Any revenue monitor that only scans the signer wallet will silently miss all
real buyer revenue.

For GenTech: signer/ops = `0x7ebff188...`, treasury/payTo = `0xF9dc...e734`.
The Revenue Monitor (`revenue-monitor.py`) now scans BOTH via
`WALLET_EVM` + `WALLET_EVM_TREASURY`, and treats signer↔treasury moves as
internal (not false revenue). Always confirm a monitor scans the 402 `payTo`
treasury address, or buyer settlements are invisible.

## Gateway host split (no Cloudflare edit needed)

- `api.gentechlabs.net` — NOT behind Cloudflare (direct VPS nginx). This is
  where x402 settlements happen; keep it direct so no CDN sits between buyers
  and the treasury payTo. Nothing to change.
- `gentechlabs.net` (main site) — behind Cloudflare; serves static discovery
  files (`skill.md`, `llms.txt`, `.well-known/*`). Only touch Cloudflare here
  for optional cache-bypass of discovery files, not required.
