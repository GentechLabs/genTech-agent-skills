---
name: x402-api-compliance
description: Audit, fix, and deploy x402 v2 compliant APIs. Covers Payment-Required header format, /.well-known/x402 discovery, OpenAPI schema requirements, x402scan/Syra marketplace registration, and Cloudflare Worker deployment.
category: api-infrastructure
tags: [x402, api-gateway, payments, compliance, cloudflare]
---

# x402 API Compliance

Makes any API server pass the x402 v2 protocol spec. Agents discover and pay via x402.

> **Multi-facilitator debugging:** see `references/multi-facilitator-rails.md` — probed rail map for PayAI/Dexter/GoPlausible/CDP (Aug 2026), client-compatibility pitfalls (ASCII-only challenge envelopes, `accepts[0]` ordering with Base first, self-pay rejection, npm stale-resolve), and the end-to-end settle verification loop.

## When to use

- An API returns 402 but x402scan shows "No valid x402 response found"
- Adding `/.well-known/x402` endpoint for agent discovery
- Registering on x402scan, Syra marketplace, or other x402 directories
- Deploying or updating an x402 gateway on Cloudflare Workers
- **Auditing third-party x402 APIs for compliance** — scanning the ecosystem to identify gaps in other implementations before integration or PR contributions

## Two approaches to compliance

| Approach | When to use | Effort |
|----------|------------|--------|
| **AgentCash Router** (`@agentcash/router`) | Building a new Node.js API or wrapping an existing Express/Next.js/Hono/Bun app | 10 min — drop-in library |
| **Hand-rolled** (via `@x402/express`, `@x402/hono`, `@x402/core`, or language-native SDK) | Non-Node.js runtime (Python, Rust, Go), Cloudflare Workers, or need full control over 402 response shape | 1-3 hours |

> **Nginx static serving:** Discovery endpoints (`/.well-known/x402`, `/.well-known/x402-bazaar`) can be served from static files via nginx instead of proxying to a live backend. See `references/bazaar-manifest-nginx-deployment.md` for the config pattern and why this is more reliable.

**Recommended: AgentCash Router for Node.js projects.** Built by Merit Systems, tested against tens of thousands of endpoints. Handles 402 challenges, settlement, x402scan discovery indexing, and wallet identity automatically.

## The facilitator ↔ rail matching map ("the matching game")

Multiple facilitators, multiple rails — each facilitator only settles the rails it's wired
for. Getting listed/settled is a **matching problem**: CDP↔Base/Bazaar, GoPlausible↔Base/Solana/Algorand,
PayAI↔Avalanche/XLayer (+7 more), Dexter↔OpenDexter. CDP Bazaar and OpenDexter are **separate catalogs**
— a CDP settlement does NOT list you on OpenDexter. Full map, decision rule, diagnostic
sequence (incl. the simulation-overwrite bug + stale-process env check), and indexing-lag
expectations: **`references/facilitator-rail-matching.md`**.

**Live `/supported` probe results (Aug 30, 2026 — re-probe before wiring; endpoints drift):**

| Facilitator | x402 v2 rails settled | Notes |
|---|---|---|
| **PayAI** (`facilitator.payai.network`) | Base 8453, Avalanche 43114, Polygon 137, **X Layer 196**, Arbitrum 42161, SKALE 1329/713715, Solana 5eykt4…/EtWTRABZ… | Settles **every rail GenTech advertises** — the universal fallback. v1 also supported (16 nets) |
| **Dexter** (`x402.dexter.cash`) | Base, Avalanche, Polygon, Arbitrum, OP 10, BSC 56, World 480, Monad 143, Winners 4663, Solana — **NO X Layer** | Schemes: `exact`/`upto`/`batch-settlement`/`tab`/`bridge`. Gas-sponsored. **Their SDK cannot parse an X Layer-only challenge** (`unsupported_network`) |
| **GoPlausible** (`facilitator.goplausible.xyz`) | Base, Base Sepolia, Solana mainnet+devnet, Algorand mainnet+testnet | Smallest coverage; required for Algorand (x402 Global Challenge) |
| **CDP** (`api.cdp.coinbase.com`) | Base (proven Aug 19+30) | JWT auth; `/supported` needs auth — probe returns `Unauthorized`; rejects self-pays (see pitfall below) |

Probe command: `curl -s https://facilitator.payai.network/supported | python3 -c "import json,sys; [print(k.get('x402Version'), k.get('scheme','exact'), k.get('network')) for k in json.load(sys.stdin)['kinds']]"`

## Multi-network facilitator coverage — the "traffic but no revenue" audit

**The #1 revenue-killer to check first when traffic is up but settlements are zero:** a gateway that advertises services on chains where it has **no wired facilitator + payTo**. Clients on those chains get the 402 challenge, try to pay, the gateway rejects the proof (or never advertises the rail), and they bounce. **Traffic without matching revenue almost always means the funnel breaks at the settlement step, not discovery.**

**The rule (Jordan directive, Aug 7 2026):** before deploying an x402 service on any network, confirm a facilitator is available for that network AND wire it in. Never advertise a rail you can't settle. The registry (AgentScan) makes you findable; the facilitator makes you payable — they go together.

### The audit — check every advertised chain has a settleable rail

1. **Read the gateway's `NETWORKS` registry** (the CAIP-2 map). Each entry needs a `payto_env` + a configured `payTo`. A network with an empty `payTo` is dropped by `enabled_networks()` — it's advertised nowhere.
2. **Decode the live 402 `accepts[]`** — this is ground truth for what's actually advertised:
   ```bash
   curl -s -D - https://api.yoursite.com/v1/score/0x0 | grep -i payment-required | sed 's/^[Pp]ayment-[Rr]equired: //' | tr -d '\r' | base64 -d | python3 -c "import json,sys; [print(a['network'], a['payTo']) for a in json.load(sys.stdin)['accepts']]"
   ```
3. **Cross-reference against where you're LISTED** (AgentScan, ERC-8004 identities, marketplaces). If you're listed on Avalanche but `accepts[]` has no `eip155:43114`, that's the revenue leak.
4. **Confirm the facilitator supports the chain** before wiring: `curl https://facilitator.payai.network/supported` returns the network list.

**Confirmed Aug 7, 2026:** GenTech's gateway only advertised Base + Algorand while being listed on AgentScan (Avalanche) with ERC-8004 identities on XLayer. Avalanche clients literally could not pay — a major cause of the traffic-without-revenue gap. Fix: added the Avalanche rail + PayAI facilitator (below).

### Adding a new EVM rail via the PayAI facilitator (the pattern)

PayAI (`facilitator.payai.network`) is the #2 x402 facilitator by volume, free tier $0/mo up to 10K settlements/mo then $0.001/tx, no API key, 16 networks (Base, Avalanche, X Layer, Solana, Polygon, Arbitrum, Sei, SKALE + testnets). It's the natural rail for Avalanche/X Layer.

1. **Add the network to `NETWORKS`** (CAIP-2, native USDC asset, 6 decimals, `payto_env`):
   ```python
   "avalanche": {
       "network": "eip155:43114",
       "asset": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",  # native USDC on Avalanche C-Chain
       "decimals": 6,
       "payto_env": "X402_PAYTO_AVALANCHE",
       "payto_default": "",
       "extra": {"name": "USD Coin", "version": "2"},
   },
   ```
2. **Add a `verify_proof_via_payai()`** — mirror the GoPlausible path: POST `{paymentPayload, paymentRequirements}` to `{PAYAI_FACILITATOR}/verify` (expect `{isValid, invalidReason}`), then `/settle` (expect `{success, transaction}`). Same envelope as CDP/GoPlausible.
3. **Route by proof network** in the verify dispatch: `is_avalanche = proof_network == "eip155:43114"` → `verify_proof_via_payai`.
4. **Set the payTo** in env (`X402_PAYTO_AVALANCHE=<owner wallet>`) and add the network to `X402_NETWORKS="base,algorand,avalanche"`.
5. **Restart the gateway** (systemd re-reads `.env` — see the stale-credential pitfall below) and re-decode `accepts[]` to confirm the new rail is advertised.
6. **Add a test** asserting the rail appears when payTo is set and is dropped when it's empty (never advertise a rail you can't settle).

**PayAI verify/settle envelope** (from docs.payai.network/x402/reference): `/verify` returns `{isValid, invalidReason, invalidMessage}`; `/settle` returns `{success, transaction, network, payer}`. Avalanche mainnet = `eip155:43114`, Fuji = `eip155:43113`. Native USDC on Avalanche C-Chain = `0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E`.

## The receive side — accepting standard payments (the wall, not the door)

A gateway that returns a spec-perfect 402 is only half the job. If it can't **receive** the standard proof, every visiting agent bounces: find us → hit endpoint → 402 challenge → try to pay → proof rejected → 402 again → give up. **Zero traction despite full discovery is the signature of a receive-side bug, not a demand problem.** Always test the FULL loop, not just the 402 emission:

```
discovery → 402 challenge → pay/sign → retry with Authorization: x402 <proof> → HTTP 200 with data
```

### Stacked receive-side bugs (GenTech gateway, Aug 2026 — the real customer blocker)

The production gateway had THREE independent bugs, any one of which blocked payment. Fix in this order:

1. **Wrong payment header read.** Gateway read a private `x-402-token` header. Standard x402 v2 clients send `Authorization: x402 <json>`; the older convention is `X-Payment`. Every real client's proof was ignored → always 402.
   ```python
   def extract_proof(request) -> str | None:
       auth = request.headers.get("Authorization", "")
       if auth.lower().startswith("x402 "):
           return auth[5:].strip()
       xpay = request.headers.get("X-Payment") or request.headers.get("X-PAYMENT")
       if xpay:
           return xpay.strip()
       legacy = request.headers.get("x-402-token") or request.headers.get("X-402-Token")
       return legacy.strip() if legacy else None
   ```

2. **Proxy path mangling.** Even with a valid proof, the proxy stripped `/v1/` and forwarded wrong paths → backend 404. FastAPI route `/v1/{service}/{path:path}` delivers `path` WITHOUT the leading service segment (e.g. `score/0x...` for `/v1/security/score/0x...`). Map public prefix → backend prefix explicitly:
   ```python
   # manifest service key -> (backend base, public path prefix, backend path prefix)
   BACKEND_ROUTES = {
       "token_security": ("http://127.0.0.1:8088", "score/", "/v1/score/"),
       "market_intelligence": ("http://127.0.0.1:8082", "price/", "/v1/price/"),
   }
   ```
   Strip `public_prefix` from `path`, then prepend `backend_prefix`.

3. **Routing-table mismatch with the manifest.** The `/.well-known/x402-bazaar` manifest advertised 6 services but the gateway only routed 2 with live backends (the rest hit a stub `{"status":"available","paid":true}` — worse than a 404). **The manifest must only list services with live, correctly-routed backends.** Advertising phantom endpoints burns reputation exactly when you're asking others to trust your compliance.

### Pass the proof through to backends

