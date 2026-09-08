# Treasury Defender — Airdrop/Dust-Token Defense Service (Aug 2, 2026)

GenTech's 7th paid x402 service. Born from the fake "RBTC.b" airdrop that hit
Jordan's Avalanche wallet — the scammer's token became a product.

**Service file:** `/root/gentechlabs/services/treasury_defender.py` (port **8096**)
**Manifest:** `/.well-known/x402-bazaar` v9.0.0 — `/v1/defender/classify/{chainId}/{token}` @ $0.01
**Gateway wiring:** `BACKEND_ROUTES["treasury_defender"]` + `URL_TO_SERVICE["defender"]` in `/root/vaults/gentech/10-Labs/x402-gateway/server.py`
**systemd:** `x402-backend@treasury_defender.service` (template unit)

## Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /v1/defender/classify/{chainId}/{token}` | Read-only classification: KNOWN / UNKNOWN / SUSPICIOUS + reasons |
| `POST /v1/defender/quarantine/{chainId}/{token}` | Record token as flagged (hidden from value, never auto-traded) |
| `GET /v1/defender/flagged` | List quarantined tokens (persisted `/root/gentechlabs/data/treasury-quarantine.json`) |
| `POST /v1/defender/burn/{chainId}/{token}` | Returns transfer-to-0xdead calldata for the OWNER to sign — never auto-signs |

## The security principle (critical)

**Quarantine + don't touch beats burning.** Auto-burning unknown tokens is
how wallets get drained — interacting with a hook-bearing scam contract
(approve/transfer) is the trap. The burn endpoint deliberately returns
calldata for the user to execute in their own wallet, and only for tokens
classified SUSPICIOUS via non-interactive signals (homoglyph / zero
liquidity). Never auto-execute.

## Homoglyph detection (the core trick)

Scam tokens impersonate real symbols with Unicode confusables: Cyrillic
`С`/`Ѕ` (look like C/S), dotted `Ḍ` (looks like D), combining marks
(U+0301 acute). Detection recipe:

1. `unicodedata.normalize("NFKD", symbol)` then drop combining marks.
2. Map confusables via a lookup table: `С→C, Ѕ→S, Ḍ→D, А→A, В→B, Е→E, Н→H,
   К→K, М→M, О→O, Р→P, Т→T, Х→X, І→I, У→Y` (+ lowercase variants).
3. Strip to `[A-Za-z0-9]`, uppercase, compare against known-token symbols.

The NFKD-only approach FAILS on Cyrillic C (stays `С`, ≠ `C`) — the
confusables map is the actual fix. Verified: `ÚSDС`, `USḌC`, `UЅDС` all
caught; real `USDC`/`BTC.b` correctly KNOWN.

## ABI string decode gotcha (eth_call)

`eth_call` string returns are ABI-encoded: `[offset][length][padded bytes]`.
Decoding the whole hex as UTF-8 yields `\x00`-padding noise. Correct parse:

```python
h = raw[2:]
if len(h) >= 128:
    length = int(h[64:128], 16)
    if length > 0 and 128 + length * 2 <= len(h):
        h = h[128:128 + length * 2]
return bytes.fromhex(h).decode("utf-8", errors="replace").strip("\x00")
```

## Port conflict pattern

8095 was already taken by the ARC gateway (`python3 -m src.gateway` in
`/root/programmable-money-x402/gateway` — a legitimate long-running process,
NOT stale junk). Fix: systemd drop-in override instead of killing:

```bash
mkdir -p /etc/systemd/system/x402-backend@treasury_defender.service.d
cat > /etc/systemd/system/x402-backend@treasury_defender.service.d/port.conf << 'EOF'
[Service]
Environment=PORT=8096
EOF
systemctl daemon-reload && systemctl restart x402-backend@treasury_defender.service
```

Always check `ss -tlnp | grep <port>` and identify the process before
killing — killing a live gateway to free a port is worse than moving.

## x402 simulation proof format (for testing paid endpoints)

The gateway's `verify_proof_simulation` expects a specific proof shape — the
"proof is not valid JSON" / "invalid signature" loop cost several iterations.
Correct format for a $0.01 service (amount = 10000 atomic units):

```python
import json, hmac, hashlib, time
secret = "dev-secret-change-in-production"   # GATEWAY_SECRET fallback
recipient = "0xF9dcBFF7EdDd76c58412fd46f4160c96312ce734"
now = int(time.time())
amount, nonce = "10000", "test-1"
proof = {"chain": "eip155:8453", "token": "USDC", "amount": amount,
         "recipient": recipient, "validAfter": now - 10,
         "validBefore": now + 300, "nonce": nonce}
proof["signature"] = hmac.new(secret.encode(),
    f"{amount}:{recipient}:{nonce}:{now-10}:{now+300}".encode(),
    hashlib.sha256).hexdigest()
# Header: Authorization: x402 <json.dumps(proof)>
```

Key details: signature is a field INSIDE the JSON (not a separate header),
HMAC over `amount:recipient:nonce:validAfter:validBefore`, keys are
`chain`/`token` (NOT `network`/`asset`), amount must equal
`int(price * 1_000_000)`. Underpay on a $0.02 service → 402 (that's the
verification working, not a bug).

## Adding a new paid service — full checklist

1. Write FastAPI backend with `/v1/health` + `X-Payment-Proof` gate (402 when missing).
2. systemd template unit `x402-backend@<name>.service` (or drop-in for port).
3. Gateway: `BACKEND_ROUTES` tuple + `URL_TO_SERVICE` public-segment mapping.
4. Restart gateway: `py_compile` → `systemctl restart x402-api` → `is-active` → E2E curl with valid proof.
5. Manifest: bump `version`, add service row (`/var/www/gentechlabs/.well-known/x402-bazaar`).
6. **Registry** (`11-Mess Hall/marketplace-listings-registry.md`) + **Bankr skill**
   (`Gentech-Labs/genTech-agent-kit/master/skills/bankr/SKILL.md`, push to master branch).
7. Commit backend to kit repo (`/root/repos/genTech-agent-kit/services/`).

## Bankr registry correction lesson

The marketplace registry initially said "Bankr NOT LISTED" — wrong: $TREASURY
launched via Bankr Jul 22 (build queue said "shipped", the row was never
created). **Before declaring a platform unlisted, cross-check the build
queue + git history (`git -C vault log --grep=<platform>`) — "already
shipped" work is easy to forget when the registry was built later.**
