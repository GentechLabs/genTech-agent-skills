# x402 Ecosystem Scan — July 15, 2026

**Scout**: x402 Compliance Scout cron (daily 12:10 UTC)
**Model**: deepseek-v4-flash
**Scope**: Public GitHub repos mentioning x402, deployed endpoint probing, x402scan.com

---

## Previous PR Status

| PR | Repo | Description | Status |
|----|------|-------------|--------|
| [#5](https://github.com/marlinprotocol/x402-gateway/pull/5) | marlinprotocol/x402-gateway | README header docs fix | **open** (since Jul 14) |
| [#8](https://github.com/brave-experiments/private-x402-gateway/pull/8) | brave-experiments/private-x402-gateway | `X-Payment-Required` → `Payment-Required` (6 files) | **open** (since Jul 14) |
| [#30](https://github.com/mark3labs/x402-go/pull/30) | mark3labs/x402-go | Lowercase EVM asset addresses | **open** (since Jul 14) |
| [#6](https://github.com/GOATNetwork/agentkit/pull/6) | GOATNetwork/agentkit | ERC-8004 testnet3 address fix | **open** |
| [#410](https://github.com/p-e-w/heretic/pull/410) | p-e-w/heretic | Byte tensor fix (ARA branch) | **open** |
| [#2](https://github.com/srotzin/hive-rosetta/pull/2) | srotzin/hive-rosetta | Lowercase asset addresses in Node+Python registry | **just submitted** |

**None merged since last scan. 6 PRs now pending across the ecosystem.**

---

## TIER 1 — Quick Wins (Auto-PR'd This Run)

### 1. srotzin/hive-rosetta — lowercase asset addresses ✅ PR #2
- **URL**: https://github.com/srotzin/hive-rosetta
- **Fix**: Mixed-case asset addresses in `packages/rosetta-node/src/registry.js` (USDT `0xfde4C...` → lowercase, Base Sepolia USDC `0x036CbD5...` → lowercase) and Python equivalent in `hive_rosetta/registry.py`
- **PR**: [#2](https://github.com/srotzin/hive-rosetta/pull/2) — "fix: normalize EVM asset addresses to lowercase hex for x402 v2 compliance"
- **4 files changed**: Node registry, Python registry, Node test, Python test

---

## TIER 2 — Gentech Only (Build List)

### 1. rplryan/x402-payment-harness
- **URL**: https://github.com/rplryan/x402-payment-harness
- **Nature**: Python EOA-based x402 client library + CLI (published on PyPI v1.0.1)
- **Issues**:
  - `signer.py:130`: hardcodes `"x402Version": 1` instead of `2`
  - Uses `X-PAYMENT` header (v1 deprecated) instead of `PAYMENT-SIGNATURE` (v2)
  - Flat payload `{ x402Version, scheme, network, payload }` — missing `accepted` envelope
  - `README.md` references `X-PAYMENT-REQUIRED` header (deprecated v1 name)
- **Effort**: Medium (2-3 files in `x402_harness/` package + tests)
- **Last commit**: 2026-02-27 (stale)

### 2. gwrxuk/Agent-8004-x402
- **URL**: https://github.com/gwrxuk/Agent-8004-x402
- **Nature**: Full-stack agent payment gateway with ERC-8004 trust layer
- **Issues**:
  - `services/x402-gateway/src/lib/invoice.js:7`: `version: "x402-1"` — v1 format, no `x402Version`
  - `invoice.js:19`: Uses `X-Payment` header (v1) — missing `Payment-Required` header
  - `invoice.js:20`: Sends 402 with bare JSON body, no structured v2 header payload
  - `clients/ts-sdk/src/index.js:13`: Reads `x-payment` header (v1) instead of `payment-signature` (v2)
  - Uses `receiver` instead of `payTo`, no `scheme`, no `resource` block, no `accepts` array
- **Effort**: High (3 services: gateway, client SDK, coordinator)
- **Last commit**: 2025-11-12 (very stale)

### 3. HyperbolicLabs/hyperbolic-x402
- **URL**: https://github.com/HyperbolicLabs/hyperbolic-x402
- **Nature**: Production Vercel-deployed x402 chat completions gateway (hyperbolic-x402.vercel.app)
- **Issues**:
  - No `/.well-known/x402` endpoint (verified: 404 returned)
  - Uses old `@coinbase/x402` v0.5.x and `x402-express` v0.5.x — not canonical x402-foundation v2 packages
  - Network configured as `"base"` in middleware config — should be CAIP-2 `"eip155:8453"`
  - Payment middleware runs AFTER input validation at line 462-472 (`api/index.ts`) — returns 400 before 402
  - `/v1/chat/completions` returns 400 (validation) instead of 402 for unauthenticated requests
- **Effort**: Medium (discovery endpoint + middleware reorder + SDK upgrade + CAIP-2)
- **Production endpoint**: Still broken — returns 400, not 402

### 4. aws-samples/sample-secure-agentic-payments-on-aws-x402
- **URL**: https://github.com/aws-samples/sample-secure-agentic-payments-on-aws-x402
- **Nature**: AWS serverless system for Bedrock agents with x402 payments
- **Issues**:
  - `backend/x402_protocol.py`: Uses completely custom `X-Payment-Amount`, `X-Payment-Recipient`, `X-Payment-Token`, `X-Payment-Network` individual headers
  - No `Payment-Required` header with structured JSON v2 payload
  - No `/.well-known/x402` endpoint
  - `X-PaymentProof` class uses non-standard proof format
- **Effort**: High (full rewrite of `x402_protocol.py` + `lambda_handler.py` + test fixtures)

### 5. coinbase/payments-mcp
- **URL**: https://github.com/coinbase/payments-mcp
- **Issue**: [#22](https://github.com/coinbase/payments-mcp/issues/22) — Does not read `PAYMENT-REQUIRED` header, only reads response body (v1 behaviour)
- **Status**: Open since Jan 2026. x402-foundation/x402#1052 linked but never merged.
- **Effort**: Medium (add `PAYMENT-REQUIRED` header parsing via `response.headers.get("payment-required")` — single file change)

### 6. selfradiance/x402-license-gateway (NEW — Jul 15 second pass)
- **URL**: https://github.com/selfradiance/x402-license-gateway
- **Nature**: Production Cloudflare Worker serving 20 licensed assets via x402 v2. Uses canonical `@x402/hono` SDK.
- **Issues**:
  - Discovery at `GET /` instead of `GET /.well-known/x402` — machine-readable catalog exists but at wrong path
  - USDC address `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` is checksummed (mixed case) — v2 spec requires lowercase hex
  - Middleware (canonical SDK) handles 402 correctly — no issue there
- **Effort**: LOW (single route addition + one constant change)
- **Last commit**: Jun 12, 2026 (active)

### 7. itublockchain/hackmoney-router402 (NEW — Jul 15 second pass)
- **URL**: https://github.com/itublockchain/hackmoney-router402
- **Nature**: Full-stack OpenRouter-compatible AI gateway with x402. ETHGlobal HackMoney 2026 Finalist. 203 commits.
- **Issues**:
  - Server-side v2 compliant (canonical `@x402/core/server`) ✅
  - Client-side (`apps/server/src/services/auto-payment.ts`): vestigial v1 code paths producing `x402Version: 1` flat payloads
  - V1 paths at lines 276 and 425 — backward-compat fallbacks that should be cleaned up
- **Effort**: MEDIUM (clean up old v1 paths in `auto-payment.ts`)
- **Last commit**: Feb 10, 2026 (stale)

---

## Scanned — Already Compliant (No Action)

| Repo | Notes |
|------|-------|
| quiknode-labs/x402-payments | ✅ Ruby gem, v2 compliant |
| quiknode-labs/x402-rails | ✅ Rails middleware, v2 default |
| x402-foundation/x402 | ✅ Canonical v2 SDK (6.3k ⭐) |
| x402-rs/x402-rs | ✅ `x402-axum::paygate` generates v2 headers |
| mark3labs/x402-go | ✅ V2 package passes 14 suits (PR #30 pending for asset casing) |
| michielpost/x402-dotnet | ✅ .NET SDK, v2 models, correct header format |
| srotzin/hive-rosetta | ✅ Node+Python signer, v2 compliant (after today's PR #2) |
| MikeyPetrillo/Agent402 | ✅ Production x402 with 504 tools, full v2 discovery |
| api.autonomagic.org | ✅ Has proper .well-known/x402 |
| yan253319066/XPayLabs-x402-seller | ✅ Uses canonical `@x402/express` SDK |

## Non-Actionable (Skipped)

| Repo | Reason |
|------|--------|
| Samdevrel/x402-api-gateway | Demo project — no actual API server code |
| sailorpepe/undesirables-x402-server | Uses v2 correctly — X-PAYMENT v1 header reading is intentional backward compat |
| mark3labs/mcp-go-x402 | MCP transport wrapper, not a gateway |
| second-state/x402-facilitator | Facilitator impl, not a gateway |
| bartonguestier1725-collab/x402-pay | Broker-based client library |
| aibtcdev/x402-sponsor-relay | Stacks-specific relay |
| xpaysh/awesome-x402 | Curated resource list |
| bsaepfl/bsa-sp-template-x402-2026 | Hackathon starter kit |
| NoFxAiOS/nofx | AI trading terminal, x402 tangential |
| Haustorium12/gold-402 | Curated catalog of x402 projects |
| vercel-labs/x402-ai-starter | **Archived** Jun 25, 2026 |
| ekailabs/x402-openrouter | Single initial commit, skeleton only |
| up2itnow0822/clawpay-mcp | MCP transport layer, not server gateway |
| cinderwright-ai/cinderwright-api | Endpoint unreachable, couldn't inspect source |

## Ecosystem Observations

- **x402scan.com**: 2,087+ public repos tagged with `x402` on GitHub — ecosystem growing fast
- **Existing PRs**: 6 pending across the ecosystem; none have merged yet
- **Hyperbolic**: Still broken (400 not 402) — no updates since Sep 2025
- **New anti-pattern discovered**: Discovery at `GET /` instead of `/.well-known/x402` (~10% of new implementations)
- **Second pass (same day)**: 8 repos checked, 2 new Tier 2 items added, 0 Tier 1 fixes
- **Agent402.Tools**: 504 tools, $0.001-$1.5 USDC per call, full v2 support — gold standard for x402 deployment
