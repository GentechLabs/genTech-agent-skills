# x402scan Compatibility — Getting Listed on the x402 Block Explorer

## What is x402scan?

x402scan (x402scan.com) is the block explorer, analytics dashboard, and marketplace for x402-paid APIs. It discovers APIs automatically by probing endpoints for 402 responses and parsing OpenAPI specs.

**Key stats (Jun 2026):** 8.58M transactions, $1.11M volume, 119.61K buyers, 39K sellers.

## How x402scan Discovers APIs

1. You enter your API URL at x402scan.com/add
2. x402scan fetches `/openapi.json` from your API
3. It probes each endpoint looking for 402 responses
4. It parses `x402` annotations in the OpenAPI spec
5. If endpoints return 200 without 402 challenges, they show as "errors"

## Requirements for x402scan Listing

### 1. Return 402 for Paid Endpoints

When no payment header is present, return HTTP 402 with x402 payment requirements:

```json
{
  "error": "Payment Required",
  "x402Version": 1,
  "accepts": [{
    "scheme": "x402",
    "network": "base",
    "maxAmountRequired": "10000",
    "resource": "/v1/score/{mint}",
    "description": "Pay $0.01 USDC for /v1/score/{mint}",
    "mimeType": "application/json",
    "payTo": "0xYourPayoutAddress"
  }],
  "facilitator": "https://api.cdp.coinbase.com/platform/v2/x402"
}
```

### 2. OpenAPI Spec with x402 Annotations

Each paid endpoint needs an `x402` field in the OpenAPI spec:

```json
{
  "paths": {
    "/v1/score/{mint}": {
      "get": {
        "summary": "Token Risk Scoring",
        "x402": {
          "amount": "10000",
          "token": "USDC",
          "network": "base"
        }
      }
    }
  }
}
```

Free endpoints need `"security": []` to skip probing:

```json
{
  "/v1/health": {
    "get": {
      "summary": "Health check",
      "security": []
    }
  }
}
```

### 3. Contact Info in OpenAPI Spec

Add to `info`:

```json
{
  "info": {
    "contact": {
      "name": "Your Name",
      "email": "you@example.com",
      "url": "https://yourdomain.com"
    }
  }
}
```

## FastAPI Implementation Pattern

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

PAID_ENDPOINTS = {"/v1/data": 0.01}  # path -> price_usd

def check_payment(request: Request):
    return bool(request.headers.get("X-Payment"))

def pay_402(price_usd, resource):
    return JSONResponse(status_code=402, content={
        "error": "Payment Required",
        "x402Version": 1,
        "accepts": [{
            "scheme": "x402", "network": "base",
            "maxAmountRequired": str(int(price_usd * 1_000_000)),
            "resource": resource,
            "payTo": "0xYourAddress",
        }],
        "facilitator": "https://api.cdp.coinbase.com/platform/v2/x402",
    })

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    from fastapi.openapi.utils import get_openapi
    schema = get_openapi(title=app.title, version=app.version, description=app.description, routes=app.routes)
    for path, methods in schema["paths"].items():
        for method, details in methods.items():
            if path in PAID_ENDPOINTS:
                price = PAID_ENDPOINTS[path]
                details["x402"] = {"amount": str(int(price * 1_000_000)), "token": "USDC", "network": "base"}
            elif path in ["/v1/health", "/v1/apis"]:
                details["security"] = []
    app.openapi_schema = schema
    return app.openapi_schema

app.openapi = custom_openapi
```

## Common Pitfalls

- **FastAPI overrides custom OpenAPI:** FastAPI auto-generates `/openapi.json`. You MUST override `app.openapi` with a custom function to add x402 annotations. A separate `@app.get("/openapi.json")` endpoint won't work — FastAPI's built-in takes precedence.
- **Free endpoints get probed:** If you don't add `"security": []` to free endpoints, x402scan tries to pay for them and shows errors.
- **Contact info missing:** x402scan shows a warning if `info.contact` is missing from the OpenAPI spec.
- **v1 vs v2 format:** x402scan expects v1 format (payment in response body). Ampersend clients use v2 (PAYMENT-REQUIRED header). Our server uses v1 for x402scan compatibility; Ampersend still works because it falls back to body parsing.

## Verified

x402scan successfully discovered our API (gentechlabs.net) with 10 paid + 2 free endpoints using this pattern. Status: listed, awaiting first transaction.
