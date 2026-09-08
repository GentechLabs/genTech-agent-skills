# API Fleet Audit — Find Silent Revenue Leaks (Aug 2026)

Audit recipe for a fleet of paid/live APIs. **A service can pass health checks
and still earn nothing.** Audit for *data*, not just *uptime*.

## Core Lesson

A paid API that returns placeholder data (hardcoded zeros, `[]`, `"placeholder"`)
cannot earn a cent even if a client pays the 402 challenge. It returns garbage,
the client never returns, and the listing sits on the marketplace looking live
but converting nothing.

## The Three Signals

| Signal | Meaning | Action |
|--------|---------|--------|
| ✅ HEALTHY | Real data, OR a proper `402` payment challenge | Ship it |
| ❌ PLACEHOLDER | Hardcoded zeros / `"placeholder"` / empty shells | **Fix first** |
| ⚠️ STUB | Empty array `[]` / dict `{}` | Wire the real engine |

**A `402` is HEALTHY for a paid endpoint** — it means the payment gate works.
Don't mistake a 402 for a failure.

## The Recipe

1. **Probe every endpoint** (`curl` or the kit's `services/api-audit.py`).
   Capture: HTTP status, body length, first ~150 chars.
2. **Classify** each response (data / 402 / placeholder / stub).
3. **Flag placeholders FIRST** — those are the silent revenue leaks.
4. **Fix the data layer.** Replace placeholder bodies with a real source:
   - A public API (CoinGecko, Etherscan, a free REST endpoint)
   - A live RPC call (`eth_gasPrice`, etc.)
   - A **working internal engine you already built — don't duplicate, reuse.**
     A thin proxy to a working service is faster + more reliable + less code.
5. **Add a pytest** asserting "not placeholder" — prevents regression.
6. **Restart + re-audit** — confirm the endpoint now returns real data.

## Detection Pitfall

Match **exact zero values** (`"price":0,`) NOT decimal zeros (`"price":0.09`).
`0.09` is real data; `0` alone is a placeholder. A naive regex flags valid
low-value responses as broken.

## Real Sources That Work From the VPS (verified Aug 2026)

- **CoinMarketCap** — key in `/root/.hermes/scripts/cmc_config.json` (`coinmarketcap_api_key`). Works.
- **CoinGecko** — free, no key. Needs explicit `&vs_currencies=usd` or returns empty `{}`.
- **Binance** — GEO-BLOCKED from the VPS (HTTP 451). Do NOT put in a fallback chain.
- **Ethereum gas** — Etherscan V2 `/v2/api?chainid=1&module=gastracker&action=gasoracle` (rate-limits without key) OR public RPC `eth_gasPrice` (needs `User-Agent` header, else 403).
- **Base gas** — `https://mainnet.base.org` `eth_gasPrice`.
- **Polygon gas** — `https://gasstation.polygon.technology/v2` `standard.maxFee` (needs `User-Agent` header, else 403).

**Gotcha:** public RPCs and gas stations return 403 to bare `urllib` — always send
`User-Agent: Mozilla/5.0`.

## Gateway Health-Check Bug (found Aug 2026)

The x402 gateway `/status` reported all backends "down" while they were healthy.
Two bugs:
1. It checked `{url}/health` but backends expose **`/v1/health`**.
2. `BACKEND_ROUTES` values are **tuples** `(base, public_prefix, backend_prefix)` —
   it interpolated the whole tuple into the URL. Use `route[0]` for the base.

Fix:
```python
for name, route in BACKEND_ROUTES.items():
    base = route[0]  # tuple (base, public_prefix, backend_prefix)
    r = await client.get(f"{base}/v1/health")
```

## Dead-Service Detection (the port-conflict variant)

A service can look "live" but be a non-functional shell:
- **Check for real provider keys.** The standalone Agent Search API had EXA/GROK/SURF
  keys all empty + payment stub mode — it would return empty even with a port.
  `PAYMENT_STUB_MODE=true` + no provider keys = not production-ready.
- **Check nginx → port mapping.** `search.gentechlabs.net` proxied to port 8091,
  but 8091 legitimately ran the gateway's `agent_discovery` backend. The nginx
  block pointed at the wrong service and only served 404s → comment it out
  (reversible) rather than delete, document why.

## Real Incident (Aug 3-4, 2026)

| Endpoint | Was | Fixed |
|----------|-----|-------|
| deal-tracker `/v1/deals` | stub `[]` | wired real CheapShark engine + 4 gaming endpoints |
| crypto-price `/v1/price` | `price:0.0 placeholder` | CMC→CoinGecko fallback chain |
| gas-price `/v1/gas` | all-zero | live RPC + Polygon gas station |
| token-security `/v1/score` | `score:0 unknown` | thin proxy to working Rugcheck (8088) |
| Agent Search API | dead shell (no keys, port conflict) | nginx block disabled |

Result: **13 live, revenue-capable APIs** (8 x402 gateway services + 5 standalone),
all gateway backends `ok`, 4 gaming sub-endpoints on the deals API.

## Audit Tool

`genTech-agent-kit/services/api-audit.py` — reusable auditor. Probe all defined
targets, classify, flag placeholders:
```bash
python3 services/api-audit.py                       # audit all
python3 services/api-audit.py --url http://localhost:8080/v1/price/BTC
```
Keep `PLACEHOLDER_TOKENS` to exact-zero matches (see pitfall above).
