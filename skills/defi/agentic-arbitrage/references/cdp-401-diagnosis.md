# Coinbase CDP 401 — Diagnostic Path (Aug 4, 2026)

A `401 Unauthorized` from the Coinbase CDP API is a **credential-side rejection**, NOT
a code bug. This is the fastest way to prove it, so you don't chase a phantom code issue.

## The definitive test — run the SDK's own call

```bash
cd /root/.hermes/profiles/gentech
set -a; source .env 2>/dev/null; set +a
python3 -c "
import os, asyncio
from cdp import CdpClient
async def main():
    c = CdpClient()
    try:
        accts = dict(list(await c.evm.list_accounts()))
        print('SUCCESS', accts)
    except Exception as e:
        print('FAIL', getattr(e,'http_code', getattr(e,'status','?')))
    finally:
        await c.close()
asyncio.run(main())
"
```

- `200` → key is valid; problem is elsewhere (funding, path, token support).
- `401` → Coinbase rejects the credential itself. Stop debugging code.

## Why you can trust the 401 conclusion

1. **Key format is correct.** `CDP_API_KEY_ID` is a 36-char UUID, `CDP_API_KEY_SECRET`
   is an 88-char Ed25519 base64 key. Both present in `.env`.
2. **JWT signs fine.** `generate_jwt(JwtOptions(...))` produces a valid token.
3. **Real endpoint confirmed.** The SDK base is `https://api.cdp.coinbase.com/platform`,
   and the accounts resource is `/v2/evm/accounts` (NOT `/v1/...`). Full URL:
   `https://api.cdp.coinbase.com/platform/v2/evm/accounts`.
   The SDK signs with `parsed_url.path` = `/platform/v2/evm/accounts`, `request_host` =
   `api.cdp.coinbase.com`. If you hand-sign, use EXACTLY these.
4. Even a correct-format key can 401 if it was **rotated/revoked** after it last worked,
   belongs to a **different project**, or lost its **EVM account read scope**.

## Red herrings

- A second var named `CDP_API_KEY` (32 chars) is NOT a valid signing secret — it fails
  `_parse_private_key` with "Key must be either PEM EC key or base64 Ed25519 key".
  Ignore it; the real pair is `CDP_API_KEY_ID` + `CDP_API_KEY_SECRET`.

## Fix (user action, not code)

Regenerate the API key in the Coinbase portal (cloud.coinbase.com → project → API keys),
scope it to the EVM account with read + trade, hand the fresh ID+secret to the agent,
update `.env`, re-run the test above until `200`.

## Wallet secret (the trade-capable credential)

- `CDP_API_KEY_SECRET` = read-only API auth (balances, quotes).
- `CDP_WALLET_SECRET` = server-account signing secret (authorizes a real swap).
- It lives at `/root/.blockrun/cdp-wallet-secret` (chmod 600) — provided by Jordan.
- **It is NOT auto-read by `gta_coinbase_leg.py`.** The SDK reads it from the
  `CDP_WALLET_SECRET` env var or the `CdpClient(wallet_secret=...)` arg. If you want a
  real swap to sign, load this file into `CDP_WALLET_SECRET` (or pass it to the client)
  — it is stored but not wired into execution as of Aug 4.
- Only `cbBTC` (Base, `0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf`, 8 dec) is a verified
  tradeable leg. AVAX/PAXG/etc. return "unsupported-token" until their real Base contract
  addresses are looked up and added to `SUPPORTED` in `gta_coinbase_leg.py`.
