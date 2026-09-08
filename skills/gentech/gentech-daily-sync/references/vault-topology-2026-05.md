# Vault Topology — GenTech Labs (as of 2026-05-13)

**Scope:** Daily second brain sync routing — where files actually live.

## Quick Map (Daily Sync视线)

| What | Where | Notes |
|------|-------|-------|
| Daily summary digest | `11-Mess Hall/daily/YYYY-MM-DD-summary.md` | Auto-curated, 7-day retention |
| Daily context folder | `11-Mess Hall/YYYY/W##/YYYY-MM-DD/` | ISO week layout; contains `today-context.md` |
| Working memory | `00-Working-Memory.md` | **MAY NOT EXIST** — sprint state lives in today-context.md |
| ~~Active handoffs~~ | ~~`09-Green Room/active-handoffs/`~~ | **ARCHIVED** to `10-Archive/green-room-stale/` |
| ~~All handoffs board~~ | ~~`11-Mess Hall/handoff-board.md`~~ | **ARCHIVED** to `10-Archive/mess-hall-stale/` |
| ~~Coordination board~~ | ~~`11-Mess Hall/agent-coordination-board.md`~~ | **ARCHIVED** to `10-Archive/mess-hall-stale/` |
| ~~Task board~~ | ~~`11-Mess Hall/task-board.md`~~ | **ARCHIVED** to `10-Archive/mess-hall-stale/` |
| DeFi LP tracker | `09-Green Room/LP Scout — IL Tracker vs HODL & Stake.md` | Primary LP signal (IL, efficiency, fees) |
| DeFi milestone | `09-Green Room/Defi-Strategy-Engine-Evolution.md` | Milestone ladder + state machine |
| LP snapshots | `09-Green Room/lp-status-*.md` | Timestamped position captures |
| DeFi analysis | `09-Green Room/defi-*.md` | Cron bugs, consolidation memos |
| Labs queue | `02-Labs/Labs-Queue.md` | Dmob's active task list |
| Hackathons active | `02-Labs/Hackathons/Active/` | Current hackathon folders |
| Swarms adapter | `02-Labs/Swarms-Solana-Adapter.md` | Build status, gaps |
| Content queue | `06-Content/Queue/CONTENT-QUEUE.md` | Desmond's pending content |
| X drafts | `06-Content/X-Drafts/` | Unpublished social posts |
| Research | `03-Strategies/` | YoYo's competitive intel, research |
| Dev blog | `04-Entertainment/dev-blog/` | Long-form posts |
| Weekly summaries | `08-Logs/2026-W##.md` | Week rollups |
| HQ summaries | `00-HQ/Summaries/` | Jordan-curated summaries |
| Considerations | `11-Mess Hall/considerations.md` | Decisions to make (active) |
| Ideas | `09-Green Room/ideas.md` | Active ideas (hackathons, revenue, content) |
| Workflow | `09-Green Room/WORKFLOW-ACTIVE.md` | Solo operation protocol |

## Solo Operation Changes (May 2026)

The multi-agent coordination layer has been archived. In solo operation:
- **No active-handoffs directory** — handoffs tracked inline in `today-context.md`
- **No coordination board** — Gentech IS the coordinator
- **No task board** — sprint state lives in today-context.md
- **Handoff board archived** — historical reference only at `10-Archive/mess-hall-stale/handoff-board.md`
- **Agent check-in table removed** — DMOB, YoYo, Desmond deploy only when Jordan activates them

## Legacy Paths (DO NOT USE)

| Old Path | Status | Replacement |
|----------|--------|-------------|
| `08-Daily/` | ❌ Deprecated → renamed to `08-Logs/` | Use `11-Mess Hall/daily/` |
| `03-Projects/DeFi/` | ❌ Moved to `09-Green Room/` | Use `09-Green Room/(LP Scout\|DeFi-Strategy-Engine-Evolution).md` |
| `01-Agency/` | ❌ Archived to `10-Archive/multi-agent-era/` | Solo operation — no multi-agent coordination |
| `09-Green Room/active-handoffs/` | ❌ Archived to `10-Archive/green-room-stale/` | Track handoffs inline in today-context.md |
| `11-Mess Hall/handoff-board.md` | ❌ Archived to `10-Archive/mess-hall-stale/` | Track handoffs inline in today-context.md |
| `11-Mess Hall/agent-coordination-board.md` | ❌ Archived to `10-Archive/mess-hall-stale/` | Not needed — Gentech IS the coordinator |
| `11-Mess Hall/task-board.md` | ❌ Archived to `10-Archive/mess-hall-stale/` | Sprint state lives in today-context.md |
| `00-Working-Memory.md` | ❌ May not exist | Sprint state lives in today-context.md |

## Week Folder Convention

Vault uses **ISO week numbers** (W01–W53) under year folders:

```
11-Mess Hall/
├── daily/                          # Global daily summary files (not per-week)
│   ├── 2026-05-02-summary.md
│   ├── 2026-05-03-summary.md
│   └── 2026-05-04-summary.md
└── 2026/
    ├── W16/                        # Apr 16–19, 2026
    ├── W17/                        # Apr 20–26, 2026
    ├── W18/                        # Apr 27 – May 3, 2026
    ├── W19/                        # May 4–9, 2026
    └── W20/                        # May 10–16, 2026  ← CURRENT
        ├── 2026-05-10/
        ├── 2026-05-11/
        ├── 2026-05-12/
        └── 2026-05-13/
```

**Why per-week folders?** Enables clean archiving, week-based rollups, and avoids root-level filename collisions across years.

## Discovery Notes (2026-05-13)

- **Solo operation restructure complete** — Multi-agent coordination boards archived to `10-Archive/mess-hall-stale/`
- Handoff tracking is now inline in `today-context.md` — no separate board files
- `00-HQ/Approvals/` has 5 stale resolved items (Apr 27-May 2) — needs archiving
- `09-Green Room/` contains 2 stale discussions (agent platforms, BirdeyeBIP) with no responses
- `ob sync` still not configured — brain backup not running
- Vault git has periodic uncommitted changes — commit after each sweep

**Future-proofing:** If vault structure changes again, check `INDEX.md` at vault root for canonical folder map and `11-Mess Hall/README.md` for Mess Hall organization guide.