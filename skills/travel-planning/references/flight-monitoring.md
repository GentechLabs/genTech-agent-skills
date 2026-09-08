# Flight Price Monitoring — Cron Job Methodology

## Overview
Automated flight price tracking via scheduled cron jobs. Designed for Hermes agent cron delivery — report only on meaningful changes, silent log otherwise.

## Search Strategy

### Parallel web_search queries (run all simultaneously):
```
1. "[ORIGIN] [DEST] flights [month] [year] round trip cheapest"
2. "Google Flights [origin city] [dest city] [date range]"
3. "Expedia flights [ORIGIN] to [DEST] [year]"
4. "cheapest flights [origin city] to [dest city] [season] [year]"
5. "[AIRLINE] [ORIGIN] [DEST] flight [month] [year]" (if targeting specific carriers)
```

### Data extraction from snippets:
- Aggregator results embed prices in descriptions: "Flights from X to Y start at $NNN"
- KAYAK route pages mention: "cheapest round-trip price...$NNN"
- Expedia snippets: "Cheap Flights from X to Y...$NNN for round trip"
- Multiple $X,XXX mentions in a snippet = price range for the route

### Terminal curl for airline details:
```bash
curl -s "https://www.kayak.com/flight-routes/[ORIGIN]-[DEST]" \
  -H "User-Agent: Mozilla/5.0 ..." | grep -oP '\$[\d,]+' | head -20
```
Returns dollar amounts from the page. First occurrences are typically the featured/cheapest fares.

### flightconnections.com for route structure:
- No booking, but shows: airlines serving route, typical stops, flight duration, alliances
- Search snippets contain: "The two airlines most popular with KAYAK users are X and Y. With an average price for the route of $Z"

## Price Assessment Scale

| vs. Target Range | Assessment | Action |
|-----------------|------------|--------|
| Below target low | **Steal** | Buy now |
| Within target range | **Good** | Set alert for further drops |
| 10-25% above target | **Average** | Wait, set alert |
| 25%+ above target | **Overpaying** | Wait for off-peak or alternate dates |

## Alert Thresholds
- Meaningful change: >$50 from previous check
- Target hit: price enters the defined "good deal" range
- New low: price drops below any previously recorded price
- Otherwise: log silently, don't deliver

## Price History Tracking
Store in vault: `00-HQ/01-Travel/[ORIGIN]-[DEST]/price-history.md`

Format:
```
## Price History — CVG → MNL

| Date | Cheapest RT | Source | Airlines |
|------|------------|--------|----------|
| 2026-05-28 | $916 | Expedia | Korean Air, ANA, United |
| 2026-05-29 | $895 | Kayak | Korean Air, Cathay Pacific |
```

## Report Template (for cron delivery)
```markdown
## ✈️ [ORIGIN] → [DEST] Flight Price Report
**Route:** [City] ([ORIG]) → [City] ([DEST])
**Dates:** [date range]
**Report Date:** [today]

### 1. 💰 Current Cheapest Prices
[table of sources and prices]

### 2. 📊 Price Change from Yesterday
[delta or "First scan — no baseline"]

### 3. 🎯 Assessment: [Steal/Good/Average/Overpaying]
[1-2 sentence rationale]

### 4. ✅ Recommendation: [Buy now / Wait / Set alert]
[actionable next step]

### 5. 🏆 Top Airline Options
[table with airline, est. price, route type]
```

## Common Routes — Known Price Ranges
*Update as data accumulates*

| Route | Great Deal | Good | Fair | Overpaying |
|-------|-----------|------|------|------------|
| CVG → MNL RT | <$900 | $900-1,100 | $1,100-1,400 | >$1,400 |

## Pitfalls
- **Pin the date range to actual travel dates, not a broad season.** A cron job scanning "July through September" returns noise from dates outside the real window. If Jordan says "late August early September," the prompt should say `Aug 25 – Sep 10` — not "summer 2026." Narrow scope = fewer irrelevant results = cleaner alerts.
- Browser tools (browser_navigate) timeout on Google Flights, Kayak, Skyscanner — these are JS-heavy SPAs
- web_extract fails on most booking sites (DuckDuckGo backend blocks them)
- Flight prices in search snippets may be one-way even when described as "round trip" — cross-reference multiple sources
- Prices shown are often "last 72 hours" snapshots, not real-time availability
- Summer peak (Jun-Aug) prices for SE Asia routes are typically 20-30% higher than shoulder season (Sep-Oct, Apr-May)
