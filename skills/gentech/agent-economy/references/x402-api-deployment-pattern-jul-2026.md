# x402 API Deployment Pattern — Agent Search API (July 4, 2026)

## Overview

Complete deployment transcript for the Agent Search API, establishing a repeatable pattern for deploying x402-enabled APIs on the GenTech infrastructure.

**API Details:**
- **Name:** Agent Search API
- **Domain:** `https://search.gentechlabs.net`
- **Port:** 8091 (local), proxied via nginx
- **Endpoints:** 5 (1 free, 4 paid)
- **Pricing:** $0.005-0.025 per call
- **Stack:** FastAPI + x402 + Exa + Grok/xAI + Surf AI
- **Tests:** 8/8 passing
- **Revenue Target:** $1,200-18,000/year

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Cloudflare DNS                           │
│              (search.gentechlabs.net)                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          │ HTTPS (Flexible SSL)
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      Nginx Reverse Proxy                    │
│                  /etc/nginx/sites-available/gentech          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          │ HTTP (localhost)
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              FastAPI Application (Port 8091)                 │
│           /root/agent-search-api/main.py                     │
└─────────────────────────────────────────────────────────────┘
```

## Nginx Configuration Pattern

**File:** `/etc/nginx/sites-available/gentech`

```nginx
# Agent Search API
server {
    listen 80;
    server_name search.gentechlabs.net;

    # Root endpoint - API info
    location = / {
        proxy_pass http://127.0.0.1:8091/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Status endpoint
    location = /status {
        proxy_pass http://127.0.0.1:8091/status;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Search endpoints
    location /search {
        proxy_pass http://127.0.0.1:8091;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60;
        proxy_connect_timeout 30;
    }

    # OpenAPI docs
    location /docs {
        proxy_pass http://127.0.0.1:8091/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # OpenAPI JSON
    location /openapi.json {
        proxy_pass http://127.0.0.1:8091/openapi.json;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Agent card for discovery
    location /.well-known/agent-card.json {
        alias /root/gentechlabs/search/.well-known/agent-card.json;
        add_header Access-Control-Allow-Origin *;
    }

    access_log /var/log/nginx/search.gentechlabs.net.access.log;
    error_log /var/log/nginx/search.gentechlabs.net.error.log;
}
```

## Systemd Service Pattern

**File:** `/etc/systemd/system/search-api.service`

```ini
[Unit]
Description=Agent Search API - FastAPI backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/agent-search-api
Environment="PATH=/root/.hermes/profiles/gentech/home/.local/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/local/lib/hermes-agent/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8091
Restart=always
RestartSec=10
StandardOutput=append:/var/log/search-api.log
StandardError=append:/var/log/search-api-error.log

[Install]
WantedBy=multi-user.target
```

## Agent Card Format

**File:** `/root/gentechlabs/search/.well-known/agent-card.json`

```json
{
  "agent": {
    "id": "gentech-agent-search",
    "name": "GenTech Agent Search API",
    "version": "1.0.0",
    "description": "Unified search service bundling Exa, Grok, and Surf with x402 payments",
    "capabilities": [
      "web-search",
      "ai-search",
      "aggregated-search",
      "payment-integration"
    ],
    "skills": [
      "web-intelligence",
      "search-aggregation",
      "api-development"
    ],
    "domains": [
      "web-search",
      "ai-agents",
      "payments"
    ],
    "endpoints": {
      "base": "https://search.gentechlabs.net",
      "api": {
        "status": "GET /status (free)",
        "aggregated": "POST /search ($0.025)",
        "exa": "POST /search/exa ($0.01)",
        "grok": "POST /search/grok ($0.01)",
        "surf": "POST /search/surf ($0.005)"
      }
    },
    "pricing": {
      "currency": "USD",
      "unit": "per-call",
      "tiers": [
        {"endpoint": "/search", "price": 0.025},
        {"endpoint": "/search/exa", "price": 0.01},
        {"endpoint": "/search/grok", "price": 0.01},
        {"endpoint": "/search/surf", "price": 0.005}
      ]
    },
    "payment": {
      "protocol": "x402",
      "network": "base",
      "currency": "USDC",
      "facilitator": "bazaar"
    },
    "contact": {
      "name": "GenTech Labs",
      "url": "https://gentechlabs.net"
    },
    "updated": "2026-07-04T13:00:00Z"
  }
}
```

## Deployment Steps

1. **Build the API** with x402 middleware
2. **Configure environment** with API keys
3. **Select port** (check availability with `netstat`)
4. **Start local server** and verify endpoints
5. **Configure nginx** (append to existing config, test with `nginx -t`)
6. **Reload nginx** with `systemctl reload nginx`
7. **Create systemd service** file
8. **Enable and start** service: `systemctl enable --now search-api`
9. **Create agent card** at `/.well-known/agent-card.json`
10. **Test all endpoints** (free + paid with/without payment)

## Pricing & Revenue

| Endpoint | Cost | Description |
|----------|------|-------------|
| GET /status | Free | API health check |
| POST /search | $0.025 | Aggregated search |
| POST /search/exa | $0.01 | Exa search |
| POST /search/grok | $0.01 | Grok search |
| POST /search/surf | $0.005 | Surf search |

**Revenue Target:** $1,200-18,000/year
- Break-even: ~4,800 calls/month at $0.025 avg
- Target: ~72,000 calls/month at $0.025 avg

## Pitfalls

1. **Port conflicts:** Always check with `netstat -tlnp | grep <port>` before starting
2. **SSL certificates:** Don't create local certs. Use Cloudflare Flexible SSL (HTTP proxy only)
3. **Nginx location:** Append to existing `/etc/nginx/sites-available/gentech`, don't create new file
4. **Agent card path:** Must be `/.well-known/agent-card.json` for auto-discovery
5. **Background processes:** Use `background=true` with `notify_on_complete=true` for bounded tasks
6. **Payment verification:** Set `PAYMENT_STUB_MODE=true` for development testing

## Verification Commands

```bash
# Check port availability
netstat -tlnp | grep 8091

# Test status endpoint (free)
curl -s https://search.gentechlabs.net/status | python -m json.tool

# Test agent card
curl -s https://search.gentechlabs.net/.well-known/agent-card.json | python -m json.tool

# Test paid endpoint (should return 402 without payment)
curl -s -X POST https://search.gentechlabs.net/search/exa \
  -H "Content-Type: application/json" \
  -d '{"query": "AI agents", "numResults": 5}' \
  -w "\nHTTP Status: %{http_code}\n"

# Check service status
sudo systemctl status search-api --no-pager

# View logs
tail -f /var/log/nginx/search.gentechlabs.net.error.log
```

## Version History

- **v1.0.0** (July 4, 2026): Initial deployment
  - 5 endpoints (1 free, 4 paid)
  - x402 payment integration
  - Multi-provider search (Exa, Grok, Surf)
  - Revenue target: $1,200-18,000/year