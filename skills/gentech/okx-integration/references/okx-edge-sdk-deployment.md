# OKX-edge — Official OKX Pay SDK Edge (Phase 1 of the Sep 3 audit fix)

**When to use:** OKX.AI listing rejections that say "use the OKX official standard Pay SDK",
or when the challenge shape is compliant but the paid replay still fails. The durable fix is
NOT another gateway patch — it's a dedicated edge service wired to `OKXFacilitatorClient`.

## Why a separate edge (not a gateway patch)

Three rejections taught this. The generic gateway serves a multi-rail challenge (5 networks +
`extensions.bazaar`) that OKX's static check fails, AND even where the challenge is compliant,
OKX's SDK-paid proofs verify via the **OKX Broker** which our PayAI-verified replay path can't
confirm. The official SDK edge owns the EXACT registered URLs and verifies through the OKX
facilitator. Keep the generic gateway untouched for Dexter/CDP/PayAI/Bazaar traffic — two doors,
one backend.

## The SDK stack (verified working)

```bash
npm install @okxweb3/x402-express @okxweb3/x402-core @okxweb3/x402-evm express http-proxy-middleware
```

Key exports (verified):
- `@okxweb3/x402-core` → `OKXFacilitatorClient` (constructor takes `{apiKey, secretKey, passphrase}`)
- `@okxweb3/x402-express` → `paymentMiddleware`, `x402ResourceServer`
- `@okxweb3/x402-evm/exact/server` → `ExactEvmScheme`

## The compliant challenge shape (byte-identical to passing sellers)

- `x402Version: 2`, **single** `accepts` entry
- `network: eip155:196` (X Layer), `asset: 0x779ded0c9e1022225f8e0630b35a9b54be713736` (USDT0)
- `extra: {name: 'USD₮0', version: 1}`
- **no** `extensions` block
- `resource.url` = the exact probed URL (including bare path)
- envelope < ~1KB
- price as USD string `'$0.05'` (winner band 0.03–0.18; `0.005` was an outlier that got rejected)

## CRITICAL: register BOTH GET and POST for each path

OKX's validator probes the registered URL with **GET** (bare, no params). If the edge only
registers POST, GET returns 404 and the static check fails. Register both:

```js
const routes = {
  "GET /v1/market/price": { accepts: {...} },
  "POST /v1/market/price": { accepts: {...} },
  "GET /v1/security/score": { accepts: {...} },
  "POST /v1/security/score": { accepts: {...} },
};
```

## Audit-address pass-through ("do not intercept")

OKX's audit test address `0xbc59eb75C55e3bF1E63aaeE653C2b8E02BFd2033` sends free/small test
payments and must NOT be intercepted with verification logic. Add a middleware that bypasses
payment for that payer (match on `x-payer` / `x-wallet` header).

## systemd + nginx wiring

- systemd unit: `EnvironmentFile=/root/.hermes/profiles/gentech/.env` (loads OKX creds), `ExecStart`
  with the real node path (`/usr/local/node22/bin/node` — NOT `/usr/bin/node`), `Restart=always`.
- nginx: add `location /v1/market/price` and `location /v1/security/score` blocks proxying to the
  edge port (e.g. 8410) in BOTH the HTTP and HTTPS server blocks for `api.gentechlabs.net`.
  The generic `location /` still proxies to the main gateway (8090).

## Phase 2 — rewrite service definitions (never create duplicates)

- Use `operation:update` keyed by the existing service `id` — never `operation:create` a service
  whose name already exists (→ "Duplicate service names").
- **Two services in one ASP cannot share the same endpoint** (→ "endpoint duplicates ... within the
  same ASP"). Give each a distinct OKX-edge path (e.g. Market Intelligence → `/v1/market/price`,
  Token Security → `/v1/security/score`).
- A2MCP description is 4 lines (all REQUIRED or listing QA rejects):
  1. what the service does
  2. param spec — ALL key params on ONE line, `name(type, required/optional): meaning`
  3. request method (POST/GET)
  4. a working `curl` example using the real endpoint URL
- `fee` as a plain number string `'0.05'` (USDT implied).

## Phase 3 — pre-resubmission checklist (run ALL before activate; no blind relists)

1. **GET bare-path probe** (what OKX does) → must return 402, not 404
2. **POST-with-body probe** → same 402 shape
3. **Challenge shape** → single accepts, eip155:196, USDT0, no extensions, exact URL
4. **Envelope** < ~1KB
5. **Official CLI quote** → `onchainos payment quote <url> --method POST --param symbol=BTC`
   must succeed and issue a `paymentId`
6. **Real pay loop** → needs USDT on X Layer (eip155:196) in the OKX wallet; `hasBalance:false`
   blocks the actual settlement. Fund ~$0.05–0.10 before the full pay→replay→200 test.

