# Keep-Both Merge for Human-Written Log Conflicts (Rebase Chain)

## Symptom
During a multi-commit `git pull --rebase` of a shared vault repo, a conflict in a
*narrative* markdown file (e.g. `01-HANDOFFS/treasury-completions.md`) where one side holds
old dated log entries and the other holds newer ones. Neither side should be discarded —
the history is a running log that must retain both.

## Root cause
Automated writers append dated entries to the same human-readable log. The two sides are not
duplicates — they are different date ranges. `git checkout --theirs` or `--ours` would
silently delete a range of log history.

## Fix — keep BOTH sides, then continue the chain
```bash
# 1. Identify the conflict(s)
git diff --name-only --diff-filter=U

# 2. Author the merged file by hand, keeping both dated sections
#    For a markdown log: old entries block + fresh entries block, concatenated.

# 3. Stage + continue, in order
git add <file>
GIT_EDITOR=true git rebase --continue   # repeat for each subsequent conflict in the chain
```

## Continuing a long rebase chain
This often occurs mid-chain where multiple commits (from another agent's batch) each touch
different files. After resolving one conflict, `git rebase --continue` surfaces the NEXT
commit's conflict. Iterate: resolve → `git add` → `GIT_EDITOR=true git rebase --continue`
until the chain completes, then `git push`.

If the chain fails at a non-content file, prefer `git rebase --abort` + fresh pull over
grinding through many manual resolutions — the abort discards only the half-applied chain,
and your committed work is preserved.

## Real-world (Aug 18, 2026)
Rebasing `main` onto `origin/main` on the ProtoJay4789.github.io vault produced:
- **Timestamp-only JSON conflicts** (`poe2-dashboard-data.json`, `build-health.json`) —
  resolved by keeping the NEWER timestamp (same spirit as Pitfall 12 header-only pattern)
- **A keep-both md conflict** in `treasury-completions.md` — old 08-06→08-15 entries +
  new 08-18 entries both retained

Resolution: keep both sides, `git add`, `GIT_EDITOR=true git rebase --continue` (repeated
across the chain), then `git push`. Confirmed clean at origin.

## See also (in git-conflict-resolution SKILL.md)
- Pitfall 10 — stale tracking ref causes false "up-to-date"
- Pitfall 12 — header-only JSON conflict markers (sed + json.dump)
- `references/orphaned-rebase-state-pitfall.md` — orphaned rebase blocks pulls
