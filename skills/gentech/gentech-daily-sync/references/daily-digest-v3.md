# Daily Digest v3.1 — Group Highlights + Wins

**Updated:** 2026-06-10
**Cron Job:** `b006812998df`
**Schedule:** 11:00 AM ET daily
**Delivery:** `telegram:-1003863540828` (HQ group)
**Replaced:** Old "Morning Brief + Yesterday's Closeout" format which ran stale hackathon context

## Purpose

Deliver Jordan a scannable daily digest showing what was discussed and what got done across all four Gentech groups. Only groups with activity appear. No fluff, no stale context.

## Data Sources — PROVEN ORDER

**Vault files are PRIMARY and most reliable. Always start here.**

| Priority | Source | Why | Speed |
|----------|--------|-----|-------|
| 1 | `Daily/YYYY-MM-DD.md` | richest summary — lists every topic, files created, decisions made | instant |
| 2 | `HQ/STATUS-BOARD.md` | active work, blockers, upcoming deadlines | instant |
| 3 | `HQ/jordan-queue.md` | items needing Jordan's action | instant |
| 4 | `Mess-Hall/sweep-report-YYYY-MM-DD.md` | vault cleanup, stale items flagged | instant |
| 5 | `find . -name "*.md" -mtime -1` | filesystem scan for all modified files | instant |
| 6 | `02-Labs/` hackathon folders | submission drafts, deploy guides, evaluations | instant |
| 7 | `AAE/` folder | integration assessments, outreach drafts | instant |
| 8 | session_search browse+scroll | conversation-level detail (supplement only) | slow |
| 9 | session_search by topic keywords | catch-all (includes cron noise) | slow |

**Why vault first:** session_search does NOT support Telegram group ID filtering. Browsing recent sessions returns mostly cron jobs. Vault files are written by nightly sweeps and daily notes — they capture everything that happened.

Group-to-topic mapping (for structuring output, NOT for querying session_search):

| Group | Chat ID | Topic |
|-------|---------|-------|
| HQ | `-1003863540828` | Coordination, decisions, blockers |
| Strategies | `-1002916759037` | Finance, DeFi, portfolio, yield |
| Labs | `-1003872552815` | Code, SDKs, smart contracts, dev |
| Entertainment | `-1003893562036` | Content, social media, hackathons |

## Output Format

```
☀️ **Daily Digest — [Yesterday's Date]**

**🏢 HQ (Coordination)**
• [topic or decision]
• [concrete action taken]

**📈 Strategies (Finance)**
• [topic]
• [outcome]

**🔬 Labs (Code)**
• [topic]
• [shipped or built]

**🎬 Entertainment (Content)**
• [topic]
• [completed]

**⚠️ Blockers**
• [blocker with age if known]

**⚙️ System:** [disk usage] | [uptime]
```

## Rules

1. **Only include groups with activity** — skip groups with no conversations yesterday
2. **Two bullets max per group** — "what we talked about" + "what got done"
3. **Concrete actions only** — don't summarize闲聊, focus on decisions and shipped work
4. **System health footer** — `df -h / | tail -1` and `uptime`
5. **No Steve Harvey voice** — clean, professional, scannable
6. **Jordan scans in 30 seconds** — bold group names, no paragraphs, only bullets
7. **Always include Blockers section** if any exist — this is actionable, not filler

## Proven Workflow (Step by Step)

### Step 1: Read yesterday's daily note
```bash
cat /root/vaults/gentech/Daily/$(date -d yesterday +%Y-%m-%d).md
```
This is the single richest source. It lists every topic discussed, files created, and decisions made. Parse into group buckets (HQ/Strategies/Labs/Entertainment).

### Step 2: Read status board + queue
```bash
cat /root/vaults/gentech/HQ/STATUS-BOARD.md
cat /root/vaults/gentech/HQ/jordan-queue.md
```
Cross-reference with daily note. Status board shows blockers and deadlines. Queue shows what needs Jordan.

### Step 3: Check for sweep report
```bash
cat /root/vaults/gentech/Mess-Hall/sweep-report-$(date -d yesterday +%Y-%m-%d).md
```
Sweep reports flag stale items, cross-file contradictions, and urgency markers.

### Step 4: Filesystem scan for all modified files
```bash
cd /root/vaults/gentech && find . -name "*.md" -mtime -1 -not -path "./.obsidian/*" | sort
```
Catches anything the daily note missed — hackathon drafts, AAE assessments, gaming updates.

### Step 5: Read key modified files
Based on the scan, read any files that look significant:
- `02-Labs/` → hackathon submissions, deploy guides, evaluations
- `AAE/` → integration assessments, partnership outreach
- `Green-Room/` → new ideas, completed research
- `Gaming/` → GenTech Power updates

### Step 6: session_search (supplement only)
If vault files are thin or you need conversation-level color:
```
session_search(sort="newest", limit=20)  # browse recent
session_search(session_id="...", window=10)  # scroll into telegram sessions
```
⚠️ Does NOT support group ID filtering. Returns mostly cron jobs. Use only as supplement.

### Step 7: Compile and deliver
Group findings into the output format. Bold group names. No paragraphs. Max 2 bullets per group. Include Blockers section and System health.

## Session Search Tips

**⚠️ Group-based filtering does NOT work.** `session_search(query="group:-1003863540828")` and `source:telegram group:-XXX` return zero results. Do not use these.

**Working approach — session_search with browse+scroll pattern:**

The most reliable method for pulling yesterday's group activity is a two-step process:

**Step 1: Browse recent sessions** — identifies which sessions exist and their source:
```
session_search(sort="newest", limit=20)
```
This returns session metadata: session_id, source (telegram/cron), timestamps, message_count, and a preview. Key patterns:
- **Telegram sessions**: session_id starts with `YYYYMMDD_HHMMSS_*` (e.g., `20260605_120058_8c2fd926`)
- **Cron sessions**: session_id starts with `cron_*_YYYYMMDD_HHMMSS`
- **Source field**: `"telegram"` = direct Jordan/team conversation, `"cron"` = automated job

**Step 2: Scroll into promising sessions** — read actual conversation content:
```
session_search(session_id="20260605_120058_8c2fd926", window=10)
```
This returns the actual messages. Scroll forward/backward by passing message IDs from the result as `around_message_id`.

**Step 3: Topic keyword search** — when browse doesn't surface everything:
```
session_search(query="Orbis x402", sort="newest", limit=5)
```
⚠️ Topic searches return ALL sessions matching the keyword (including cron jobs). Filter mentally for telegram-sourced ones.

**Fallback — vault files** (when session_search is empty or stale):

| Vault File | What It Contains | Path |
|------------|------------------|------|
| Daily note | Tasks, deadlines, blockers, recent activity | `Daily/YYYY-MM-DD.md` |
| Nightly sweep | Vault cleanup log, flagged items | `Mess-Hall/sweep-report-YYYY-MM-DD.md` |
| Status board | Active work, blockers, coming up | `HQ/STATUS-BOARD.md` |
| Jordan queue | Items needing Jordan's action | `HQ/jordan-queue.md` |
| Hackathon tracker | All hackathon status | `00-HQ/hackathon-tracker.md` |

**Four-tier fallback chain:**
1. **Vault files** (fastest, most structured) — daily note + sweep report + status board
2. **Filesystem scan** (`find . -name "*.md" -mtime -1`) — catches everything modified yesterday
3. **session_search browse+scroll** (for conversation detail) — browse recent, scroll into telegram sessions
4. **session_search by topic** (catch-all) — keyword searches across sessions (includes cron noise)
