# Git Remote URL Audit — tokens in `.git/config`

## Why
Live credentials can be embedded directly in a repo's git remote URLs as
`https://USER:TOKEN@github.com/OWNER/REPO.git`. File-content scans never see
them — they live in `.git/config`, not in tracked files. The classic case is
a GitHub PAT (`ghp_...`) pasted into the remote to make pushes authenticate.
If `.git/config` is shared, backed up, or the remote is printed, the token leaks.

## How to detect
```bash
# Show all remotes with any embedded credentials
git remote -v

# Or grep the config directly (mask output to avoid echoing the token)
grep -E "https://[^/]+:[^/@]+@github.com" .git/config
```

## How to fix
1. Strip the token from the remote URL:
   ```bash
   git remote set-url origin "https://github.com/OWNER/REPO.git"
   git remote set-url org   "https://github.com/OWNER-ORG/REPO.git"
   ```
   (Repeat per remote, preserving the canonical GitHub host.)
2. Keep auth working via the credential store instead:
   - Git credential store: `~/.git-credentials` (ensure perms `600`).
   - Do NOT put the token back in the URL.
3. Verify auth still works after cleanup:
   ```bash
   git ls-remote <remote> main   # should succeed via credential store
   ```
4. Rotate the token anyway — it briefly lived in a config surface. Even if
   never pushed, rotation is the cheap, prudent step.

## Confirmation
`grep -c "ghp_\|gho_\|github_pat_" .git/config` → `0` after cleanup.

## Why the content scan misses it
`search_files`/`grep` over tracked files never inspects `.git/config`. Always
pair a file-content sweep with `git remote -v` on every local repo.
