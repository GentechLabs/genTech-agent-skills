# ARD Integration — GenTech x402 gateway (Aug 26, 2026)

Full detail for the ARD (Agentic Resource Discovery) registration workflow. See the
`platform-registration` SKILL.md "ARD" section for the 6-step summary.

## What ARD is
Open, federated discovery protocol for agentic resources (MCP servers, A2A agents,
Skills, APIs). Backed by Cisco, Databricks, GitHub, Google, Hugging Face, Microsoft,
Nvidia, Salesforce, ServiceNow, Snowflake. Solves the *discovery* bottleneck; we solve
the *payment* bottleneck (x402). Complementary layers of the same stack.

## Repos
- `ards-project/ard-spec` (435★, Apache-2.0, active) — the spec + conformance CLI
- `ards-project/ard-connectors` (15★) — client-side connectors (Skills + MCP) for
  Claude/ChatGPT/Copilot/Gemini to search ARD discovery services
- Fork: `GentechLabs/ard-spec`

## The validated manifest (what we shipped)
`conformance/examples/gentech-x402/ard.json`:
```json
{
  "specVersion": "1.0",
  "host": { "displayName": "GenTech Labs", "identifier": "did:web:gentechlabs.net",
            "documentationUrl": "https://gentechlabs.net" },
  "entries": [{
    "identifier": "urn:air:gentechlabs.net:api:x402-gateway",
    "displayName": "GenTech x402 Gateway",
    "type": "application/mcp-server-card+json",
    "url": "https://api.gentechlabs.net/.well-known/x402-bazaar",
    "description": "Paid API gateway for AI agents using the x402 protocol. 10 live services across Base, Solana, Avalanche, X Layer, and Algorand...",
    "tags": ["x402","payments","api","defi","agent-economy","erc-8004"],
    "representativeQueries": ["check if a token is a honeypot...", "analyze a wallet portfolio...", "score an LP position efficiency...", "discover AI agents registered on ERC-8004", "get a price quote for an x402 API call"],
    "capabilities": ["TokenSecurity","WalletAnalysis","DefiLpAnalytics","AgentDiscovery","X402Payments"],
    "metadata": { "x402Version": 2, "settlementChains": "base, solana, avalanche, xlayer, algorand", "serviceCount": 10 },
    "trustManifest": { "identity": "did:web:gentechlabs.net", "identityType": "did",
      "attestations": [{ "type": "API-Documentation", "uri": "https://gentechlabs.net", "mediaType": "text/html" }] }
  }]
}
```

## Conformance CLI
```bash
# Validate a local file
python3 conformance/bin/conformance-test manifest conformance/examples/gentech-x402/ard.json
# Validate a LIVE URL (proves production compliance)
python3 conformance/bin/conformance-test manifest https://api.gentechlabs.net/.well-known/ard.json
# → CONFORMANCE STATUS: PASS — 0 critical errors, 0 warnings
```

## Pitfalls
- **`metadata` values must be SCALARS** (string/number/bool), NOT arrays. The CLI
  rejects arrays: `'[...]' is not of type 'string'`. Use a comma-joined string for
  multi-value metadata (e.g. `"settlementChains": "base, solana, avalanche"`).
- **The conformance CLI is zero-dependency Python** — runs out of the box, no install.
- **`/.well-known/ard.json` is served by nginx** from `/var/www/gentechlabs` (the
  `/.well-known/` location block already sets `default_type application/json` + CORS).
  Just drop the file there, `chown www-data:www-data`, `chmod 644`.

## What we submitted (Aug 26, 2026)
- **Issue #83** — "Reference publisher: GenTech Labs — x402 payment rail + agent-economy API gateway"
- **PR #84** — "feat(conformance): add GenTech x402 gateway as reference example" — OPEN + MERGEABLE
- **Commented #67** — "How can independent publishers get resources listed in GitHub Agent Finder's curated catalog?" — our exact question, with a concrete validated case
- **Live manifest** — `https://api.gentechlabs.net/.well-known/ard.json` (HTTP 200, conformance PASS in prod)

## Why it matters
An AI client querying an ARD discovery service can now find our x402 gateway for
"check if this token is a honeypot" and pay us per call. That's the distribution
channel, real and deployed — and we're a reference publisher in a standards body
backed by Google/Microsoft/Nvidia.

## Next steps (tracked in vault `10-Labs/ard-integration-2026-08-26.md`)
- Track #67 for the independent-publisher catalog path
- Watch PR #84 for merge (per PR cadence rule: let it sit, no nudging)
- Consider contributing to spec issues (#77 verification-service type maps to our API Safety Suite)
