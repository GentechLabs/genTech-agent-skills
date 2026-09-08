# KeeperHub key testing — verify BEFORE wiring (Aug 2026)

When Jordan hands you a key for a KeeperHub-style execution layer, test it before
adding it to `.env` and restarting the gateway. The failure mode is subtle: a
**`wfb_` key authenticates (HTTP 200) but cannot open an MCP session**, so you can
waste a whole integration loop believing the rail works.

## Step 1 — definitive session test (the plugin's own client)

The canonical tell is the plugin client's session handshake raising:

```
RuntimeError: KeeperHub did not return mcp-session-id
```

Drive it directly (no gateway needed):

```python
import sys
sys.path.insert(0, "/root/.hermes/profiles/gentech/plugins/keeperhub")
from keeperhub_plugin.client import KeeperHubClient
try:
    c = KeeperHubClient("kh_...")
    c._ensure_session_unlocked()          # raises for wfb_ keys
    print("SESSION OK:", c.session_id)
except Exception as e:
    print("SESSION FAILED:", e)
```

A good `kh_` key returns a session id whose decoded payload carries
`"scope": "mcp:read mcp:write mcp:admin"`. A `wfb_` key returns HTTP 200 but **no**
`mcp-session-id` header (curl confirms: 200 with body `"authentication":{"required":true}`).

## Step 2 — REST scope probe (no session needed)

Same key against the REST surface tells you read vs write:

| Endpoint | `wfb_` (read-only) | `kh_` (org) |
|---|---|---|
| `GET /api/workflows` | 200 `[]` | 200 list |
| `GET /api/mcp/workflows` | 200 (public listings) | 200 (org) |
| `GET /api/keys` | 401 | 200 |
| `POST /api/workflows` | 405 | 200/201 |
| `GET /api/mcp/workflows/{slug}/call` POST | 503 (often "owner disabled") | depends |

## Step 3 — confirm real scope with a live MCP call

If Step 1 passed, call `list_workflows` over MCP and check it returns your org's
workflow rows (each with `organizationId`). Returning real rows = fully live.

## Takeaways

- **Do not trust HTTP 200 alone** — a `wfb_` key passes the transport but fails the
  session handshake. Check the session-id, then the JWT scope.
- **`kh_` = organisation key** (full scope, Settings → API Keys → Organisation).
  `wfb_` = webhook/user key — read-only, no MCP.
- **Probe cheaply with curl/httpx before any gateway restart.** The whole sequence
  above takes seconds and avoids the "wired a dead key, restarted, nothing loads" trap.
- Once live, prove the rail with a read-only `execute_protocol_action`
  (e.g. `aave-v3/get-user-account-data` on the wallet's own address) before any
  funds-moving tx — see the SKILL.md pitfall "Prove the rail before any real tx."
