# Fed Event Tracker — Cron Jobs & Scripts

**Created:** June 11, 2026
**Purpose:** Remind Jordan before Fed events + deliver cliff notes summaries after FOMC decisions

## Cron Jobs

| Job | Schedule | Type | Delivers To |
|-----|----------|------|-------------|
| Fed Event Reminder — Daily | 0 12 * * * (8 AM EDT) | Script-only | HQ |
| FOMC Summary — Post-Meeting | 30 20 * * * (4:30 PM ET) | Agent-driven | HQ |

## Script

**Path:** `/root/.hermes/scripts/fed-event-tracker.py`

Checks for upcoming FOMC meetings and Fed Chair speeches. Outputs reminders 2 days before, 1 day before, and day-of. On the day after each FOMC meeting, outputs "summary needed" which triggers the agent to search for the decision.

## 2026 FOMC Calendar

| Date | Label | Notes |
|------|-------|-------|
| Jan 28 | FOMC Meeting | Already passed |
| Mar 18 | FOMC Meeting | Already passed |
| May 6 | FOMC Meeting | Already passed |
| **Jun 17** | **FOMC Meeting — Warsh's First** | **Next meeting — critical** |
| Jul 29 | FOMC Meeting | |
| Sep 17 | FOMC Meeting + SEP (Dot Plot) | SEP = Summary of Economic Projections |
| Oct 28 | FOMC Meeting | |
| Dec 9 | FOMC Meeting + SEP (Dot Plot) | |

## Key Context (June 2026)

- **New Fed Chair:** Kevin Warsh took over from Powell on May 15, 2026
- **Hawkish tilt:** Despite market expectations for rate cuts, Warsh is signaling possible HIKES
- **Bond markets pricing in hikes** — yields rising significantly
- **Elevated CPI/PPI + strong jobs** reinforce inflation focus
- **June 16-17 is Warsh's first FOMC meeting** — the fork in the road for crypto markets

## Adding New Events

To add Fed Chair speeches or special events:
1. Edit `/root/.hermes/scripts/fed-event-tracker.py`
2. Add to `FED_SPEECHES_2026` list: `{"date": "YYYY-MM-DD", "time": "HH:MM ET", "label": "Description"}`
3. No restart needed — script reads fresh each run

## Summary Format

The agent-driven FOMC summary delivers:
1. **Rate Decision** — hold, cut, or hike? By how much?
2. **Key Quote** — most important line from statement/press conference
3. **Dot Plot** — if SEP released, rate path projection
4. **Market Reaction** — stocks, crypto, bonds, gold response
5. **What It Means** — one sentence on portfolio impact
