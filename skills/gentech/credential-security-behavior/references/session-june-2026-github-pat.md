# Session: GitHub PAT Handling — June 19, 2026

## Timeline

1. User pasted a fine-grained PAT (`github_pat_11AV5GT4Q...`)
2. Agent attempted to write to `/root/.github-token`
3. Security redaction truncated display but file was written correctly (93 bytes)
4. Verification via `cat` showed truncated output; `wc -c` confirmed correct length
5. Git push failed — token lacked `Contents: Write` permission
6. User provided classic PAT (`ghp_Hg...yJ7W`)
7. Git push still failed — remote URL had old token embedded
8. Fixed remote URL, git push succeeded
9. `gh auth` failed — `GITHUB_TOKEN` env var had old token
10. Updated env var, `gh auth` succeeded

## Root Causes Found

| Issue | Cause | Fix |
|-------|-------|-----|
| API works but git push fails | Fine-grained PAT lacks `Contents: Write` | Use classic PAT with `repo` scope |
| Git push fails despite correct credentials | Remote URL has embedded token | `git remote set-url origin https://github.com/user/repo.git` |
| `gh auth` fails despite valid token | `GITHUB_TOKEN` env var has old token | Update env var in `~/.hermes/.env` |
| `git credential fill` returns wrong token | Gitconfig has `gh auth git-credential` in chain | Simplify to `helper = store` only |

## Commands Used

```bash
# Check token validity
curl -s -H "Authorization: Bearer $TOKEN" https://api.github.com/user

# Check scopes
curl -s -H "Authorization: Bearer $TOKEN" https://api.github.com/rate_limit | python3 -c "import sys,json; print(json.load(sys.stdin).get('resources',{}).get('core',{}).get('remaining','?'))"

# Fix remote URL
git remote set-url origin https://github.com/user/repo.git

# Fix gitconfig
cat > ~/.gitconfig << 'EOF'
[user]
    name = ProtoJay4789
    email = protojay4789@users.noreply.github.com
[credential]
    helper = store
EOF

# Update env var
sed -i 's/GITHUB_TOKEN=.*/GITHUB_TOKEN=new_token/' ~/.hermes/.env

# Verify credential helper
git credential fill <<EOF
protocol=https
host=github.com
EOF
```

## Key Insight

**Classic PATs with `repo` scope are the most reliable for agent automation.** They work for API, git, and GitHub CLI without per-repository permission configuration.

## Related Issues

- `gh auth status` shows "token is invalid" but API works → `GITHUB_TOKEN` env var override
- `git push` fails with "Invalid username or token" → Remote URL has embedded token
- `git credential fill` returns wrong token → Gitconfig has conflicting credential helpers