Backends often have their own payment gate (e.g. rugcheck's MVP accepts any non-empty `X-Payment-Proof`). After the gateway verifies, forward the proof on the backend's expected header:
```python
headers = {
    "X-402-Token": proof or "",
    "X-Payment-Proof": proof or "",  # backend's gate
}
```

### Verification paths

| Mode | When | Mechanism |
|------|------|-----------|
| **CDP facilitator** (`api.cdp.coinbase.com/platform/v2/x402`) | Production, real EIP-3009 | JWT-auth (EdDSA/ES256) POST `/verify` `{x402Version, paymentPayload, paymentRequirements}` then POST `/settle` — needs real CDP key + key ID + key secret. Full contract in `references/cdp-bazaar-self-settlement.md` |
| **Local HMAC simulation** | Dev/test with our SDK | HMAC(amount:recipient:nonce:validAfter:validBefore, GATEWAY_SECRET) |

Gate with `PAYMENT_VERIFY_MODE=simulation` until real CDP creds exist — auto mode with a key-but-no-secret rejects HMAC proofs and kills the dev loop. **In auto mode, do NOT fall back to simulation after the facilitator says invalid** — that would accept forged proofs.

### EIP-712 domain parameters — mandatory on every accepts[] entry

`extra: {name, version}` (the token's EIP-712 domain name/version) must be on EVERY EVM `accepts[]` entry, or:
- x402-list signability chip = **"route not signable"** (a standard client cannot build the signature)
- Compliance grade capped at C (failing: "EIP-712 domain parameters present on every EVM entry")

USDC on Base = `{"name": "USD Coin", "version": "2"}`. The values must match the actual token domain — hardcoding the wrong name breaks signature verification.

**Confirmed Aug 2, 2026:** adding `extra` to every `accepts[]` entry flipped the GenTech gateway's x402-list compliance from **C 13/14 → A 14/14 the same day** the monitor re-ran (compliance sub-score 93% → 100%, chips "updated 4h ago" on the fix date). The "EIP-712 domain parameters present on every EVM entry" check flipped to ok, "payTo address recoverable" and "payTo at accepts[0].payTo (conformant shape)" passed, and the signability chip cleared. The x402-list monitor re-probes every ~16 min, so a gateway fix shows up in the chips within the hour — verify the grade flip as proof of the fix, don't just re-read your own curl output.

## The landing website drifts from the manifest — sync it to ground truth

The bazaar manifest (`/.well-known/x402-bazaar`) is the **single source of truth** for the
x402 surface: marketplaces (x402-list, Agentic.Market, Bazaar) crawl it and auto-propagate
changes. But the **marketing/landing website** (`gentechlabs.net`) is a **manually-maintained
mirror** — and it goes stale with fictional product names that never match the manifest.

**Confirmed Aug 5, 2026:** `gentechlabs.net` listed 6 invented "products" (Agent Registration,
DeFi Intelligence, Agent Search, Fleet Monitor, Agent Starter Kit, x402 Gateway) that did NOT
match the 8 real live gateway services (token_security, market_intelligence, agent_discovery,
defi_lp_analytics, wallet_analysis, nft_search, treasury_defender, lineage_guard). The site
also claimed a wrong backend list ("gas estimation, rug checks, search, deals, arbitrage").

**Ground truth to sync against — never trust the stale page:** the gateway's `/status` endpoint
reports the REAL live services + backend health (`{"gateway":"x402-v2","status":"operational",
"services":[...],"backends":{...ok}}`). Use it, not memory or the old HTML.

**The registry sweep (Jordan's standing ask when anything changes):**
1. Hit `api.gentechlabs.net/status` → the live service list (ground truth)
2. Probe each service path → expect HTTP **402** (correct paywall) — confirms live + gated;
   500/404 means broken
3. Diff that against the website's API section; replace stale/fictional names with the real ones
4. Update `marketplace-listings-registry.md` (the vault row-per-platform checklist) so every row
   reflects current reality — flag rows needing a human login (Swarms, Atelier) vs auto-sync
5. The manifest bump auto-propagates to crawlers — the website does NOT auto-sync, it needs the
   manual edit above

**When syncing the website:** replace the whole API card grid with the real services (one card
each, real data source + price tag), add a "+N standalone APIs" line, and point the "browse all
APIs" button at `api.gentechlabs.net/docs` (the live spec), not the homepage. Verify with a fresh
`curl https://gentechlabs.net` grep for the new service names.

**Agent-facing discovery docs are a SECOND drift surface (Aug 30, 2026 sweep).** Beyond the marketing site, these surfaces each carried their own stale story and must be synced together whenever the product positioning changes: `/.well-known/x402` + `x402.json` (twin files — see nginx pitfall under Canonical discovery path), `/.well-known/x402-bazaar`, `/.well-known/agent-card.json` (skill ORDER matters — list treasury/flagship skills first, commodity security last), `/llms.txt`, `/llms-full.txt`, `/skill.md`. GenTech's repositioning to "Agentic Treasury first": the bazaar manifest was already correct but x402.json led with "Token security", agent-card led with "rugcheck" and dated to June, and llms.txt/skill.md listed security first. Buyers' first impression of WHAT WE ARE comes from whichever doc they hit — metadata positioning matters as much as the code (registry lesson Aug 24). Sync procedure: rewrite all surfaces with the same positioning + service order, sync the file twins, then verify each URL live.

## Cross-marketplace listing verification

After fixing a gateway (or periodically), verify the fix is reflected across every x402 directory, not just your own curl output. Workflow: probe the gateway directly first, then check each marketplace/directory. Report PASS / FAIL / NOT-LISTED / CANNOT-VERIFY per marketplace with one action item each.

**Step 1 — Direct gateway probes (always first):**
```bash
curl -s -o /dev/null -w '%{http_code}' https://api.yoursite.com/.well-known/x402        # expect 200
curl -s -o /dev/null -w '%{http_code}' https://api.yoursite.com/.well-known/x402-bazaar # expect 200 (bazaar manifest)
curl -s -D /tmp/h -o /tmp/b https://api.yoursite.com/v1/security/score/0x...            # expect 402 + payment-required header
# Envelope checks: x402Version 2, accepts[0].extra {name, version} on EVERY EVM entry
# Receive-side: bad proof on Authorization: x402 / X-Payment -> clean 402 (payment_proof_invalid), NOT 500
```
If a malformed proof returns `{"error":"payment_proof_invalid"}` instead of 500, the gateway is correctly parsing standard payment headers (receive side works).

**Step 2 — Per-directory checks:** the directory landscape, exact check commands, expected states, and the Aug 2 2026 verification transcript are in `references/marketplace-listing-verification.md`.

Key rules:
- **Settlement-gated directories** (x402scan.com, Agentic.Market): services appear only after real on-chain usage. NOT-LISTED there with zero settlements is *expected*, not a failure — the action item is "get the first settled payment" (or manual submission where offered).
- **SPA sites** (Next.js — x402scan, 8004scan, agentic.market): curl returns an HTML shell. Use the browser + the site's search box; verify "No matching results." / fallback-list behavior explicitly.
- **GitHub-backed directories** (gold-402, awesome-x402): grep the raw file — `curl -s https://raw.githubusercontent.com/OWNER/REPO/main/... | grep -i gentech`. Stale URLs in README entries are common (old Cloudflare Worker domains after a domain migration) — that's an action item (fix the entry), not a listing removal.
- **Directories with free search APIs** (agent-tools.cloud `/api/v1/search`): curl with `Accept: application/json`; check `health`, `x402_ok`, `http_status`, `well_known_url` fields.
- **8004scan.io** mirrors on-chain ERC-8004 registration, NOT gateway compliance — its X402 flag comes from registration metadata. A stale listing there means refresh the registration (agent_set_uri), not the gateway.
- Version skew is NOT just cosmetic — fix it properly: `/.well-known/x402`, `/.well-known/x402.json`, `/.well-known/x402-bazaar`, AND the wire envelope must all report the same version. **Root cause found Aug 2, 2026:** the gateway's envelope builder had a HARDCODED `"version": "7.0.0"` string, so even after the manifest files were bumped to 9.0.0, the 402 wire envelope still claimed 7.0.0. Permanent fix: read the version from the single source of truth (the bazaar manifest) — `"version": MANIFEST.get("version", "9.0.0")` — and regenerate the static discovery files FROM the manifest, not by hand. One manifest, every surface derives from it; future bumps can't skew. Verify with one sweep across all four surfaces (three discovery files + wire envelope from a real 402).

### Canonical discovery path — serve `/.well-known/x402` exactly

Checkers and marketplaces probe `/.well-known/x402`, `/.well-known/x402.json`, AND `/.well-known/x402-bazaar` independently. If nginx serves `/.well-known/` statically, a file named `x402.json` does NOT satisfy the `x402` probe. Copy/alias the file at BOTH names. A missing canonical path shows as a separate failure from the header issue.

**Pitfall — nginx static shadow makes doc edits invisible, and the `.json`/extensionless twins drift (confirmed Aug 30, 2026):** when nginx has `location /.well-known/ { root /var/www/gentechlabs; }` on the api server block, the GATEWAY is bypassed for all discovery paths — it serves whatever static file is on disk. Two failure modes:
1. **Editing one twin doesn't update the other.** Rewriting `x402.json` leaves the extensionless `x402` file stale (Live `/.well-known/x402` served old v9.3.2/7-services while disk `x402.json` was new v9.4.1/10-services). They are SEPARATE files; sync after every edit: `cp x402.json x402 && chown www-data:www-data x402 x402.json`.
2. **Editing server.py's embedded discovery content does nothing** for these paths — the static file wins regardless of what the live gateway would serve.

**Diagnostic:** check the HTTP `Last-Modified` header vs the disk file's mtime, and compare `Content-Length` to the file size. A stale date/size on a live endpoint with a fresh disk file = static shadow. Check which nginx location matches: `grep -n 'well-known' /etc/nginx/sites-enabled/<site>`. Fix: always update the static files (both names) as the source of truth for discovery docs, or reconfigure nginx to proxy `/.well-known/` to the gateway for a single source of truth. Also note `llms.txt`, `llms-full.txt`, and `skill.md` are served the same static way from `/var/www/gentechlabs/`.

### Receive-side verification checklist (add to the main checklist)

- [ ] Send `Authorization: x402 <valid-proof>` → HTTP 200 with REAL data (not a stub)
- [ ] Send `X-Payment: <valid-proof>` → HTTP 200 (older convention)
- [ ] No proof → 402; malformed proof → 402; wrong-amount proof → 402
- [ ] Every `accepts[]` entry carries `extra: {name, version}`
- [ ] `/.well-known/x402`, `/.well-known/x402.json`, `/.well-known/x402-bazaar` all return 200
- [ ] Manifest lists ONLY services with live, correctly-routed backends
- [ ] Test with a real agent SDK, not just curl — the header the SDK sends must match what the gateway reads

## The x402 v2 Payment-Required header

The scanner checks the `Payment-Required` response header (not just the 402 status code).

> **Must be base64-encoded JSON in the header.** Returning 402 with only a JSON body is the most common compliance failure. The `PAYMENT-REQUIRED` header (all caps, underscored) must carry the base64-encoded payment payload. CORS headers also required. See `references/bazaar-manifest-nginx-deployment.md` for the FastAPI implementation pattern.

### AgentCash Router — recommended Node.js approach

The `@agentcash/router` package ships a compliant x402/MPP API in minutes. Auto-generates discovery, handles protocol negotiation, and supports fixed, metered, and streaming pricing. Built by Merit Systems.

```bash
npm install @agentcash/router zod
```

```typescript
import { Router } from "@agentcash/router";
import { createServer } from "http";
import { z } from "zod";
const router = new Router();

// Fixed price — most common
router.route("search").paid("0.01")
  .body(z.object({ q: z.string() }))
  .handler(async ({ body }) => search(body.q));

// Metered — handler calls charge() as it works
router.route("research").upTo("0.05")
  .handler(async ({ charge }) => { await charge("0.001"); return deepWork(); });

// Wallet identity — no signup flow
router.route("profile").siwx()
  .handler(async ({ wallet }) => profileFor(wallet));

createServer(router.fetch).listen(3000);
```

Auto-handles: `GET /.well-known/x402`, `GET /openapi.json` with pricing extensions, protocol negotiation (x402 or MPP), and x402scan indexing.

**When NOT to use:** Python/Rust/Go runtimes, Cloudflare Workers, or when full control over the 402 response shape is needed. For those, use the native `@x402/*` SDK or hand-roll.

### Required format

```json
{
  "x402Version": 2,
  "error": "Payment required",
  "resource": {
    "url": "https://api.example.com/endpoint",
    "description": "Description of what this endpoint does and costs",
    "mimeType": "application/json",
    "serviceName": "Your Service Name",
    "tags": ["x402", "api"]
  },
  "accepts": [{
    "scheme": "exact",
    "network": "eip155:8453",
    "amount": "5000",
    "asset": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
    "payTo": "0xYourPaymentAddress",
    "maxTimeoutSeconds": 60
  }],
  "extensions": {
    "bazaar": {
      "bazaarResourceServerExtension": true,
      "discoveryUrl": "https://api.example.com/.well-known/x402-bazaar",
      "info": {
        "title": "Service Name",
        "description": "Short description of the API",
        "version": "1.0.0",
        "x402Version": 2,
        "seller": {
          "name": "Your Company",
          "website": "https://example.com"
        },
        "input": {
          "example": {
            "address": "0x1234567890abcdef1234567890abcdef12345678"
          }
        },
        "output": {
          "description": "What the endpoint returns",
          "example": {
            "success": true,
            "data": {}
          }
        }
      },
      "schema": {
        "type": "object",
        "properties": {
          "result": {"type": "object"},
          "error": {"type": "string"}
        }
      }
    }
  }
}
```

The `extensions.bazaar.info` block with `input`, `output`, and `seller` is required for Agentic Market / Coinbase Bazaar discovery. The `info.output` field in particular — without it the validator shows "Missing info.output — required for discovery".

### Key differences from v1 (common mistakes)

| Field | Correct (v2) | Wrong (v1) |
|-------|-------------|------------|
| Top-level version | `x402Version: 2` | `version: "x402-v2"` |
| Payment scheme | `scheme: "exact"` | `type: "x402"` |
| Recipient field | `payTo` | `payment_address` |
| Asset casing | **lowercase** hex | mixed/uppercase |
| Amount type | string (wei) | number |
| Headers needed | `Payment-Required` (base64 JSON) | just body |

## Bazaar manifest (`/.well-known/x402-bazaar`)

> **Separate from `/.well-known/x402`.** The bazaar manifest is consumed by Agentic Market and Coinbase Bazaar for auto-discovery. See `references/bazaar-manifest-nginx-deployment.md` for file format, nginx config pattern, Cloudflare WAF bypass, and pre-deployment verification.

## `/.well-known/x402` discovery endpoint

Must return a JSON document with:

```json
{
  "version": 1,
  "resources": ["https://api.example.com/endpoint1", "..."],
  "resourceDetails": [{"url": "...", "name": "...", "description": "...", "price": 0.005}],
  "freeTier": {
    "health": "https://api.example.com/health",
    "pricing": "https://api.example.com/pricing",
    "openapi": "https://api.example.com/openapi.json"
  },
  "baseGateway": {
    "enabled": true,
    "network": "eip155:8453",
    "networkLabel": "Base Mainnet",
    "asset": "0x...",
    "assetLabel": "USDC",
    "payTo": "0x...",
    "gatewayUrl": "https://api.example.com",
    "discoveryUrl": "https://api.example.com/.well-known/x402",
    "openapiUrl": "https://api.example.com/openapi.json",
    "facilitators": ["x402.org"]
  }
}
```

## OpenAPI schema requirements

For x402scan probe generation, parameters must:
- Be non-required (`required: false`) for query params
- Include a `default` value so the scanner knows what to send
- Path params (`{id}`, `{mint}`) can be required: true
- Header params (X-Payment-Proof) should be required: true

## Cloudflare Worker deployment

```bash
# Install token
echo 'cfut_YOUR_TOKEN' > ~/.cloudflare-token

# Deploy
CLOUDFLARE_API_TOKEN=$(cat ~/.cloudflare-token) wrangler deploy src/worker.ts --name your-worker-name
```

### Pitfall — Cloudflare Worker route intercepts root traffic (blocks VPS)

A Cloudflare Worker deployed with a route matching `domain.com/*` or `domain.com` will intercept ALL traffic before it reaches your origin server (VPS, nginx, etc.). The Worker serves its own response instead of passing through to the origin, making it look like your VPS changes aren't being served — even though `curl localhost` on the VPS shows the correct content.

**Symptoms:**
- `curl -H "Host: domain.com" http://localhost/` returns the correct VPS content
- `curl https://domain.com/` returns a completely different page (the Worker's response)
- Cloudflare cache purge doesn't fix it
- The Worker's build may be failing (merge conflicts in worker.ts, GitHub auth issues) but the old deployed version still intercepts traffic

**Fix — Remove the root route from the Worker:**

1. Go to Cloudflare Dashboard → Workers & Pages → your-worker
2. Click the **Triggers** tab (or **Domains** tab depending on UI version)
3. Find the route matching `domain.com/*` or `domain.com`
4. Delete that route (keep only API-specific routes like `api.domain.com/*`, `domain.com/api/*`)
5. Traffic to the root domain now passes through to your origin server normally

**Fix — Update Worker to pass through root traffic (alternative):**
If you want to keep the Worker but have it proxy through to the VPS for paths it doesn't handle, add a pass-through in the Worker:

```javascript
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    // Let root traffic pass through to VPS
    if (url.pathname === '/' || url.pathname.startsWith('/portfolio') || url.pathname.startsWith('/investor-deck')) {
      return fetch(`http://${VPS_IP}${url.pathname}${url.search}`, {
        method: request.method,
        headers: request.headers,
        body: request.body,
      });
    }
    // Handle API routes in the Worker
    // ... your API logic here
  }
}
```

**Real example (Jul 22, 2026):** GenTech's `gentechlabs-api` Worker had a route matching `gentechlabs.net/*` that served an old landing page instead of the VPS hub.html. The Worker file had merge conflicts (`<<<<<<<` markers) and the build was failing, but the previously-deployed version kept intercepting traffic. The fix required removing the root route from the Worker's Triggers tab in Cloudflare Dashboard.

### Pitfall — Cloudflare Workers 1042 error (account-level)

Some Cloudflare accounts (particularly personal/free-tier accounts without Workers Paid subscription) return **error code 1042** on ALL deployed workers regardless of code complexity. Even a "hello world" worker fails. This is an account-level restriction, not a code bug.

**Symptoms:**
- `curl` returns `error code: 1042` with HTTP 404
- Deployment succeeds but runtime fails
- Every worker on the account has the same error
- `wrangler whoami` shows account is authenticated and functional
- Account may have hit Workers Paid plan limits or be on restricted free tier

**Workaround — VPS systemd deployment:**

Instead of Cloudflare Workers, deploy the x402 test harness as a systemd-managed Node.js service on your VPS behind nginx:

```bash
# 1. Create systemd service
cat > /etc/systemd/system/x402-test.service << 'EOF'
[Unit]
Description=x402 Test Harness
After=network.target
[Service]
Type=simple
ExecStart=/usr/bin/node /opt/x402-test.js
Restart=always
RestartSec=5
User=root
[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload && systemctl enable x402-test && systemctl start x402-test

# 2. Add nginx reverse proxy to main site:
# location /x402-test/ {
#     proxy_pass http://127.0.0.1:3099/;
#     proxy_set_header Host $host;
# }
```

## Ecosystem-wide compliance auditing

Use this pattern to scan third-party x402 implementations across the ecosystem and identify compliance gaps. Works for pre-integration due diligence, competitive analysis, and PR contribution targeting.

### Audit methodology

For each target, check four layers in order:

**Layer 1 — Discovery endpoint** (`/.well-known/x402`)
```bash
curl -s https://target.example.com/.well-known/x402
```
Check: `version`, `resources[]`, `resourceDetails[]`, `baseGateway` block (enabled, network CAIP-2, asset, payTo, gatewayUrl). If `version` is missing, the endpoint is incomplete. If only `ownershipProofs` is present, it's a stub.

**Layer 2 — 402 status code**
```bash
curl -s -o /dev/null -w '%{http_code}' https://target.example.com/protected-endpoint
```
Must return 402. If it returns 401 or 200, the endpoint isn't x402-gated.

**Layer 3 — Payment-Required header**
```bash
curl -s -D - -o /dev/null https://target.example.com/protected-endpoint | grep -i payment
```
Check header name: should be `payment-required` (lowercase, v2). If `x-payment-required` or `x-payment` also appear, those are deprecated v1 headers — should be removed.

Then decode the payload:
```bash
curl -s -D /tmp/h -o /tmp/b https://target.example.com/protected-endpoint
HEADER=$(grep -ia '^payment-required:' /tmp/h | sed 's/.*: //')
echo "$HEADER" | base64 -d | python3 -m json.tool
```
Check for:
- `x402Version: 2` (not `version: "x402-v2"`)
- `accepts[]` array with each entry having `scheme`, `network` (CAIP-2), `amount`, `asset` (lowercase hex), `payTo`, `maxTimeoutSeconds`
- `resource` block with `url`, `description`, `mimeType`, `serviceName`, `tags`
- `extensions` (bazaar is the standard discovery extension)

**Layer 4 — Body format**  
```bash
cat /tmp/b | python3 -m json.tool
```  
**v2 note:** The `Payment-Required` HEADER is the canonical carrier of structured payment JSON. The response body is free-form and may be empty, a simple error message, or nonstandard — this is NOT a compliance failure.  

Common body patterns seen in production:
- **Minimal body** — `{"error":"Payment Required","message":"..."}` (BlockRun, twit.sh)
- **Custom wrapper** — `paymentInfo` key with nested fields (BlockRun legacy, JarvisClaw)
- **Empty body** — `{}` (x402-rs crate design choice)

Do NOT require body fields for v2 compliance. Only the header carries the structured payment data.  
(For v1 the body was the primary carrier — but v1 is deprecated.)

### Source code inspection

For open-source gateway implementations, verify the middleware layer:
- **x402-rs (Rust / Axum)**: `x402-axum::paygate` generates V2-compliant `Payment-Required` headers automatically. The Marlin gateway uses this — its middleware is correct but it's missing a `/.well-known/x402` route.
- **x402-foundation/x402 (TypeScript)**: Canonical SDK. Server middleware (`@x402/express`, `@x402/hono`, etc.) generates compliant V2 responses.
- **x402-foundation/x402 (Python)**: `x402.http.middleware.fastapi.PaymentMiddlewareASGI` — generates V2 if configured with `x402ResourceServer`.
- **mark3labs/x402-go (Go)**: Dual-package layout (`v1` root, `v2/` subdirectory). V2 package passes all 14 test suites. Architecture:
  - Types v2: `PaymentRequired` with `x402Version: 2`, `PaymentRequirements` with `scheme`, `network` (CAIP-2), `amount`, `asset`, `payTo`, `maxTimeoutSeconds`, `extra` — all spec-compliant
  - Encoding: base64(std) + JSON — correct for `X-PAYMENT` / `X-PAYMENT-RESPONSE` headers
  - Middleware: `X-PAYMENT` header check, facilitator verify/settle, settlement interceptor, dual-fallback facilitators, lifecycle hooks. Gin wrapper also available
  - Client: 402 auto-roundtrip via `X402Transport` (`http.RoundTripper`), multi-signer selection, payment callbacks
  - CAIP-2 validation: `eip155:8453` (numeric chain IDs), `solana:5eykt4...` (genesis hash length check)
  - Signers: Full EIP-3009 (EVM) and SVM (Solana) implementations
  - MCP integration: MCP server wrapper with per-tool payment gating
  - **Gap: no `/.well-known/x402`** — same as x402-rs. Middleware handles 402 correctly but no discovery route.
  - **Gap: checksummed asset defaults** — chain configs ship mixed-case addresses (e.g. 0x833589fCD6eDb6...). PR #30 submitted to lowercase.
- **quiknode-labs/x402-rails**: Ruby on Rails middleware (v1.2.0). Verified v2 compliant: PAYMENT-REQUIRED header, CAIP-2 networks, Bazaar discovery. No action needed.
- **quiknode-labs/x402-payments**: Ruby client SDK. Verified v2 compliant: PAYMENT-SIGNATURE header, CAIP-2 accepted.network. No action needed.
- **srotzin/hive-rosetta**: Node.js + Python EIP-3009 signer library (hive-rosetta). Verified v2 compliant: `PAYMENT-REQUIRED` header, `x402Version: 2`, `scheme: "exact"`, `payTo`, lowercase-ready (asset casing fix PR #2 submitted). Cross-language parity (Python `hive_rosetta` mirrors Node `rosetta-node`).

### Monorepo/third-party source audit (code-audit protocol)

When auditing a third-party open-source x402 implementation from source (not just curl endpoints), use this methodology:

**Phase 1 — Map the architecture**
```bash
# Identify the packages and their roles
find . -name 'package.json' -maxdepth 3 | while read f; do echo "--- $f"; jq '.name, .dependencies | select(.!=null) | keys | map(select(contains("x402")))' "$f"; done
```
Look for three expected roles: **gateway** (issues 402s, verifies tokens), **facilitator** (verifies/settles payments), **client** (creates payment payloads). Determine whether they're one monolith or separate services.

**Phase 2 — Find the 402 response construction**
```bash
# Search for where Payment-Required is built
grep -rn 'Payment-Required\|X-Payment-Required\|buildPaymentRequired\|createPaymentRequired' --include='*.ts' --include='*.js' --include='*.rs' --include='*.py' .
```
Check whether the header name is `Payment-Required` (v2 spec) or `X-Payment-Required` (deprecated). Check whether the implementation uses `@x402/core`'s `x402ResourceServer` or rolls its own.

**Phase 3 — Cross-reference canonical types from node_modules**
```bash
# Compare the local types against @x402/core v2 spec
cat node_modules/@x402/core/dist/cjs/mechanisms-Djgn2ixv.d.ts | grep -A 10 'type PaymentRequired =' 
cat node_modules/@x402/core/dist/cjs/mechanisms-Djgn2ixv.d.ts | grep -A 10 'type PaymentPayload ='
cat node_modules/@x402/core/dist/cjs/schemas/index.d.ts | grep -A 20 'PaymentRequiredV2Schema\|PaymentPayloadV2Schema'
```
Key v2 shape checks against local code:
- `PaymentRequired` must have `x402Version`, `resource: ResourceInfo`, `accepts: PaymentRequirements[]`, optional `extensions`
- `PaymentRequirements` must use `amount` (not `maxAmountRequired` — that's v1)
- `PaymentPayload` must have `accepted: PaymentRequirements` (envelope), not flat `scheme`/`network` (that's v1)
- `network` must be CAIP-2 format (`${string}:${string}`)

**Phase 4 — Check for facilitator-gateway config drift**
```bash
# Compare config defaults across services
grep -rn 'PRICE_AMOUNT\|PRICE_NETWORK\|PRICE_ASSET\|PRICE_PAY_TO\|network\|payTo\|amount' --include='*.ts' --include='*.rs' --include='*.py' --include='*.json' .
```
Key questions:
- Do gateway and facilitator share the same default network? (Common trap: gateway defaults to mainnet, facilitator defaults to devnet)
- Do they share the same asset mint address? (Trap: different tokens)
- Is the default `payTo` a real address, not a system contract? (Trap: Solana system program `11111111111111111111111111111111`)
- Does the facilitator reconstruct requirements from its own env instead of using the client's `accepted` payload?

**Phase 5 — Check client payload version alignment**
```typescript
// Look for this pattern in client code:
// Using a V1 scheme class but passing x402Version: 2
const scheme = new ExactSvmSchemeV1(signer);               // V1 scheme
const result = await scheme.createPaymentPayload(2, reqs);  // but version=2
```
V1 scheme classes produce flat payloads `{ x402Version, scheme, network, payload }` — missing the `accepted: PaymentRequirements` envelope that v2 requires. This is a structural mismatch that causes v2 facilitator verification to reject the payload.

**Phase 6 — Check for type re-exports and drift risk**
```typescript
// Anti-pattern: locally redefining PaymentRequired instead of importing
interface PaymentRequired {
  x402Version: number;  // matches v2 now, but drifts silently
  resource: { url, description?, mimeType? };
  accepts: PaymentRequirements[];
  extensions?: Record<string, unknown>;
}
// vs importing from @x402/core
import type { PaymentRequired } from "@x402/core/types";
```

**Phase 7 — Cross-service version audit (mixed v1/v2 monorepo detection)**
```bash
# Search for version indicators separately in server vs client directories
grep -rn 'x402Version' --include='*.ts' --include='*.js' --include='*.rs' --include='*.py' server/ client/ apps/ packages/ 2>/dev/null
# Check for maxAmountRequired (v1 field name) vs amount (v2)
grep -rn 'maxAmountRequired\|"amount":' --include='*.ts' --include='*.js' . 2>/dev/null | grep -v node_modules
# Check payload shape — flat {x402Version, scheme, payload} vs envelope {accepted: {...}}
grep -rn 'accepted:' --include='*.ts' --include='*.js' . 2>/dev/null
```
It's possible for a monorepo to have:
- **Server middleware** that correctly generates v2 402 responses (reads `payment-signature`, returns CAIP-2, etc.)
- **Auto-payment / client code** that still constructs v1 payloads (`x402Version: 1`, `maxAmountRequired`, flat `{x402Version, scheme, network, payload}` shape) for the facilitator

This happens when the server was upgraded to v2 but the client-side settlement code was missed. Detection requires checking each service's version independently — don't assume all parts of a monorepo are at the same x402 version.
**Common tell**: the server imports from `@x402/core` (v2 SDK) while `auto-payment.ts` constructs `{ x402Version: 1, scheme: 'exact', ... }` manually.

### Real-world compliance gaps found (July 2026 scan)

See `references/ecosystem-scanning-methodology.md` for the full methodology, and `references/july-15-2026-scan-results.md` / `references/july-16-2026-scan-results.md` / `references/july-17-2026-scan-results.md` for the most recent scan results. Key patterns:

| Gap | Prevalence | Fix effort |
|-----|-----------|------------|
| No `/.well-known/x402` endpoint | ~60% of implementations | LOW (add route) |
| **Discovery at `GET /` instead of `/.well-known/x402`** | **~10%** | **LOW (add canonical route — `/` is human-friendly root, not a substitute for discovery; x402-license-gateway is a live example)** |
| Deprecated v1 headers (`X-PAYMENT`) alongside v2 | ~40% | LOW (remove header) |
| Body format nonstandard or empty | ~50% | LOW (align JSON shape) |
| `baseGateway` block missing | ~40% | MEDIUM |
| No `resourceDetails` (per-endpoint pricing) | ~50% | MEDIUM |
| Asset addresses not lowercase hex | ~30% (found in x402-go, x402-dotnet, hive-rosetta, x402-rs configs) | LOW (one-liner per address) |
| Not x402-gated at all (401 instead of 402) | ~10% | HIGH |
| Mixed v1/v2 monorepo (server v2, client/auto-pay v1) | ~15% of monorepos | MEDIUM (multi-file, needs per-service audit) |

## CDP Bazaar (Coinbase) — settlement-gated listing with its own auth + envelope traps

The CDP x402 Bazaar (`api.cdp.coinbase.com/platform/v2/x402`) is the OTHER settlement-gated
marketplace alongside OpenDexter. Indexing triggers on **settlement**, not verify. It has
four non-obvious gotchas a gateway integration must handle (all confirmed live Aug 4 2026):
CDP requires a **JWT** (EdDSA for Ed25519 keys / ES256 for EC PEM), not HMAC → 401 otherwise;
the gateway must call **`/settle` after `/verify`** (verify alone never indexes);
the `/verify` envelope needs `paymentRequirements` = the accepted option object **directly**
(not wrapped in `accepts[]`); and the SDK sends the proof in a **`PAYMENT-SIGNATURE`** header
(base64 JSON), which most gateways don't read. Full recipe, working Python JWT builder, exact
envelope schema, rejected shapes, Node SDK import map, and the end-to-end debug order — in
**`references/cdp-bazaar-self-settlement.md`**.

**Fast triage:** CDP returns 401 → auth/JWT problem. Returns 400 with a schema message →
auth is fine, payload shape is wrong. Never guess the envelope — monkeypatch `globalThis.fetch`
in Node and print the SDK's actual `/verify` body, then replicate it.

**Pitfall — the running gateway holds STALE CDP credentials (a 401 that survives a code fix).**
The gateway's systemd unit loads env from a file (`EnvironmentFile=/root/.hermes/profiles/gentech/.env`),
but if the service was started BEFORE the CDP key was rotated, the **running process keeps the old
key ID + secret in its own `/proc/<pid>/environ`** — different from what the `.env` file now holds.
The CDP facilitator rejects the stale JWT → `401 Unauthorized` on every `/verify`, and the self-settle
fails with `payment_proof_invalid / facilitator returned 401`. Editing gateway code does nothing; the
fix is to **restart the service** so it re-reads the current `.env`:
```bash
# Compare the running process's creds against the .env file
cat /proc/<pid>/environ | tr '\0' '\n' | grep -E "^CDP_API_KEY_ID=|^CDP_API_KEY_SECRET="
grep -E "^CDP_API_KEY_ID=|^CDP_API_KEY_SECRET=" /root/.hermes/profiles/gentech/.env
# If they differ, the process is stale — restart to load current creds
systemctl restart x402-api
# Verify the new pid picked up the correct keys, then re-run the self-settle
```
**Confirmed Aug 5, 2026:** the GenTech gateway ran with key `dcc952…`/secret `CjVkAQ…` while the
`.env` held `f341f8…`/`p97RW1…`. After `systemctl restart x402-api`, the first real x402 settlement
went through (0.005 USDC, arb wallet `0x3d117…`, endpoint `/v1/market/price/ETH`, 402→200 with real
data). **Diagnostic order:** if a self-settle returns 401, check the running process's env against the
`.env` file BEFORE touching gateway code — a stale-credential restart is a 30-second fix, a code
"fix" for a non-existent bug wastes a session. (This is the same class of stale-mirror trap as
`source-of-truth-verification` — the live process env is ground truth, the `.env` file is intent.)

## OpenDexter (open.dexter.cash/mcp) — settlement-gated x402 marketplace

OpenDexter is the x402 search engine / marketplace MCP. **It auto-catalogs APIs from real settlements — no registration form, no approval, zero config.** Verified live Aug 3, 2026.

### How listing actually works (the critical fact)

- **Dexter auto-discovers any API that receives a successful x402 payment through ITS facilitator.** On settlement, it extracts the resource URL + method from the payment payload, the seller wallet from `payTo`, and API metadata. The resource appears as "discovered"; you can then claim it to add branding/description/verification.
- **No registration form exists.** Getting listed = settle one real x402 payment through Dexter's facilitator → auto-catalog → claim the resource.
- **Testnet USDC does NOT trigger it.** Auto-discovery runs on real settled payments through Dexter's mainnet facilitator. Testnet settlements are invisible — they never reach the catalog. It must be real mainnet USDC (~$1 is enough).

### Verify Dexter sees your endpoints (read-only, free)

Initialize an MCP session and call `x402_check` against your endpoint:

```python
# init → notifications/initialized → tools/call x402_check
# url=https://api.yoursite.com/v1/security/score/0x0, method=GET
# Expect: requiresPayment=True, authMode=paid, statusCode=402 → Dexter recognizes it as x402-paid
# Health endpoint: free=True, statusCode=200 → reachability confirmed
```

The server returns `{free, authMode, statusCode, requiresPayment, intentId, quoteOnly}`. If `requiresPayment=True, authMode=paid` on your paid endpoint, Dexter already recognizes it — the only remaining step is a real settlement.

### OpenDexter tool surface (5 tools)

| Tool | Auth | Purpose |
|---|---|---|
| `x402_search` | noauth | Natural-language marketplace search; read-only, free, never pays |
| `x402_check` | noauth/oauth2 | Inspect exact endpoint + pricing before paying; quote-only anonymous |
| `x402_access` | noauth | Wallet-gated API access (SIWS proof, not payment) |
| `x402_wallet` | oauth2 | View Dexter payment wallet (passkey, no private key) |
| `dexter_portfolio` | oauth2 | Governed asset portfolio for authenticated session |

**MCP session flow:** `initialize` → `notifications/initialized` → `tools/list` / `tools/call`. SSE framing: strip `event: message\n` and `data: ` prefixes before parsing JSON. Search responses prepend a `SECURITY:` untrusted-data notice line before the JSON — find the first `{` and parse from there.

### The funding blocker (honest)

Both OpenDexter AND Syra are **wallet-gated and settlement-driven**. There is no application form. The blocker is a **funded mainnet wallet + a real settlement**, not API readiness. Check first whether a real funded wallet exists (Q402 trial is gasless relay, not a funded mainnet wallet; treasury_manager.py sample wallets are fake). If none exists, the task is "get a funded wallet," not "submit to the marketplace."

### The self-settlement recipe (how listing actually gets triggered)

To turn "Dexter recognizes us" into "Dexter catalogs us," settle ONE real x402 payment against our own endpoint through Dexter's facilitator. Full recipe — the `@dexterai/x402` Node `payAndFetch` flow, the on-chain balance verification (publicnode Base RPC + User-Agent workaround), the funding-gap pattern (funded-wallet-no-key vs signable-wallet-no-USDC), the `self-settle.mjs` scaffold, AND the receive-side blocker (gateway verify mode must match the facilitator, or the real payment gets rejected and never settles) — lives in **`references/opendexter-self-settlement.md`**.

**SDK version trap + v5 API surface (proven Aug 30, 2026):** the gateway dir's `package.json` declared `@dexterai/x402: ^5.4.2` but Node silently resolved a **stale v3.9.0 from a parent `/root/node_modules`** (no local install existed). v3 can't parse x402-v2 multi-rail challenges. Check before debugging: `cd <project> && node -e "console.log(require('@dexterai/x402/package.json').version)"` — if it doesn't match package.json, run `npm install '@dexterai/x402@^5.4.2'` locally. In v5, `createX402Client` and `wrapFetch` are **not exported** (d.ts lies) — the working verbose debug pattern is `createBudgetAccount({budget:{total:"0.05"}, evmPrivateKey, maxAmountAtomic:"20000", verbose:true})` then `agent.fetch(url)`. Working end-to-end script: `dexter-final.mjs` in the gateway repo (buyer = arb wallet, seller = signer payTo). Minimal $0.005–$0.015 settles land on-chain and hit the revenue ledger; whether tiny settles trigger Dexter's catalog listing specifically is pending verification (index-verify watcher armed Aug 30).

**Funding-gap pattern (check before claiming readiness):** self-settlement needs a wallet you can SIGN from that HOLDS USDC. These frequently split across two wallets — one has USDC but no private key in env (Jordan's ERC-8004/revenue owner wallet `0x7ebff...`), the other has the key but no USDC (GTA arb wallet `0x3d117...` in `secure/gentech-arb-wallet.json`). Verify USDC + gas on-chain before assuming you can settle; don't trust a wallet just because config references it. **But funding alone is NOT enough** — even with USDC in the signable wallet, the settlement still fails if the gateway's verify mode doesn't match the facilitator (see the receive-side blocker section in the reference). Fund the wallet AND align verify mode; both are required.

**Algorand rail prerequisite — the ASA opt-in wall:** before an Algorand wallet can receive USDC (ASA 31566704), it must opt in via a 0-unit asset transfer to self, or exchanges (Coinbase) refuse the send. Full recipe + verification in `references/algorand-usdc-optin.md`.

## x402scan registration flow

Registering your API on [x402scan](https://www.x402scan.com/resources/register) is the primary way to get discovered by agents on Poncho and Agent Cash.

For the step-by-step web UI registration walkthrough (including the "Set up x402 with a prompt" flow, scanner output interpretation, and programmatic registration via agentcash MCP), see **`references/x402scan-web-ui-registration.md`**.

### Step-by-step

1. **Navigate** to `https://www.x402scan.com/resources/register`
2. **Enter your gateway URL** — `https://api.yoursite.com`
3. **Auto-discovery** — The scanner reads `/.well-known/x402` and identifies all endpoints
4. **Review results** — It shows:
   - Detected endpoints and their pricing
   - A preview of your merchant description (from discovery metadata)
   - Any errors preventing full validation
5. **Fix validation errors** (see below)
6. **Add** — Click the "Add" button once endpoints show as valid

### Homepage "Add your API" flow (verified Aug 2, 2026)

The site's homepage ALSO has an **"Add your API"** button (`https://www.x402scan.com` — top right / hero) that opens the same registration on the homepage route. Enter `api.yoursite.com` in the `https://` + hostname box (NOT a full URL). It probes immediately and shows:
- Detected resource count on the button — e.g. **"Add API (2 resources)"** — clicking it registers instantly and shows the success dialog **"You're registered!"** with a merchant page link (`https://tryponcho.com/m/<hostname>`) and options to review your API page / test endpoints.
- The **"7 endpoints with errors"** accordion lists free endpoints the probe couldn't 402 — fix per the FastAPI shadowing pitfall above (`openapi_url=None` + `security: []` on free endpoints), then re-visit the page fresh (the scanner caches per URL).

Even when endpoints show probe errors, **Add still works** — the listing is registered; the errors only affect how fully agents can auto-probe. Fix the spec after registering and re-probe.

### "Missing input schema" error

The scanner probes each endpoint to verify it returns a 402 payment challenge. But it needs to know what parameters to send. If your OpenAPI spec doesn't define `requestBody` or `parameters` with default values, the scanner can't construct a probe request — so the endpoint shows as "invalid" with error:

> `Missing input schema — add a requestBody or parameter schema to your OpenAPI spec so agents know what to send`

**Fix:** For each endpoint in your OpenAPI spec:
- Add `parameters` with `required: false` + a `default` value for query params
- Add `requestBody` schemas for POST endpoints
- Path parameters (`{id}`, `{mint}`) can be `required: true` — these work
- Add header params like `X-Payment-Proof` as `required: true`

**Example OpenAPI fix:**
```json
"/v1/games/search": {
  "get": {
    "parameters": [
      {
        "name": "q",
        "in": "query",
        "required": false,
        "schema": { "type": "string", "default": "zelda" },
        "description": "Search query"
      }
    ],
    "responses": {
      "402": { "description": "Payment required — x402 challenge" }
    }
  }
}
```

Without this, the scanner shows "0 valid resources" and the endpoint cannot be registered even though the x402 paywall works perfectly in production.

### "Expected 402, got 400" error

If endpoints return HTTP 400 (validation error) instead of 402 when probed without payment, **request validation is running before the paywall middleware**. The 402 challenge must fire before body/query schema validation rejects the request.

**Fix:** Move the paywall middleware to run before input validation. In Express/Hono:
```typescript
// WRONG: validation before payment
app.get('/endpoint', validateInput, paywall, handler);

// RIGHT: payment before validation
app.get('/endpoint', paywall, validateInput, handler);
```

Alternatively, if the endpoint is not x402-paid, add `"security": []` to its OpenAPI definition to exclude it from probing.

### "Endpoint did not return a 402 payment challenge" with HTTP 500

When x402scan probes your gateway and reports **`"Endpoint did not return a 402 payment challenge"`** with a **500 status code** (not 400), the root cause is distinct from the standard paywall-ordering problem.

**Root cause:** Your OpenAPI spec marks query parameters as `required: true`, and the server framework validates these BEFORE any middleware runs. When x402scan probes without parameters (it doesn't know valid values yet), the framework rejects the request at the routing/validation layer — never reaching the paywall middleware — and returns a 500 (framework-level crash from missing required params) instead of a 402.

This is distinct from the "Expected 402, got 400" pattern where input validation runs inside the handler. Here, the server framework itself crashes before any middleware executes.

**Fix — Option A (recommended for x402scan compatibility):** Make OpenAPI query params non-required with defaults.
```json
// WRONG: x402scan probe causes framework crash
"parameters": [{
  "name": "q", "in": "query",
  "required": true,                    // ← causes 500 on probe
  "schema": { "type": "string" }
}]

// RIGHT: probe can proceed
"parameters": [{
  "name": "q", "in": "query",
  "required": false,                   // ← probe-safe
  "schema": { "type": "string", "default": "zelda" },
  "description": "Search query"
}]
```

The OpenAPI `parameters` block describes what AGENTS should send — `required: true` means "a valid request must include this param". But the gateway has two independent validation layers:
- **Framework-level validation** (Cloudflare Workers Router, Hono param validation, Express route matching) — runs first, rejects missing required params before any middleware
- **Application-level validation** (Zod in handler, schema checks) — runs inside your handler, after the paywall

The 500 happens when framework-level validation rejects the probe before the paywall can respond with a 402.

**Fix — Option B (gateway reorder):** Move the x402 payment challenge to execute BEFORE the framework's param validation:
- **Cloudflare Workers / Hono:** Use a global middleware that intercepts ALL requests and returns 402 for paid paths before the router processes path params
- **Express:** Mount the paywall as `app.use()` middleware (not per-route), so it intercepts before the route handler validates params
- **Python/FastAPI:** Use ASGI middleware that returns 402 for paid paths before the router validates query params

**Fix — Option C (last resort):** If you cannot reorder middleware (e.g., `itty-router` in Cloudflare Workers bakes param extraction into routing), make ALL probe parameters `required: false` in the OpenAPI spec despite your application requiring them. Then validate manually in the handler and return a proper 402 challenge if payment is missing.

**Real example (Jul 17, 2026):** GenTech x402 gateway on Cloudflare Workers. All 16 OpenAPI endpoints had `required: true` query params. x402scan probed without params → Cloudflare Workers framework crashed with 500 before any middleware fired. Fix: changing `required: true` to `required: false` with defaults in the OpenAPI spec while keeping server-side param validation in the handler layer. See build queue item #70.

## Discovery tool — @agentcash/discovery

The official x402scan discovery CLI validates your OpenAPI spec and probes endpoints before registration.

### Install (auto-cached via npx)
```bash
npx -y @agentcash/discovery@latest discover "<origin_url>"
```

### Commands

| Command | What it does |
|---------|-------------|
| `discover <origin>` | Full audit: fetches OpenAPI spec, checks metadata, probes endpoints, reports warnings |
| `check <endpoint>` | Single endpoint probe — validates 402 behavior and metadata |

### Warning codes (from production runs)

| Code | Level | Meaning | Fix |
|------|-------|---------|-----|
| `OPENAPI_CONTACT_MISSING` | info | `info.contact` has no email | Add `info.contact.email` |
| `FAVICON_MISSING` | warn | No favicon at origin | Add `/favicon.ico` (cosmetic, not blocking) |
| `L2_NO_PAID_ROUTES` | info | No endpoints marked as paid | Add `x-payment-info` to each route |
| `L2_AUTH_MODE_MISSING` | warn | Route missing auth mode declaration | Add `security: [{ x402: [] }]` to each route |
| `L3_AUTH_MODE_MISSING` | warn | No auth mode in spec at probe level | Same as L2 — add security scheme + ref |
| `L4_GUIDANCE_MISSING` | info | No `info.x-guidance` text | Add markdown guidance string to `info.x-guidance` |

### What a clean report looks like

```
Routes: 15, all apiKey+paid
Warnings (1):
  [warn] FAVICON_MISSING — No favicon found at this origin.
```

Only `FAVICON_MISSING` is acceptable. All other warnings must be resolved before x402scan will register the origin.

## Canonical fix — ENDPOINT_META-based OpenAPI generation

The production pattern for fixing OpenAPI schemas at the source (vs proxy-patching) is to replace the generic route-loop with a **per-endpoint metadata map** that defines method, summary, description, params, and requestBody schemas — all with real examples.

### Pattern summary

Replace the old generic loop (which assigns `get` to everything with a generic `query` param) with a `Record<string, EndpointMeta>` that maps each route to its proper method and parameters:

```typescript
interface EndpointMeta {
  method: 'get' | 'post';
  summary: string;
  description: string;
  queryParams?: { name: string; type: string; description: string; example?: string | number; required?: boolean }[];
  pathParams?: { name: string; type: string; description: string; example?: string }[];
  requestBody?: {
    required?: boolean;
    properties: { name: string; type: string; description: string; example: any; required?: boolean }[];
  };
}
```

Each route entry specifies:
- **GET endpoints**: `queryParams` with `required: false` + `example` values so the scanner knows what to send
- **POST endpoints**: `requestBody` with `application/json` schema + `example` object with real data
- **Path parameter endpoints**: `pathParams` with `required: true` + real base58/examples

The generator function then iterates over the PRICING map, looks up metadata, and builds the full OpenAPI operation including:
- `parameters` array (path + query params assembled correctly per endpoint type)
- `requestBody.content["application/json"].schema` for POST endpoints (with `properties`, `required`, and `example`)
- Per-endpoint `responses["402"]` with the full `accepts[]`, `instructions`, `proofStructure` schema
- Per-operation `security: [{ x402: [] }]`
- Top-level `components.securitySchemes.x402` (apiKey in header)

### Key rules

1. **Query params must be `required: false`** with a `default` or `example` so x402scan's discovery tool (`@agentcash/discovery`) knows what to send as a probe
2. **POST endpoints need `requestBody.content["application/json"]`** with both `schema.properties` (structured types) AND `example` (a concrete invocation object)
3. **Path params can be `required: true`** — the scanner handles these via URL templating
4. **Each operation needs `security: [{ x402: [] }]`** — without this, the scanner marks it `L2_AUTH_MODE_MISSING`
5. **Each operation needs a `responses["402"]`** with a detailed JSON schema of the payment-required response shape
6. **The 402 response schema should include examples** of the `accepts[]` items, `instructions.proofStructure`, and `network` values so agents can construct valid payment proofs

### Reference implementation

See `references/openapi-endpoint-meta-pattern.md` for the full Cloudflare Worker `handleOpenAPI()` + `ENDPOINT_META` implementation used on the GenTech x402 gateway (15 endpoints, 3 POST + 12 GET). This pattern has been deployed and verified live.

## Quick fix — OpenAPI spec patcher

When you can't edit the server source code (e.g. Docker container, third-party service), run a proxy patcher that fetches the live spec and adds the missing fields:

```typescript
// Hono-based OpenAPI patcher — proxies original, adds x-payment-info + security
import { Hono } from 'hono';
const app = new Hono();

const priceMap = { /* endpoint → price mapping */ };

