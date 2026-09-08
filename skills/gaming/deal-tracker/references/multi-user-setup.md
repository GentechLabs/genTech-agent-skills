# Multi-User Setup & Per-User Cron Jobs

## Adding a New User (e.g., Vanito)

### Step 1: Get Their Steam Info
- Steam profile URL (e.g., `https://steamcommunity.com/id/vanzantkiller`)
- Steam ID (17-digit number, e.g., `76561198132811363`)
- Profile must be Public (Game Details)

### Step 2: Sync Their Wishlist
```bash
cd /root/vaults/gentech/10-Labs/deal-tracker
python3 deal_runner.py sync-steam 76561198132811363
```
This creates `watchlist-76561198132811363.json` automatically.

### Step 3: Create Per-User Cron Jobs
Use `[Username]` prefix in job names for clarity:

```
[Vanito] GenTech Shop — Weekly Sales Sweep
[Vanito] GenTech Shop — Game Release Intelligence
```

**Schedule:**
- Weekly Sales: Wed 12 PM (same as Jordan)
- Daily Patch Notes: 2 PM (same as Jordan)

**Prompt pattern:**
```
1. Sync Vanito's Steam wishlist:
cd /root/vaults/gentech/10-Labs/deal-tracker
python3 deal_runner.py sync-steam 76561198132811363

2. Generate the weekly report for Vanito:
python3 deal_runner.py check --user 76561198132811363
```

### Step 4: Verify
- Check `watchlist-{steam_id}.json` exists and has games
- Run a test sweep to confirm deals are found
- Confirm delivery to Entertainment group

## Cron Job Naming Convention

| Pattern | Example |
|---------|---------|
| `[Jordan] GenTech Shop — Weekly Sales Sweep` | Jordan's deal alerts |
| `[Jordan] GenTech Shop — Game Release Intelligence` | Jordan's patch notes |
| `[Vanito] GenTech Shop — Weekly Sales Sweep` | Vanito's deal alerts |
| `[Vanito] GenTech Shop — Game Release Intelligence` | Vanito's patch notes |
| `[Jordan] POE2 Build Health — Gaming Hub Sync` | Jordan's build tracker |

**Rule:** Always prefix with `[Username]` so Jordan and team know whose job it is.

## File Structure
```
watchlist.json                    → Jordan's default
watchlist-76561198132811363.json   → Vanito's watchlist
.patch-notes-state/               → Per-game release intel state
```

## Gotchas
- Steam profile must be Public (Game Details) for wishlist API to work
- CheapShark rate limiting: 429s after ~5-10 rapid requests
- Per-user reports auto-detect all watchlist files via glob
- Feature flags per user: `{"patch_notes": true, "deal_tracker": true}`
