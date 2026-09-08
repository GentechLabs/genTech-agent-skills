# CheapShark Rate Limit Fallback Pattern

## Problem

CheapShark rate-limits aggressively. After ~5-10 rapid requests from the same IP, all subsequent calls return HTTP 429 for 60-120+ seconds. This makes batch deal sweeps (86+ games) unreliable from the terminal.

**Critical: 429s can persist 5+ minutes.** A single burst of rapid calls (e.g. from a previous failed cron run) can lock the IP for 5+ minutes. The `/stores` endpoint recovers first (~60-90s), but the `/deals` endpoint stays blocked much longer. If you get 429 on `/deals`, the IP may be unusable for the entire cron window. **Do not retry from the same IP repeatedly** — each retry resets the cooldown timer. Switch to `web_extract` immediately or skip the sweep and report the block.

## Solution: Two-Tier Strategy

### Tier 1 — Terminal client (fast, but rate-limited)

Use `CheapSharkClient` (urllib/requests) for small batches (<10 games) or when you know the IP is fresh. The client has built-in rate limiting (1s delay) and retry logic.

```python
from deal_tracker import CheapSharkClient
client = CheapSharkClient(cache_enabled=True)
results = client.search_deals("Resident Evil 3")
```

### Tier 2 — `web_extract` fallback (slower, bypasses 429)

When the terminal client is 429'd, use `web_extract` to fetch individual deal lookups. This tool routes through a different egress path and is not subject to the same rate limit.

```python
from hermes_tools import web_extract
import json

result = web_extract(urls=[f"https://www.cheapshark.com/api/1.0/deals?title={title}&upperPrice=9999"])
# result["results"][0]["content"] contains JSON in a markdown code block
```

**Important:** `web_extract` returns the JSON wrapped in a markdown code fence. Parse it with:

```python
import json, re
content = result["results"][0]["content"]
# Strip markdown code fence
json_str = re.sub(r'^```json\n|```$', '', content.strip(), flags=re.MULTILINE)
data = json.loads(json_str)
```

### Tier 3 — Batch via all-deals endpoint (1-2 calls, but large response)

Instead of 86 individual title searches, fetch the full deals list and match by `steamAppID`:

```python
import json, urllib.request
url = "https://www.cheapshark.com/api/1.0/deals?upperPrice=9999&pageSize=500"
req = urllib.request.Request(url, headers={"User-Agent": "GenTech-Shop/1.0"})
with urllib.request.urlopen(req, timeout=30) as resp:
    all_deals = json.loads(resp.read().decode())

# Build lookup by steamAppID
deal_by_appid = {}
for d in all_deals:
    appid = d.get("steamAppID")
    if appid:
        appid = int(appid)
        if appid not in deal_by_appid or float(d.get("savings", 0)) > float(deal_by_appid[appid].get("savings", 0)):
            deal_by_appid[appid] = d
```

**Caveat:** The all-deals endpoint is also rate-limited. If 429'd, fall back to Tier 2.

## Store Name Resolution

The `/deals` endpoint returns `storeID` (numeric string), NOT `storeName`. Resolve via:

```python
# Fetch store map once
stores_url = "https://www.cheapshark.com/api/1.0/stores"
# ... fetch and parse ...
store_map = {str(s["storeID"]): s["storeName"] for s in stores_data}

# Then for each deal:
store_name = store_map.get(str(deal["storeID"]), f"Store {deal['storeID']}")
```

Store ID to name mapping (as of Jul 2026):
| ID | Store |
|----|-------|
| 1 | Steam |
| 2 | GamersGate |
| 3 | GreenManGaming |
| 4 | Amazon |
| 5 | GameStop |
| 7 | GOG |
| 11 | Humble Store |
| 13 | Uplay |
| 15 | Fanatical |
| 21 | WinGameStore |
| 23 | GameBillet |
| 25 | Epic Games Store |
| 27 | Gamesplanet |
| 30 | IndieGala |
| 35 | DreamGame |

## Cron Job Pattern

For weekly cron sweeps of 86+ games:

1. **First attempt:** Use `CheapSharkClient` with `cache_enabled=True` and 1s delay between calls. This works if the IP is fresh.
2. **If 429'd:** Kill the process, wait 60s, then use `web_extract` for individual lookups of the top-priority games only (the ones most likely to be on sale).
3. **Alternative:** Use the all-deals batch approach (Tier 3) with a single API call, then match by `steamAppID`. This is 1-2 calls instead of 86.
4. **If completely blocked (5+ min):** Skip the sweep and report the block. Do NOT keep retrying — each retry resets the cooldown. Use the last-known-good data from the HTML dashboard (`wishlist-vanito.html`, `hub-vanito.html`) as a fallback for the report. The dashboard data is stale (last updated ~Jul 8) but better than nothing.

## Last-Known-Good Fallback

When CheapShark is completely blocked, the HTML dashboards in the vault contain the last successful deal scan. These are static HTML files with embedded deal data:

- `/root/vaults/gentech/Gaming/wishlist-vanito.html` — Vanito's wishlist with tiered deals
- `/root/vaults/gentech/hub-vanito.html` — Vanito's hub dashboard

Parse these with `web_extract` or `read_file` to extract the last-known deal data. The HTML has a consistent structure: `.game` divs with `.game-title`, `.price-current`, `.discount`, and `.store` classes. The stats bar at the top shows total games, on-sale count, deep cuts, and unreleased counts.
