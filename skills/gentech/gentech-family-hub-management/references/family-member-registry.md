# Family Member Registry — GenTech Hubs

**Last Updated:** 2026-07-05
**Purpose:** Central registry of all family members, their Steam IDs, cronjobs, and hub infrastructure.

---

## Jordan (ProtoJay4789)

### Identity
- **Name:** Jordan
- **Steam ID:** `76561197996487689`
- **Profile:** ProtoJay4789
- **Groups:** HQ, Strategies, Labs, Entertainment

### Hub Infrastructure
- **Main Hub:** `/root/ProtoJay4789.github.io/hub-jordan.html` (if exists)
- **Data File:** `/root/ProtoJay4789.github.io/hub-jordan-data.json` (if exists)
- **Portfolio:** `https://protojay4789.github.io`

### Cronjobs

#### Game Intelligence
| Job ID | Name | Schedule | Status | Next Run |
|--------|------|----------|--------|----------|
| 41f8e6d0e24b | `[Jordan] GenTech Shop — Game Release Intelligence` | Daily 2:00 PM | ✅ Active | 2026-07-06 14:00 |
| 90e51510349c | `[Jordan] GenTech Shop — Voice Patch Notes (Optimus Prime)` | Daily 2:30 PM | ✅ Active | 2026-07-05 14:30 |

#### Shopping & Sales
| Job ID | Name | Schedule | Status | Next Run |
|--------|------|----------|--------|----------|
| 80fd54684d86 | `[Jordan] GenTech Shop — Weekly Sales Sweep` | Wed 12:00 PM | ✅ Active | 2026-07-08 12:00 |

### Data Sources
- **Steam Wishlist:** https://steamcommunity.com/profiles/76561197996487689/wishlist
- **Steam Recent Games:** https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key=STEAM_API_KEY&steamid=76561197996487689&count=10

---

## Vanito

### Identity
- **Name:** Vanito
- **Role:** GenTech Warrior, PoE2 Player, Jordan's Son
- **Steam ID:** `76561198132811363`
- **Groups:** Entertainment
- **Music Style:** Hood rap with Japanese anime energy
- **Beat-em-up Game Interest:** Wants music for beat-em-up games

### Hub Infrastructure
- **Main Hub:** `https://protojay4789.github.io/hub-vanito.html`
- **Data File:** `/root/ProtoJay4789.github.io/hub-vanito-data.json`
- **Music Dashboard:** `https://protojay4789.github.io/Gaming/vanito-music-dashboard.html`
- **Wishlist Tracker:** `https://protojay4789.github.io/Gaming/wishlist-vanito.html`

### Hub Data Structure
```json
{
  "lastUpdated": "2026-07-04T12:00:00.000Z",
  "name": "Vanito",
  "avatar": "Vanito",
  "tagline": "PoE2 Warrior",
  "steamId": "76561198132811363",
  "status": "Active",
  "projects": [],
  "stats": {
    "level": 0,
    "builds": 0,
    "gold": 0
  },
  "music": {
    "songs": [
      {
        "title": "EXTINCTION PROTOCOL",
        "style": "Resident Evil Mercenaries - Industrial Metal/Hip-Hop",
        "added": "2026-07-05"
      },
      {
        "title": "GRAVITY'S KISS",
        "style": "Stellar Blade - Electronic Synth/Korean-English Mix",
        "added": "2026-07-05"
      }
    ],
    "lastUpdated": "2026-07-05"
  }
}
```

### Cronjobs

#### Game Intelligence
| Job ID | Name | Schedule | Status | Next Run |
|--------|------|----------|--------|----------|
| e28c895e6a11 | `[Vanito] GenTech Shop — Game Release Intelligence` | Daily 3:00 PM | ✅ Active | 2026-07-05 15:00 |
| a564b3353770 | `[Vanito] GenTech Shop — Voice Patch Notes (Optimus Prime)` | Daily 3:30 PM | ✅ Active | 2026-07-05 15:30 |

#### Shopping & Sales
| Job ID | Name | Schedule | Status | Next Run |
|--------|------|----------|--------|----------|
| 1c25463fc281 | `[Vanito] GenTech Shop — Weekly Sales Sweep` | Wed 12:00 PM | ✅ Active | 2026-07-08 12:00 |

#### Music Sync
| Job ID | Name | Schedule | Status | Next Run |
|--------|------|----------|--------|----------|
| f3e90d867b9c | `vanito-music-sync` | Every 6 hours | ✅ Active | 2026-07-05 18:35 |

