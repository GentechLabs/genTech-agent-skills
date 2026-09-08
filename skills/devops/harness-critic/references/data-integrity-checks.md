# Data Integrity Checks for Harness Critic

This reference documents the data integrity checks the Critic should run every cycle, with exact commands and expected outcomes.

## 1. Critique Log Corruption

**Check:** Scan for embedded read_file line-number prefixes.

```bash
python3 -c "
import re
from pathlib import Path
text = Path('facts/critique-log.md').read_text()
corrupt = [(i+1, l) for i, l in enumerate(text.split('\n')) if re.match(r'^\d+\|', l)]
if corrupt:
    print(f'CORRUPTION FOUND: {len(corrupt)} lines')
    for n, l in corrupt[:5]:
        print(f'  Line {n}: {l[:60]}')
else:
    print('No corruption found')
"
```

**Repair:** `python3 scripts/repair-critique-log.py`

## 2. Git Repository

**Check:**
```bash
git -C /root/.hermes/profiles/gentech/harness status 2>&1
```

**Expected:** Shows branch and clean working tree.
**Failure:** `fatal: not a git repository` — flag as HIGH.

**Init (one-time):**
```bash
cd /root/.hermes/profiles/gentech/harness
git init
git add -A
git commit -m "harness baseline evolve-N"
```

## 3. State File Staleness

**Check mtime vs last cycle timestamp:**
```bash
python3 -c "
from pathlib import Path
import time
files = ['facts/harness-state.md', 'facts/prediction-outcomes.md', 'facts/recommendation.md']
now = time.time()
for f in files:
    p = Path(f)
    if p.exists():
        age_hours = (now - p.stat().st_mtime) / 3600
        print(f'{f}: {age_hours:.1f}h old')
    else:
        print(f'{f}: MISSING')
"
```

**Expected:** All files updated within the last cycle window (e.g., < 4h for a 4h cycle).

## 4. Prediction Outcomes Completeness

**Cross-reference predictions.md against prediction-outcomes.md:**
```bash
python3 -c "
from pathlib import Path
import re
preds = Path('facts/predictions.md').read_text()
outcomes = Path('facts/prediction-outcomes.md').read_text()
# Find all PREDICTION #N entries
pred_ids = set(re.findall(r'PREDICTION #(\d+)', preds))
outcome_ids = set(re.findall(r'PREDICTION #(\d+)', outcomes))
missing = pred_ids - outcome_ids
if missing:
    print(f'Missing outcomes for predictions: {sorted(missing, key=int)}')
else:
    print('All predictions have outcomes')
"
```

## 5. Action-Type Diversity

**Check unique RECOMMENDED_ACTION types in last 7 days:**
```bash
grep '^RECOMMENDED_ACTION:' facts/execution-log.md | sort | uniq -c | sort -rn
```

**Expected:** At least 3 distinct action types. If all are the same, flag as CRITICAL.

## 6. Entry Count Integrity

**Verify critique log entry count:**
```bash
grep -c '^## Critique Entry' facts/critique-log.md
```

**Expected:** Increases by exactly 1 each cycle. If it stays the same or jumps by >1, flag.
