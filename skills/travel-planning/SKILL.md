---
name: travel-planning
description: "Trip planning workflow: flight price research, hotel platform comparison, budget analysis, cultural intelligence, and destination guides. Covers Southeast Asia focus (Philippines, Thailand, Bali, Vietnam) with Agoda/Booking.com/Airbnb comparison."
tags: [travel, flights, hotels, budget, southeast-asia, cultural-intelligence]
trigger: "When the user mentions trip planning, vacation, flights, hotels, travel budget, destination research, cultural rules for a country, theme park tickets, amusement park deals, or entertainment venue pricing."
related_skills: [agent-coordination, market-macro-monitor]
version: 1.1.0
author: Gentech
---

# Travel Planning Workflow

## When to Use
- User asks about visiting a country/city
- User wants to compare flight prices or routing options
- User mentions a trip, vacation, or travel dates
- User asks "can I afford this trip?"
- Creating or updating trip docs in the vault

## Prerequisites
- LetsFG SDK installed (`/root/LetsFG`)
- Web search for fallback price data
- Vault location: `00-HQ/01-Travel/[Country]/`

## Workflow

### 1. Trip Affordability Engine

Before researching destinations, check if the user can afford the trip.

**Required inputs:**
- Pay rate ($/hr)
- Average weekly hours
- OT pattern (hours/week at 1.5x)
- Monthly bills
- Savings window (weeks until trip)
- Trip cost range (flights + accommodation + spending)

**Calculation:**
```
Weekly gross = (regular hrs × rate) + (OT hrs × rate × 1.5)
Net weekly = weekly gross × 0.78 (after ~22% tax)
Total available = net weekly × weeks until trip
Trip cost = flights + accommodation + spending
Buffer = total available - trip cost
```

**Verdict scale:**
- 🟢 **Solid** — Buffer > 30% of trip cost
- 🟡 **Doable, but tight** — Buffer 10-30%
- 🔴 **Not this time** — Buffer < 10% or negative

**Also provide:**
- Week-by-week savings tracker
- Price sensitivity ("if flights go up $200, you're still OK")
- Recommended buy date for tickets

### 2. Flight Research

**Primary: LetsFG (try first)**
```python
from letsfg.local import search_local
result = await search_local('CVG', 'MNL', '2026-07-25', mode='fast', max_browsers=4)
```
- If offers returned → sort by price, present top 5-10
- If zero offers or errors → fall back to web search

**Fallback: Web Search**
Search Google Flights, Skyscanner, Expedia, Kayak via `web_search`.
Compile results into a comparison table.

**Price benchmarks (save to trip doc):**
| Route | Great Deal | Good Price | Fair | Overpaying |
|-------|-----------|------------|------|------------| 
| CVG → MNL RT | Under $900 | $900-1,100 | $1,100-1,400 | Over $1,400 |

**Critical: Browser tools timeout on flight SPAs.** Google Flights, Kayak, and Skyscanner are JavaScript-heavy single-page apps that consistently timeout in headless environments. Do NOT waste time retrying browser_navigate to these sites. Instead:

1. **Primary method: web_search snippets** — Aggregator search results embed actual prices in their snippets (e.g., "Cheap Flights from Cincinnati to Manila...$916 for round trip"). Run parallel searches across 4-5 aggregators and extract prices directly from snippets. This is faster and more reliable than visiting the sites.

2. **Secondary method: terminal curl + grep** — For deeper data (airline names, route details), `curl` the Kayak route page and `grep -oP '\$[\d,]+'` to extract all dollar amounts from the HTML. Works because Kayak renders some price data server-side.

3. **Route intelligence: flightconnections.com** — Not a booking site, but excellent for understanding route structure: which airlines serve the route, typical stops, flight duration, alliances. Search snippets from this domain contain rich metadata.

### 3. Hotel Platform Comparison

**Key platforms for Southeast Asia:**

