# Agentscan API Reference

## Base URL
```
https://agentscan.info/api
```

No API key required. Rate-limited (429 on abuse).

## Key Endpoints

### List Agents
```
GET /api/agents?page=1&page_size=20&sort=recent
```

### Search Agents
```
GET /api/agents?search=GenTech&page=1&page_size=10
```

### Filter by Network
```
GET /api/agents?network_id=avalanche&page=1&page_size=5
```

### Agent Details
```
GET /api/agents/{agent_id}
```

## Response Format
```json
{
  "items": [
    {
      "name": "GenTech Labs",
      "address": "0x...",
      "description": "...",
      "reputation_score": 0.0,
      "status": "active",
      "network_id": "avalanche",
      "id": "uuid",
      "created_at": "2026-06-21T23:37:35",
      "token_id": 140225,
      "owner_address": "0x...",
      "skills": ["security_privacy/security_privacy"],
      "domains": [],
      "classification_source": "ai"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

## Verification Workflow

After registration, verify with:
```bash
curl -s "https://agentscan.info/api/agents?search=GenTech&page=1&page_size=5" | python3 -m json.tool
```

Check `created_at` timestamp to confirm recent registration.

## On-Chain Verification

Check for `Registered` events on the Identity Registry:
- Contract: `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432`
- Event topic: `0x6cd8594df6446610564bf1ea1e804402ea0006dc7b541d3a430d1ea0a62cffd4`

```bash
curl -s -X POST <RPC_URL> -H "Content-Type: application/json" -d '{
  "jsonrpc": "2.0",
  "method": "eth_getLogs",
  "params": [{
    "fromBlock": "0x...",
    "toBlock": "latest",
    "address": "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432",
    "topics": ["0x6cd8594df6446610564bf1ea1e804402ea0006dc7b541d3a430d1ea0a62cffd4"]
  }],
  "id": 1
}'
```

**Pitfall:** Avalanche RPC limits getLogs to 2048 blocks. Use narrow block ranges or rely on Agentscan API for verification.

## MCP Server

Agentscan also has an MCP server for AI assistant integration. See docs at https://agentscan.info/docs.
