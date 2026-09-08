# Movie Price Comparison — Data Sources

## Primary: TMDB Watch Providers (Free)

**API:** https://api.themoviedb.org/3/
**Auth:** Free API key (register at themoviedb.org)
**Rate limit:** 40 requests/10 seconds

### Key Endpoints

#### Search movies
```
GET /search/movie?query={title}&api_key={key}
→ Returns: id, title, overview, release_date, poster_path, vote_average
```

#### Watch providers (pricing)
```
GET /movie/{id}/watch_providers?api_key={key}
→ Returns: results.{country}.flatrate (streaming), .rent, .buy, .free
→ Each provider: provider_name, provider_id, logo_path, link, display_priority
```

**Note:** TMDB shows WHERE to watch but not always exact prices. For pricing, the `link` field goes to JustWatch page with actual prices.

### Simulation Mode
For MVP/demo, `movie_client.py` returns realistic mock data:
- 6 popular movies (Oppenheimer, Dune, Interstellar, The Matrix, Dune Part Two, Barbie)
- Realistic streaming/rent/buy providers with prices
- No API key needed for demo

### When to wire real API
1. Register at themoviedb.org → get free API key
2. Set `TMDB_API_KEY` env var
3. MovieClient switches from simulation to live API automatically

## Secondary: JustWatch (Scraping)

JustWatch has the most complete pricing data (100+ platforms) but no free public API.
- Unofficial Python wrappers exist (justwatch, JustWatchAPI)
- Can scrape pricing for digital purchase/rental
- Useful for V2 when we need exact prices across all platforms

## Physical Media: Blu-ray.com

For 4K Blu-ray / Steelbook pricing across Best Buy, Walmart, Target:
- No public API
- Scraping possible but fragile
- V2 feature — physical media collectors are passionate and will pay

## Architecture Decision
Jordan's rule: **Consolidate similar services into one repo.** Games and movies share the same pattern (search → compare → alert), so they live in `deal-tracker-api/` together. Don't create separate repos for each vertical.
