# Cursor Directory — Plugin Submission Format

**Platform:** cursor.directory
**Submission URL:** cursor.directory/plugins/new
**Auth:** GitHub sign-in (human must do this)
**Review:** None (community directory). Official Marketplace requires manual review at cursor.com/marketplace/publish.

## Two Paths

| Path | URL | Review | Requirements |
|------|-----|--------|-------------|
| **Cursor Directory** (community) | cursor.directory/plugins/new | None — instant listing | GitHub login, avatar, description, tags, rules, MCP servers, skills |
| **Official Marketplace** (curated) | cursor.com/marketplace/publish | Manual review by Cursor team | Plugin must be open source, `.cursor-plugin/plugin.json` manifest, manual review of every update |

## Submission Fields (Cursor Directory)

| Field | Value (GenTech Example) |
|-------|------------------------|
| **Name** | GenTech Gateway |
| **Description** | x402 pay-per-call gateway for AI agents — 16 endpoints, 5 chains, no API keys |
| **Source URL** | github.com/ProtoJay4789/x402-gateway |
| **Tags** | x402, payments, usdc, base, solana, gateway, mcp |
| **Logo/Avatar** | Square PNG, ~400KB, recognizable at 96x96px |
| **Rules** | 1+ spend-safety rules (markdown, paste into field) |
| **MCP Servers** | JSON config for streamable-http MCP servers |
| **Skills** | 1-4 skill descriptions (name + description each) |

## Rules Format

Rule name: `gentech-spend-safety`

```
gentech-spend-safety:
- The `gen_pay`, `gen_batch_pay`, and `gen_withdraw` tools spend real USDC.
  Before calling any of them, tell the user the exact amount and destination
  and get explicit approval. Never spend unprompted.
- Free endpoints (gen_status, gen_balance, gen_quote, gen_scan) can be used
  freely to answer questions.
```

## MCP Server Format

```json
{
  "name": "gentech-gateway",
  "type": "streamable-http",
  "url": "https://your-gateway.com/mcp",
  "description": "x402 compliance gateway",
  "tools": ["gen_discover", "gen_status", "gen_balance", "gen_pay"]
}
```

## Skills Format

1. Skill name: `x402-payment`
   — Description of the skill and what it does.
2. Skill name: `compliance-scanner`
   — Description of the skill.

## GenTech Submission Status

- **Community Directory (cursor.directory):** 🟡 Prepped but needs Jordan to sign in with GitHub and paste content
- **Official Marketplace (cursor.com/marketplace/publish):** 🔴 Not yet submitted — requires open-source plugin repo with `.cursor-plugin/plugin.json`
- **Prepped content:** `09-Green Room/submissions/cursor-directory-submission.md`
- **Logo:** `09-Green Room/branding/gentech-gateway-logo.png`

## Pitfalls

- **Logo must be clean at small sizes** — avoid gradients, fine details, or glow effects. Dark navy circle + white bold letter + single accent dot works best.
- **Spend-safety rules are essential** — without them, agents may spend unprompted. Cursor's directory reviews these.
- **Tags drive discoverability** — use all relevant tags. Users search by tag on cursor.directory.
- **Official Marketplace requires open source** — every plugin must be open source and reviewed. Not compatible with closed-source gateways.
