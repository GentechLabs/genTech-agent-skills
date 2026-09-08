# Token Death & Account Disappearance — Recovery Reference

## Session: Jul 22, 2026 (14:00 UTC)

### What Happened

The `ghp_*` token stored in `secrets/github-token` and `~/.config/gh/hosts.yml` was revoked or expired. The `gh auth status` check confirmed:

> `The token in .../hosts.yml is invalid.`

Worse — the ProtoJay4789 account itself returned 404 from every URL (profile, repos, forks, PRs). This means either:
1. The account was deleted or suspended by GitHub
2. The account was renamed (and we're using the old handle)
3. The token was revoked and the account is in a restricted state

### Impact

- **All forks gone.** Every fork URL verified via browser returned 404.
- **All PRs are ghosts.** The REST API returned PR data (cached from the token's last valid state), but browser verification confirmed every single PR URL returned 404. The entire PR portfolio — 30+ open PRs across 25+ repos — no longer exists.
- **No new PRs or issues could be filed.** Cannot operate without a valid token.

### Detection Sequence

1. `gh auth status` → `X Failed to log in` + `token is invalid`
2. `gh api user` → `HTTP 200` (account active). If it returned 404, the account would be deleted. Note: `gh api repos/ProtoJay4789` returning 404 is NORMAL — that looks for a repo named "ProtoJay4789", not the user account.
3. Browser verification of PR URLs → all 404
4. Browser verification of fork URLs → all 404
5. Browser verification of account profile → 404

### What Was Lost

| Asset | Count | Details |
|-------|-------|---------|
| Open PRs | ~30 | Across 25+ repos (awesome lists, x402 ecosystem, protocol repos) |
| Forks | ~25 | One per target repo |
| Merged PRs | 3 | gold-402#39, xpaysh/awesome-x402#701, TencentDB-Agent-Memory#475 (approved) |
| Pending reviews | Unknown | All reviewer comments lost with the PRs |

### Recovery Steps (for Jordan)

1. **Generate a new Fine-Grained Token** with scopes: `repo`, `workflow`, `user`, `admin:public_key`
2. **Update both locations:**
   - `~/.config/gh/hosts.yml` — replace `oauth_token` value
   - `/root/.hermes/profiles/gentech/secrets/github-token` — replace contents
3. **Verify account status** — check if `ProtoJay4789` was renamed. If renamed, update the handle in all configs.
4. **Re-fork and re-submit** — the entire PR portfolio needs to be rebuilt from scratch. The diff content is lost with the forks.
5. **Update rotation file** — set `repos_pending` to the full seed list so the next cron run picks up from scratch.

### Prevention

- Monitor token expiry dates (GitHub tokens can have explicit expiration)
- Add a weekly token health check cron that runs `gh auth status` and alerts if invalid
- Store a backup token in a separate location (e.g., vault) for recovery
