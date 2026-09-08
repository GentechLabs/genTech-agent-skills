# IsThereAnyDeal API Reference

## Base URL
`https://api.isthereanydeal.com`

## Auth
API key as query param `?key=...` or header `ITAD-API-Key: ...`
Rate limit: 1000 requests / 5 min (verified email)

## Key Endpoints

### Free (no auth)
- `GET /service/shops/v1` — List all active stores (35+)
- `GET /service/shops/map/v1` — Store ID → name mapping

### Game Lookup
- `GET /games/search/v1?title={query}` — Search by title, returns ITAD game IDs
- `GET /games/lookup/v1?id={itad_id}` — Get game details by ITAD ID

### Pricing
- `POST /games/prices/v3` — Body: array of ITAD game IDs. Returns current prices across all stores, historical lows, deal cuts
- `POST /games/overview/v2` — Body: array of ITAD game IDs + country/currency. Full price overview
- `POST /games/historylow/v1` — Body: array of ITAD game IDs. Historical low prices
- `POST /games/storelow/v2` — Body: array of ITAD game IDs. Store-specific lowest prices

### History
- `GET /games/history/v2?id={itad_id}` — Price history chart data

### Deals
- `POST /deals/v2` — Current deals across all stores (OAuth required)

### Waitlist / Collection (OAuth)
- `GET /waitlist/games/v1` — User's waitlist
- `PUT /waitlist/games/v1` — Add to waitlist
- `GET /collection/games/v1` — User's collection

### Webhooks
- `PUT /webhooks/v1` — Register webhook for deal alerts

## Response Format (prices/v3)
```json
{
  "id": "game-uuid",
  "historyLow": {
    "all": { "amount": 29.95, "currency": "USD" },
    "y1": { "amount": 29.95 },
    "m3": { "amount": 34.27 }
  },
  "deals": [{
    "shop": { "id": 6, "name": "Fanatical" },
    "price": { "amount": 53.88, "currency": "USD" },
    "regular": { "amount": 59.99 },
    "cut": 10,
    "storeLow": { "amount": 31.79 },
    "drm": [{ "id": 61, "name": "Steam" }],
    "url": "https://itad.link/..."
  }]
}
```

## ToS Summary
- ✅ Commercial use if app is public
- ✅ Can enrich with own data
- ✅ Can use subset of data
- ❌ Must not compete with ITAD
- ❌ Must not remove affiliate tags from URLs

## Shop IDs (verified)
| ID | Name |
|----|------|
| 6 | Fanatical |
| 7 | Humble Store |
| 11 | Steam |
| 13 | GreenManGaming |
| 20 | GameBillet |
| 25 | GamesPlanet US |