app.get('/openapi.json', async (c) => {
  const resp = await fetch('https://origin.example.com/openapi.json');
  const spec = await resp.json();
  
  // Add contact + guidance
  spec.info.contact = { email: 'your@email.com' };
  spec.info['x-guidance'] = 'How to use this API...';
  
  // Add security scheme
  spec.components.securitySchemes.x402 = {
    type: 'apiKey', in: 'header', name: 'X-Payment-Proof',
    description: 'x402 micropayment proof'
  };
  
  // Add x-payment-info + security to every path
  for (const [path, methods] of Object.entries(spec.paths)) {
    for (const method of Object.keys(methods)) {
      const op = methods[method];
      const price = priceMap[path] || '0.005';
      op['x-payment-info'] = {
        price: { fixed: { mode: 'fixed', currency: 'USD', amount: price } },
        protocols: [{ x402: {} }]
      };
      op.security = [{ x402: [] }];
      if (!op.responses) op.responses = {};
      if (!op.responses['402'])
        op.responses['402'] = { description: 'Payment Required' };
    }
  }
  return c.json(spec);
});
```

Then expose via Cloudflare Tunnel or ngrok and register the tunnel URL on x402scan.

## Common pitfalls (from real failures)

- **Wrong token address silently breaks settlement detection** — before wiring any USDC/ERC-20 address into a gateway, revenue scanner, or settlement config, verify it on-chain with `eth_getCode` + symbol/decimals calls. A dead address means payouts are never detected, with no error. Canonical USDC per chain + the exact check commands: **`references/onchain-token-address-verification.md`** (proven Aug 12, 2026 — Revenue Monitor had a no-code Base USDC address).

- **x402scan says "No valid x402 response found"** — nearly always a v1 vs v2 format mismatch. The scanner expects the exact v2 shape. Check: `x402Version: 2` as a number, `scheme: "exact"`, `payTo` not `payment_address`, lowercase asset hex.
- **x402scan shows 0 valid resources** — OpenAPI schema is missing parameter defaults. Query params need `required: false` + a `default` value so the scanner knows what to send as a probe.
- **FastAPI `/openapi.json` custom route gets SHADOWED by the framework's auto-generated spec** — If you register `@app.get("/openapi.json")` on a FastAPI app created WITHOUT disabling the built-in route (`FastAPI(title=...)` default), the framework's auto-generated route (registered at app creation, carries `operationId` names like `serve_manifest__well_known_x402_bazaa`) WINS over your later custom route. Symptom: `curl /openapi.json` returns the auto spec (3.1.0, all paths as GET, no `security: []` markers) — NOT your hand-written spec. x402scan then probes free endpoints (`/.well-known/*`, `/health`, `/openapi.json`, `/`) as if they were paid and reports "N endpoints with errors". **Fix:** create the app with `FastAPI(title=..., openapi_url=None, docs_url=None, redoc_url=None)` so your custom spec is the ONLY one; verify route ownership with `python -c "import server; [r.path for r in server.app.routes if 'openapi' in r.path]"` (expect exactly one `/openapi.json`). Then mark every FREE endpoint with `"security": []` in the spec (the probe skips them) and keep `security: [{x402: []}]` only on paid routes. Also add `info.contact.email` — x402scan needs it for ownership verification (`OPENAPI_CONTACT_MISSING` warning). **Live example Aug 2, 2026:** GenTech gateway showed "7 endpoints with errors" on x402scan for exactly this reason; after `openapi_url=None` + free-endpoint `security: []`, spec served correctly (title v9.0.0, contact present, 7 free + 1 paid route).
- **nginx can shadow the live gateway with a stale static file** — If nginx has `location /openapi.json { root /var/www/...; }` AND proxies `/` to the gateway, the static file wins for that exact path. A month-old static `openapi.json` (e.g. "5 live x402-protected APIs" from June) silently serves instead of the live spec — curl shows 200 so it looks healthy. Check BOTH the static file's mtime and which nginx location matches (`nginx -T | grep -B2 -A6 "location /openapi.json"`). Prefer proxying `/openapi.json` to the gateway (single source of truth) or deleting the stale static file.
- **x402scan auto-indexing fails silently on missing `.json` alias** — The scanner probes BOTH `/.well-known/x402` AND `/.well-known/x402.json`. If only one path exists and the other returns 404, auto-indexing fails without a clear error. Always serve the same discovery document on both paths, or add a redirect/alias from `.json` to the canonical path. Verified: GenTech's own gateway had this exact issue (Jul 22, 2026) — `.well-known/x402` returned valid JSON but `.well-known/x402.json` returned 404, blocking x402scan and Agentic.Market auto-indexing.
- **Body empty on V2** — The x402-rs crate intentionally returns an empty body for V2 (only the header carries the payment-required JSON). This is technically acceptable per the crate's design but diverges from the Syra reference which includes JSON in both header and body. If a scanner reads body instead of header, it will fail.
- **Network names in human format** — Config files often use `"base-sepolia"` or `"solana-devnet"`. The internal SDK converts these to CAIP-2 for the header, but manual inspection of the config can mislead about what's actually sent.
- **Cached results on x402scan** — The scanner caches per URL. After fixing, navigate to the register page fresh (not just revisit) to force a new probe.
- **Marlin gateway lacks discovery** — Uses x402-rs middleware which handles the 402 flow correctly, but the gateway itself has no `/.well-known/x402` route. This must be added manually in the application code.
- **x402-check only scanned for deprecated header** — The ecosystem's primary validation tool (`suryast/x402-check`) originally checked `x-payment-required` (v1 deprecated) FIRST and `payment-required` (v2 canonical) as a fallback. This meant fully v2-compliant endpoints that only emit `payment-required` would be missed. **Fix:** swap header priority — `payment-required` first, `x-payment-required` as fallback. See [PR #12](https://github.com/suryast/x402-check/pull/12).
- **x402-rs V2 middleware produces empty body** — When using the V2 `PaymentRequirements` type, the 402 response body is `Body::empty()`. The payment-required JSON is only in the `Payment-Required` header. If a consuming client reads the body, it will get nothing. This is a design choice of the crate, not a bug.
- **x402-rs crate version 1.3.0 vs 2.0.2**
- **Default `payTo` is the Solana system program** — Some configs default to `11111111111111111111111111111111` (Solana system account) as the `payTo` address. This address cannot receive SPL token transfers. Without explicit configuration, all generated 402 responses contain a dead receiver address. The v2 spec requires `payTo` to be a valid recipient address for the specified token and chain.
- **V1 scheme class produces V2-stamped payload (missing `accepted` envelope)** — A common client-side anti-pattern: using `ExactSvmSchemeV1` (V1 client class) but passing `x402Version: 2`. V1 schemes produce flat payloads: `{ x402Version, scheme, network, payload }`. V2 payloads require an `accepted: PaymentRequirements` envelope object at the top level. The flat V1 payload is structurally incompatible with v2 facilitator verification even though it claims `x402Version: 2`. The correct v2 class is `ExactSvmScheme` (from `@x402/svm/exact/client`), not `ExactSvmSchemeV1`.
- **Solana CAIP-2 uses genesis hashes, not human names** — For compliance audits, note that Solana CAIP-2 format uses genesis hashes: `solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp` (mainnet), `solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1` (devnet). The v2 spec enforces CAIP-2 via a `${string}:${string}` Network type with colon-separator validation. Human-friendly config values like `"solana-mainnet"` or `"solana-devnet"` will fail zod schema validation in `@x402/core` v2.
- **x402-rs crate version 1.3.0 vs 2.0.2** — The Marlin gateway pins x402-rs crates at 1.3.0, where V2 `PaymentRequired` is missing the `extensions` field entirely (added in 2.x). This prevents advertising protocol extensions like Bazaar, fee payer info, or custom metadata. Gateways on 1.3.0 will fail x402scan probes that check for `extensions`. See `references/x402-rs-crate-internals.md`.
- **V1 uses `X-PAYMENT` header, V2 uses `Payment-Signature`** — The V1 `PaygateProtocol` const `PAYMENT_HEADER_NAME` is `"X-PAYMENT"`; V2 uses `"Payment-Signature"`. The Marlin gateway uses V2 price tags (`V2Eip155Exact`, `V2SolanaExact`), so it reads `Payment-Signature` and never emits the deprecated `X-PAYMENT` header.
- **"Expected 402, got 400" on production deployments** — The Hyperbolic x402 gateway (`hyperbolic-x402.vercel.app`) demonstrates this: input validation (Zod schema) runs BEFORE the payment middleware inside the route handler, so an unauthenticated request with an invalid body gets a 400 before the 402 can fire. **Fix**: apply the paywall as Express-level middleware (via `app.use()` or route-array middleware), not inside the handler after `schema.parse()`. The skill's x402scan registration section documents the general fix; this deployment is a live example of the same mistake.
- **x402-go sends checksummed asset addresses** — The Go SDK's default chain configs (`BaseMainnet.USDCAddress`, etc.) ship mixed-case checksummed addresses. The x402 v2 spec requires lowercase hex. The SDK's internal comparison is case-insensitive, so it works in practice, but the wire format (`"0x833589fCD6eDb6..."`) doesn't match the lowercase spec. Fix: lowercase the constants or add a marshal hook.
- **Go SDK also lacks discovery endpoint** — Like x402-rs, `mark3labs/x402-go` has no `/.well-known/x402` route. The middleware handles 402 correctly but servers using it need to add discovery manually. Same low-effort fix as the Rust gap.
- **Repo has compliance gap AND open security issues — defer the PR.** When a scanned repo has a minor compliance gap alongside open security issues, do NOT submit a compliance fix. Document the gap, add the repo to the Security-issue deferral category, and revisit after security issues are resolved. **Proven:** Jul 15, 2026 — adipundir/aptos-x402 (missing resource field + 2 facilitator-bypass issues).

## Cron execution workflow — efficient multi-repo scanning

When running the Compliance Scout cron (or any bulk x402 ecosystem scan), use this pattern to minimise round-trips and avoid redundant work:

### 1. Discover repos to scan

```python
from hermes_tools import web_search
# Search for multiple keyword combinations in one batch
for q in ["x402 gateway", "x402 api", "x402 payment-required header"]:
    web_search(f"site:github.com {q} 2026", limit=10)
```

Also check `xpaysh/awesome-x402` and the GitHub `topics/x402` page for newly listed projects.

### 2. Pre-scan: classify before cloning

Not every repo that mentions "x402" has actual API implementation code. Save time with a quick classifier:

| Check | Skip if | Actionable if |
|-------|---------|---------------|
| README describes a demo, slide deck, or concept | `CONVERSATION_LOG.md`, `agent.json` (no API code) | Has actual server middleware or client code |
| Only contains example configs, no src/ | Empty `src/`, only `examples/` | Has `src/`, `lib/`, `api/`, or `backend/` |
| Uses managed SDK (old Coinbase `@coinbase/x402`) | Hard to fix upstream, SDK-owned 402 generation | Has custom middleware, custom 402 response construction |
| Changelog says "v2 support" | Already compliant | No recent mentions of v2 |

### 3. Clone with depth 1, then pattern-scan

```bash
# Batch clone — one terminal call per 3-4 repos (parallel via bg)
git clone --depth 1 https://github.com/owner/repo.git
git clone --depth 1 https://github.com/owner2/repo2.git
```

Then use `search_files` (ripgrep) to find relevant code patterns across each repo:

```python
from hermes_tools import search_files
# Check for header name usage
search_files(pattern="X-PAYMENT|X-Payment|x-payment|PAYMENT_REQUIRED|payment_address", path="/tmp/repo")
# Check for v2 compliance
search_files(pattern="x402Version|payTo|scheme|accepted", path="/tmp/repo")
# Check for SDK version
search_files(pattern="@coinbase/x402|x402-express|@x402/core", path="/tmp/repo", file_glob="*.json")
```

### 4. Check existing PRs before submitting new ones

Before forking and opening a Tier 1 PR, verify a fix for the same issue doesn't already exist:

```bash
gh pr list --repo owner/repo --state open --json title,number,headRefName
```

Search for keywords: "v2", "payment-required", "lowercase", "payTo", "header". If a matching PR is already open, skip it and note the gap as "pending upstream merge" instead.

### 4.5 Verify fix timestamps against bot reviews

If a matching PR exists AND has bot feedback (e.g., Greptile flagged issues), check whether the fix was ALREADY pushed in a newer commit. Do NOT re-open a new PR or duplicate work without this check:

```bash
# Get the latest commit OID and its timestamp
gh pr view N -R owner/repo --json commits --jq '.commits[-1].oid, .commits[-1].committedDate'

# Check the bot's review timestamp
gh pr view N -R owner/repo --json comments \
  --jq '.comments[] | select(.author.login == "greptile-apps") | .createdAt'
```

If the latest commit on the PR branch is **newer** than the bot's review timestamp, the fix is already applied — no action needed. Greptile auto-re-evaluates on each push; the absence of a new comment just means the bot's re-scan hasn't triggered yet.

**Pitfall**: Do not rely on `updatedAt` of the PR itself — it updates on every event (comment, label, push), not just code changes. Compare the **bot comment timestamp** against the **commit date** specifically.

**Real example (Jul 16, 2026):** pay-skills #190 had Greptile feedback at Jul 15 14:46 UTC. The latest commit `2b45210` was pushed at Jul 16 08:13 UTC — clearly newer. The missing OpenAPI parameters that Greptile flagged had already been added in that commit. No re-work needed.

### 5. Endpoint probing for deployed services

For repos that deploy a live service (Vercel, Cloudflare, etc.), probe the actual endpoint:

```bash
# Check discovery
curl -s --max-time 10 https://target.example.com/.well-known/x402
# Check 402 behaviour
curl -s -D - -o /dev/null --max-time 10 https://target.example.com/protected-endpoint
# Check middleware order (400 vs 402)
curl -s -D - -o /dev/null --max-time 10 -X POST https://target.example.com/completions -H 'Content-Type: application/json' -d '{"bad":"data"}'
```

A 400 (validation error) instead of 402 means the paywall runs AFTER input validation — a classic "Expected 402, got 400" error. See the x402scan registration section for the fix.

### 6. Note non-actionable repos for future triage

Some repos are deliberately not v2-compliant or intentionally use custom headers. Document these in the scan report so the next cron run doesn't re-scan them. Categories:

- **Demo-only**: No actual implementation code (e.g. Samdevrel/x402-api-gateway)
- **Already compliant**: Full v2 support verified (e.g. quiknode-labs/x402-payments, x402-rails)
- **Closed issues**: Feature request already implemented (e.g. strands-agents/sdk-python #1959)
- **Pending upstream PR**: Issue exists but an open PR addresses it (e.g. coinbase/payments-mcp #22 → x402-foundation/x402#1052)
- **Security-issue deferral**: Compliance gap exists but repo has open security issues. Skip PR submission; document the gap in scan results and revisit after security issues close. (e.g. adipundir/aptos-x402 — missing resource field, 2 open facilitator-bypass issues)

Store findings in a scan-results reference file so future runs can diff against them.

### Incident log — gateway simulation-overwrite bug (Aug 11, 2026)

**Issue:** Real x402 payments were verified+settled by CDP but then **rejected at the last step** — the gateway returned `payment_proof_invalid / proof is not valid JSON` on every paid request. Result: 402 on retry, no settlement, zero revenue despite full discovery.
**Root cause:** In the `auto` verify mode dispatch, the `verify_proof_simulation(proof, price)` call ran **unconditionally** (missing `else`) after the CDP branch. The comment said "try CDP when a key exists, else simulation", but simulation ran *always*. When CDP correctly verified+settled a real EIP-3009 proof, the result was overwritten by simulation mode (which expects the old flat HMAC `{amount,recipient,nonce,validAfter,validBefore,signature}` object, not a base64 JSON envelope) → `json.JSONDecodeError` → "proof is not valid JSON" → 402. Every real payment bounced at the final gate.
**Fix:** Wrap the simulation fallback in `else:` so it only runs when there's no CDP key:
```python
else:
    # no CDP key → simulation (HMAC dev/ARC gateway proof format)
    valid, reason = verify_proof_simulation(proof, price)
```
Applied to BOTH the live gateway (`10-Labs/x402-gateway/server.py`) and the agent kit (`genTech-agent-kit/services/x402-gateway-server.py`) — the kit had the same bug. After the fix + `systemctl restart x402-api.service`, the self-settle went 402→200 with real data, and the on-chain Base USDC dropped (2.967→2.942, nonce 7), confirming settlement.
**Diagnostic signal:** if a paid endpoint returns `proof is not valid JSON` (without "or base64") while CDP creds are present and `PAYMENT_VERIFY_MODE=auto`, suspect this simulation-overwrite bug — check that `verify_proof_simulation` is gated behind `else:`.
**Documented where:** `x402-api-compliance` skill incident log + `marketplace-listings-registry.md`.

### Incident log — CDP Bazaar / Agentic.Market NOT indexing correctly-configured service (Aug 11, 2026)

**Issue:** After a real 0.025 USDC settlement on Base through the CDP facilitator (wallet 0x7ebff, nonce 7), Agentic.Market search still returns `{"services":[],"total":0}` for `gentechlabs`, `api.gentechlabs.net`, `gentech`. NOT-INDEXED despite the settlement landing and the gateway being correct.
**Root cause:** Not our configuration — a documented CDP platform gap. Verified all of:
- Our 402 challenge carries a valid `extensions.bazaar` block (title, description, input/output schema, seller) — confirmed live.
- The **official CDP validation endpoint** `POST https://api.cdp.coinbase.com/platform/v2/x402/validate` returns 200 with `bazaarExtension` present — the exact check the "Get discovered" docs say determines indexing eligibility. We pass.
- Settle uses `wrapFetchWithPayment` (canonical path that attaches `paymentPayload.resource`).
- **GitHub x402-foundation/x402#2112 (closed):** teams with 8+ successful CDP settlements across 5 setup iterations still weren't indexed; the documented `EXTENSION-RESPONSES` header (the diagnostic for indexing acceptance) was **never emitted** by the CDP facilitator. x402 ROADMAP notes "multiple facilitators see dozens of endpoints that aren't discoverable in Bazaar." Multiple independent reproductions.
**Fix / decision (Jordan, Aug 11):** **Stop the CDP-settlement-as-indexing lever** — it's a known platform bug, not something more settlements fix. Keep the gateway validated (it is). Shift indexing effort to the working discovery paths: **x402scan** (`/.well-known/x402` + OpenAPI probes) and **OpenDexter** (auto-catalogs from a real settlement through ITS facilitator, separate from CDP). These index via the discovery/OpenAPI surface the issue confirms is being read (32×/89× reads observed on other setups).
**Diagnostic signal:** if validation passes (200 + bazaarExtension) AND a settlement landed but the catalog still shows 0, check whether it's the CDP platform gap before burning more gas. The docs' own `EXTENSION-RESPONSES` header is the tell — if CDP never emits it, indexing is blocked on their side.
**Documented where:** `x402-api-compliance` skill incident log + `marketplace-listings-registry.md`.

### Incident log — OKX-compliant single-rail mode silently blocks every other facilitator (Aug 30, 2026)

**Issue:** Dexter-facilitated self-settlement failed with `unsupported_network` even though the gateway was listed as multi-rail, the wallet was funded, and the 402 challenge decoded perfectly by hand.

**Root cause:** the gateway ran with `X_OKX_COMPLIANT=1` (set Aug 25 for OKX's A2MCP validator, which rejects multi-network `accepts[]`). That mode emits a **single-rail X Layer (eip155:196) challenge** — but Dexter's facilitator/SDK has **no X Layer support**, so their SDK throws `unsupported_network` before building any payment. One env var turned a 5-rail gateway into a 1-rail gateway for every non-OKX client.

**Fix:** flip `X_OKX_COMPLIANT=0` and reorder rails **Base-first** in `X402_NETWORKS="base,xlayer,algorand,avalanche,solana"` (Base is the only rail all four facilitators settle — clients that naively take `accepts[0]` get a universally-settleable option). Restart the gateway. Re-run the OKX validator only with `X_OKX_COMPLIANT=1` temporarily, then flip back.

**Rule:** an OKX-mode env flag must never be left on outside an active OKX validation window. When any client fails with `unsupported_network` on a funded, compliant setup, decode the live `PAYMENT-REQUIRED` header FIRST — check what rails the challenge actually advertises vs what that client's facilitator supports, before debugging the client.

**Diagnostic lesson:** "each facilitator is different — probe each one's `/supported` to see exactly what it wants" (Jordan, Aug 30). `/supported` is the ground truth for every facilitator's rail + scheme list; wire challenges to match the intersection of rails your buyers actually use.

### Incident log — CDP rejects self-pays: `self_send_not_allowed` (Aug 30, 2026)

**Issue:** after fixing the challenge rails, the Dexter SDK settle against our own gateway got `payment_proof_invalid` and CDP returned `{"invalidReason":"self_send_not_allowed","isValid":false}` — buyer wallet (`0x7ebff…`, the signer/payer test wallet) was the SAME address as `payTo`.

**Root cause:** the CDP facilitator refuses payments where sender == recipient. Self-pays were fine in earlier tests; CDP now blocks them.

**Fix:** settle with a **different buyer wallet** than the `payTo` address. GenTech pattern: arb wallet `0x3d117…` (key in `secure/gentech-arb-wallet.json`) as buyer, signer `0x7ebff…` as seller. Keep two funded test wallets on standby for settlement testing — one will eventually be the payTo and fail with this error.

**Diagnostic order for a settled-then-rejected self-test:** SDK completes full handshake (balance OK → EIP-712 signed → payment dispatched) then facilitator rejects → check for self-send before suspecting envelope/format bugs. The gateway's rejection reason string appears in the client only as a generic code (`payment_rejected`); add a temporary gateway-side `print()` at the reject point (then REMOVE it) or read `journalctl -u x402-api` to see the facilitator's actual reason.

### Incident log — non-ASCII character in challenge description breaks Node client settlement (Aug 12, 2026)

**Issue:** The OpenDexter self-settlement (`@dexterai/x402` `payAndFetch`) returned `{ok:false, reason:"error", detail:"Invalid character"}` on every endpoint, even with a funded signable wallet (0x7ebf…96a, ~2.9 USDC on Base) and a spec-perfect 402. No payment was ever dispatched.

**Root cause:** The gateway's challenge `resource.description` contained an **em-dash** (`—`, U+2014): `"GenTech Labs x402 — Market"`. Node-based x402 clients serialize the payment envelope with `btoa(JSON.stringify({... resource: {description: "…—…"}}))`, and **Node's `btoa()` throws `Invalid character` on any char outside Latin-1** (U+0000–U+00FF). The em-dash is U+2014 → the `PAYMENT-SIGNATURE` base64 encode dies before any on-chain transaction is built. Confirmed in isolation: `btoa` with the em-dash threw; same object with a plain hyphen (`-`) encoded cleanly.

**Why this bites:** the 402 header itself decodes fine (it's our own base64 with UTF-8), so the server looks healthy — but EVERY Node-based paying client (Dexter SDK, many agent toolchains) fails at signature-build time. A gateway can be fully spec-compliant yet un-settleable by Node clients.

**Fix:** keep every field that gets base64'd into the payment payload **ASCII-only** (hyphen, not em-dash; no curly quotes, no smart typography). In the gateway, replace non-ASCII typographic chars in `description`/`resource`/`extensions.bazaar.info` strings with ASCII equivalents. Then **restart the gateway service** (systemd re-reads the file) and re-run the self-settle.

**Diagnostic order for "Invalid character" on a Node x402 client:**
1. Confirm the wallet is funded + signable on the target chain (not a funding gap).
2. Base64-decode the live `PAYMENT-REQUIRED` header and grep the payload for non-ASCII: `curl -s -D - URL | grep -i payment-required | tr -d '\r' | sed 's/^[Pp]ayment-[Rr]equired: //' | base64 -d | grep -oP '[^\x00-\x7F]'` — any hit is the culprit.
3. Reproduce in isolation: `node -e "console.log(btoa(JSON.stringify({description:'…'})))"` vs a hyphen — confirms the char class.
4. Fix the source string, restart the gateway, re-settle.

**Documented where:** `x402-api-compliance` skill incident log + `marketplace-listings-registry.md` row 8c (OpenDexter SETTLED Aug 12).

## Lane rules  
- **Tier 1 (quick PRs)**: Auto-execute, no notification needed  
- **Tier 2 (deep work)**: Label as **"Gentech Only"** — agent works it 24/7, never hits Jordan's inbox  
- Any deep work escalation must use the exact phrase "**Gentech Only**" so the build queue processor knows whose lane it is  
- **Time zone**: All job times in EST (Eastern Standard Time, UTC-5) when communicating with Jordan  
- **Cron scheduling**: Stagger related jobs 10 min apart to avoid inbox clutter. Default window: 12:00 UTC (7:00 AM EST)  
  
## Autonomous PR Pipeline (Gentech Only)

The **x402 Compliance Scout cron** (daily 12:10 UTC = 7:10 AM EST) runs this skill autonomously:

**Tier 1 — Quick wins** are auto-submitted as PRs: wrong header names, field names, asset casing, docs.
**Tier 2 — Deep work** is reported back labeled **"Gentech Only"** — agent works it 24/7, never hits Jordan's inbox.

The lane rule: x402 compliance fixes are pure code. No signups, no wallets, no human decisions needed.
All deep work items get the **Gentech Only** label so Jordan's inbox stays clean.

See `references/x402-pr-methodology.md` for the real PRs submitted and the submission flow.

## Tools

- **GenTech x402 Compliance Scanner** — `github.com/x402-foundation/x402/pull/2905` — portable Python compliance scanner contributed to the x402 Foundation repo. Validates endpoint 402 response shape, accepts[] schema, CORS, amount format, and OpenAPI discovery. Submitted as reference implementation for issue #2823 (payment-integrity verifier).
- **GenTech x402 Test Harness** — `test.api.gentechlabs.net` — free public reference endpoint for testing x402 compliance. See `references/test-harness.md`. Use this to validate client implementations before deploying.

- **x402-compliance-checker** — `scripts/x402-compliance-checker.py` — scan any endpoint for spec compliance. 42+ checks per endpoint. Generates fix templates. Used by the cron scout.

- **x402-check** — `github.com/suryast/x402-check` — CLI + npm library + GitHub Action to validate any x402 endpoint's Payment-Required header format. Note: PR [#12](https://github.com/suryast/x402-check/pull/12) fixes header priority for v2 detection.
- **x402trace** — `github.com/fardinvahdat/x402trace` — x402 debugger CLI for Base. Probe, validate, explain, reconcile.
- **x402 Surface Check** — `github.com/TateLyman/x402-surface-check` — No-payment public-surface checker for manifests, OpenAPI specs, and HTTP 402 challenges. Also available as [GitHub Action](https://github.com/marketplace/actions/x402-surface-check).
- **API Safety Suite** — `references/api-safety-suite.md` — Golden test harness that validates all 15 x402 endpoints every 6 hours. Runs as cron (job_id `59283121321a`). Results fed to Compliance Scout via context_from. See reference for setup and endpoint checklist.
- **@agentcash/discovery** — `npx -y @agentcash/discovery@latest discover` — Official x402scan discovery CLI. Validates OpenAPI spec and probes endpoints before registration. See the "Discovery tool" section above.
- **x402scan** — `https://www.x402scan.com/resources/register` — register your API URL
- **x402scan explorer** — `https://www.x402scan.com` — browse the ecosystem (18.62M txns, $863.98K volume as of July 2026)
- **Syra Marketplace** — email `support@syraa.fun` to list third-party APIs
- **x402 Discovery Spec** — `GET /.well-known/x402` must serve the resource catalog
- **x402-rs** — `github.com/x402-rs/x402-rs` — Rust SDK with Axum middleware (V1+V2)
- **x402-go** — `github.com/mark3labs/x402-go` — Go SDK with net/http, Gin, and MCP support (V1+V2)
- **x402-foundation/x402** — `github.com/x402-foundation/x402` — canonical multi-language SDK (6.3k ⭐)
- **quiknode-labs/x402-rails** — `github.com/quiknode-labs/x402-rails` — Ruby on Rails paywall middleware (v2 compliant)
- **quiknode-labs/x402-payments** — `github.com/quiknode-labs/x402-payments` — Ruby client gem for signing payment headers (v2 compliant)
- **Reference (Syra)** — `api.syraa.fun/.well-known/x402` — gold standard implementation
- **CDP Facilitator** — `https://api.cdp.coinbase.com/platform/v2/x402` — production facilitator
- **x402.org Facilitator** — `https://www.x402.org/facilitator` — testnet facilitator
- **Platform Directory** — `/root/vaults/gentech/references/platform-directory.md` — x402 ecosystem map: tracked repos, compliance statuses, PR states, tiers, and non-actionable categories. Updated by the Compliance Scout cron. Check before scanning new repos.

## Cloudflare WAF bypass for discovery endpoints

Cloudflare's WAF can block programmatic access to `/.well-known/` discovery paths while leaving other endpoints like `/health` accessible. This prevents marketplace auto-indexing because crawlers receive HTTP 403 instead of the discovery document.

### Symptoms
- `curl https://api.yoursite.com/health` returns 200
- `curl https://api.yoursite.com/.well-known/x402` returns 403 (Cloudflare error 1003)
- Works locally via `curl -H "Host: ..." http://localhost/`
- Both browser and curl User-Agents get the same 403

### Fix — Option A (quickest): DNS-only mode
Cloudflare Dashboard → DNS → tap orange cloud → toggle to **grey cloud** (DNS-only). Takes 5 seconds but loses CDN/DDoS protection for that subdomain.

### Fix — Option B (proper): WAF skip rule
Cloudflare Dashboard → Security → WAF → Custom rules → Create rule: Hostname equals `api.yoursite.com`, URI Path starts with `/.well-known/` → **Skip**. Add a second rule for `/v1/` paths.

### Pitfall — Grey cloud (DNS-only) breaks SSL if cert doesn't cover subdomain

Switching a Cloudflare-proxied subdomain to **DNS-only (grey cloud)** means Cloudflare no longer terminates SSL for that subdomain. Traffic goes directly to your origin server, which must present a valid SSL certificate matching the hostname.

**Symptoms:**
- After toggling from orange to grey cloud, the endpoint returns TLS errors
- Validator: `tls: failed to verify certificate: x509: certificate is not valid for any names`
- Works locally via `curl --resolve` or `curl -k`

**Fix — Get a Let's Encrypt cert that covers all subdomains:**
```bash
sudo systemctl stop nginx
sudo certbot certonly --standalone --non-interactive --agree-tos \
  -m admin@example.com --expand \
  -d example.com -d api.example.com -d arcade.example.com
# Then update nginx ssl paths and restart:
sudo systemctl start nginx
```

**Prevention:** Before switching to DNS-only, verify your origin has a valid cert covering the subdomain. The self-signed cert that works behind Cloudflare proxy won't work once you bypass it.

### Pitfall — 77k+ systemd restart loop
If a systemd service for your x402 gateway has `Restart=always` and the entry point doesn't exist, it accumulates tens of thousands of failed restarts filling logs.

**Root cause:** `ExecStart` references a module that doesn't exist (e.g. `server:app` but file is `gateway.py`). Working directory is missing the expected module.

**Fix:** Stop the service, verify the entry point exists, create missing file or update systemd service, reload and start.

**Prevention:** Verify the module exists before enabling:
```bash
python3 -c "import sys; sys.path.insert(0, '/path/to/app'); from mymodule import app; print('OK')"
```

## Incident log after every fix

Jordan's rule: **"After every mistake, we fix it and document how we fixed it so nobody repeats it."**

Every time a deployment issue or compliance gap is fixed:
1. Fix the root cause
2. Add an entry to the incident log in the compliance doc (`x402-compliance-standards.md`)
3. Update this skill if a new pitfall or workflow pattern was discovered

The log entry includes: **Date** — **Issue** — **Cause** — **Fix** — **Documented Where**

This captures operations lessons any agent should know, distinct from memory (user preferences) and transient task state.

## Verification checklist

### Validation tools

- **Agentic Market Validator** — `https://agentic.market/validate` — Tests x402 endpoints against Transport (6 checks), Payment Requirements (8 checks), and Bazaar Extension (5 checks). Use this as the final sign-off before registering on any marketplace. The `.well-known/x402-bazaar` manifest is a discovery resource (returns 200), not a paid endpoint (returns 402) — test both the manifest AND a real paid endpoint.
- **@agentcash/discovery** — `npx -y @agentcash/discovery@latest discover` — Official x402scan discovery CLI

### For your own API
- [ ] `GET /.well-known/x402` returns valid resource catalog with `baseGateway`
- [ ] `GET /.well-known/x402.json` also returns the same document (or redirects to canonical path)
- [ ] `curl -D- endpoint` returns HTTP 402 with `Payment-Required` header
- [ ] Base64-decode the header — must have x402Version: 2, scheme: 'exact', payTo
- [ ] No deprecated X-PAYMENT or X-PAYMENT-REQUIRED headers present (keep only Payment-Required / payment-required)
- [ ] Response body is free-form in v2 — do NOT require spec fields in body (only header matters)
- [ ] `maxTimeoutSeconds` present on every `accepts[]` entry
- [ ] Asset addresses are lowercase hex
- [ ] OpenAPI spec has parameter schemas with defaults
- [ ] Register on x402scan → verify "valid resources" count > 0

### For auditing third-party APIs
- [ ] Check `/.well-known/x402` exists and has `baseGateway`
- [ ] Verify 402 response uses V2 header format (not V1)
- [ ] Decode `Payment-Required` header — confirm `x402Version: 2`
- [ ] Check for deprecated v1 headers
- [ ] Compare body format to Syra reference
- [ ] Check if `resourceDetails` has per-endpoint pricing

### For source-code monorepo audits
- [ ] Map packages: gateway, facilitator, client — separate services or monolith?
- [ ] Compare `@x402/core` types from node_modules against local redefinitions
- [ ] Check Payload has `accepted` envelope (not flat `scheme`/`network`)
- [ ] Verify gateway and facilitator share consistent default network/asset/payTo
- [ ] Confirm `payTo` default is a real address (not a system contract)
- [ ] Check client uses `ExactSvmScheme` (v2) not `ExactSvmSchemeV1`
- [ ] Confirm header is `Payment-Required` not `X-Payment-Required`
- [ ] Verify `/.well-known/x402` route exists
- [ ] Check facilitator uses payload's `accepted` fields instead of reconstructing from env
