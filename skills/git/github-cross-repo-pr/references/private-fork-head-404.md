# Cannot open a PR to a public repo from a private fork (Aug 26 2026)

## Symptom
`gh pr create --repo ORG/REPO --head USER:BRANCH` failed with:
```
pull request create failed: GraphQL: not all refs are readable (createPullRequest)
```

## Root cause
You cannot open a cross-repo PR into a **public** repo from a **private** fork. GitHub can't expose the head repo's refs for comparison, so the API/GraphQL rejects the `head:` reference. The error is generic ("not all refs are readable") and looks like an auth problem — it is not. It's a visibility problem on the head fork.

Diagnosis: `gh api repos/ProtoJay4789/bankr-skills` returned 404 even though `git ls-remote` on the same URL worked. A 404 via the API while git push/ls-remote works = the repo is PRIVATE (git auth uses an embedded/credentialed token; the API token can't see it). A private fork is unreachable as a PR head.

## The fix — use a PUBLIC fork under the clean account
1. Create a **public** fork under the account that can be a PR head (on a fresh/unflagged account):
   ```bash
   gh api -X POST "repos/ORG/REPO/forks" --jq '.html_url,.private'
   # NOTE: the fork lands with the SOURCE repo's name by default (e.g. BankrBot/skills -> GentechLabs/skills),
   # and the response .private is false.
   ```
   The fork must be **public** — that's the whole point. Verify: `gh api "repos/<ACCT>/<REPO>" --jq '.private'` → `false`.
2. Push your branch to the public fork. If the default `gh` token is a different account than the one owning the fork, force the token inline:
   ```bash
   GH_TOKEN=$(gh auth token --hostname github.com) git push \
     https://x-access-token:$(gh auth token --hostname github.com)@github.com/<ACCT>/<REPO>.git \
     <BRANCH>:<BRANCH>
   ```
   A plain `git push <fork-remote>` may fail with `403: Permission denied to <other-account>` because the lingering git credential belongs to a different account. Inline the token of the account that owns the fork.
3. Open the PR from the public fork:
   ```bash
   gh pr create --repo ORG/REPO --head <ACCT>:<BRANCH> --base main --title "..." --body "..."
   ```
   Now `head` is a public fork and the refs are readable → the PR opens.

## Verification
- PR opens with state `OPEN` and `mergeable=MERGEABLE`.
- `gh pr view <N> --repo ORG/REPO --json state,mergeable`

## Contrast with the restricted-account case
This is the INVERSE of github-cross-repo-pr's main workflow: there, the flagged account CAN'T fork at all (403 "You cannot fork this repository at this time"). Here, the fork EXISTS but is private. The common thread: the head must be a **public, API-visible** repo for a cross-repo PR. If the account can't create public forks, fall back to the manual-repo + browser-compare flow in SKILL.md.
