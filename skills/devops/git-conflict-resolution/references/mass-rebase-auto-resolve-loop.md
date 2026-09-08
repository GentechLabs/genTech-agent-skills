# Mass Rebase (Hundreds of Commits) — Automated Resolve-and-Continue Loop

**Proven Aug 24, 2026** on a 398-commit, 1.16 GiB vault rebase that had stalled at commit 6.

## Symptom

An interactive rebase of a large repo stalls at commit N because *every few commits* hits a conflict in the same set of cumulative log/registry files: `treasury-completions.md`, `marketplace-listings-registry.md`, `build_queue.json`, `jordan-queue.md`, handoff logs. Manual per-conflict resolution (each needs `add` + `--continue`) would take hours.

## Root cause

Cumulative log files are touched by nearly every commit. During a rebase, each commit's diff re-applies against the accumulating base, so the same file conflicts repeatedly — not because content differs, but because both sides append to the same running log. Nearly all such conflicts are **keep-live (HEAD)** resolutions: the current on-disk state is the accumulated, chronologically-later truth; the incoming rebase commit re-applies an OLDER snapshot of the same log.

## The loop

```bash
cd /root/vaults/gentech
# Resolve ALL unmerged files to HEAD (the live state) then continue. Repeat in batches.
timeout 280 bash -c '
  i=0
  while [ $i -lt 120 ]; do
    unmerged=$(git diff --name-only --diff-filter=U 2>/dev/null | wc -l)
    if [ "$unmerged" -gt 0 ]; then
      git checkout --ours -- . 2>/dev/null   # keep live HEAD version
      git add -A 2>/dev/null
      echo "[$i] resolved $unmerged unmerged"
    fi
    out=$(GIT_EDITOR=true git rebase --continue 2>&1)
    rc=$?
    prog=$(echo "$out" | grep -oE "Rebasing \(([0-9]+)/([0-9]+)\)" | tail -1)
    echo "[$i] rc=$rc $prog"
    if echo "$out" | grep -q "No rebase in progress"; then echo "DONE"; break; fi
    i=$((i+1))
  done
'
```

398 commits took 3 batched passes (each ~280s timeout).

## When `--ours` (live HEAD) is the RIGHT choice

- **Cumulative logs/registries** (`*-completions.md`, `marketplace-listings-registry.md`, `build_queue.json`, `jordan-queue.md`, handoff logs): ALWAYS keep HEAD.
- **Duplicate / add-add conflicts** where both sides are identical: keep HEAD.
- **Do NOT auto-resolve** production code/config where the incoming commit adds real content — inspect manually and stop the loop.

## Pitfalls inside the loop

- `GIT_EDITOR=true git rebase --continue` is REQUIRED — cron/shell has no `$EDITOR`; without it continue fails silently with "Terminal is dumb, but EDITOR unset".
- Stash unrelated working-tree edits BEFORE continuing (`git stash push -m "..." <file>`) — a stray modified file blocks the rebase with "cannot pull with rebase: Your index contains uncommitted changes".
- After `--ours` + `add -A`, confirm `git diff --name-only --diff-filter=U` is empty before continuing, else the loop stalls with "You must edit all merge conflicts" (harmless — re-run continue once staging is clean).
- A rewritten branch ends up ahead of the old remote (e.g. 410 vs 402 commits). Expected after a rewrite — re-point the remote and push `main` fresh; don't try to reconcile the old divergence.
- Restore stashed working-tree edits after the rebase completes (`git stash pop`), resolving conflicts to the rebase result.

## Prevention

- For a brain/vault repo, consider whether the full commit history is worth the rebase cost — a squash or shallow history keeps it flat.
- Standardize JSON writers on `ensure_ascii=True` (escaped form) to eliminate cosmetic Unicode-escaping conflicts that pad the conflict count.