## Funding the X Layer wallet for the pay loop (verified dead-ends)

The OKX wallet is the **same EVM address across all chains** (e.g. `0x24c3382f…bbd0f` on
Base, Avalanche, X Layer). To run the real pay loop you need the settlement stablecoin ON X
Layer at that address.

**You CANNOT bridge it from Base.** `onchainos cross-chain quote --from <usdc> --to <usdt0>
--from-chain base --to-chain xlayer --readable-amount 1 --receive-address <addr>` returns
`{"fallback":{"outcome":"no_path","message":"Insufficient liquidity"},"routerList":[]}`
for BOTH USDC→USDT0 and USDC→USDC_Bridged. The Base→X Layer bridge catalog has no live
liquidity for stablecoins. Do not waste time probing bridge routers — the stablecoin must be
sent **directly to X Layer** (e.g. from Coinbase if it supports X Layer as a withdrawal
network, or from a wallet that already holds it there).

X Layer USDC contracts (two distinct ones — do NOT confuse them):
- **Native USDC** (Circle's official, per Circle docs): `0xb6ceceab302e2e4948951ee7843fc24e92933061`
  (decimals 6; name/symbol read empty via `eth_call` because it's a proxy).
- **USDC_Bridged** (per OKLink): `0x74b7F16337b8972027F6196A17a631aC6dE26d22` (decimals 6).
The challenge asset is USDT0 `0x779ded0c…736` by default — confirm with the user whether
settlement should be USDC or USDT0 before changing it.

## Switching the settlement asset to USDC (non-obvious — the SDK hardcodes USDT0)

The `@okxweb3/x402-evm` SDK hardcodes USDT0 as the **default** asset for `eip155:196` in
`getDefaultAsset` (`DEFAULT_STABLECOINS["eip155:196"] = 0x779ded0c…736`). So you CANNOT switch
the asset by editing the route config's `network` or adding an `asset` field — the scheme falls
back to USDT0. To serve USDC you must pass an **explicit `AssetAmount` object as the `price`**
in each route's `accepts`:

```js
const USDC_ASSET = "0xb6ceceab302e2e4948951ee7843fc24e92933061"; // native USDC, X Layer
const PRICE = { amount: "50000", asset: USDC_ASSET, extra: {} }; // $0.05 in 6-decimals
// routes: accepts: { scheme: "exact", network: "eip155:196", payTo: PAYTO, price: PRICE }
```

`ExactEvmScheme.parsePrice` returns the object directly when `price` has an `amount` field
(and requires `asset` to be set), bypassing the default conversion. Verify the switch with the
official CLI: `onchainos payment quote <url> --method POST --param symbol=BTC` should now
report `Will pay 0.05 USDC (exact, X Layer)` with candidates `[('USDC', 'X Layer')]`.

**User preference (Jordan, Sep 7 2026):** settlement is in **USDC**, not USDT0 — "lets change it
to usdc to make it easy". Default to native USDC on X Layer for OKX-edge challenges unless the
user says otherwise.
7. **Responsiveness** → round-trip well under 20 min (target: seconds)
8. **Service defs** → `onchainos agent service-list --agent-id <id>` shows fee '0.05', POST
   endpoint, numbered description

### Priority — do NOT block the relist on the funded pay-loop test (Jordan, Sep 7 2026)

The goal is **getting listed**, not running a live settlement. If the user says they just want
to get the agents listed ("were just trying to get listed on OKX"/"I'm not in any challenge at
the moment"), do NOT hold the relist hostage to an unfunded/fundable pay-loop settlement test.

Checklist items 1–5 + 7 + 8 (probes, challenge shape, official-CLI quote, responsiveness, service
defs) are what the reviewer actually checks and are all runnable with zero funds. Item 6 (the
real pay loop) needs the settlement stablecoin ON X Layer and is only required if you're proving
live settlement. Sequence it as **nice-to-have, never a blocker**: ship the challenge + service
defs + daemon health, relist via `agent update`, and let settlement verification ride along when
the wallet is funded — don't ask the user to fund gas/stablecoin, bridge a dead-end path, or
explain settlement mechanics at length when they've said the target is the listing itself.
Do not over-rotate on wallet funding, bridge plumbing, or pay-loop mechanics when the user is
clearly signaling the review-stage goal.

## A2A daemon prerequisite

`onchainos agent update` fails with "A2A communication is not ready" until the daemon is upgraded
and healthy: `npm install -g @okxweb3/a2a-node@latest` then `okx-a2a doctor --fix` (target 10/10).
If it says "Start the daemon in-process", run `okx-a2a daemon stop` then `okx-a2a daemon start`.

## Repo

`GentechLabs/okx-edge` — server.mjs + phase2_update.py (the service-def rewrite script).
