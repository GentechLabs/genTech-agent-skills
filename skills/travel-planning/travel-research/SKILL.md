---
name: travel-research
description: Systematic travel research — flight routing, multi-country options, budget breakdowns, visa requirements, employment constraints, and timing considerations. Covers solo, couple, and group travel.
category: travel-planning
version: 1.1.0
author: GenTech
tags: [travel, flight-research, budget, multi-country, visa, timing, employment-constraints, peak-season]
---

# Travel Research — Trip Planning

**Purpose:** Systematic research for travel, including flight routing, multi-country options, budget breakdowns, visa requirements, employment constraints, and timing considerations.

---

## When to Use

- **Solo trip planning** (Jordan or other solo travelers)
- **Multi-country routes** (Philippines → Cambodia, Thailand → Laos, etc.)
- **Budget optimization** (base trip vs add-on options)
- **Visa and logistics research**
- **Weather and timing considerations**

---

## Core Philosophy: Traveler-First Constraints

**The first question is who is traveling, not where.** Solo, couple, and group trips optimize differently:
- **Solo:** most flexible, lowest per-person cost, can decide mid-trip
- **Couple/group:** coordination cost, shared lodging economy, companion constraints (PTO alignment, interests, relationship to travelers already in records)
- **Employment-constrained:** a job's peak season, blackout dates, or conversion timeline can override price and weather

**Research priorities, in order:**
1. **Hard constraints:** employment blackouts, visa windows, companion availability
2. **Cost optimization:** day-of-week, seasonality, base trip vs add-ons
3. **Usable time:** travel duration, jet lag, time-zone flip, calendar days vs on-the-ground days
4. **Flexibility:** routes that allow mid-trip changes
5. **Safety and logistics:** visas, transport, weather, health

---

## Trip Research Workflow

### Step 0: Audit Existing Trip Data and Its Data Path

Before changing any trip record, find where the **live source** is and what surfaces are generated from it.

```bash
# 1. Find the source file in the vault
grep -R "<destination>" ${VAULT_DIR}/Travel/ --include="*.json" -l

# 2. Find any generator / cron that rebuilds the public feed
grep -R "travel.*\.json\|build-travel" ${PROFILE_DIR}/cron/ ${PROFILE_DIR}/scripts/ -l

# 3. Check whether repo / webroot copies are stale mirrors
md5sum ${VAULT_DIR}/Travel/travel-*.json \
      /root/repos/gentechlabs.github.io/Travel/travel-*.json \
      /var/www/gentechlabs/Travel/travel-*.json 2>/dev/null
```

**Rule:** edit the source the generator reads, then re-run the generator. Hand-editing a generated file (e.g. `travel-live.json`) is silently erased at the next cron run.

**Rule:** verify the public surface by reading the **served bytes**, not the local file. `curl` the live URL and check the value there.

### Step 1: Define Trip Parameters

**What to ask:**
- Origin (e.g., CVG, SFO, LAX)
- Primary destination (e.g., Manila, Philippines)
- Duration (calendar days, not "trip length" marketing)
- Traveler status (solo vs couple vs group; if couple, name the companion and update records)
- Budget range
- Timing (season, weather preferences)
- **Employment constraints:** PTO blackout dates, peak season, conversion timelines, mandatory overtime

**Example:**
```
Jordan: Solo trip, CVG → Angeles City (8 days) + Cambodia (4 days), Aug/Sep 2026, budget $2,000
```

---

### Step 2: Research Flight Routing and Day-of-Week Fare

**What to research:**
- Direct vs connecting flights
- Open-jaw vs round-trip options
- Airport proximity to destination (e.g. Clark/CRK is 2–3 hours from Manila by road; traffic can stretch it)
- Multi-country routing (if applicable)
- **Day-of-week effect on international fares**

**Sources:**
- LetsFG (preferred, if available)
- Google Flights
- Airline websites
- Travel forums (Reddit r/solotravel, TripAdvisor)

**Day-of-week guidance for international departures (verified 2026 sources):**
- **Thursday** is typically the cheapest international departure day (up to ~15% below Sunday)
- **Tuesday / Wednesday** are close behind
- **Friday** can also be favorable
- **Sunday and Monday** are usually the most expensive
- Savings are smaller than for domestic flights but still meaningful on long-haul tickets

**What to document:**
| Route | Duration | Stops | Cost | Airlines | Notes |
|-------|----------|-------|------|----------|-------|
| CVG → MNL | 19–21h | 1–2 | $1,225–1,314 | United, etc. | Add MNL → CRK road time if going to Angeles City |
| MNL → CRK | 2–3h road | 0 | $20–60 | Bus/van/Grab | Traffic-sensitive |
| MNL → PNH | 3h | 0 | $80–150 | Cebu Pacific, AirAsia | Daily flights |

