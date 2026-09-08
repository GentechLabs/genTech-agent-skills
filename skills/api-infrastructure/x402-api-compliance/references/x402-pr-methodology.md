# x402 Ecosystem PR Fix Methodology

Strategy: Fix open-source x402 repos → build credibility → leads for GenTech Academy.

## Tier 1 — Quick Wins (auto-PR, no human needed)

Changes that take a single file edit:
- Wrong header name (`X-Payment-Required` → `Payment-Required`)
- Wrong field name (`payment_address` → `payTo`)  
- Wrong scheme name (`type: "x402"` → `scheme: "exact"`)
- Asset address casing (mixed → lowercase hex)
- README/docs fixes (lowercase header name → canonical form)
- Amount type (number → string)

**Done autonomously by x402 Compliance Scout cron** (daily 12:10 UTC).

## Tier 2 — Deep Work (Gentech Only label)

Changes that need architecture work:
- Adding `/.well-known/x402` endpoint from scratch
- Rebuilding payment flow for v2 compliance
- Adding middleware or route handlers
- Multi-file changes across packages

**Labeled "Gentech Only"** — agent works these 24/7, never hits Jordan's inbox.

## Real-world PRs submitted (Jul 2026)

| PR | Repo | Fix | Tier |
|----|------|-----|------|
| [#5](https://github.com/marlinprotocol/x402-gateway/pull/5) | marlinprotocol/x402-gateway | README header docs | 1 |
| [#8](https://github.com/brave-experiments/private-x402-gateway/pull/8) | brave-experiments/private-x402-gateway | `X-Payment-Required` → `Payment-Required` (6 files) | 1 |
| [#30](https://github.com/mark3labs/x402-go/pull/30) | mark3labs/x402-go | Asset addresses lowercased | 1 |
| [#6](https://github.com/GOATNetwork/agentkit/pull/6) | GOATNetwork/agentkit | ERC-8004 testnet3 address fix | 1 |
| [#410](https://github.com/p-e-w/heretic/pull/410) | p-e-w/heretic | Byte tensor fix in ARA branch | 1 |
| [#2](https://github.com/srotzin/hive-rosetta/pull/2) | srotzin/hive-rosetta | Asset addresses lowercased (Node+Python) | 1 |
| [#35](https://github.com/Recall-Kitchen/awesome-x402-mcp-services/pull/35) | Recall-Kitchen/awesome-x402-mcp-services | Add GenTech Agent Kit to AI & Data section | 1 |

## PR submission flow

1. `gh repo fork <owner>/<repo> --fork-name <name> --default-branch-only`
2. `git checkout -b fix/<description>`
3. Make changes, commit, push
4. `gh pr create --repo <owner>/<repo> --base <branch> --head <fork>:<branch> --title "..." --body "..."`
   - `<fork>:<branch>` means `<your-username>:<branch>`. The fork name (--fork-name) is NOT part of the head ref — do NOT use `user:fork-name:branch`.
5. No self-promotion in PR body. Clean professional tone.

### Pitfall: `--fork-name` ≠ `--head` format

When using `gh repo fork --fork-name <custom-name>`, the fork's name on GitHub differs from the source. However, `--head` still uses `YourUsername:branch-name` — the fork name does not appear in the head ref. The `--repo` flag pointing at the upstream is what disambiguates which fork to pull from. Never pass `YourUsername:fork-name:branch` — that's an invalid format.