| Platform | Best For | Why Cheaper in SE Asia |
|----------|----------|----------------------|
| **Agoda** | SE Asia specifically | HQ in Bangkok, lower commission, Agoda Homes |
| **Booking.com** | Global, flexible cancellation | Larger inventory, Genius rewards |
| **Airbnb** | Unique stays, monthly trips | 20-30% monthly discount |
| **HotelsCombined** | Price comparison | Searches multiple platforms |
| **Travala** | Crypto payments, x402 agent bookings | 2.2M+ hotels, USDC on Base, ~$0.01/tx |

**Travala MCP Integration (NEW — x402 agent bookings):**
- MCP Server: `https://travel-mcp.travala.com/mcp`
- No API key needed — public search endpoints
- Agent can search, compare, and book hotels autonomously
- Payment via x402 (USDC on Base, gasless)
- Register at 8004scan.io/agents for cbBTC rewards
- See vault: `Strategies/travala-mcp-integration-spec.md`
| **Travala** | Crypto-native, x402 agent bookings | 2.2M+ hotels, USDC on Base, ~$0.01/tx |

**Travala MCP Integration (Live June 2026):**
- MCP server: `https://travel-mcp.travala.com/mcp`
- No API key needed for search endpoints
- Tools: `travala_search_hotel`, `travala_search_package`, `travala_book`, `travala_book_status`, `travala_manage_bookings`, `travala_cancel_booking`
- Payment via x402 (USDC on Base, gasless)
- Agent registration at 8004scan.io/agents → earn cbBTC on bookings
- Coinbase payments MCP (`@coinbase/payments-mcp`) required for payment completion
- See vault: `Strategies/travala-mcp-integration-spec.md` for full spec

**Price differences explained:**
- Agoda: 15-20% commission, no guest service fee
- Booking.com: 15-25% commission, included in price
- Airbnb: 14-16% guest service fee + cleaning fee added at checkout
- **Example (10 nights Makati):** Agoda $450 vs Airbnb $558 vs Booking.com $520

**Recommendation logic:**
- Short stay (1-3 nights) → Agoda or Booking.com (no fees)
- Week+ vacation → Agoda (best SE Asia prices)
- Monthly stay → Airbnb (20-30% discount beats Agoda)
- Groups → Airbnb (multiple bedrooms)
- Budget backpacker → Hostelworld

**Airbnb rules change frequently:** Always check local regulations. Many Makati condos prohibit short-term rentals (<30 days). BGC is stricter.

### 4. Destination Guides

**Build for each destination:**
- Neighborhood breakdown (where to stay, where to avoid)
- Transport guide (ride-sharing, public transit, airport transfers)
- Daily budget worksheet
- Cultural rules and laws
- Safety tips and common scams
- Food recommendations
- Weather and packing list

### 5. Shopping Lists & "Pack Light, Shop Local" Philosophy

**Trigger:** Jordan asks about packing, shopping for a trip, or "what should I bring?"

**Core Insight:** Many destinations (especially Southeast Asia) have cheap, high-quality local shopping at night markets, street vendors, and local stores. Pack light on basics, buy当地 (locally) for clothes, toiletries, and beach gear.

**Shopping List Pattern (per trip):**
1. Create separate lists per traveler (e.g., `trip-1-shopping-lists.md`)
2. Split each list into:
   - **Pack from US** — Electronics, documents, prescriptions, items cheaper/better in US
   - **Buy locally** — Clothes, beach gear, toiletries, souvenirs
3. Include budget estimates per item
4. Include where to buy locally (specific markets, stores, neighborhoods)

**What to Pack from US (typically):**
- Passport, documents, flight confirmations
- Electronics (phone, charger, power bank, headphones)
- Prescription meds (30-day supply + copy)
- Sunscreen SPF 50 (expensive in SE Asia)
- Rain jacket (if wet season)
- Items she can't easily find locally

**What to Buy Locally (typically):**
- T-shirts (night markets: $3-5 each)
- Beach gear (rash guards, towels, snorkel gear: $5-9)
- Toiletries (7-Eleven, Watsons: $1-4)
- Sarongs/cover-ups ($4-7)
- Souvenirs/pasalubong ($2-9)
- Hair accessories ($1-2)

**Night Market Intelligence:**
For each destination, document:
- Best night markets (name, day, vibe)
- What they're known for
- Bargaining expectations
- What to avoid

