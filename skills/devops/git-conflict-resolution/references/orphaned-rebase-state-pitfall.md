## Pitfall 8: Orphaned Rebase State Blocks Cron Script Pulls

**Symptom:** A no_agent cron script (e.g., `gaming-hub-sync.py`) fails with `"Pulling is not possible because you have unmerged files"` but the script itself doesn't do complex merge operations.

**Root cause:** A previous `git pull --rebase` (either from another script, manual intervention, or a prior cron run) started a rebase that was never completed. The rebase left unmerged files in the working tree. On the next run, when the script does `git pull --rebase`, it fails immediately because the rebase state is still active.

**Detection:**
```bash
cd /root/repos/<target-repo>
git status  # Look for files with 'AA' (unmerged) or 'UU' status
git rev-parse --verify MERGE_HEAD 2>/dev/null && echo "Orphaned rebase in progress" || echo "No rebase"
git ls-files --unmerged | head -20  # List conflicted files
```

**Fix — clear orphaned rebase state:**
```bash
cd /root/repos/<target-repo>

# 1. Identify conflicted files
git diff --name-only --diff-filter=U

# 2. Resolve conflicts (accept current/ours version for redirect/docs)
git checkout --ours Games/.redirect.md
git checkout --ours Projects/.redirect.md
git checkout --ours Strategies/.redirect.md

# 3. Stage resolved files
git add Games/.redirect.md Projects/.redirect.md Strategies/.redirect.md

# 4. Continue and complete the rebase (or abort if no meaningful changes)
GIT_EDITOR=true git rebase --continue
# If that fails: git rebase --abort  (then git pull fresh)

# 5. Verify clean
git status
```

**Real-world example (Jul 12, 2026):** `gaming-hub-sync.py` and `[Jordan] POE2 Build Health — Gaming Hub Sync` both failed because the `ProtoJay4789.github.io` repo had an orphaned rebase with 3 unmerged `.redirect.md` files from a prior vault consolidation push. Resolution: `git checkout --ours` on the 3 redirect files, `git add`, `GIT_EDITOR=true git rebase --continue`, then `git push`.

**Prevention in cron scripts:**
```python
# Before doing git pull --rebase, check for orphaned rebase state
import subprocess

def check_orphaned_rebase():
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "MERGE_HEAD"],
        check=False, capture_output=True
    )
    if result.returncode == 0:
        # Rebase in progress — resolve or abort
        conflicted = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=U"],
            check=True, capture_output=True, text=True
        ).stdout.strip().split('\n')
        
        if conflicted and conflicted[0]:
            for f in conflicted:
                subprocess.run(["git", "checkout", "--theirs", "--", f])
            subprocess.run(["git", "add", "-u"])
        
        subprocess.run(["git", "rebase", "--continue"], check=False)
        print("Cleared orphaned rebase state")
```
