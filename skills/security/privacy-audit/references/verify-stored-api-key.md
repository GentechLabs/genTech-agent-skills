# Verifying a Stored API Key Against the Provider's Live API (proven Aug 26, 2026)

After a user pastes a key and you store it to `.env`, confirm it's actually
valid by hitting a real provider endpoint with it — read-only, never echo the
value. This catches a dead/typo'd key before you build an integration on it.

## Pattern — read the key from .env, never inline it

Write a small script that reads the key from `.env` and curls a known endpoint:

```bash
#!/usr/bin/env bash
KEY="$(grep '^CROSSMINT_API_KEY=' ${PROFILE_DIR}/.env | cut -d= -f2)"
curl -s -o /dev/null -w "%{http_code}\n" \
  "https://www.crossmint.com/api/2022-06-09/collections" -H "X-API-KEY: ${KEY}"
```

## Reading the HTTP code

- `200` — key authenticates. Valid.
- `401`/`403` — key rejected. Invalid or lacks permission.
- `404` — key AUTHENTICATED but that exact path doesn't exist. Try a known
  real endpoint (e.g. the provider's v1 collections/orders list) before
  concluding the key is bad — a 404 on a wrong path is NOT a failed key.

## Pitfall — inline curl with the key gets blocked

Embedding the raw key in a one-line `curl ... -H "X-API-KEY: <value>"` command
trips the command-parser blocklist (oversized/parseable payload). The command
is saved to `cache/blocked-scripts/` and refused. Write the script to a file
that reads the key from `.env` and run it — never inline the secret.

## CrossMint specifics (the case that proved this)

- Production key prefix `sk_production_...`; server/secret privilege class.
- v1 endpoints (`/api/2022-06-09/collections`, `/orders`) return 200 with a
  valid key; the newer `v1-alpha2/wallets` path 404s (not a key failure).
- Production onramp needs KYB + an order form; the key alone won't unlock card
  onramp at scale. Agent Wallets (x402/MPP-native) is fully API-driven.
