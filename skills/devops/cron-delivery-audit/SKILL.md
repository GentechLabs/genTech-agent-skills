---
name: cron-delivery-audit
description: Audit and fix cron job delivery targets to ensure jobs deliver to connected channels or origin, preventing silent failures when targeting disconnected Telegram groups.
tags: [cron, hermes, telegram, delivery, audit, ops]
related_skills: []
triggers:
  - Creating or updating cron jobs
  - Cron jobs not appearing in groups
  - Troubleshooting missing cron output
  - Setting up new Telegram groups for Hermes
---

# Cron Delivery Audit

Systematic approach to ensure Hermes cron jobs deliver correctly and don't collide with each other.

## The Real Problem

Hermes cron jobs deliver through the Telegram gateway — **all groups the user belongs to are reachable**. The old model of "only HOME_CHANNEL is connected" was outdated once the gateway matured. The actual failure modes are:

- **Wrong delivery target** — typos in chat IDs
- **Time collision** — multiple jobs hitting the same group at the same minute
- **Job never ran** — script error, not delivery issue
- **Empty output** — script ran but produced nothing

## Delivery Target Reference

| Target | When to Use |
|--------|-------------|
| `origin` | Default — delivers to the chat where the job was created. Safe choice for single-user. |
| `local` | Internal maintenance only (vault sync, health checks). No Telegram delivery. |
| `telegram:-1003863540828` | HQ — coordination, decisions, status reports |
| `telegram:-1003893562036` | Entertainment — games, deals, social content, Vanito |
| `telegram:-1002916759037` | **Treasury** — finance, DeFi, portfolio, yield, market signals (renamed from "Strategies" Sep 7, 2026; chat ID unchanged) |
| `telegram:-1003872552815` | Labs — code, SDKs, technical output |

**All groups are reachable.** If output isn't appearing, check `last_status` first — the job may have errored before delivery.

## Multi-User Staggering

When multiple users have cron jobs targeting the same group:

| Risk | Scenario | Fix |
|------|----------|-----|
| **Same time collision** | Two jobs fire at :00 to same group | Move one to :00, the other to :15 |
| **Cross-user overlap** | Jordan + Vanito both at 12:00 Wed | Stagger by 1+ hour |
| **Same-user pileup** | Two Vanito jobs at 13:00 Wed | Offset by 15 min |

**GenTech convention (established Jul 2026):**
- Jordan's shop jobs → Wed 12:00
- Vanito's Game Release Intel → Sun/Wed 13:00
- Vanito's Weekly Sales Sweep → Wed 13:15 (staggered by 15 min)
- Name jobs with user prefix: `[Jordan]` / `[Vanito]`

## Audit Checklist

### Step 0: Verify Script Paths in Job Prompts (Agent-Executed Jobs)

Agent-executed cron jobs (`no_agent: false`) follow a natural-language `prompt` that may reference a script path. If the path is wrong, the agent fails before starting — the job reports `last_status: ok` (the agent ran OK) but the actual work never happened.

**Check for stale paths in prompts:**
```bash
hermes cron list | grep -i "script location\|\.sh\|\.py\|/root/" | grep -E "^[[:space:]]*[A-Za-z0-9_/:\.-]+"
```

**Verify each referenced file exists:**
```bash
ls -la /root/.hermes/profiles/gentech/scripts/  # former default location
ls -la /root/my-music/                           # music sync location
ls -la /root/repos/hermes-brain/scripts/          # backup location
```

**Common stale path patterns:**
- `.sh` wrapper that was replaced by a Python script (prompt never updated)
- Path references `/root/.hermes/scripts/` but script moved to a project directory
- Script was renamed or deleted but prompt still references old name
- Path was typed manually and contains a typo

**Fix pattern:** Find the actual script, then update the prompt:
```bash
cronjob action=update job_id=<id> prompt="...actual script path..."
```