**Philippines Example:**
- Salcedo Saturday Market — artisanal food, crafts
- Legazpi Sunday Market — similar vibe
- Poblacion night market — street food, clothes
- Divisoria — bargain capital (take Grab)

**The Product Angle:**
This could be a travel companion product — most travel apps focus on booking. This focuses on the EXPERIENCE: what to wear, what to buy, where to shop, how to blend in. "Pack light, shop当地" is the philosophy.

### 6. Cultural Intelligence Layer

**For each country, document:**
- Laws (visa, drinking age, drugs, dress codes, photography)
- Cultural norms (greetings, sacred body parts, tipping)
- Safety (common scams, transport, areas to avoid)
- Food/water (tap water safety, must-try dishes)

**Key countries covered:**
- Philippines — `references/philippines-rules.md`
- Thailand — `references/thailand-rules.md`
- Bali — `references/bali-rules.md`
- Vietnam — `references/vietnam-rules.md`

### 6b. Visa & Crackdown Research (Active Monitoring)

**Trigger:** When planning a trip to a country with changing rules (Thailand, Philippines, etc.), proactively research current visa rules and enforcement trends.

**Research workflow:**
1. Search for "[country] tourist visa rules 2026" + "[country] crackdown tourists"
2. Check official embassy sites (thaiembassy.com, immigration.gov.ph)
3. Check news sites (aseannow.com, straitstimes.com, bangkokpost.com)
4. Compare current rules vs. what's documented in vault

**What to document:**
- Visa-free stay duration (and any recent changes)
- Proof of funds requirements (amount, enforcement level)
- Health insurance requirements (mandatory or recommended)
- Overstay penalties (fine amount, jail time, re-entry bans)
- Behavioral enforcement (zero tolerance, cultural rules)
- Entry via land vs. air (different limits)

**Dashboard integration:**
- Add `travelRules` section to trip JSON file
- Include both current and neighboring country rules (for multi-country trips)
- Update checklist with visa-specific items (eTravel, proof of funds, insurance)

**Thailand 2026 example (proven June 2026):**
- 60→30 day visa reduction (May 19, 2026 Cabinet approval)
- 20,000 Baht cash proof of funds (randomly enforced at immigration)
- Zero tolerance enforcement (Phuket driving, cultural respect)
- Mandatory health insurance under review
- Reference: `Travel/Thailand-2026.md` in vault

### 6. Cron Job Price Monitoring (Automated)

When running as a scheduled cron job to track flight prices:

**Search pattern** — run these in parallel:
```
web_search("CVG MNL flights [month] [year] round trip cheapest")
web_search("Google Flights Cincinnati Manila [date range]")
web_search("Expedia flights CVG to Manila [year]")
web_search("cheapest flights Cincinnati to Manila summer [year]")
```

**Data extraction hierarchy:**
1. Prices embedded in search snippets (fastest, most reliable)
2. Terminal curl + regex on Kayak route pages (for airline details)
3. Browser tools (almost always timeout — skip unless needed for booking)

**Report structure** (for cron delivery):
1. Current cheapest price found
2. Price change from previous check (if baseline exists)
3. Assessment: Steal / Good / Average / Overpaying
4. Recommendation: Buy now / Wait / Set alert
5. Airlines found: top 3 with prices

**Alert logic:**
- Only deliver report if: meaningful price change (>$50), price hits target range, or new low detected
- Otherwise, log silently — don't spam with "no change" reports
- Track previous prices in vault: `00-HQ/01-Travel/[route]/price-history.md`

**See:** `references/flight-monitoring.md` for full methodology.

### 7. Vault Organization

**Dashboard data goes to:** `09-Green Room/travel/{traveler}/`
- `{trip-name}.json` — structured trip data (drives the travel dashboard)
- Dashboard loads from JSON, renders visually, updates on refresh

**Trip docs go to:** `00-HQ/01-Travel/[Country]/`
- `README.md` — Trip overview, status, links
- `YYYY-Trip-Name.md` — Detailed trip doc (itinerary, budget, flights, hotels)
- `flights.md` — Flight research and price tracking
- `rules.md` — Cultural rules and laws

