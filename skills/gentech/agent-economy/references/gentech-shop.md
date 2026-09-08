# GenTech Shop — Shopping Intelligence Platform

## Overview

GenTech Shop is the rebranded Deal Tracker — a full shopping intelligence layer covering multiple verticals. Revenue-first priority: Amazon Affiliate (10% commission) covers tech, health, home, everything.

**Rebrand:** Deal Tracker → GenTech Shop (Jun 25, 2026)

## Architecture

Same pattern across all verticals:
1. **Monitor** — watch prices/availability
2. **Parse** — categorize what matters to user
3. **Alert** — agent tells you when something changes

## Verticals (Revenue Hierarchy)

| Rank | Vertical | Revenue Model | Commission |
|------|----------|---------------|------------|
| 🥇 | Amazon Affiliate | Covers tech, health, home, everything | Up to 10% |
| 🥈 | Tech/Electronics | High ticket items | Best Buy, Newegg |
| 🥉 | Health/Supplements | Recurring purchases | Amazon, iHerb |
| 4 | Travel/Flights | High commissions | Booking APIs |
| 5 | Fashion | Seasonal, high volume | Nike, Adidas |
| 6 | Gaming | Engagement (already have this) | CheapShark |

## Active Components

### Deal Tracker (Live)
- **Location:** `10-Labs/deal-tracker/`
- **API:** CheapShark (free, no key)
- **Features:** Game search, deal comparison, price history, wishlist monitoring
- **Tests:** 12/12 passing

### Patch Notes (Live)
- **Location:** `10-Labs/deal-tracker/release_intel.py`
- **API:** Steam News API (free, no key)
- **Features:** Devlogs, release dates, game updates
- **Filter:** By Steam library (games user actually plays)

### POE2 Build Health (Live)
- **Location:** `Gaming/poe2-jordan-monk.json`
- **Features:** Patch impact assessment, milestone tracking, build health score
- **Cron:** Daily 9 AM, syncs with Gaming Hub

### Steam Integration (Live)
- **Wishlist API:** `IWishlistService/GetWishlist/v1/` (free, no key)
- **Profile:** Public game details required
- **Multi-user:** Per-user watchlist files (`watchlist-{steam_id}.json`)

## Cron Jobs

| Job | Schedule | User |
|-----|----------|------|
| `[Jordan] GenTech Shop — Weekly Sales Sweep` | Wed 12 PM | Jordan |
| `[Jordan] GenTech Shop — Game Release Intelligence` | Daily 2 PM | Jordan |
| `[Jordan] POE2 Build Health — Gaming Hub Sync` | Daily 9 AM | Jordan |
| `[Vanito] GenTech Shop — Weekly Sales Sweep` | Wed 12 PM | Vanito |
| `[Vanito] GenTech Shop — Game Release Intelligence` | Daily 2 PM | Vanito |

## Future Phases

### Phase 1: Amazon Intelligence (Highest Revenue)
- Amazon Product Monitor (price drops, stock alerts)
- Subscribe & Save Tracker (recurring orders)
- Delivery Notifications (shipping status)
- Affiliate Link Generator (auto-tracked links)
- Price History Dashboard

### Phase 2: Vertical Expansion
- Tech/Electronics (Best Buy, Newegg)
- Health/Supplements (iHerb, Costco)
- Travel/Flights (booking APIs)
- Fashion (Nike, Adidas, Zara)

### Phase 3: Intelligence Layer
- Shopping Profile (learn what user buys)
- Smart Alerts ("your protein powder went on sale")
- Subscription Optimizer
- Cross-Retailer Comparison

### Phase 4: Gaming Intelligence (Active)
- ✅ Deal Tracker — Steam wishlist, price drops
- ✅ Patch Notes — Steam News API, devlogs
- ✅ POE2 Build Health — Patch assessment, milestones
- ✅ Vanito Integration — Steam wishlist synced, cron jobs
- 🔲 POE2 .build File Converter — Plan → export → import into game
- 🔲 Steam Playtime Filter — Patch notes by games actually played

## Key Files

- `10-Labs/deal-tracker/deal_runner.py` — Main runner script
- `10-Labs/deal-tracker/deal_tracker.py` — Core deal tracking logic
- `10-Labs/deal-tracker/release_intel.py` — Patch notes intelligence
- `Gaming/poe2-jordan-monk.json` — Jordan's Monk build data
- `Gaming/patch-data.json` — Patch notes data
- `Gaming/build-health.json` — Build health score

## Revenue Model

- Amazon Affiliate: 10% commission on qualifying purchases
- Subscribe & Save: recurring revenue from tracked orders
- Premium Tier: advanced alerts, price predictions, multi-retailer
