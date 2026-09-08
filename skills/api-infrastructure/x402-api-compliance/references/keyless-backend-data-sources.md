# Keyless Backend Data Sources for x402 Gateway Services

How to build paid x402 services whose backends need NO API keys. All sources
below are keyless public endpoints verified working Aug 2, 2026 on the GenTech
gateway (6 services, all returning 200 with real data through the standard
`Authorization: x402 <proof>` flow).

## Architecture: gateway as the only payment gate

Each backend is a thin FastAPI service on its own port. The x402 gateway is the
ONLY payment gate: it verifies the standard proof and forwards `X-Payment-Proof`
for the backend's defense-in-depth check (backends accept any non-empty header —
the real verification happened upstream).

```bash
# systemd template — one service per backend, ports 8091-8094
# /etc/systemd/system/x402-backend@.service
[Unit]
Description=GenTech x402 Backend - %i
After=network.target
[Service]
Type=simple
WorkingDirectory=/root/gentechlabs/services
EnvironmentFile=/root/.hermes/profiles/gentech/.env
ExecStart=/usr/local/lib/hermes-agent/venv/bin/python3 %i.py
Restart=always
RestartSec=3
[Install]
WantedBy=multi-user.target

systemctl enable --now x402-backend@agent_discovery.service
```

## Per-service data source quirks (the gotchas)

### 1. agent_discovery → 8004scan.io ERC-8004 registry
- Base: `https://8004scan.io/api/v1/agents`
- **Response envelope is `{items, total, limit, offset}` — NOT a bare list, and
  NOT `agents`/`data`. Parse `data.get("items", [])`.**
- **Fields are snake_case**: `agent_id`, `chain_id`, `owner_address`,
  `x402_supported`, `is_testnet`, `supported_protocols`, `created_at`,
  `star_count`. Do not read camelCase (`agentId`, `chainId`).
- Filter `is_testnet` or `_testnet_chain(chain_id)` — the registry mixes
  testnet entries; exclude `84532`, `11155111`, `0`.
- The registry currently (Aug 2026) has heavy duplicates (many "Ave.ai Trading
  Agent" rows) — expect low match rates on specific names; empty query lists agents.

### 2. defi_lp_analytics → DexScreener
- Base: `https://api.dexscreener.com/latest/dex/tokens/{address}` — keyless, no
  auth, returns `{pairs: [...]}`.
- Efficiency scoring reuses the LFJ rebalancing engine heuristics:
  `fee_to_liquidity` ratio + `buy_ratio_24h` balance → efficiency_score 0-100,
  signal = rebalance/hold/optimize.
- Verified: wSOL returns 10 real pairs (meteora SOL/USDC $72.98, $1.1M liq).

### 3. wallet_analysis → Solana RPC + DexScreener
- Balances: `https://api.mainnet-beta.solana.com` POST JSON-RPC
  `getTokenAccountsByOwner` (programId `TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA`,
  encoding `jsonParsed`) + `getBalance`.
- Prices: per-mint DexScreener call (same endpoint as above) — 40-token wallets
  take ~40 sequential calls; cap at 40 tokens and reuse the price for SOL.
- Verify the address is a valid base58 mint before calling (400s on garbage).

### 4. nft_search → Magic Eden v2
- Base: `https://api-mainnet.magiceden.dev/v2/collections`
- **The `search` param is DEAD — returns HTTP 400. Fetch `offset=0&limit=100`
  (offset/limit MUST be multiples of 20 or 400) and filter client-side on
  name+symbol.**
- Verified: "dark" matches "Dark Nights: Death Metal" collections.

## Wiring into the gateway

`BACKEND_ROUTES` maps manifest service key → `(backend base, public path prefix, backend path prefix)`.
FastAPI `/v1/{service}/{path:path}` delivers `path` WITHOUT the service segment
(e.g. `score/0x...` for `/v1/security/score/0x...`). Strip the public prefix from
`path`, then prepend the backend prefix:

```python
BACKEND_ROUTES = {
    "token_security":      ("http://127.0.0.1:8088", "score/",     "/v1/score/"),
    "market_intelligence": ("http://127.0.0.1:8082", "price/",     "/v1/price/"),
    "agent_discovery":     ("http://127.0.0.1:8091", "search",     "/v1/agents/search"),
    "defi_lp_analytics":   ("http://127.0.0.1:8092", "lp/",        "/v1/defi/lp/"),
    "wallet_analysis":     ("http://127.0.0.1:8093", "portfolio/", "/v1/wallet/portfolio/"),
    "nft_search":          ("http://127.0.0.1:8094", "search",     "/v1/nft/search"),
}
URL_TO_SERVICE = {
    "security": "token_security", "market": "market_intelligence",
    "agents": "agent_discovery", "defi": "defi_lp_analytics",
    "wallet": "wallet_analysis", "nft": "nft_search",
}
```

Forward the proof to the backend on its expected header:
`"X-Payment-Proof": proof or ""` (rugcheck-style MVP gate accepts any non-empty).

## Manifest hygiene

The bazaar manifest (`/.well-known/x402-bazaar`) must list ONLY services with
live, correctly-routed backends. Prices per service in USD: token_security
$0.01, market_intelligence $0.005, agent_discovery $0.01, defi_lp $0.02,
wallet $0.02, nft $0.01. After any change, regenerate `x402.json` from the
bazaar manifest — the two files skew if edited independently, and the version
numbers (7.0.0 vs 8.0.0) are the tell.

## Full verification matrix

Run every service at every price point — the amount check is real:
| Service | $0.01 proof | $0.02 proof | no proof |
|---------|------------|------------|----------|
| security, market, agents, nft | 200 | 200 | 402 |
| defi, wallet ($0.02) | 402 | 200 | 402 |
