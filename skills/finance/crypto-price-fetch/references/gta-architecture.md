# GTA (Gentech Trading Agent) Architecture

> Full architecture reference for the GTA Signal + Watcher system.
> Repo: `github.com/ProtoJay4789/gentech-treasury-trader`

## Overview

GTA is a three-script trading agent system that generates signals, monitors positions, and scans for cross-venue arbitrage. All scripts run as `no_agent=True` cron jobs with zero LLM overhead per tick.

## Components

### GTA Signal (`tradesta-signal.py`)
- **Schedule:** 7 AM and 7 PM ET
- **Data:** Fear & Greed (alternative.me), crypto prices (CMC → CoinGecko), commodity prices (Yahoo Finance)
- **Output:** Direction (LONG/SHORT/SKIP) + leverage + reasoning
- **Side effect:** Writes `tradesta_position.json` when a real entry is generated, clears it on SKIP

### GTA Watcher (`tradesta-watcher.py`)
- **Schedule:** Every 30 minutes
- **Data:** Current price (CoinGecko), breaking news (CryptoPanic + Google News + Yahoo RSS), macro events (FOMC dates, CPI, PCE, NFP)
- **Output:** Position status, stop-loss/take-profit alerts, news flags, macro calendar

### GTA Arb Monitor (`gta-arb-monitor.py`)
- **Schedule:** Every 5 minutes
- **Data:** Hyperliquid perp prices (Python SDK) vs Coinbase spot prices (public REST API)
- **Output:** Basis spread in bps per asset, silent when below 5 bps threshold
- **Watchlist:** BTC, ETH, SOL, AVAX, LINK, ONDO

### GTA Arb API (`gta-arb-api.py`)
- **Internal port:** 8081
- **Public URL:** `https://api.gentechlabs.net/arb`
- **npx proxy:** /arb location in api.gentechlabs.net nginx server block
- **Output:** JSON — perp, spot, basis_bps, type per asset
- **Revenue model:** Free tier (rate-limited) or 0.02 USDC/call via x402

### Position File (`tradesta_position.json`)
JSON bridge between Signal and Watcher:

```json
{
  "symbol": "BTC",
  "direction": "SHORT",
  "entry_price": 63999.42,
  "stop_loss_pct": 5,
  "take_profit_pct": 8,
  "leverage": "3x",
  "entered_at": "2026-07-25T12:05:33Z",
  "signal_source": "GTA Signal 7PM ET",
  "reason": "Continuing weakness in fear regime"
}
```

## File Locations

- **Canonical source:** `/root/repos/gentech-treasury-trader/src/`
- **Cron execution copies:** `/root/.hermes/profiles/gentech/scripts/`
- **Position file (runtime):** `/root/.hermes/profiles/gentech/scripts/tradesta_position.json`
- **Repo:** `github.com/ProtoJay4789/gentech-treasury-trader`

## nginx Deployment Pattern

Internal APIs run on high-numbered ports (8081+) and are exposed through nginx at `*.gentechlabs.net`. The nginx config at `/etc/nginx/sites-enabled/gentech` handles SSL termination and routing.

**Adding a new API endpoint:**
1. Start the service on an internal port (e.g., 8081)
2. Add a `location /path` block to the relevant `server_name` in nginx config
3. Reload: `sudo systemctl reload nginx`

**Example — `/arb` on `api.gentechlabs.net`:**
```
location /arb {
    proxy_pass http://127.0.0.1:8081;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**Existing subdomains:**
| Subdomain | Internal Port | Purpose |
|-----------|---------------|---------|
| api.gentechlabs.net | 8090 (main), 8081 (/arb) | API + Arb data |
| deals.gentechlabs.net | 8080 | Deal Tracker |
| prices.gentechlabs.net | 8082 | Crypto Price API |
| gas.gentechlabs.net | 8084 | Gas Price API |
| security.gentechlabs.net | 8086 | Token Security |
| rugcheck.gentechlabs.net | 8088 | Rug Check |
| search.gentechlabs.net | 8091 | Agent Search |

## Signal Rules

| Fear Value | Bias | Leverage Cap |
|------------|------|--------------|
| < 20 (Extreme Fear) | SKIP most, SHORT only weak ones | 3x max |
| 20-40 (Fear) | SHORT bias | 3x |
| 40-60 (Neutral) | Selective, both directions | 3x |
| 60-80 (Greed) | LONG on dips | 5x |
| > 80 (Extreme Greed) | LONG with caution | 3x |

## Cron Consolidation Pattern

When consolidating standalone no_agent scripts into GTA:

1. Extract the data-fetching logic from the old script
2. Add a function to the GTA Watcher that calls it
3. Integrate the result into the watcher report
4. **Pause** the old cron (don't delete — keep it for rollback)

**Already absorbed:**
- ✅ Fed Event Reminder (`fed-event-tracker.py`) → GTA Watcher macro awareness (FOMC dates + economic calendar, paused Jul 25)
- 📦 CMC Watchlist → planned for GTA Signal "assets on watch"
- 📦 Revenue Monitor → planned for GTA Watcher P&L section

**Cron security pitfall:** `no_agent=True` cron jobs validate that the script path resolves inside `/root/.hermes/profiles/gentech/scripts/`. Symlinks pointing outside are blocked. Always copy files in directly. Sync from the repo after updates.

## Q402 Integration Status

- **API Key:** Trial (q402_live_...), 2,000 free sends remaining
- **Expiry:** Aug 15, 2026
- **Chain:** BNB only (trial restriction)
- **Wallet Mode:** C (server-mediated, no private key in env)
- **Gas cost:** ~$0.001 per send
- **Upgrade needed for Base:** Multichain key at q402.quackai.ai/payment

## Rename History

- **Jul 25, 2026:** Renamed from "Tradesta" to "GTA" (Gentech Trading Agent)
- Cron names: GTA Signal, GTA Watcher, GTA Arb Monitor
- Script filenames still `tradesta-*.py` (internal convention — changing would break cron job references)
- Repo: `gentech-treasury-trader`

## Business Model

The Arb API follows the Trump API model — sell simple data users can't easily get elsewhere. Value prop: "US traders can't access Hyperliquid. We do. Pay 2¢ for the basis spread on 6 major assets."

Revenue tiers:
- **GTA Arb API** — raw data, x402 pay-per-call ($0.02/request)
- **GTA Execute** (future) — execute both legs for you (managed arb, subscription)
