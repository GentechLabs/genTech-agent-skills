# Verified Deal Check Pattern

**When to use:** Running deal tracker checks with 100% game identity verification (no fake games).

**Pattern:**

```python
import json
from deal_tracker import CheapSharkClient

# Load watchlist (items OR games key - dual check)
with open('watchlist.json', 'r') as f:
    data = json.load(f)
games = data.get('items', data.get('games', []))

client = CheapSharkClient(cache_enabled=True)

deep_cuts = []
solid_sales = []
light_marks = []
barely = []
unreleased = []

for game in games:
    title = game['title']
    steam_id = game.get('steam_appid')  # MUST exist for verification
    
    # Search for deals
    deals = client.search_deals(title)
    
    # CRITICAL: Filter by exact Steam AppID match ONLY
    matched_deals = [d for d in deals if d.steam_app_id == steam_id]
    
    if not matched_deals:
        # No deals with matching AppID = unreleased or not on sale
        unreleased.append((title, steam_id))
        continue
    
    # Get best price from matched deals
    best = min(matched_deals, key=lambda d: d.sale_price)
    
    # Classify by discount tier
    if best.savings >= 50:
        deep_cuts.append(best)
    elif best.savings >= 25:
        solid_sales.append(best)
    elif best.savings >= 10:
        light_marks.append(best)
    elif best.savings > 0:
        barely.append(best)
```

**Key principles:**

1. **ALWAYS sync Steam wishlist first** to get accurate `steam_appid` values
2. **Filter by `steam_app_id` field**, not title similarity — this eliminates fake games
3. **Dual key check** when loading watchlist: `data.get('items', data.get('games', []))`
4. **Unreleased detection** — empty matched_deals list = game not found on sale

**Multi-user pattern:**

```bash
# Sync each user's wishlist
python3 deal_runner.py sync-steam 76561198068413360  # Jordan
python3 deal_runner.py sync-steam 76561198132811363  # Vanito

# Watchlists created as watchlist-{steam_id}.json
# Then run the verified check pattern on each file
```

**Steam ID reference:**
- Jordan: 76561198068413360 (ProtoJay4789)
- Vanito: 76561198132811363 (vanzantkiller)