### Data Sources
- **Steam Wishlist:** https://steamcommunity.com/profiles/76561198132811363/wishlist
- **Steam Recent Games:** https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key=STEAM_API_KEY&steamid=76561198132811363&count=10
- **Hub Data:** `hub-vanito-data.json` (local JSON file)

### Music Sync Infrastructure
- **Script:** `/root/my-music/vanito-music-sync.py`
- **Source:** `hub-vanito-data.json`
- **Destination:** `Gaming/vanito-music.json`
- **Sync Frequency:** Every 6 hours
- **Workflow:** Vanito edits JSON → Sync script runs → Commits to GitHub → GitHub Pages deploys

---

## Christel

### Identity
- **Name:** Christel
- **Role:** Family member (Jordan arrival prep)
- **Groups:** Entertainment (if applicable)

### Hub Infrastructure
- **Main Hub:** `https://protojay4789.github.io/Cookbook/christel-hub.html`
- **Shopping Dashboard:** `https://protojay4789.github.io/Cookbook/shopping-list.html`
- **Cookbook:** `https://protojay4789.github.io/Cookbook/christel-kitchen.html`

### Shopping Data
- **Items Purchased:** 8 (₱3,297)
- **Items Needed:** 1 (₱1,200)
- **Grand Total:** ₱4,497
- **Platform:** Shopee Philippines

---

## Cronjob Schedule Matrix

### Daily Game Intelligence (Staggered)

| Time | Person | Job Type | Job ID |
|------|--------|----------|--------|
| 2:00 PM | Jordan | Game Release Intelligence | 41f8e6d0e24b |
| 2:30 PM | Jordan | Voice Patch Notes | 90e51510349c |
| 3:00 PM | Vanito | Game Release Intelligence | e28c895e6a11 |
| 3:30 PM | Vanito | Voice Patch Notes | a564b3353770 |

**Staggering Benefits:**
- No API rate limit clashes
- Messages spaced out for readability
- Clear separation between family member intelligence

### Weekly Sales Sweeps

| Day | Time | Person | Job ID |
|-----|------|--------|--------|
| Wednesday | 12:00 PM | Jordan | 80fd54684d86 |
| Wednesday | 12:00 PM | Vanito | 1c25463fc281 |

**Note:** Both jobs run at same time but target different Steam IDs.

---

## File Path Registry

### GitHub Pages Structure
```
/root/ProtoJay4789.github.io/
├── hub-vanito.html              # Vanito's main hub
├── hub-vanito-data.json         # Vanito's data source
├── Gaming/
│   ├── vanito-music-dashboard.html   # Vanito's music dashboard
│   ├── vanito-music.json             # Synced music data
│   ├── wishlist-vanito.html          # Vanito's wishlist tracker
│   └── poe2-vanito.json              # Vanito's POE2 builds
├── Cookbook/
│   ├── christel-hub.html             # Christel's main hub
│   ├── christel-kitchen.html         # Christel's cookbook
│   └── shopping-list.html            # Christel's shopping list
└── hub-jordan.html              # Jordan's main hub (if exists)
    hub-jordan-data.json         # Jordan's data source (if exists)
```

### Vault Structure
```
/root/vaults/gentech/
├── 15-Gaming/
│   ├── Vanito-Music-Sync.md    # Music sync protocol
│   └── poe2-vanito.json        # POE2 build data
├── 11-Mess Hall/
│   ├── vanito-hub-audit-2026-07-05.md
│   └── vanito-music-sync-active.md
└── Cookbook/
    ├── HUB.md                  # Christel's hub structure
    └── shopping-list-arrival-prep.md  # Shopping list
```

### Scripts
```
/root/my-music/
├── vanito-music-sync.py        # Vanito music sync script
├── playlists/
│   └── vanito-all.json         # Music playlist
└── README.md                   # User guide

/root/.hermes/profiles/gentech/scripts/
├── gaming-hub-sync.py          # Gaming hub sync
└── rate-limit-escalation.py    # Rate limit monitor
```

---

## Updating This Registry

### When to Update
- Adding new family member
- Changing Steam ID
- Adding/removing cronjobs
- Updating hub infrastructure
- Changing file paths

### Update Pattern
1. Update this file with new information
2. Run `ob sync` in `/root/vaults/gentech/` to commit
3. Update relevant cronjobs with new data
4. Verify all links and paths

---

## Related Skills

- `gentech-family-hub-management` — Multi-person hub coordination
- `enhanced-gentech-shop` — Shopping dashboards and price tracking
- `gentech-daily-sync` — Daily vault synchronization