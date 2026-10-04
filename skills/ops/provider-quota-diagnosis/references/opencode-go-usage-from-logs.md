# OpenCode Go — Usage From Logs

OpenCode Go has **no JSON usage endpoint** (`/v1/usage`, `/api/usage`, `/v1/limits` all return the
dashboard SPA). When you need a usage number, build it from the request logs.

## The only reliable identity

A **call** is identified by:

```
(seat, session_tag, call_number, model_id)
```

NOT by:
- a log line — retries and rotation duplicate lines
- the filename — `agent.log.1` / `.2` / `.3` may hold the same call
- `(seat, session_tag)` alone — one session makes many calls

## Session-tag shapes

Our logs emit at least two shapes. A regex that matches only one silently breaks the count.

```
[cron_<hash>_YYYYMMDD_HHMMSS]     # cron jobs
[YYYYMMDD_HHMMSS_<hash>]          # interactive sessions
```

Correct `SESSION_RE`:

```python
import re
SESSION_RE = re.compile(
    r"\[((?:cron_[a-z0-9]+_\d{8}_\d{6})|(?:\d{8}_\d{6}_[a-z0-9]+))\]", re.I)
```

## Reference counter

```python
import glob, gzip, os, re
from collections import defaultdict

LINE = re.compile(
    r"^(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2},\d+ .*?\[([^\]]+)\].*?"
    r"API call #(\d+): model=(\S+) provider=([a-z0-9\-]+) in=(\d+) out=(\d+) total=(\d+)")

ALLOWANCE = {
    "deepseek-v4.1-flash": 37_800,
    "kimi-k2.7-code": 6_750,
    "glm-5.3-flash": 7_900,
}

seen = set()
per_day = defaultdict(lambda: defaultdict(int))
for seat in sorted(glob.glob('/root/.hermes/profiles/*/')):
    for pat in ('logs/agent.log*', 'logs/errors.log*', 'logs/mcp-stderr.log*'):
        for f in glob.glob(os.path.join(seat, pat)):
            if not os.path.isfile(f):
                continue
            try:
                txt = gzip.open(f, 'rt', errors='replace').read() if f.endswith('.gz') \
                      else open(f, encoding='utf-8', errors='replace').read()
            except Exception:
                continue
            for ln in txt.splitlines():
                m = LINE.match(ln)
                if not m or 'opencode' not in m.group(5):
                    continue
                key = (seat, m.group(2), m.group(3), m.group(4))
                if key in seen:
                    continue
                seen.add(key)
                per_day[m.group(1)][m.group(4)] += 1
```

## Compare to the allowance

```python
for model, allowance in ALLOWANCE.items():
    counts = [per_day[d].get(model, 0) for d in sorted(per_day)]
    if not any(counts):
        continue
    recent = counts[-3:]  # last 3 days
    avg = sum(recent) / len(recent)
    print(f"{model}: recent avg {avg:.0f}/day -> {allowance/avg:.0f} days of runway")
    print(f"  projected month: {avg*30:,.0f} = {avg*30/allowance*100:.0f}% of {allowance:,}")
```

The 37,800 figure is the base $10/mo Go allowance. If the account is on Plus, the real bucket
is larger and these percentages are conservative. There is no API to read the Plus allowance.
