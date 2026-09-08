# PR Status Sweep — Nightly Protocol

Run this during Brain Audit Mode when there are no buildable Gentech items. Checks all open PRs across GenTech's ecosystem listings and active repos in one pass.

## When to Run

- Brain Audit Mode (Step 2.5) — after confirming no buildable items
- Any session where Jordan asks "what's the status of our PRs?"
- Before generating the Morning Digest to include fresh PR status

## The Sweep

### 0. Comprehensive Cross-Repo Discovery (Full Sweep)

**The PR portfolio is NOT the source of truth for which PRs exist.** The portfolio only tracks PRs that were previously discovered and logged. PRs may exist that the portfolio doesn't know about — submitted from a fork whose name differs from the expected one, submitted by another agent, or never recorded. Always run a cross-repo discovery before trusting the portfolio's completeness.

Build a hashmap of ALL upstream repos where GenTech has submitted or could have submitted PRs, then query each repo's PR list filtered by ProtoJay4789 head label:

```bash
declare -A REPOS=(
  ["pay-skills"]="solana-foundation/pay-skills"
  ["x402"]="x402-foundation/x402"
  ["awesome-erc8004"]="sudeepb02/awesome-erc8004"
  ["awesome-ai-agents"]="caramaschiHG/awesome-ai-agents-2026"
  ["awesome-web3"]="ahmet/awesome-web3"
  ["awesome-agent-cortex"]="0xNyk/awesome-agent-cortex"
  ["awesome-agents"]="Scottcjn/awesome-agents"
)

for name in "${!REPOS[@]}"; do
  repo="${REPOS[$name]}"
  result=$(gh api "repos/$repo/pulls?state=all&per_page=10&head=ProtoJay4789:" \
    --jq '.[] | {number, state, title: (.title[0:60]), html_url}' 2>/dev/null)
  if [ -z "$result" ]; then
    # Fallback: list all open PRs and filter by head label client-side
    result=$(gh api "repos/$repo/pulls?state=all&per_page=5" \
      --jq '.[] | select(.head.label | startswith("ProtoJay4789")) | {number, state, title: (.title[0:60]), html_url}' 2>/dev/null)
  fi
  echo "=== $name ($repo) ==="
  echo "${result:-No GenTech PRs found}"
done
```

**Why the two-step query:** The `head=ProtoJay4789:` server-side filter may return empty if GitHub's PR index is behind or the filter syntax is too specific. The fallback (no head filter, then client-side `.head.label` check) catches everything GitHub has.

