# Multi-Facilitator Rails — Verified Map & Client Compatibility (Aug 30, 2026)

Live-probed `/supported` on all four facilitators while flipping the GenTech gateway (api.gentechlabs.net) to multi-rail challenges. Use this when a buyer agent fails to pay: match their client/facilitator against this map BEFORE touching server code.

## Facilitator map (probed `/supported`, 2026-08-30)

| Facilitator | Endpoint | x402 v2 rails | Notes |
|---|---|---|---|
| PayAI | facilitator.payai.network | base, avalanche, polygon, **xlayer (eip155:196)**, arbitrum, skale, solana mainnet (+ testnets) | Settles ALL rails GenTech advertises; free tier 10k settles/mo |
| Dexter | x402.dexter.cash | base, avalanche, polygon, arbitrum, optimism, bsc, worldchain(143), (4663), solana; schemes exact/upto/tab/batch-settlement | **NO X Layer** — their SDK cannot parse it; solana feePayer + gas-sponsored |
| GoPlausible | facilitator.goplausible.xyz | base, base-sepolia, solana mainnet/devnet, algorand (both genesis hashes) | Algorand rail depends on it — CAIP-2 genesis hash must match EXACTLY or proofs unmatchable |
| CDP (Coinbase) | api.cdp.coinbase.com/platform/v2/x402 | base (JWT auth, path-bound tokens) | Proven settle path Aug 19 + Aug 30; **rejects self-pays** |

## Client-compatibility pitfalls (each one cost us a debug cycle)

1. **ASCII-only challenge envelope.** Dexter SDK v5 base64-encodes the payment envelope with `btoa()` → any non-Latin-1 char (em dash U+2014 in `resource.description`, USD₮0 symbol) throws `"Invalid character"` and the buyer dies mid-handshake. Every string inside the 402 challenge must be pure ASCII (`USDT0` not `USD₮0`, `-` not `—`). Comments in server code can stay UTF-8 — only wire payloads matter.
2. **`accepts[0]`-blind clients.** Some clients take the first option without negotiating. Order rails **Base first** (every facilitator settles it), then X Layer, Algorand, Avalanche, Solana. Control via env: `X402_NETWORKS="base,xlayer,algorand,avalanche,solana"`.
3. **OKX single-rail mode is a toggle, not a default.** `X_OKX_COMPLIANT=1` forces a single X Layer USDT0 challenge (OKX A2MCP validator requirement). Leave `0` for public discovery; flip to `1` only while re-running OKX validation, then flip back.
4. **Self-pay rejection.** CDP returns `self_send_not_allowed` when buyer == payTo. Test settles MUST use a different buyer wallet (GenTech: arb wallet 0x3d117B…eCb buys, signer 0x7ebff…96a sells — key at `/root/.hermes/profiles/gentech/secure/gentech-arb-wallet.json`).
5. **npm resolution trap.** package.json declaring `@dexterai/x402@^5.4.2` still resolved to a stale v3.9.0 in `/root/node_modules` when no local install existed. Run `npm install @dexterai/x402@^5.4.2` inside the gateway dir. v5 API: `createBudgetAccount({budget:{total}, evmPrivateKey, maxAmountAtomic, verbose})` → `agent.fetch(url)`; `createX402Client`/`wrapFetch` do NOT exist in v5; `payAndFetch(TARGET, opts, {evm: wallet}, {maxAmountAtomic})` works.
6. **Extensionless twin files.** nginx serves `/.well-known/x402` from the extensionless file `/var/www/gentechlabs/.well-known/x402`; `x402.json` is a SEPARATE file. Updating only one leaves a stale discovery doc live. Update BOTH + `chown www-data:www-data`.
7. **`/tmp` can fill the disk** (hermes sandboxes + build debris). If execute_code starts failing with `[Errno 28]`, switch to terminal and `du -sh /tmp/*` → rm the big stale dirs. 15G of stale builds broke all sandboxed execution once.

## Verification loop (inspect, don't guess)

```bash
# 1) See exactly what a buyer sees:
curl -s -D /tmp/h.txt 'https://api.gentechlabs.net/v1/market/price/ETH' -o /dev/null
PR=$(grep -i 'payment-required' /tmp/h.txt | head -1 | sed 's/^[^:]*: //' | tr -d '\r')
echo "$PR" | base64 -d | python3 -m json.tool

# 2) Check each facilitator's accepted rails:
curl -s https://facilitator.payai.network/supported | python3 -c "import json,sys;[print(k.get('x402Version'),k.get('network')) for k in json.load(sys.stdin)['kinds']]"

# 3) End-to-end settle with a real buyer wallet (~$0.005): node dexter-final.mjs (in gateway dir)

# 4) Confirm the revenue ledger ticked:
python3 /root/.hermes/profiles/gentech/scripts/revenue-monitor.py | grep -A5 'x402 Revenue'
```

## Debug sequence that worked (Aug 30, 2026)

SDK pinned locally → verbose client (`createBudgetAccount` verbose:true) → decode challenge manually → spot the em dash → ASCII-fix server challenge strings → restart gateway → hit `self_send_not_allowed` → switch buyer wallet to arb → settle lands → revenue ledger +$0.005 (tx #8, first new settlement since Aug 19). Full narrative: vault `11-Mess Hall/marketplace-listings-registry.md` (Aug 30 entry).
