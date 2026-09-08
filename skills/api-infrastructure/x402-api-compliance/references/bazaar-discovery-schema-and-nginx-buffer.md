# Bazaar Discovery Schema + nginx Buffer — two fixes that made CDP validate pass (Aug 15, 2026)

Two independent bugs blocked `POST /platform/v2/x402/validate` from returning `valid: true`.
Both are reproducible and worth checking whenever a gateway "validates but isn't indexed."

## Fix 1 — GET resources must NOT declare `bodyType`/`body` in the Bazaar discovery schema

**Symptom:** `validate` → `valid: false`, `simulation.outcome: "rejected"`,
`rejectionReason: "invalid discovery configuration"`, failing check:
`(root).input.body: Invalid type. Expected: object, given: null`.

**Root cause:** the Bazaar discovery schema splits `info.input` by method family:
- **GET/HEAD/DELETE** (`QueryDiscoveryInfo`) — has **no `body` field**; uses
  `queryParams` / `pathParams` / `headers`.
- **POST/PUT/PATCH** (`BodyDiscoveryInfo`) — carries `bodyType` + `body`.

Declaring `bodyType: "json"` on a GET resource makes the validator look for `input.body`,
find it null, and reject the whole discovery config.

**Fix** — for a GET with a path param, use `pathParams`:
```python
"input": {
    "type": "http",
    "method": "GET",
    "pathParams": {"address": {"type": "string", "description": "Token or wallet address to score"}},
    "example": {"address": "0x1234..."}
}
```
And the `schema.input.properties` must only allow query-method fields:
```python
"properties": {
    "type": {"const": "http", "type": "string"},
    "method": {"enum": ["GET", "HEAD", "DELETE"], "type": "string"},
    "queryParams": {"type": "object", "additionalProperties": True},
    "pathParams": {"type": "object", "additionalProperties": True},
    "headers": {"type": "object", "additionalProperties": True}
},
"required": ["type", "method"]
```
NOT `bodyType`/`body` in the enum or required list.

**Diagnostic order:** read the failing check in the validate response — it names the exact
field. Match the method family to the correct input shape before touching anything else.

## Fix 2 — nginx `proxy_buffer_size` 502 on large 402 challenges

**Symptom:** after Fix 1, `validate` → `valid: false`, `simulation.outcome: "rejected"`,
`rejectionReason: "endpoint failed preflight checks"`. Direct `curl` to the public endpoint
returns **HTTP 502**, but the backend on `127.0.0.1:8090` returns the correct **402**.

**Root cause:** nginx's default `proxy_buffer_size` (4k) is too small for the 402 challenge's
`WWW-Authenticate` header (full base64 payment payload + bazaar extension). nginx logs
`upstream sent too big header while reading response header from upstream` and returns 502
instead of proxying the 402.

**Fix** — raise the proxy buffer on the gateway's nginx `location /` block:
```nginx
location / { proxy_pass http://127.0.0.1:8090; ... proxy_buffer_size 16k; proxy_buffers 4 16k; }
```
Then `nginx -t && systemctl reload nginx`. Verify the public endpoint now returns **402**.

**Diagnostic signal:** backend 402 + public 502 + nginx error `upstream sent too big header`
= proxy-buffer issue, not a gateway bug. Check nginx before touching gateway code.

## After both fixes
`POST /platform/v2/x402/validate` → `valid: true`, `simulation.outcome: "accepted"`.
`index: null` persisted even with a fully valid gateway — that's the separate CDP Bazaar
indexing gap (see the Aug 11 incident log in SKILL.md), not a config problem.
