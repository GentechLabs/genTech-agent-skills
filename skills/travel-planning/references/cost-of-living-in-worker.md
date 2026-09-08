# Cost-of-Living Data in Cloudflare Workers

Embed city cost-of-living data directly in a Cloudflare Worker to avoid paying for API subscriptions (Numbeo starts at $260/mo).

## When to Use

- Travel planning needs local price intelligence (meals, transport, accommodation)
- Budget estimates for trip planning destinations
- City-to-city cost comparisons
- As a premium x402 endpoint (agents pay $0.001/query)

## Data Schema (Compact)

```js
const CITIES = [
  { 
    n: "Bangkok, Thailand",           // name
    co: "TH",                         // country code
    cu: "THB",                        // currency
    idx: [36.2, 18.5, 30.1, 22.4, 42.8],  // [CoL, Rent, Groceries, Restaurants, Purchasing Power]
    p: {                              // prices
      meal: 2.50,                     // inexpensive restaurant meal
      beer: 3,                        // domestic beer (0.5L)
      coffee: 2.50,                   // cappuccino
      milk: 1.80,                     // milk (1L)
      bread: 1.50,                    // fresh bread (500g)
      eggs: 2.20,                     // eggs (12)
      chicken: 3.50,                  // chicken fillet (1kg)
      transit: 1,                     // one-way local transport ticket
      monthly_pass: 35,               // monthly transit pass
      taxi_km: 0.50,                  // taxi per km
      utilities: 80,                  // basic utilities monthly
      internet: 22,                   // internet (60 Mbps+)
      fitness: 40,                    // fitness club monthly
      apt1_center: 550,               // 1BR apt in city center
      apt1_out: 350,                  // 1BR apt outside center
      salary: 1500                    // average monthly net salary
    }
  }
]
```

## Key Endpoints

| Route | Parameters | Returns |
|-------|-----------|---------|
| `/cost-of-living?city=Bangkok` | `city` (name or country code) | Full price breakdown + indices + affordability analysis |
| `/cost-of-living?city=Tokyo&compare=Bangkok` | `city` + `compare` | Side-by-side comparison with differentials + verdict |
| `/cost-of-living` | none | Summary list of all cities (names, indices, avg salary) |

## Integration with /plan Endpoint

The `/plan` endpoint auto-looks up cost-of-living data for the destination and adds a `monthly_budget_estimate` with hotel, food, and transport daily costs. This requires no additional API call — just a `.find()` against the embedded dataset.

## City Coverage (15 cities as of Jul 2026)

| Tier | Cities |
|------|--------|
| **Major hubs** | New York, London, Tokyo, Singapore, Dubai, Sydney, Seoul |
| **SE Asia** | Bangkok, Bali, Hanoi, Manila |
| **Budget destinations** | Mexico City, Buenos Aires, Lisbon, Barcelona, Cape Town |

## Pitfalls

- **Indices are relative** — New York = 100.0 for all indices (anchor). Other cities are relative percentages.
- **Currency varies by city** — A single response mixes JPY, THB, USD, EUR. The `currency` field tells the caller which one.
- **Data ages** — Crowdsourced data drifts. Re-check against Numbeo/Expatistan every 3-6 months for critical use cases.
- **Worker size** — 15 cities ≈ 2.5KB JSON, well within Worker limits (1MB total script). 100+ cities would need a separate KV store.
- **Numbeo API alternative** — If real-time data is needed, Numbeo's API is $260/mo (200K queries). The embedded dataset is the zero-cost alternative.
