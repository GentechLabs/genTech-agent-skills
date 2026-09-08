# CheapShark API Reference

Free game deals API — no key required. 35 active stores.

## Base URL
`https://www.cheapshark.com/api/1.0`

## Endpoints

### GET /deals
Search current deals.
- `title` — fuzzy search (e.g., "mario" returns "Elmarion: Dragon Time")
- `storeID` — filter by store (1=Steam, 7=GOG, 13=Humble, etc.)
- `upperPrice` — max price filter
- `pageSize` — results per page (default 60)
- `sortBy` — "Deal Rating", "Title", "Savings", "Price", "Metacritic", "Reviews", "Release", "Popularity"
- `metacritic` — minimum Metacritic score
- `steamRating` — minimum Steam rating percent

### GET /games
Search games by title.
- `title` — game name
- `limit` — max results
- `exact` — 1 for exact match, 0 for fuzzy

### GET /stores
List all stores. Returns 35 stores with `storeID`, `storeName`, `isActive`, `images`.

### GET /deals?gameID=X
Get all deals for a specific game. **IMPORTANT:** This is the correct endpoint. Do NOT use `games/{id}/deals` — it returns HTTP 500.

## Gotchas

1. **gameID deals** — Use `deals?gameID=X`, not `games/{id}/deals` (500 error)
2. **Fuzzy search** — `title` is fuzzy. Use `exact=1` on `/games` for precision
3. **Free games** — `salePrice: "0"` is valid (e.g., Epic free games). Don't assert > 0
4. **No price history** — CheapShark has no history endpoint. Track manually via periodic snapshots
5. **Store IDs** — 1=Steam, 2=GamersGate, 3=GreenManGaming, 7=GOG, 11=Humble, 13=Fanatical, 15=DLGamer, 21=WinGameStore, 23=GameBillet, 24=Voidu, 27=Gamesplanet, 28=Gamesload, 29=2Game, 31=IndieGala, 33=Blizzard, 34=Dotemu, 35=DLCompare

## Rate Limiting
No official limit documented. Be polite: 1 request/second recommended. Cache responses with 1-hour TTL.
