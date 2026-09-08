---
name: gentech-daily-sync
description: Daily second brain sync — orchestrate, summarize, and archive cross-team activities for GenTech Labs. Silent-run capable (vault-only output).
ai_hint: Recurring Gentech orchestration pattern; vault topology-dependent
---

## Trigger

- Running daily sync as Gentech CEO/COO
- Compiling daily status from vault sources
- "Daily second brain sync" command
- End-of-day or start-of-day coordination roundup
- **Morning Digest v2.0** — cross-group conversation synthesis delivered to HQ at 7:00 AM ET. Pulls yesterday's conversations from ALL Telegram groups (HQ, Strategies, Labs, Entertainment). Saves full digest to `08-Daily-Digest/YYYY-MM/YYYY-MM-DD.md`. Includes Idea Incubator section at bottom. See `references/morning-digest-v2.md` for format.
- **DAILY DIGEST v3.1 — Group Highlights + Wins** — reworked May 31, 2026. Pulls yesterday's conversations from each Telegram group (HQ, Strategies, Labs, Entertainment) via `session_search`. Shows what was discussed and what got done per group. Only groups with activity appear. System health footer (disk + uptime). Delivered to HQ at 11 AM ET. Replaced the old "Morning Brief + Yesterday's Closeout" format which ran stale hackathon context. See `references/daily-digest-v3.md` for format.
- **Weekly Sunday Review** — cron-triggered 3-section review (brain sync + skills update + x402 ecosystem scan). Uses `delegate_task` with 3 parallel research subagents for the x402 scan. See `references/weekly-review-pattern.md` for format, data sources, and delegation pattern.
- **End-of-shift wrap-up for Jordan** — when explicit request for handoff summary with sections: Accomplishments, Pending Approvals, Active Discussions, Blocked Items, Tomorrow's Priorities
- **Pre-shift coordination for Jordan** — morning briefing before team starts work; focus on priorities, deadlines, decisions needed, and immediate action items. Sections: Sprint State, Today's Priorities, Hackathon Deadlines, Critical Decisions Needed, System Health Snapshot, Action Items — Immediate. Keep direct and skimmable; end with forward-looking hook.

## AI Behavior

Speaking style: Warm, mature, calm authority. Use "We're building" not "They're building". 2–3 sentences per thought. End with forward-looking hooks: "This is just the beginning…"

Tone: Visionary storyteller, deliberate cadence, big-picture focus.

Format: Markdown with YAML frontmatter; structured sections; concise bullet-heavy writing.

Routing: Delegate via department Telegram groups, not DMs. Use Green Room for cross-department handoffs.

## Process

