# x402scan.com / x402-list.com Compatibility — Verified Fixes (Aug 2026)

Two external monitors check x402 services: **x402scan.com** (auto-detects APIs that
return proper 402 responses) and **x402-list.com** (live listing with per-service
ASSESSMENT chips: reliability / compliance / signability / price / risk / traction).
The listing URL for our gateway: `https://x402-list.com/services/gentech-labs-x402-gateway`.

## The #1 Fix: EIP-712 domain parameters in every accepts[] entry

x402-list's **signability** chip ("route not signable") and its compliance grade
(capped at C) fail when a 402 envelope's EVM `accepts[]` entry lacks the token's
EIP-712 domain parameters:

> "At least one EVM route on this service returns its 402 without the EIP-712
> domain parameters (extra.name and extra.version), so a standard x402 client
> cannot build the signature for that route."

**Fix — add `extra: {name, version}` to EVERY accepts entry** (this is the EIP-712
domain of the payment token, e.g. USDC = name `"USD Coin"`, version `"2"`):

```python
"accepts": [
    {
        "scheme": "exact",
        "network": "eip155:8453",
        "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # USDC on Base
        "amount": str(price_atomic),
        "payTo": os.getenv("X402_PAYTO_ADDRESS", "0x..."),
        "maxTimeoutSeconds": 300,
        "extra": {                      # <-- this was the missing field
            "name": "USD Coin",
            "version": "2"
        }
    }
],
```

The spec source (Binance x402 v2 verify-payment docs) confirms: `extra.name` and
`extra.version` are the token EIP-712 domain name/version. Hardcoding is fine for
a fixed asset; if supporting multiple tokens, derive name/version per asset.

**Where it lives in our stack:** `/root/vaults/gentech/10-Labs/x402-gateway/server.py`
→ `build_payment_required()` (systemd unit `x402-api.service`, port 8090, behind
api.gentechlabs.net). Deploy = `systemctl restart x402-api` then verify:
`curl -s <endpoint> | python3 -m json.tool` and check `accepts[0].extra`.

## Canonical discovery path: /.well-known/x402

x402-list / generic checkers probe `/.well-known/x402` (no extension). Our nginx
serves `/.well-known/` statically from `/var/www/gentechlabs/.well-known/`, which
had `x402.json` and `x402-bazaar` but NOT a bare `x402` file → 404.

**Fix:** `cp x402.json x402 && chown www-data:www-data x402 && chmod 644 x402`
in `/var/www/gentechlabs/.well-known/`. (Adding a FastAPI route alone is NOT
enough — nginx's `location /.well-known/` static block shadows it.)

## Assessment chip semantics (what the checkers actually measure)

| Chip | Meaning | Our status (Aug 2, 2026) |
|------|---------|--------------------------|
| reliability | uptime + response time probes (every ~16 min) | 100% (255 checks, ~200ms avg) |
| compliance | 14 x402 conformance checks; the EIP-712 `extra` check is the cap | 13/14 → 14/14 after fix |
| signability | can a standard x402 client build the signature from the captured 402 | fixed by extra.name/version |
| price | captured 402 amount in USD | $0.01 |
| risk | deterministic blocklist / reserved-brand flags only | clean |
| traction | on-chain USDC settlements via measured facilitators | $0 until real volume — "honest, not broken" |

**Traction $0 is NOT a defect** — it means no on-chain settlement recorded yet.
Only real x402 volume moves it. Don't treat it as a bug to fix.

## Verification recipe (run after any 402-shape change)

```bash
# 1. The paid endpoint returns 402 with a signable envelope
curl -s "https://api.gentechlabs.net/v1/security/score?address=0x1234567890abcdef1234567890abcdef12345678" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); a=d['accepts'][0]; print(a.get('extra'), a.get('payTo'))"
# expect: {'name': 'USD Coin', 'version': '2'} 0xF9...

# 2. Discovery paths serve 200
curl -s -o /dev/null -w "%{http_code}" https://api.gentechlabs.net/.well-known/x402        # 200
curl -s -o /dev/null -w "%{http_code}" https://api.gentechlabs.net/.well-known/x402-bazaar # 200
```

x402-list rescans roughly every 5h — a fix shows up on the listing by the next scan.

## Related

- `agent-economy` §3 (x402 Bazaar listing) — 402-missing payment check
- `references/x402-api-deployment-pattern-jul-2026.md` — full deploy pattern
- `references/agentic-market-cdp-facilitator.md` — Coinbase auto-indexing path
