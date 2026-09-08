# Shared Quiet Hours Module

## Location
`/root/.hermes/profiles/gentech/scripts/quiet_hours.py`

## Usage
```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from quiet_hours import is_quiet_hours

if is_quiet_hours():
    sys.exit(0)  # or suppress Telegram output
```

## Configuration
- `QUIET_START = 22` (10pm ET)
- `QUIET_END = 8` (8am ET)
- Timezone: UTC-4 (Eastern Time)

## Pattern
All GenTech cron scripts should import from this shared module rather than defining their own quiet hours constants. This ensures consistent behavior across:
- CMC Bullish Watchlist
- Fed Event Reminder
- DeFi Milestone (has its own copy for backward compat)
- Any future cron scripts

## Why Shared?
Jordan's directive: "all cron jobs should be silent overnight." Having one source of truth for quiet hours prevents drift between scripts. If the quiet window changes, update one file, not ten.
