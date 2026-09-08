# AgentRanking.io Registration Strategy

**Last Updated:** July 6, 2026

## Platform Overview

**What It Is:**
- Agent ranking and discovery platform
- ERC-8004 Identity Registry integration (on-chain agent registration)
- REST API + MCP server for programmatic discovery
- Verification (KYA), ranking system, and boost mechanics
- Token support: $AR (AgentRanking token)

**Traffic:** Unknown (no web traffic data available yet)

---

## Registration Process

### Phase 1: On-Chain Registration (Mandatory)

**Method:** Web form → Register on ERC-8004 Identity Registry

**Steps:**
1. Go to https://app.agentranking.io/launch
2. Fill in agent metadata:
   - Agent Name (required)
   - Description (required, 0-500 chars)
   - Profile Image (optional, PNG/JPG/WebP up to 5MB)
   - Agent Type (optional)
   - Tags (optional, comma separated)
   - TEE Declaration (optional, self-declaration)
   - Staked Collateral (optional, declare trust backing)
3. Select deploy chain (Base is cheapest default)
4. Review and submit transaction

**Result:** Agent minted on ERC-8004 registry, auto-indexed by AgentRanking

### Phase 2: Verification (KYA) — Optional

**Method:** Web form → Verify → Pay

**Benefits:**
- ✅ Verified badge on profile
- ✅ Richer profile fields (image, banner, description)
- ✅ Placement on verified agents showcase
- ✅ Trust signals for marketplaces

**Pricing:** Pricing shown before payment in Verify flow

**Pitfall:** Verification pricing unknown without browsing the Verify page

### Phase 3: Boosts and Visibility — Optional

**Method:** Web form → Boost → Pay

**Benefits:**
- Power Ranking boosts for leaderboard placement
- Featured placement (editorial, requires team contact)
- Enhanced visibility in discovery feeds

**Pricing:** Pricing shown in Boost flow

---

## API Endpoints (for Integration)

**Public REST API:**

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/agents` | Paginated agent directory (filters: page, perPage, chain, search, owner, skills, x402, verified, archetype, minScore, sort) |
| `GET /api/v1/agents/:chainId/:agentId` | Full agent profile (metadata, services, capabilities, feedback, on-chain enrichment) |
| `GET /api/v1/stats` | Directory-wide counts (totals, x402/MCP/A2A/OASF coverage, topChains, updatedAt) |
| `GET /api/v1/wallets/:address/agents` | Active agents owned by an EVM address (case-insensitive, up to 100, score-ordered) |
| `GET /api/v1/reputation/:wallet` | Trust-oracle style wallet signal for agents/LLMs |
| `GET /api/v2/agents` | Same as v1 plus verified-revenue filters (verifiedRevenue, minMonthlyPnl, maxBurnToEarn, sort=perf_desc) |

**MCP Server:**
- URL: `https://app.agentranking.io/api/mcp`
- Catalog: `/.well-known/mcp.json`
- Methods: POST, GET, DELETE
- Tools, auth, and x402-paid tools available

**Rate Limits:**
- `/api/v1/*` and `/api/v2/*` can be rate-limited per IP (Redis env vars: `PUBLIC_API_RATELIMIT_PER_MINUTE`, `PUBLIC_API_V2_RATELIMIT_PER_MINUTE`)
- `/api/agents` uses `AGENTS_API_RATELIMIT_PER_MINUTE`
- Over limit returns `429` + `Retry-After` header

---

## Supported Chains

**Every active AgentRanking chain is shown with its logo. Dimmed options are not available for EVM deploy (e.g., Solana, Telegram, or networks not yet in Rainbow). Base is still the cheapest default.**

**Known Supported Chains (from docs):**
- Base (8453) — cheapest default
- Other EVM chains (check /api/networks for full list)

**To query supported chains:**
```bash
curl -s "https://app.agentranking.io/api/networks" | jq .
```

---

## x402 and MCP Support

**x402:**
- Supported in API filters (`x402` filter in `/api/v1/agents`)
- x402-paid tools available in MCP server (when configured)

**MCP:**
- Public MCP server at `https://app.agentranking.io/api/mcp`
- Catalog at `/.well-known/mcp.json`
- Tools and x402-paid tools available

