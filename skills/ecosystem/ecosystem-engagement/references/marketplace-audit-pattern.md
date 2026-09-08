# Marketplace Audit Pattern

Run periodically (weekly or after any new platform integration) to catch stale listings, unsubmitted PRs, and new opportunities.

## Audit Checklist

1. **List all marketplaces we're on** — OKX AI, Swarms, Atelier, x402 Bazaar, awesome lists, Coinbase Bazaar, Agentic.Market
2. **Check each listing for staleness** — Is the description current? Are new endpoints listed? Is pricing up to date?
3. **Cross-reference PRs against reality** — For every PR in the portfolio, verify it actually exists and is still open/merged
4. **Check for unsubmitted drafts** — Scan `10-Labs/` for PR-ready files that were written but never submitted
5. **Check for new platforms** — Any new agent marketplaces, x402 directories, or A2A registries launched since last audit
6. **Update the audit document** — Save findings to `10-Labs/marketplace-audit.md`

## Stale Fork Cleanup

When the GitHub account has 100+ repos, many are stale forks from PR submissions that were merged or abandoned.

### Cleanup Criteria
- **Stale forks** — forks where no PR was ever submitted, or the PR was merged and the fork is no longer needed
- **Stale own repos** — hackathon projects, experiments, superseded tools that are no longer maintained

### Cleanup Workflow
1. List all repos: `curl -s -H "Authorization: Bearer $GITHUB_TOKEN" "https://api.github.com/users/ProtoJay4789/repos?per_page=100&type=all&sort=updated"`
2. Categorize: active own, active forks (PRs submitted), stale forks (no PRs), stale own (abandoned)
3. Delete stale forks: `gh api -X DELETE repos/ProtoJay4789/<name>`
4. Archive stale own repos: `gh repo edit ProtoJay4789/<name> --visibility private` or delete if truly abandoned
5. Update the audit document with counts

### Pitfalls
- Don't delete forks that have open PRs — verify PR status first
- Don't delete repos that are referenced in the vault — check for vault references first
- Some repos (portfolio, profile) should be kept even if stale
