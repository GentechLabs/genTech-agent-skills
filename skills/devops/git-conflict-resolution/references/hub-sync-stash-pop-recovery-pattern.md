# Hub Sync Stash Pop Recovery Pattern

**Date:** July 9, 2026  
**Repo:** ProtoJay4789.github.io  
**Corrupted file:** `DeFi/defi-data.json` (>100 conflict markers)  
**Root cause:** Stash-pop conflict during nightly hub sync cron job

## Failure Sequence

1. Nightly hub sync script ran on schedule (20:00 UTC)
2. Script did `git stash` → `git pull --rebase origin main` → `git stash pop`
3. The stash contained an old version of `defi-data.json` that conflicted with newly pulled updates
4. `git stash pop` left conflict markers in the working tree but did NOT drop the stash (stash@{0..2} all contained defi-data.json variants)
5. A prior run had also left the repo in a detached HEAD rebase state (from a previous `git pull --rebase` that was aborted mid-way)
6. The actual push failed: "git push failed after retries" — main was behind origin/main by 11 commits
7. The live verification `/DeFi/` returned 404 (expected — no index.html in directory, this is a false alarm)

## Script Output

```
Removing stale lock file (age: 6287s)
HUB SYNC ISSUES:
  ⚠️ Existing dash parse: Invalid JSON in /root/ProtoJay4789.github.io/DeFi/defi-data.json
  🔴 Push failed: git push failed after retries
  ⚠️ Live verification: missing HTTP Error 404: Not Found
```

## Recovery Steps

### Phase 1: Restore the Corrupted File

The committed version on main was actually clean — the conflict was only in the working tree. The file was passed over from the clean commit `789c3a7d`:

```bash
# Find the last clean commit for this file
git log --all --oneline -- DeFi/defi-data.json | head -5
# → 789c3a7d Nightly hub sync: 2026-07-09 20:00 UTC

# Restore file from that commit
git checkout 789c3a7d -- DeFi/defi-data.json

# Verify JSON is valid
python3 -m json.tool DeFi/defi-data.json
# → Valid JSON, 15/15 sections present
```

### Phase 2: Fix Diverged Branch

The repo was in a detached HEAD state from a previous failed rebase:

```bash
# Check state
git branch  # → * (no branch, rebasing main) — detached HEAD!
git status  # → modified: DeFi/defi-data.json

# Abort the stuck rebase
git rebase --abort

# Fetch remote
git fetch origin

# Rebase main onto origin/main
git rebase origin/main
# → CONFLICT in DeFi/defi-data.json (hub sync vs origin/main diverged)

# Accept the hub sync version (it has latest data)
git checkout --theirs -- DeFi/defi-data.json
git add DeFi/defi-data.json
EDITOR=true git rebase --continue
# → Successfully rebased and updated refs/heads/main
```

### Phase 3: Push and Verify

```bash
# Push
git push origin main
# → main -> main

# Verify
curl -I https://ProtoJay4789.github.io/DeFi/defi-data.json
# → HTTP 200
```

### Phase 4: Clean Up Stale Stashes

The 3 stale stashes (stash@{0..2}) all contained old defi-data.json variants that caused the original conflict. Cleaned them:

```bash
git stash drop stash@{2}
git stash drop stash@{1}
git stash drop stash@{0}
```

Remaining stashes (stash@{3..6}) did not touch defi-data.json.

## Key Insights

1. **`git stash pop` does NOT drop the stash on conflict** — it leaves the stash intact AND writes conflict markers to the working tree. This means subsequent `git stash pop` calls keep failing on the same conflict. Always check for this.

2. **Detached HEAD from prior rebase blocks pushes** — a stuck rebase leaves the repo in `(no branch, rebasing main)` state. `git rebase --abort` is the first step before any other git operation.

3. **GitHub Pages 404 on a directory is expected** — `/DeFi/` returns 404 when there's no `index.html` in that directory. The actual data file at `/DeFi/defi-data.json` serves 200. This is NOT a real health issue.

4. **Multiple stashes accumulate** — When stash pop keeps failing, each new `git stash` creates a new stash entry while the old ones persist. Over 3 nightly runs, 3 conflicted stashes accumulated. Clean them after resolution.

5. **The committed file was clean** — Irony: the file in the repo (commit 789c3a7d) was valid JSON with all 15 dashboard sections. The corruption was only in the working tree. Restoring from that commit was clean.

## Prevention Applied

For the nightly hub sync script, these defenses are needed:

1. **Pre-commit conflict marker scan** — before writing any JSON file, scan it for `<<<<<<<` / `=======` / `>>>>>>>`
2. **JSON validation before commit** — try `json.loads()` before `git add`
3. **Handle stash pop failure explicitly** — check exit code AND stdout for "CONFLICT"
4. **Limit stash depth** — use `git stash push --include-untracked` with a message; if pop fails, don't push again

## Related

- `cron-truth-layer` skill: Anti-Pattern 9 (sanitize_json_text + load_json_safe)
- `git-conflict-resolution` skill: Pitfall 7 (this pattern's entry in the main skill)
