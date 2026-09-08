# Installed Games Auto-Discovery

## Pattern Overview

Instead of manually maintaining an "installed games" list, auto-discover from Steam API play history in two phases:

### Phase 1: Auto-Discover (First Run)
- Pull `last_played` timestamps from Steam Owned Games API
- Filter to games played in last 14 days
- Generate draft JSON file
- Show results to user

### Phase 2: User Curates
- User removes uninstalled games
- User adds installed-but-not-played games
- User saves final JSON file

### Phase 3: Ongoing News Scanning
- Use curated list for daily news scans
- User updates JSON file anytime

## JSON Structure

```json
{
  "owner": "Jordan",
  "lastUpdated": "2026-07-04",
  "autoDiscovered": true,
  "games": [
    {
      "name": "Path of Exile 2",
      "appid": 123456,
      "source": "steam-api",
      "added": "2026-07-04",
      "lastPlayed": "2026-07-03",
      "playtimeHours": 45.2
    }
  ]
}
```

## Steam API Call

```python
import requests
from datetime import datetime, timedelta

url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
params = {
    'key': STEAM_API_KEY,
    'steamid': STEAM_ID,
    'include_appinfo': True,
    'include_played_free_games': True,
    'format': 'json'
}

response = requests.get(url, params=params)
games = response.json()['response']['games']

# Filter to last 14 days
fourteen_days_ago = int((datetime.now() - timedelta(days=14)).timestamp())
recently_played = [
    game for game in games
    if game.get('last_played', 0) > fourteen_days_ago
]
```

## Timestamp Conversion

Steam `last_played` is Unix timestamp (seconds since epoch). Convert to readable date:

```python
from datetime import datetime
last_played_date = datetime.fromtimestamp(last_played).strftime("%b %d, %Y")
```

## Cron Job Prompt Template

```python
"""
Check for new game news for TWO categories:
1. Wishlist games — Games Jordan wants to buy
2. Recently played games (last 60 days) — Games Jordan is actively playing

Load wishlist from: /root/ProtoJay4789.github.io/Gaming/gentech-shop.json
Load recently played from: /root/ProtoJay4789.github.io/Gaming/installed-games.json

Search for news (patch notes, general news, major announcements) via web_search
with game title + "news", "update", "patch", "announcement" keywords.

Deliver split report with two sections:

📋 WISHLIST WATCH
• [list top 10 wishlist games]
Watchlist: X total games
[News items]

🕹️ RECENTLY PLAYED (Last 60 Days)
• Game Name — Last played: Jul 3, 2026
[News items]
"""
```

## File-Based Control

User edits `installed-games.json` directly to add/remove games. No conversation needed. Changes are picked up on next cron run.

## Credential Requirements

Need two environment variables:
- `STEAM_API_KEY` — Get from https://steamcommunity.com/dev/apikey
- `STEAM_ID` — User's Steam profile ID (64-bit)

Store in `/root/.hermes/profiles/gentech/.env`:
```
STEAM_API_KEY=your_api_key_here
STEAM_ID=your_steam_id_here
```

## Report Format

```
🎮 GenTech Game News — Your personal game release intelligence

---

📋 WISHLIST WATCH
• SUPERHOT VR
• No Rest for the Wicked
• ...

Watchlist: 65 total games

[News for wishlist games]

---

🕹️ RECENTLY PLAYED (Last 60 Days)
• Path of Exile 2 — Last played: Jul 3, 2026
• No Rest for the Wicked — Last played: Jul 2, 2026
• Horizon Heat — Last played: Jun 15, 2026

[News for recently played games]

---

✅ No other updates since last check
```

## Pitfalls

- **Missing Steam credentials** — If `STEAM_API_KEY` or `STEAM_ID` not in `.env`, cannot pull owned games. Fallback to manual list.
- **Steam profile privacy** — Owned Games API requires public profile. If empty results, profile may be private.
- **Last 14 days vs 60 days** — Discovery uses 14 days for initial draft, but ongoing scans use 60 days. Two different windows.
- **First run noise** — First cron run shows ALL games in 14-day window. Subsequent runs only show NEW news.
- **User doesn't update JSON** — If user never curates the draft file, continue using auto-discovered list. Prompt occasionally to review.