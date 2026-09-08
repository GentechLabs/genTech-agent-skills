# CDP Bazaar Self-Settlement (Coinbase x402 Bazaar)

Getting a gateway listed on the **CDP x402 Bazaar** (`api.cdp.coinbase.com/platform/v2/x402`)
is settlement-driven, like OpenDexter — but with its own set of non-obvious traps.
Hard-won live transcript, Aug 4 2026 (GenTech gateway). Read this BEFORE wiring a
CDP-settlement path so you don't re-derive the auth + envelope schema by trial and error.

## The indexing mechanism (from Coinbase's Bazaar docs)

- **Indexing runs after SETTLEMENT completes — verify alone is NOT enough.** The CDP
  facilitator catalogs your resource the first time it **settles** a payment for that
  endpoint. `paymentPayload.resource` must be set in the payload.
- **No separate registration step.** There is no form. Settlement through the CDP
  facilitator is the trigger.
- **30-day recency window:** endpoints with no activity in 30 days are excluded from
  results. Newly-indexed resources with no calls yet are not subject to this filter.
- **Quality metrics refresh on a 6-hour schedule.** After a settlement, the resource may
  not move up in search for up to 6 hours. Don't panic when a fresh search returns 0.
- **Verify your listing:** `GET /v2/x402/discovery/search?query=<domain>&limit=5`
  (no auth needed for discovery reads). Empty results immediately after settlement is
  expected — the ranking update lag is the reason, not a failed settlement.

## The gateway must call /settle after /verify

