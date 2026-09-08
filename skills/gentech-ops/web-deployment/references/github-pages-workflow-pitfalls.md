# GitHub Pages deploy-workflow pitfalls (Aug 2026)

## 1. A Pages deploy workflow in a NON-Pages repo spams failing deploys on EVERY push

The vault repo (`GentechLabs/gentech-vault`) had a stray `deploy-portfolio.yml`
that fired an `actions/configure-pages` workflow on every push — but the vault
repo has **no Pages enabled**. Result: every brain-backup push spawned a deploy
run that failed in ~45s and **emailed the owner each time**.

Failure signature:
```
##[error]Get Pages site failed. Please verify that the repository has Pages
enabled and configured to build using GitHub Actions... Error: Not Found
```

Diagnose:
```bash
# does the repo even have Pages enabled?
gh api repos/<owner>/<repo>/pages --jq '.html_url // "NO PAGES ENABLED"'
# what runs did pushes trigger?
gh run list --repo <owner>/<repo> --limit 8 \
  --json createdAt,workflowName,conclusion,headSha \
  --jq '.[] | "\(.createdAt) | \(.workflowName) | \(.conclusion) | \(.headSha[0:7])"'
```

Fix: remove the misplaced workflow from the non-Pages repo, commit, push.
Verify the **fix commit did NOT spawn a new deploy run** — the newest entry in
`gh run list` should be the pre-fix commit, not yours. The deploy workflow
belongs ONLY in the repo that actually hosts the site and has Pages enabled.

## 2. The portfolio's GitHub home migrated from dead `ProtoJay4789` account to `GentechLabs`

*(Aug 30 update: the migration completed via repo RENAME — see section 3 below for the
provision-limbo that followed and the VPS-mirror fix. The old `ProtoJay4789.github.io`
URLs are permanently dead; the canonical repo is now `GentechLabs/gentechlabs.github.io`.)*

The old `ProtoJay4789` user account is gone:
- `github.com/ProtoJay4789` → 404
- `ProtoJay4789/ProtoJay4789.github.io` repo → 404

The portfolio now lives at **`GentechLabs/ProtoJay4789.github.io`**:
- Pages enabled, build_type `workflow`
- Live at `gentechlabs.github.io/ProtoJay4789.github.io/` (HTTP 200)
- Last deploy success

Local clones may still point `origin` at the dead account. The embedded token in
the remote URL masks the host, so inspect with `git remote -v` and fix:
```bash
git remote set-url origin https://github.com/GentechLabs/ProtoJay4789.github.io.git
```

**Signal note:** `gh` CLI authenticates as **GentechLabs**, so
`gh repo view ProtoJay4789/...` returns "Could not resolve to a Repository" —
that is the **migrated-repo signal**, not a permissions error. Don't misread it
as a token/scope problem.

Verify the live site with the `gentechlabs.github.io/...` URL (HTTP 200), and
confirm the deploy workflow lives in the GentechLabs repo whose Pages is enabled.
