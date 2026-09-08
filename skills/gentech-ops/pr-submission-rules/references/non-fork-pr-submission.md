# Non-Fork PR Submission — Browser Fallback

## Problem
GitHub account ProtoJay4789 cannot fork certain repos via the API. The endpoint `POST /repos/{owner}/{repo}/forks` returns "You cannot fork this repository at this time" even for public repos with `allow_forking: true`. This is an account-level restriction.

Creating a manual repo at `github.com/new` and pushing code does NOT create a real GitHub fork. The API returns `"fork": false, "parent": null`, and cross-repo PRs fail with `"field": "head", "code": "invalid"`.

## Workflow

### Step 1: Set up a manual repo with the upstream's code

```bash
# Create repo at github.com/new (same name as upstream for clarity)
# Do NOT initialize with README, .gitignore, or license

# On your local machine:
git clone https://github.com/<UPSTREAM_OWNER>/<REPO>.git /tmp/fresh-repo
cd /tmp/fresh-repo
git remote rename origin upstream
git remote add origin https://github.com/ProtoJay4789/<REPO>.git
git push -u origin main
```

### Step 2: Add your changes on a feature branch

```bash
git checkout -b <feature-branch>
# ... make changes, commit ...
git push -u origin <feature-branch>
```

### Step 3: Rebase onto upstream main (critical — without shared history the compare page won't work)

```bash
git fetch upstream main
git rebase upstream/main
git push origin <feature-branch> --force
```

After rebase, the branch shares git history with the upstream. Verify with `git log --oneline | head -3` — the first commit should be from the upstream's main.

### Step 4: Submit PR via browser compare link

Format:
```
https://github.com/<UPSTREAM_OWNER>/<REPO>/compare/<BASE>...<FORK_OWNER>:<FORK_REPO>:<BRANCH>
```

Example (GOATNetwork/agentkit, verified Jul 28 2026):
```
https://github.com/GOATNetwork/agentkit/compare/main...ProtoJay4789:agentkit:main
```

Send this link to the user (Jordan). They open it in browser, click "Create Pull Request," and paste the description.

### Step 5: Split long PR descriptions into parts

Telegram truncates messages over ~4000 chars. Split the PR body into 2-3 parts that the user can copy-paste sequentially into the PR description field. Each part should end at a logical section break.

## Rebasing after the repo exists (if compare shows "nothing to compare")

```bash
cd <local-repo>
git remote add upstream https://github.com/<UPSTREAM>/<REPO>.git
git fetch upstream main
git checkout <your-branch>
git rebase upstream/main
git push <fork-remote> <your-branch>:main --force
```

The compare link then shows the diff.

## Limitations
- The API method (`gh pr create`) will NEVER work for cross-repo PRs from a non-fork repo. The browser method is the only path.
- After rebasing, the fork's `main` branch becomes different from upstream's main. This is fine — the feature branch is what matters for the PR.
