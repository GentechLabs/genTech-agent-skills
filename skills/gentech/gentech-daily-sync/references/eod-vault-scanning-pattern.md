# End-of-Day Wrap-Up — Vault Scanning Pattern

When producing an end-of-day handoff for Jordan, use this scanning order for maximum signal with minimum noise.

## Scan Order (Priority)

### 1. Today's Build Logs
`09-Green Room/build-logs/2026-05-*.md`
These contain the actual shipped work. Read files modified today to identify completed builds and in-progress projects with status markers (e.g. "~75% complete").

### 2. Contest/Hackathon Scans
`02-Labs/Contest-Scans/summary_YYYY-MM-DD.md`
Contains the day's qualified opportunities, prize pools, and deadlines. Quick signal for pipeline health.

### 3. Vault Sweep
`11-Mess Hall/vault-audits/vault-sweep-YYYY-MM-DD.md`
Reports sync status, stale artifacts, orphaned files, and actionable items.

### 4. Active Ideas
`09-Green Room/ideas.md`
Check for newly added ideas (unchecked boxes with recent timestamps).

### 5. Blockers Tracker
`11-Mess Hall/considerations.md`
Checkbox list of open decisions and blockers. Sectioned by topic. The file mtime reflects last edit to ANY item, not individual item age.

### 6. Sprint/Task Board
`11-Mess Hall/task-board.md`
Active sprint status, hackathon deadlines, completed builds, and department assignments.

### 7. Today's Context
`11-Mess Hall/YYYY/W##/YYYY-MM-DD/today-context.md`
Active Discussions table, Open Action Items, Resolved items.

### 8. Session History
`session_search` with topic-specific queries (hackathon, defi monitoring, content).
Look for cron job sessions and direct Telegram conversations from today.

## Anti-Patterns

- **Don't scan `09-Green Room/active-handoffs/`** — this directory doesn't exist in solo operation.
- **Don't treat `11-Mess Hall/task-board.md` as gospel** — it may be stale (last updated during multi-agent era). Cross-reference with actual file modifications.
- **Don't assume `00-Working-Memory.md` exists** — sprint state lives in `today-context.md` now.
- **Don't scan all 3,600+ vault files** — use targeted directory scans (build-logs, contest-scans, vault-audits, today's context folder).
- **Don't include resolved items in the blockers section** — check the "Resolved" section of `today-context.md` to avoid reporting old problems.

## Section Order (Jordan's Preferred Format)

1. What Got Done (builds shipped, research completed, content produced)
2. Still In Progress (active work, % complete, what's remaining)
3. Blockers & Decisions Needed (categorized, direct action asks)
4. Tomorrow's Priorities (deadline-driven, sorted by urgency)

Keep it warm and concise. 2-3 sentences per thought. End with a forward-looking hook.
