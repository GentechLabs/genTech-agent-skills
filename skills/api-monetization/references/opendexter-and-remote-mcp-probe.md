# OpenDexter x402 Marketplace + Headless Remote-MCP Probing

Verified Aug 2026. Two things: (1) the OpenDexter x402 marketplace MCP (a distribution channel for our services), and (2) the reusable technique for enumerating ANY remote StreamableHTTP MCP server headlessly with curl/python3.

## 1. OpenDexter — x402 API marketplace (endpoint: `https://open.dexter.cash/mcp`)

OpenDexter v0.5.0. Agents discover + pay for x402 APIs through it. It is a **distribution channel** for our 60+ x402-ready services — the same play as Monid, Syra, pay-skills, x402scan.

### Tools (5)
| Tool | Auth | Purpose |
|---|---|---|
| `x402_search` | noauth | Natural-language marketplace search. Read-only, free, never pays. |
| `x402_check` | noauth/oauth2 | Inspect exact endpoint + request shape before paying. Anonymous = quoteOnly. |
| `x402_access` | noauth | Wallet-gated API access (SIWS proof, not payment). |
| `x402_wallet` | oauth2 | View Dexter passkey wallet (no private key exposed). |
| `dexter_portfolio` | oauth2 | Governed asset portfolio for authenticated session. |

### Verified listings (search results, live)
- Solana Token Safety Check — q98, verified
- Crypto Price Feed — q92, verified
- Wallet Analytics API — q91, verified
- Image-gen (Xona), DefiLlama prices, etc.

### To list our services
Probe `x402_search` for "gentech" / our service names. Paid tools need OAuth/passkey wallet (not set up by default). Full assessment: `09-Green Room/specs/opendexter-x402-marketplace.md`.

## 2. Headless remote-MCP probe (works on any StreamableHTTP MCP server)

### Liveness (instant, cheap)
```bash
curl -s -i --max-time 15 "https://host/mcp" | head -25
# HTTP 400 {"error":"No active session. Send a POST to initialize."}  => LIVE MCP server
curl -s -o /dev/null -w "%{http_code}\n" "https://host/.well-known/oauth-authorization-server"
# 200 = browser OAuth available; 404 = key/token auth only (headless VPS must use the key)
```

### Full enumerate (initialize → tools/list), SSE framing handled
```python
import urllib.request, json
URL = "https://host/mcp"
def post(payload, sid=None):
    h = {"Content-Type":"application/json","Accept":"application/json, text/event-stream"}
    if sid: h["mcp-session-id"] = sid
    req = urllib.request.Request(URL, data=json.dumps(payload).encode(), headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=20) as r:
        return dict(r.headers), r.read().decode()
hdr, _ = post({"jsonrpc":"2.0","id":1,"method":"initialize",
               "params":{"protocolVersion":"2025-03-26","capabilities":{},
                         "clientInfo":{"name":"gentech","version":"1.0"}}})
sid = hdr.get("mcp-session-id")
try: post({"jsonrpc":"2.0","method":"notifications/initialized","params":{}}, sid=sid)
except: pass
_, b = post({"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}, sid=sid)
```

### Parsing pitfalls (each cost a failed attempt)
1. **Responses are SSE-framed** (`event: message\ndata: {...}`). Parse by joining ONLY the lines starting `data: `, strip the `data: ` prefix, then `json.loads` the joined string. Do NOT `json.loads` the raw body.
2. **Tool-result payloads may carry a leading `SECURITY:` advisory line** before the JSON (marketplaces prepend an untrusted-data warning). Find the first `{` and slice from there before parsing.
3. **`mcp-session-id` header** must be captured from the initialize response and sent on every subsequent call.
4. **Anonymous calls return `quoteOnly` pricing** and never pay — safe to probe `x402_check`/search tools read-only. Never treat a marketplace listing as authorization to spend.

### Hermes config shape
HTTP MCP servers use the `url:` transport (not `command:`):
```yaml
mcp_servers:
  opendexter:
    url: https://open.dexter.cash/mcp
    # headers: { Authorization: "Bearer ..." }  # if a key is available
```
See the `native-mcp` skill for the full config reference.