**Research/reference goes to:** `09-Green Room/`
- `southeast-asia-booking-platforms.md` — Platform comparison
- `travel-rules-framework.md` — Cultural intelligence
- `philippines-trip-planner.md` — Trip-specific planning
- `travel-affordability-engine.md` — Budget analysis spec

### 8. Travel Dashboard (Visual Output Layer)

The travel dashboard is the visual output of trip planning data. Same pattern as the gaming dashboard — JSON data + HTML renderer.

**Dashboard URL:** `https://protojay4789.github.io/Travels/travel-dashboard.html`
**Data source:** `Travels/travel-jordan.json` (same directory as HTML)
**Vault copy:** `09-Green Room/travel/{traveler}/{trip-name}.json`

**What it shows:**
- Trip selector tabs (multiple trips in one dashboard)
- Trip overview (legs, dates, destinations)
- Budget tracker with category breakdown
- Flight cards with booking status
- Restaurants (must try + nearby)
- Places to go (parks, malls, neighborhoods)
- Day-by-day timeline (color-coded: travel/explore/work/relax/home)
- Interactive checklist + packing list (localStorage persisted)
- Travel tips

**Multi-trip support (Jun 2026):**
- JSON structure: `trips: [...]` array with `activeTrip` field
- Trip selector tabs at top — click to switch between trips
- Each trip has its own theme colors
- Shows flight companion (e.g., "Flying with: Vanito") and special dates (e.g., "Christel's Birthday")
- Status badges: Planning (blue), Dreaming (pink), Active (green)

**Theme system:** Each trip can have its own color palette via `theme.colors` in JSON. Philippine Sunset = warm cream, gold, orange, blue. Thai Islands = ocean blue, green, gold. Songkran Splash = blue, yellow, orange. See `gentech-hub` skill references for palette templates.

**Workflow:**
1. Plan trip → generate JSON data
2. Agent updates JSON from conversation
3. Dashboard renders visually
4. User checks off items, agent tracks progress
5. Dashboard re-renders on refresh

**See:** `gentech-hub` skill for full template documentation and JSON schema.

## Agent Hotel Booking (Travala MCP)

Travala's MCP server enables AI agents to search and book 2.2M+ hotels autonomously via x402 payments on Base.

**MCP Server:** `https://travel-mcp.travala.com/mcp`
**No API key needed** for search endpoints.

### Tools
- `travala_search_hotel` — location, dates, price range, filters
- `travala_search_package` — room types, rates, meal plans
- `travala_book` — book + x402 payment (USDC, ~$0.01/tx)
- `travala_book_status` — recovery for failed bookings
- `travala_manage_bookings` — lookup existing bookings
- `travala_cancel_booking` — cancel with refund

### Agent Registration
Register at 8004scan.io/agents for ERC-8004 agentId. Set `rewardWallet` in skill file. Earn cbBTC on completed bookings.

### Integration with GenTech Travels
Travala MCP = data + booking engine. Our x402/Q402 = payment layer. Privacy wrapper = our moat. Telegram/Discord/X = distribution.

**Full spec:** `Strategies/travala-mcp-integration-spec.md` in vault.

## MCP-First Approach (When Bot Detection Blocks You)

Agoda, Airbnb, Booking.com, and most booking sites use heavy JavaScript + aggressive bot detection. When they block or paywall you (date picker loops, cookie walls, 403s), **stop and check available MCP servers first** instead of fighting the browser.

### Available MCP Routes

| Service | Cost | What It Does | Status |
|---------|------|-------------|--------|
| **Tripadvisor** (Pay catalog - `paysponge/tripadvisor`) | $0.01/call | Hotel/restaurant/attraction search, details, reviews, photos | Needs Pay account setup + USDC |
| **Google Places** (Pay catalog - `solana-foundation/google/places`) | $0.001/call | Text & nearby search for places, hotels, businesses | Needs Pay account setup + USDC |
| **Travala MCP** | Free search, x402/book | 2.2M+ hotels, search/book autonomously, USDC on Base | Live, no API key for search |

