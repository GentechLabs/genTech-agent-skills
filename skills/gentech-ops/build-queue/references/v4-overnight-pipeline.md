# V4 Overnight Pipeline — Nightly Build Session + Morning Digest

> Part of the `build-queue` skill suite.
> Updated Jul 10, 2026 — Replaced no_agent scripts with agent-driven jobs.

---

## Core Philosophy

**Night work is silent work.** Jordan is asleep. No notifications, no Telegram pings. The agent works through the build queue, logs everything to the vault, and only reports in the morning digest.

**Quiet hours** means "don't send notifications to Jordan while he's asleep" — NOT "stop working." The old quiet-hours gate on cron jobs that blocked builds has been removed from the Build Queue job. It still applies to jobs that would spam Jordan overnight (market alerts, social posts, etc.).

---

## Pipeline Timeline (ET) — Jul 2026

| Time (ET) | Job | Type | What It Does | Silent? |
|-----------|-----|------|-------------|---------|
| **Every 30m** | **Build Queue Tick** | `no_agent` script | Scan queue → generate Forge task list + Jordan items → print summary | ✅ Silent |
| **12:00 AM** | **Nightly Build Session** | LLM agent (gets tick output via context_from) | Read handoff files → work cloud items → update queue → log to vault | ✅ Silent |
| **12:00 AM** | V4 Nightly Maintenance | `no_agent` script | Git pull/add/commit/push vault | ✅ Silent |
| **8:00 AM** | **Morning Digest** | LLM agent (gets night session output via context_from) | Read night session output + handoff files → deliver to HQ | 📬 Delivers |

### Context Chain
```
Build Queue Tick (stdout)
  → context_from: injected into ↓
Nightly Build Session (reads handoff files, works cloud queue items, outputs overnight log)
  → context_from: injected into ↓
Morning Digest (reads handoff files + nightly log, delivers to HQ Telegram)
```

This ensures the nightly session automatically knows queue state without re-reading JSON, and the morning digest knows what was shipped overnight. No data lost between chained jobs.

## Handoff Files

Every 30 minutes the tick script generates two documents in `Gentech/handoffs/gentech-to-forge/`:

**`<date>-forge-tasks.md`** — Forge's actionable task list:
- All desktop/GPU items assigned to Forge
- Priority-sorted with difficulty and descriptions
- Ready vs blocked items clearly marked
- Self-serve instructions for independent work

**`<date>-jordan-items.md`** — Jordan's action items:
- Items needing signup, auth, wallet, or decision
- Clean bullets scannable during a work break

---

## Nightly Build Session

**Schedule:** `0 4 * * *` (4:00 AM UTC = midnight ET)
**Delivery:** `local` (completely silent)
**No quiet-hours gate** — quiet hours blocks notifications, not build work.

### Workflow

1. Read `/root/vaults/gentech/scripts/build_queue.json`
2. Focus on items with `assigned_to: "gentech"` and `status` not in `["shipped", "blocked", "cancelled"]`
3. Skip items `assigned_to: "forge"` and `assigned_to: "jordan"`
4. Per item: **develop → verify → ship** (see `build-queue-processor` skill)
5. **Before each item:** log plan to `11-Mess Hall/nightly-build-log.md`
6. **After each item:** log results, blockers, Jordan needs
7. If blocked by Jordan decision, add to "Jordan Needs" list, move to next item
8. At stopping point: write final summary

### Build Log Format

```markdown
# Nightly Build Log — July 10, 2026

## Phase: Developing Deal Tracker
Started: 00:05 ET
Plan: Add 5 new stores to price comparison

## Phase: Testing
All 12 tests green ✅

## Phase: Verifying
GLM-5.2 audit: 2 minor issues fixed
Status: → shipped

## Blocked: Agent Registration API
Needs Jordan → Decide pricing tier

## Summary
2 items: 1 shipped, 1 blocked, 1 awaiting Jordan
```

---

## Morning Digest

**Schedule:** `0 12 * * *` (12:00 PM UTC = 8:00 AM ET)
**Delivery:** Telegram HQ
**Type:** LLM agent (not no_agent script)

### What it does:
1. Reads `nightly-build-log.md` (if exists)
2. Reads `build_queue.json`
3. Generates digest: Overnight Summary, Jordan Needs, Forge's Next Up, Deadlines Today

### Output format:
```
🌙 Overnight Summary
• Deal Tracker — shipped (12/12 tests)
• Agent Registration API — blocked (needs pricing)

📋 Jordan Needs
• Agent Registration API — set pricing tier
• Pika Subscription — sign up by Jul 14

🔧 Forge's Next Up
• SCN Outreach — fork repo, open Issue/PR

⏰ Deadlines Today
• Jul 10 — Sourcegraph essay due
```

If nothing happened: `Nothing was built overnight — first session starts tonight.`

---

## Pitfalls

- **Scheduling is UTC, timezone is ET** — Midnight ET = 4:00 AM UTC (EDT). Cron schedules in UTC.
- **Nightly Build Session is silent** — `deliver: local` = no Telegram. Only Morning Digest sends.
- **Morning Digest is an LLM agent** — Not a no_agent script. Reads nightly-build-log.md and generates a contextual report.
- **Build log is a rolling log** — One file per night. Morning digest reads it, next night overwrites.
- **Quiet hours philosophy** — Blocks NOTIFICATIONS to Jordan, not work. Build work ignores quiet hours. Market alerts still respect them.
- **Nightly maintenance + night build same time** — Maintenance is fast no_agent (~seconds). Build session runs after. No conflict.