Many gateways (incl. GenTech's) only call `/verify` and never `/settle`. The Bazaar
indexes on settlement, so **verify alone means you'll never be listed even though payments
"work."** After a successful `/verify` (HTTP 200), POST the same envelope to `/settle`.

```
POST https://api.cdp.coinbase.com/platform/v2/x402/verify   → 200 {isValid:true, payer}
POST https://api.cdp.coinbase.com/platform/v2/x402/settle   → 200 (indexes the resource)
```

`/settle` submits the on-chain tx (EIP-3009, gas-sponsored by CDP) and is what triggers
the Bazaar cataloging.

## CDP JWT auth — HMAC is NOT accepted (the 401 trap)

CDP returns **401 Unauthorized** if you authenticate with a plain HMAC or a bearer key.
It requires a **JWT** signed with your API key secret:

- **Ed25519 key** (base64, 64 bytes decoded — GenTech's `CDP_API_KEY_SECRET` is this)
  → JWT signed with **EdDSA**.
- **PEM EC key** → JWT signed with **ES256** (PKCS8 import).
- Key type detection: `len(base64.b64decode(secret)) == 64` → Ed25519; else try PEM EC.

JWT claims (mirrors the CDP SDK's `generateJwt`):
```json
header = {"alg":"EdDSA","kid":"<CDP_API_KEY_ID>","typ":"JWT","nonce":"<16-byte hex>"}
claims = {
  "sub": "<CDP_API_KEY_ID>",
  "iss": "cdp",
  "aud": "cdp_service",
  "uris": ["POST api.cdp.coinbase.com/platform/v2/x402/verify"],  // method host path
  "iat": now, "nbf": now, "exp": now + 120
}
```
Python (Ed25519, via `nacl.signing`):
```python
import base64, json, secrets, time
from nacl.signing import SigningKey
def b64url(b): return base64.urlsafe_b64encode(b).rstrip(b"=").decode()
decoded = base64.b64decode(secret); sk = SigningKey(decoded[:32])
now = int(time.time()); nonce = secrets.token_hex(16)
hdr = {"alg":"EdDSA","kid":key_id,"typ":"JWT","nonce":nonce}
claims = {"sub":key_id,"iss":"cdp","aud":"cdp_service",
          "uris":[f"POST api.cdp.coinbase.com/platform/v2/x402/verify"],
          "iat":now,"nbf":now,"exp":now+120}
si = f"{b64url(json.dumps(hdr).encode())}.{b64url(json.dumps(claims).encode())}"
jwt = f"{si}.{b64url(sk.sign(si.encode()).signature)}"
headers = {"Authorization": f"Bearer {jwt}"}
```
The `uris` claim **binds the exact method+host+path** — use the verify path when calling
verify and the settle path when calling settle (they differ). A JWT signed for `/verify`
won't work on `/settle`.

**Diagnostic signal:** if CDP returns 401 → auth problem (JWT). If it returns 400 with a
schema message → auth is accepted, payload shape is wrong. That's the fast triage.

## The exact /verify + /settle envelope schema (the trial-and-error win)

CDP requires `{x402Version, paymentPayload, paymentRequirements}` — and the
`paymentRequirements` field is the trickiest part. It must be **the accepted payment
option object directly** (with `scheme` at the top level), NOT wrapped in an `accepts`
array, and NOT a re-built structure.

Working shape (confirmed CDP returns `{"isValid":true,"payer":"0x..."}`):
```python
payload = {
    "x402Version": pp.get("x402Version", 2),
    "paymentPayload": pp,                       # the full payment payload
    "paymentRequirements": pp["accepted"],      # the accepted option object, direct
}
```
where `pp["accepted"]` looks like:
```json
{"scheme":"exact","network":"eip155:8453","asset":"0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
 "amount":"10000","payTo":"0xF9dc...","maxTimeoutSeconds":300,"extra":{"name":"USD Coin","version":"2"}}
```

**Rejected shapes** (all return 400 `'paymentRequirements' is invalid: must match one of
[x402V2PaymentRequirements, x402V1PaymentRequirements]. x402V2PaymentRequirements
requires 'scheme'`):
- `{"paymentPayload": proof}` (missing x402Version + paymentRequirements) → 400
- `{"paymentRequirements": {"accepts": [option]}}` (wrapped) → 400
- `{"paymentRequirements": {"x402Version":2,"resource":{...},"accepts":[...],"extensions":{}}}` → 400
- `{"paymentRequirements": {"scheme":"exact","network":...,"amount":...,"payTo":...}}` (partial) → 400

**Ground-truth capture method:** instead of guessing the schema, monkeypatch `globalThis.fetch`
in Node and print `opts.body` on the `/verify` call the CDP SDK makes. That shows the exact
envelope the SDK sends — replicate it in the gateway. This is far faster than trial-and-error
against the 400 responses.

## Client-side header — the PAYMENT-SIGNATURE gap

The x402 SDK sends the payment proof in a header your gateway must read:
- **v2** → `PAYMENT-SIGNATURE` header (base64-encoded JSON payload)
- **v1** → `X-PAYMENT` header (base64-encoded JSON)

A gateway's `extract_proof` that only reads `Authorization: x402` / `X-Payment` /
`x-402-token` will silently IGNORE the SDK's real proof and keep returning 402. Add:
```python
psig = request.headers.get("PAYMENT-SIGNATURE") or request.headers.get("payment-signature")
if psig: return psig.strip()
```
Also: the v2 SDK **base64-encodes** the JSON payload. If your verifier does
`json.loads(proof_str)` directly, base64-decode first, then parse.

## Node SDK import map (exact paths)

The x402 JS API differs from the Python docs. Working imports:
```js
import { x402Client } from "@x402/core/client";
import { ExactEvmScheme } from "@x402/evm/exact/client";
import { wrapFetchWithPayment } from "@x402/fetch";
import { privateKeyToAccount } from "viem/accounts";

const client = new x402Client();
client.register("eip155:*", new ExactEvmScheme(privateKeyToAccount(pk)));
const fetchWithPayment = wrapFetchWithPayment(fetch, client);
```
Note: `x402Client` must be `new`-ed (it's a class, not a factory). The CDP SDK's
`CdpX402Client` needs `CDP_WALLET_SECRET` to provision a managed wallet — if you only have
`CDP_API_KEY*`, use the vanilla `x402Client` with your own EVM key instead; the CDP
facilitator still settles it (which is what triggers Bazaar indexing).

## Dependency isolation

`@dexterai/x402` (Dexter) and `@coinbase/cdp-sdk` (CDP) conflict on `@x402/core` version
(Dexter wants 2.12, CDP wants ^2.19). **Install them in separate directories**, don't mix
in one package.json. Each self-settle script lives in its own dir with its own deps.

## Base RPC for on-chain balance checks

`base-rpc.publicnode.com` works for `eth_call` balance reads; `base.llamarpc.com` returns
HTTP 521 and publicnode may 403 raw urllib (User-Agent block). Add a `User-Agent` header:
```python
req = urllib.request.Request(rpc, data=..., headers={"Content-Type":"application/json","User-Agent":"curl/8"})
```

## End-to-end debug order (the sequence that worked)

1. Auth first — fix the JWT until CDP returns 400-schema, not 401.
2. Then envelope — capture the SDK's real `/verify` body via fetch monkeypatch, replicate it.
3. Then `/settle` — add the settle call after successful verify.
4. Then gateway restart (systemd `x402-api.service`, reads env from `.env` — flip
   `PAYMENT_VERIFY_MODE` to `cdp`; the `.env` is credential-protected, edit via `sed` not
   the patch tool).
5. Run the self-settle script → expect a 200 on the retry.
6. Verify the Bazaar search (allow up to 6h for ranking).