### Workflow

1. **Bot detected?** → Don't retry the browser more than once
2. **Check Pay catalog:** `mcp__pay__search_catalog(query="hotel search tripadvisor travel")`
3. **If Pay is unfunded:** Fall back to `web_search` snippets (aggregators embed prices in text)
4. **If you find a match:** `mcp__pay__get_catalog_entry(fqn="...")` for endpoint details, then `mcp__pay__curl` to call

## Pitfalls

1. **LetsFG connectors fail on headless VPS** — Fall back to web search immediately, don't debug Playwright paths mid-conversation
2. **Browser tools timeout on flight SPAs** — Google Flights, Kayak, Skyscanner are JS-heavy SPAs that consistently timeout in headless environments. Use web_search snippets + terminal curl instead. Do NOT retry browser_navigate more than once.
3. **Airbnb total cost is misleading** — Always calculate with service fee (14-16%) + cleaning fee
4. **Agoda prices change by currency** — Always check in USD and local currency
5. **Airbnb rules change frequently** — Check local regulations before recommending
6. **Flight prices are volatile** — Set alerts, don't commit to a price without checking multiple sources
7. **Don't assume accommodation type** — Ask: solo? couple? group? budget? luxury?
8. **web_extract doesn't work for flight sites** — Uses DuckDuckGo backend which blocks URL extraction for most booking sites. Use terminal curl instead.
9. **Clarify full routing before quoting prices** — When the user says "fly from X to Y", confirm the complete itinerary (origin → destination → any intermediate legs) before researching. The user may mean CVG→CEB (direct international) not MNL→CEB (domestic). A wrong assumption wastes the whole research pass.
10. **Philippines island geography trips up first-timers** — Cities like Lapu-Lapu are on separate islands (Mactan) connected by bridges, not remote. Cebu City is on Cebu Island proper. Clarify this early — users often think "city" = "mainland" and get confused about ferry vs bridge access.
11. **Book DIRECT with majors, not OTAs (Jordan's standing preference, Aug 2026)** — Jordan wants to book with the major airlines (United, Air Canada, Delta, Alaska) directly for status benefits, miles, and direct support. He explicitly treats OTAs like Expedia as risky: "if something happens you might be shit out of luck." Do NOT lead with Expedia/Orbitz/Travelocity as the booking recommendation. Use OTAs only as a *price-discovery* cross-reference, then recommend booking the same fare direct on the airline's site. When a cheap OTA fare is on a major (e.g. Alaska), say so and point to booking it direct. Note: airline deep-link search URLs (united.com/flights-search?..., delta.com/flights-search/results?...) often 404 or redirect, and their search widgets fight automation — use web_search snippets for airline fares and give the user the direct booking link rather than fighting the widget.

## References

- `references/philippines-rules.md` — Philippines cultural intelligence
- `references/switzerland-schengen-visa.md` — Switzerland/Schengen visa from the Philippines (documents, fees, process, links)
- `references/cebu-lapu-lapu-guide.md` — Cebu & Lapu-Lapu City first-timer guide: geography, flights, hotels, tips
- `references/cvg-ceb-route.md` — CVG→CEB route reality: no nonstop, October cheapest, Alaska ~$480 sweet spot, direct-with-major tradeoffs
- `references/thailand-rules.md` — Thailand cultural intelligence
- `references/booking-platforms.md` — Agoda vs Booking.com vs Airbnb comparison
- `references/cost-of-living-in-worker.md` — Embed city cost-of-living data in Cloudflare Workers (zero-API-cost alternative to Numbeo's $260/mo plan)
- `references/flight-monitoring.md` — Cron job flight price monitoring methodology, report template, alert logic
- `references/travala-mcp-integration.md` — Travala Travel MCP: 6 API tools, x402 payments, agent registration, GenTech Travels integration plan
- `references/travala-mcp.md` — Travala Travel MCP integration: tools, setup, x402 payments, agent rewards
- `references/theme-park-tickets.md` — Theme park & entertainment ticket research: Groupon/reseller comparison, deal structures, Universal Orlando specifics, blockout date handling