1. **Identify date & week** — Get current date, compute ISO week number (W##), fetch vault year folder `11-Mess Hall/YYYY/`. If W## folder missing, create it.
2. **Create today's context folder** — Ensure `11-Mess Hall/YYYY/W##/YYYY-MM-DD/` exists before reading/writing any files.
3. **Scan for recent vault activity** — Use Python mtime scan across vault for files modified in last 24h. Exclude `.git/`, `tmp/`, `__pycache__/`, `node_modules/`, `.obsidian/`. Sort descending; include top 20 items in daily summary **OR** scan selective department folders (`02-Labs/`, `03-Strategies/`, `04-Entertainment/`, `09-Green Room/`) for targeted reads.
4. **Read yesterday's daily context** — Attempt to read `11-Mess Hall/YYYY/W##/YYYY-(previous-day)/today-context.md` for carry-forward items. If missing, try alternative files in the previous day's folder (e.g., `overnight-sprint-status.md`, `rotation-log-*.md`) — these often contain the same carry-forward signals. If still missing (weekend/holiday), scan backwards one day at a time until a context file is found or W##-1 week boundary reached.
5. **Read today's context (if exists)** — Open `11-Mess Hall/YYYY/W##/YYYY-MM-DD/today-context.md`. If missing, note "today-context not yet published" and proceed — it may be written later by Gentech or agents.
6. **Read rotation log (if exists)** — Open `11-Mess Hall/YYYY/W##/YYYY-MM-DD/rotation-log.md` for operations log. If absent, create with basic metadata (date, sync start).
7. **Pull active handoffs** — **Solo operation:** Handoffs are tracked inline in `today-context.md` Active Discussions table, not in separate files. Check `10-Archive/mess-hall-stale/handoff-board.md` for historical reference if needed. Scan `09-Green Room/WORKFLOW-ACTIVE.md` for coordination protocols.
8. **Read approval decisions** — Scan `00-HQ/Approvals/` (YYYY-MM-DD-*.md) plus `00-Inbox/approvals/` for active queues. If neither folder exists or both are empty, note "No pending approvals" — do not treat missing folders as an error. Use `search_files` or `os.walk` to discover actual contents.
9. **Read auto-updated DeFi trackers explicitly** — 
   - `09-Green Room/LP Scout — IL Tracker vs HODL & Stake.md` (LP snapshot + efficiency)
   - `09-Green Room/Defi-Strategy-Engine-Evolution.md` (milestone tracker state — renamed from D5→DeFi on May 7)
   - Also scan `09-Green Room/` for files matching `lp-status-*.md` and `defi-*.md`
10. **Read project updates by department** — Pull latest from:
    - `02-Labs/` (hackathon folders, Labs-Queue.md, R&D status)
    - `03-Strategies/` (research, competitive intel, strategy docs)
    - `04-Entertainment/` (content pipeline, dev-blog, social drafts)
    - `00-HQ/` (summaries, operations decisions)
11. **Compile structured report** — Build sections: TL;DR, Department Status Tables, Incidents (if any), Decisions (since last sync), Open Items (table format), Risks (Critical/Medium/Low), Week Status.
12. **Add forward hook** — End with "This is just the beginning…" trajectory paragraph.
13. **Write daily summary file** — Save to `11-Mess Hall/daily/YYYY-MM-DD-summary.md`. Include: date, week, sprint name, agent activity table (Dept/Agent/Status/Focus/Blockers), action items table, ideas/notes, links.
14. **Update working memory** — Patch `00-Working-Memory.md` to reflect current sprint status, incident resolution state, and handoff backlog. Use structured memory entry format (`## Memory Entry — YYYY-MM-DD (Agent)`).
15. **Commit to git** — Stage new/updated files under `11-Mess Hall/` and `00-Working-Memory.md`. Commit with message prefix `docs: daily sync — YYYY-MM-DD` followed by concise body (3-5 bullets). Keep commits atomic (daily sync only).
16. **Obsidian sync** — Run `cd /root/vaults/gentech && ob sync` if CLI available.
17. **Delivery mode** — Check the cron job instruction. If it says "your final response will be delivered to the user" or similar, produce a concise actionable summary as your final response — do NOT use `[SILENT]`. Only use `[SILENT]` when the cron job is configured for vault-only updates with no delivery. See `references/silent-run-protocol.md` for decision tree.

## Vault Paths (Current as of 2026-05-04)

- **Daily summary digest:** `11-Mess Hall/daily/YYYY-MM-DD-summary.md` (auto-curated, 7-day retention)
- **Daily context folder:** `11-Mess Hall/YYYY/W##/YYYY-MM-DD/` (per-ISO-week year-folders)
- **Mess Hall root:** `11-Mess Hall/` (contains `daily/`, `vault-audits/`, `2026/W##/` date folders, `considerations.md`, `archive/`. The legacy `handoff-board.md`, `task-board.md`, `agent-coordination-board.md` still exist at root but are **DEPRECATED** — stale data, not maintained in solo operation).
- **Green Room:** `09-Green Room/` (active handoffs, approvals, cross-group work-in-progress)
- **Active handoffs:** `09-Green Room/active-handoffs/` (YYYY-MM-DD-*.md files)
- **Approvals:** `00-HQ/Approvals/` and `00-Inbox/Approvals/` (pending decisions)
- **Project trackers:** `02-Labs/` for active builds and hackathons; `06-Content/` for social/draft content; `03-Strategies/` for research
- **HQ Operations:** `00-HQ/` (summaries, approvals, team manifest, workflow docs)
- **Working memory:** `00-Working-Memory.md` (single source of truth for sprint state and incident resolution)

**Note:** The legacy `08-Daily/` folder has been superseded by the `11-Mess Hall daily/` pattern. Weekly organization uses ISO week numbers under `11-Mess Hall/YYYY/W##/`. Daily files are NOT stored in date-named root folders; they live in the per-week date subfolders.

**Sources To Read**

**Daily continuity (in precedence order):**
- Today's context: `11-Mess Hall/YYYY/W##/YYYY-MM-DD/today-context.md` (primary briefing)
- Previous day's context: `11-Mess Hall/YYYY/W##/YYYY-(prev-day)/today-context.md` (carry-forward risks)
- **Considerations tracker**: `11-Mess Hall/considerations.md` (open action items with `[ ]` checkboxes, sectioned by topic — primary source for stale-item triage and blocker identification)
- ~~Active handoffs: `09-Green Room/active-handoffs/*YYYY-MM-DD*.md`~~ **(ARCHIVED — directory does not exist in solo operation)**
- ~~Coordination boards: `11-Mess Hall/handoff-board.md`, `11-Mess Hall/agent-coordination-board.md`, `11-Mess Hall/task-board.md`~~ — These still exist at root but are **DEPRECATED** (stale, not maintained). Handoff status is now inline in `today-context.md` Active Discussions table and tracked via `considerations.md` checkboxes
- Working memory: `00-Working-Memory.md` **(MAY NOT EXIST in solo operation — sprint state lives in today-context.md)**

**DeFi / LP trackers (signal sources):**
- LP monitoring: `09-Green Room/LP Scout — IL Tracker vs HODL & Stake.md` (IL, efficiency, fee metrics)
- DeFi milestone: `09-Green Room/DeFi-Strategy-Engine-Evolution.md` (milestone ladder, state machine)
- LP status snapshots: `09-Green Room/lp-status-*.md` (timestamped position files)
- DeFi analysis: `09-Green Room/defi-*.md` (cron bugs, consolidation memos)

**Departmental activity sources:**
- Labs (Dmob): `02-Labs/Labs-Queue.md`, `02-Labs/Hackathons/Active/`, `02-Labs/Swarms-Solana-Adapter.md`
- Strategies (YoYo): `03-Strategies/` (research, competitive intel, LP analysis)
- Entertainment (Desmond): `04-Entertainment/dev-blog/`, `06-Content/Queue/`, `06-Content/X-Drafts/`
- HQ / Jordan: `00-HQ/Summaries/`, `00-HQ/Approvals/`, `00-Inbox/Approval Queue.md`

**Recent vault changes (targeted scan):**
Prefer selective directory scan over full mtime sweep for speed and relevance:
```python
import os
from datetime import datetime, timedelta
cutoff = datetime.now() - timedelta(days=1)
target_roots = [
    '02-Labs', '03-Strategies', '04-Entertainment',
    '09-Green Room', '00-HQ', '00-Inbox', '11-Mess Hall'
]
recent = []
for root in target_roots:
    for dirpath, dirnames, filenames in os.walk(f'/root/vaults/gentech/{root}'):
        for f in filenames:
            if f.endswith('.md'):
                fp = os.path.join(dirpath, f)
                if datetime.fromtimestamp(os.path.getmtime(fp)) > cutoff:
                    recent.append(fp)
```
Or simpler: `git log --since='1 day ago' --oneline --all` for commit-driven insight.

**Verification sources:**
- Weekly reports: `08-Logs/2026-W##.md`
- Vault sweep logs: `08-Logs/vault-sweep-*.md`
- Session archives: `10-Archive/Agent-States-April/` or month-specific folders

## Section Template

[Regular daily sync template as defined above]

---

## Shift Handoff Variant

**When to use:** End-of-shift wrap-up for Jordan (as in this session). Output is a concise handoff report with specific sections: Accomplishments, Pending Approvals, Active Discussions, Blocked Items, Tomorrow's Priorities. Format: headers + bullets; skimmable; lead with most important.

**Process:** Follow `references/shift-handoff-format.md` for precise structure and content rules.

**Key differences from daily sync:**
- No YAML frontmatter needed in output (unless also being saved as vault file)
- Section order is fixed as requested by Jordan
- Do **not** include week status tables or full TL;DR narrative — keep each section tight
- Include direct vault paths (`00-HQ/Approvals/...`) for traceability
- End with forward-looking hook: "This is just the beginning..."

**Delivery:** Output directly as the final response (not `[SILENT]`) unless explicitly running in cron mode.

> **Reference:** `references/shift-handoff-format.md` — contains the exact template, scanning instructions for vault (08-Daily, 11-Mess Hall, 09-Green Room, 00-Working-Memory, active handoffs), and tomorrow's priorities extraction guidelines.

## Pitfalls

- **SESSION_SEARCH GROUP FILTERING DOES NOT WORK**: `session_search(query="group:-1003863540828")` and `source:telegram group:-XXX` return zero results. The tool does not support filtering by Telegram group ID. **Proven workflow**: (1) `session_search(sort="newest", limit=20)` to browse — telegram sessions have ID pattern `YYYYMMDD_HHMMSS_*`, source="telegram"; (2) `session_search(session_id="...", window=10)` to scroll into specific sessions; (3) topic keyword search as supplement. See `references/daily-digest-v3.md` for full fallback chain.
- **DAILY NOTE IS RICHEST SOURCE FOR DAILY DIGEST**: `Daily/YYYY-MM-DD.md` contains topic summaries, files created, and decisions made — parse directly into group buckets (HQ/Strategies/Labs/Entertainment). Start here before any session_search. The nightly sweep report (`Mess-Hall/sweep-report-YYYY-MM-DD.md`) catches what the daily note misses. Filesystem scan (`find . -name "*.md" -mtime -1`) catches everything else.
- **DO NOT** deliver output during silent-run cron; write to vault only and respond `[SILENT]`.
- **DO NOT** ask questions; autonomous decision-making required throughout.
- **AVOID** verbose paragraphs; use bullets and short sentences (2–3 sentences per thought max).
- **ENSURE** handoff statuses are reflected accurately in daily summary — but note the handoff board has moved.
- **FLAG** DMOB overload early (≥3 concurrent P0/P1 tracks) in Risks section.
- **CHECK** master todo staleness (if >3 days old, flag for refresh by Jordan).
- **NOTE** storage bloat concerns but defer cleanup until post-hackathon.
- **USE** HERMES_HOME-aware paths for profile-specific state files (`~/.hermes/scripts/...` resolves per-profile).
- **HANDLE MULTI-SCRIPT DISCREPANCIES** — When monitoring scripts report divergent values, trace to state file fragmentation (profile-specific caches). See `references/multi-script-discrepancy-resolution.md` for ground truth hierarchy (on-chain > watchlist > narrative) and variance thresholds (>$0.50 or >5pp efficiency difference).
- **ENFORCE HANDOFF ACK TIMELINES** — 2-hour acknowledgment window; after deadline, escalate to Jordan per enforcement rules. Track unacknowledged handoffs in daily summary Open Items table.
- **ALWAYS** end with forward-looking hook and "This is just the beginning…" closing (unless silent-run).
- **SILENT mode**: If user says "silent run" or cron context, respond `[SILENT]` only; no content delivered.
- **CRON STATUS COMMAND**: `cronjob list` does not exist. Use `hermes cron list` for cron job status checks. The hermes CLI outputs a formatted table with job IDs, schedules, last-run status, and next-run times.
- **GIT QUOTING**: `11-Mess Hall/` contains a space. Always quote paths in shell commands: `git add "11-Mess Hall/daily/..."`. Unquoted `git add 11-Mess Hall/...` silently fails to stage anything.
- **`ob sync` UNCONFIGURED**: Obsidian CLI sync is not set up for the gentech vault (`No sync configuration found`). Step 16 should be skipped or run `ob sync-setup` first. Do not treat sync failure as blocking.
- **WEEK-ROLLOVER EDGE CASE**: On first daily sync of a new ISO week (typically Monday ~03:00 UTC), the `11-Mess Hall/YYYY/W##/` folder may not exist yet. Create it before attempting to write `today-context.md`. Week number from `datetime.isocalendar()`.
- **VAULT STRUCTURE ASSUMPTION GUARD**: Do NOT hardcode `08-Daily/` as write target — that path is legacy (renamed to `08-Logs/`). Current daily summary location is `11-Mess Hall/daily/YYYY-MM-DD-summary.md`. Context files belong under `11-Mess Hall/YYYY/W##/YYYY-MM-DD/`. If either path structure is missing, create it.
- **PORTFOLIO/CONTENT TRACKER SWAP**: The DeFi/LP trackers formerly lived in `03-Projects/DeFi/`; they now reside in `09-Green Room/` with prefixed filenames (`LP Scout — ...`, `Defi-Strategy-Engine-Evolution.md`). Scan `09-Green Room/` for `lp-status-*.md` and `defi-*.md` patterns instead. Note: D5→DeFi rename completed May 7; script filenames (`defi-master-cron.py`) kept as-is for cron compatibility.
- **SAME-DAY RE-SYNC**: When a second sync runs on the same day (common with cron), the daily summary file (`11-Mess Hall/daily/YYYY-MM-DD-summary.md`) already exists. **Update it** — do NOT create a second file or overwrite with only the delta. Read the existing summary, merge new data (fresh LP snapshots, new handoffs, updated blockers), and write the complete updated file.
- **LP OUT-OF-RANGE = IMMEDIATE FLAG**: When reading LP tracker data, if price is outside the position range, this is a CRITICAL finding — flag it as the #1 item for Jordan, above all other priorities. Zero fee accrual means real money lost every hour. Include: current price, range bounds, recommended new range (±3% around current price), and the fact that position is likely one-sided. Do not bury this in the body — lead with it.
- **APPROVAL QUEUE MAY NOT EXIST**: `00-HQ/Approvals/` and `00-Inbox/approvals/` are referenced as standard paths but may be empty or have only stale items. Use `search_files` or `os.walk` to check. If empty or all resolved, note "No pending approvals" — don't treat stale approvals as active items.
- **STALE ITEM SCANNING**: When asked to check for stale items (>48h), use Python mtime scan across the target directory. Only one stale item is common — don't expect large lists. Report with file path, age in days, and what action is needed.
- **CRON DELIVERY vs SILENT-RUN**: The skill's default is `[SILENT]` for cron. But some cron jobs are configured to deliver output to Jordan. Check the cron job's instruction text — if it mentions delivery, produce output. The `[SILENT]` rule applies only to vault-only background syncs.
- **WEEKLY REVIEW CRON PATH MISMATCH**: The cron job prompt says "Review /root/vaults/gentech/08-Daily/" but `08-Daily/`, `Daily/`, `11-Mess Hall/daily/`, `00-Working-Memory.md`, and `11-Mess Hall/considerations.md` **don't exist** in the current vault structure. The git log (`git log --since='7 days ago' --oneline --all`) is the primary signal source, not directory scans. Ideas live in `11-Mess Hall/ideas.md`. Completed reviews save to `11-Mess Hall/YYYY/W##/YYYY-MM-DD-weekly-review.md`. See `references/weekly-review-pattern.md` for the corrected section-1 data sources.
- **SOLO OPERATION — DEPRECATED COORDINATION BOARDS**: Since the solo operation restructure (May 2026), `01-Agency/` is archived. The handoff board, coordination board, and task board **still exist at Mess Hall root** but are deprecated — they contain stale data (27–29 days overdue) and are not maintained. Do NOT treat them as active trackers. `09-Green Room/active-handoffs/` directory does not exist in solo operation. Handoff tracking is inline in `today-context.md` Active Discussions table.
- **`00-Working-Memory.md` MAY NOT EXIST**: This file was part of the multi-agent era. In solo operation, sprint state lives in `today-context.md` and `rotation-log-*.md`. Don't treat a missing working memory file as an error.
- **`considerations.md` STALENESS CHECK**: The file `11-Mess Hall/considerations.md` uses `[ ]` checkbox syntax under `## Topic` section headers. The file's mtime reflects the last edit to ANY item, not individual item age. To determine if a specific checkbox item is stale, check when it was first added (section header date or prior rotation logs), not the file mtime. Items with no resolution after 5+ days should be flagged as stale.
- **CONTEXT CAP BEFORE DAILY RESET**: Hermes context resets around 11:30 AM-12:00 PM UTC daily. When conversations are active late in the day and approaching context limits, save a `_cap.md` file to `08-Daily-Digest/YYYY-MM/` with a brief summary of the day's conversations. Morning Digest v2.0 reads this as fallback if `session_search` returns incomplete results. Without a cap, yesterday's side conversations and ideas may be lost to context truncation.
- **MORNING DIGEST v2.0 IDEA INCUBATOR**: The Morning Digest is no longer a passive summary. The bottom section must actively synthesize yesterday's conversations, suggest connections between topics, and prompt Jordan with 2-3 specific questions or next steps. Green Room / Mess Hall are consolidated into this as the active idea space. Do not just summarize — advance the ideas.
- **MORNING DIGEST VAULT PATH**: v2.0 saves to `08-Daily-Digest/YYYY-MM/YYYY-MM-DD.md` (month-organized), NOT `11-Mess Hall/daily/YYYY-MM-DD-summary.md` (legacy). Both paths may exist — the new digest is the active one for cross-group conversation synthesis.

## Support Files

This skill bundles:
- `references/daily-sync-vault-map.md` — Full vault topology diagram
- `references/silent-run-protocol.md` — Cron delivery decision tree: when to use [SILENT] vs deliver output
- `references/multi-script-discrepancy-resolution.md` — State file fragmentation detection, ground truth hierarchy, variance thresholds, follow-up task template
- `references/shift-handoff-format.md` — End-of-shift handoff template
- `references/shift-handoff-checklist.md` — Handoff scanning checklist
- `references/pre-shift-coordination-format.md` — Morning briefing template
- `references/morning-digest-v2.md` — Morning Digest v2.0 format: cross-group synthesis, Idea Incubator, context cap rules
- `templates/daily-sync-frontmatter.md` — YAML frontmatter starter template
- `scripts/scan-recent-vault-files.sh` — Bash one-liner to list recent vault changes
- `scripts/get-current-week.sh` — Compute week number and W## path
- `scripts/verify-daily-sync.sh` — Post-write validation checks
- `references/eod-vault-scanning-pattern.md` — Proven vault scan order for end-of-day wrap-ups (targeted dirs, anti-patterns, section format)

See skill files under `~/.hermes/profiles/gentech/skills/gentech-daily-sync/` for details.

**Support Files (new):**
- `references/daily-digest-v3.md` — Daily Digest v3.0 format: closeout + morning brief + system health, data sources, session search tips.
- `references/x402-ecosystem-snapshot-2026-06.md` — x402 ecosystem baseline: key players, Circle Agent Stack, WURK.FUN, scale metrics. Update each weekly scan.
- `references/x402-ecosystem-snapshot-2026-07.md` — July 2026 update: Foundation move, SDK expansion (SVM, Stellar, paywall), 1,879 GitHub repos, 10.5M+ AIsa transactions, production deployment explosion.
