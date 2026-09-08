# CMC Watchlist Management

## Script Location
`/root/.hermes/profiles/gentech/scripts/cmc-watchlist.py`

Global cron copy: `/root/.hermes/scripts/cmc-watchlist.py`

## What It Does
Fetches prices for Jordan's watchlist via CMC API with CoinGecko fallback. Runs on a cron schedule every 2 hours (7 AM–10 PM ET). Silent unless a coin moves ≥1.5% since last check.

**Silent mode:** Outputs nothing if no coin moved ≥1.5% since last run. The `no_agent` cron delivers empty stdout as silence.

## Current Watchlist (8 coins)
```python
COINS = [
    {"symbol": "BTC",  "cmc_id": "1"},
    {"symbol": "SOL",  "cmc_id": "5426"},
    {"symbol": "LINK", "cmc_id": "1975"},
    {"symbol": "AVAX", "cmc_id": "5805"},
    {"symbol": "TAO",  "cmc_id": "22974"},
    {"symbol": "XAUt", "cmc_id": "5176"},
    {"symbol": "ONDO", "cmc_id": "26754"},
    {"symbol": "COQ",  "cmc_id": "28675"},
]
```

CoinGecko fallback IDs:
```python
CG_IDS = {
    "BTC": "bitcoin", "SOL": "solana", "LINK": "chainlink",
    "AVAX": "avalanche-2", "TAO": "bittensor", "XAUt": "tether-gold",
    "ONDO": "ondo-finance",
    "COQ": "coq-inu",
}
```

## Purpose by Coin
| Coin | Thesis | Why Tracked |
|------|--------|-------------|
| **BTC** | Store of value, crypto beta | Market context for all trades |
| **SOL** | Smart contract platform | Major position. Speed, scale, memecoin volume |
| **LINK** | Oracle network | Only well-known decentralized oracle |
| **AVAX** | Primary LP position | Fee farming, subnets, institutional adoption |
| **TAO** | AI / DePIN | Open-source AI network, decentralized inference |
| **XAUt** | Tether Gold — digital gold | Track gold price. Long-term safe haven, but user acknowledges it's not safer than anything else right now. Kept for monitoring, not active trading. |
| **ONDO** | RWA tokenization | Real-world assets on-chain, institutional bridge |
| **COQ** | Meme coin | AVAX ecosystem memecoin, community-driven |

## Data Sources
- **Prices**: CMC API (primary), CoinGecko (fallback)
- **API Key**: Loaded from `/root/.hermes/scripts/cmc_config.json` (primary). Falls back to `$CMC_API_KEY` environment variable (stored in both `/root/.hermes/profiles/gentech/.env` and `/root/.hermes/.env`).

### API Key Setup
When Jordan provides a new CMC API key:
1. Write to `/root/.hermes/scripts/cmc_config.json` in format `{"coinmarketcap_api_key": "xxx"}`
2. Append to `/root/.hermes/profiles/gentech/.env` as `CMC_API_KEY=xxx`
3. Append to `/root/.hermes/.env` as `CMC_API_KEY=xxx`
4. Verify with a quick CMC API call: fetch quotes for 1-2 known coins and check prices look right

The scripts (cmc-watchlist.py, defi-master-cron.py, cmc-news-trigger.py) all use `load_cmc_key()` which checks the config file first, then the env var. No hardcoded keys remain.

## Related Scripts
Other coin lists that mirror the watchlist changes:

| Script | Location | Purpose |
|--------|----------|---------|
| `defi-master-cron.py` | profile + global | Comprehensive DeFi cron (lightweight CMC tracking) |
| `cmc-news-trigger.py` | global only | News + price threshold alerts for watchlist tokens |

When pruning or adding coins, update **all three scripts** plus both profile/global paths. Search for the old symbol across all scripts after removing to ensure no stale references remain.

## Full Sync Checklist
When adding or removing a coin:
1. Edit COINS array in all 3 scripts (profile + global)
2. Edit CG_IDS dict in `cmc-watchlist.py` and `cmc-news-trigger.py` (profile + global)
3. Run `cp` for each script: profile → `/root/.hermes/scripts/`
4. Search for old symbol across all scripts to catch missed references
5. Verify: `python3 <script>` and check for correct output

## Editing the List

### Removing a coin
1. Delete its `{"symbol": ...}` entry from `COINS` in all 3 scripts (profile + global)
2. Delete its CoinGecko ID from `CG_IDS` in `cmc-watchlist.py` and `cmc-news-trigger.py`
3. Sync global copies: `cp` profile → `/root/.hermes/scripts/`
4. Verify: next cron tick should exclude the removed coin

### Adding a coin
1. Get CMC ID from `https://coinmarketcap.com/currencies/<slug>/` (numeric ID in page source)
2. Get CoinGecko ID from `https://api.coingecko.com/api/v3/coins/list` (JSON, search by symbol)
3. Add to `COINS` array in all 3 scripts + `CG_IDS` dict
4. Sync global copies
5. Test with `python3 cmc-watchlist.py`
6. Verify next cron tick shows the new coin

## Cron Job
- **Name:** `CMC Bullish Watchlist`
- **Job ID:** `0e3db2c4ffcb`
- **Schedule:** `0 7-22/2 * * *` (every 2 hours, 7 AM–10 PM ET)
- **Deliver:** Strategies group (`telegram:-1002916759037`)
- **Script:** `cmc-watchlist.py` (no_agent: true — script stdout IS the message)
- **Threshold:** 1.5% movement triggers a report; silent otherwise

## Pitfalls
- **Symbol must match CMC format** — e.g., "ONDO" not "Ondo", "XAUt" not "XAUT"
- **Multiple CMC entries per token** — some tokens have multiple listings; use the highest-market-cap one
- **CMC free tier limits** — may not return data for obscure or newly listed tokens
- **CoinGecko ID name inconsistency** — IDs don't follow a pattern ("avalanche-2" has a suffix, "bittensor" doesn't). Test new IDs against the `/simple/price` endpoint.
- **All 3 scripts must stay in sync** — if `cmc-news-trigger.py` still has an old coin, news alerts for it still fire. Search for the old symbol across all scripts after removing.
- **XAUt format**: The ticker is `XAUt` (uppercase X, A, U, lowercase t), not `XAUT`. CMC is case-sensitive for this symbol.
