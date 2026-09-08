# CDP Bazaar Self-Settlement — Getting Listed (Aug 3, 2026)

How to actually get a service indexed on the **CDP x402 Bazaar** (Coinbase's
discovery catalog). This is the hard-won, verified mechanism — the gateway
looked "live" and x402-compliant but was NOT listed because it never settled.

## The core rule: SETTLE, not verify

Per Coinbase docs: **"The CDP Facilitator catalogs your service the first time
it SETTLES a payment for that endpoint... indexing happens when settlement
succeeds. Verify alone is not enough."**

- A resource server that only calls `/verify` and never `/settle` will NEVER
  appear in the Bazaar, no matter how many 402 challenges it serves.
- The payment payload sent to the facilitator MUST include
  `paymentPayload.resource` so CDP knows which resource to catalog.
- Ranking updates on a **6-hour schedule** — a newly settled payment won't
  move search results immediately. Allow up to 6h before checking.
- **30-day recency window:** resources with no activity in 30 days drop out of
  results. Newly indexed resources with no calls yet are exempt.

## The two catalogs (don't confuse them)

| Catalog | Trigger | Facilitator |
|---------|---------|-------------|
| **CDP Bazaar** (Coinbase) | First successful **settle** through CDP facilitator | `api.cdp.coinbase.com/platform/v2/x402` |
| **OpenDexter / Dexter** | Any x402 payment **settled through Dexter's facilitator** | Dexter facilitator |

They catalog differently. Our gateway was wired for CDP Bazaar (declares
`bazaarResourceServerExtension: true` + `discoveryUrl` in its 402 response) but
was in `PAYMENT_VERIFY_MODE=simulation` — so it never settled through any real
facilitator and appeared on neither.

## The three gateway fixes (all in `10-Labs/x402-gateway/server.py`)

### 1. `extract_proof` must read the `PAYMENT-SIGNATURE` header

The CDP SDK (x402 v2) sends the payment in a **`PAYMENT-SIGNATURE`** header
(base64-encoded JSON). The gateway only read `Authorization: x402`,
`X-Payment`, and `x-402-token`. Add:

```python
psig = request.headers.get("PAYMENT-SIGNATURE") or request.headers.get("payment-signature")
if psig:
    return psig.strip()
```

Verified from the SDK source (`@x402/core/dist/esm/chunk-*.mjs`):
- v2 → `{ "PAYMENT-SIGNATURE": base64(payload) }`
- v1 → `{ "X-PAYMENT": base64(payload) }`

### 2. `verify_proof_via_cdp` must base64-decode the proof

The CDP SDK sends base64-encoded JSON, but the gateway did `json.loads`
directly. Handle both raw JSON and base64:

```python
try:
    proof = json.loads(proof_str)
except json.JSONDecodeError:
    import base64 as _b64
    decoded = _b64.b64decode(proof_str + "=" * (-len(proof_str) % 4)).decode("utf-8")
    proof = json.loads(decoded)
```

### 3. Add the `/settle` call after a successful `/verify`

This is the one that actually gets you listed. After `/verify` returns 200,
POST the same payload to `/settle`:

```python
settle_resp = client.post(
    "https://api.cdp.coinbase.com/platform/v2/x402/settle",
    json=payload,
    headers={**headers, "Content-Type": "application/json"},
)
```

## CDP facilitator auth: JWT, NOT HMAC

The gateway's original auth used `X-CDP-Timestamp` + `X-CDP-Signature` (HMAC) —
CDP rejects this with **401 Unauthorized**. CDP requires a **JWT** signed with
the API key secret, with a `uris` claim binding method/host/path.

Key format determines algorithm (from `@coinbase/cdp-sdk/_cjs/auth/utils/jwt.js`):
- **base64 Ed25519 key (64 bytes)** → `EdDSA` (our key is this)
- **PEM EC key** → `ES256`

JWT shape (EdDSA):
```python
header = {"alg": "EdDSA", "kid": api_key_id, "typ": "JWT", "nonce": hex(16 bytes)}
claims = {
    "sub": api_key_id, "iss": "cdp", "aud": "cdp_service",
    "uris": [f"POST api.cdp.coinbase.com/platform/v2/x402/verify"],
    "iat": now, "nbf": now, "exp": now + 120,
}
# signing_input = b64url(header) + "." + b64url(claims)
# sig = Ed25519.sign(signing_input)  (seed = first 32 bytes of base64-decoded secret)
# jwt = signing_input + "." + b64url(sig)
```

**Verification that auth is correct:** a JWT-signed call returns **400**
(payload validation) not **401** (auth). 401 = wrong auth; 400 = auth accepted,
payload wrong.

### CRITICAL: the JWT is PATH-BOUND — mint one per endpoint (Aug 4, 2026)

This is the bug that made the money never move. A JWT's `uris` claim pins it
to ONE path. A token minted for `/verify` is **rejected with 401 on `/settle`**,
and vice-versa. Refactor JWT generation into a helper taking the op path, and
call it fresh for each endpoint:

```python
def _jwt(op_path):  # op_path = "/platform/v2/x402/verify" or ".../settle"
    ...  # header + claims with uris = [f"POST api.cdp.coinbase.com{op_path}"]
verify_headers = {"Authorization": f"Bearer {_jwt('/platform/v2/x402/verify')}"}
settle_headers = {"Authorization": f"Bearer {_jwt('/platform/v2/x402/settle')}"}  # FRESH token
```

