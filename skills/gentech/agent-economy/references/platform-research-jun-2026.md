# Platform Registration Research — June 24, 2026

## Agenstry.com (launched Jun 23, 2026)

- **URL:** agenstry.com/submit
- **Cost:** Free, no login required
- **Format:** A2A Agent Card (JSON)
- **Auto-discovery:** Publish `/.well-known/agent-card.json` — they index automatically
- **Verification:** DNS-TXT record ownership for verified badges
- **Index:** ~101K agents + MCPs (~1,738 A2A agents, ~98K MCP servers)

## x402 Directories

### x402-list.com
- **URL:** x402-list.com/submit
- **Cost:** Free
- **Format:** Web form (name, URL, email, category, description, endpoints)
- **Auto-probe:** Validates HTTP 402 responses
- **Restriction:** No free hosting domains

### signal402.com
- **URL:** signal402.com/register
- **Cost:** $0.01 x402 payment
- **Format:** Web form (name, URL, category, price, description)
- **Review:** Manual before listing

### x402.direct
- **Status:** Currently down (500 error)
- **Discovery:** Automated via Bazaar + well-known manifest

## A2A Registries

### a2a-registry.org (Official)
- **Discovery:** Auto-scan from URL
- **Supports:** A2A Protocol, MCP, OpenAI Plugins

### a2aregistry.org (v2.0.0)
- **Discovery:** Well-known URI
- **Features:** 127+ agents, MCP integration, Python SDK

### a2alist.ai
- **Cost:** $0.99 USDC via x402
- **Features:** Active verification, security ratings

### a2aagentlist.com
- **Submission:** Email to gal6111@gmail.com