**Why this beats the portfolio-only approach:** The portfolio may be stale, missing entries, or wrong about PR numbers. The cross-repo sweep is the ground truth. Proven Jul 24, 2026: the portfolio tracked 4 PRs, but the full sweep found 10 — 6 were missing entirely (awesome-web3 #733, awesome-agent-cortex #43/#44, awesome-agents #40, awesome-ai-agents-2026 #455, pay-skills #154).

**After the sweep, reconcile with the portfolio:**
- Remove PRs from the portfolio that don't appear in the sweep (possible phantom or wrong org/repo)
- Add PRs the sweep found but the portfolio missed
- For any PR the sweep expected but didn't find, check the **repo organization** — a wrong org returns a silent empty result, not a 404 error. The `gh api repos/wrong-org/repo/pulls` just returns empty, making it look like there are no PRs when the problem is simply the wrong org name.

### 1. Read the PR Portfolio

```bash
cat /root/vaults/gentech/10-Labs/pr-portfolio.md
```

This is the canonical list of ALL previously-discovered PRs. It is NOT the source of truth for existence — that's the cross-repo sweep above. Use the portfolio to track which PRs have been logged and their history, not to discover new or missed PRs.

### 2. Verify PR Numbers Exist Before Checking Status

**Do not assume PR numbers in the queue or portfolio are real.** PRs can be deleted by maintainers, renumbered during repo migration, or simply never created (phantom PRs from stale queue notes).

**Preferred method — REST API PR list filtered by head label:**

This is the most reliable technique. Query the upstream repo's open PRs and filter by your username. This catches PRs from any fork name, regardless of what the fork is actually called:

```bash
gh api repos/<owner>/<repo>/pulls --jq '.[] | select(.head.label | startswith("ProtoJay4789")) | {number, state, title: .title[0:60]}'
```

**Fallback method — REST API create attempt (422 confirmation):**

When `gh pr list` (GraphQL) returns empty due to rate limiting, or when you need to confirm a specific branch's PR exists, use the create endpoint. A 422 "already exists" response is definitive proof the PR is real:

```bash
gh api repos/<owner>/<repo>/pulls --method POST \
  -f head='ProtoJay4789:<branch>' \
  -f base='main' \
  -f title='test'
# 422 "already exists" = PR confirmed real
# 201 = PR was just created (abort — don't actually create it)
# 403 = rate limited, stop
```

**Why this matters:** `gh pr list` uses GraphQL which has a SEPARATE rate limit bucket from REST. A GraphQL rate limit hit returns empty results silently — you will see zero PRs even when PRs exist. The REST create endpoint bypasses this entirely. This technique was proven Jul 22, 2026: `gh pr list` returned empty for pay-skills, but the create endpoint confirmed PRs #190 and #192 both existed.

**⚠️ 201 = portfolio branch name may be wrong.** A 201 response (successful creation) does NOT necessarily mean the PR was genuinely unsubmitted — it often means the portfolio's branch name is stale. In Jul 2026, `gh api repos/sudeepb02/awesome-erc8004/pulls --method POST -f head='ProtoJay4789:format-ordering'` returned 201 (created PR #87) because PR #82 used `main` as the head branch, not `format-ordering`. The branch `format-ordering` existed on the fork but had never been a submitted PR — the actual PR was from a different branch.

**Recovery when 201 happens:** Immediately:
1. **Close the accidental PR:** `gh api repos/<owner>/<repo>/pulls/<number> --method PATCH -f state='closed'`
2. **Log it** — note the PR number, the branch used, and that it was closed
3. **Check the real PR's actual head branch** via the upstream open-PR list filtered by username:
   ```bash
   gh api repos/<owner>/<repo>/pulls --jq '.[] | select(.head.label | startswith("ProtoJay4789")) | {number: .number, head: .head.label, title: .title[0:60]}'
   ```
4. **Update the portfolio** with the correct branch name — branch-field freshness matters

**Quick existence check — single PR by number:**

```bash
gh api repos/<owner>/<repo>/pulls/<number> --jq '{number: .number, state: .state}' 2>&1
```

If the response is `404 Not Found`:
- The PR number does not exist in that repo
- Check if the repo's PRs skip that number (e.g. #153 → #155 with no #154)
- Check if the PR was on a different repo than expected (e.g. a fork vs upstream)
- **Do NOT mark the PR as "closed" or "rejected"** — it was never created
- Update the queue/portfolio to remove the phantom reference
- If the queue item was blocked on this PR, unblock it and update the detail field

**⚠️ 404 from wrong org — a distinct pitfall from phantom PRs.** A 404 for `pulls/<number>` does NOT mean the PR was deleted; it means the repo itself doesn't exist at that URL. If you checked `solana-foundation/awesome-erc8004` and got 404, but the PR was actually on `sudeepb02/awesome-erc8004`, the 404 is a wrong-org error, not a phantom PR. Differentiating between the two is critical:
- **Phantom PR:** The upstream repo exists but the PR number doesn't. Confirmed by running `gh api repos/<owner>/<repo>` (repo exists) then `pulls/<number>` (404).
- **Wrong org:** The upstream repo itself returns 404. Confirm by checking the repo's existence: `gh api repos/<owner>/<repo>` returns 404. Then search for the correct org:
  ```bash
  gh search repos awesome-erc8004 --limit 5 --json nameWithOwner
  ```
  Proven Jul 24, 2026: `gh api repos/solana-foundation/awesome-erc8004` returned 404, but `sudeepb02/awesome-erc8004` existed with PR #82 alive.

### 2.5 Stale `hosts.yml` token — the working token lives in the `origin` remote URL

**⚠️ Proven Aug 7, 2026: the token in `~/.config/gh/hosts.yml` can itself be stale (HTTP 401 "Bad credentials") while the repo is perfectly reachable.** The valid token is frequently embedded directly in the `origin` remote URL (form `https://USER:TOKEN@github.com/...`). This is NOT the same as the GITHUB_TOKEN-env-var conflict described elsewhere — here `hosts.yml` is the *only* token source and it is wrong.

**Symptom:** every per-PR check returns `state=None` / `Bad credentials` / HTTP 401, even though the rate-limit endpoint returns a healthy budget and `git` push/pull to `vault` works (git uses the remote-URL credential, not `hosts.yml`).

**Diagnose before trusting an empty PR list:**
1. Test the `hosts.yml` token on ONE known PR. If 401, it is stale — don't loop the whole portfolio on a dead token.
2. Extract the working token from the origin remote URL and test that:
   ```bash
   ORIGIN_URL=$(git remote get-url origin)
   GH_TOKEN=$(echo "$ORIGIN_URL" | sed -E 's#https://[^:]+:([^@]+)@.*#\1#')
   curl -s -H "Authorization: token $GH_TOKEN" \
     "https://api.github.com/repos/solana-foundation/pay-skills/pulls/154" | \
     python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('state'), d.get('message'))"
   ```
   A `state: open` (no `message`) confirms the remote-URL token works.

**Correct endpoint — don't drop the `pulls` segment.** The per-PR status endpoint is:
```
GET https://api.github.com/repos/{owner}/{repo}/pulls/{number}
```
`repos/{owner}/{repo}/{number}` (omitting `pulls`) returns **404**, which a hasty check can misread as a phantom/missing PR. When looping in code, use the full `pulls/{number}` path.

**Looping quirk:** prefer Python (`urllib`/`subprocess curl`) over a shell `for` loop interpolating `$GH_TOKEN` — a shell loop can silently drop or mangle an embedded token and return 401 for every item, which looks like "all PRs gone" when they are actually all open.

| Scenario | hosts.yml token | origin-remote token | Action |
|----------|----------------|--------------------|--------|
| Token death | ❌ 401 | ❌ 401 | Renew credential (Jordan) |
| **Stale hosts.yml only** | ❌ 401 | ✅ 200 `state: open` | Use remote-URL token for the sweep |

### 3. Check Each PR via REST API

GitHub GraphQL has a lower rate limit than REST. Use REST for bulk sweeps:

```bash
# Pattern for each PR:
gh api repos/<owner>/<repo>/pulls/<number> --jq '{state: .state, merged: .merged, title: .title, updated_at: .updated_at}'
```

Key fields to check:
- `state` — "open", "closed"
- `merged` — true/false (false + closed = rejected or abandoned)
- `updated_at` — when the last activity happened
- `mergeable` — "true", "false", or null (not yet computed)

### 4. Check Rate Limit First

```bash
gh api rate_limit --jq '{core: .rate.remaining, graphql: .graphql.remaining, search: .search.remaining}'
```

- REST: 5000/hr
- GraphQL: 5000/hr
- If GraphQL is exhausted, use REST only
- If REST is low (< 100), prioritize the most important PRs

### 5. Handle Rate Limit Exhaustion

When the GitHub API returns `403 rate limit exceeded` mid-sweep:

1. **Stop immediately** — do not retry; every retry burns another request against the exhausted budget
2. **Note which PRs were checked and which remain** — record the last checked PR number
3. **Report the partial result** in the Morning Digest with a note that the sweep was incomplete
4. **The rate limit resets at the top of each hour** — if the session continues past the reset, resume the sweep
5. **For unauthenticated requests** (no `gh` auth): the limit is only 60/hr. Authenticate with `gh auth status` first. If unauthenticated, the sweep will exhaust the budget on the first few PRs.

### 6. Update the PR Portfolio

When a PR status changes:
- Open → Closed (no merge): mark as `🔴 Closed (no merge)` and note the date
- Open → Merged: mark as `✅ Merged` and remove from build queue if applicable
- Closed → Reopened: update status back to `🟢 Open`
- **Phantom PR** (404): mark as `❌ Never existed` and remove from queue dependencies

### 7. Propagate to Build Queue

If a PR status change affects a queue item (e.g. PR was closed without merge, or a blocker was resolved), update the queue item's `detail` or `status` field. Then regenerate handoffs.

For phantom PRs specifically:
- Remove the "blocked on PR #X" language from the queue item's `detail` field
- If the item was blocked solely on that PR, change status from `blocked` to `pending`
- Add a note explaining the PR never existed and what the real next step is

## Mass 404 Detection and Handling

> **⚠️ First observed Jul 26, 2026: ALL 10 PRs across 8 repos returned 404 simultaneously.**
> This is distinct from individual phantom PRs, wrong-org errors, or rate-limit exhaustion.
> It is a mass-deletion event — all our PRs were systematically removed by maintainers.

### When to Suspect a Mass 404 Event

When every PR in the portfolio returns 404 and the following are also true:

1. **Account is alive:** `gh api user` returns valid ProtoJay4789 data, not 404
2. **All upstream repos exist:** `gh api repos/<owner>/<repo>` returns 200 for every repo in the portfolio
3. **Other users' PRs are visible:** `gh api repos/<owner>/<repo>/pulls?state=all&per_page=5` returns real data from other contributors
4. **The PR numbers are skipped in the repo's PR sequence:** Listing all PRs shows #153 → #155 (no #154), or #207 → #208 with no #190/#192 in between
5. **REST API is working (rate limit available):** `gh api rate_limit --jq '.rate.remaining'` shows > 10 remaining

If ALL five conditions hold, this is a mass deletion — not a token issue, account issue, or rate limit problem.

### Diagnostic Sequence

```python
import urllib.request, json

portfolio = [
    ("solana-foundation", "pay-skills", 154),
    ("solana-foundation", "pay-skills", 190),
    ("solana-foundation", "pay-skills", 192),
    ("x402-foundation", "x402", 2905),
    # ... include all portfolio entries
]

def check_pr(owner, repo, num):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{num}"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github.v3+json")
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        return f"EXISTS: state={data.get('state')}, merged={data.get('merged')}"
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}"

# Phase 1: Check ALL PRs in portfolio
for owner, repo, num in portfolio:
    print(f"  PR #{num} ({owner}/{repo}): {check_pr(owner, repo, num)}")

# Phase 2: If ALL are 404, verify account health
resp = urllib.request.urlopen(urllib.request.Request(
    "https://api.github.com/user",
    headers={"Accept": "application/vnd.github.v3+json"}
), timeout=10)
user = json.loads(resp.read())
print(f"Account: {user.get('login')} — active: yes")

# Phase 3: Cross-check by listing ALL recent PRs in each repo
for owner, repo in [repo for _, repo in _]:  # unique repos
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all&per_page=10"
    resp = urllib.request.urlopen(urllib.request.Request(
        url, headers={"Accept": "application/vnd.github.v3+json"}
    ), timeout=10)
    prs = json.loads(resp.read())
    our_prs = [p for p in prs if p.get("head", {}).get("label", "").startswith("ProtoJay4789")]
    print(f"  {owner}/{repo}: {len(prs)} recent PRs, {len(our_prs)} from us")
    for p in prs[:3]:
        print(f"    PR #{p['number']}: {p['user']['login']} — {p['title'][:50]}")
```

**Output pattern that confirms mass deletion:**
```
  PR #154 (solana-foundation/pay-skills): HTTP 404
  PR #190 (solana-foundation/pay-skills): HTTP 404
  PR #192 (solana-foundation/pay-skills): HTTP 404
  ...
Account: ProtoJay4789 — active: yes
  solana-foundation/pay-skills: 5 recent PRs, 0 from us
    PR #205: x402engine — Add x402engine gateway provider
    PR #204: MacroPulse — Add Macro Pulse (finance) provider
    PR #203: Utilia — Add Utilia Solana Preflight
```

If every repo shows "0 from us" while showing valid PRs from other users, the deletion is confirmed across the entire portfolio.

### Confirming a Single Repo's PR Sequence (Missing Number Detection)

To distinguish "PR was deleted" from "PR number never existed" in a single repo, check the surrounding PR numbers. A PR number that was genuinely used (then deleted) would leave a gap in the sequence. A PR number that was never claimed would not:

```bash
# Check PR sequence around a suspected deletion
# If PR #154 returns 404, check #153 and #155
gh api repos/solana-foundation/pay-skills/pulls/153 --jq '{number, state, title: .title[0:40]}'
gh api repos/solana-foundation/pay-skills/pulls/155 --jq '{number, state, title: .title[0:40]}'
```

If #153 and #155 both exist with PRs from other users, and #154 is purely missing (not merged, not closed — just gone), the PR at #154 was deleted. A merged PR retains its number. A closed-but-unmerged PR also retains its number. A 404 means the PR record was physically removed from the database — this only happens when the PR branch (head) no longer exists AND the PR was closed by a maintainer with branch deletion, or when the maintainers explicitly purged the PR record.

**Scope assessment — cross-repo sweep:** Run the sequence check across MULTIPLE repos, not just one. If PR #154 is missing in pay-skills AND #192 is missing in pay-skills AND #2905 is missing in x402-foundation/x402 AND #733 is missing in ahmet/awesome-web3 — all gaps in the PR sequence of independent repos — this is a mass deletion targeting our submissions specifically, not a single-repo maintainer cleanup.

### Response to Mass 404

1. **Update every PR portfolio entry** from `✅ OPEN` to `❌ DELETED (404)` with the audit date
2. **Add a header banner** to the portfolio documenting the mass deletion event
3. **Propagate to queue items** — if any queue item was "blocked on PR" where the PR is now confirmed deleted, change the status: the PR no longer exists and cannot be revived. The item's blocker is the lack of an open PR, not the PR's merge status.
4. **Flag for Jordan** — mass deletion across 8+ repos is not random. It may indicate:
   - Repo maintainers coordinated a cleanup of agent-submitted PRs
   - Our submissions were flagged as spam/low-quality across multiple curators
   - A tool or registry that indexes these repos triggered bulk removals
   Jordan needs to decide whether to re-submit, change approach, or deprioritize ecosystem listings
5. **Do NOT re-submit** until Jordan reviews — resubmitting PRs that were just deleted by maintainers would damage our reputation further
6. **Increment the queue version** and add a `consolidation_notes` entry documenting the sweep results

### How Mass 404 Differs From Other 404 Scenarios

| Scenario | Account Check | Repo Check | Other PRs Visible | Our PRs Gone? | Action |
|----------|--------------|------------|-------------------|---------------|--------|
| Token death | ✅ Account exists | ✅ Repos exist | ❌ No — all API calls 401/403 | — | Renew token |
| Account deleted | ❌ User 404 | ❌ Repos 404 | ❌ N/A | — | Report to Jordan |
| Wrong org | ✅ Account exists | ❌ Repo 404 (wrong org) | ❌ Wrong URL | — | Find correct org |
| Individual phantom | ✅ Account exists | ✅ Repo exists | ✅ Other PRs visible | Only 1-2 PRs 404 | Mark as phantom |
| **Mass deletion** | ✅ Account exists | ✅ Repos exist | ✅ Other PRs visible | **ALL PRs 404** | Flag for Jordan + update portfolio |
| Rate limit (REST) | ✅ Works | ✅ Works | ❌ Empty/null | — | Wait/reset |

## Pitfalls

- **"All deleted" claims in the portfolio may be false — always verify with REST API before propagating.** The portfolio may contain a header like "ALL 10 PRs returned HTTP 404. Systematically deleted/removed by repo maintainers." This claim can be wrong — it may have been caused by a GraphQL rate limit issue in a prior session. **Verification protocol:** Run `gh api repos/<owner>/<repo>/pulls/<number> --jq '{state, merged_at}'` for each PR. If every PR returns `state: "open"`, the "all deleted" claim was false. Update the portfolio header to reflect the corrected status and add a note explaining the false positive. Confirmed Jul 28, 2026: portfolio claimed all 10 PRs deleted, but REST API confirmed all 10 still open — the false claim was from a prior session's GraphQL rate limit exhaustion.

- **GraphQL rate limit resets hourly** — If GraphQL is exhausted, switch to REST. REST has a separate 5000/hr budget.
- **Closed PRs without merge** — Check `closed_by` to see if a maintainer closed it or the author did. If closed_by is null, it was likely auto-closed by a bot or stale-bot.
- **PRs may have been replaced** — A closed PR may have a replacement PR with a different number. Check the repo's open PRs for similar titles.
- **Timeline endpoint may 404** — `pulls/{number}/timeline` and `pulls/{number}/events` are not available on all repos. Fall back to `pulls/{number}/reviews` and `pulls/{number}/comments`.
- **Rate limit recovery** — If both REST and GraphQL are exhausted, note the PRs that couldn't be checked and retry next session. The rate limit resets at the top of each hour.
- **Fork-name mismatch — the most common false negative.** When checking if a PR exists, do NOT search for a fork by its expected name alone (e.g. `ProtoJay4789/pay-skills`). The actual fork may have a different name (`ProtoJay4789/pay-skills-fork`). This caused the Jul 20 audit to falsely report all 11 PRs as "never submitted" — the forks existed under different names. **Fix:** Instead of checking the fork directly, query the upstream repo's open PR list and filter by `head.label` starting with your username:
  ```bash
  gh api repos/<owner>/<repo>/pulls --jq '.[] | select(.head.label | startswith("ProtoJay4789")) | {number: .number, title: .title, state: .state}'
  ```
  This catches PRs from any fork name. Run this once per upstream repo, not once per expected fork name.
- **Fork names are not predictable.** GitHub auto-generates fork names when the expected name is taken, or when the user renames the fork. Never hardcode a fork name in queue notes or portfolio entries. Always discover the actual fork name via the upstream PR list or the user's repos list (`gh api users/ProtoJay4789/repos --jq '.[] | select(.fork == true) | .name'`).
- **Portfolio entries with wrong PR numbers.** The PR portfolio may list PR numbers that don't match reality (e.g. listing PR #154 when the actual PR is #192). Always verify the actual PR number from the upstream repo's PR list, not from the portfolio entry. Update the portfolio with the correct number after verification.
- **Phantom PRs in queue notes.** Queue items can accumulate stale references to PRs that never existed. Common causes: (1) a PR number was guessed or estimated before submission, (2) the PR was on a different repo than the one checked, (3) the PR was deleted by maintainers. Always verify existence before treating a PR number as real. A 404 means the PR was never created — update the queue to remove the dependency.
- **Unauthenticated rate limit is 60/hr.** If `gh auth status` shows no authentication, the sweep will exhaust the budget on the first few PRs. Authenticate first, or use a personal access token via `GH_TOKEN` env var. Without auth, limit the sweep to 3-5 PRs max.
- **Portfolio branch-name drift causes accidental PR creation.** When the portfolio lists a wrong head branch (e.g. `format-ordering` when the actual PR uses `main`), the REST POST verification creates a real PR instead of returning 422. The branch has content, just never submitted. **Detection:** 201 response on a PR you expected to exist. **Fix:** Close immediately, discover the real head branch from the upstream PR list, update the portfolio. Add this as a pitfall because it wastes rate limit budget and creates noise in the target repo.
- **Mass 404 can look like token death at first glance.** When the first PR check returns 404, the natural assumption is "the token is dead" or "rate limited." Don't stop at one PR. Check ALL portfolio entries systematically across all repos. If every single one returns 404 while `gh api user` works and repo PR lists return other users' PRs, the pattern is mass deletion — not a token/auth problem. The full sweep is essential to differentiate.
- **Mass-deletion detection requires checking PR sequence gaps, not just 404s.** A single missing PR number in a sea of existing ones is a phantom. A cluster of missing numbers that align with our portfolio across multiple independent repos is a deletion event. The cross-repo gap analysis is the diagnostic signal — run it before concluding mass deletion.
