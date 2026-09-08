# GTA Arb Monitor — Architecture & Script Reference

## Cron Jobs

| Cron | Cadence | Script | Purpose |
|------|---------|--------|---------|
| GTA Signal | 7AM/7PM ET | tradesta-signal.py | Direction + leverage from fear/greed |
| GTA Watcher | Every 30 min | tradesta-watcher.py | Position monitor + news + macro events |
| GTA Arb Monitor | Hourly | gta-arb-monitor.py | Cross-venue basis scan (silent unless >5bps) |
| GTA Arb API | Continuous | gta-arb-api.py | HTTP server on :8081, proxied at api.gentechlabs.net/arb |

## Hyperliquid Price Fetch (curl-based, no SDK timeout issues)

```python
def get_hl_prices() -> dict:
    url = "https://api.hyperliquid.xyz/info"
    payload = json.dumps({"type": "allMids"})
    cmd = ["curl", "-s", url, "-X", "POST", "-H",
           "Content-Type: application/json", "-d", payload, "--max-time", "8"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    return json.loads(result.stdout)
```

**IMPORTANT:** The SDK's `requests.post()` has no default timeout and can
hang indefinitely. Always use curl with `--max-time 8` and explicit
`Content-Type: application/json`.

## Funding Rate Fetch

```python
def get_funding_rate() -> dict:
    url = "https://api.hyperliquid.xyz/info"
    meta_payload = json.dumps({"type": "meta"})
    cmd = ["curl", "-s", url, "-X", "POST", "-H",
           "Content-Type: application/json", "-d", meta_payload,
           "--max-time", "8"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    meta = json.loads(result.stdout)
    # Parse perp universe for funding rates
    ...
```

## Basis Calculation

```python
def calc_basis(perp_price, spot_price):
    if not perp_price or not spot_price or spot_price == 0:
        return None, None
    diff = perp_price - spot_price
    basis_bps = round((diff / spot_price) * 10000, 1)
    typ = "CONTANGO" if diff > 0 else "BACKWARDATION"
    return basis_bps, typ
```

## Report Format

```
🔁 GTA ARB SCAN — <TIME> UTC

⚡ ARB OPPORTUNITY DETECTED ⚡
<ASSET> — <CONTANGO/BACKWARDATION> ±X.X bps
  Perp: $X.XX | Spot: $X.XX
  Trade: <Short/Long> perp + <Long/Short> spot
  Funding: ±X.XX% APR

━━━ FULL SCAN ━━━
Asset    Perp         Spot         Basis      Type
──────── ──────────── ──────────── ────────── ──────────────
BTC      $XX,XXX.XX   $XX,XXX.XX   +X.X bps   CONTANGO
...
```

Split long messages into **Part 1/Part 2** by default (Telegram ~4000 char
limit). Always split before sending.

## Public API Endpoint

`GET https://api.gentechlabs.net/arb`

Returns JSON with perp price, spot price, basis bps, and type for each
watched asset. The nginx config proxies port 8081.

## Current Watchlist

BTC, ETH, SOL, AVAX, LINK, ONDO, PAXG

CoinGecko IDs: bitcoin, ethereum, solana, avalanche-2, chainlink,
ondo-finance, pax-gold

## Scripts Location

All scripts live at:
`/root/.hermes/profiles/gentech/scripts/` (actual file copies, not symlinks)

Repo mirror at:
`/root/repos/gentech-treasury-trader/src/`

**CRITICAL:** Symlinks from repo to scripts dir are blocked by cron
security guard. Must use actual `cp` copies.
