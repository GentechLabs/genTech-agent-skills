# API Placeholder-Data Audit — worked incident & detection reference

## The core insight

**A payment gate working ≠ endpoint earning.** Health checks passing and a
correct 402 payment challenge prove the *gate* works — they say nothing about
whether the *data layer* returns real, useful payloads. An endpoint can sit on
the marketplace looking live, return a perfect 402, get paid, and still hand
the client `price:0.0` / `[]` / `score:0`. That's dead surface area on the
payment rail: it converts nothing.

## Real incident (GenTech, Aug 3 2026)

Full audit of every running API service found **four placeholder endpoints**
while all four showed as "live / green":

| Endpoint | Returned | Root cause |
|----------|----------|-----------|
| deal-tracker `/v1/deals` | `{"deals":[]}` | Stub — real CheapShark engine never wired into FastAPI |
| crypto-price `/v1/price/BTC` | `price:0.0, source:"placeholder"` | Hardcoded placeholder |
| gas-price `/v1/gas` | `{ethereum:0, base:0, polygon:0}` | Hardcoded zeros |
| token-security `/v1/score/{mint}` | `score:0, level:"unknown"` | Hardcoded stub |

None could earn. The health endpoints all returned 200 `status:ok`. The lesson:
**audit for data, not just uptime.**

## The fix paths that worked

- **crypto-price** → CMC→CoinGecko fallback chain (CMC key at
  `/root/.hermes/scripts/cmc_config.json` or `COINMARKETCAP_API_KEY` env;
  fallback CoinGecko `simple/price`; Binance geo-blocked from VPS HTTP 451 so
  omitted). Stablecoins fast-path to $1.00.
- **gas-price** → live RPC `eth_gasPrice` (eth via
  `https://ethereum-rpc.publicnode.com`, base via `https://mainnet.base.org`)
  + Polygon gas station `/v2`. **Pitfall: these public RPCs return HTTP 403 to
  bare `urllib` — must send a `User-Agent: Mozilla/5.0` header.** Etherscan V2
  `/v2/api?chainid=1&module=gastracker&action=gasoracle` works keyless with a
  1/5s rate limit.
- **token-security** → thin proxy to the working Rugcheck engine (port 8088).
  Preserve the backend's 402 challenge so the endpoint stays x402-compliant.
- **deal-tracker** → wire the real CheapShark engine (`search_deals`) into the
  FastAPI server; the engine lives in a sibling dir, add its path to `sys.path`.

## Detection token list (match EXACT zeros, not decimals)

These substrings flag a placeholder. Crucially, `"price":0` alone is wrong —
it matches `"price":0.09` (real). Only match exact zero:

```python
PLACEHOLDER_TOKENS = [
    '"source":"placeholder"', '"source": "placeholder"',
    '"price":0}', '"price":0,', '"price": 0}', '"price": 0,',
    '"score":0}', '"score":0,', '"score": 0}', '"score": 0,',
    '"level":"unknown"',
    '"ethereum":0}', '"ethereum":0,', '"ethereum": 0}', '"ethereum": 0,',
    '"base":0}', '"base":0,', '"polygon":0}', '"polygon":0,',
    '"deals":[]', '"deals": []', '"watches":[]', '"risk_factors":{}',
]
```

## The reusable tool

`Gentech-Labs/genTech-agent-kit` ships `services/api-audit.py`:
- `python3 services/api-audit.py` — audit all defined targets
- `--url http://localhost:8080/v1/price/BTC` — single probe
- `--health-only` — just health endpoints

It classifies HEALTHY / PLACEHOLDER / STUB / REDIRECT and prints the body
snippet so you can see at a glance whether an endpoint returns real data or
junk.

## Why it's a revenue problem, framed for others

Every placeholder endpoint is a listing that "looks live but converts nothing."
The fix order: find placeholders → wire real data (public API / live RPC /
reuse an internal engine) → add a test → restart → re-audit. This is the
difference between "we have 16 APIs on the marketplace" and "16 APIs that
actually earn."
