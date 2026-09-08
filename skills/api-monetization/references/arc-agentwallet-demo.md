# ArcAgentWallet Interactive Demo — Deployment Pattern

> Deploy a live, interactive hackathon demo for an x402-based agent wallet on Arc. Judges click buttons, watch the full 402 challenge → payment → response flow in a terminal-style UI. No real USDC moves.

## What It Demonstrates

1. **ArcAgentWallet dashboard** — agent wallet with USDC balance on Arc testnet
2. **Autonomous agent actions** — click to trigger: check price, analyze wallet, stream data
3. **Full x402 flow** — HTTP 402 challenge → auto-solve → paid response
4. **Arc-native messaging** — "USDC as gas, no ETH needed", "sub-second finality"

## Architecture

```
Browser (demo.gentechlabs.net/arc/)
    │
    ├─ GET /v1/price?symbol=ETH        → api.gentechlabs.net (x402 gateway, port 8090)
    │   ← HTTP 402 with accepts[] challenge
    │
    ├─ POST /v1/simulate-pay            → gateway generates HMAC proof
    │   ← {proof, authorization_header}
    │
    └─ GET /v1/price + Authorization    → gateway verifies + returns data
        ← HTTP 200 with paid response
```

## Files

### 1. Nginx config (`/etc/nginx/sites-enabled/demo`)

Serve the static HTML from a subdirectory with SSL:

```nginx
server {
    server_name demo.gentechlabs.net;
    root /var/www/gentechlabs;

    location /arc/ {
        root /var/www/gentechlabs/arc-demo;
        index index.html;
        try_files /index.html =404;
    }

    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/demo.gentechlabs.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/demo.gentechlabs.net/privkey.pem;
}
```

**Pitfall:** Do NOT use `alias` with `try_files` — nginx will 403 on directory index. Use `root` + explicit `try_files /index.html` instead. This was the #1 debugging time-sink.

### 2. Gateway endpoint: `/v1/simulate-pay`

Add to `x402-gateway/server.py` after the `/health` endpoint:

```python
@app.post("/v1/simulate-pay")
async def simulate_pay(request: Request):
    """Generate a simulated x402 proof for demo purposes.
    HMAC-signed with GATEWAY_SECRET — no real USDC moves."""
    body = await request.json()
    amount = str(body.get("amount", "0"))
    recipient = body.get("recipient", "0x0000000000000000000000000000000000000001")
    nonce = str(body.get("nonce", str(int(time.time()))))
    valid_after = int(body.get("validAfter", 0) or 0)
    valid_before = int(body.get("validBefore", 0) or int(time.time()) + 3600)

    secret = os.getenv("GATEWAY_SECRET", "dev-secret-change-in-production")
    signature = hmac.new(
        secret.encode(),
        f"{amount}:{recipient}:{nonce}:{valid_after}:{valid_before}".encode(),
        hashlib.sha256,
    ).hexdigest()

    proof = {"amount": amount, "recipient": recipient, "nonce": nonce,
             "validAfter": valid_after, "validBefore": valid_before,
             "signature": signature, "network": "eip155:8453"}
    proof_json = json.dumps(proof)
    auth_header = f"x402 {base64.urlsafe_b64encode(proof_json.encode()).decode()}"

    return Response(content=json.dumps({
        "proof": proof, "authorization_header": auth_header,
        "note": "Simulated proof — no real USDC moves. Demo only."
    }), media_type="application/json", headers={"Access-Control-Allow-Origin": "*"})
```

Restart after adding: `systemctl restart x402-api`

### 3. HTML playground structure

Key sections:
- **Wallet panel** — shows agent balance, Arc testnet chain ID, gateway URL
- **Stats panel** — service count, latency, auth method
- **Action buttons** — each triggers the full 402 → simulate → retry flow
- **Terminal** — shows the SDK code being executed + step-by-step output

The JavaScript flow:
1. `fetch(GATEWAY + path)` → expect 402
2. Parse challenge, call `/v1/simulate-pay` to get proof
3. `fetch(GATEWAY + path, {headers: {Authorization: auth_header}})` → get data
4. Log each step to terminal with colored output

### 4. CORS requirement

Gateway must have CORS middleware with `allow_origins=["*"]` — the demo runs on `demo.gentechlabs.net` but calls `api.gentechlabs.net` (different origin).

## Verification

```bash
# 1. Demo page loads
curl -s -o /dev/null -w "%{http_code}" https://demo.gentechlabs.net/arc/  # 200

# 2. Gateway returns 402 on unpaid call
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8090/v1/price?symbol=ETH  # 402

# 3. Simulate-pay works
curl -s -X POST http://127.0.0.1:8090/v1/simulate-pay \
  -H "Content-Type: application/json" \
  -d '{"amount":"0.001","recipient":"0x0"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['proof']['signature'][:20])"  # prints hex signature

# 4. CORS headers present on 402 response
curl -si http://127.0.0.1:8090/v1/price?symbol=ETH | grep -i "access-control"  # allow-origin: *
```

## Pitfalls

- **Don't use `alias` + `try_files $uri/` in nginx** — causes 403 directory index errors. Use `root` + explicit file path.
- **Gateway must have CORS** — otherwise browser fetch from demo domain gets blocked. The gateway already has `CORSMiddleware(allow_origins=["*"])`.
- **Demo defaults to localhost:8088** — always update the gateway URL input to the live API before showing judges.
- **Simulate-pay uses HMAC** — in production this is EIP-3009 `transferWithAuthorization` on Arc. The demo explicitly says "simulation mode — no real USDC moves."
