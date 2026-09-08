# Build Queue Consolidation — July 12, 2026

## The Problem
Jordan noticed Forge wasn't seeing build queue items. Investigation revealed **7 stale markdown files** across 4 locations, all out of sync. The V4 Build Queue Tick cron was erroring silently every 30 minutes (FileNotFoundError on missing JSON).

## The Fix

### 1. Created Canonical JSON Queue
`scripts/build_queue.json` with 23 items, each carrying:
- `id`, `name`, `difficulty`, `priority`, `status`
- `assigned_to` — gentech | forge | jordan | auto
- `platform` — cloud | desktop | either | any (routes to correct agent)
- `needs_jordan` — bool
- `blocked_on` — optional dependency ID
- `deadline` — optional ISO date

### 2. Fixed the Tick Script
`build_queue_tick.py` was crashing on missing JSON. Rewrote it to:
- Exit with clear error on missing/corrupt queue (no silent crashes)
- Generate **Forge task handoff** → `Gentech/handoffs/gentech-to-forge/<date>-forge-tasks.md`
- Generate **Jordan action items** → `Gentech/handoffs/gentech-to-forge/<date>-jordan-items.md`
- Print structured summary (counts by agent, platform, urgent deadlines)
- Stdout captured by cron, fed to Nightly Build Session via `context_from`

### 3. Updated Nightly Build Session
Midnight ET cron updated to:
- Read tick stdout via `context_from`
- Work cloud items (Gentech's lane)
- Generate Morning Digest source

### 4. Updated Morning Digest
8 AM ET cron updated to:
- Read nightly session output via `context_from`
- Read latest handoff files for Forge tasks + Jordan items
- Deliver overnight report to HQ

### 5. Stamped All Stale Copies
7 files across vault/ProtoJay4789/repos/portfolio all got deprecation banners.

### 6. Context Chaining
```
Tick (every 30m, no_agent)
  → stdout → context_from →
Nightly Build Session (midnight, LLM)
  → stdout → context_from →
Morning Digest (8 AM, LLM)
  → delivers to HQ
```

## Files Changed
| File | Change |
|------|--------|
| `scripts/build_queue.json` | **NEW** — canonical queue, 23 items |
| `scripts/build_queue_tick.py` | **REWRITTEN** — added handoff generation, error handling |
| `scripts/gentech-queue-remote.json` | **DELETED Jul 15** — stale duplicate that survived first sweep (JSON format, not markdown, so `find` by `build-queue*` / `build_queue*` glob missed it) |
| `Gentech/handoffs/gentech-to-forge/2026-07-11-forge-handoff.md` | **STAMPED** with deprecation redirect |
| `Gentech/00-HQ/build-queue.md` | **STAMPED** deprecated |
| `10-Labs/build-queue.md` | **STAMPED** deprecated |
| `ProtoJay4789.github.io/Gentech/00-HQ/build-queue.md` | **STAMPED** deprecated |
| `ProtoJay4789.github.io/10-Labs/build-queue.md` | **STAMPED** deprecated |
| `repos/ProtoJay4789.github.io/Gentech/00-HQ/build-queue.md` | **STAMPED** deprecated |
| `repos/ProtoJay4789.github.io/10-Labs/build-queue.md` | **STAMPED** deprecated |
| `portfolio/10-Labs/build-queue.md` | **STAMPED** deprecated |
| Nightly Build Session cron | **UPDATED** — reads tick via context_from |
| Morning Digest cron | **UPDATED** — reads nightly via context_from |

## Future Maintenance
- The tick script runs every 30 min — if it ever errors, check `build_queue.json` exists and is valid JSON
- When adding new items, ONLY edit `scripts/build_queue.json` — never create a new markdown queue
- If you discover another stale queue file, stamp it with the deprecation banner
- Run the audit: `find /root -name "build-queue*" -o -name "build_queue*" 2>/dev/null | sort`
