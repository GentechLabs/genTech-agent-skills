# Robinhood MCP OAuth PKCE Flow

## Status (Jul 27, 2026)
**Not yet authenticated.** User needs to open an authorize URL in their browser.

## MCP Server Endpoint
`https://agent.robinhood.com/mcp/trading`

## Auth Requirements
- **Type:** OAuth 2.0 Authorization Code + PKCE
- **Bearer token** (JWT) must be sent as `Authorization: Bearer <token>` header
- Token endpoint: `https://api.robinhood.com/oauth2/token/`
- Authorization endpoint: `https://robinhood.com/oauth/authorize`
- Supported grant types: `authorization_code`, `refresh_token`
- Token endpoint auth method: `none` (PKCE handles client auth)
- Scopes: `internal`

## Registration
Client registration is at `https://agent.robinhood.com/oauth/trading/register`:
```json
POST /oauth/trading/register
{
  "redirect_uris": ["https://api.gentechlabs.net/robinhood-callback"],
  "client_name": "GTA Trading",
  "token_endpoint_auth_method": "none",
  "grant_types": ["authorization_code"],
  "response_types": ["code"],
  "scope": "internal"
}
```

Returns client_id: `LtLiNmbs9owbYfWgBlC68Z2VujIPuvGoAiSYr8xW`

## PKCE Flow

### Step 1: Generate verifier + challenge
```python
import secrets, hashlib, base64
verifier = secrets.token_urlsafe(64)[:128]
challenge = base64.urlsafe_b64encode(
    hashlib.sha256(verifier.encode()).digest()
).rstrip(b'=').decode()
```

### Step 2: Build authorization URL
```python
params = {
    'client_id': CLIENT_ID,
    'response_type': 'code',
    'scope': 'internal',
    'redirect_uri': REDIRECT_URI,
    'code_challenge': challenge,
    'code_challenge_method': 'S256',
}
url = f"https://robinhood.com/oauth/authorize?{urllib.parse.urlencode(params)}"
```

**IMPORTANT:** Use `/oauth/authorize`, NOT `/oauth`. The latter redirects to home page.

### Step 3: User opens URL in browser
User must be **already logged into Robinhood**. They'll see an authorize screen.

### Step 4: Exchange code for token
```python
data = urllib.parse.urlencode({
    'client_id': CLIENT_ID,
    'grant_type': 'authorization_code',
    'code': received_code,
    'redirect_uri': REDIRECT_URI,
    'code_verifier': verifier,
}).encode()
req = urllib.request.Request('https://api.robinhood.com/oauth2/token/',
    data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
```

### Step 5: Token response
```json
{
  "access_token": "eyJ...",
  "refresh_token": "...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

## Callback Server
The callback listener runs on port 8765 at `https://api.gentechlabs.net/robinhood-callback`.
Implemented as a route in the Hermes bridge server (`/root/hermes-bridge/server.py`).
Cloudflare tunnel routes `api.gentechlabs.net` → port 8765.

## Password Grant (Fallback)
The OAuth server also supports `grant_type=password` but it's deprecated:
```json
POST https://api.robinhood.com/oauth2/token/
{"grant_type":"password","client_id":"LtLiNmbs9owbYfWgBlC68Z2VujIPuvGoAiSYr8xW",
 "scope":"internal","username":"...","password":"..."}
```
Returns: `"This version of Robinhood is no longer supported"`.

## MCP Tool Discovery (after auth)
```
POST https://agent.robinhood.com/mcp/trading
Authorization: Bearer <token>
Content-Type: application/json

{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}
```

## Pitfalls
- Redirect URI must be pre-registered with POST to `/oauth/trading/register`
- Registration returns an existing client_id even without redirect_uris in the body
- The authorization server at `.well-known/oauth-protected-resource/mcp/trading` specifies `scopes_supported: ["internal"]`
- HTTP redirect (not HTTPS) to the callback may be blocked by browsers — always use HTTPS
- The MCP endpoint returns `authentication required` without a valid Bearer JWT
- Test auth with empty Bearer: `Authorization: Bearer` returns `JWT verification failed` (positive signal: JWT parsing is happening)
- Test auth with fake token: returns `JWT verification failed` (not "invalid" — means the server validates JWTs)
