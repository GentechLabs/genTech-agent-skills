# Latch402 — x402 Endpoint Verification

**Agent:** 5577 (call from any agent environment)
**Purpose:** Scans your x402 endpoint and returns a readiness report before marketplace submission or Global Challenge entry.

## How to Use

From any agent environment:
```
I'd like to use the service provided by Agent 5577.
```

Latch402 scans the endpoint and returns:
- Detailed readiness report of what's remaining
- What to fix before submission
- Or confirms it's 100% ready to submit

## Open-Source Alternatives

| Tool | Type | What It Checks |
|------|------|----------------|
| suryast/x402-check | CLI + npm library | 402 challenge shape, EIP-712 typed data, settlement path, well-known schema |
| onescales/x402checker | CLI | x402 support detection, options, networks, amounts, tokens, pay-to addresses |
| x402 Surface Check | GitHub Action | CI-ready x402 readiness checks |
| xpaysh/awesome-x402 | GitHub Action | Endpoint validator for 402 challenge, EIP-712, settlement, well-known |

## When to Use

- Before submitting to any x402 marketplace (OKX, Syra, x402scan, etc.)
- Before entering the Algorand x402 Global Challenge
- After deploying a new x402 endpoint
- After making changes to payment middleware

## Related

- `agent-economy` skill — section 7 (Algorand x402 Global Challenge)
- `x402-api-compliance` skill — full x402 audit/fix/deploy workflow
