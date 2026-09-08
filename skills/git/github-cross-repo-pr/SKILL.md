---
name: github-cross-repo-pr
description: Create PRs from a restricted GitHub account that cannot fork via API. Covers manual fork workarounds, shared-history rebase, browser-based PR creation, and troubleshooting comparison failures.
---

# GitHub Cross-Repo PR — Restricted Account Workflow

Use this when the user's GitHub account cannot fork a repo via API ("You cannot fork this repository at this time") and needs to submit a cross-repo pull request.

## Prerequisites

- Local clone of the upstream repo with `origin` set to the upstream URL
- Branch with your changes ready locally
- GitHub personal access token with `repo` scope

## Workflow

### Step 1: Rebase your branch on upstream/main

```bash
git remote add upstream https://github.com/ORG/REPO.git
git fetch upstream main
git checkout YOUR_BRANCH
git rebase upstream/main
```

This ensures your branch shares commit history with upstream — required for GitHub's comparison tool to work across repos.

### Step 2: Create a fresh repo on GitHub (manual fork)

The API fork is blocked. Instead:
1. Go to `github.com/new`
2. Repository name: match the original repo name if possible
3. Description: clear fork intent (e.g. "Fork of ORG/REPO — X contribution")
4. **Public** — required for cross-repo PRs
5. **Do NOT initialize** with README, .gitignore, or license
6. Click **Create repository**

### Step 3: Push your rebased branch

```bash
git remote add new-fork https://USERNAME:TOKEN@github.com/USERNAME/NEW-REPO.git
git push new-fork YOUR_BRANCH:main --force
```

Use `main` as the target if that's the default branch. The `--force` is safe since this is a fresh empty repo.

### Step 4: Create PR via browser (API won't work for non-forks)

Open this URL format:

```
https://github.com/ORIGINAL_ORG/ORIGINAL_REPO/compare/main...YOUR_USERNAME:YOUR_REPO:YOUR_BRANCH
```

Example:
```
https://github.com/GOATNetwork/agentkit/compare/main...ProtoJay4789:agentkit:main
```

### Step 5: Verify the comparison

Before clicking "Create Pull Request", check that:
- **base repository:** `ORIGINAL_ORG/ORIGINAL_REPO`
- **base:** `main`
- **head repository:** `YOUR_USERNAME/YOUR_REPO`
- **compare:** `YOUR_BRANCH`
- The page shows actual file diffs (not "There isn't anything to compare")

### Step 6: Submit with description

Title: `<type>: <brief description>` (e.g. `feat: add compliance plugin`)
Body: Brief description of what was built and why.

## Troubleshooting

### "There isn't anything to compare"
**Cause:** Your branch doesn't share commit history with upstream's main.
**Fix:** Re-run Step 1 (`git rebase upstream/main`) and force-push again.

### "There isn't anything to compare" (after successful rebase)
**Cause 2:** The manual repo's default branch doesn't match what the compare URL expects. If your manual repo's default branch is `feat/compliance-plugin` but the URL targets `main`, GitHub can't resolve it.
**Fix:** Push to the manual repo's **default branch**: `git push new-fork YOUR_BRANCH:main --force`. The `:main` target tells GitHub which branch on the head repo to compare.

### "head: invalid" from API
**Cause:** The GitHub REST API rejects cross-repo PRs when the head repo isn't a proper fork — even after a successful shared-history rebase.
**Fix:** Skip the API entirely — use the browser URL in Step 4. The browser comparison tool is more permissive than the API.

### "You cannot fork this repository at this time"
**Cause:** GitHub account restrictions (common with flagged/limited accounts). The API returns this even if the repo's `allow_forking` is `true` — it's an account-level restriction, not a repo-level one.
**Fix:** Use Steps 2-3 (manual repo creation instead of fork). The manual repo works for cross-repo PRs once it shares commit history.

### Comparison shows the wrong base repo
**Cause:** The URL didn't specify the upstream org correctly.
**Fix:** Use the exact format: `/compare/main...YOUR_USER:YOUR_REPO:BRANCH` — the `...` is critical.

### "Contribute" button only shows local options (clone, SSH, download zip)
**Cause:** You are on your fork's Code tab, not the original repo's. The "Contribute -> Open Pull Request" button only appears on the original repo's Code tab when a fork with recent pushes exists.
**Fix:** Navigate to the original repo's Code tab (`github.com/ORIGINAL_ORG/ORIGINAL_REPO`) — the yellow banner appears there. Or skip the UI entirely and use the direct compare URL from Step 4.

