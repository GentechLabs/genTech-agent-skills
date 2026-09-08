# Arc x402 Gateway — Deployment Reference

Arc is Circle's L1 blockchain where **USDC is the native gas token** (18 decimals).
Chain ID: 5042002 (testnet). This changes the x402 deployment model significantly
vs standard EVM chains where you need ETH/BNB for gas.

## Key Differences from Standard EVM x402

| Property | Standard EVM (Base, Ethereum) | Arc |
|----------|-------------------------------|-----|
| Gas token | ETH (volatile) | USDC (stable) |
| Gas cost | ~$0.01-0.50 | ~$0.009 flat |
| Decimals | 6 (USDC) | 18 (native USDC) |
| Settlement | Needs ETH for gas + USDC for value | Pure USDC |
| Agent requirement | Must hold 2 assets | Holds 1 asset |

## Arc Testnet Details

| Parameter | Value |
|-----------|-------|
| Chain ID | 5042002 |
| RPC URL | `https://rpc.testnet.arc.network` |
| Explorer | `https://testnet.arcscan.app` |
| Faucet | `https://faucet.circle.com` |
| Currency | USDC (18 decimals) |
| viem chain | `arcTestnet` (built-in) |

## x402 Gateway Architecture on Arc

Since Arc uses USDC as gas, the x402 facilitator model changes:

1. **No gas sponsorship needed** — the agent already holds USDC, which covers both
   the payment value AND the transaction fee. No need for Q402 or Coinbase CDP
   to sponsor gas.
2. **Single-asset wallets** — agents only need USDC. No ETH/BNB bridging.
3. **EIP-3009 still works** — `transferWithAuthorization` works on Arc EVM.
   The facilitator just needs to submit the tx; gas comes from the same USDC.

## FastAPI Gateway Template

```python
# src/gateway.py — Arc x402 Gateway
import os, time, uuid, json, hmac, hashlib
from fastapi import FastAPI, Request, Response, HTTPException
from pydantic import BaseModel

ARC_RPC_URL = os.getenv("ARC_RPC_URL", "https://rpc.testnet.arc.network")
ARC_CHAIN_ID = 5042002
RECIPIENT_ADDRESS = os.getenv("RECIPIENT_ADDRESS", "")
GATEWAY_SECRET = os.getenv("GATEWAY_SECRET", "dev-secret")

PRICING = {
    "micro": {"amount": "0.001", "description": "Token price check"},
    "standard": {"amount": "0.01", "description": "LP analysis"},
    "premium": {"amount": "0.05", "description": "Risk scoring"},
}

app = FastAPI(title="Arc x402 Gateway")

@app.get("/v1/health")
async def health():
    return {"status": "ok", "chain": "Arc Testnet", "chain_id": ARC_CHAIN_ID}

@app.get("/v1/price")
async def get_price(request: Request, symbol: str = "ETH", tier: str = "standard"):
    if tier not in PRICING:
        raise HTTPException(status_code=400, detail=f"Invalid tier")
    
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("x402 "):
        now = int(time.time())
        challenge = {
            "version": "x402-v1",
            "payment": {
                "chain": "arc-testnet",
                "chain_id": ARC_CHAIN_ID,
                "token": "USDC",
                "amount": PRICING[tier]["amount"],
                "recipient": RECIPIENT_ADDRESS,
                "validAfter": now,
                "validBefore": now + 1800,
                "reference": str(uuid.uuid4()),
            },
        }
        return Response(content=json.dumps(challenge), status_code=402,
                       headers={"Content-Type": "application/json"})
    
    # Verify proof (HMAC for simulation, EIP-3009 in production)
    return {"symbol": symbol, "price": 3500.42, "tier": tier}
```

## Testing Pattern

```python
# tests/test_gateway.py
import pytest, hmac, hashlib, time, uuid
from httpx import ASGITransport, AsyncClient
from src.gateway import app, GATEWAY_SECRET

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

def _gen_proof(amount="0.01"):
    now = int(time.time())
    sig = hmac.new(GATEWAY_SECRET.encode(),
        f"{amount}:0xTest:{uuid.uuid4()}:{now}:{now+1800}".encode(),
        hashlib.sha256).hexdigest()
    return {"chain": "arc-testnet", "token": "USDC", "amount": amount,
            "recipient": "0xTest", "validAfter": now, "validBefore": now+1800,
            "nonce": str(uuid.uuid4()), "signature": sig}

@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/v1/health")
    assert resp.status_code == 200
    assert resp.json()["chain_id"] == 5042002

@pytest.mark.asyncio
async def test_402_challenge(client):
    resp = await client.get("/v1/price?symbol=ETH")
    assert resp.status_code == 402
    assert resp.json()["payment"]["chain"] == "arc-testnet"

@pytest.mark.asyncio
async def test_verify_valid(client):
    proof = _gen_proof()
    resp = await client.post("/v1/verify", json=proof)
    assert resp.json()["valid"] is True

@pytest.mark.asyncio
async def test_verify_expired(client):
    proof = _gen_proof()
    proof["validAfter"] = int(time.time()) - 7200
    proof["validBefore"] = int(time.time()) - 3600
    sig = hmac.new(GATEWAY_SECRET.encode(),
        f"{proof['amount']}:{proof['recipient']}:{proof['nonce']}:{proof['validAfter']}:{proof['validBefore']}".encode(),
        hashlib.sha256).hexdigest()
    proof["signature"] = sig
    resp = await client.post("/v1/verify", json=proof)
    assert resp.json()["valid"] is False
```

## Open-Source Readiness Checklist

- [ ] `pyproject.toml` with `[tool.pytest.ini_options]` and `asyncio_mode = "auto"`
- [ ] `.env.example` with placeholder values (no real secrets)
- [ ] `.gitignore` excluding `__pycache__`, `.env`, `.venv/`
- [ ] `LICENSE` (MIT)
- [ ] `README.md` with install, config, and endpoint docs
- [ ] `src/__init__.py` and `tests/__init__.py` (empty, for package discovery)
- [ ] All tests passing: `python3 -m pytest tests/ -v`

## Pitfalls

- **`request := Request` bug** — Never assign `request := Request` in a route function.
  FastAPI injects the request when you add `request: Request` as a parameter.
  Using `Request` (the class) instead of the instance causes `AttributeError: 'property' object has no attribute 'get'`.
- **f-string backslash** — `f"...{', '.join(f'{k} (${v["amount"]})' for ...)}"` fails because
  f-string expressions can't contain backslashes. Extract to a variable first.
- **HMAC constant-time comparison** — Use `hmac.compare_digest()` not `==` for signature verification.
- **Time window validation** — Always check `validAfter`/`validBefore` before signature verification.
  An expired proof with a valid signature is still invalid.
