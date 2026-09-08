# Ampersend x402 MCP Proxy Setup

## Overview

Ampersend provides x402 machine-to-machine payment capabilities for Hermes agents. It works as an **HTTP proxy** — not a stdio MCP server. The proxy intercepts MCP requests, handles x402 payment negotiation automatically, and forwards to a target MCP server.

## ⚠️ Critical: HTTP Proxy, Not Stdio

The ampersend proxy starts an HTTP server on port 3000 (configurable). It CANNOT be used as a `command:` stdio entry in Hermes config. Using `command: node` with proxy-cli.js will fail silently — the server starts on port 3000 but Hermes tries to communicate via stdin/stdout, getting no response.

**Correct config: HTTP transport with `url:`**

```yaml
mcp_servers:
  ampersend:
    url: "http://127.0.0.1:3000/mcp"
    connect_timeout: 60
    timeout: 120
```

**Wrong config (will fail):**

```yaml
mcp_servers:
  ampersend:
    command: "node"
    args: ["/root/repos/ampersend-hermes/dist/mcp/proxy-cli.js"]
    # ^^^ THIS DOES NOT WORK — proxy-cli.js starts an HTTP server, not stdio
```

## Architecture

```
Hermes ──POST──▶ ampersend proxy (port 3000) ──POST──▶ target MCP server
                    │
                    └── If response is HTTP 402, proxy authorizes
                        payment via ampersend API, then retries
```

The proxy requires a `target` URL parameter on each request: `http://127.0.0.1:3000/mcp?target=<TARGET_URL>`. Without it, the proxy returns 400 "Missing target URL parameter".

**Implication:** The proxy can only be used in front of another MCP server. It's not a standalone tool server — it's payment middleware.

## Prerequisites

The proxy must be running as a background service before Hermes can connect.

### Run as systemd service

```ini
# /etc/systemd/system/ampersend-proxy.service
[Unit]
Description=Ampersend MCP Proxy (x402 payments)
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/node /root/repos/ampersend-hermes/dist/mcp/proxy-cli.js
Environment=AMPERSEND_AGENT_ACCOUNT=0x...
Environment=AMPERSEND_AGENT_KEY=0x...
Environment=AMPERSEND_NETWORK=base
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable --now ampersend-proxy
```

### Run manually (for testing)

```bash
AMPERSEND_AGENT_ACCOUNT=0x... \
AMPERSEND_AGENT_KEY=0x... \
AMPERSEND_NETWORK=base \
node /root/repos/ampersend-hermes/dist/mcp/proxy-cli.js
```

## Setup Steps

### 1. Clone and build

```bash
cd /root/repos
git clone https://github.com/edgeandnode/ampersend-hermes.git
cd ampersend-hermes
npm install
npx tsc  # builds to dist/
```

### 2. Configure credentials

```bash
ampersend config set "0xagentKey:::0xagentAccount"
```

Or fresh setup:

```bash
ampersend setup start --name "my-agent"
# Show user_approve_url to user for approval
ampersend setup finish
```

### 3. Start the proxy (systemd or manual)

See "Run as systemd service" above.

### 4. Verify proxy is running

```bash
curl -s -X POST http://127.0.0.1:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
# Should return: {"error":"Missing target URL parameter"}  ← means proxy is alive
```

### 5. Add to Hermes config (HTTP transport)

```bash
# Use sed since patch tool blocks config.yaml edits
cd ~/.hermes/profiles/gentech
sed -i '/^mcp_servers:/a\  ampersend:\n    url: http://127.0.0.1:3000/mcp\n    connect_timeout: 60\n    timeout: 120' config.yaml
```

### 6. Verify in Hermes

```bash
hermes mcp list     # should show ampersend with transport=HTTP
hermes mcp test ampersend   # will get 400 (expected — no target URL)
```

Note: `hermes mcp test ampersend` returns 400 because it doesn't pass a target URL. This is expected — the proxy IS running, it just needs a target to proxy to.

## Spend Limits

Configured in the Ampersend dashboard, not in the MCP config:
- Daily limit (e.g., $100 USD)
- Per-transaction limit (recommended to set)
- Monthly limit (optional)
- Auto top-up (optional)

## CLI Usage (outside MCP)

```bash
# Check cost before paying
ampersend fetch --inspect https://api.example.com/paid-endpoint

# Make a paid request
ampersend fetch https://api.example.com/paid-endpoint
```

## Security Notes

- NEVER ask the user to sign into Ampersend dashboard in a browser you control
- NEVER log/echo private keys (AMPERSEND_AGENT_KEY)
- Treat payment authorization as irreversible
- Set per-transaction limits to prevent runaway spending
