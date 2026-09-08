# Pay-Skills Catalog Fix Patterns

Fix patterns for `solana-foundation/pay-skills` PRs flagged by Greptile or other bots.

## File Structure Detection

Before fixing, determine which file structure the branch uses:

### Structure A: Embedded OpenAPI (PR #192 style)
```
providers/gentech/games-intel/PAY.md    # frontmatter has `openapi.content` with inline JSON
providers/gentech/x402-gateway/PAY.md   # master PAY.md with correct prices
providers/gentech/x402-gateway/openapi.json  # canonical spec (x402-gateway only)
```
Sub-provider PAY.md files have the OpenAPI spec **embedded inline** as `openapi.content: |`. The frontmatter also has `accepts:` and `pricing.per_request`.

### Structure B: Per-service sidecar (PR #190 style)
```
providers/gentech/games-intel/PAY.md         # frontmatter has `openapi.path: openapi.json`
providers/gentech/games-intel/openapi.json   # only this service's endpoints
```
Each service has its own `openapi.json` sidecar. PAY.md frontmatter has `openapi.path: openapi.json`, no `accepts` field (networks live in the spec), and `pricing.per_request`.

## Greptile Flag Resolution

### P1: Pricing Mismatch

**Problem**: `per_request` in PAY.md frontmatter differs from endpoint `x-payment-info.price.amount` in the OpenAPI spec.

**Fix by structure**:
- **Structure A (embedded)**: Update `per_request` in the PAY.md frontmatter to match the **minimum** endpoint price. Example: games-intel has endpoints at $0.005 and $0.001; set `per_request: 0.001`.
- **Structure B (sidecar)**: Update `per_request` in PAY.md frontmatter and/or the amount in `openapi.json`. The values must match numerically (trailing zeros are fine: `0.005` == `0.005000`).

**Verify**:
```python
import json, re
with open("providers/gentech/games-intel/PAY.md") as f:
    content = f.read()
pay_val = float(re.search(r'per_request:\s*([\d.]+)', content).group(1))
with open("providers/gentech/games-intel/openapi.json") as f:
    oas = json.load(f)
for path, methods in oas["paths"].items():
    for method, d in methods.items():
        amt = d.get("x-payment-info",{}).get("price",{}).get("amount")
        if amt and abs(pay_val - float(amt)) > 0.0001:
            print(f"MISMATCH: {path} OAS={amt} vs PAY.md={pay_val}")
```

### P1: Algorand Missing from Sub-Provider

**Problem**: Sub-provider PAY.md lists fewer networks than the canonical x402-gateway spec.

**Fix by structure**:
- **Structure A (embedded)**: Add `- algorand:mainnet` to the YAML `accepts` array AND check that the embedded OpenAPI's `x-payment-info.networks` includes `algorand:*`.
- **Structure B (sidecar)**: Add `algorand:mainnet` to the `accepts` array if it exists. Services that omit `accepts` entirely need no change since networks are in the spec. The `openapi.json` should already have `algorand:*` in every endpoint's `x-payment-info.networks`.

**Canonical networks to sync**:
```
eip155:8453, eip155:56, eip155:196, eip155:43114,
solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp,
algorand:wGHE2Pwdvd7S12BL5FaOP20EGYesN73ktiC1qzkkit8=
```

### P2: Broken Table Formatting

**Problem**: Endpoint table rows concatenated on a single line.

**Fix**: Each endpoint gets its own table row:
```markdown
| Endpoint | Description |
|----------|-------------|
| `GET /api/games/search` | Game search across multiple platforms |
| `GET /api/games/cheapest` | Cheapest game price finder |
```

### P1: Shared OpenAPI Bleeding

**Problem**: All services share one `../openapi.json`, making every endpoint appear to belong to every service.

**Fix**: Create per-service `openapi.json` (Structure B). Each file contains only that service's paths plus `/health` and `/pricing`.

### P2: Wrong Category

**Problem**: Service categorized `finance` but belongs in `shopping`, `data`, or `media`.

**Fix** (per CONTRIBUTING.md):
| Service | Correct Category | Reason |
|---------|-----------------|--------|
| games-intel | shopping | Game price comparison |
| movie-intel | media (or shopping) | Movie search/details |
| market-intel | shopping | Cross-category price comparison |
| shipping-tracker | shopping | Tracking service |
| agent-discover | data | AI agent directory |

## Git Workflow for Multi-Branch Fixes

When fixing Greptile flags across multiple PR branches on the same fork:

### Setup
```bash
cd /tmp/pay-skills
git remote set-url origin https://github.com/ProtoJay4789/pay-skills-fork.git
```

**Pitfall**: Embedded HTTPS tokens in remote URLs (e.g., `https://user:ghp_xxx@github.com/...`) can expire silently. `gh auth` handles token refresh. If a push fails with "Invalid username or token", run `git remote set-url origin https://github.com/<user>/<repo>.git` and retry.

### Stash/Checkout Pitfall

**Do NOT** `git stash` on one branch and `git checkout` to another branch that has different versions of the same files. The stash pop will create merge conflicts in every shared file.

**Safe pattern**:
```bash
# Option A: Commit before switching
git add -A && git commit -m "wip: in-progress fixes"
git checkout <other-branch>

# Option B: Hard reset after uncommitted work is safe to discard
git add -A && git stash
git checkout <other-branch> && git reset --hard HEAD

# Option C: Cherry-pick specific file changes between branches
git checkout <source-branch> -- providers/gentech/games-intel/PAY.md
```

### Finding PR Branches (from outside any git repo)
```bash
gh api search/issues --method GET \
  -f q='author:ProtoJay4789 type:pr is:open repo:solana-foundation/pay-skills' \
  --jq '.items[] | {number, title, html_url, state, updated_at}'
```

### Pushing After Fix
```bash
git add -A && git commit -m "fix: description of all changes"
git push origin <branch-name>
gh pr comment <number> --repo solana-foundation/pay-skills \
  --body "✅ Addressed Greptile feedback:\n1. ...\n2. ..."
```

## Greptile Re-Trigger

After pushing, Greptile auto-re-scans within ~2 minutes. If it doesn't re-scan:
```bash
gh pr view <number> --repo solana-foundation/pay-skills \
  --json commits --jq '.commits[-1].oid'
```
Confirm the commit hash is present on the PR branch.
