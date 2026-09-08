# x402 Gateway Server-Side Verification Loop (Aug 2, 2026)

The **seller-side** half of x402 compatibility. The checker side (EIP-712
`extra.name/version`, `/.well-known/x402`, assessment chips) is in
`x402scan-compatibility.md`. This file is the GATEWAY side — what makes a
paying agent actually get data.

## The Core Lesson

A gateway that returns a spec-perfect 402 but **cannot receive a standard
payment** is a wall, not a door. That was our exact state: $0 traction despite
10K+ visitors/week, because three stacked bugs meant bots could discover us
but never complete a payment.

**Always test the FULL loop, not just discovery:**
`discovery → 402 → pay → proof header → 200 with real data`

## Bug Stack That Killed Traction (all three required fixing)

1. **Wrong payment header.** Gateway only read private `x-402-token`.
   Standard x402 v2 clients send `Authorization: x402 <proof>`; older
   convention is `X-Payment`. Every real client's proof was ignored → 402.
2. **Proxy path mangling.** Even with a valid token, the proxy stripped
   `/v1/` and forwarded wrong paths → backend 404.
3. **Routing table vs manifest mismatch.** Manifest advertised 6 services,
   `BACKEND_ROUTES` only mapped old keys to wrong paths, and 4 of 6 services
   had NO backend at all (returned stubs after payment).

## The Fix Pattern (in `/root/vaults/gentech/10-Labs/x402-gateway/server.py`)

### 1. Accept standard proof headers

```python
def extract_proof(request):
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("x402 "):
        return auth[5:].strip()
    xpay = request.headers.get("X-Payment") or request.headers.get("X-PAYMENT")
    if xpay:
        return xpay.strip()
    # legacy private header kept for backward compat only
    legacy = request.headers.get("x-402-token") or request.headers.get("X-402-Token")
    if legacy:
        return legacy.strip()
    return None
```

### 2. Verify the proof

- **Production:** CDP facilitator `POST https://api.cdp.coinbase.com/platform/v2/x402/verify`
  with `{paymentPayload, paymentRequirements}` envelope. Needs `CDP_API_KEY`
  (+ `CDP_API_KEY_SECRET` for HMAC-signed requests with
  `X-CDP-Timestamp`/`X-CDP-Signature` headers).
- **Dev/simulation:** local HMAC over
  `amount:recipient:nonce:validAfter:validBefore` with `GATEWAY_SECRET` —
  must match your SDK's proof format.
- Mode switch: `PAYMENT_VERIFY_MODE=simulation|cdp|auto` in env. **Pitfall:**
  with `auto`, if `CDP_API_KEY` is set but no secret, CDP calls fail and you
  must NOT fall back to simulation on a genuine rejection — return 402.

### 3. Route to the real backend (3-tuple table)

```python
BACKEND_ROUTES = {
    # service_key: (backend_base, public_path_prefix, backend_path_prefix)
    "token_security": ("http://127.0.0.1:8088", "score/", "/v1/score/"),
    "agent_discovery": ("http://127.0.0.1:8091", "search", "/v1/agents/search"),
}
URL_TO_SERVICE = {"security": "token_security", "agents": "agent_discovery"}
```

FastAPI splits `/v1/{service}/{path}` — `path` arrives as e.g. `score/0x...`,
NOT `security/score/0x...`. Strip the public prefix, apply the backend prefix,
forward. Forward `X-Payment-Proof` (and legacy `X-402-Token`) to backends —
rugcheck-style MVP gates accept any non-empty proof.

## Manifest Truth Rule

**The manifest is a promise.** Only list services with live, correctly-routed
backends. 4 phantom services = paid calls return stubs = reputation damage
worse than not listing them. Either build the backends or trim the manifest
(`/var/www/gentechlabs/.well-known/x402-bazaar`). Bumped to v8.0.0 with the 6
real services.

## The Verification Matrix (run for EVERY service at EVERY price point)

| Case | Expected |
|------|----------|
| correct payment proof | **200 + real data** |
| underpaid proof (e.g. $0.01 on a $0.02 service) | 402 (proves amount check works) |
| no proof | 402 |

Underpayment rejection is a FEATURE — it proves the gate checks amounts, not
just header presence.

## Keyless Data Sources for Backends (all verified live Aug 2026)

| Service | Source | Gotcha |
|---------|--------|--------|
| agent_discovery | `https://8004scan.io/api/v1/agents` | Returns `{items,total,...}` — read `.items`. Fields are **snake_case**: `agent_id`, `chain_id`, `owner_address`, `x402_supported`, `is_testnet`. Filter `is_testnet`/known testnet chain IDs (84532, 11155111, 1187947933). |
| defi_lp_analytics | `https://api.dexscreener.com/latest/dex/tokens/{addr}` | `.pairs[]` with liquidity/volume/fee. Fee-to-liquidity + buy-ratio scoring mirrors LFJ engine. |
| wallet_analysis | Solana RPC `getTokenAccountsByOwner` + DexScreener per-mint pricing | RPC POST JSON-RPC; cap token scan (~40), skip zero balances, price each mint via DexScreener. |
| nft_search | Magic Eden v2 `https://api-mainnet.magiceden.dev/v2/collections` | **NO search param** (400s). Fetch `offset=0&limit=100` (offset/limit must be multiples of 20) and filter client-side. |

## Deployment

- systemd template: `/etc/systemd/system/x402-backend@.service` — one unit,
  enable per service: `systemctl enable --now x402-backend@<name>.service`
- Ports 8091-8094; each backend has `/v1/health` + one paid endpoint
- Backends live in `/root/gentechlabs/services/*.py`; kit copies in
  `a2a/services/` or repo `services/` dir

## Log It

Full symptom→cause→fix→verification→lesson entry in
`/root/vaults/gentech/11-Mess Hall/infrastructure-issues-playbook.md`
(Issue #4 = gateway couldn't accept standard payments; Issue #5 = phantom
endpoints). Jordan's directive: every infra issue gets logged there so we
diagnose recurring problems in minutes and help partners faster.
