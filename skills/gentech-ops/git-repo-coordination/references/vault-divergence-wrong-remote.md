# Vault "Divergence" False Alarm — wrong remote tracking (Aug 26, 2026)

## Symptom
`git rev-list --left-right --count @{u}...HEAD` reports a terrifying divergence
(e.g. 410 remote-only vs 473 local), and `git pull --rebase` / `git merge` both fail on
`build_queue.json` + brain files. Handoffs look "lost" and the sync appears hopelessly broken.
It is tempting to force-push and risk brain work.

## Real cause
The repo has MULTIPLE remotes, and `main` is tracking a **legacy/stale** one — not the canonical
sync remote. In the Gentech vault:
- `vault` → `GentechLabs/gentech-vault` — the NEW canonical brain remote (use this)
- `origin` + `hub` → `ProtoJay4789.github.io` — the OLD GitHub-Pages repo (legacy)
- `desmonds` → unrelated

`main` was tracking `origin` (the old Pages repo), whose only commits are automated
`Sync POE2 builds` jobs. Comparing against `origin` made a healthy repo look irreconcilably broken.

## Diagnosis — identify WHICH remote is upstream BEFORE touching anything
```bash
git remote -v                     # list all remotes + URLs — spot the legacy ones
git rev-parse --abbrev-ref @{u}   # WHICH remote does main track? (origin? vault?)
# If @{u} is a legacy/old-account remote → false alarm, not real breakage.
```

## Fix — re-point `main` to the canonical sync remote, then reconcile against THAT
```bash
git branch --set-upstream-to=vault/main main
git fetch vault main
git rev-list --left-right --count vault/main...HEAD   # re-check — likely near-clean
```

## If it IS genuinely diverged against the correct remote
- List remote-only files that are MISSING locally and back up any unique blobs first:
  ```bash
  git diff --name-only HEAD..vault/main | while read f; do [ ! -e "$f" ] && echo "MISSING: $f"; done
  # submodule gitlinks (mode 160000) point to their own repos — not real content loss.
  # a real blob (binary) IS unique — extract before reconcile:
  git show "vault/main:<path>" > /tmp/preserve.bin
  ```
- Force-push the true source of truth (usually local = the brain/handoffs):
  ```bash
  git push vault main --force
  ```
- GH013 secret-scan (git-repo-coordination Pitfall 10) scans every commit in a force-push — review history first.

## Rule of thumb
A "divergence" that looks catastrophic but whose remote-only commits are all one automated job's
name (e.g. "Sync POE2 builds") is usually the WRONG-REMOTE false alarm, not real breakage.
Check `@{u}` + `git remote -v` BEFORE force-pushing. Re-point `main` to the canonical remote first.