**Probe to confirm the path-binding:** POST to `/settle` with a settle-path JWT
→ expect **400** (payload validation, auth accepted). POST with a verify-path
JWT → **401 Unauthorized**. If settle uses the verify token, you get 401 and
nothing settles — even though `/verify` returned 200 and the gateway served the
resource.

## `paymentRequirements` schema — the other 400 (Aug 4, 2026)

CDP `/verify` and `/settle` body is `{ x402Version, paymentPayload,
paymentRequirements }`. The `paymentRequirements` field must be **the accepted
payment option object directly** (with `scheme` at the top level) — NOT wrapped
in an `accepts` array.

- `paymentRequirements = {accepts: [accepted_opt]}` → 400 `"x402V2PaymentRequirements requires 'scheme'"`
- `paymentRequirements = accepted_opt` (has `scheme`) → **200 `{"isValid":true}`**

```python
payload = {
    "x402Version": _ver,
    "paymentPayload": _pp,          # full payload incl. payload.authorization + accepted
    "paymentRequirements": _pp.get("accepted", {}),  # accepted option directly, NOT {accepts:[...]}
}
```
Ground truth: capture the exact body the CDP SDK sends by monkeypatching
`globalThis.fetch` to log the `/verify` request body — never guess the schema.

> **Debugging method that cracked all of this:** don't reverse-engineer the
> facilitator's schema by trial-and-error 400s. Instrument the actual SDK —
> monkeypatch `globalThis.fetch` to dump the real `/verify` body + auth headers,
> and inspect `@x402/core` compiled source (the `encodePaymentSignatureHeader`
> and `HTTPFacilitatorClient.settle` methods). Ground truth beats guessing.

## Verify settlement actually landed on-chain — don't trust the 200

The gateway serves the resource even when `/settle` FAILS (it treats settle as
non-fatal). A 200 with no `payment-response` header does NOT prove settlement.
Confirm by checking the USDC balance delta on Base:

```python
# balanceOf(payer) before vs after via eth_call — a clean self-settle drops ~0.02 USDC
# (0.01 for /verify + 0.01 for /settle). No delta = settle silently failed.
```

If the payer balance is unchanged, the settle failed (usually the path-bound
JWT 401 above) — fix that, not the gateway's resource serving.

## Backend routing trap: settle against the RIGHT service (Aug 4, 2026)

Self-settling against a **Solana-only** service with an **EVM** address returns
a non-payment `400 {"error":"invalid_mint"}` AFTER payment succeeds — it looks
like a settlement failure but is really the backend rejecting the address
format. Our `security/score` proxies Rugcheck (Solana-only). Pick a paid
endpoint that accepts the address type you test with — `wallet/portfolio` and
`defi/lp` handle EVM addresses and return proper payment challenges.

**Probe backends before choosing a self-settle target** (expect a clean 200 or a
`payment_required` challenge, NOT `invalid_mint`/`Not Found`):

## The self-settlement script

`10-Labs/x402-gateway/cdp-settle/cdp-settle.mjs` — pays our own endpoint with
our own EVM key (GTA arb wallet, USDC on Base) through the CDP facilitator,
triggering verify + settle + Bazaar indexing.

**Why our own key instead of `CdpX402Client`:** `CdpX402Client` needs
`CDP_WALLET_SECRET` to provision a managed wallet. We don't have that, but we
DO have our own EVM key with USDC on Base. The vanilla x402 client signs with
our key and the CDP facilitator still settles it — which is what triggers
indexing.

**Correct TypeScript client pattern** (the Python docs example does NOT match
the JS API):
```js
import { x402Client } from "@x402/core/client";
import { ExactEvmScheme } from "@x402/evm/exact/client";
import { wrapFetchWithPayment } from "@x402/fetch";
import { privateKeyToAccount } from "viem/accounts";

const client = new x402Client();
client.register("eip155:*", new ExactEvmScheme(privateKeyToAccount(pk)));
const fetchWithPayment = wrapFetchWithPayment(fetch, client);
const response = await fetchWithPayment(TARGET, { method: "GET" });
```

**Dependency conflict gotcha:** `@dexterai/x402` (Dexter) pins `@x402/core@2.12`
but `@coinbase/cdp-sdk` needs `@x402/core@^2.19`. They clash in one package.json.
Use a **separate directory** (`cdp-settle/`) for the CDP script so the two
SDKs don't fight.

## Wallet funding reality

To self-settle you need USDC in a wallet you can SIGN from. Two wallets, opposite
problems (Aug 3):
- `0x7ebff...` (Jordan's owner wallet) — HAS USDC but NO private key in env
- `0x3d117...` (GTA arb wallet) — HAS the key but had no USDC

Fix: fund the signable wallet (`0x3d117...`) with ~$2 USDC on Base. The
settlement caps at $0.02, so $1-2 is plenty. No gas needed — the CDP
facilitator sponsors gas.

## Verify listing

```bash
curl "https://api.cdp.coinbase.com/platform/v2/x402/discovery/search?query=gentech&limit=5"
# empty resources = not listed yet; allow up to 6h after a real settle
```

## The bigger product insight (Jordan, Aug 3)

Every x402 marketplace catalogs DIFFERENTLY (CDP settles→indexes, Dexter
settles→catalogs, Syra uses on-chain identity/8004). Nobody has written the
connective tissue. This friction is itself a product: **"x402 Marketplace
Connector Guides — How to Get Listed Everywhere"** — a living, maintained
protocol-by-protocol reference. Captured in `09-Green Room/ideas.md`.
