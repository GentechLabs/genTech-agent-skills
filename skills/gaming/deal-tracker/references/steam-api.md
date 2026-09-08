# Steam API Reference

## Wishlist
```
GET https://api.steampowered.com/IWishlistService/GetWishlist/v1/?steamid={steam_id}
Response: { "response": { "items": [{ "appid": 12345, "priority": 0, "added": 1234567890 }] } }
```

## Resolve Vanity URL
```
GET https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?vanityurl={custom_url}
Response: { "response": { "success": 1, "steamid": "76561198000000000" } }
```
Note: May require API key. Fallback: scrape profile page for `steamID64`.

## App Details
```
GET https://store.steampowered.com/api/appdetails?appids={appid}
Response: { "{appid}": { "success": true, "data": { "name": "Game Name", ... } } }
```
Rate limit: 1 request/sec recommended.

## Jordan's Profile
- URL: https://steamcommunity.com/id/ProtoJay4789/
- Steam ID: 76561198068413360
- Wishlist: 63 games (as of Jun 2026)
