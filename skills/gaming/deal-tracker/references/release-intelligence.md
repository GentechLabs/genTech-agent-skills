# Game Release Intelligence — Full News Coverage

## Overview

Stateful tracking of game news, patch notes, release dates, Early Access status, and general game news via Steam APIs. Powers the "GenTech Game News" feature with two feeds: **Wishlist Watch** and **Recently Played**.

## Two-Section Report Structure

### 1. Wishlist Watch
- Games user wants to buy (from Steam wishlist)
- Monitors: patch notes, general news, major announcements (delays, sequels, cancellations, release dates)
- Source: Steam wishlist → CheapShark cross-reference

### 2. Recently Played (Last 60 Days)
- Games user is actively playing
- Auto-discovered via Steam API `last_played` timestamps
- Monitors: same news types as wishlist
- Source: Steam owned games API → filtered by playtime recency

## Data Sources

### Steam News API
- Endpoint: `ISteamNews/GetNewsForApp/v0002/?appid={appid}&count=10&maxlength=500`
- Returns: news items with title, feed, date, gid
- Rate limit: polite (1 req/sec recommended)
- **Coverage:** Patch notes, dev posts, official announcements

### Steam AppDetails API
- Endpoint: `store.steampowered.com/api/appdetails?appids={appid}&cc={currency}`
- Returns: release_date, developers, price_overview, detailed_description
- **Currency parameter:** Use `cc=us` for USD (default), `cc=uk`, `cc=eu`, etc.

### Steam Owned Games API (Recently Played)
- Endpoint: `IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={steam_id}&include_appinfo=true&include_played_free_games=true`
- Returns: All owned games with `playtime_forever` and `last_played` timestamps
- **Filter:** Games with `last_played > (current_time - 60 days)`
- **Conversion:** Unix timestamp → readable date: `datetime.fromtimestamp(last_played).strftime("%b %d, %Y")`

### General News Sources
- web_search queries: game title + "news", "update", "patch", "announcement", "1.0", "sequel", "delay"
- Sources checked: Steam news, official game sites, Reddit, Twitter/X, gaming news outlets

## News Categories

When scanning for news, classify into three types:

| Category | Trigger Keywords | Examples |
|----------|------------------|----------|
| Patch Notes | "patch", "update", "fix", "hotfix", "balance" | Version 1.2.3 patch notes, hotfix 1.2.4 |
| General News | "news", "event", "community", "devlog", "roadmap" | Community event, dev blog, roadmap update |
| Major Announcement | "delay", "sequel", "cancellation", "release date", "1.0", "launch" | Game delayed to Q4, Sequel announced, 1.0 release date |

## Key Features

### 1. Steam AppID Cross-Referencing
**Problem:** CheapShark's `deals?title=X` returns fuzzy matches. "Covenant" matched "Succubers! Dark Covenant".

**Solution:** Use Steam AppID as primary identifier.
- For Steam-synced games, `game_id` IS the Steam AppID
- Search CheapShark by title, filter by `steamAppID` field
- If no AppID match → return None (game unreleased/not on sale)
- Only fall back to title matching if no AppID available

**Implementation in `get_cheapest_price()`:**
```python
effective_appid = steam_appid or (int(game_id) if game_id.isdigit() else None)
if effective_appid and title:
    raw = self._get("deals", {"title": title, ...})
    app_matches = [d for d in raw if str(d.get("steamAppID", "")) == str(effective_appid)]
    if app_matches:
        data = app_matches
    elif effective_appid:
        return None  # Game has no deals with this AppID
```

### 2. Strict Title Matching (Fallback)
When no Steam AppID available:
- **Single-word titles:** Require exact word match in deal title
- **Multi-word titles:** Require 70%+ word overlap AND deal title not drastically longer (2.5x)

### 3. Early Access Detection
Steam API has no native `early_access` flag. Detect from:
```python
desc = details.get("detailed_description", "").lower()
details["_is_early_access"] = "early access" in desc
```

**Early Access rules:**
- Cannot have release dates or pre-orders
- Shows `coming_soon: false` but is still in EA
- Often increases price at 1.0 launch
- Track `is_early_access` in results → show `[Early Access]` tag + price warning

### 4. Price Announcement Detection
Monitor news items for price-related keywords:
```python
price_keywords = ["price", "cost", "$", "increase", "discount", "launch price", "1.0 price"]
is_price_update = any(kw in item_lower for kw in price_keywords)
```

Show `💰 PRICE` tag in reports for price-related news.

### 5. Stateful Tracking
- Per-game state files in `.patch-notes-state/` directory
- Track: seen news IDs, release date, last checked
- Only report NEW items since last run
- First run returns all news; subsequent runs return only new items

## Multi-User Support

### Per-User Watchlists
- Jordan: `watchlist.json` (default)
- Others: `watchlist-{steam_id}.json`
- Auto-detect via glob: `watchlist-*.json`

### Feature Flags
Each watchlist has `features` dict:
```json
{
  "patch_notes": true,
  "deal_tracker": true
}
```
- Both default ON for new users
- Toggle via: `deal_runner.py toggle <steam_id> <feature> <on|off>`
- Scripts check flags and skip disabled users

### Steam Vanity URL Resolution
```python
vanity_url = f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?vanityurl={steam_id}"
# Returns: {"response": {"success": 1, "steamid": "..."}}
```

## CLI Usage

```bash
# Run Patch Notes (all watchlists, max 15 games)
python3 release_intel.py --max 15

# Unreleased games only (faster)
python3 release_intel.py --unreleased-only

# Specific currency
python3 release_intel.py --currency us
```

## Cron Job Integration

**GenTech Patch Notes** (daily 2 PM ET):
1. Sync both wishlists (Jordan + Vanito)
2. Run release_intel.py --max 15
3. Format as Telegram message
4. Deliver to Entertainment group

## Report Format

```
🔔 GAME INTEL — New Updates
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎮 Game Title
   👨‍💻 Developer Name
   📅 RELEASE DATE: Month Day, Year
   ⚡ Date changed from previous!
   📰 News Title [DEV] 💰 PRICE
      Date — Feed
      🔗 URL
   💵 Current EA Price: $39.99
   ⚠️ Price may increase at 1.0 launch

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 UNRELEASED / EARLY ACCESS (N total)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • Game Title — Date [Early Access]
```

## Pitfalls

- **CheapShark rate limiting** — 429s after ~5-10 rapid requests. Use cache.
- **Regional pricing** — Steam API returns prices based on `cc` parameter. Always use `cc=us` for USD.
- **First run noise** — First run of release_intel.py shows all historical news. Subsequent runs only show NEW items.
- **State file growth** — Keep last 50-100 news IDs per game to prevent unbounded growth.
- **Steam profile privacy** — Wishlist API requires public profile. If no items returned, profile is private.
