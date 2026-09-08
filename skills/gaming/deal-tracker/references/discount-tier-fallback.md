# Discount Tier Fallback Pattern

**When to use:** `weekly_report.py` times out (120s+) or hangs. Usually caused by API rate limits when checking 60+ games.

**What it does:** Manual tiered report generation — loads watchlist.json, uses `get_cheapest_price()` with Steam AppID cross-referencing, buckets by discount depth.

**Key principle:** Always use `get_cheapest_price(game_id, title, steam_appid=...)` for verified results. The `search_deals(title)` approach returns fuzzy matches that can include unrelated games (confirmed Jul 14, 2026: 4 of 8 apparent deals were false positives before Steam AppID filtering).

**Copy-paste script:**

```python
import json
from deal_tracker import CheapSharkClient
from concurrent.futures import ThreadPoolExecutor, as_completed

client = CheapSharkClient(cache_enabled=True)

with open('watchlist.json') as f:
    data = json.load(f)
games = data.get('games', data.get('items', []))

deals_50plus = []
deals_25_49 = []
deals_10_24 = []
upcoming_no_deal = []
released_no_deal = []

for g in games:
    title = g['title']
    sid = g.get('steam_appid', g.get('game_id', ''))
    
    # Use Steam AppID cross-referencing for accuracy
    deal = client.get_cheapest_price(g['game_id'], title=title, steam_appid=sid)
    
    if deal and deal.savings >= 10:
        if deal.savings >= 50:
            deals_50plus.append(deal)
        elif deal.savings >= 25:
            deals_25_49.append(deal)
        else:
            deals_10_24.append(deal)
        continue
    
    # No significant deal — classify as upcoming or just not on sale
    # (Can optionally check Steam API via release_intel.get_app_details()
    #  to distinguish unreleased from full-price)
    if deal is None:
        upcoming_no_deal.append(title)
    else:
        released_no_deal.append(title)

deals_50plus.sort(key=lambda d: d.savings, reverse=True)
deals_25_49.sort(key=lambda d: d.savings, reverse=True)
deals_10_24.sort(key=lambda d: d.savings, reverse=True)

# Print report
print(f"🔥 DEEP CUTS (50%+ off) — {len(deals_50plus)}")
for d in deals_50plus:
    print(f"  {d.title}")
    print(f"     ${d.sale_price:.2f}  was ${d.normal_price:.2f}  (−{d.savings:.0f}%)  @ {d.store_name}")

print(f"\n💰 SOLID SALES (25-49% off) — {len(deals_25_49)}")
for d in deals_25_49:
    print(f"  {d.title}")
    print(f"     ${d.sale_price:.2f}  was ${d.normal_price:.2f}  (−{d.savings:.0f}%)  @ {d.store_name}")

print(f"\n🏷️ LIGHT MARKS (10-24% off) — {len(deals_10_24)}")
for d in deals_10_24:
    print(f"  {d.title}")
    print(f"     ${d.sale_price:.2f}  was ${d.normal_price:.2f}  (−{d.savings:.0f}%)  @ {d.store_name}")

print(f"\n📋 No significant deal: {len(released_no_deal)}  •  Upcoming/unreleased: {len(upcoming_no_deal)}")
```

**Pre-order deal handling:** Games with `coming_soon: True` on Steam may still have pre-order deals. `get_cheapest_price()` with steam_appid returns valid pre-order prices — include them in the discount tiers rather than treating them as unreleased. Verified Jul 14, 2026: Onimusha: Way of the Sword (releases Sep 3, 2026) had a $57.39 pre-order at 18% off via GreenManGaming.

**Performance note:** Expect 90-120 seconds for a full 64-game check with `cache_enabled=True`. CheapShark rate-limits aggressively (~5-10 rapid calls triggers 429). The cache prevents redundant calls on re-runs.

**Steam API release status differentiation:** When you need to distinguish "unreleased" from "not on sale" (instead of lumping both as "no deal"), use `release_intel.get_app_details(int(steam_appid))`:
```python
info = release_intel.get_app_details(int(sid))
if info:
    rd = info.get('release_date', {})
    if rd.get('coming_soon', False):
        # Genuinely unreleased
    else:
        # Released, just not on sale right now
```

**Timing for reliable batch checks:**
- 60-80 games: allow 90-120s with cache
- Steam AppID resolution: 1 req/sec via Steam API (adds ~3-5s per 10 games)
- Always set `cache_enabled=True` for batch operations
