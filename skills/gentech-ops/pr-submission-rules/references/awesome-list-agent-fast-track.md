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

If the PR is missing the badge, the Glama bot comments asking for it. Add the badge, update the PR body, and the bot re-checks.

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
