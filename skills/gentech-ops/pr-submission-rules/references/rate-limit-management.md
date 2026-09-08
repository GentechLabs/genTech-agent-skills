# Rate Limit Management for PR Scans

When scanning 50+ open PRs (common in 3x daily cron jobs), GitHub API rate limits are a recurring constraint. Both GraphQL (used by `gh pr view`) and REST (used by `gh api repos/...`) have separate but exhaustible budgets.

## Allocation Strategy

| API | Budget | Rate | Best For | Limit Behavior |
|-----|--------|------|----------|---------------|
| **GraphQL** (gh pr view --json) | 5,000 points/hr | ~1 pt/call | Detail: mergeable, mergeStateStatus, statusCheckRollup, comments | Hard cap — once exhausted, ALL GraphQL calls fail for 1 hour |
| **REST** (gh api repos/...) | 5,000 requests/hr for authed users | 1 req/call | Bulk: state, title, mergeable (basic), comments count | Separate pool from GraphQL — can fall back when GraphQL is exhausted |

## Tiered Scan Strategy (Recommended for 50+ PRs)

### Tier 1: Initial Inventory (REST — cheapest path, always works)

Get the full PR list in one call:

```bash
gh api search/issues --method GET -f q='author:ProtoJay4789 type:pr is:open' \
  --jq '.items[] | {number, title: (.title[:60]), html_url, repository_url, updated_at}' \
  --paginate
```

Cost: 1 REST request + potentially a few more for pagination. Light.

### Tier 2: Batch Status Check (REST — for basic mergeable + state)

If you just need state + mergeable + title for all PRs, use REST (`gh api repos/`):

```bash
for pr in "owner/repo#123"; do
  repo=$(echo $pr | cut -d# -f1)
  num=$(echo $pr | cut -d# -f2)
  gh api repos/$repo/pulls/$num --jq '{state, mergeable, title}'
done
```

Cost: 1 REST req per PR. 59 PRs = 59 requests (~1.2% of hourly budget).

### Tier 3: Detailed Check (GraphQL — for mergeStateStatus, checks)

Only run GraphQL on PRs that need deeper investigation:
- BLOCKED or UNSTABLE PRs from Tier 2
- PRs with comments from bots
- PRs submitted in the last 24h

```bash
gh pr view <num> -R <repo> --json mergeable,mergeStateStatus,statusCheckRollup,comments,reviews
```

Cost: 1 GraphQL point per PR. Reserve for 10-20 PRs max per scan.

## Rate Limit Recovery

### When GraphQL is exhausted:
- **REST still works** (separate budget pool)
- Fall back to `gh api repos/owner/repo/pulls/N` for individual PR status
- MergeStateStatus is NOT available via REST — accept the BLOCKED/UNSTONE limitation
- Report which PRs couldn't get full detail due to rate limits

### When BOTH are exhausted:
- **This CAN happen** — 45+ REST calls + 45+ GraphQL calls in a single session can exhaust both budgets, especially if the REST budget was already partially consumed by prior operations (repo listing, user lookups, etc.)
- **The `gh api rate_limit` endpoint is misleading** — It reports the core endpoint limit (60/hr for the `/rate_limit` endpoint itself), NOT the REST API limit (5000/hr). When REST calls start returning 403, the `rate_limit` endpoint may still show 59 remaining because it's a different bucket. Do NOT trust `rate_limit` as a reliable indicator of REST availability.
- **Recovery:** Schedule the next scan run (3x daily at 8h intervals resets the budget). Log: "Rate-limited mid-scan — N PRs remaining unchecked. Will recheck on next run."
- **Fallback for this run:** Use the last known state from the previous scan. If the previous scan reported 0 CONFLICTING PRs, assume no new conflicts emerged (PRs don't spontaneously go CONFLICTING without a push to the base branch).

### Prevention:
- Use the tiered approach above (~60 REST calls = 1.2% budget, well within limits)
- Avoid mixing `gh pr view --json statusCheckRollup` for 50+ PRs in GraphQL — that's 50 points gone instantly
- When you need full detail for 50+ PRs, batch into 2 cron runs: one for REST inventory, one for GraphQL detail
- **Critical: Do NOT run Tier 2 (REST) and Tier 3 (GraphQL) scans in the same session for 45+ PRs.** The combined load can exhaust both budgets. Run REST first, then defer GraphQL detail to the next cron run.
- **Use `execute_code` with `terminal()` for batch scans** — this lets you handle partial failures per-PR instead of crashing the whole batch, and you can stop early if rate limit errors start appearing.

## REST-Based Inventory (Preferred Over Search API)

**The GitHub Search API (`gh api search/issues`) blocks user-based queries for ProtoJay4789** — returns HTTP 422 with `"The listed users cannot be searched either because the users do not exist or you do not have permission to view the users."` This is a persistent account-level restriction, not a transient error.

**Use the REST API instead — iterate known repos and filter by author:**
```bash
for repo in "owner/repo1" "owner/repo2"; do
  gh api "repos/$repo/pulls?state=open&per_page=10" --jq \
    '[.[] | select(.user.login == "ProtoJay4789") | {number, title, state, head: .head.ref, updated_at: .updated_at, mergeable: .mergeable}]'
done
```

**Cost:** 1 REST request per repo. 48 repos = 48 requests (~1% of 5,000/hr budget). Well within limits.

**Maintain a seed list** — the `pr-submission-rules` skill's "Known PR Targets" table serves as the seed list. When adding a new repo, add it to the table so future scans pick it up.

## Verified Behavior (Jul 19-20 2026)

- 50 individual `gh pr view --json mergeable,mergeStateStatus,...` calls exhausted GraphQL budget
- REST API remained available for `gh api repos/owner/repo/pulls/N` calls initially
- **New (Jul 20):** 45 REST calls + 45 GraphQL calls in the same session exhausted BOTH budgets
- **New (Jul 20):** The `gh api rate_limit` endpoint reported 59 remaining while REST calls returned 403 — the rate_limit endpoint shows a different bucket than the REST API
- The `search/issues is:merged` endpoint does NOT return `merged_at` via search index — verify with `gh pr view`
- After GraphQL exhaustion, `gh pr view --json anything` returns the "rate limit exceeded" error for ALL repos
- The REST API is the reliable fallback for basic state queries, but only when its own budget hasn't been exhausted
- **`gh api repos/owner/repo/pulls/N` returns `mergeable: null` when rate-limited** — not a transient compute delay, but a rate-limit signal. If ALL PRs return null, you're rate-limited, not waiting for GitHub to compute mergeability.
