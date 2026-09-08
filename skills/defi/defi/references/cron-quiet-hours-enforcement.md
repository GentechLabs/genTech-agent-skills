# Cron Quiet Hours Enforcement — Quan Jobs Should Not Run

**User directive:** "During quiet hours, none of the Quan jobs should be running at all."

## The Problem

Scripts like `lp-monitor-v2.py` had quiet hours checks that printed `"QUIET_HOURS — no report"` and exited successfully. This wastes compute, makes API calls, and spawns unnecessary LLM invocations even when the user doesn't want alerts.

## The Fix: Cron Schedule Enforcement

Instead of quiet hours logic in scripts, **exclude quiet hours from cron schedules directly**. Jobs simply don't fire during quiet hours.

**Quiet hours definition:** 23:00 - 06:00 ET

## Schedule Updates Applied (Jul 5, 2026)

| Job | Old Schedule | New Schedule | Status |
|-----|--------------|--------------|--------|
| LP Monitor v2 | `3,13,23,33,43,53 6-22 * * *` | `3,13,23,33,43,53 7-22 * * *` | ✓ Fixed |
| CMC Bullish | `0 7-23/2 * * *` | `0 7-22/2 * * *` | ✓ Fixed |
| Morning To-Do | `30 6 * * *` | `30 7 * * *` | ✓ Fixed |
| Session Reset | `0 6 * * *` | `0 7 * * *` | ✓ Fixed |

## Technical Jobs (Run 24/7 — Intentional)

These infrastructure jobs MUST run 24/7 regardless of quiet hours:

| Job | Purpose | Why 24/7 |
|-----|---------|----------|
| Rate Limit Monitor | Infrastructure alerting | Catch rate limit failures immediately |
| Cron Health Monitor | Infrastructure health | Auto-fix broken cron jobs |
| Gaming Hub Sync | Background data sync | Non-user-facing data pipeline |
| Context Snapshot | Vault maintenance at midnight | Essential backup task |
| Brain Backup | Backup at 22:00 | Before quiet hours start |

## Implementation Pattern

```bash
# Wrong: Script checks quiet hours and prints "QUIET_HOURS — no report"
# This wastes compute and makes API calls

# Right: Exclude quiet hours from cron schedule
# Schedule: 3,13,23,33,43,53 7-22 * * *  (runs 7am-10pm, silent 11pm-6am)
```

## Verification

After updating schedules, verify with:

```bash
# List all cron jobs and check schedules
hermes cronjob list | jq '.[] | {name, schedule}'

# Check current time vs quiet hours
python3 -c "
from datetime import datetime, timezone, timedelta
now = datetime.now(timezone(timedelta(hours=-4)))
hour = now.hour
print(f'Current time (ET): {now.strftime(\"%H:%M\")}')
print(f'Quiet hours (23-6): {\"Yes\" if hour >= 23 or hour < 6 else \"No\"}')
"
```

## Related Skills

- `defi` — LP monitoring and cron orchestration
- `gentech-ops` — Cron schedule management

**User feedback:** "Stop the jobs from running, don't just make them silent."