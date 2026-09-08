# Circle Agent Marketplace — Registration Reference

## Platform
- **URL:** https://agents.circle.com
- **Seller Form:** https://forms.gle/7YFzvdmMcn1JH5tF6
- **Docs:** https://developers.circle.com/gateway/nanopayments/quickstarts/seller
- **SDK:** `@circle-fin/x402-batching` (npm)

## Requirements
- Must have x402-enabled endpoints returning HTTP 402 with valid payment challenge
- Uses Circle Gateway for settlement (x402 batching)
- Web form submission only — needs Jordan's browser
- 41 services currently listed as of Jul 15, 2026

## Format
Submit via Google Form: Company name, website, work email, developer doc URL, and anything else. No specific endpoint format required — describe your API in natural language.

## Our Prepared Endpoints (5)

| Service | Endpoint | Price | Category |
|---------|----------|-------|----------|
| Token Risk | `GET /api/token/risk?address=&chain=` | $0.01 | Security |
| Market Intel | `GET /api/intel/search?q=` | $0.005 | Finance |
| Wallet Analyzer | `GET /api/wallet/analyze?address=` | $0.025 | Finance |
| Game Intel | `GET /api/games/search?q=` | $0.005 | Media |
| NFT Search | `GET /api/nft/search?q=` | $0.005 | Media |

## Key Difference from Pay-Skills
- Circle marketplace is agent-facing (agents discover and pay for APIs), not a developer registry
- Uses Circle's own Gateway settlement, not generic x402 facilitator
- Lower friction — no PR, no OpenAPI spec, just a web form
- All endpoints must accept GET (Circle probes with GET requests)

## Notes
- Gateway wallet address needed for settlement. Store in vault/credentials.
- Docs saved at `10-Labs/circle-marketplace-submission.md` for copy-paste into form.
