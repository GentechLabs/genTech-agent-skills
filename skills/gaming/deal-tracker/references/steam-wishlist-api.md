# Steam Wishlist API

## Endpoints Used

### 1. IWishlistService (primary — used by sync-steam)
```
GET https://api.steampowered.com/IWishlistService/GetWishlist/v1/?steamid={steam_id64}
```
Returns: `{"response": {"items": [{"appid": 1234, "priority": 0, "added": ...}]}}`

**This is the endpoint `cmd_sync_steam()` uses.** Returns app IDs only — no game names. Must resolve names separately via appdetails.

### 2. Store Wishlist Data (legacy, paginated)
```
GET https://store.steampowered.com/wishlist/profiles/{steam_id64}/wishlistdata/?p=0
```
Returns: dict keyed by appid, includes `game_name`, prices, reviews.
Pagination via `?p={page}`. More data per game but slower.

## Response Shape (IWishlistService)
```json
{
  "response": {
    "items": [
      {"appid": 1234, "priority": 0, "added": 1234567890}
    ]
  }
}
```

## Name Resolution
After fetching app IDs from IWishlistService, resolve names via:
```
GET https://store.steampowered.com/api/appdetails?appids={appid}
```
Rate limit: ~200 req/5min. Batch with 1s sleep every 10 calls.

## Notes
- Public wishlists only — private wishlists return empty
- Steam profile URL: `https://steamcommunity.com/id/{username}` → get steam_id64
- Our Steam ID: `76561198068413360` (ProtoJay4789)
- `appid` is Steam's app ID — use to look up ITAD game ID via `/lookup/id/shop/1/`

## Schema Mismatch Pitfall
`cmd_sync_steam()` writes games under `"games"` key in watchlist.json.
`WishlistMonitor._load()` reads from `"items"` key (canonical) with fallback to `"games"`.
**Always write new sync sources under the `"items"` key** to match the canonical format.
