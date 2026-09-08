# HTTPS for Constrained Devices — Cloudflare Tunnel Pattern

## Problem

Devices like Ray-Ban Meta smart glasses require HTTPS URLs. They won't load HTTP pages at all. Additionally, HTTPS pages cannot make API calls to HTTP backends (mixed content blocking).

## Solutions

### Option 1: Cloudflare Tunnel (Quickest)

No account needed for quick tunnels:

```bash
cloudflared tunnel --url http://localhost:8765
# Outputs: https://random-name.trycloudflare.com
```

**Systemd service for persistence:**
```ini
[Unit]
Description=Cloudflare Tunnel for Bridge
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/cloudflared tunnel --url http://localhost:8765
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Limitations:**
- Quick tunnels generate random URLs that change on restart
- No uptime guarantee (account-less)
- For permanent URLs, use named tunnels with a Cloudflare account

### Option 2: Serve from Same Origin

If the bridge server serves both the HTML and the API, use relative paths:

```javascript
// Auto-detect: same origin if served from bridge
const API_BASE = (location.port === '8765') ? '' : `http://${location.hostname}:8765`;
```

When `API_BASE` is empty string, fetch calls use relative URLs (same origin). No mixed content issue.

### Option 3: here.now UI + HTTPS Backend

Publish the UI on here.now (HTTPS), expose the backend via Cloudflare Tunnel (HTTPS). Update the HTML to point to the tunnel URL.

### Option 3: Cloudflare Workers with Headless OAuth

For headless/remote environments where `wrangler login` (browser-based OAuth) isn't possible:

**Step 1: Create temporary account**
```bash
wrangler deploy --temporary --name <worker-name> /path/to/worker.js
# Outputs: Claim URL (valid for 60 minutes)
```

**Step 2: User claims the account**
- Click the claim URL in a browser
- Authorize with your Cloudflare account
- Temporary account becomes linked to your real account

**Step 3: Deploy and configure routes**
Now you can:
```bash
wrangler deploy /path/to/worker.js
wrangler routes add <domain>/* --worker <worker-name>
```

**Pitfalls:**
- OAuth callback expects localhost - fails when user clicks from remote machine
- Rate limiting: After too many failed quick tunnel attempts, you'll get 429 errors
- Temporary accounts expire in 60 minutes - claim URL is time-sensitive
- Must have existing Cloudflare account to claim (no anonymous claiming)

**Use when:**
- No browser access on the deployment machine
- Need custom domain routing (unlike quick tunnels which use random URLs)
- Want persistent, branded URLs

### Option 4: Workers + Custom Domain Origin Routing

For API proxy scenarios where you need Workers to route to a backend:

**Worker code pattern:**
```javascript
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    if (url.hostname === 'api.example.com') {
      const originUrl = new URL(request.url);
      originUrl.hostname = '2.24.195.196'; // VPS IP
      originUrl.port = '80'; // Backend port
      
      const originRequest = new Request(originUrl, request);
      const response = await fetch(originRequest);
      
      // Add CORS headers
      const corsHeaders = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      };
      
      const newResponse = new Response(response.body, response);
      Object.entries(corsHeaders).forEach(([key, value]) => {
        newResponse.headers.set(key, value);
      });
      
      return newResponse;
    }
    
    return fetch(request);
  }
};
```

## Verification

```bash
# Test HTTPS access
curl -s https://your-tunnel.trycloudflare.com/api/health

# Test from device browser
# Open the URL in the device's browser

# Test Worker routing
curl -s https://api.example.com/v1/health
```

## Session Reference

**Vanito's Ray-Ban Integration (Jun 15, 2026):**
- HTTP URL `http://2.24.195.196:8765` was rejected by Ray-Ban Meta browser
- Cloudflare Tunnel provided instant HTTPS at `https://small-bunch-acceptance-acquisitions.trycloudflare.com`
- Bridge server running as systemd service `gentech-bridge` on port 8765
- Tunnel running as systemd service `gentech-tunnel`

**API Server + Worker Proxy (Jun 29, 2026):**
- API server on localhost:8080 couldn't be reached via Cloudflare Workers (522 timeout)
- Root cause: Worker had no origin configured - didn't know where to route requests
- Solution: Headless OAuth + custom domain routing
- Pattern: `wrangler deploy --temporary` → claim URL → configure routes → origin proxy
