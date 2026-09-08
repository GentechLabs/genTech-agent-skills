# Verify any ERC-20 / token address on-chain before trusting it in config

A wrong or typo'd token address silently breaks x402 settlement detection, revenue
monitoring, and payout tracking — the monitor just never sees the transfers, with no
obvious error. **Always confirm the address is real code AND the right token before
wiring it into a gateway, revenue scanner, or settlement path.**

## Check 1 — is there contract code at the address? (`eth_getCode`)

```bash
curl -s -X POST https://mainnet.base.org -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":["0x<ADDR>","latest"]}' \
  | python3 -c "import json,sys; c=json.load(sys.stdin)['result']; print('HAS CODE' if c!='0x' and len(c)>2 else 'NO CODE — dead address')"
```

`0x` or empty result = no contract deployed there = the address is wrong or the chain is wrong.

## Check 2 — what token is it? (symbol / name / decimals)

```bash
for sig in 0x95d89b41 0x06fdde03 0x313ce567; do   # symbol() / name() / decimals()
  curl -s -X POST <RPC> -H "Content-Type: application/json" \
    -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"eth_call\",\"params\":[{\"to\":\"0x<ADDR>\",\"data\":\"$sig\"},\"latest\"]}" \
    | python3 -c "import json,sys; r=json.load(sys.stdin)['result']; print(r)"
done
```

- `0x` on a `decimals()` call = no code there.
- Confirmed canonical USDC per chain: **Base** `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` (symbol "USDC", name "USD Coin", decimals 6), **Avalanche** `0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E`, **BNB** `0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d`. But verify ANY address you're about to trust rather than assuming the constant is right in a given copy.

## Real case (Aug 12, 2026)

The Revenue Monitor's `USDC_CONTRACTS["base"]` was `0x83358933e2...` — **no contract code on Base**, a dead address. The scanner had been looking for USDC transfers to a non-existent contract and would **never have caught marketplace payouts** (Nevermined, AgentLux). One `eth_getCode` check per address before trusting it closes this class of silent revenue gap.