---

### Step 3: Research Multi-Country Options

**When traveler wants add-ons:**

**Key questions:**
- Can you reach second destination from primary?
- What's the routing? (direct, via hub, train, bus)
- How much does it cost? (flight vs ground transport)
- Visa requirements for second country?

**Example: Angeles City → Cambodia**

| Option | Route | Duration | Cost | Pros | Cons |
|--------|-------|----------|------|------|------|
| **Phnom Penh** | CRK → MNL → PNH | 4h 45min | $240-280 | Cheaper, capital city | Less iconic |
| **Siem Reap** | CRK → MNL → REP | 5h 15min | $260-340 | Angkor Wat | More expensive |

---

### Step 4: Break Down Budget

**Base trip vs add-on structure:**

**Base trip (primary destination):**
| Category | Cost |
|----------|------|
| Flights (round-trip) | $800-1,100 |
| Hotels (8 nights) | $120-200 |
| Food & drinks (8 days) | $80-120 |
| Transport (local) | $40-60 |
| **Base subtotal** | **$1,040-1,480** |

**Add-on (secondary destination):**
| Option | Flights | Hotels | Food | Tours | Total |
|--------|---------|--------|------|-------|-------|
| Phnom Penh (4 days) | $240-280 | $60-120 | $32-48 | $40-60 | $372-508 |
| Siem Reap (4 days) | $260-340 | $80-160 | $40-60 | $60-100 | $440-660 |

**Total options:**
- Base only: $1,040-1,480
- Base + Phnom Penh: $1,412-1,988
- Base + Siem Reap: $1,480-2,140

---

### Step 3: Research Employment and Calendar Constraints

**Employment constraints can override price and weather.** Ask explicitly:
- Are there PTO blackout dates?
- Is there a peak season with mandatory overtime?
- Are there conversion, review, or training windows that must be cleared?
- Does "already approved PTO survives blackout" apply?

**How to treat conflicting sources:** record every claim rather than picking one. If operators say "Nov 15 – Dec 31" and a 2026 alert says "Nov 28 – Dec 24," state both and flag the risk window as the union (earliest start to latest end).

**Key distinction:** "I don't care about holiday pay" ≠ "I can be absent during peak." Pay is a money choice; attendance policy is a job-risk choice. Keep them separate in the recommendation.

### Step 4: Compute Usable Days, Not Calendar Days

Long-haul travel consumes days on both ends. Report usable time honestly.

| Calendar days | CVG ↔ Manila round trip (~50h door-to-door) | Jet lag (~2 days inverted) | Approx usable days |
|---------------|-----------------------------------------------|----------------------------|--------------------|
| 7             | 2 days lost                                   | 2 days slow                | ~3                 |
| 8             | 2 days lost                                   | 2 days slow                | ~4                 |
| 10            | 2 days lost                                   | 2 days slow                | ~6                 |
| 14            | 2 days lost                                   | 2 days slow                | ~10                |

**Rule:** state the usable-days estimate before booking, so the traveler chooses the duration with the right expectation.

### Step 5: Research Visas and Logistics

**Visa research:**
- **Destination:** What's required?
  - Visa on arrival? ($, duration, photos needed)
  - E-visa? (apply online, processing time)
  - No visa? (passport validity only)
- **US citizens:** 30-day visa-free common in SE Asia
- **Other passports:** Check requirements

**Example: Cambodia**
- Visa on arrival: $30 USD
- Duration: 30 days
- Required: Passport photo, USD cash
- Alternative: E-visa (apply online, faster processing)

**Logistics:**
- Airport to city transport (taxi, train, bus)
- Local transportation (Grab, tuk-tuk, transit)
- Safety considerations for the traveler profile
- **Time-zone flip:** note the direction and duration of inversion

---

### Step 6: Research Weather and Timing

**Seasonal factors:**
- **Rainy season:** Philippines/Cambodia (May-Oct) — cheaper, but expect rain
- **Dry season:** Philippines/Cambodia (Nov-Apr) — expensive, better weather
- **Peak season:** December/January — most expensive, crowded

**Weather research:**
| Month | Rainfall | Temp | Typhoon Risk | Crowds | Price |
|-------|----------|------|--------------|--------|-------|
| June | Moderate | 27-32°C | Low-Moderate | Moderate | High |
| July | Heavy | 26-31°C | Moderate | Moderate-High | High |
| August | Heavy | 26-31°C | Moderate-High | Moderate | Medium |
| **September** | Moderate-Heavy | 26-31°C | Moderate | Low | **Low** ⭐ |
| **November** | Low-Moderate | 26-31°C | Low | Moderate | Medium-High |

