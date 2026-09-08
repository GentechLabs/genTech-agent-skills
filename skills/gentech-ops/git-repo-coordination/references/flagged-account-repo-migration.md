# Migrating Repos Off a Flagged Account to a Clean Account

**Proven Aug 24, 2026** — moving repos from `ProtoJay4789` (flagged, throttled to the anonymous 60 req/hr tier) to `GentechLabs` (clean, normal 5000/hr).

## Core rule
Do NOT rely on GitHub's transfer API or the flagged account's own API. A flagged account returns 0 repos anonymously and its API is unreliable/403s. **Use the local clones as ground truth and push them to the clean account directly.**

## Workflow
1. For each repo, find the local clone — check BOTH `/root` and `/root/repos/` (many live under `/root/repos/`).
2. Create the target repo on the clean account via REST (NOT `gh repo create`, which routes through GraphQL):
   ```
   curl -X POST https://api.github.com/user/repos \
     -H "Authorization: token <TOKEN>" -H "Accept: application/vnd.github+json" \
     -d '{"name":"<name>","public":true}'
   ```
3. Point origin to the clean account and push the local branch:
   ```bash
   git remote set-url origin https://x-access-token:<TOKEN>@github.com/<CleanAcct>/<name>.git
   git push -u origin HEAD:main
   ```
4. Verify public visibility:
   ```bash
   curl -H "Authorization: token <TOKEN>" https://api.github.com/repos/<CleanAcct>/<name>  # private: false
   ```

## Pitfalls
- **Local repos may live under `/root/repos/` not `/root/`** — check both before concluding a repo is missing.
- **Big binaries in git history = flag trigger AND push blocker.** A repo whose history carries a >100MB binary (node_modules, Chrome-headless shells, build toolchains) fails push with `GH001: Large files detected ... exceeds 100.00 MB`. "Excessive bandwidth / big binaries in repos" is ALSO a documented GitHub account-flag trigger (Acceptable Use §9). **Do NOT force-push bloat onto the clean account.** Options: (a) rewrite history to strip the binary (filter-branch / filter-repo), or (b) leave the repo local-only — the deployed artifact usually already lives on the VPS. Risking the clean account over one bloated repo is not worth it.
- **Never push a vault mid-rebase.** If `.git/rebase-merge/` is present (active git rebase), do NOT force-push — risks losing brain state. Finish the rebase first, then swap the remote.
- **Org transfer is manual, no API.** Moving a repo from a personal account into an org's ownership is a web-UI step; don't expect an API to do it.
- **Pace the creates** (~1s sleep between) and prefer `git push` (git protocol — never counted against API) over more REST calls.

## Overlap note
This complements the flag-rules knowledge in `github-rate-limit-scheduler` (user-owned, not curator-managed). Both cover the same territory; consider consolidating if that skill is ever adopted.
