# x402 Bazaar Listing Guide

## How It Works

**No manual registration needed.** Your API gets listed automatically when:
1. You use the CDP Facilitator for payments
2. You add the Bazaar discovery extension to routes
3. You complete at least one successful payment settlement

## Steps to Get Listed

### 1. Set Up x402 Payment Gateway
```python
# Use CDP Facilitator for verify/settle
FACILITATOR = "https://api.cdp.coinbase.com/platform/v2/x402"
```

### 2. Add Bazaar Discovery Extension
```python
# In your route middleware, add discovery metadata
declareDiscoveryExtension({
    "input": {"mint": "So11...xxx"},
    "inputSchema": {"type": "object", "properties": {"mint": {"type": "string"}}},
    "output": {"score": 85, "level": "low_risk"},
})
```

### 3. Complete One Payment
- Any agent paying for your API triggers auto-listing
- Settlement must complete (verify alone is not enough)
- Check `EXTENSION-RESPONSES` header for Bazaar status

## Builder Codes (ERC-8021) — On-Chain Attribution

Builder Codes enable on-chain attribution tracking for x402 payments. They append ERC-8021 Schema 2 codes to settlement transaction calldata.

### Minting
- Mint at base.dev → Settings → Builder Code
- Format: `^[a-z0-9_]{1,32}$` (lowercase, digits, underscores)
- ERC-721 NFT on Base chain

### Three Attribution Codes
| Field | Set by | Description |
|-------|--------|-------------|
| `a` | Resource server (us) | App code — identifies our API |
| `w` | Facilitator | Wallet code — identifies settlement |
| `s` | Client | Service code(s) — buyer attribution |

### Our Builder Code
- Code: `bc_gentech` (pending mint at base.dev)
- Payout address: `0x7ebff188f2Eba16518C02864589b1403a5d1296a`
- Server version: v1.1.0 (builder code in /v1/apis response)

### Python SDK Status
- The x402 Python SDK does NOT have a builder_code extension yet (TypeScript only)
- Workaround: add builder code metadata to API response manually
- The CDP facilitator handles CBOR encoding on settlement

### Multi-Chain Status
| Chain | Builder Code Support |
|-------|---------------------|
| Base | ✅ Live — ERC-8021 |
| Solana | ❌ No equivalent yet |
| Arbitrum | ❌ No equivalent yet |
| Avalanche | ❌ No equivalent yet |

## Visibility Rules
- Newly indexed resources appear promptly
- 30-day rolling window: need at least one call/settlement per 30 days
- High-cardinality paths (UUIDs, addresses) may be normalized

## Our APIs (Deployed on Port 8090)

| API | Price | Category |
|-----|-------|----------|
| `/v1/score/{mint}` | $0.01 | Blockchain |
| `/v1/defi/{protocol}` | $0.05 | Finance |
| `/v1/travel/search` | $0.01 | Travel |
| `/v1/content/{platform}` | $0.02 | Media |
| `/v1/agent/search` | $0.005 | AI |
| `/v1/agent/{agent_id}` | $0.005 | AI |

## Revenue Monitor
- Cron job tracks BlockRun balance every 6 hours
- Alerts when balance drops below $5 (low) or $2 (critical)
- Script: `revenue-monitor.py` in scripts directory

## Community Bazaars
- x402bazaar.org offers manual registration
- CDP Bazaar is automatic (preferred)