**Recommendation:** September is cheapest (30-45% less than June/July) but rainy. Travelers can work around rain (indoor activities, museums, malls). November begins the dry season but sits near peak-season pricing and employment blackout windows in US retail/logistics.

---

### Step 7: Create Decision Framework

**Option A: Base only**
- ✅ Lower cost ($1,040-1,480)
- ✅ More time in primary destination
- ✅ Simpler logistics
- ❌ Less variety

**Option B: Base + Cheapest add-on**
- ✅ More variety
- ✅ Still reasonable cost ($1,412-1,988)
- ✅ Capital city experience (Phnom Penh)
- ❌ More travel time

**Option C: Base + Premium add-on**
- ✅ Bucket list item (Angkor Wat)
- ✅ Iconic experience
- ❌ Higher cost ($1,480-2,140)
- ❌ More travel time

**Option D: Shorter window before peak**
- ✅ Avoids employment blackout / MET risk
- ✅ Still visits the destination
- ❌ Less time on the ground

When the trip is employment-constrained, **Option D may be the best Option A**. Lead with the calendar constraint, then optimize price within the safe window.

---

## Trip Documentation

### File Structure

```
${VAULT_DIR}/HQ/01-Travel/
├── Philippines/
│   ├── 2026-Solo-Trip-Angeles-City-Cambodia.md (full plan)
│   └── 2026-Birthday-Trip-Pampanga.md (updated status)
```

### Trip Plan Template

**Header:**
```markdown
---
type: trip
title: "Solo Trip — Destination"
status: planning
dates: "Aug/Sep 2026"
origin: CVG
tags: [travel, solo, philippines, cambodia]
updated: 2026-07-07
---
```

**Sections:**
1. Trip overview (origin, destination, duration, traveler status)
2. Proposed itinerary (day-by-day)
3. Flight research (routing, costs, airlines)
4. Budget breakdown (base + add-ons)
5. Logistics (transport, visa, safety)
6. Weather and timing (seasonal factors)
7. Recommendations (options, trade-offs)
8. Next steps (decisions needed, booking actions)

---

## Theme Park Ticket Research

**When the user asks about theme park tickets** (Universal Orlando, Disney, etc.), follow this workflow:

### Step 1: Identify the Deal

The **Buy 3 Get 2 Free** promo is the standard Universal Orlando deal in 2026:
- Buy a 3-Day Park-to-Park ticket → get 2 days FREE = 5 days total
- Covers: Epic Universe, Universal Studios Florida, Islands of Adventure
- Park-to-park = hop between all parks same day
- Valid through December 16, 2026
- Blockout dates: July 1-6, Oct 9-12, Nov 18-28

### Step 2: Check Discount Resellers

**Undercover Tourist** (undercovertourist.com) is the best discount reseller:
- Usually $20-30 cheaper per ticket than gate price
- E-ticket delivery, go straight to gate
- Calendar shows per-day pricing (varies by date)
- August pricing typically $75-85/day per person for the 3-Day Park-to-Park + 2 Free deal

### Step 3: Present Options Clearly

| Option | What You Get | Estimated Cost |
|--------|-------------|---------------|
| **3-Day Park-to-Park + 2 Free** | 5 days, 3 parks, park-to-park | ~$225-255/person total |
| **Add Volcano Bay** | Water park upgrade | Higher, check site |
| **Bundle with hotel** | Save up to $300 on package | Varies |
| **Universal direct** | Same deal, slightly higher | ~$260-300/person |

### Step 4: Check Blockout Dates

The promo has specific blockout dates where first visit is NOT valid:
- July 1-6, 2026
- October 9-12, 2026
- November 18-28, 2026

### Step 5: Use Browser for Calendar Pricing

The Undercover Tourist site uses a dynamic calendar widget. To get exact August pricing:
1. Navigate to the ticket page
2. Dismiss any popup
3. Click the right arrow (>) next to the month name to advance to the desired month
4. Read the per-day prices from the calendar buttons

**Pitfall:** The browser may struggle with the calendar navigation. If clicking the right arrow doesn't advance the month, try clicking it multiple times or use browser_vision to confirm the current month.

