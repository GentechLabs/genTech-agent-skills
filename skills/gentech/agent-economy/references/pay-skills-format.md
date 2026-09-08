# Pay-Skills Format Reference

Solana Foundation's pay-skills catalog format for listing x402-powered APIs.

## PAY.md Structure

```yaml
---
name: <unique-api-name>          # kebab-case, prefixed with org
title: <Human-readable title>    # "Org — API Name"
category: <category>             # shopping, finance, security, etc.
version: 1.0.0
author: <org-name>
description: >                   # One-line description
  <What the API does>
  <Payment model and network>
endpoints:
  - method: GET|POST
    path: /v1/<endpoint>
    description: <What it does>
    price_usd: <price>
    request: { <param>: "<type>" }
    response: { <field>: "<type>" }
network: base|solana
currency: USDC
payment_protocol: x402
base_url: https://<your-domain>
---

# <Title>

<Description>

## Endpoints

- `GET /v1/<endpoint>` — <Description> ($<price>)

## Payment

x402 USDC on Base. Each call returns a `Payment-Required` header with x402 challenge when payment is needed.
```

## Categories

- `shopping` — Deal tracking, price comparison
- `finance` — DeFi, yields, gas prices
- `security` — Token security, rug checks
- `travel` — Flights, hotels, destinations
- `data` — Web scraping, content extraction
- `ai-agents` — Agent discovery, routing, identity
- `identity` — ERC-8004, KYC, verification
- `wallets` — Smart wallet deployment

## Validation Checklist

- [ ] Name is unique and kebab-case
- [ ] Title follows "Org — API Name" pattern
- [ ] All endpoints have method, path, description, price
- [ ] Request/response examples are valid JSON
- [ ] Network matches your x402 deployment
- [ ] base_url is correct and live

## Submission Process

1. Fork `solana-foundation/pay-skills` repo
2. Add `PAY.md` to `providers/<org>/<api-name>.md`
3. Validate with `pay skills validate`
4. Submit PR with description
5. Wait for review (typically 1-3 days)

## Common Mistakes

1. **Wrong network** — Must match your x402 deployment (Base for us)
2. **Missing price** — Every endpoint needs `price_usd`
3. **No health endpoint** — Include `/v1/health` for discoverability
4. **Vague description** — Be specific about what the API does
5. **No request/response examples** — Helps agents understand usage
