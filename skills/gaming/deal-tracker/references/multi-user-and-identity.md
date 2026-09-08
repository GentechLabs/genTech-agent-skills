# Multi-User Support & Game Identity Verification

## Steam AppID Cross-Referencing

### Problem
CheapShark's title search is fuzzy. Single-word titles like "Covenant" match unrelated games ("Succubers! Dark Covenant"). The `gameID` endpoint is even worse — returns completely unrelated results.

### Solution
Use Steam AppID as primary cross-reference. For Steam-synced games, `game_id` IS the Steam AppID.

### Implementation in `get_cheapest_price()`
```python
def get_cheapest_price(self, game_id: str, title: str = "", steam_appid: Optional[int] = None) -> Optional[Deal]:
    # Determine Steam AppID for cross-reference
    effective_appid = steam_appid or (int(game_id) if game_id.isdigit() else None)

    # Strategy 1: If we have a Steam AppID, search by title and filter by steamAppID
    if effective_appid and title:
        raw = self._get("deals", {"title": title, "upperPrice": 60, "pageSize": 50})
        app_matches = [d for d in raw if str(d.get("steamAppID", "")) == str(effective_appid)]
        if app_matches:
            data = app_matches
        elif effective_appid:
            # We have a Steam AppID but no deals match — game is unreleased or not on sale
            return None

    # Strategy 2: Fall back to strict title matching (only when no Steam AppID)
    if not data and not effective_appid and title:
        # Single-word: require exact word match
        # Multi-word: require 70%+ overlap and deal title isn't drastically longer
```

### Key Rules
1. If `effective_appid` is set and no deals match → return None (don't fall through to title matching)
2. Single-word titles: require exact word match in deal title words
3. Multi-word titles: require 70%+ word overlap AND deal title length < 2.5x search title length

## Multi-User Watchlist Support

### File Structure
- `watchlist.json` — Jordan's default watchlist
- `watchlist-{steam_id}.json` — Per-user watchlists (e.g., `watchlist-76561198068413360.json`)

### CLI Usage
```bash
# Jordan's wishlist (default)
python3 deal_runner.py sync-steam

# Another user by Steam ID
python3 deal_runner.py sync-steam 76561198068413360

# Another user by vanity URL
python3 deal_runner.py sync-steam Vanito
```

### Vanity URL Resolution
```python
vanity_url = f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?vanityurl={steam_id}"
# Returns: {"response": {"success": 1, "steamid": "76561198068413360"}}
```

### Auto-Detection in Reports
```python
def get_all_watchlists() -> list[tuple[str, str]]:
    """Find all watchlist files (default + per-user)."""
    watchlists = []
    watchlist_dir = os.path.dirname(WATCHLIST_FILE)
    if os.path.exists(WATCHLIST_FILE):
        watchlists.append(("Jordan", WATCHLIST_FILE))
    for path in sorted(glob.glob(os.path.join(watchlist_dir, "watchlist-*.json"))):
        steam_id = os.path.basename(path).replace("watchlist-", "").replace(".json", "")
        watchlists.append((f"User {steam_id}", path))
    return watchlists
```

## Steam News API (Release Intelligence)

### Endpoint
```
GET https://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid={appid}&count=10&maxlength=500
```

### Response Structure
```json
{
  "appnews": {
    "newsitems": [
      {
        "gid": "12345",
        "title": "Patch Notes v1.2",
        "feedname": "steam_community_announcements",
        "date": 1744931676,
        "contents": "..."
      }
    ]
  }
}
```

### Relevant Feeds (Developer Updates)
- `steam_community_announcements` — Official dev posts
- `steam_updates` — Patch notes
- `steam_deck` — Deck-specific updates
- `steam_global` — Platform-wide news

### Stateful Tracking
- State stored in `.release-intel-state.json` per appid
- Tracks `seen_ids` (last 100 news GIDs) and `release_date`
- First run returns all news; subsequent runs return only NEW items
- Detects release date changes (TBA → actual date)

## Early Access Detection

### Problem
Steam API doesn't have a native `early_access` flag. Games like "No Rest for the Wicked" show as released (April 2024) but are actually in Early Access with 1.0 launch coming later.

### Solution
Detect Early Access from `detailed_description` containing "early access" text.

### Implementation
```python
def get_app_details(appid: int, currency: str = "") -> dict | None:
    details = app_data.get("data", {})
    # Detect Early Access from description
    desc = details.get("detailed_description", "").lower()
    details["_is_early_access"] = "early access" in desc
    return details
```

### Key Rules
1. Early Access games: `coming_soon: false` but still in EA
2. EA games cannot have release dates or pre-orders on Steam
3. Price often increases at 1.0 launch — show warning in reports
4. Tag with `[Early Access]` in Patch Notes output

## Currency Parameter

### Problem
Steam `appdetails` returns regional pricing based on server location. Server may return CNY instead of USD.

### Solution
Use `cc=us` parameter to force USD pricing.

### Implementation
```python
DEFAULT_CURRENCY = "us"  # USD default

def get_app_details(appid: int, currency: str = "") -> dict | None:
    cc = currency or DEFAULT_CURRENCY
    url = f"{STEAM_APPDETAILS}?appids={appid}&cc={cc}&filters=release_date,price_overview,basic"
```

### CLI Usage
```bash
python3 release_intel.py --currency us     # USD (default)
python3 release_intel.py --currency uk     # GBP
python3 release_intel.py --currency eu     # EUR
python3 release_intel.py --currency jp     # JPY
```

## Feature Flags

### Problem
Multi-user system needs per-user feature control. Some users may want Deal Tracker but not Patch Notes, or vice versa.

### Solution
Each watchlist has a `features` dict. Both default ON for new users.

### Implementation
```json
{
  "steam_id": "76561198068413360",
  "features": {
    "patch_notes": true,
    "deal_tracker": true
  },
  "games": [...]
}
```

### CLI Toggle
```bash
python3 deal_runner.py toggle <steam_id> patch_notes off
python3 deal_runner.py toggle <steam_id> deal_tracker on
```

### Script Behavior
- `weekly_report.py` checks `features.deal_tracker` — skips if false
- `release_intel.py` checks `features.patch_notes` — skips if false
- Both auto-detect all watchlist files via glob
