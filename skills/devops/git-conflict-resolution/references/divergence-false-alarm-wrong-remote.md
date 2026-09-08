# Pitfall 15 — "Divergence" False Alarm: main Tracks the WRONG Remote (Aug 26, 2026)

## Symptom
`git rev-list --left-right --count @{u}...HEAD` shows a huge divergence (409 local vs 473
remote commits) and you're about to force-push or abort — but nothing is actually broken.
The "divergence" is against the WRONG remote.

## Root cause
A repo has MULTIPLE remotes, and `main` was tracking `origin` (the old, superseded
GitHub-Pages repo) instead of the canonical sync remote (`vault` → `GentechLabs/gentech-vault`).
The remote-only commits (all "Sync POE2 builds") lived on the *old* repo's remote, not the
real brain remote. `@{u}` expands to the configured upstream — which was `origin`, not
`vault`. So every sync check falsely reported a divergence even though the vault was
perfectly in sync with the actual brain remote.

## Diagnosis — check WHICH remote @{u} points to BEFORE panicking
```bash
cd /root/vaults/gentech
git remote -v                      # list ALL remotes (vault, origin, hub, ...)
git rev-parse --abbrev-ref @{u}    # ← WHICH remote? origin/main or vault/main?
# If @{u} is NOT the canonical sync remote, the divergence number is meaningless.

# Compare against the CORRECT remote explicitly, not @{u}:
git fetch vault main
git rev-list --left-right --count vault/main...HEAD   # 0 0 = actually in sync
```

## Fix — set canonical remote as upstream so future checks + pulls are correct
```bash
git branch --set-upstream-to=vault/main main
git rev-parse --abbrev-ref @{u}    # now → vault/main
```

## Before force-pushing local→remote, confirm what remote-only files you'd lose
List remote-only files and check they're (a) regenerable, (b) submodule gitlinks, or
(c) genuinely unique. Preserve any unique binary via `git show origin/main:<path>` before
overwriting. Here the only unique file was a Vanito MP4 (20MB, gitignored) — extract it,
then `git add -f` it back after the reconcile.

## Key lesson
`git rev-list @{u}...HEAD` only tells you about the *configured tracking remote*. In a
multi-remote vault it can produce a scary false divergence. Always identify the canonical
remote first, then compare against it explicitly. Also: after re-enabling GitHub transfers
on a new (non-flagged) account, the old account's rate-limit reason for avoiding GitHub no
longer applies — but keep pushes small/batched and never embed PATs, or the new account gets
flagged too.
