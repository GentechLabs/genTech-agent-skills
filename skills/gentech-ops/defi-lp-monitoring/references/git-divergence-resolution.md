# Git Hub Divergence Resolution

The on-chain reader commits `defi-data.json` and pushes after every read cycle. When other processes (gaming hub sync, nightly maintenance, hub-sync-nightly cron, manual pushes) have committed to the same repo between reader cycles, the push is rejected as non-fast-forward.

**Jul 3, 2026 incident:** The on-chain reader pushed commit `94b9e8d1` with fresh rebalance data, but `origin/main` had moved ahead with 3 POE2 sync commits. The reader had `pull.rebase=true` configured, which created merge conflict artifacts (`<<<<<<< Updated upstream`) in the remote `defi-data.json`. The GitHub Pages CDN then served a corrupted JSON file until manually fixed.

## Diagnosis

Check for failure after a reader push:

```bash
# Check if push was rejected
cd /root/ProtoJay4789.github.io
git log --oneline origin/main -1
git log --oneline HEAD -1
# If HEAD is ahead but push failed: divergent branches
```

## Resolution Sequence (Fast Path)

When the push fails because remote has diverged:

```bash
# 1. Discard local commits, align with origin
git fetch origin
git reset --hard origin/main

# 2. Re-run the on-chain reader (writes fresh clean data)
python3 /root/.hermes/profiles/gentech/scripts/run-reader.py

# 3. Let the reader's auto-commit+push handle the rest
```

The reader's own commit/push logic will re-commit and push cleanly from the aligned HEAD.

## Manual Resolution (If Reader Auto-Commit Fails)

```bash
# 1. Sync with origin
git fetch origin
git reset --hard origin/main

# 2. Write fresh defi-data.json from tracker/reader
python3 /root/.hermes/profiles/gentech/scripts/run-reader.py

# 3. If reader script fails to push, do it manually
git add DeFi/defi-data.json
git commit -m "auto: on-chain position update $(date +%H:%M)"
git push origin main
```

## Merge-Commit Corruption (Jul 18, 2026 Incident)

A different form of corruption occurs when a **merge commit** (not a rebase) contains unresolved conflict markers that get written into the tracked file. This can happen when `git merge` is used instead of `git pull --rebase` and conflicts aren't resolved before committing.

**Symptoms:**
- `defi-data.json` opens with `<<<<<<< Updated upstream` repeated on multiple lines (426 lines in the Jul 18 incident)
- The corrupted file was committed and pushed — the CDN serves the garbage directly
- `git reset --hard origin/main` does NOT fix this because `origin/main` itself has the corruption
- `json.load()` fails with `Expecting property name enclosed in double quotes`

**Diagnosis:**
```bash
head -5 DeFi/defi-data.json
# Shows conflict marker artifacts
```

**Resolution (restore from git history):**
```bash
# 1. Find a pre-corruption commit that has a clean version of the file
git log --oneline -- DeFi/defi-data.json | head -10

# 2. Restore from that commit
git show <clean-commit>:DeFi/defi-data.json > DeFi/defi-data.json

# 3. Verify valid JSON
python3 -c "import json; json.load(open('DeFi/defi-data.json'))"

# 4. Commit and push the fix
git add DeFi/defi-data.json
git commit -m "fix: restore defi-data.json from git corruption"
git push origin main
```

**Prevention:** Any script that runs `git merge` should check for conflict markers before committing. If `<<<<<<<` appears in tracked JSON files, abort the merge and use the restore pattern instead. For LP pipeline repos, prefer `fetch && reset --hard origin/main` over `pull --rebase` to avoid creating conflict artifacts entirely.

## Reader Commit Lost After Pull --Rebase

A subtle edge case that occurred Jul 18, 2026: the on-chain reader successfully reads on-chain data, writes `defi-data.json`, **commits** locally (e.g., `1b4b4527`), but the push is rejected because the remote has moved. Another process (or manual intervention) then runs `git pull --rebase`, which **rewrites history** and discards the reader's commit entirely — the reader's fresh data is still in the working tree, but it's now an uncommitted dirty diff.

**Symptoms:**
- Reader output says `[main abc1234] auto: on-chain position update`
- But `git log --oneline -1` shows a different commit
- `git status` shows `nothing to commit, working tree clean` — the data was written but the commit was replaced during rebase
- The remote never received the reader's data

**Root Cause:** The reader's internal sequence is: write → commit → push. If push is rejected, some versions of the reader's wrapper do not retry. If someone then runs `pull --rebase` (or the reader's own wrapper does), the rebase selects the remote commits as "ours" and discards the local reader commit as "theirs."

**Resolution:**

```bash
# 1. Check if the file has the reader's data or is stale
python3 -c "import json; d=json.load(open('DeFi/defi-data.json')); print(d['lpPosition']['rangeMin'])"

# 2. If stale, re-run the reader to write fresh data
python3 /root/.hermes/scripts/run-reader.py

# 3. Manual commit and push (don't rely on reader's auto-push when this is flapping)
git add DeFi/defi-data.json
git commit -m "update: on-chain position refresh"
git push origin main
```

**Prevention:** The reader script should not attempt auto-push at all. Instead, use a **two-phase pattern**: the reader writes the data and commits locally; a separate cron tick (or a post-reader hook) handles the push with proper retry logic. Until that's implemented, always verify `git log --oneline -1` after a reader run and push manually if the commit didn't stick.

## Why This Happens

The ProtoJay4789.github.io repo receives commits from multiple independent processes:

| Source | Schedule | Typical File |
|--------|----------|-------------|
| On-chain reader | Every 10 min (:00/:10/:20) | `DeFi/defi-data.json` |
| Gaming hub sync | Every 6 hours | `Gaming/*` |
| Hub nightly sync | Daily 20:00 ET | `DeFi/*`, `Gaming/*` |
| POE2 build health | Daily 09:00 ET | `Gaming/POE2/*` |

Any of these can commit between reader cycles, causing the reader's push to reject. The `git reset --hard origin/main` approach is safe because the reader always writes **fresh** on-chain data — nothing is lost by discarding a stale local commit.

## Prevention

The reader script could be improved to handle divergence gracefully:

```python
# Proposed fix for run-reader.py push logic
import subprocess
result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
if result.returncode != 0 and "rejected" in result.stderr:
    # Remote diverged — fetch, reset, re-commit
    subprocess.run(["git", "fetch", "origin"])
    subprocess.run(["git", "reset", "--hard", "origin/main"])
    # Re-run the write + commit + push
    write_defi_data()  # re-write
    subprocess.run(["git", "add", "DeFi/defi-data.json"])
    subprocess.run(["git", "commit", "-m", "auto: position update"])
    subprocess.run(["git", "push", "origin", "main"])
```

Until that fix is applied, the manual `fetch && reset --hard && re-run reader` sequence is the reliable workaround.
