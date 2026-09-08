# AgentCash Integration Reference

**Platform:** https://agentcash.dev
**Purpose:** AI agents buy data/APIs on your behalf. 959K+ paid calls, $100K giveaway.

## Integration Status

- **OpenAPI spec:** LIVE at gentechlabs.net/openapi.json
- **Endpoints:** 12 with x-payment-info
- **Apply for giveaway:** agentcash.dev/onboard

## Requirements

1. **OpenAPI spec** at `GET /openapi.json`
2. **x-payment-info** on each paid endpoint
3. **x-discovery** with ownership proofs
4. **info.x-guidance** for user-friendly discovery
5. **info.contact.email** for verification

## OpenAPI Spec Format

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "GenTech Labs API Suite",
    "x-guidance": "Use Rugcheck for token safety...",
    "contact": {"email": "jordanjones0902@gmail.com"}
  },
  "x-discovery": {
    "ownershipProofs": ["gentechlabs-erc8004-1770"]
  },
  "paths": {
    "/v1/score/{mint}": {
      "get": {
        "x-payment-info": {
          "price": {"mode": "fixed", "currency": "USD", "amount": "0.010000"},
          "protocols": [{"x402": {}}]
        }
      }
    }
  }
}
```

## Revenue Potential

- 959K+ paid calls already happening
- Our 12 APIs capture a share
- $100K giveaway = free money
- Partners (Nansen, Zapper) = credibility

## Timeline

- **Today** — ✅ OpenAPI spec created
- **Tomorrow** — Apply for $100K giveaway
- **This week** — Fund wallet for verification
- **Next week** — Monitor for discovery