### The fork/repo never appears in the head repository dropdown
**Cause:** The manual repo was not created via GitHub's Fork button, so GitHub does not recognize it as a fork. The dropdown only shows repos registered as proper forks.
**Fix:** Bypass the dropdown entirely — use the direct compare URL: `https://github.com/ORIGINAL_ORG/ORIGINAL_REPO/compare/main...YOUR_USER:YOUR_REPO:YOUR_BRANCH`

### Stale env token shadows the valid one
**Symptom:** `gh auth status` says "The token in GITHUB_TOKEN is invalid" even though
`curl -H "Authorization: token $(cat /root/.hermes/profiles/gentech/secrets/github-token)" https://api.github.com/user` returns 200 and identifies ProtoJay4789.
**Cause:** A dead `GITHUB_TOKEN` in the profile `.env` overrides the valid
`secrets/github-token` — scripts read env first. `.bashrc` may already be clean; the
`.env` copy is what poisons every session.
**Fix:** Copy the valid token into `.env` (`GITHUB_TOKEN=<value from secrets/github-token>`).
Also unset it defensively at the top of cron/one-shot scripts (`unset GITHUB_TOKEN`).

### Verify API results with the token, not bare curl
After `gh repo create`/push, a bare unauthenticated `curl api.github.com/repos/...`
can return a misleading 404 on a repo that actually exists. Always re-check with
`-H "Authorization: token $(cat /root/.hermes/profiles/gentech/secrets/github-token)"`
before declaring a push failed. (The King's Gambit push WAS live; the first re-check
was a red-herring 404.)

### GraphQL vs REST buckets are separate
`gh repo create`/`gh repo fork` go through GraphQL, which can be hard-capped at 0/0
on a flagged account while REST core is healthy (56/60). Work around repo creation
via REST (`POST /user/repos` + raw `git push`); forks have no workaround — the API
returns `403: You cannot fork this repository at this time`, an account restriction.
Queue the fork for a human one-click.

## Contribution-Ready Handoff (proven Aug 2, 2026)

When the fix is committed locally and ONLY the manual fork blocks the PR, don't
leave the work in limbo — hand it to Jordan as a queue item with everything he
needs to complete in one click:

1. Commit the fix locally, run the project's own test suite + typecheck, verify green.
2. Add to `HQ/jordan-queue.md` under a "Manual GitHub Forks" section:
   - Exact fork URL: `https://github.com/ORG/REPO/fork`
   - Commit hash + what it fixes + test status (e.g. "13/13 + 27/27 green")
   - The instruction: "Tell Gentech the fork URL → Gentech pushes branch + opens PR"
3. When Jordan returns the fork URL: add the fork as a remote, push the branch,
   open the PR via API or compare URL, verify it lists "Closes #NNN".

**Reality check (Aug 2, 2026):** of a batch of "manual forks", only some repo names
resolve — check each target with the API before queueing (Dexter-DAO/dexter and
near-examples/near-ai-agent-market both 404'd as stale names; only XRPLF resolved).
And someone else may already have fixed the issue you picked — OHM issue #771 was
submitted by another contributor hours before our sweep ran. Check issue/PR state
before committing effort; a "moot" contribution still teaches the pattern.

## User Preference Notes

- The user finds GitHub's branch/repo comparison UI confusing — always provide a direct clickable URL that bypasses dropdowns. Never ask the user to navigate dropdown menus.
- Prefer browser-based PR creation over API when GitHub account restrictions exist
- Verify the comparison page actually shows diffs before telling the user to click "Create Pull Request"
- If the direct URL does not work, rebase on upstream/main and push to the manual repo's default branch, then re-try the URL
- The `:YOUR_BRANCH` suffix in the compare URL is the branch name on the head repo — use `main` if that is what the manual repo's default is
- **When the user is on the GitHub compare page and it shows "There isn't anything to compare", first check if the head repo's default branch matches the compare target.** If the manual repo's default branch is `feat/compliance-plugin` but the URL targets `main`, push to `main` on the manual repo: `git push new-fork YOUR_BRANCH:main --force`
- **The `Contribute` button may not appear on the user's fork** — GitHub only shows it on the original repo's Code tab when a fork with recent pushes exists. Always provide the direct compare URL as the primary path.
- **If the user says "I hate the way GitHub has this laid out" or similar frustration, do NOT explain the UI again.** Just provide the direct URL and let them click it. The user has repeatedly expressed confusion with GitHub's compare UI — respect that and skip explanations.
