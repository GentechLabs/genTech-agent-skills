# Multi-Writer Push Saga — Stale Branch Ref + Archive-Tree Trap (Aug 31, 2026)

Session: scrubbing a departed collaborator from the public Pages repo while ~8 cron writers push to it.

## The five-layer failure chain (each masked the next)

1. **Push rejected non-FF even though `HEAD~1 == origin/main`.** Verified via fetch that local parent matched remote tip, yet every push returned `! [rejected] (non-fast-forward)`.
2. **Root cause: `refs/heads/main` was a stale divergent commit.** The working tree was checked out on a detached HEAD (from repeated `git reset --hard` during earlier rebase fights) — or on another branch entirely (`git symbolic-ref HEAD` printed `refs/heads/gh-pages`). A push sends `refs/heads/<branch>`, NOT HEAD. All my "parent == tip" checks compared HEAD, which the push never used. `git branch -f main HEAD` fixed it instantly.
3. **Trap 1 — archive-restore clobber:** earlier attempt rebuilt a "clean tree" with `git archive <scrub-commit> | tar -x`. The scrub commit predated a big repo restructure; the diff vs remote showed **1,509 files / +138K lines** — resurrections of deleted pages. The push never landed (saved by the stale branch ref), which prevented publishing a clobbered site. **Never reconstruct trees from an old commit's archive in a live multi-writer repo.** Correct move: `git fetch && git reset --hard origin/main`, re-apply ONLY the intended minimal delta on the current tip, then push.
4. **Trap 2 — cron churn:** `scripts/build_queue.json` is edited in place by cron without committing. Sweeping it into a scrub commit (or `git add -A`) turns every rebase into a conflict. Commit only explicitly-touched paths.
5. **Trap 3 — parallel repos with same name:** `/root/vaults/gentech` (vault) and `/root/repos/gentechlabs.github.io` (site) both exist; deep in conflict-fighting, commands ran against the vault whose remote is the DEAD old `ProtoJay4789.github.io` mirror. Near-miss: almost pushed to the wrong repo. **Always `pwd` + `git remote get-url origin` before any destructive/push op in a multi-repo session.**

## The proven end-game pattern (works with hostile concurrent writers)

```bash
cd /root/repos/<repo>
git fetch origin --quiet
git reset --hard origin/main --quiet      # current tip is the ONLY base
python3 scrub_pass.py                      # minimal, targeted edits only
git add <explicit-paths>
git commit -m "..."
git branch -f main HEAD                    # ← THE fix: point the branch ref at what you verified
git push origin main
```

Then verify server-side, not locally:
```bash
git ls-remote origin refs/heads/main       # must equal your pushed SHA
curl -s -o /dev/null -w '%{http_code}' https://<site>/<scrubbed-path>   # 404 = scrubbed
```

## Detection cheat-sheet

- Push rejects non-FF but HEAD looks right → check `git rev-parse refs/heads/main` vs `git rev-parse HEAD`.
- Push sends the wrong ref → `git symbolic-ref HEAD` (detached?) + `git remote get-url --push origin` (right repo?).
- Huge unexpected diff vs remote → you rebuilt from an old tree; reset and replay the delta.
- Rebase loop with phantom commits replaying → stale rebase-merge state in .git; abort, verify tree, redo as fresh commit.

See also: `references/divergence-false-alarm-wrong-remote.md` (related wrong-remote failure) and SKILL.md Pitfall 10 (stale tracking ref lies).
