# Rebase Cascade Prevention — Automated Data Syncs

**Date:** Jul 19, 2026
**Author:** Gentech
**Context:** Hub Nightly Sync failed when `git pull --rebase` hit 15 divergent commits, each causing a fresh conflict. The script's one-shot resolver only handled the first.

## The Problem

`git pull --rebase` re-applies every commit between local and remote, one at a time. When there are N divergent commits, EACH ONE can conflict. A script that handles ONE conflict only survives the first — the next `rebase --continue` hits commit 2's conflict, and so on for all N.

## Detection

| Symptom | Root Cause |
|---------|-----------|
| `git status` shows "interactive rebase in progress; onto <sha>" | Rebase cascade stuck mid-way |
| `both modified: file.json` with no other changes | Conflict artifacts from rebase |
| Pre-push validation fails, file has only 1-2 keys | Cascading rebase corrupted the file |
| Multiple "Nightly hub sync" commits on main branch | Frequent small syncs = more divergence |

**Check divergence count:**
```bash
git rev-list --count HEAD..origin/main
# If > 1, rebase WILL cascade through each commit
```

## The Fix: Merge Over Rebase

For scripts that **fully regenerate** data files from an authoritative source (vault, API, on-chain data), use `git fetch + git merge --strategy-option theirs` instead of rebase.

### Comparison Table

| Strategy | Conflict Resolution | Multi-Commit Behavior | When to Use |
|----------|-------------------|----------------------|-------------|
| `git pull --rebase` | One conflict at a time, per commit | Cascades through N commits | User-edited files, editorial content |
| `git fetch + git merge --strategy-option theirs` | All conflicts resolved in one pass with `theirs` | One-shot (no cascade) | **Fully regenerated data files** |
| `git fetch + git pull --no-rebase` | One-shot merge (default strategy) | One-shot merge | Mixed-content repos |

### Preferred Pattern

```python
def push_data_to_github(data_file, repo_path):
    """
    Push a fully-regenerated data file to a shared repo.
    Uses merge with theirs to avoid rebase cascade.
    """
    import subprocess, time, json

    # 1. Verify source file is valid JSON
    with open(data_file) as f:
        json.load(f)  # will raise if invalid

    # 2. Copy to repo
    subprocess.run(f"cp {data_file} {repo_path}/DeFi/", shell=True, check=True)

    # 3. Stage
    subprocess.run(f"cd {repo_path} && git add -A", shell=True, check=True)

    # 4. Commit (skip if no changes)
    out = subprocess.run(
        f"cd {repo_path} && git diff --cached --quiet",
        shell=True, capture_output=True
    )
    if out.returncode == 0:
        return "no_changes"

    subprocess.run(
        f"cd {repo_path} && git commit -m 'data: sync update'",
        shell=True, check=True
    )

    # 5. Fetch remote
    subprocess.run(f"cd {repo_path} && git fetch origin main", shell=True, timeout=30)

    # 6. MERGE (not rebase) — theirs strategy, one-shot conflict resolution
    merge = subprocess.run(
        f"cd {repo_path} && git merge origin main --no-edit --strategy-option theirs",
        shell=True, capture_output=True, text=True, timeout=30
    )
    if merge.returncode != 0:
        subprocess.run(f"cd {repo_path} && git merge --abort", shell=True)
        raise RuntimeError(f"Merge failed: {merge.stderr}")

    # 7. Pre-push JSON validation
    with open(f"{repo_path}/DeFi/defi-data.json") as f:
        json.load(f)  # verify still valid after merge

    # 8. Push with retry
    for attempt in range(3):
        push = subprocess.run(
            f"cd {repo_path} && git push", shell=True,
            capture_output=True, text=True, timeout=30
        )
        if push.returncode == 0:
            return "pushed"
        time.sleep(30 * (2 ** attempt))

    raise RuntimeError(f"Push failed after 3 retries: {push.stderr}")
```

### Recovery From Stuck Rebase

When you encounter a stuck rebase cascade:

```bash
# 1. Diagnose
cd /path/to/repo
git status
# → "interactive rebase in progress; onto <sha>"

# 2. Abort (safe — rebase is atomic, nothing lost)
git rebase --abort

# 3. Verify vault/authoritative source
python3 -c "import json; json.load(open('/path/to/vault/source.json')); print('OK')"

# 4. Copy vault → repo
cp /path/to/vault/source.json path/to/repo/target.json

# 5. Commit and merge
cd /path/to/repo
git add target.json
git commit -m "data: recovery from rebase cascade"
git fetch origin main
git merge origin main --no-edit --strategy-option theirs
git push
```

### When to Keep Rebase

Rebase is still appropriate when:
- **User-edited files** — the user's changes should be replayed on top of remote
- **Multiple manual edits** — rebase preserves a linear history for review
- **Editorial content** — conflicts need human judgment, not auto-resolution
- **Non-data files** — HTML templates, JS code, markdown docs

### When to Use Merge-With-Theirs

Merge-with-theirs is the right choice when:
- **File is fully regenerated** — vault → API → on-chain data pipeline
- **Authoritative source exists** — the previous version is always discardable
- **No human edits** — the file is purely machine-generated
- **Multiple scripts write to same file** — race conditions are the norm, not the exception

## Historical Context

| Date | Event | Fix |
|------|-------|-----|
| Jul 10, 2026 | Sequence vulnerability: pre-commit scan missed rebase-introduced markers | Added post-rebase scan |
| Jul 12, 2026 | Rebase --continue missing after conflict resolution | Added continues step |
| Jul 15, 2026 | Vault-fallback recovery for structurally incomplete JSON after sanitize | Added re-copy from vault |
| **Jul 19, 2026** | **Multi-commit rebase cascade (15 commits)** | **Switched to merge-with-theirs strategy** |

The progression shows that rebase is fundamentally fragile for automated data syncs. Each fix added a new layer of defense, but only the merge strategy eliminates the class of failure entirely.
