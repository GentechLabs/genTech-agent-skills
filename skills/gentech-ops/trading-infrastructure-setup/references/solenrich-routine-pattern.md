# SolEnrich Condor Routine Pattern

## Overview
SolEnrich (solenrich.com) is an x402-native Solana data enrichment API. 34 endpoints, pay-per-call USDC on Solana, $0.001-$0.10/request. No subscriptions, no API keys. MCP integration available.

## Routine File
Location: `/root/condor/routines/solenrich.py`

## Endpoints Used for Agent Builders Cup

### LP Layer (Meteora/Orca/Raydium)
| Endpoint | Cost | Purpose |
|----------|------|---------|
| `enrich-token-full` | $0.004 | Price, volatility, concentration, risk flags |
| `protocol-profile` | $0.008 | TVL, yield pools, health signals |
| `new-tokens` | $0.012 | Discover recently launched pools with risk scoring |
| `trending-signals` | $0.05 | Composite ranking of trending tokens + whale activity |

### Arbitrage Layer (cross-venue)
| Endpoint | Cost | Purpose |
|----------|------|---------|
| `perps-cross-venue-funding` | $0.015 | Rates across Jupiter, Adrena, Hyperliquid, dYdX |
| `perps-basis-signal` | $0.015 | Net-yield-after-borrow basis trade scanner |
| `perps-market-structure` | $0.012 | OI, utilization, skew per market |

### LLM Reasoning
| Endpoint | Cost | Purpose |
|----------|------|---------|
| `query` | $0.003 | Plain English → synthesized answer |
| Any endpoint with `format: "llm"` | varies | Natural language briefing instead of raw JSON |

## Cost Estimate
~$0.05 per full agent tick (token enrichment + perps check + trending scan).
$800 capital covers ~16,000 ticks — more than enough for 48 hours.

## Key Implementation Details

### Free Demo (rate-limited)
```python
POST https://api.solenrich.com/demo/enrich
{"address": "TOKEN_MINT_OR_WALLET"}
# 10 queries/hr per IP, single-address only
```

### Paid (x402)
```python
POST https://api.solenrich.com/entrypoints/{endpoint}/invoke
Headers: Content-Type: application/json
Body: {"mint": "...", "format": "llm"}
# Returns 402 if no x402 payment header
```

### Output Format
- `format: "json"` — structured data for programmatic use
- `format: "llm"` — natural language briefing for LLM context
- `format: "both"` — JSON + `llm_summary` field

### Error Handling
- HTTP 402 → payment required (x402 USDC needed)
- HTTP 429 → rate limited (10 free queries/hr)
- Timeout → 15s default, retry with backoff

## Routine Structure
```python
CATEGORY = "Solana Data"

class Config(BaseModel):
    endpoint: str = Field(default="enrich-token-light", description="...")
    address: str = Field(default="", description="Token mint or wallet")
    format: str = Field(default="llm", description="json, llm, or both")
    use_demo: bool = Field(default=True, description="Use free demo endpoint")

async def run(config: Config, context) -> str:
    payload = _build_payload(config)
    data = await _call_solenrich(config.endpoint, payload, config.use_demo)
    return _format_result(data, config)
```

## MCP Integration (for Claude Desktop)
```json
{
  "mcpServers": {
    "solenrich": {
      "type": "streamable-http",
      "url": "https://api.solenrich.com/mcp"
    }
  }
}
```
