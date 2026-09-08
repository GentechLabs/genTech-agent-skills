# x402 Test Harness

Free public reference endpoint for testing x402 compliance.
Deployed by GenTech Labs.

## Endpoint

```bash
curl -i https://test.api.gentechlabs.net/hello
# → 402 Payment Required
# → Payment-Required: <base64 v2 challenge>
```

## Available routes

| Route | Price | Description |
|-------|-------|-------------|
| `/hello` | $0.001 | Greeting — basic x402 flow test |
| `/evm/weather` | $0.001 | EVM (Base Sepolia) test |
| `/solana/weather` | $0.001 | Solana Devnet test |

## Usage

1. Curl the endpoint → get 402 + Payment-Required header
2. Sign the challenge with your wallet
3. Resubmit with X-Payment-Proof
4. Get 200 + response data

## Can be used for

- Validating your x402 client implementation
- Testing the Academy Module 1 flow
- Quick sanity check before production deployment
