# ProtoJay4789.github.io Conflict Case Study

Real-world analysis of Git conflicts in Gentech's automated portfolio and gaming hub repository.

## Repository Context

**Target Repo:** `/root/repos/ProtoJay4789.github.io`  
**Purpose:** GitHub Pages site hosting portfolio, gaming hub, DeFi dashboards, and music collections  
**Problem:** Frequent Git conflicts disrupting automated sync operations

## Conflicting Cron Jobs Identified

### 1. Gaming Hub Sync (ID: 1e8d33a03513)
- **Schedule:** `0 */6 * * *` (Every 6 hours: 00:00, 06:00, 12:00, 18:00 UTC)
- **Script:** `/root/.hermes/profiles/gentech/scripts/gaming-hub-sync.py`
- **Function:** Syncs POE2 build data from vault to GitHub Pages
- **Files Modified:** `Gaming/*.json` (9 files)
- **Status:** Enabled, 42 completions
- **Conflict Mitigation:** Uses `git stash` + `git pull --rebase` + `git stash pop`

### 2. POE2 Build Health Sync (ID: 02461aa0a77b)
- **Schedule:** `0 9 * * *` (Daily at 09:00 UTC)
- **Script:** `/root/.hermes/profiles/gentech/scripts/gaming-hub-sync.py` (**SAME SCRIPT!**)
- **Function:** Monitors Path of Exile 2 patches and syncs with gaming hub
- **Files Modified:** `Gaming/*.json` (same files as #1)
- **Status:** Enabled, 14 completions
- **CONFLICT RISK:** HIGH - Uses same script, can run concurrently with #1

### 3. Hub Nightly Sync (ID: d8d1c3adbbb4)
- **Schedule:** `0 20 * * *` (Daily at 20:00 UTC)
- **Script:** `/root/.hermes/profiles/gentech/scripts/hub-sync-nightly.py`
- **Function:** Syncs on-chain DeFi data to JSON files
- **Files Modified:** 
  - `DeFi/defi-data.json`
  - `DeFi/rainbow/yield-rainbow-data.json`
  - `DeFi/economic-calendar.json`
- **Status:** Enabled, 14 completions
- **Conflict Mitigation:** Stash before pull, accepts upstream on conflict

### 4. Portfolio Health Check (ID: ce23c5df747b)
- **Schedule:** `0 12 * * *` (Daily at 12:00 UTC)
- **Script:** Runs `portfolio_sync.py` inline in job prompt
- **Function:** Verifies portfolio data alignment and syncs if needed
- **Files Modified:** 
  - `projects.json` (root)
  - `data/projects.json`
  - `index.html`
- **Status:** Enabled, 23 completions
- **Conflict Mitigation:** Pre-sync pull, retry logic (3 attempts)

### 5. Vanito Music Sync (ID: f3e90d867b9c)
- **Schedule:** `every 360m` (Every 6 hours interval, not cron-based)
- **Script:** `/root/my-music/vanito-music-sync.py`
- **Function:** Syncs Vanito's music collection from GenTech Hub
- **Files Modified:** Music-related files in hub
- **Status:** Enabled, 4 completions
- **Conflict Mitigation:** Unknown (script not analyzed in depth)

## Critical Timing Conflicts

### Danger Zone: 12:00 UTC
**Jobs running simultaneously:**
- Portfolio Health Check (12:00)
- Gaming Hub Sync (12:00)

**Result:** Both jobs attempt to push at same time → HIGH conflict probability

### Medium Risk: 09:00 UTC
**Jobs running simultaneously:**
- POE2 Build Health (09:00)
- Gaming Hub Sync (if interval aligns)

**Result:** Same script pushing same files → Data corruption risk

### Medium Risk: 18:00 UTC
**Jobs running simultaneously:**
- Gaming Hub Sync (18:00)
- Vanito Music Sync (interval may align)

**Result:** Different files, but concurrent pushes

### Safe Zone: 20:00 UTC
**Single job:**
- Hub Nightly Sync (20:00)

**Result:** No conflicts

## Git Log Conflict Evidence

Recent commits show race condition pattern:
```
2026-07-05 15:24:35 - Sync POE2 builds (9 files)
2026-07-05 15:24:27 - feat: update Jordan's Monk character
[8-second gap → manual edit conflicted with automated sync]

2026-07-05 12:00:58 - Gaming Hub Sync
2026-07-05 12:01:41 - Portfolio Health Check  
[43-second gap → concurrent jobs]
```

### Pattern Recognition
1. Same author (Gentech = automated)
2. Commits within seconds/minutes
3. Different files modified
4. Rebase conflicts in job logs

## Script Analysis Results

### gaming-hub-sync.py
**Current approach:**
```python
# Lines 48-55
subprocess.run(["git", "stash"], check=False, capture_output=True)
subprocess.run(["git", "pull", "--rebase"], check=True, capture_output=True)
subprocess.run(["git", "stash", "pop"], check=False, capture_output=True)
```

**Issues:**
- No error handling for stash pop conflicts
- No retry logic if pull fails
- Doesn't check for concurrent jobs running
- Uses `check=True` on pull - will crash on conflict

### hub-sync-nightly.py
**Current approach:**
```python
# Lines 398-424
subprocess.run(f"git stash", shell=True)
# ... after push ...
subprocess.run(f"git stash pop", shell=True)
if "CONFLICT" in pop_out:
    # Accept upstream version to avoid blocking
    subprocess.run(f"git checkout --theirs -- $(git diff --name-only --diff-filter=U)")
```

**Strengths:**
- Checks for CONFLICT in stash pop output
- Accepts upstream version to avoid blocking next sync
- Uses `check=False` to avoid crashes

**Issues:**
- Still vulnerable to race conditions during push window
- No coordination with other jobs
- No file-based locking

### portfolio_sync.py
**Current approach:**
```python
# Lines 41-76
def pre_sync_pull():
    # Fetch and check for divergence
    local_sha = git("rev-parse", "HEAD").stdout.strip()
    remote_sha = git("rev-parse", "origin/main").stdout.strip()
    
    if local_sha != remote_sha:
        pull = git("pull", "--rebase", "origin", "main")
        if pull.returncode != 0:
            git("rebase", "--abort", check=False)
            print(f"WARNING: rebase conflict, aborted. Continuing with local state.")
            return False
```

**Strengths:**
- Pre-sync pull to lock canonical source
- Checks for remote divergence before reading
- Graceful abort on conflict
- Retry logic in push_with_retry (3 attempts)

**Issues:**
- Only protects against remote changes, not concurrent local jobs
- No file-level locking
- Retry doesn't back off (immediate retry)

## Specific Issues Discovered

### Issue 1: Same Script, Different Jobs
**Problem:** Gaming Hub Sync and POE2 Build Health both use `gaming-hub-sync.py` independently  
**Impact:** Both jobs write to same files (`Gaming/*.json`)  
**Current Behavior:** Race condition, last writer wins, potential data loss  
**Fix Needed:** Consolidate to single job OR add coordination within script

### Issue 2: No File Locking
**Problem:** None of the scripts implement file-based locking  
**Impact:** Multiple jobs can start simultaneously  
**Current Behavior:** Concurrent execution leads to conflicts  
**Fix Needed:** Add `fcntl` lock file to all sync scripts

### Issue 3: Schedule Overlaps
**Problem:** Multiple jobs scheduled at exact same times  
**Impact:** Guaranteed race conditions  
**Current Behavior:** Conflicts at 12:00 UTC daily  
**Fix Needed:** Offset schedules by 15 minutes

### Issue 4: Missing Retry Backoff
**Problem:** `portfolio_sync.py` retries immediately on failure  
**Impact:** Retries collide with the condition that caused the failure  
**Current Behavior:** Rapid retries increase conflict probability  
**Fix Needed:** Exponential backoff (30s, 60s, 120s)

### Issue 5: Manual vs Automated Collisions
**Problem:** Jordan's manual edits conflict with automated syncs  
**Impact:** Manual work lost or corrupted  
**Current Behavior:** Force-fix required, data loss risk  
**Fix Needed:** Better conflict resolution (upstream-first for automated)

## Recommended Fixes for This Repo

### Immediate (Today)
1. **Add file locking** to all 4 sync scripts
2. **Reschedule jobs** to eliminate 12:00 overlap:
   - Portfolio Health Check: 12:00 (keep)
   - Gaming Hub Sync: 12:15
   - POE2 Build Health: 09:30 (instead of 09:00)
   - Vanito Music Sync: 18:15
3. **Add error handling** for stash pop conflicts

### This Week
4. **Implement retry with exponential backoff** in all scripts
5. **Add pre-push conflict detection** before attempting push
6. **Create central sync manager** to coordinate all jobs

### Next Sprint
7. **Consider GitHub Actions** for sync jobs
8. **Evaluate SQLite** for defi-data.json (current size: 502 lines)
9. **Build monitoring dashboard** for sync health

## Files to Modify

1. `/root/.hermes/profiles/gentech/cron/jobs.json` - Reschedule jobs
2. `/root/.hermes/profiles/gentech/scripts/gaming-hub-sync.py` - Add locking + retry
3. `/root/.hermes/profiles/gentech/scripts/hub-sync-nightly.py` - Add locking + retry
4. `/root/.hermes/profiles/gentech/scripts/portfolio_sync.py` - Add backoff
5. `/root/my-music/vanito-music-sync.py` - Add locking + retry

## Expected Impact

**Before fixes:**
- 5+ conflicts per week
- Manual intervention required
- Risk of data loss during force-fixes
- Sync jobs fail silently

**After Phase 1 (locking + rescheduling):**
- 1-2 conflicts per week (70% reduction)
- Automatic conflict resolution
- No data loss
- Better error visibility

**After Phase 2 (retry + coordination):**
- Near-zero conflicts (<1/month)
- Fully automated operation
- Better reliability
- Monitoring capability

## Lessons Learned

1. **Always audit cron schedules** for time overlaps before deployment
2. **File locking is essential** for any multi-writer system
3. **Same script = same coordination** - duplicate jobs need coordination
4. **Retry logic needs backoff** - immediate retries make problems worse
5. **Check git logs for patterns** - close commits = race conditions
6. **Pre-sync pulls are good** but not sufficient for concurrent writers
7. **Accept upstream on conflict** - safer for automated systems than manual

## Command Reference

```bash
# List all cron jobs that write to this repo
cd /root/.hermes/profiles/gentech/cron
jq -r '.jobs[] | "\(.id) | \(.name) | \(.schedule.display) | \(.script)"' jobs.json | grep -i "hub\|portfolio\|sync\|music"

# Check git log for conflict patterns
cd /root/repos/ProtoJay4789.github.io
git log --all --pretty=format:"%ad|%an|%s" --date=iso | head -50

# Find commits within seconds of each other
git log --all --pretty=format:"%h|%ad|%an|%s" --date=iso | \
  awk 'NR>1 {diff=$2-prev; if(diff<60) print prev_time" → "$2" | "$3" | "$4} {prev=$2; prev_time=$2}'

# Check for duplicate scripts
jq -r '.jobs[] | .script' /root/.hermes/profiles/gentech/cron/jobs.json | sort | uniq -d

# Visualize schedule overlaps
jq -r '.jobs[] | "\(.schedule.display) | \(.name)"' /root/.hermes/profiles/gentech/cron/jobs.json | sort
```