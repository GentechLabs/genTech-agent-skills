# OASF Metadata Format (ERC-8004)

## Required Fields

```json
{
  "name": "Agent Name",
  "description": "What the agent does",
  "version": "1.0.0",
  "services": [
    {
      "type": "mcp|http|x402",
      "url": "https://endpoint.com/api",
      "oasfVersion": "1.0",
      "skills": ["skill-1", "skill-2"],
      "domains": ["domain-1", "domain-2"],
      "active": true
    }
  ]
}
```

## Optional Fields

```json
{
  "author": "username",
  "homepage": "https://github.com/username",
  "contact": "email@example.com",
  "metadata": {
    "chain": "base",
    "erc8004": true,
    "x402": true,
    "mcp": true,
    "openSource": true,
    "license": "MIT",
    "tags": ["tag1", "tag2"]
  }
}
```

## Service Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | string | Yes | `mcp`, `http`, or `x402` |
| url | string | Yes | Endpoint URL |
| name | string | No | Human-readable name |
| description | string | No | What the service does |
| oasfVersion | string | Yes | Usually `1.0` |
| skills | string[] | Yes | OASF skill tags |
| domains | string[] | Yes | OASF domain tags |
| active | boolean | Yes | Whether service is live |
| pricing | object | No | Pricing info (see below) |

## Pricing Object (for x402)

```json
{
  "pricing": {
    "model": "pay-per-query|freemium|subscription",
    "amount": 0.01,
    "currency": "USDC",
    "protocol": "x402",
    "note": "Optional note"
  }
}
```

## OASF Skill Tags (136 total)

Common skills for agent economy:
- `token-analysis`, `risk-scoring`, `rugpull-detection`, `security-audit`
- `credit-scoring`, `reputation-analysis`, `agent-verification`
- `travel-search`, `flight-research`, `hotel-search`
- `social-scraping`, `content-analysis`, `trend-detection`
- `agent-identity`, `payment-processing`, `enforcement`, `audit-trails`
- `code-generation`, `code-review`, `nlp`

## OASF Domain Tags (204 total)

Common domains:
- `defi`, `security`, `blockchain`, `finance`
- `ai-agents`, `infrastructure`, `identity`, `payments`
- `travel`, `data`, `tourism`, `content`
- `social-media`, `analytics`, `technology`

## Example: GenTech Labs

```json
{
  "name": "GenTech Labs",
  "description": "AI agent economy infrastructure — risk scoring, data access, identity verification, and DeFi intelligence for autonomous agents.",
  "version": "1.0.0",
  "author": "ProtoJay4789",
  "services": [
    {
      "type": "x402",
      "url": "https://api.gentechlabs.com/rugcheck",
      "name": "Rugcheck v2",
      "skills": ["token-analysis", "risk-scoring"],
      "domains": ["defi", "security"],
      "pricing": {"model": "pay-per-query", "amount": 0.01, "currency": "USDC", "protocol": "x402"},
      "active": true
    }
  ]
}
```

## Hosted Metadata

After creating the JSON, host it on GitHub raw URL:
```
https://raw.githubusercontent.com/{owner}/{repo}/main/erc-8004/agent-metadata.json
```

This URL becomes the on-chain URI when registering.

## Agentscan Skill Picker (Mobile UI)

The Agentscan Create page has a skill picker with 136 skills organized by category.

**How to use it efficiently:**
1. Don't scroll — use the search bar at the top
2. Type one keyword (e.g., `security`)
3. Check the matching skill
4. Clear the search, type the next keyword
5. Repeat for all needed skills

**Recommended skills for agent economy agents:**
- `security` → Security Privacy
- `vulnerability` → Vulnerability Analysis
- `search` → Search
- `retrieval` → Retrieval Of Information
- `risk` → Risk Classification

**Key facts:**
- Skills are optional — register with just name + description + MCP services
- Domains are also optional — can add later
- Agent metadata can be updated after registration via `setAgentURI()`
- The skill picker categories include: Agent Orchestration, Advanced Reasoning, Analytical Skills, Security Privacy, Tabular Text, Tool Interaction, and many more
