# OpenDexter Self-Settlement — Triggering Auto-Catalog

Verified Aug 3, 2026. OpenDexter (open.dexter.cash/mcp) catalogs any API that
receives a **real x402 settlement through Dexter's facilitator** — no registration
form, no approval. To get listed, settle ONE real payment against our own endpoint
through Dexter's facilitator, then the resource appears as "discovered" and you claim
it to add branding/description/verification.

## Why self-settlement is the only path

Dexter auto-discovery extracts the resource URL/method from the payment payload, the
seller wallet from `payTo`, and metadata + hit counts. **Testnet USDC does NOT trigger
it** — it must be real mainnet USDC moving through Dexter's facilitator (~$1 is enough).

## Verify Dexter already sees your endpoints (read-only, free)

Initialize an MCP session against `https://open.dexter.cash/mcp`, then `tools/call`
`x402_check` with your paid endpoint:
- Paid endpoint (e.g. `.../v1/security/score/0x0`) → expect `requiresPayment=True,
  authMode=paid, statusCode=402` → Dexter already recognizes it as x402-paid.
- Free endpoint (e.g. `/health`) → `free=True, statusCode=200` → reachability.
- If `requiresPayment=True` on your paid endpoint, the only remaining step is a real
  settlement. NOT listed + zero settlements is *expected*, not a failure.

MCP handshake: `initialize` → `notifications/initialized` → `tools/list`/`tools/call`.
SSE framing: strip `event: message\n` and `data: ` prefixes before parsing JSON.
Search responses prepend a `SECURITY:` untrusted-data notice before the JSON — find
the first `{` and parse from there. Public RPCs (base.llamarpc.com, 1rpc.io) 403
Python urllib; `base-rpc.publicnode.com` with a `User-Agent: Mozilla/5.0` header works.

## The Dexter Node-agent pay flow (self-settle.mjs)

Dexter's `@dexterai/x402` client `payAndFetch(url, init, wallets, opts)` settles through
Dexter's facilitator automatically when the endpoint 402s — this is the trigger. Built
at `10-Labs/x402-gateway/self-settle.mjs`:

```bash
npm i @dexterai/x402 viem
EVM_PRIVATE_KEY=<hex> node self-settle.mjs
```

```js
import { payAndFetch, createEvmKeypairWallet } from "@dexterai/x402/client";
const wallet = await createEvmKeypairWallet(process.env.EVM_PRIVATE_KEY); // ⚠️ ASYNC — must await
const result = await payAndFetch(TARGET, { method: "GET" }, { evm: wallet }, {
  maxAmountAtomic: "20000",        // 0.02 USDC cap (6 decimals)
});
```

**Pitfall — `createEvmKeypairWallet` is ASYNC.** Calling it without `await` returns an
empty `{}` wallet object; the SDK then reports `No connected wallet for any available
network: eip155:8453` (or `Invalid character`). Always `await` it. Do NOT pass a
`chainId` option to `payAndFetch` — the client auto-detects the network from the 402
response's `accepts[]`; a hardcoded `chainId` that doesn't match the wallet slot shape
causes the same "no connected wallet" error. (The docs example omits it for a reason.)

`payAndFetch` probes once; on 402 it signs, retries, returns `PayResult`. Narrow on
`ok` then `paid`:
- `ok:true, paid:true` → `amountPaid`, `txSignature`, settled receipt. The endpoint is
  now auto-cataloged.
- `ok:false, reason:"insufficient_funds"` → wallet needs more USDC on the target chain.
- `reason:"timeout"` → safe to retry (no payment sent). `reason:"payment_unconfirmed"`
  → do NOT blind-retry (could pay twice).
- EVM wallets via `createEvmKeypairWallet(hex)`; Solana via `createKeypairWallet(base58)`
  with `USDC_MINT` from the SDK. You can pass both `{solana, evm}` and it settles on
  whichever network the 402 asks for.

## The funding-gap pattern (check before assuming you can settle)

Self-settlement needs a wallet you can **sign from** that holds USDC. These often
split across two wallets — check both sides:

