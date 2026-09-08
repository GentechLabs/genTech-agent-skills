---
name: deal-tracker
description: "GenTech Shop — Shopping intelligence layer. Cross-store price comparison for GAMES (CheapShark, 35+ stores) and MOVIES (TMDB Watch Providers, 40+ platforms). CLI wishlist monitoring + FastAPI paid API with x402 micropayments. Rebranded from Deal Tracker to GenTech Shop (Jun 2026)."
version: 0.2.0
author: gentech
category: gaming
hermes:
  tags: [gaming, deals, steam, price-tracking, wishlist, genTech-shop, shopping-intelligence]
  trigger: "When user mentions game deals, Steam sales, price tracking, wishlist alerts, GenTech Shop, or asks 'what's the cheapest price for X'"
---

# GenTech Shop — Shopping Intelligence Layer

## Purpose
Cross-store price comparison for games AND movies. Two delivery modes:
1. **CLI tool** — wishlist monitoring, price alerts, Telegram notifications via cron
2. **Paid API** — FastAPI + x402 micropayments, serves game/movie deal data to other agents

**Rebrand:** Deal Tracker → GenTech Shop (Jun 2026). Same architecture, broader vision. Shopping intelligence that plugs into your world.

## API — Two Tiers

### MVP: CheapShark (free, no key)
- **Provider:** CheapShark (https://www.cheapshark.com/api/1.0)
- **Auth:** None required
- **Rate limit:** Be polite (1 req/sec recommended)
- **Stores:** 35 active stores
- **Built:** `10-Labs/deal-tracker/deal_tracker.py` — 12/12 tests passing

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/deals?title=X&upperPrice=N` | GET | Search deals by title |
| `/games?title=X&limit=N` | GET | Search games by title |
| `/deals?gameID=X` | GET | All deals for a specific game |
| `/stores` | GET | List all stores with IDs |
| `/deals?storeID=N` | GET | Filter by store |

**Key CheapShark gotchas:**
- `gameID` deals endpoint is `deals?gameID=X`, NOT `games/{id}/deals` (latter returns 500)
- `title` search is fuzzy — "mario" returns "Elmarion: Dragon Time" too
- Free games show `salePrice: 0` — handle $0 as "free" not "error"
- No price history endpoint — track manually via periodic snapshots
- **`storeName` is NOT in the deals response** — the `deals` endpoint returns `storeID` (numeric string), not `storeName`. You must resolve store names via the `/stores` endpoint and cache the mapping. The `CheapSharkClient` now does this automatically via `_resolve_store_name()`.
- **CheapShark 429s are aggressive and long-lived** — After ~5-10 rapid requests the IP gets 429'd for 60-120+ seconds. The `web_extract` tool bypasses this (different egress path). Use `web_extract` as a fallback for individual deal lookups when the terminal-based client is rate-limited.
- **CheapShark 429s can persist 5+ minutes** — In practice, a single burst of rapid calls (e.g. from a previous failed cron run) can lock the IP for 5+ minutes. The `/stores` endpoint recovers first (~60-90s), but the `/deals` endpoint stays blocked much longer. If you get 429 on `/deals`, the IP may be unusable for the entire cron window. **Strategy:** Always use `CheapSharkClient` (with built-in 1s delay) for the first call. If that 429s, do NOT retry from the same IP — switch to `web_extract` immediately or skip the sweep entirely and report the block.

### Fallback: Steam Store API (free, no key)

When CheapShark is 429'd (which can last 5+ minutes), use the **Steam Store API** as a zero-config fallback:

- **Endpoint:** `https://store.steampowered.com/api/appdetails?appids=ID&cc=us`
- **Auth:** None required
- **Rate limit:** Very generous (1 req/sec is fine)
- **Data:** Returns current price, discount %, and release date
- **Limitation:** Steam sales only — won't find deals at Fanatical, Humble, GameBillet

**Integration pattern for weekly_sweep.py:**
```python
# When CheapShark 429s, fall back to Steam API
import json
from urllib.request import urlopen

def check_steam_prices(watchlist_games):
    results = []
    for game in watchlist_games:
        appid = game.get('steam_appid')
        if not appid:
            continue
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=us"
        with urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        app_data = data.get(str(appid), {})
        if not app_data.get('success'):
            continue
        price_data = app_data.get('data', {}).get('price_overview', {})
        if price_data and price_data.get('discount_percent', 0) > 0:
            results.append({
                'title': game['title'],
                'price': price_data['final'] / 100,
                'normal': price_data['initial'] / 100,
                'savings': price_data['discount_percent'],
                'store': 'Steam'
            })
    return results
```

**When to use:** Only as fallback when CheapShark returns 429. Steam API is simpler but only covers Steam store. The batch all-deals approach (fetching top 500 deals and matching by steamAppID) should be tried first since it catches cross-store deals.

### Fallback: Steam Store API (free, no key)

When CheapShark is 429'd (which can last 5+ minutes), use the **Steam Store API** as a zero-config fallback:

- **Endpoint:** `https://store.steampowered.com/api/appdetails?appids=ID&cc=us`
- **Auth:** None required
- **Rate limit:** Very generous (1 req/sec is fine)
- **Data:** Returns current price, discount %, and release date
- **Limitation:** Steam sales only — won't find deals at Fanatical, Humble, GameBillet

**Integration pattern for weekly_sweep.py:**
```python
# When CheapShark 429s, fall back to Steam API
import json
from urllib.request import urlopen

def check_steam_prices(watchlist_games):
    results = []
    for game in watchlist_games:
        appid = game.get('steam_appid')
        if not appid:
            continue
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=us"
        with urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        app_data = data.get(str(appid), {})
        if not app_data.get('success'):
            continue
        price_data = app_data.get('data', {}).get('price_overview', {})
        if price_data and price_data.get('discount_percent', 0) > 0:
            results.append({
                'title': game['title'],
                'price': price_data['final'] / 100,
                'normal': price_data['initial'] / 100,
                'savings': price_data['discount_percent'],
                'store': 'Steam'
            })
    return results
```

**When to use:** Only as fallback when CheapShark returns 429. Steam API is simpler but only covers Steam store. The batch all-deals approach (fetching top 500 deals and matching by steamAppID) should be tried first since it catches cross-store deals.
- **Provider:** IsThereAnyDeal (https://api.isthereanydeal.com)
- **Key:** Saved to `config/deal-tracker.env`
- **Rate limit:** 1000 requests per 5 minutes (verified email)
- **Spec:** OpenAPI 3.1.0, 46 endpoints
- **Status:** Not yet integrated — ITAD key was claimed verified but never stored

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/games/search/v1` | GET | API Key | Search for games by title |
| `/games/prices/v3` | POST | API Key | Compare prices across all stores |
| `/games/overview/v2` | POST | API Key | Full price overview + historical low |
| `/games/history/v2` | GET | API Key | Price history chart data |
| `/games/historylow/v1` | POST | API Key | Historical low price |
| `/games/storelow/v2` | POST | API Key | Store-specific lows |
| `/deals/v2` | POST | API Key | Current deals across stores |
| `/service/shops/v1` | GET | None | List all stores |
| `/waitlist/games/v1` | GET | OAuth | Get user waitlist |
| `/webhooks/v1` | PUT | OAuth | Real-time deal alerts |

## Architecture

### CLI Tool (`10-Labs/deal-tracker/`)
- `deal_tracker.py` — CheapSharkClient, DealAnalyzer, WishlistMonitor, DealReporter
- `deal_runner.py` — CLI runner: check, search, hot, trend, add, remove, list, sync-steam
- `price_history.py` — snapshots to vault for trend analysis
- `test_deal_tracker.py` — 12/12 tests against live API
- `watchlist.json` — tracked games with target prices (default/Jordan)
- `watchlist-{steam_id}.json` — per-user watchlists (Vanito, etc.)
- **Weekly report pattern when `weekly_report.py` times out**: Use ad-hoc Python script to:
  1. Load watchlist JSON (items or games key)
  2. Use `CheapSharkClient.search_deals(title)` + filter by `steam_appid`
  3. Classify by discount tiers (50%+, 25-49%, 10-24%, <10%)
  4. Render with emoji headers and Steam IDs for verification
- Cron jobs: 9am + 9pm daily via Hermes

### Paid API (`10-Labs/deal-tracker-api/`)
- `api/server.py` — FastAPI app (7 endpoints, x402 payment gate)
- `api/payment.py` — PaymentVerifier (MVP stub)
- `api/cache.py` — TTL cache (5min games, 30min movies)
- `api/movie_client.py` — TMDB Watch Providers (simulation mode)
- `api/tests/test_api.py` — 25/25 tests
- **Deployed:** port 8080, nginx at `deals.gentechlabs.net`
- **Systemd:** `deal-tracker-api.service` (enabled, auto-restart)

### API Endpoints (16 total — Updated Jun 25, 2026)
| Endpoint | What | Price |
|----------|------|-------|
| `GET /v1/health` | Health check | Free |
| `GET /v1/stats` | Query stats | Free |
| `GET /v1/games/search?q=X` | Game deals across 35+ stores | $0.005 |
| `GET /v1/games/cheapest?q=X` | Cheapest game price | $0.005 |
| `GET /v1/games/{id}/news?count=N` | Game patch notes & devlogs | $0.001 |
| `GET /v1/games/{id}/release` | Release date & status | $0.001 |
| `GET /v1/games/{id}/track` | Track game (stateful, new items only) | $0.001 |
| `GET /v1/movies/search?q=X` | Movie streaming/buy/rent prices | $0.005 |
| `GET /v1/movies/cheapest?q=X` | Cheapest movie option | $0.005 |
| `GET /v1/movies/{id}/details` | Cast, studio, genres, runtime | $0.001 |
| `GET /v1/movies/{id}/trailers` | YouTube trailers | $0.001 |
| `GET /v1/intel/search?q=X` | Unified games + movies search | $0.005 |
| `GET /v1/intel/cheapest?q=X` | Cheapest across all platforms | $0.005 |
| `GET /v1/airdrops/check?wallet=X` | Airdrop eligibility | $0.01 |
| `GET /v1/airdrops/calendar` | Upcoming airdrops | $0.01 |
| `GET /v1/wallet/analyze?address=X` | Wallet analytics | $0.025 |
| `GET /v1/wallet/smart-money` | Smart money wallets | $0.025 |
| `GET /v1/nft/search?q=X` | NFT search | $0.005 |
| `GET /v1/nft/collection?name=X` | NFT collection info | $0.005 |

**PayAI facilitator** module (`api/payai_facilitator.py`) enables Solana-native x402 payments alongside existing CDP (Base).

**47/47 tests passing** as of Jun 25, 2026.

### MCP Server (SSE Mode — UE5.8 Compatible)

The GenTech Shop also runs as a standalone MCP server at `github.com/ProtoJay4789/genTech-shop`. Supports both stdio (for Claude Desktop) and SSE (for Unreal Engine 5.8).

**MCP tools available:**
- `gaming_deals` — Steam wishlist price/deal checker
- `release_calendar` — Upcoming game releases
- `poe2_build_health` — Path of Exile 2 patch impact
- `gaming_hub_status` — Data sync status

**UE5.8 Setup:**
```bash
# Start server in SSE mode
cd /tmp/genTech-shop
pip install -r requirements.txt
python server.py sse    # listens on http://localhost:8000/sse

# Expose externally (for demos):
tunnelto -p 8000        # generates public URL (needs tunnelto.dev API key for custom subdomain)
```

In UE5.8: Plugins → MCP Client → add connection with SSE transport → paste URL.

### V2 (Week 2)
5. **Target price alerts** — User sets target price per game, alert when hit
6. **Auto-buy flow** — Agent prompts user → opens store page → completes purchase
7. **Game Release Intelligence** — Track unreleased wishlist games for devlogs, release date announcements, trailers. Uses Steam News API + appdetails. Stateful (only alerts on NEW news).
8. **Multi-user support** — Per-user watchlists, vanity URL resolution, auto-detection in reports.
9. **Patch Notes API** — FastAPI endpoints for game news, release dates, and stateful tracking. Module: `api/patch_notes.py`.

### V3 (Future)
7. **ITAD premium tier** — Integrate IsThereAnyDeal for 70+ stores, price history, webhooks
8. **x402 payments** — Agent-to-store crypto payments (when stores support it)

## Data Flow
```
Steam Wishlist → ITAD Price Check → Compare 70+ Stores
                                          ↓
                                   Price History (vault)
                                          ↓
                                   Telegram Alert
                                   "Elden Ring is $51.59 at GameBillet
                                    (cheapest right now)
                                    Steam has it at $59.99
                                    Historical low: $29.95"
```

## References
- `references/movie-api.md` — TMDB Watch Providers API, JustWatch, physical media data sources
- `references/cheapshark-api.md` — CheapShark API endpoints and gotchas
- `references/cheapshark-rate-limit-fallback.md` — CheapShark 429 fallback pattern using web_extract, store name resolution, and batch all-deals approach
- `references/itad-api.md` — IsThereAnyDeal API (premium tier)
- `references/steam-wishlist-api.md` — Steam wishlist integration
- `references/weekly-report.md` — Weekly tiered discount report formatter
- `references/release-intelligence.md` — Game Release Intelligence: Full news coverage (wishlist + recently played), Steam News API, Steam Owned Games API, news categorization, auto-discovery pattern
- `references/installed-games-auto-discovery.md` — Two-phase installed games discovery: auto-discover from Steam API → user curates → ongoing news scanning. JSON structure, timestamp conversion, file-based control.
- `references/multi-user-setup.md` — Multi-user watchlist configuration
- `references/steam-api.md` — Steam Web API for appdetails, news, user profiles, owned games
- `references/multi-user-and-identity.md` — Steam AppID cross-referencing, multi-user watchlists, Steam News API
- `references/verified-deal-check.md` — Pattern for 100% verified game identity checks (no fake games)
- **Prompt to customize** — When building app UI: "What would you like to track?" with checkboxes. Both checked by default.
- **Toggle anytime** — Users can enable/disable features in settings without losing data.
- `references/multi-user-and-identity.md` — Steam AppID cross-referencing, multi-user watchlists, Steam News API

## Files
- `10-Labs/deal-tracker/deal_tracker.py` — CheapShark client (games) with Steam AppID cross-referencing
- `10-Labs/deal-tracker/deal_runner.py` — CLI runner (multi-user: `sync-steam [steam_id_or_vanity]`, `toggle <steam_id> <feature> <on|off>`)
- `10-Labs/deal-tracker/weekly_report.py` — Tiered discount report (multi-user: auto-detects all watchlists)
- `10-Labs/deal-tracker/weekly_sweep.py` — Standalone weekly sweep script (rebuilt Jul 2026, uses batch all-deals approach)
- `10-Labs/deal-tracker/release_intel.py` — Game Release Intelligence (news + release dates + Early Access detection, stateful)
- `10-Labs/deal-tracker/price_history.py` — price snapshots
- `10-Labs/deal-tracker/watchlist.json` — Jordan's games (default watchlist)
- `10-Labs/deal-tracker/watchlist-{steam_id}.json` — Per-user watchlists
- `10-Labs/deal-tracker/.patch-notes-state/` — Per-game release intel state (seen news IDs, release dates)
- `/root/get_wishlist_names.py` — Jordan's full Steam appid list (86 games, hardcoded array, useful fallback when watchlist.json is missing)
- `10-Labs/deal-tracker-api/api/server.py` — FastAPI paid API
- `10-Labs/deal-tracker-api/api/patch_notes.py` — Patch Notes API module (news + release endpoints)
- `10-Labs/deal-tracker-api/api/movie_client.py` — TMDB client (movies)
- `10-Labs/deal-tracker-api/api/payment.py` — x402 payment verifier
- `10-Labs/deal-tracker-api/api/cache.py` — TTL cache layer
- `config/deal-tracker.env` — ITAD API key (future)

## Telegram Alert Format
```
🎮 DEAL ALERT: {game_name}
💰 Best Price: ${price} at {store} ({cut}% off)
📊 Price Range: ${low} - ${high}
📈 Historical Low: ${history_low}
🔗 Buy: {affiliate_url}
```

## Discount Tiers (Yield Rainbow Style)

Every deal gets classified by discount depth — no more flat dumps:

| Tier | Emoji | Range | Meaning |
|------|-------|-------|---------|
| Deep Cut | 🔥 | 50%+ off | Real deal — buy now |
| Solid Sale | 💰 | 25-49% off | Worth considering |
| Light Mark | 🏷️ | 10-24% off | Meh, maybe wait |
| Barely Touching It | 📉 | <10% off | Skip — not a real sale |

**Report structure:**
```
🔥 DEEP CUTS (50%+ off)
━━━━━━━━━━━━━━━━━━━━━━━
Game A — $9.99 (was $39.99) 75% off @ Store

💰 SOLID SALES (25-49% off)
━━━━━━━━━━━━━━━━━━━━━━━
Game B — $14.99 (was $24.99) 40% off @ Store

🏷️ LIGHT MARKS (10-24% off)
━━━━━━━━━━━━━━━━━━━━━━━
Game C — $17.99 (was $19.99) 10% off @ Store

📉 BARELY TOUCHING IT (<10%)
━━━━━━━━━━━━━━━━━━━━━━━
Game D — $28.99 (was $29.99) 3% off @ Store

🚨 UNRELEASED / UPCOMING
━━━━━━━━━━━━━━━━━━━━━━━
Game E — Not yet available (wishlist tracked)
```

## Subscription Price Flags

Some stores (Green Man Gaming XP, Humble Choice) have member-only pricing. Flag these:
- Add `(XP)` or `(Member)` suffix to price when subscription-required
- Show both member and non-member price when available
- Never assume user has a subscription — show standard price as primary

## Sale Period Tracking

Detect and tag major sale events:
- Steam Summer/Winter Sale
- Epic Mega Sale
- GOG Summer Sale
- etc.

Add sale period context to reports when active:
```
📢 ACTIVE SALE: Steam Summer Sale (ends Jun 30)
```
## Identity / Multi-user (CRITICAL — fixed Aug 2026)

**Every user must have their OWN watchlist file, and every script/cron job must reference ONE file by identity.** The old design had ALL scripts (jordan_sweep*, vanito_sweep*, weekly_sweep) read the same single `watchlist.json` — so "Jordan's" weekly report was actually Vanito's games (or vice versa) depending on which job ran. That is exactly the "you didn't know who was who" bug.

**Canonical files (deal-tracker dir):**
- `watchlist-vanito.json` — Vanito's 86 games (was `watchlist.json`)
- `watchlist-jordan.json` — Jordan's list (CURRENTLY EMPTY; needs Jordan's Steam ID to sync)
- `user_sweep.py <watchlist_path> "<User Label>"` — the ONE identity-aware sweep. Reads only its own file, tags output with the user label, CheapShark-batch by AppID → Steam API fallback on 429.

**Cron jobs wired to identity:**
- `[Vanito] Weekly Sales Sweep` (1c25463fc281) → `user_sweep.py watchlist-vanito.json "Vanito"`
- `[Jordan] Weekly Sales Sweep` (80fd54684d86) → `user_sweep.py watchlist-jordan.json "Jordan"`
- `[Jordan] Game Release Intelligence` (41f8e6d0e24b) → reads `watchlist-jordan.json` only

**Jordan's Steam identity:** vanity `ProtoJay4789` resolves to steamID64 `76561198068413360`. `OJAY4789` does NOT resolve. Wishlist API (`store.steampowered.com/wishlist/profiles/{id}/wishlistdata/`) requires a PUBLIC profile — if it returns a 1MB HTML "sign in" page, the profile is private and you cannot auto-sync. Get the Steam ID from the user instead.

**Pitfalls**

- **CRITICAL: Always sync from Steam wishlist first** — Fuzzy title matching returns unrelated games (e.g., "Nancy Drew" shows up when it's not on the wishlist). BEFORE running deal checks, sync the actual Steam wishlist to get exact Steam AppIDs:
  ```bash
  python3 deal_runner.py sync-steam <steam_id>
  ```
  Then filter deals by `steam_appid` field, not title similarity. This eliminates fake games entirely.

- **CRITICAL: CheapShark gameID deals endpoint returns unrelated games** — `deals?gameID=X` returns fuzzy/related results, NOT exact matches. NBA 2K26 shows up for "Elden Ring" gameID. `get_cheapest_price()` MUST use `deals?title=X` with title-similarity filtering instead of gameID. This is the #1 integration gotcha.
- **CRITICAL: Single-word titles match wrong games** — "Covenant" matched "Succubers! Dark Covenant" because fuzzy title matching found the word. FIX: Use Steam AppID as primary cross-reference. For Steam-synced games, `game_id` IS the Steam AppID. When `effective_appid` is set and no deals match that AppID, return None (game unreleased/not on sale) instead of falling through to title matching.
- **Steam AppID cross-referencing pattern** — `get_cheapest_price(game_id, title, steam_appid)` now uses a two-strategy approach: (1) If Steam AppID available, search by title then filter by `steamAppID` field in CheapShark results; (2) Only fall back to strict title matching if no AppID. Single-word titles require exact word match; multi-word require 70%+ overlap and deal title not drastically longer.
- **Early Access detection** — Steam API doesn't have a native `early_access` flag. Detect from `detailed_description` containing "early access" text. Early Access games: (1) show `coming_soon: false` but are still in EA, (2) cannot have release dates or pre-orders, (3) often increase price at 1.0 launch. Track `is_early_access` in results and show `[Early Access]` tag + price warning in reports.
- **Currency parameter for Steam API** — `appdetails` endpoint returns regional pricing. Use `cc=us` (or `cc=uk`, `cc=eu`, etc.) to get USD pricing. Default: `us`. Override with `--currency` flag in release_intel.py.
- **Multi-user watchlist support** — `deal_runner.py sync-steam [steam_id_or_vanity]` accepts any Steam ID or vanity URL. Per-user watchlists stored as `watchlist-{steam_id}.json`. Jordan's default uses `watchlist.json`. Weekly report and release intel auto-detect all watchlist files via glob.
- **Feature flags for multi-user** — Each watchlist has a `features` dict: `{"patch_notes": true, "deal_tracker": true}`. Toggle via `deal_runner.py toggle <steam_id> <feature> <on|off>`. Both default ON for new users. Scripts check flags and skip disabled users.
- **Steam vanity URL resolution** — Use `ISteamUser/ResolveVanityURL/v0001/?vanityurl={name}` to convert custom URLs to numeric IDs. Returns `{"response": {"success": 1, "steamid": "..."}}` on success.
- **Steam profile must be public** — Wishlist API (`IWishlistService/GetWishlist/v1/`) requires public profile. If "No items found", profile is private. User must set Game Details to Public in Steam Privacy Settings.
- **CheapShark rate limiting is aggressive** — 429s after ~5-10 rapid requests. `REQUEST_DELAY=5s` between calls + retry with exponential backoff (3 attempts). Cron job should only run 1-2x/day. During testing, repeated runs can ban your IP for hours.
- **Title similarity filtering** — When using `deals?title=X`, filter results by checking if >50% of search title words appear in the deal title. Without this, "elden ring" matches "ELDEN RING NIGHTREIGN" DLC which is a different product.
- **Steam wishlist API** — Use `IWishlistService/GetWishlist/v1/?steamid={id}` (returns appids), then resolve names via `appdetails?appids={id}`. Rate limit: 1 request/sec for appdetails. Profile must be public.
- **Steam vanity URL resolution** — Custom URLs (e.g., `steamcommunity.com/id/ProtoJay4789`) need resolution to numeric ID. Scrape the profile page for `steamID64` or use `ISteamUser/ResolveVanityURL` (may require API key).
- **CheapShark fuzzy search** — `title` parameter is fuzzy. "mario" returns "Elmarion: Dragon Time". Use `exact=1` on `/games` endpoint for precise matches.
- **Free games = $0 salePrice** — Stardew Valley is free on Epic. Don't assert `sale_price > 0`; use `>= 0` and handle $0 as "free".
- **gameID deals endpoint is HTTP 500** — Use `deals?gameID=X`, NOT `games/{id}/deals` (returns HTTP 500). Though we no longer use gameID for price lookups.
- **WishlistMonitor schema: `games` vs `items` key mismatch** — `cmd_sync_steam()` writes `{"games": [...]}` but `WishlistMonitor._load()` historically only read `{"items": [...]}`. FIXED: `_load()` now checks both keys (`data.get("items", data.get("games", []))`). If adding a new sync source, write under `"items"` key to match the canonical format, or update `_load()`.
- **WishlistItem.from_dict() chokes on extra fields** — `cls(**data)` raises TypeError on unknown keys (e.g. `steam_appid` from Steam sync). FIXED: `from_dict()` now filters to known dataclass fields via `dataclasses.fields(cls)`. Any new WishlistItem fields must be added to the dataclass, not passed through as extras.
- **Batch operations must enable cache** — `CheapSharkClient(cache_enabled=False)` makes 63+ redundant API calls. Always use `cache_enabled=True` for batch check/search operations.
**CLI `check` is not a recognized subcommand** — `deal_runner.py` arg parser has no `elif args[0] == "check"` branch. Running `python3 deal_runner.py check` prints usage help and exits. To run a price check, call with NO arguments: `python3 deal_runner.py` (no args → `cmd_check()`). The docstring lists `check` as a command but it's not wired up.
**Raw `cmd_check()` output is not tiered** — The CLI output shows flat price listings without discount classification. Use `weekly_report.py` instead for proper tiered formatting (🔥 Deep Cuts, 💰 Solid Sales, 🏷️ Light Marks, 📉 Barely, 🚨 Unreleased).
**`weekly_report.py` timeouts** — The weekly report script can timeout (120s+) likely due to API rate limits when checking 60+ games. When this happens, use the manual tiered report pattern: load watchlist.json directly, iterate items, call `client.search_deals(title)`, filter by title similarity, pick best price per game, then bucket by discount depth (50%+, 25-49%, 10-24%, <10%). See `references/discount-tier-fallback.md` for a copy-paste pattern.
- **CheapShark 429s block terminal-based clients for minutes** — After ~5-10 rapid requests the IP gets 429'd for 60-120+ seconds. The `web_extract` tool bypasses this (different egress path). For cron jobs: use `web_extract` for individual deal lookups when the terminal-based client is rate-limited. See `references/cheapshark-rate-limit-fallback.md`.
- **`storeName` is NOT in the deals response** — The `/deals` endpoint returns `storeID` (numeric string), not `storeName`. Resolve via `/stores` endpoint. The `CheapSharkClient._resolve_store_name()` method handles this automatically with caching.
- **ITAD API key never stored** — Ideas.md says "ITAD API key verified" but no key exists in `.env` or anywhere in the vault. Don't reference it until actually saved.
- **Telegram bot token** — hermes config.yaml references `${TELEGRAM_BOT_TOKEN}` (env var), but it's usually set in `/root/.hermes/profiles/gentech/.env`, not exported. Read from `.env` file directly when sending messages programmatically. Pattern: `grep TELEGRAM_BOT_TOKEN ~/.hermes/profiles/gentech/.env`
- API key must not be exposed in logs or Telegram messages
- Rate limit: 1000 requests / 5 min — implement caching
- Affiliate tags in URLs must not be removed (ITAD ToS)
- Must not compete with ITAD — we add value via Telegram alerts + auto-buy
- Some stores have subscription-only prices — flag these separately
