# Theme Park & Entertainment Ticket Research

## When to Use
User asks about theme park tickets, amusement park deals, concert tickets, or entertainment venue pricing in the US or internationally.

## Research Workflow

### 1. Identify the Venue & Current Promotions
- Search for the venue's official deals/specials page
- Common pattern: multi-day promos (Buy X Get Y Free, Kids Free, etc.)
- Note the **purchase deadline** AND the **visit window** — these are different

### 2. Check Authorized Resellers (Parallel)
| Reseller | Notes |
|----------|-------|
| **Groupon** | Often 20-36% off multi-day tickets. Check "Purchase by" date. |
| **Get Away Today** | Authorized for Universal, Disney. Sometimes deeper discounts. |
| **Undercover Tourist** | Long-standing authorized reseller. Bundles with hotels. |
| **Costco** | Travel packages with tickets + hotel. Members-only pricing. |
| **Sam's Club** | Occasionally has FL resident or multi-day deals. |
| **Tripster** | Bundles tickets with nearby attractions. |

### 3. Price Comparison Framework
Always compare:
- **Direct from venue** (official price)
- **Groupon** (often cheapest for multi-day)
- **Authorized reseller** (Get Away Today, Undercover Tourist)
- **Package deals** (hotel + tickets bundle)

Present as a comparison table with:
- Ticket type (Base vs Park-to-Park vs VIP)
- Price per person
- Price for group (if # of people known)
- Savings vs direct
- Any blockout dates or restrictions

### 4. Key Details to Surface
- **Blockout dates** — Can make or break the deal
- **Purchase deadline** vs **visit window** — Different dates
- **Refund/transfer policy** — Most are non-refundable, non-transferable
- **Valid date range** — Must fall within user's trip dates
- **Biometric/ID requirements** — Some parks require scan at entry
- **Park hopping rules** — Base (one park/day) vs Park-to-Park (all parks same day)
- **Special access** — Hogwarts Express at Universal requires Park-to-Park

### 5. Decision Matrix for User
Present options based on trip length:
- **1-2 days** → Single-day or 2-day tickets (usually not discounted much)
- **3-5 days** → Buy X Get Y Free promos (sweet spot for savings)
- **7+ days** → Multi-day packages with hotel bundles

### 6. À La Carte vs Bundled Comparison
**Pitfall:** Users sometimes plan to buy a base multi-day ticket for legacy parks + separate single-day tickets for the new/premium park. In 2026, Universal restructured multi-day tickets to include Epic Universe — so the "old school" approach of buying separate tickets is almost always more expensive.

**Example (Universal Orlando 2026, solo traveler):**
| Approach | What You Get | Total Cost |
|----------|-------------|------------|
| À la carte: 5-day Studios/Islands + 1 Epic Universe day | 6 days, split tickets | ~$490-540 |
| À la carte: 5-day Studios/Islands + 2 Epic Universe days | 7 days, split tickets | ~$630-680 |
| Buy 3 Get 2 Free (direct) | 5 days, all parks | $367-427 |
| Buy 3 Get 2 Free (Groupon) | 5 days, all parks | ~$257 |

**Always check if the bundled deal covers the parks the user wants** before recommending à la carte. The 2026 multi-day products (3+, 4+, 5+) include Epic Universe access, making separate Epic Universe tickets redundant.

## Universal Orlando Specifics (2026)
- **Epic Universe** is the new park (opened 2025) — highest demand
- Single-day Epic Universe: starts at $139
- Buy 3 Get 2 Free: ~$73-85/day (Base vs Park-to-Park)
- 7 Days for Price of 5: ~$65/day (cheapest per-day, but higher total)
- Blockout dates vary by promo — always check before buying
- Groupon purchase deadline for summer 2026: August 26, 2026
- **2026 ticket restructuring**: Multi-day tickets (3+) now include Epic Universe access. "2-Park" products (Studios + Islands only) are separate and less common. Don't assume the user needs to buy Epic Universe separately — the bundled deal likely already covers it.

## Disney World Comparison
- Similar promo structure to Universal
- Free Dining deals come and go — check Disney Tourist Blog
- Costco packages often best value for Disney

## Pitfalls
1. **Groupon Cloudflare blocks** — Bot detection prevents direct browser access. Use search snippets + third-party review sites for pricing instead.
2. **Dynamic pricing** — Theme parks use date-based pricing. Weekend/holiday prices spike. Check multiple date ranges.
3. **Purchase deadline confusion** — User may think deal expires before their trip when it's actually the purchase deadline, not visit deadline.
4. **Non-refundable tickets** — Most promo tickets are final sale. Confirm trip dates before buying.
5. **web_extract often fails** — DuckDuckGo backend blocks extraction from many booking/travel sites. Fall back to browser_navigate or web_search snippets.
6. **À la carte pricing trap (2026+)** — Universal restructured multi-day tickets in 2026 to include Epic Universe. Users planning to buy "a 5-day Studios/Islands ticket + separate Epic Universe days" will pay significantly more ($490-680) than the Buy 3 Get 2 Free bundle ($257-427). Always check if bundled deals already cover the parks they want before recommending à la carte.

## Sources for Deal Tracking
- Disney Tourist Blog (disneytouristblog.com) — Universal + Disney deals, detailed pricing breakdowns
- Deep Arrival (deeparrival.com) — Excellent ticket deal analysis with decision matrices and cost math
- Touring Plans (touringplans.com) — Crowd calendars + pricing
- Theme Park Shark (themeparkshark.com) — Official price tracking, ticket structure explanations
- MouseSavers (mousesavers.com) — Disney-focused deals
- Theme Park Insider (themeparkinsider.com) — Reviews + deals

## Live Deal Links (verified Jun 2026)
- Groupon Universal Orlando: `https://www.groupon.com/deals/gl-universal-orlando-59` (Buy 3 Get 2 Free, purchase by Aug 26, 2026)
- Universal Official Deals: `https://www.universalorlando.com/web/en/us/tickets-packages/deals-specials`
- Get Away Today: `https://www.getawaytoday.com/tickets/universal-orlando-resort/` (authorized reseller, sometimes deeper discounts)