| Side | Need | GenTech example |
|---|---|---|
| Funded wallet | Has USDC but NO private key in env | `0x7ebff...` (Jordan's ERC-8004/revenue owner wallet, 2.97 USDC on Base) |
| Signable wallet | Has private key but NO USDC | `0x3d117...` (GTA arb wallet, key in `secure/gentech-arb-wallet.json`, 0.001 USDC) |

Verify balances on-chain before claiming readiness (publicnode Base RPC works):
`balanceOf` for USDC (`0x70a08231` + padded address) → `/1e6`; `eth_getBalance` for gas.

**The unlock is one of:** (a) send ~$2 USDC on Base to the signable wallet, or
(b) provide the private key for the funded wallet (store in `config/secrets.env`,
never echo in chat). Q402 trial is gasless *relay* — not a funded mainnet wallet.
`treasury_manager.py` sample wallets are hardcoded fake data. Don't treat either as
settlement-capable.

## The receive-side blocker — gateway verify mode must match the facilitator

**The #1 reason a self-settlement "fails" after funding is not the SDK — it's the
gateway's verify mode.** A gateway in `PAYMENT_VERIFY_MODE=simulation` verifies proofs
via a local HMAC secret, NOT real EIP-3009 signatures. When the Dexter SDK signs a real
EIP-3009 payment and retries, the simulation-mode gateway **rejects it** (returns 402
again), so no settlement ever completes → no auto-catalog. The SDK then surfaces a
generic `Invalid character` error, which is misleading.

**Diagnose with a fetch wrapper** (wrap `globalThis.fetch` to log every call):
```
>> FETCH GET <endpoint>            # probe → 402
>> FETCH GET <endpoint>            # retry with payment → 402 AGAIN (rejected!)
>> FETCH POST api.dexter.cash/api/base/rpc   # balance check
RESULT ok:false reason:error detail:Invalid character
```
The retry returning 402 again (not 200) is the tell: the gateway rejected the real
proof. The `Invalid character` is a downstream symptom, not the cause.

**Fix:** the gateway must verify via the SAME facilitator the payment settles through.
- To catalog on **CDP Bazaar**: set `PAYMENT_VERIFY_MODE=cdp` (uses CDP keys already in
  env) so the gateway accepts real EIP-3009 proofs and completes settlement.
- To catalog on **OpenDexter/Dexter**: the payment must settle through Dexter's
  facilitator, which means the gateway must accept Dexter-facilitated proofs — a bigger
  change than flipping a mode flag.

**Two separate catalogs, two separate mechanisms (research, Aug 3 2026):**
- **CDP Bazaar** (Coinbase): catalogs on the first **settlement** through the CDP
  facilitator, with `paymentPayload.resource` set. Our gateway already declares
  `bazaarResourceServerExtension` + `discoveryUrl`, so it's wired for CDP Bazaar.
- **OpenDexter/Dexter**: catalogs on settlement through **Dexter's** facilitator.
  Different facilitator → different verify path.

**Decision rule:** if the goal is "get listed somewhere real," prefer the path the
gateway was built for (CDP Bazaar — flip to `cdp` mode, use existing keys). OpenDexter
requires re-wiring the gateway to accept Dexter-facilitated proofs. Don't assume one
settlement lists you on both — they're separate facilitators.

## After settlement

Search `x402_search` for our host (e.g. `api.gentechlabs.net`); once present, claim the
discovered resource on dexter.cash to add branding/description/verification.

### Verifying the settlement triggered cataloging — `capabilitySearch` (Node)

After a successful settlement, do NOT expect the gateway to appear immediately. Verify
with the SDK's `capabilitySearch` (read-only, free, no wallet). Two gotchas confirmed
Aug 12, 2026:

1. **`capabilitySearch` takes an OBJECT, not a string.** `capabilitySearch({ query: "..." })`
   — passing a bare string throws `capabilitySearch: query is required`. Use the object form:
   ```js
   import { capabilitySearch } from "@dexterai/x402/client";
   const r = await capabilitySearch({ query: "token security" });
   const strong = r?.strongResults || [], related = r?.relatedResults || [];
   // our gateway is listed if any result.url contains "gentechlabs.net"
   [...strong, ...related].forEach(a => console.log(a.name, a.price, a.url));
   ```
2. **Indexing is NOT immediate — it lags ~24h.** A successful settlement does not list
   you right away. Searches immediately after will return 0 strong/0 related hits for
   your host even though the payment landed on-chain. Do NOT re-settle to force it
   (burns USDC). Instead arm a **24h re-check cron** that re-runs `capabilitySearch`
   for your host and reports when the gateway appears.

Relevant intent queries that surface x402 API competitors (useful to sanity-check the
catalog is live): "token security", "wallet analysis", "get ETH price", "nft search".

