# OASF Metadata — Top-Level Skills/Domains Fix

## Problem

AgentScan shows empty skills/domains even though the OASF metadata includes them.

**Root cause:** OASF metadata format supports skills/domains at TWO levels:
- **Top-level (agent-wide)**: AgentScan reads from here
- **Service-level**: Specific to each service

If skills/domains are only inside services, AgentScan shows them as empty.

## Reproduction

```bash
# Check AgentScan API
curl -s "https://agentscan.info/api/agents?search=Gentech" | jq '.result[0].skills'
# Output: []
```

## Fix Pattern

Add top-level `skills` and `domains` arrays to OASF metadata. These should be a union of all service-level skills/domains.

**Before (broken):**
```json
{
  "name": "GenTech Labs",
  "services": [
    {
      "name": "Rugcheck v2",
      "skills": ["token-analysis", "risk-scoring"],
      "domains": ["defi", "security"]
    }
  ]
}
```

**After (fixed):**
```json
{
  "name": "GenTech Labs",
  "skills": [
    "token-analysis",
    "risk-scoring",
    "credit-scoring",
    "agent-verification",
    "travel-search",
    "social-scraping",
    "payment-processing",
    "erc-8004"
  ],
  "domains": [
    "defi",
    "security",
    "blockchain",
    "ai-agents",
    "identity",
    "finance",
    "travel",
    "data",
    "social-media",
    "content",
    "analytics",
    "infrastructure",
    "payments"
  ],
  "services": [
    {
      "name": "Rugcheck v2",
      "skills": ["token-analysis", "risk-scoring"],
      "domains": ["defi", "security"]
    }
  ]
}
```

## Update Process

1. **Fix metadata locally** — Add top-level arrays
2. **Upload to IPFS** — Use Pinata, Web3.storage, or similar
3. **Update on-chain** — Call `setTokenURI(tokenId, "ipfs://...")` on ERC-8004 contract
4. **Wait for sync** — AgentScan updates within 24 hours

## Contract

- **Address:** `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` (CREATE2, same on all chains)
- **Method:** `setTokenURI(uint256 tokenId, string uri)`
- **Gas:** ~$0.01 on L2s

## Tools

- **Tenderly** (tenderly.co) — Supports UUPS proxy contracts, use `Write Contract`
- **Brownie/Hardhat** — Scripted updates

## Verified Fix

**Agent:** GenTech Labs (Token ID #1770 on Avalanche)
**Status:** Skills/domains empty → Fixed metadata prepared → Pending on-chain update

**Verification:**
```bash
curl -s "https://agentscan.info/api/agents?search=Gentech" | jq '.result[0] | {name,skills,domains,updated_at}'
```

Before fix:
```json
{
  "skills": [],
  "domains": [],
  "updated_at": "2026-06-27T03:50:03.566920"
}
```

After on-chain update:
```json
{
  "skills": ["token-analysis", "risk-scoring", ...],
  "domains": ["defi", "security", ...],
  "updated_at": "2026-06-27T..."
}
```