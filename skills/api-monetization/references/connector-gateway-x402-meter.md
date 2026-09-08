# Connector Gateway × x402 Meter — the "front door / turnstile" seam

Verified Aug 23, 2026: self-hosted **OpenConnector** (`oomol-lab/open-connector`,
Apache-2.0, 4.9k⭐) as the connector/auth gateway, with a thin **x402 meter** in
front of it as the payment rail. The two layers stack instead of colliding:
the connector holds the tokens (custody / trust moat), the meter collects the
fee. This is the seam for "we own the auth boundary AND the payment rail."

## Why this wins (the strategic framing)
GenTech had an x402 rail earning ~$0 because it had no reason to be used. A
connector gateway gives agents a reason to pay: durable, real access to 1,395
providers (Gmail, Notion, GitHub, Shopify, …). So the collision is a clean
**stacking of layers**, not a fork:

| Layer | Tool | Role |
|-------|------|------|
| Connector/auth | OpenConnector (self-host) | identity — holds tokens, gates access |
| Payment metering | x402 meter (this recipe) | billing — 402 challenge, USDC settlement |
| Back-office | Paymenter / WHMCS / Blesta ext | invoices, plans |
| Distribution | Nevermined, Toku, OKX, Circle, x402scan | agents discover us |

## OpenConnector quick facts (self-host spike)
- Deploy prebuilt image: `docker compose up -d` → `ghcr.io/oomol-lab/open-connector:latest`, port 3000.
- Catalog: `GET /v1/providers` → `data[]` (1,395 providers; authTypes: api_key, oauth2, custom_credential, no_auth).
- MCP surface: `GET /mcp/tools` (list_apps, list_connections, search_actions, get_action_guide, execute_action).
- Connect a provider: `PUT /api/connections/github` with `{"authType":"api_key","connectionName":"default","values":{"apiKey":"<PAT>"}}` — it even resolves the account profile (accountId/displayName) without exposing the token.
- Execute: `POST /v1/actions/<service>.<action>` with `{"input":{...}}`. No-auth (arxiv) and credentialed (github.check_repository_starred) both return real data.
- **Security posture is real:** SSRF-guarded egress (`providerFetch`, validates URL + redirects + DNS), action allow/block policies, redacted run logs, encrypted tokens behind the boundary. This is what makes it a custody/trust moat vs Composio cloud (which holds tokens for you).
- OAuth providers require **OAuth client apps you register per provider** (README note) — that's the honest custody cost; OOMOL-hosted mode supplies the apps but you lose token custody.

## The meter — working FastAPI proxy
Sits on port 3010 in front of the connector on 3000. Reuses the SAME x402 v2
`PaymentMiddlewareASGI` pattern as the production gateway — do not rebuild the
rail, wrap the connector.

```python
# oc_meter.py (trimmed to the essential seam)
import os, httpx
from fastapi import FastAPI, Request
from x402.http import FacilitatorConfig, HTTPFacilitatorClient
from x402.http.types import RouteConfig, PaymentOption, RoutesConfig
from x402.http.middleware.fastapi import PaymentMiddlewareASGI
from x402.mechanisms.evm.exact import ExactEvmServerScheme
from x402.schemas import Network
from x402.server import x402ResourceServer

OC_URL = os.getenv("OC_CONNECTOR_URL", "http://127.0.0.1:3000")
PAY_TO = os.getenv("OC_PAY_TO_ADDR", "")   # treasury wallet
FACILITATOR = os.getenv("OC_FACILITATOR_URL", "https://x402.org/facilitator")
NETWORK: Network = os.getenv("OC_NETWORK", "eip155:8453")

app = FastAPI(title="Connector Meter")

@app.post("/v1/actions/{action_id}")
async def execute_action(action_id: str, request: Request):
    body = await request.json()
    async with httpx.AsyncClient(base_url=OC_URL, timeout=30) as c:
        r = await c.post(f"/v1/actions/{action_id}", json=body)
        try: return r.json()
        except Exception: return {"success": False, "error": r.text}

def _build_routes() -> RoutesConfig:
    return { f"POST /v1/actions/*": RouteConfig(   # NOTE: glob, see pitfall
        accepts=[PaymentOption(scheme="exact", pay_to=PAY_TO,
                               price=f"${os.getenv('OC_PRICE_USD','0.01')}",
                               network=NETWORK)],
        mime_type="application/json",
        description="Connector action — pay-per-call via x402",
    ) }

if PAY_TO:
    facilitator = HTTPFacilitatorClient(FacilitatorConfig(url=FACILITATOR))
    server = x402ResourceServer(facilitator)
    server.register(NETWORK, ExactEvmServerScheme())
    app = PaymentMiddlewareASGI(app=app, routes=_build_routes(), server=server)
```

Run:
```bash
export OC_CONNECTOR_URL=http://127.0.0.1:3000 OC_PAY_TO_ADDR=0x... \
  OC_FACILITATOR_URL=https://x402.org/facilitator OC_NETWORK=eip155:84532 OC_PRICE_USD=0.01
uvicorn oc_meter:app --port 3010
```

## Verified behavior
- Direct to connector (`:3000/v1/actions/arxiv.search_papers`) → **200** (unmetered).
- Through meter (`:3010/v1/actions/arxiv.search_papers`) → **402 Payment Required**, real x402 v2 challenge (USDC, network, payTo), body `{}`.
- Connector backend untouched/healthy after each meter call.

## Pitfalls (both cost real debugging time)

### 1. Middleware route key MUST be a glob `*`, not a FastAPI `{param}`
`PaymentMiddlewareASGI` matches paths with its own compiled regex
(`x402/http/x402_http_server_base.py::_get_route_config`). A route key like
`POST /v1/actions/{action_id}` does NOT match a request `/v1/actions/arxiv.search_papers`
— the middleware's `requires_payment()` returns `None` and the request **proxies through
UNPAID (200)**. Symptom: you think you're monetizing but calls pass for free.
Fix: use `POST /v1/actions/*` as the route key. Always verify by curling the meter
and confirming you get 402 before payment, not 200.

### 2. Facilitator network coverage — mainnet `exact` needs a real facilitator
Default `https://x402.org/facilitator` supports `exact` on **Base Sepolia**
(`eip155:84532`) but **NOT Base mainnet** (`eip155:8453`). Route init raises
`RouteConfigurationError: Facilitator doesn't support "exact" on "eip155:8453"`.
The `x402.org` facilitator is testnet-only. For production Base mainnet use
**CDP / Q402 / Dexter** (our prod gateway uses CDP/Q402). This is a one-line
config swap (`OC_NETWORK` + `OC_FACILITATOR_URL`), not a code change.

## Layer-stacking check before claiming revenue
Don't rebuild what exists. Before building a meter, inventory the fleet:
- A **connector gateway** (OpenConnector) provides identity/auth — not payment.
- The **x402 rail** (gold-402 / iagent-x402 / hackmoney-router402, live
  `api.gentechlabs.net`) provides metering/settlement.
- **Billing panels** (Paymenter/WHMCS/Blesta) are back-office, separate layer.
The meter is the thin seam that joins connector + rail so they cooperate rather
than conflict. Check `/root/vaults/gentech/09-Green Room/specs/openconnector-spike.md`
for the full spike log.
