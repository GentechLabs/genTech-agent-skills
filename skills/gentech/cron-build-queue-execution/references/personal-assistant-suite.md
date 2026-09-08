# Personal Assistant Suite — the single reporting layer (Aug 25, 2026)

Jordan consolidated all "report-to-Jordan" cron summaries into ONE recurring assistant. This is the durable architecture; it supersedes the older assumption that the Morning/EOD digest, Revenue Monitor, Opportunity Scanner, and Marketplace scouts each post their own standalone message to HQ.

## The PA Suite
- Job `ac736cacf5e5`, **3x daily (8:00 / 14:00 / 20:00 UTC)** + a Monday weekly-planner beat.
- Delivers to HQ (`telegram:-1003863540828`).
- **Blockers-first**: the highest-signal item surfaces at the TOP of every run.
- **Progress-delta from handoffs**: reads `01-HANDOFFS/` completion files + inbound lanes + git log, reports what shipped since the last run ("progress updates as they happen").
- **Context**: pulls via `context_from` from the silent collectors.
- Always reads BOTH `HQ/jordan-queue.md` (human actions) and `HQ/pr-queue.md` (GitHub/PR work) — surfaces only what needs Jordan's hand from the PR queue; otherwise one line "running autonomously".

## Folded / retired (no longer standalone messages)
- **End-of-Day Digest (23:00)** → PAUSED (retired); PA 8pm owns the day-wrap.
- **Revenue Monitor, Opportunity Scanner, API Marketplace Scout, Agent-Market Momentum** → `deliver: local` (silent collectors) feeding the PA via context.

## New collector
- **Grant & Gated-Opportunity Deadline Tracker** (`e152f82238f8`, Mon+Thu 9am, `deliver: local`): reads jordan-queue + `09-Green Room/` for recorded deadlines, flags 🔴 due≤7d / ⏰ ≤30d / ❌ missed, writes `cron/output/grant-deadlines.md`, feeds the PA Monday planner. Guard against the "too tight, dropped" loss pattern (Gemini-XPRIZE / Delphi / CockroachDB).

## Stays separate (do NOT wrap in PA)
- Autonomous **workers** (builds, GitHub scheduler, overnight builds).
- **Infra watchdogs/monitors** (port, memory, rate-limit, vault health).
- **handoff-watcher** — kept as the real-time alert (ONCE per new handoff); the PA gives the daily consolidated view.

## Decision rule for any reporting cron
1. Summary the PA should own? → fold into PA `context_from` + set standalone to `local`.
2. Real-time infra/blocker alert? → keep direct.
3. Collector? → silent (`local`) + wire into the PA's `context_from`.

Result: one daily voice (3 beats), no double-summaries.
