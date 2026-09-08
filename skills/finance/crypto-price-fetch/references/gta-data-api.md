# GTA Data API — x402 Product Reference

## API Endpoint

\`\`\`
GET /arb
URL: https://api.gentechlabs.net/arb
Content-Type: application/json
\`\`\`

## Deployment

| Detail | Value |
|--------|-------|
| Internal port | 8081 |
| Public URL | https://api.gentechlabs.net/arb |
| nginx | /etc/nginx/sites-enabled/gentech — location /arb → proxy_pass 127.0.0.1:8081 |
| Service start | GTA_API_PORT=8081 python3 gta-arb-api.py |
| Runs as | Persistent background process |

## Response

\`\`\`json
{
  "status": "ok",
  "timestamp": "2026-07-25T13:41:25.053466+00:00",
  "assets": 6,
  "data": {
    "BTC": {"perp": 64148.50, "spot": 64117.36, "basis_bps": 4.86, "type": "CONTANGO"},
    "ETH": {"perp": 1865.05, "spot": 1863.95, "basis_bps": 5.87, "type": "CONTANGO"}
  }
}
\`\`\`

## Revenue Model

Two tiers:
1. **Free** — rate-limited (10 req/hr), no API key
2. **Paid** — 0.02 USDC per call via x402

### x402 Flow

1. Client calls without payment → 402 response with payment headers
2. Client sends 0.02 USDC to gentechlabs.eth on Base
3. Client re-requests with proof → gets data

Current implementation serves all requests freely (no API key enforced). The 402 response structure is ready. Set GTA_API_KEY to enable paid-only mode.

## Marketplace Targets

- EvoMap Capsules
- OKX AI Marketplace
- Hive / freelance platforms

## Source

- Monitor: /root/.hermes/profiles/gentech/scripts/gta-arb-monitor.py
- API: /root/.hermes/profiles/gentech/scripts/gta-arb-api.py
- Repo: github.com/ProtoJay4789/gentech-treasury-trader
