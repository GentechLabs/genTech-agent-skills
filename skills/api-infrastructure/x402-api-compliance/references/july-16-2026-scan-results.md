# x402 Ecosystem Scan — July 16, 2026

**Scout**: x402 Compliance Scout cron (daily 12:10 UTC)
**Model**: deepseek-v4-flash
**Scope**: Public GitHub repos mentioning x402, deployed endpoint probing, x402scan.com ecosystem

---

## PR Status (from previous scans)

| PR | Repo | Description | Status |
|----|------|-------------|--------|
| [#5](https://github.com/marlinprotocol/x402-gateway/pull/5) | marlinprotocol/x402-gateway | README header docs fix | **open** (since Jul 14) |
| [#8](https://github.com/brave-experiments/private-x402-gateway/pull/8) | brave-experiments/private-x402-gateway | `X-Payment-Required` → `Payment-Required` (6 files) | **open** (since Jul 14) |
| [#30](https://github.com/mark3labs/x402-go/pull/30) | mark3labs/x402-go | Lowercase EVM asset addresses | **open** (since Jul 14) |
| [#2](https://github.com/srotzin/hive-rosetta/pull/2) | srotzin/hive-rosetta | Lowercase asset addresses (Node+Python) | **open** (since Jul 15) |
| [#423](https://github.com/strands-agents/tools/pull/423) | strands-agents/tools | payment-required header support in http_request tool | **MERGED** ✅ |

**4 PRs still pending across the ecosystem. strands-agents/tools #423 merged.**

---

## TIER 1 — Quick Wins (None This Run)

No Tier 1 fixes identified this run.

---

## TIER 2 — Gentech Only (Build List Updates)

### 1. HyperbolicLabs/hyperbolic-x402 — Still broken (400, not 402)
- **URL**: https://github.com/HyperbolicLabs/hyperbolic-x402
- **Probed**: `hyperbolic-x402.vercel.app/v1/chat/completions` returns HTTP 400, not 402
- **Root cause**: Input validation (Zod) runs before payment middleware inside route handler. Paywall never fires.
- **Issues**: Old `@coinbase/x402` SDK, no `/.well-known/x402`, human network names, validation-before-payment
- **Last commit**: 2026-02-24 (4 months stale)
- **Significance**: Production deployment with real traffic. This is the highest-value Tier 2 target.

### 2. smartcontractkit/x402-cre-price-alerts *(NEW)*
- **URL**: https://github.com/smartcontractkit/x402-cre-price-alerts
- **Nature**: Chainlink CRE demo: x402 payment for crypto price alerts via Gemini+OpenAI SDK
- **Issues**:
  - Uses deprecated `@coinbase/x402` SDK (`x402-express`, `x402`, `x402-fetch` packages), not canonical `@x402/*`
  - `x-payment` header (v1 deprecated) instead of `payment-signature` (v2)
  - `x-payment-response` header instead of v2 response format
  - Network `"base-sepolia"` (human name) not CAIP-2 `eip155:84532`
  - No `/.well-known/x402` endpoint
  - References old `x402.org` facilitator URL
- **Effort**: Medium (SDK swap + header rename + CAIP-2 + discovery endpoint)
- **Last commit**: 2026-02-24

### 3. itublockchain/hackmoney-router402 *(NEW)*
- **URL**: https://github.com/itublockchain/hackmoney-router402
- **Nature**: OpenRouter-compatible AI gateway with x402 micropayments (ETHGlobal HackMoney 2026 Finalist)
- **💡 Key pattern**: **Mixed v1/v2 monorepo** — server uses v2 correctly, client auto-payment uses v1
  - **Server (paid.ts)**: V2 compliant ✅ `@x402/core/server`, CAIP-2 `eip155:8453`, `payTo`, `scheme: exact`
  - **Auto-payment (auto-payment.ts)**: V1 ❌ `x402Version: 1` (line 425), `maxAmountRequired` (v1 field, line 281), flat payload without `accepted` envelope
  - **Settle body** (line 276): `x402Version: 1` — sent to the facilitator in v1 format even though the server generates v2 402 challenges
  - **OpenAPI spec**: References `X-Payment` header name (v1 deprecated)
  - **Header reading**: Reads `payment-required` header correctly ✅ (v2 name), but constructs payment in v1 format
- **Effort**: Low-Medium (update auto-payment.ts facilitator payload + OpenAPI header name)
- **Last commit**: 2026-02-10 (5 months stale)

---

## Already Compliant — Verified This Run

| Repo/Service | Notes |
|-------------|-------|
| **selfradiance/x402-license-gateway** | Full v2: `@x402/hono 2.14.0`, `ExactEvmScheme`, CAIP-2, Bazaar extension, 20 license routes. Discovery served at root `/` (human-readable) and `/.well-known/x402` (auto by SDK) |
| **Nexus Agent Services** *(new)* | **Gold standard**. 30+ endpoints at nexus-agent-xa12.onrender.com. Full v2 discovery with `paymentContextToken` per entry. CDP facilitator. Free tier endpoints. `x402Version: 2`, CAIP-2, lowercase asset, `payTo`, `scheme: exact`. See ecosystem-scanning-methodology.md for the `paymentContextToken` extension pattern |
| MikeyPetrillo/Agent402 | Production x402 with 504 tools, full v2 discovery |
| quiknode-labs/x402-payments | Ruby gem, v2 compliant |
| quiknode-labs/x402-rails | Rails middleware, v2 default |
| mark3labs/x402-go | V2 package (PR #30 pending for asset casing) |
| srotzin/hive-rosetta | Node+Python signer, v2 compliant |
| x402-rs/x402-rs | `x402-axum::paygate` generates v2 headers |
| x402-foundation/x402 | Canonical v2 SDK |

## Non-Actionable (Skipped/Verified)

| Repo | Reason |
|------|--------|
| google-agentic-commerce/a2a-x402 | Spec repo — defines A2A x402 extension protocol, not a server implementation |
| ekailabs/x402-openrouter | Stale — single commit, 11 months ago |
| vercel-labs/x402-ai-starter | Archived by owner (Jun 25, 2026) |
| x402-policy (x402-api-seven.vercel.app) | Vercel deployment not found — stale |
| Samdevrel/x402-api-gateway | Demo-only project |
| sailorpepe/undesirables-x402-server | V2 compliant; X-PAYMENT v1 header is intentional backward compat |

## New Patterns Documented

### Pattern: Mixed v1/v2 Monorepo
A repo can have v2-compliant server middleware while its client/auto-payment service still uses v1 payloads. The server reads `payment-required` (v2) and generates v2 402 responses, but when the auto-payment service constructs a payment to the facilitator, it sends `x402Version: 1`, `maxAmountRequired`, and a flat payload (missing `accepted` envelope). This creates a hidden compliance gap: the facilitator receives a v1-shaped payment and may misinterpret it.

**Detection**: Search for `x402Version: 1` separately in server/ and client/ directories. The server may never emit v1 but the client may still construct it.

**Fix**: Update client/auto-payment payload to `x402Version: 2` with `accepted: { scheme, network, amount, asset, payTo, maxTimeoutSeconds }` envelope.

### Pattern: paymentContextToken in Discovery
Production x402 deployments like Nexus Agent Services are including a `paymentContextToken` (UUID) in each entry of the discovery response's `accepts[]` array. This token is passed to the CDP facilitator to correlate payment sessions and is recommended for any gateway using the CDP facilitator.

The standard discovery format (defined in spec/v0.2) does not require this field, but it's becoming a de facto extension for CDP facilitator users.

---

## Part 2 — Jul 16 Run 2 (x402 Compliance Scout, 12:10 UTC)

### PR Audit — 29 Open PRs Checked

| Status | Count |
|--------|-------|
| Open, mergeable, no bot flags | 25 |
| Greptile flags already fixed (verified) | 2 (pay-skills #190, awesome-solana-ai #197) |
| Merged | 1 (strands-agents/tools #423) |
| Needs human attention | 0 |

### Key Verification: Greptile Fixes Were Already Pushed

**solana-foundation/pay-skills #190** — Greptile 4/5 confidence flagged:
- Missing query parameters in all 9 openapi.json files
- `per_request` inaccuracy on games-intel/movie-intel

Latest commit `2b45210` (Jul 16 08:13 UTC) is **newer** than the Greptile review (Jul 15 14:46 UTC). Verification showed all 9 specs now have `parameters` blocks with `required: false` + `default` values, and `per_request` corrected to `0.001`. Fix already pushed.

**solana-foundation/awesome-solana-ai #197** — Greptile flagged:
- Duplicate repo in two sections (both entries link to same repo)
- `gentech-agent-kit` out of alphabetical order
- `GenTech x402 Gateway` uses title-case label

Latest commit `56235fe` (Jul 16) consolidated to a single entry, fixed alpha order, removed the developer-tools duplicate. Verified via `git diff main..gentech-agent-kit -- README.md`.

### New SDK Audits

| Repo | Version | Compliance | Details |
|------|---------|------------|---------|
| **michielpost/x402-dotnet** | v2.2.0 (Jul 6) | ✅ V2 | `PaymentRequiredResponse` with `X402Version`, `Resource`, `Accepts`. `PaymentRequirements` has `Scheme`, `Network` (CAIP-2), `Amount`, `Asset`, `PayTo`, `MaxTimeoutSeconds`. Header: `PAYMENT-REQUIRED` (uppercase, HTTP case-insensitive). Attribute API uses `MaxAmountRequired` name but wire format uses correct v2 shapes. |
| **minhqdao/x402-dart** | new (Jul 16) | ✅ V2 | Canonical x402-foundation SDK structure (x402_core + x402_svm packages). `RouteConfig` with `accepts`. `PaymentOption` has `scheme`, `payTo`, `price`, `network` (CAIP-2). Facilitator client sends `x402Version` in requests. |

### Non-Actionable Added
- lemmaoracle/example-x402 (1⭐, example-only)
- up2itnow0822/agentpay-mcp (2 months stale)

### No New Compliance Gaps Found
All audited repos are either v2 compliant or non-actionable. Zero Tier 1 PRs needed for new discoveries. No build queue additions.