**Pitfall:** The job shows `last_status: ok` even when the path is bad, because the agent ran its full lifecycle (looked for file, didn't find it, returned a no-op result). This makes stale path errors invisible on the cron dashboard. Check agent logs for `No such file or directory` when status is `ok` but expected output is missing:

```bash
grep "vanito-music-sync\|No such file" /root/.hermes/profiles/gentech/logs/agent.log
```

### Step 1: List All Jobs with Schedules + Deliveries

```bash
hermes cron list | grep -E "name:|schedule:|deliver:|last_status:"
```

### Step 2: Check for Time Collisions

Scan for jobs with identical cron expressions targeting the same group. Common collision patterns:
- Same user, two jobs at the same HH:00 (offset by 15 min)
- Different users, same HH:00 (stagger by 1 hr)

### Step 3: Verify Names Are Clear

Jobs should be self-explanatory in the group feed. Prefix with user name:
- `[Jordan] GenTech Shop — Weekly Sales Sweep` ✅
- `Sales Sweep` ❌ — whose?

## Fix Patterns

**Update delivery target:**
```bash
cronjob action=update job_id=<id> deliver=telegram:-1003893562036
```

**Stagger by changing schedule:**
```bash
cronjob action=update job_id=<id> schedule="15 13 * * 3"
```
(`15 13 * * 3` = Wednesday at 1:15 PM)

**Rename for clarity:**
```bash
cronjob action=update job_id=<id> name="[Jordan] GenTech Shop — Weekly Sales Sweep"
```

## Common Job Types and Recommended Delivery

| Job Type | Recommended | Why |
|----------|-------------|-----|
| Single-user content (deals, intel) | Per-topic group or `origin` | Lands where user will see it |
| Team-wide updates (Daily Digest) | HQ (`-1003863540828`) | Everyone sees it |
| Internal maintenance | `local` | No delivery needed |
| Vanito-specific content | Entertainment (`-1003893562036`) | Kept separate from Jordan's ops |

## Group Rename Propagation (Strategies → Treasury, Sep 7 2026)

When a Telegram group is renamed (the ID does not change), a full-propagation audit must verify no config/documentation still carries the old label — the gateway keeps working because delivery is by chat ID, but docs, skill notes, and prompts go stale silently. Sweep order for a group rename:
1. **Channel directory** — the gateway's `channel_directory.json` renames the main entry automatically (the `<id>:<topic>` suffixed entries keep old names; those are historical topic labels — inert, do not edit).
2. **config.yaml** — `telegram.channel_prompts` entry for the chat ID (prompt wording may still say the old name). Update the label so the agent's opening framing matches.
3. **Live cron jobs** — enable only delivery targets need the ID (unchanged); only the `prompt` text may mention the old group name. Verify NO enabled job delivers to a chat that was actually retired.
4. **Skills + memories** — grep for the old name in `skills/**` and any docs; a stale note contradicting the rename (e.g. claiming the group is "RETIRED") must be corrected or it will mislead future sessions into wrong routing.
5. **History/logs** — old-name strings inside `state/rich_sent_index.json`, conversation logs, and topic names are inert records; leave them (editing risks nothing but touches nothing useful either).

Rule: **rename keeps the chat ID** — so cron `deliver` and `routing` tables that reference the ID are still correct; only the *label/prompt* surface needs updating. This is why the rename audit is primarily a doc-prompt-skill sweep, not a delivery-target rewrite. Only when a chat is truly RETIRED (bot kicked / group deleted) do you rewrite `deliver` targets to a live chat — a rename and a retirement are different operations.

Verify a claimed rename against the live channel directory: read `channel_directory.json` and confirm the main (non-topic) entry for the ID now shows the new name; if it does and cron `deliver` still points at that ID, no delivery rewrite is needed.

## Proactive Audit Pattern

Run this audit whenever:
- Creating or updating a cron job
- Two jobs target the same group at the same time
- User asks "where did my cron output go?"
- User asks "why are these coming at the same time?"
- **A profile split / handoff just happened** (work moved to a sibling profile) — see "Dead-Job Purge After a Profile Split" below
- **User asks to review/improve the cron fleet** (e.g. "what would you change about our cron jobs?")

## Dead-Job Purge After a Profile Split (Aug 11, 2026)

When work is handed to a sibling profile (gentech → treasury/gizmo) or a job is superseded, the old profile keeps orphaned paused/disabled jobs. They don't run, but they bloat every `cronjob list`, clutter health checks, and get counted in "how many jobs" audits.

**Signature of a migrated job:** `paused_at` set + `paused_reason` reads "migrated to <profile> (swap <date>)", or a duplicate of a job now owned by another profile.

**Signature of a dead delivery:** `last_delivery_error` contains "bot was kicked from the supergroup chat" — the bot left that group but the job still targets it. The job (and the old group's jobs) can be removed if ownership moved elsewhere.

**Purge workflow:**
1. `cronjob action=list` — identify paused/disabled jobs whose replacement lives in another profile, plus completed one-shot jobs and duplicate trackers.
2. Confirm each is truly dead (not a job you want back). Keep intentionally-paused jobs that will resume.
3. `cronjob action=remove job_id=<id>` for each.
4. Re-list to verify the count dropped and no live job was caught.

**Also check for provider-switch collisions** during a fleet review: multiple mechanisms mutating the fleet's provider/model (a standalone `provider-auto-switch` cron + the canonical `cron-provider-sync.py` + a rate-limit auto-escalator + leftover one-shot "Fleet Switch" scripts) can clobber each other and flip jobs mid-day. Consolidate to ONE authority — the Auto-Sync — and pause/remove the redundant ones.

## Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Time collision | Two messages arrive simultaneously in one group | Offset one by 15+ min |
| Unclear job name | User asks "what's this?" | Prefix with `[User]` |
| Wrong group delivery | Vanito content in HQ | Set explicit `telegram:-10038...` target |
| Empty output | Job shows "ok" but no message | Check script output, maybe `no_agent` mode |
| Hardcoded old chat ID | Job delivers to defunct group | Update `deliver:` to current target |
| Stale stagger | Both jobs at same time after timezone change | Re-audit after DST or schedule overhaul |
| Overnight chat delivery | Job fires 3-7am ET into a Telegram group | `deliver=local`, or shift schedule to waking hours (see Quiet Hours Discipline) |
| Schedule format rejected on update | `Invalid schedule 'once at 2026-09-30 13:00'` | `cronjob update` accepts one-shot timestamps only as ISO — `2026-09-30T13:00:00` — not the "once at ..." prose form some listings show |

## Quick Reference

**List all jobs clean:**
```bash
hermes cron list | grep -E "name:|schedule:|deliver:|last_status:"
```

**Find time collisions:**
```bash
hermes cron list | grep -B 5 "schedule:" | grep -E "name:|schedule:"
```

**Safe defaults for GenTech:**
- Jordan → HQ or topic group
- Vanito → Entertainment
- Stagger like-jobs by 15+ min
- Name with `[User]` prefix

## Related Documentation

- Hermes docs: `https://hermes-agent.nousresearch.com/docs/cron-jobs`
- Topic routing: `routing` skill
- Single-agent multi-channel: `single-agent-multi-channel` skill

## Quiet Hours Discipline (Jordan, Sep 1 2026)
Fleet-wide quiet hours = **3–7am ET** (Jordan asleep). Jobs may RUN overnight (backup, sweeps, sync — silence is fine), but NO chat deliveries may land in that window:
- Recurring jobs firing 03:00–06:59 ET that post to chats → change `deliver=local`, or re-anchor the schedule to waking hours. `deliver=local` + `context_from` chaining keeps data flowing to the PA/overnight scanners with zero human noise.
- One-shot reminders created overnight (e.g. "fires 09:00 UTC = 5am ET") → re-anchor to waking hours (13:00+ UTC).
- Per-agent bot-chat wakers (`bot-chat:<agent>`) → constrain cron hours, e.g. `*/10 11-22 * * *` UTC.
- Fleet-wide directives (quiet hours, protocol changes) → write ONE dated handoff note to every agent's `INBOX/<group>/` lane in the vault (single write, all agents' wake triggers pick it up) instead of messaging N groups.
- Audit pattern: list all jobs, flag any with `deliver` targeting origin/telegram AND a cron hour in 07:00–10:59 UTC (03:00–06:59 ET) or `schedule` hitting `3,4,5,6` UTC hours; fix each (deliver=local or shift schedule). Re-audit after any fleet change — new jobs drift into overnight slots.

## Intentional Pause Naming Convention

When pausing a cron job for a known reason (vacation, market lull, seasonal break), rename it with a `[Reason]` prefix so the intent is clear at a glance:

- `[Vacation] Portfolio Health Check` — paused for trip, will resume on return
- `[Seasonal] Holiday Deal Scanner` — paused until next holiday season
- `[Deprecated] Old Price Monitor` — replaced by new version

This prevents confusion between "paused intentionally" and "paused because it broke." To resume, just rename the job back: remove the `[Reason]` prefix and unpause:

```bash
cronjob action=update job_id=<id> name="Portfolio Health Check"
cronjob action=resume job_id=<id>
```

## Related Documentation

- Hermes docs: `https://hermes-agent.nousresearch.com/docs/cron-jobs`
- Topic routing: `routing` skill
- Single-agent multi-channel: `single-agent-multi-channel` skill