# Cronjob Coordination Strategies for Multi-Person Systems

**Date:** 2026-07-05
**Purpose:** Patterns for coordinating cronjobs across multiple family members to avoid API rate limits and message congestion.

---

## Problem Statement

When running cronjobs for multiple family members (Jordan, Vanito, Christel, etc.), simultaneous execution causes:
1. API rate limit hits (Steam, web search, etc.)
2. Message congestion in Telegram groups
3. Confusion about whose intelligence is being delivered
4. Cronjob failures due to resource contention

---

## Coordination Strategy

### Staggered Execution Pattern

**Rule:** Space out cronjobs by 30-minute intervals when they hit the same APIs or deliver to the same channels.

**Example: Game Intelligence Jobs**

| Time | Person | Job Type | Job ID |
|------|--------|----------|--------|
| 2:00 PM | Jordan | Game Release Intelligence | 41f8e6d0e24b |
| 2:30 PM | Jordan | Voice Patch Notes | 90e51510349c |
| 3:00 PM | Vanito | Game Release Intelligence | e28c895e6a11 |
| 3:30 PM | Vanito | Voice Patch Notes | a564b3353770 |

**Benefits:**
- Steam API gets 4 separate hits spaced by 30 minutes
- Entertainment group gets messages spread over 1.5 hours
- Each job has dedicated resources
- Clear separation between family member outputs

### Update Pattern

**When:** New family member added, new job type created, or API rate limit issues arise.

**Example: Staggering Vanito's jobs**
```bash
# Original: Both at 2:00 PM
# Vanito game intel: 2:00 PM
# Vanito voice notes: 2:00 PM

# Updated: Stagger by 30 minutes
cronjob action=update job_id=e28c895e6a11 schedule="0 15 * * *"  # 3:00 PM
cronjob action=update job_id=a564b3353770 schedule="30 15 * * *"  # 3:30 PM
```

**Cron Expression Format:**
- `0 14 * * *` = 2:00 PM daily
- `30 14 * * *` = 2:30 PM daily
- `0 15 * * *` = 3:00 PM daily
- `30 15 * * *` = 3:30 PM daily

---

## Person-Level Data Isolation

### Prompt-Level Identification

**Rule:** Every cronjob prompt MUST explicitly state which person it's serving, including Steam ID.

**Pattern:**
```python
prompt = """
You are Gentech delivering PERSON_NAME's GenTech Game News — personalized game release intelligence.

⚠️ IMPORTANT: This is for PERSON_NAME's data, NOT other family members.

Steam ID: PERSON_STEAM_ID
Steam Wishlist: https://steamcommunity.com/profiles/PERSON_STEAM_ID/wishlist
Steam Recent Games: https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key=STEAM_API_KEY&steamid=PERSON_STEAM_ID&count=10

Fetch PERSON_NAME's wishlist and recent games, then search for patch notes, news, and announcements.
"""
```

**Example: Jordan's Game Intelligence**
```python
prompt = """
You are Gentech delivering Jordan's GenTech Game News — personalized game release intelligence for JORDAN (ProtoJay4789), not Vanito.

⚠️ IMPORTANT: This is for JORDAN's wishlist (Steam ID: 76561197996487689), NOT Vanito's (76561198132811363).

## STEP 1: Get Jordan's Steam ID
Jordan's Steam ID: 76561197996487689

## STEP 2: Fetch Jordan's Steam Wishlist
Use Steam Community API:
https://steamcommunity.com/profiles/76561197996487689/wishlist

## STEP 3: Get Jordan's Recently Played Games
Use Steam API to get games played in the last 2 months:
https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key=STEAM_API_KEY&steamid=76561197996487689&count=10

## STEP 4: Fetch Game News for Jordan's Games
[Rest of the prompt...]
"""
```

---

## Cronjob Naming Convention

### Pattern: `[Person] GenTech Shop — Function Name`

**Examples:**
- `[Jordan] GenTech Shop — Game Release Intelligence`
- `[Vanito] GenTech Shop — Game Release Intelligence`
- `[Jordan] GenTech Shop — Voice Patch Notes (Optimus Prime)`
- `[Vanito] GenTech Shop — Weekly Sales Sweep`

**Why This Works:**
- Easy to identify at a glance whose job is running
- Clear separation in cronjob list
- Prevents confusion when debugging

---

## Related Skills

- `gentech-family-hub-management` — Multi-person hub coordination
- `gentech-family-hub-management:references/family-member-registry.md` — Family member data
- `agent-health-audit` — Systematic health checks across cronjobs