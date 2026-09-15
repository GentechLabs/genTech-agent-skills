# Awesome List Agent Fast-Track Patterns

## 🤖🤖🤖 Agent PR Fast-Track

Several awesome-list repos (punkpeye/awesome-mcp-servers, punkpeye/awesome-mcp-devtools) offer a **fast-track merge** for automated agent PRs. Add `🤖🤖🤖` to the END of the PR title to opt in. Doing so triggers a streamlined review process that merges agent PRs faster.

**How to use:**
```bash
gh pr create --title "Add GenTech Shop to Gaming section 🤖🤖🤖" --body "..."
```

## Glama Score Badge

For MCP servers listed in awesome-mcp-servers, the Glama bot REQUIRES:
1. The MCP server must be listed on [glama.ai/mcp/servers](https://glama.ai/mcp/servers)
2. The Glama score badge must be appended after the description:
   ```
   [![OWNER/REPO MCP server](https://glama.ai/mcp/servers/OWNER/REPO/badges/score.svg)](https://glama.ai/mcp/servers/OWNER/REPO)
   ```
3. Run `docker build` first locally or use Glama's Dockerfile upload if needed

**The badge is a HARD MERGE GATE — treat it as a precondition, not a follow-up.** The bot comments
within ~15 seconds of opening (`<!-- glama-check -->`) and labels the PR `missing-glama`. Evidence:
of 43 merged PRs sampled across a 3-day window, every one carried a badge line in its diff; the few
that merged while still labelled `missing-glama` added it mid-PR (`missing-glama` → `has-glama`).
**Do not reason "other entries in this section omit it" — they don't reach merge without it.**

**Add the badge as a COMMIT to the PR branch, not by editing the PR body.** The bot re-scans on new
commits; a body edit does not change the file the bot checks.

**Verify the badge URL actually resolves before relying on it:** `curl -s
https://glama.ai/mcp/servers/OWNER/REPO/badges/score.svg` returns an SVG whose `<title>` reads *"This
MCP server is not listed on Glama"* when the repo is absent (or listed under a retired account name —
an org rename leaves prior listings on the dead account). Submit via Glama's *Add Server* first
(needs a Dockerfile / build spec that starts and answers introspection), then add the badge. Badge
resolves at any non-zero score; at 0% the SVG cannot render.

## Ordering Rules

- Entries must be alphabetical by full repo name (`owner/repo`)
- When inserting between two existing entries, match the surrounding format exactly
- If categories exist, place within the correct category section

## pay-skills Catalog Pricing Sync

When submitting to `solana-foundation/pay-skills`, the Greptile bot will flag:
- `pricing.per_request` in YAML frontmatter vs `x-payment-info.price.amount` in OpenAPI spec
- Network lists (Algorand, Solana, etc.) in frontmatter vs spec
- Endpoint table formatting (collapsed rows)

**Always** verify the per-service PAY.md matches the master openapi.json before submitting.
