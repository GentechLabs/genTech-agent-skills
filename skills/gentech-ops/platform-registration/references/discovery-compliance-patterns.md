# x402 Discovery-Compliance Patterns (proven Aug 20 2026)

Session evidence: OKX ASP rejection + AgentCash discovery compliance. These are the
concrete "what a platform's automated reviewer/crawler enforces" rules you must meet
BEFORE listing — pair with the DOCS-FIRST DOCTRINE at the top of SKILL.md.

## 1. OKX ASP (OnchainOS) — how approval review probes your endpoint

Read: `https://web3.okx.com/onchainos/dev-docs/okxai/registerasp`

An A2MCP/API service endpoint must be ONE of two compliant forms:
- **Form ① — free**: returns the result directly; no billing.
- **Form ② — x402 pay-per-call**: returns a standard `402 Payment Required`
  challenge, and after the user pays the request is replayed to fetch the result.

Rejection trap that cost us a cycle (Agent #2849, Aug 20):
- Service pointed at `/v1/defi/lp/{address}` (address-gated). OKX's automated
  probe calls the endpoint BARE (no valid `{address}`), so even after paying it
  can't produce qualified data → reviewer classifies as `HTTP 402 without
  qualified delivery`.
- **Fix:** repoint the A2MCP service to a form-② endpoint with a SIMPLE, known-valid
  input that returns real data on replay — e.g. `market_intelligence`
  (`/v1/market/price/{symbol}`). Service update is on-chain; then re-activate.

Also: OKX probes for "did not respond within 20 minutes" — the okx-a2a daemon MUST
be current. Fix stale daemon with `okx-a2a doctor --fix` (upgrades CLI, restarts,
then doctor shows N/N pass).

## 2. AgentCash — discovery-based, NO registration form
Read: `agentcash.dev/docs/sell-to-agents` + `/docs/discovery`

There is NO "submit your API" button. AgentCash indexes from the discovery contract.
Precedence: ① `/openapi.json` ② correct 402 header response. Once met, the origin is
registered on x402scan/mppscan automatically.

Requirements the crawler enforces (our spec initially FAILED these):
- `info.title`, `info.x-guidance`, `info.contact.email` present.
- **`x-payment-info` on EVERY paid endpoint** (we only had 2 of 9).
- **input AND output schema per operation** (generic `/v1/{service}/{path}`
  catch-all → `Input/Output Schema Missing`).
- `x-discovery.ownershipProofs` (we were missing it entirely).
- `responses.402` per endpoint.

**Verify end-to-end without waiting for their crawler:**
```bash
npx -y agentcash@0.17.0 discover "https://api.gentechlabs.net"
```
Expect `found: true`, `source: openapi`, `trustTier: ownership_verified`, and each
paid endpoint listed. (Note: `@agentcash/cli` is a login-only CLI, NOT the discover
probe — use the legacy unscoped `agentcash@0.17.0`.)

## 3. Build `/openapi.json` from the manifest, not a static dict
The reusable fix: generate per-service path entries dynamically from the live
manifest (`SERVICES`) so each paid endpoint carries its real `price_usd`, a 402
response, path-param schema, and (for body-driven services) a request body example.
- Skip services with `price_usd: null` (e.g. treasury_defender).
- Add `x-discovery.ownerships` at spec root.
- Add requestBody examples for services like `agent_research`/`deal_tracker` to fix
  `Expected 402, got 400` (probe needs valid input to reach the 402).
- Bump `openapi` to 3.1.0.

## 4. Settlement verification discipline
Before sending a real self-settle payment to prove the loop:
- Verify the treasury `payTo` wallet actually holds USDC on the settlement chain
  (`eth_call` balanceOf) — 0 USDC = cannot receive/confirm.
- Find a signer whose key derives to a wallet with spendable USDC + native gas.
- Do NOT hand-roll EIP-3009 `TransferWithAuthorization` against a real private key
  unless the user explicitly signs off on that path. Prefer a proven gasless client
  (Q402) or wait for a real buyer using their own wallet.