**Pitfall — Cloudflare blocking:** Undercover Tourist uses Cloudflare bot detection. The browser may get stuck on a "Just a moment..." / "Performing security verification" page. When this happens:
- The site is effectively blocked — no amount of retrying will get through
- Do NOT keep retrying the same URL — it will keep hitting Cloudflare
- Fall back to search result snippets for pricing (Google shows "from $X" in search results)
- Try Universal's own ticket store as an alternative (though it may also error)
- Present the "from" price as an estimate and note that exact pricing requires visiting the site directly
- Provide the direct link so the user can check themselves

### Step 6: Quote as Estimates

Always present ticket prices as **estimates** — the calendar shows per-day prices that vary, and final checkout may include tax. Use "~$X" or "estimated $X-XX" language.

**CRITICAL — "Starting from" is NOT the price for your dates:**
The "from $X" price shown on search results and product pages is the cheapest possible date (usually a Tuesday in September or off-peak). Peak dates like August 1st can be **$80-100+ more** than the "from" price. Always:
- Quote the "from" price as a range: "starting from ~$X, but August 1st will likely be higher"
- If you can't get the exact calendar price (blocked by Cloudflare, etc.), say: "I can only see the starting price of ~$X — the actual August 1st price will be higher. Here's the link to check yourself."
- Never say "it costs $X" based on the starting price alone — the user will see a different number at checkout and lose trust

### What Happened

**Context change:**
- User: "Kristell is no longer in the group. We've broken up. This is going to change the trip drastically."
- Original plan: Couple trip to Philippines (Makati/BGC)
- New plan: Solo trip to Angeles City (8 days) + Cambodia (4 days)

**Research completed:**
1. **Flight routing:** CVG → CRK (Clark Airport, literally in Angeles City)
2. **Multi-country option:** CRK → MNL → Cambodia (no direct flights, must route via Manila)
3. **Budget breakdown:** Base ($1,040-1,480) + Cambodia add-on ($372-660)
4. **Visa research:** Cambodia visa on arrival ($30 USD, 30 days)
5. **Weather timing:** September is cheapest (30-45% less) but rainy
6. **Decision framework:** Phnom Penh (cheaper) vs Siem Reap (Angkor Wat, bucket list)

### Key Learnings

**Solo trip planning:**
- Solo = more flexibility (can decide on Cambodia option while in Angeles City)
- Solo = lower costs (one person, not two)
- Solo = no coordination needed (book when ready)

**Multi-country routing:**
- Angeles City → Cambodia requires Manila layover (CRK → MNL → PNH/REP)
- No direct flights to Cambodia from Clark Airport
- Total travel time: 4h 45min - 6h 45min each way

**Budget structure:**
- Base trip vs add-on options help traveler see trade-offs
- Solo traveler can decide mid-trip (book Cambodia hotel from Angeles City)

**Visa research:**
- Cambodia visa on arrival is easy ($30 USD, passport photo, cash)
- No e-visa needed for US citizens

**Weather timing:**
- September is cheapest but rainy (monsoon season)
- Rain is usually brief (1-2 hours), mornings often clear
- Pack waterproof gear, plan indoor activities

### Files Created

- `HQ/01-Travel/Philippines/2026-Solo-Trip-Angeles-City-Cambodia.md` — Full plan
- `HQ/01-Travel/Philippines/2026-Birthday-Trip-Pampanga.md` — Updated status (solo, not couple)

---

## Pitfalls

### Pitfall 1: Not Confirming Solo Traveler Status

**Symptom:** Research assumes couple travel, then traveler status changes.

**Impact:** Wrong budget (double costs), wrong logistics (2 people vs 1), wrong recommendations.

**Fix:** **Always ask:** "Solo, couple, or group?" before starting research.

**Session 2026-07-07 example:**
- Original research: Couple trip to Makati/BGC
- User update: "Kristell is no longer in the group. Solo trip."
- Fix: Re-plan for solo traveler, adjust budget, change destination to Angeles City + Cambodia

---

### Pitfall 2: Assuming Direct Flights Between Secondary Destinations

**Symptom:** Assume CRK → Cambodia has direct flights.

**Impact:** Wrong travel time, wrong cost, wrong logistics.

**Fix:** **Always research multi-country routing:**
- Check if direct flights exist
- If not, identify hub cities (Manila, Bangkok, Singapore)
- Calculate total travel time (layovers included)
- Factor layover costs (meals, airport waiting)

**Session 2026-07-07 example:**
- Assumption: Angeles City → Cambodia direct
- Reality: CRK → MNL (45min) + MNL layover (1-3h) + MNL → Cambodia (3h) = 4h 45min - 6h 45min total
- Fix: Document full routing, including layovers

---

### Pitfall 3: Not Separating Base Trip from Add-ons

**Symptom:** Present single cost for entire trip (e.g., "$1,500 for Angeles City + Cambodia").

