# x402-list.com Submission

**Status:** Submitted Jul 29, 2026 (pending review)
**URL:** https://x402-list.com/submit
**API:** https://x402-list.com/api/v1/submit (POST, form-encoded)

## Submission Details

- **Service name:** GenTech Labs x402 Gateway
- **Base URL:** https://api.gentechlabs.net
- **Website URL:** https://gentechlabs.net
- **Email:** jordanjones0902@gmail.com
- **Category:** Blockchain
- **Description:** Pay-per-call API gateway with 6 services across Base Network. Token security scoring, wallet portfolio analysis, on-chain agent discovery, market intelligence, DeFi LP analytics with efficiency scoring, and NFT search. All endpoints use x402 micropayments (USDC on Base).
- **Endpoints:** /v1/security/score, /v1/wallet/portfolio, /v1/agents/search, /v1/market/price, /v1/defi/lp, /v1/nft/search
- **Notes:** Full x402 Bazaar manifest at https://api.gentechlabs.net/.well-known/x402-bazaar. Gateway returns proper HTTP 402 with accepts[] payload. 6 chains supported (Base, Ethereum, Avalanche, Solana, BNB, Arbitrum). Prices range from $0.005 to $0.02 per call.

## Pitfalls

1. **Endpoint paths must NOT contain `{param}` curly braces** — The validator rejects paths like `/v1/security/score/{address}`. Use plain paths like `/v1/security/score` instead. The first submission with `{address}` paths was rejected but still counted toward the 7-day cooldown.

2. **7-day cooldown between submissions** — The form rejects resubmissions from the same email within 7 days. After 14 days, resubmission requires a $0.50 x402 payment via their API.

3. **Auto-probe + manual review** — After submission, they probe endpoints for valid HTTP 402 responses, then manually review. Submissions still pending after 7 days are auto-rejected.

## Next Steps

- Monitor for approval email at jordanjones0902@gmail.com
- If rejected, resubmit via API with correct paths (no curly braces) after 14 days
- Also register on PayAI Bazaar at facilitator.payai.network for OrbitX402 → xPay discovery
