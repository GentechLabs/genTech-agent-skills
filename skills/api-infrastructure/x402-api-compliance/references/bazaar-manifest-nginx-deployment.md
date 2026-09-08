# Bazaar Manifest + Nginx Static Serving

Production pattern for serving x402 Bazaar discovery manifests without requiring a live backend.

## Two Discovery Endpoints

The x402 ecosystem has two separate discovery endpoints — they serve different purposes:

| Endpoint | Purpose | Consumed By |
|----------|---------|-------------|
| `/.well-known/x402` | x402scan resource catalog (per-endpoint pricing, baseGateway config) | x402scan, Poncho, Agent Cash |
| `/.well-known/x402-bazaar` | Bazaar service manifest (services list, pricing tiers, supported chains) | Agentic Market, Coinbase Bazaar, x402 Bazaar crawlers |

**They are NOT interchangeable.** A marketplace may check one or both. Always serve both.

## Bazaar Manifest Format

File at `/var/www/gentechlabs/.well-known/x402-bazaar`:

```json
{
  "name": "GenTech Labs x402 Gateway",
  "description": "Pay-per-call API gateway with 15+ endpoints",
  "url": "https://api.gentechlabs.net",
  "version": "7.0.0",
  "x402_version": "2.0",
  "payment": {
    "protocol": "x402",
    "currency": "USDC",
    "network": ["base", "ethereum", "avalanche", "solana", "bnb", "arbitrum"],
    "price_range_usd": [0.001, 0.10]
  },
  "services": {
    "token_security": {
      "description": "Token risk scoring and rugcheck analysis",
      "endpoint": "/v1/security/score/{address}",
      "chains": ["base", "ethereum", "bnb"],
      "price_usd": 0.01
    }
  }
}
```

## Nginx Configuration Pattern

Every API-facing subdomain in nginx needs its own `location /.well-known/` block that serves static files. This must come **before** the catch-all `location /` proxy pass.

### Correct config:

```nginx
# API server — x402 endpoints
server {
    listen 443 ssl;
    server_name api.gentechlabs.net;

    ssl_certificate /etc/nginx/ssl/gentechlabs.crt;
    ssl_certificate_key /etc/nginx/ssl/gentechlabs.key;

    # .well-known served from disk — no backend needed for discovery
    location /.well-known/ {
        root /var/www/gentechlabs;
        default_type application/json;
        add_header Access-Control-Allow-Origin *;
    }

    # Everything else proxies to backend
    location / {
        proxy_pass http://127.0.0.1:8090;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Common mistake (WRONG):

```nginx
# ❌ No .well-known block — requests hit the backend
# If backend is down, ALL .well-known requests fail with 502/503
location / {
    proxy_pass http://127.0.0.1:8090;
}
```

### Why static files work:
- Discovery manifests rarely change (only when you add/remove services)
- They don't need business logic or auth
- Static files are faster and more reliable than proxying to a backend
- The backend can crash or be down for maintenance without breaking discovery

## File Naming

The Bazaar spec requires the filename **exactly** `x402-bazaar` (no extension):

```
/var/www/gentechlabs/.well-known/
├── x402-bazaar       # Bazaar manifest (no extension!)
├── x402.json         # Optional: legacy/alias
└── agent-card.json   # OKX AI marketplace card
```

If you previously named it `x402.json`, create a copy:
```bash
cp /var/www/gentechlabs/.well-known/x402.json /var/www/gentechlabs/.well-known/x402-bazaar
```

## Cloudflare WAF Consideration

Cloudflare WAF rules can block programmatic access to `.well-known/` paths. If external `curl` returns `error code: 1003` but local `curl localhost` works, the WAF is blocking.

**Fix via Cloudflare Dashboard:**
1. Security → WAF → Custom Rules
2. Create rule:
   - Field: `Hostname` → equals → `api.gentechlabs.net`
   - Field: `URI Path` → starts with → `/.well-known/`
   - Then: **"Skip"** (all remaining WAF features)
3. Deploy

Without this, marketplaces that crawl the manifest will see 403 and treat the service as unavailable.

## Pre-Deployment Verification

Before claiming a listing is live, verify from EXTERNAL (not localhost):

```bash
# Must work from any network, any user-agent
curl -s -o /dev/null -w "HTTP %{http_code}" https://api.gentechlabs.net/.well-known/x402-bazaar
# Expected: HTTP 200

curl -s -o /dev/null -w "HTTP %{http_code}" https://gentechlabs.net/.well-known/x402-bazaar
# Expected: HTTP 200

# Test with an agent-like user-agent
curl -s -o /dev/null -w "HTTP %{http_code}" -A "Grok/1.0" https://api.gentechlabs.net/.well-known/x402-bazaar
# Expected: HTTP 200
```

If localhost works but external returns 403/5xx, check:
1. Cloudflare WAF rules
2. Cloudflare SSL/TLS settings (Full vs Flexible)
3. Nginx error logs at `/var/log/nginx/error.log`

## x402 v2 Payment-Required Header

The `PAYMENT-REQUIRED` response header is required by the x402 v2 spec. Without it, bazaar discovery will reject the endpoint.

### Required format (from a FastAPI gateway):

```python
import base64, json
from fastapi import Response

def build_payment_required(service_name: str, price_usd: float) -> dict:
    return {
        "version": "2.0",
        "accepts": [{"scheme": "x402", "network": "base", "asset": "USDC"}],
        "price": {"amount": str(price_usd), "currency": "USD"},
        "payTo": os.getenv("X402_PAYTO_ADDRESS", ""),
        "maxTimeoutSeconds": 300,
        "description": f"Payment for {service_name}",
    }

def payment_required_response(service_name: str, price_usd: float) -> Response:
    payload = build_payment_required(service_name, price_usd)
    payload_b64 = base64.b64encode(json.dumps(payload).encode()).decode()
    return Response(
        status_code=402,
        content=json.dumps(payload),
        media_type="application/json",
        headers={
            "PAYMENT-REQUIRED": payload_b64,  # Base64-encoded per v2 spec
            "Access-Control-Allow-Origin": "*",
        },
    )
```

### Common pitfalls:
- **Body-only, no header:** Bazaar discovery will reject. Must have `PAYMENT-REQUIRED` header.
- **Wrong header name:** Use `PAYMENT-REQUIRED` (all caps underscored), not `X-PAYMENT`, not `Payment-Required`.
- **No base64 encoding:** The header value must be base64-encoded JSON, not raw JSON.
- **No CORS:** Add `Access-Control-Allow-Origin: *` on all 402 responses.
- **Auth middleware running before x402:** Returns 401/403 instead of 402. x402 middleware must run FIRST.
- **Static file permissions:** Files served by nginx must be readable by `www-data`. Root-owned files with `0600` permissions cause 403 Forbidden. Fix: `sudo chown -R www-data:www-data /var/www/...`.
- **Subdomain coverage:** Every API subdomain needs its own `location /.well-known/` block. Catch-all `location /` with proxy_pass is NOT sufficient — backend crashes break discovery.
- **Cloudflare grey-cloud shortcut:** For static subdomains, toggling orange cloud → grey cloud (DNS-only) bypasses all WAF rules in 5 seconds. Use for non-critical endpoints; use proper WAF skip rules for production API traffic.