**Impact:** Traveler can't see trade-offs, can't decide mid-trip.

**Fix:** **Break down budget:**
- Base trip cost (primary destination)
- Add-on costs (secondary destinations)
- Total for each option
- This shows: "I can do base only ($1,040-1,480) and decide on Cambodia later"

**Session 2026-07-07 example:**
- Good: Base ($1,040-1,480) + Phnom Penh ($372-508) = $1,412-1,988 total
- Bad: "$1,988 for Angeles City + Cambodia" (no breakdown)

---

### Pitfall 4: Not Researching Visa Requirements

**Symptom:** Assume visa-free or visa on arrival without checking.

**Impact:** Traveler denied entry, stranded at border, forced to return.

**Fix:** **Always research:**
- Visa requirements (free, on arrival, e-visa, embassy)
- Cost ($ USD, local currency)
- Duration (30 days, 60 days, etc.)
- Requirements (photos, cash onward ticket, proof of funds)
- Processing time (e-visa: 3-5 days vs on arrival: immediate)

**Session 2026-07-07 example:**
- Good: Cambodia visa on arrival ($30 USD, passport photo, cash)
- Would be bad: Assume free entry (wrong for some passports)

---

### Pitfall 5: Not Considering Weather and Timing

**Symptom:** Recommend cheapest month without considering weather.

**Impact:** Traveler arrives during monsoon, experiences constant rain, disappointed.

**Fix:** **Research seasonal factors:**
- Rainfall (mm/month, patterns)
- Temperature (average, humidity)
- Typhoon/hurricane risk
- Crowds (peak vs off-peak)
- Price (how much cheaper off-peak)
- **Trade-offs:** "September is 30% cheaper but rainy — can you work around rain?"

**Session 2026-07-07 example:**
- September is cheapest (30-45% less) but rainy season
- Recommendation: "Pack waterproof gear, plan indoor activities (museums, malls)"
- Silver lining: Rains are intense but brief (1-2 hours), mornings often clear

---

### Pitfall 6: Not Providing Decision Framework

**Symptom:** Present options without helping traveler choose.

**Impact:** Traveler overwhelmed, delays decision, no clarity.

**Fix:** **Create decision framework:**
- Option A vs Option B vs Option C
- Pros and cons for each
- Total cost for each
- Trade-offs (cost vs experience vs time)

**Session 2026-07-07 example:**
- Option A: Base only (cheaper, simpler)
- Option B: Base + Phnom Penh (more variety, still reasonable cost)
- Option C: Base + Siem Reap (bucket list, more expensive)
- Help traveler choose based on priorities

---

## Quick Reference: Research Checklist

**Before starting:**
- [ ] Confirm traveler status (solo, couple, group)
- [ ] Confirm origin and primary destination
- [ ] Confirm duration and budget range
- [ ] Confirm timing (season, weather preferences)

**Research phase:**
- [ ] Flight routing (direct vs connecting, open-jaw options)
- [ ] Airport proximity (how far from destination)
- [ ] Multi-country options (if applicable)
- [ ] Budget breakdown (base + add-ons)
- [ ] Visa requirements (free, on arrival, e-visa)
- [ ] Weather and timing (seasonal factors)
- [ ] Logistics (transport, safety)

**Documentation:**
- [ ] Create trip plan file in vault
- [ ] Document flight routing table
- [ ] Document budget breakdown
- [ ] Document visa requirements
- [ ] Create decision framework
- [ ] List next steps (decisions needed, booking actions)

---

## Related Skills

- **vault-research-protocol** — Always search vault before external research
- **context-loading** — Load prior travel research from vault
- **auto-logging** — Auto-log trip details to vault
- **public-artifact-verification** — Verify outward-facing artifacts as the consumer sees them
- **source-of-truth-verification** — Find the file/code that actually runs

## Support Files

- `references/trip-data-path-and-privacy-check.md` — data-path audit for travel hubs and the companion-photo boundary

## Tools

- **LetsFG** — Flight search (preferred, if available)
- **Google Flights** — Flight search
- **Airline websites** — Direct booking, seat selection
- **Travel forums** — Reddit r/solotravel, TripAdvisor for real experiences

---

## Tools

- **LetsFG** — Flight search (preferred, if available)
- **Google Flights** — Flight search
- **Airline websites** — Direct booking, seat selection
- **Travel forums** — Reddit r/solotravel, TripAdvisor for real experiences

---

---

*Created: July 7, 2026 | Updated: October 1, 2026*
*Status: Active*
*Applies to: Solo, couple, and group travel; multi-country trips; budget optimization; employment-constrained trips*