**Stats tracking:**
- Directory-wide x402 coverage tracked in `/api/v1/stats`
- MCP coverage tracked in `/api/v1/stats`
- A2A (Agent-to-Agent) coverage tracked in `/api/v1/stats`
- OASF (Open Agent Standard for Federation) coverage tracked in `/api/v1/stats`

---

## ARScore Calculation

**What It Is:**
- Agent Ranking Score (displayed on agent listings)
- 14-21 range seen in current sample agents

**How It's Calculated:**
- Unknown (not documented in public docs)
- Likely combines: reputation, verification, activity, staking, boosts

**Pitfall:** ARScore methodology not public — need to register agent and observe behavior

---

## GenTech Integration Path

### Agents to List

| Agent | Description | Chain | Priority |
|-------|-------------|-------|----------|
| **DeFi Intelligence Agent** | Real-time DeFi portfolio intelligence, LP monitoring, yield opportunities | Base (8453) | 🔴 High |
| **LP Monitoring Agent** | Automated LP position monitoring, efficiency tracking, rebalance alerts | Base (8453) | 🔴 High |
| **Agent Registration API Agent** | ERC-8004 agent registration API, identity verification | Base (8453) | 🟡 Medium |
| **Email Agent (Forge)** | Cloudflare Email Service + MCP integration, business workflows | Base (8453) | 🟡 Medium |

### Why AgentRanking Fits GenTech

- ✅ ERC-8004 support (GenTech uses ERC-8004 for identity)
- ✅ x402 support (GenTech uses x402 for payments)
- ✅ MCP server (GenTech already uses MCP)
- ✅ REST API for programmatic discovery
- ✅ On-chain registry (trustless verification)
- ✅ Verification badges (builds trust with buyers)

---

## Action Items

### Research (Pending)
- [ ] Browse Verify page to get verification pricing
- [ ] Browse Boost page to get boost pricing
- [ ] Query `/api/networks` for full list of supported chains
- [ ] Query `/api/v1/stats` for current ecosystem stats

### Registration (Forge to execute)
- [ ] Register DeFi Intelligence Agent on Base
- [ ] Register LP Monitoring Agent on Base
- [ ] Register Agent Registration API Agent on Base
- [ ] Register Email Agent (Forge) on Base

### Verification (Optional, Jordan to decide)
- [ ] Verify DeFi Intelligence Agent (KYA)
- [ ] Verify LP Monitoring Agent (KYA)
- [ ] Verify Agent Registration API Agent (KYA)
- [ ] Verify Email Agent (KYA)

### Boosts (Optional, Jordan to decide)
- [ ] Boost DeFi Intelligence Agent for leaderboard placement
- [ ] Boost LP Monitoring Agent for leaderboard placement

---

## Pitfalls

- **Verification pricing unknown** — Need to browse Verify page before paying
- **Boost pricing unknown** — Need to browse Boost page before paying
- **ARScore methodology unknown** — Can't optimize ranking without understanding scoring
- **Supported chains unknown** — Need to query `/api/networks` before deploying
- **TEE declaration is self-declaration** — Not audited, just metadata
- **Staked collateral is declarative** — Not verified on-chain, just metadata

---

## Comparison to Other Marketplaces

| Platform | On-chain Registry | x402 Support | MCP Support | Verification |
|----------|------------------|--------------|-------------|--------------|
| **AgentRanking.io** | ✅ ERC-8004 | ✅ | ✅ | ✅ KYA |
| **Atelier** | ❌ Unknown | ✅ | ❓ Unknown | ✅ Yes |
| **Agentic.Market** | ❓ Unknown | ✅ | ❓ Unknown | ✅ Yes (indexed) |
| **Swarms** | ❓ Unknown | ✅ | ❓ Unknown | ✅ Yes |

**GenTech's Strategy:**
- **AgentRanking.io** — On-chain ERC-8004 registry (primary identity layer)
- **Atelier** — Solana marketplace (USDC payments)
- **Agentic.Market** — Auto-indexed via Bazaar (largest x402 marketplace)
- **Swarms** — x402 filter (complementary discovery)

---

## References

- [Get your agent listed](https://app.agentranking.io/docs/listing)
- [Public API](https://app.agentranking.io/docs/api)
- [Verification & reputation](https://app.agentranking.io/docs/verification)
- [Launch Agent](https://app.agentranking.io/launch)
- [MCP overview](https://app.agentranking.io/docs/mcp)
- [MCP tools reference](https://app.agentranking.io/docs/mcp/tools)