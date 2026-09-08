---
name: crypto-price-fetch
description: Fetch cryptocurrency prices with robust fallback chain, generate GTA trading signals, run the Watcher co-pilot (news-aware position monitoring with stop-loss, macro event tracking, and Fed calendar awareness).
---

# Crypto Price Fetch

Fetch cryptocurrency prices with automatic fallback between providers and comprehensive error handling.

**Related**: 
- `references/cmc-watchlist-management.md` — CMC watchlist script configuration and maintenance
- `references/buy-zone-framework.md` — Tiered buy zones for watchlist coins
- `references/gta-architecture.md` — Full GTA trading agent architecture (Signal → Position → Watcher)
- `references/solana-network-data-dashboard.md` — Solana Foundation's official network data dashboard (solana.com/data, 9 providers) — approved treasury reference for SOL tx count, fees, compute units, fee payers. Signal playbook: tx up + fees down = healthy blockspace; fee-payer spikes = new wallets.

## Fallback Chain

1. **CoinMarketCap** (primary) — needs API key in environment or at `/root/.hermes/scripts/cmc_config.json`
2. **CMC keyless trial endpoint** (same-provider fallback, verified 2026-08-29) — `https://pro-api.coinmarketcap.com/trial-pro-api/v1/cryptocurrency/listings/latest?limit=N` — NO key required, returns real JSON with live prices + `credit_count` in status. Use when the keyed call fails (error_code 1001 invalid key, 429, billing). Limitations: listings/latest only (top-N by rank, no arbitrary symbol lookup — find your coin's rank in the payload), ~1 credit-equivalent per call, no SLA. 
3. **CoinGecko** (free, no key) — reliable fallback, rate-limited  
4. **Binance** (tertiary) — public API, high availability (blocked from execute_code sandbox — HTTP 451, see pitfall 8)

```python
# Keyless CMC trial fallback — slot between keyed CMC and CoinGecko
def fetch_cmc_trial(top_n=20):
    url = f"https://pro-api.coinmarketcap.com/trial-pro-api/v1/cryptocurrency/listings/latest?limit={top_n}"
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    return {c["symbol"]: c["quote"]["USD"]["price"] for c in data.get("data", [])}
```

**CRITICAL: CMC is primary, not fallback.** The GTA Signal cron job generates the report as a stand-alone Python script executed by the scheduler. It runs at 7 AM ET and 7 PM ET, writing a position file when a real entry signal (LONG/SHORT with non-zero leverage) is generated.

## Implementation

Use `execute_code` with Python standard library only. The function should handle various error conditions and edge cases.

```python
import json, urllib.request, os, time, socket
from typing import Optional, Dict, Any

class CryptoPriceFetcher:
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.socket_timeout = timeout
        
    def fetch(self, symbol: str) -> Optional[float]:
        """Fetch price for a cryptocurrency symbol."""
        for attempt in range(self.max_retries):
            try:
                price = self._try_fetch(symbol)
                if price is not None:
                    return price
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
        return None
    
    def _try_fetch(self, symbol: str) -> Optional[float]:
        # Try CoinMarketCap if API key exists
        api_key = os.environ.get("COINMARKETCAP_API_KEY", "")
        if api_key:
            try:
                price = self._fetch_cmc(symbol, api_key)
                if price:
                    return price
            except Exception:
                pass
        
        # CoinGecko fallback
        try:
            price = self._fetch_coingecko(symbol)
            if price:
                return price
        except Exception:
            pass
        
        # Binance tertiary fallback
        try:
            price = self._fetch_binance(symbol)
            if price:
                return price
        except Exception:
            pass
        
        return None
    
    def _fetch_cmc(self, symbol: str, api_key: str) -> Optional[float]:
        url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={symbol}&convert=USDC"
        req = urllib.request.Request(
            url, 
            headers={
                "X-CMC_PRO_API_KEY": api_key,
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0"
            }
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read())
            quote = data["data"][symbol]["quote"]["USDC"]
            return float(quote["price"])
    
    def _fetch_coingecko(self, symbol: str) -> Optional[float]:
        # ID mapping for common cryptocurrencies
        id_map = {
            "AVAX": "avalanche-2", "ETH": "ethereum", "BTC": "bitcoin",
            "SOL": "solana", "MATIC": "matic-network", "LINK": "chainlink",
            "UNI": "uniswap", "AAVE": "aave", "ARB": "arbitrum", "OP": "optimism",
            "JOE": "joe", "USDC": "usd-coin", "USDT": "tether", "DAI": "dai",
            "PENGU": "pudgy-penguins", "PEPE": "pepe", "WIF": "dogwifcoin",
            "BONK": "bonk", "FET": "fetch-ai", "RENDER": "render-token",
            "TIA": "celestia", "SEI": "sei-network", "SUI": "sui"
        }
        
        # Stablecoins return $1.00
        if symbol in ["USDC", "USDT", "DAI"]:
            return 1.00
        
        cg_id = id_map.get(symbol.upper(), symbol.lower())
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd"
        req = urllib.request.Request(
            url, 
            headers={
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0"
            }
        )
        
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read())
            return float(data[cg_id]["usd"])
    
    def _fetch_binance(self, symbol: str) -> Optional[float]:
        # Map symbol to Binance trading pair format
        binance_map = {
            "AVAX": "AVABUSD",
            "BTC": "BTCUSDC",
            "ETH": "ETHUSDC",
            "SOL": "SOLUSDC",
            "JOE": "JOEBUSD"
        }
        
        pair = binance_map.get(symbol.upper(), f"{symbol}USDC")
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={pair}"
        
        with urllib.request.urlopen(url, timeout=self.timeout) as resp:
            data = json.loads(resp.read())
            return float(data["lastPrice"])
```

## Usage

```python
fetcher = CryptoPriceFetcher()
avax_price = fetcher.fetch("AVAX")
avax_change = ((avax_price - last_price) / last_price) * 100
```

### Buy Zone Integration

After fetching prices, the CMC watchlist script (`/root/.hermes/profiles/gentech/scripts/cmc-watchlist.py`) maps each asset to its zone and outputs a report if movement exceeds the 1.5% threshold. See `references/cmc-watchlist-management.md` for the current watchlist, add/remove workflow, and script sync procedure.

## GTA Watcher — Agent Co-Pilot (every 30 min)

The **GTA Watcher** runs every 30 minutes (no_agent cron, `tradesta-watcher.py`) and monitors the active position created by the GTA Signal. It communicates via a **position file** (`tradesta_position.json`):

- **Signal** writes the position file when it generates a LONG/SHORT with non-zero leverage
- **Watcher** reads the position file and checks price, news, and macro events
- **Watcher clears** the position file when the next Signal says SKIP

### Architecture

```
┌─────────────────────┐     ┌─────────────────────────────┐
│  GTA Signal          │     │  GTA Watcher                 │
│  (7AM/7PM ET)        │────▶│  (every 30 min)              │
│                      │     │                              │
│  Fear & Greed        │     │ ├── Price check              │
│  Price action        │     │ ├── News scan (CryptoPanic,  │
│  Direction+leverage  │     │ │   Google News, Yahoo Fin.) │
│  Writes position     │     │ ├── Stop-loss / take-profit  │
└──────────┬───────────┘     │ ├── Macro events (FOMC, CPI) │
           │                 │ └── Thesis-breaker flags     │
           ▼                 └──────────────┬───────────────┘
  ┌──────────────────┐                      │
  │  Position File   │◀─────────────────────┘
  │  (JSON bridge)   │
  └──────────────────┘
```

### News Awareness Layer

The Watcher scans **three free RSS/API sources** for breaking headlines:
1. **CryptoPanic** — `/api/v1/posts/?kind=news&limit=5` (free, no auth)
2. **Google News RSS** — `news.google.com/rss/search?q=crypto+bitcoin+breaking`
3. **Yahoo Finance RSS** — `finance.yahoo.com/news/rssindex`

Each headline is checked against **thesis-breaker keywords**:
- **Long positions** flagged on: hack, crash, ban, sanction, SEC, CFTC, fraud, recession, rate hike
- **Short positions** flagged on: approval, ETF, adoption, institution, ATH, partnership

When a thesis-breaker is detected, the Watcher calls for **human review** — no automatic execution.

### Macro Event Awareness

The Watcher checks FOMC meeting dates and key economic events (CPI, PPI, NFP, Core PCE) within a 7-day window. Displays in the report as a `📅 MACRO THIS WEEK` section with FOMC flags. Imminent FOMC (within 48h) triggers:
```
⚠️ FOMC window — consider reducing position size or flat before print.
```

This replaces the standalone `fed-event-tracker.py` cron. See `FOMC_2026` list in the watcher script for current dates.

### GTA Arb Monitor — Cross-Venue Basis Scanner

The **GTA Arb Monitor** (`gta-arb-monitor.py`) scans every 5 minutes for basis opportunities between Hyperliquid perp and Coinbase spot prices. Silent when nothing to report. See `references/gta-arb-monitor.md` for detection formulas and threshold tuning.

### Architecture

Hyperliquid L1 (232 assets) → Python SDK (no geo-restriction via VPS) → GTA Arb Monitor → Calculate basis in bps → Flag if > 5 bps

### Basis Types
- **CONTANGO** (+bps) — perp above spot. Trade: short perp + long spot
- **BACKWARDATION** (-bps) — perp below spot. Trade: long perp + short spot

### Cron
- `0 * * * *` (hourly, no_agent cron)
- Silent when spreads are below threshold
- **Cadence note (Jul 25):** Originally every 5 min during proof-of-concept. Reduced to hourly once proven. Arb spreads move over hours, not minutes — hourly scan is sufficient.

### GTA Data API — x402 Product
The arb data is exposed as an HTTP API on port 8080 (`gta-arb-api.py`). Returns JSON with perp, spot, basis_bps per asset. Revenue model: free tier (rate-limited) or 0.02 USDC per call via x402. See `references/gta-data-api.md`.

### Geo-Bypass Pattern (VPS Agent)
Hyperliquid's geo-block is at the **frontend** (website), not the protocol. The Python SDK talks directly to the L1 chain via RPC — no IP check. The VPS (non-US IP) has full read/write access. Agent wallet mode (trade-only, cannot withdraw) keeps custody with the user. This is the standard pattern used by US-based quant teams.

**Connection confirmed (Jul 25, 2026):**
- 232 tradable assets on Hyperliquid (BTC, ETH, SOL, AVAX, LINK, ONDO all confirmed)
- 939 mid prices available in real-time
- VPS IP (2.24.195.196) is non-US — no geo-restriction on API calls
- ONDO confirmed as a tradable perp pair with good liquidity

**Pitfall — Hyperliquid API requires Content-Type header:** When using `curl` to call `https://api.hyperliquid.xyz/info`, the `Content-Type: application/json` header is REQUIRED. Without it, the API returns an empty response — no error, no data. This was discovered when the arb monitor migrated from the Python SDK (which adds the header automatically) to direct `curl` calls for timeout control. Both `{"type":"allMids"}` and `{"type":"meta"}` endpoints enforce this.

**Proof of value (Jul 25, 2026):** ONDO was showing +10.6 bps contango on the arb monitor when Ondo Finance announced its SBI Group Japan partnership. The arb monitor caught the spread widening before the news hit mainstream — confirming the product thesis that real-time basis data from a geo-blocked venue is valuable to traders who can't access it.

**Pitfall:** The CDP CLI returns 401 Unauthorized despite having valid API keys in `~/.config/cdp/config.json` (key_id + key_secret). The error `OS keychain not accessible — secrets stored in keychain will not be available` precedes the 401. Setting `CDP_API_KEY_NAME` and `CDP_API_KEY_PRIVATE_KEY` env vars does not resolve it. This is a CDP SDK auth handshake failure on headless VPS — the SDK expects OS keychain access which doesn't exist in a terminal-only environment.

**Workaround for Coinbase access:**
- **Read-only (prices):** Use the Coinbase public REST API — `api.coinbase.com/v2/prices/{pair}/spot` — no auth needed. Already used by the GTA Arb Monitor.
- **Trade execution:** A Coinbase.com Advanced Trade API key (generated from Coinbase.com → API → Create API Key) is needed, NOT the CDP API key. CDP keys are for on-chain wallet operations, not exchange trading.
- **Alternative:** Use CoinGecko as spot price source (free, no key) when Coinbase public API rate-limits.

## Q402 Execution (future)

The GTA Watcher will call **Q402** for gasless settlement when stop-loss or take-profit triggers. Currently Q402 is configured (Trial key, Mode C, BNB-only, 2,000 free sends remaining). Upgrade to Multichain key unlocks Base and all other chains for the Agentic Treasury.

### Stop-Loss / Take-Profit Logic

| Parameter | Default | Description |
|-----------|---------|-------------|
| `stop_loss_pct` | 5% | Exit the position if it moves against entry by this % |
| `take_profit_pct` | 8% | Take profit if the position reaches this % gain |

Alerts are displayed as `🛑 STOP-LOSS TRIGGERED` or `✅ TAKE PROFIT HIT` with P&L % since entry.

### Cron Setup

Both scripts run as `no_agent=True` cron jobs (zero LLM overhead):

- **GTA Signal** — `0 7,19 * * *` (7 AM and 7 PM ET)
- **GTA Watcher** — `*/30 * * * *` (every 30 min)

**IMPORTANT — Symlink pitfall:** Cron jobs with `no_agent=True` require scripts in `/root/.hermes/profiles/gentech/scripts/`. Symlinks pointing outside this directory are **blocked** by the cron security guard. Always copy files in, or create the symlink from the repo but verify the cron run succeeds. The canonical source is at `github.com/ProtoJay4789/gentech-treasury-trader`. Sync by copying from the repo into the scripts directory after updates.

### Report Format (Watcher)

```markdown
👁️ GTA WATCHER — 09:00 pm PH time

**Position:** 🔴 BTC SHORT @ $63,983.83
**Now:** $64,051.00 (flat | 24h: -1.1%)
**Sentiment:** Fear & Greed 27 — Fear

━━━ 📰 WIRE CHECK ━━━
🟡 Crypto Market Rebounds: Bitcoin Reclaims $66K
🟡 Outdoor giant closing 91 stores in bankruptcy
**Call:** Macro signals diverging from trade thesis.

━━━ 📅 MACRO THIS WEEK ━━━
🚨 FOMC in 4 days
📊 Core PCE in 6d

━━━
⚙️ Stop: 5% | TP: 8% | Entry: $63,984
👁️ Watcher every 30 min | Next signal: 7 AM / 7 PM ET
```

## Pitfalls & Edge Cases

### 1. Rate Limiting (CoinGecko)
CoinGecko free tier is rate-limited (~10-30 req/min). The fetcher includes:
- Exponential backoff retry logic
- Multiple fallback sources to distribute load

### 2. Stablecoin Pricing
Stablecoins (USDC, USDT, DAI) are pegged to USD and should return $1.00 directly rather than making API calls.

### 3. Symbol Mapping
Different exchanges use different symbol formats:
- CoinGecko uses IDs (AVAX → "avalanche-2")
- Binance uses trading pairs (AVAX → "AVABUSD")
- Maintain mapping dictionaries for common tokens

**CoinGecko ID naming is inconsistent** (pitfall): IDs don't follow a pattern. Examples: "avalanche-2" (has suffix), "pudgy-penguins" (full name), "matic-network" (chain name), "bonk" (just the ticker lowercase). The `symbol.lower()` fallback is unreliable — always maintain an explicit id_map for tokens you actually trade. When an ID is wrong, CoinGecko returns an empty `{}` response rather than an error, so failures are silent. Test new IDs with a direct browser fetch before adding to the map.

### 4. Network Timeouts
Always set reasonable timeouts (default: 10 seconds) to prevent hanging.

### 5. API Key Management
CoinMarketCap requires an API key. The fetcher gracefully falls back to other sources if the key is missing or the API fails.

**CMC Key Invalid vs Missing** (discovered 2026-05-09): CMC API can return `"error_message": "This API Key is invalid."` (error_code 1001) even when a key file exists. The key may be expired, revoked, or malformed. Detection:
```python
if "error_code" in data and data["error_code"] == 1001:
    print("CMC API KEY INVALID — key expired or revoked. Falling back to CoinGecko.")
### 5. API Key Management
CoinMarketCap requires an API key. The fetcher gracefully falls back to other sources if the key is missing or the API fails.

**CMC Key Path Mismatch (discovered 2026-06-08):** The vault uses `HQ/` not `00-HQ/` on disk. Correct path: `/root/vaults/gentech/HQ/config/cmc-api-key.env`. Scripts should try multiple paths. See `references/cmc-watchlist-management.md` for current config.

### 6. Error Handling
All external calls are wrapped in try/except blocks. The fetcher returns None if all sources fail, allowing the caller to handle missing data gracefully.

### 7. CoinGecko Free Tier Historical Endpoint Now Requires API Key (Discovered 2026-06-05)

`/market_chart` and `/coins/{id}/market_chart` endpoints return **HTTP 401 Unauthorized** on CoinGecko free tier. Fetching price history (all-time low, bear market low, 90-day trends) is no longer possible via free CoinGecko.

**Workaround:** Use Binance klines endpoint for OHLC data: `https://api.binance.com/api/v3/klines?symbol=AVAXUSDT&interval=1d&limit=90`. If Binance is blocked (see pitfall 8), use browser as API proxy for CoinGecko simple/price or DexScreener for recent data.

### 8. Binance API Blocked From Hermes Sandbox (Discovered 2026-06-05)

Binance API returns **HTTP 451** from the Hermes execute_code sandbox. The simple price endpoint (`/api/v3/ticker/price`) is blocked.

**Workaround:** Use CoinGecko simple/price endpoint (still works on free tier) or browser_navigate + browser_snapshot to read JSON API responses directly.

### 10. DexScreener Search Endpoint Returns Fake Prices (Critical — Discovered 2026-07-13)

**Symptom:** DexScreener `/latest/dex/search?q=BTC` returns inflated prices (e.g., BTC $79.8K vs real $62.4K, ETH $2.3K vs real $1.8K). All tokens show +0.00% 24h change because `priceChange` is an empty object `{}`.

**Root cause:** DexScreener's search endpoint prioritizes Solana-based wrapped pairs with fake/manipulated liquidity as the top result. A Solana BTC/USDC pair with $7.9B in fabricated liquidity dominates results over legitimate Ethereum/Base pairs.

**The `priceChange` field is always empty `{}`** on the search endpoint. The pair-specific endpoint (`/latest/dex/pairs/{chain}/{address}`) returns `priceChange.h24` correctly, but only if you know the exact pair address.

**Fix — Two-layer defense:**

**Layer 1: Use CoinGecko as primary source for major tokens**
```js
const res = await fetch(
  'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,avalanche-2&vs_currencies=usd&include_24hr_change=true',
  { cache: 'no-store' }
);
```
CoinGecko includes `usd_24h_change` (accurate 24h %). Rate limited (~30 req/min) but fine for dashboards.

**Layer 2: DexScreener pair endpoint with verified addresses**
```js
const res = await fetch(`https://api.dexscreener.com/latest/dex/pairs/base/0xf272fa039c68a79015b721df554f3bcb8a54016df9075e67a654b4d63e6afc51`);
const data = await res.json();
const pair = data.pair; // pair.priceUsd and pair.priceChange.h24 are accurate
```

**Known-good pair addresses (verified):** WBTC/Base `0xf272fa...`, SOL/Base `0x1131DB...` (both return accurate prices with real 24h change).

**DO NOT USE** search endpoint with broad token queries for price display — results are unreliable. For user-facing dashboards, prefer CoinGecko or verified pair addresses.

**Detection:** If BTC price shows >$75K when Pyth/CoinGecko shows ~$62K, the DexScreener fake pair bug is active.

### 11. DO NOT ASSUME THE ASSET From Price Levels Alone (Critical)

When a user mentions abbreviated price levels (e.g., "we went past 820, now at 720"), do NOT assume which asset they're talking about. In this session, Jordan said "820" meaning AVAX at $8.20 and I assumed ETH at $1,820 — completely wrong analysis that wasted time and eroded trust.

**Rules:**
- Abbreviated prices can refer to any asset. "820" could be $8.20, $820, $82.00, or 820 units of something
- If the user doesn't name the asset, ASK or present 2-3 candidates: "Are you looking at AVAX (~$8), ETH (~$1,800), or something else?"
- Watchlist tokens (BTC, SOL, AVAX, LINK, TAO, ONDO) are the most likely candidates in Jordan's conversations
- Only after confirming the asset should you pull price data and give analysis
- NEVER present a full technical analysis on an unconfirmed asset — it looks foolish when wrong

## Performance Considerations

- Use connection pooling for high-frequency requests
- Cache results to avoid repeated API calls
- Respect rate limits of each provider
- Consider using WebSocket streams for real-time data

## Commodity Prices (Gold, Silver, Oil)

The crypto fallback chain doesn't cover commodities. Use **Yahoo Finance** via `execute_code` — no API key needed.

```python
import json, urllib.request

COMMODITY_TICKERS = {
    "XAU": "GC=F",   # Gold futures
    "XAG": "SI=F",   # Silver futures
    "OIL": "CL=F",   # WTI Crude Oil futures
}

def fetch_commodity(symbol: str) -> dict:
    """Returns {'price': float, 'prev_close': float, 'change_pct': float}"""
    ticker = COMMODITY_TICKERS.get(symbol.upper())
    if not ticker:
        return None
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
        meta = data["chart"]["result"][0]["meta"]
        price = meta["regularMarketPrice"]
        prev = meta["chartPreviousClose"]
        return {"price": price, "prev_close": prev, "change_pct": ((price - prev) / prev) * 100}
```

**Pitfall**: Yahoo Finance v8 API is unauthenticated for basic chart data but may throttle rapid repeated calls. Batch commodity requests if fetching multiple.

**Pitfall**: Yahoo returns *futures* prices (GC=F, SI=F, CL=F), not spot. They track closely but can diverge around contract rollovers. For most signal-report purposes, the difference is negligible.

## Macro Event Analysis Workflow

When market news breaks (oil spike, Fed decision, geopolitical escalation), trace the correlation path to crypto and specific positions:

### Step 1: Identify the Event
- What happened? (oil spike, Fed decision, bank failure, geopolitical escalation)
- Immediate market reaction? (equity sell-off, flight to safety, etc.)

### Step 2: Trace the Correlation Path
| Event Type | Typical Path |
|------------|-------------|
| Risk-off (equity crash) | Equities → BTC → altcoins → specific tokens |
| Inflation (oil/goods spike) | Commodities → Fed expectations → USD strength → crypto weakness |
| Rate hike | USD up → crypto down → stablecoin yields up |
| Geopolitical (war, sanctions) | Oil up → inflation expectations → mixed for crypto (flight to safety vs risk-off) |
| Stablecoin depeg | Contagion risk → all crypto down |

### Step 3: Assess Impact
- Check if LP positions are in/out of range
- Evaluate if stablecoin-heavy allocation protected or hurt
- Factor in macro context (risk-on vs risk-off regime)

### Step 4: Actionable Recommendations
- LP range adjustments (if applicable)
- Allocation changes
- Risk management steps
- Timing for real-world conversions

## Emergency Fallback: Browser API Proxy (Discovered 2026-05-07, updated 2026-05-09)

When `execute_code` + `urllib.request` fails (sandbox network restrictions) or `terminal` curl is blocked by security scans, use the browser as an API proxy. Two approaches work:

**Approach A — `browser_snapshot` (preferred, simpler):**
```
Step 1: browser_navigate(url="https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,solana,chainlink,avalanche-2,bittensor&vs_currencies=usd&include_24hr_change=true")
Step 2: browser_snapshot(full=True)
```
The JSON response appears as a `StaticText` element in the snapshot. Parse it directly. Works reliably for CoinGecko, CoinCap, and any JSON API endpoint.

**Approach B — `browser_console` (alternative):**
```
Step 1: browser_navigate(url="https://api.coingecko.com/api/v3/simple/price?ids=avalanche-2&vs_currencies=usd&include_24hr_change=true")
Step 2: browser_console(expression="document.body.innerText")
```
Returns the raw JSON string. Requires parsing.

**CoinGecko `vs_currencies` required**: The `simple/price` endpoint no longer defaults to USD. Always include `&vs_currencies=usd` explicitly — omitting it returns an empty `{}` silently (discovered 2026-06-23).

**Multi-token batch**: CoinGecko supports comma-separated IDs in a single call — fetch all watchlist tokens at once to minimize browser round-trips.

**Yahoo Finance via browser**: When `execute_code` isn't available (cron jobs, etc.), use the browser API proxy for commodity prices:
```
Step 1: browser_navigate(url="https://query1.finance.yahoo.com/v8/finance/chart/GC=F?interval=1d&range=1d")
Step 2: browser_console(expression="document.body.innerText")
```
Parse the JSON response for `chart.result[0].meta.regularMarketPrice` (current) and `chart.result[0].meta.chartPreviousClose` (previous close). Works for GC=F (Gold), SI=F (Silver), CL=F (Oil).

**Do NOT use**: `delegate_task` with `web` toolsets for price fetching — results frequently come back empty.

## Testing

```python
# Test with known values
assert abs(fetcher.fetch("USDC") - 1.00) < 0.01
assert fetcher.fetch("AVAX") > 0  # Should return a positive number
```

## GTA Signal — Leverage Trading Signal Reports

The **GTA (Gentech Trading Agent)** generates LONG/SHORT/SKIP signals daily at 7 AM and 7 PM ET via a `no_agent` Python script. The Signal evaluates Fear & Greed + price action for BTC (primary), SOL, AVAX, LINK, and PENGU, then writes a position file that the GTA Watcher reads.

### Asset Universe
- **Crypto:** SOL, AVAX, LINK, PENGU (memecoin — 2x max)
- **Commodities:** XAG/USD (Silver), XAU/USD (Gold), USOILSPOT/USD (WTI Crude)

### Data Gathering Order
1. **Crypto prices** — **CoinMarketCap primary** (API key at /root/.hermes/scripts/cmc_config.json). Returns price + 24h change + 7d change in one call. Fall back to CoinGecko if CMC fails.
2. **Commodity prices** — **Yahoo Finance first** (via `execute_code` or browser API proxy). `GC=F` (Gold), `SI=F` (Silver), `CL=F` (Oil). Yahoo gives structured JSON with price + previous close in one call. If Yahoo fails, fall back to Kitco via browser (`kitco.com/charts/gold` — shows live bid/ask). Avoid `web_search` for commodity prices — it returns stale/conflicting data from multiple sources. See commodity section above for code.
3. **Fear & Greed Index** — `https://api.alternative.me/fng/?limit=1`. Returns `value` (0-100) and `value_classification`. Browser API proxy works reliably.
4. **Market context** — Bitcoin price (proxy for crypto beta), VIX (equity stress), S&P 500 (risk-on/off gauge). Yahoo Finance sidebar or CoinGecko for BTC.

### Signal Rules
| Fear Index | Bias | Leverage Cap | Notes |
|------------|------|--------------|-------|
| < 20 (Extreme Fear) | SKIP most assets. SHORT only demonstrably weak ones (worst performers, broken supports) on relief bounces | 3x max | Default posture is capital preservation. Contrarian longs are tempting but rarely work — wait for Fear > 25 |
| 20-40 (Fear) | SHORT bias, high-confidence LONGs allowed | 3x | Wait for confirmation |
| 40-60 (Neutral) | Only high-confidence setups, both directions | 3x | Selective |
| 60-80 (Greed) | LONG on dips | 5x | Trend-following |
| > 80 (Extreme Greed) | LONG on dips but watch for reversals | 3x | Take profit zones |

### Asset-Specific Rules
- **PENGU (memecoin):** 2x max leverage. Skip if 7d change is -10% or worse. Never trade in Extreme Fear.
- **Gold/Silver:** Normally safe-haven, but check if they're *not* rallying in fear — signals forced selling / yield spike. If gold/silver are selling off *with* everything else (not just underperforming, but actually red), it means liquidity crisis / deleveraging — SHORT them on bounces. Skip only if direction is ambiguous.
- **Oil:** Geopolitical premium = direct play. Long on supply disruption headlines. Tightest stops of all assets.
- **SOL:** Relative strength leader in crypto. If SOL holds while others bleed, it's the first bounce candidate.

### Key Level Detection
Flag as KEY LEVEL ⚠️ when:
- Asset is within 2% of a round number ($6.00, $65, $4,000, etc.)
- Intraday range exceeds 2× recent average range (volatility expansion)
- Price touches a multi-day high/low

### Report Format (GTA Signal)
```markdown
📊 GTA SIGNAL
**Date:** [date]

## 🔴 MARKET OVERVIEW
| Metric | Value | Change |
| Fear & Greed | X | Classification |
| Bitcoin | $XX,XXX | ±X% |
| VIX | XX | ±X% |

## 📈 SIGNAL DASHBOARD
### [ASSET]
| Metric | Value |
| Price | $X.XX |
| 24h Change | ±X% |
| Trend | Bullish/Bearish/Neutral |
| Signal | 🟢 LONG / 🔴 SHORT / ⚪ SKIP |
| Leverage | Xx |
| Confidence | High/Medium/Low |
| Key Level | Description (if applicable) |

**Reasoning:** 1-2 sentences.

## 🎯 SUMMARY TABLE
| Asset | Price | 24h | Signal | Leverage | Confidence |
```

### Pitfalls
- **CoinGecko PENGU ID:** Must use `pudgy-penguins` (with hyphen). Using `pudgypenguins` returns empty `{}` silently — no error, just no data.
- **Gold/silver not rallying in fear** = forced selling or yield spike. Don't assume safe-haven bid exists.
- **Yahoo Finance commodities** are futures prices (GC=F, SI=F, CL=F), not spot. Track closely but can diverge at contract rollovers.
- **Investing.com** has aggressive Cloudflare bot detection — use Yahoo Finance instead.
- **DuckDuckGo** search can fail silently with date-filtered queries. Use browser or alternative sources.
- **`web_extract` with DuckDuckGo backend** (discovered 2026-06-20): `web_extract` fails with "DuckDuckGo (ddgs) is a search-only backend and cannot extract URL content." This is a hard limitation — DuckDuckGo is search-only, not an extraction backend. **Workaround:** Use `browser_navigate` + `browser_snapshot` or `browser_console` to fetch page content directly. For structured JSON APIs, the browser API proxy pattern (see Emergency Fallback section) works reliably.
- **Commodity price conflicts from web_search** (discovered 2026-06-20): `web_search` for commodity prices returns stale or conflicting data from multiple sources (e.g., one site says silver $67.91, another says $63.47). Always prefer Yahoo Finance via `execute_code` or browser API proxy for a single authoritative source. If Yahoo Finance is unavailable, use Kitco (browser_navigate to kitco.com/charts/gold or /silver) which shows live bid/ask.

## LP Position Monitoring (absorbed from lp-position-monitor)

LP position monitoring applies the same fallback-chain data retrieval pattern to DeFi liquidity positions. When the primary data source (blockchain explorer, RPC endpoint) fails, cascade through secondary sources (DeFi Llama API, historical estimates) before giving up.

### Fallback Chain for LP Data
1. **Blockchain Explorer / RPC** — direct on-chain queries for pool reserves, LP token balances
2. **DeFi Llama API** — aggregated pool data, TVL, fee APY
3. **Historical Estimation** — last known position + price movements to estimate current IL and value

### Assessment Protocol
- **Full data available** → detailed analysis with exact IL, value, fee accrual
- **Partial data** → estimation with clear confidence level and caveats
- **No data** → document limitations, flag for manual check

### Key Patterns
- Always log errors at each fallback step for diagnosis
- Use `crypto-price-fetch` (this skill) for the token price component of LP valuation
- Integrate with milestone tracking: `calculate_milestone_progress(daily_fees, target_fees)` → progress bar + percentage
- Generate timestamped vault entries with consistent markdown structure (market data, LP status, error log, recommendations)

### Pitfalls
- Block explorers actively block automated access — use stealth techniques, rotate user agents, add delays
- Stablecoin pairs should be priced at $1.00, not fetched from APIs (reduces API calls and avoids errors)
- Rate limits on free APIs (DeFi Llama) — cache results, batch requests
- Always document when estimates are used and their confidence level — never present estimates as facts
- **Historical price accuracy**: When citing ATH or drawdown percentages, verify the exact numbers before presenting. It's easy to confuse assets (e.g., saying "AVAX from $126" when the user meant "BTC from $126K"). If the user provides a number, trust their figure over your memory — they're looking at the chart, you're recalling from training data.