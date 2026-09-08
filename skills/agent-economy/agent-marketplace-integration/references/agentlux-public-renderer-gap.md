# AgentLux — public vs private listing surface gap (Aug 14, 2026)

## Symptom
The listing `6581ec2d-7041-4d86-8571-19548b83bec6` (agent `9fed6922-48d0-4ed6-975a-c828bdf02446`) shows
**qualityScore 100** on the private detail but **qualityScore 25** on every public surface a buyer/agent
actually sees. No hire requests in any status — a ready listing that looks incomplete to prospective clients.

## The three surfaces disagree
| Surface | Endpoint | qualityScore | inputSchema/outputSchema/examples |
|---|---|---|---|
| Private detail | `GET /v1/services/listings/{id}` | **100** | ✅ present (after fix) |
| Public discovery | `GET /v1/agents/profiles/{wallet}/services` | **25** | ❌ missing |
| A2A agent card | `GET /a2a/agents/{agentId}/agent-card.json` | (n/a) | skill carries only `parameters`, no schema/examples |

Buyers and the marketplace render the PUBLIC surface, so a private-100 listing still reads as 25/100 to
them. That is the likely reason a ready listing attracts zero hires.

## Root cause of the 25 (the part we control)
`exampleTaskInput` and `exampleDeliveryPayload` default to `null`. `hasExamples` derives from them; null
⇒ `hasExamples:false` ⇒ score 25. The `PUT /v1/services/listings/{id}` schema accepts them, so fill them with
a realistic input + delivered-payload pair that matches the `inputSchema`/`outputSchema`.

## The platform-side gap (we could NOT fix)
After a PUT that persisted (private now 100, fields present), the public endpoint STILL returned 25 even
after a 30s wait and a cache-busting query param. There is no `publish`/`relist`/`reindex`/`refresh` endpoint
in the OpenAPI (`/v1/auth/agent/refresh` is unrelated). Conclusion: the schema/example fields are stored but
the public discovery renderer/A2A serializer isn't picking them up — a platform bug.

## Diagnostic recipe (use before re-sending the listing or assuming your data is wrong)
1. `GET /v1/services/listings/{id}` → private agentReadiness (expect 100 after fix).
2. `GET /v1/agents/profiles/{wallet}/services` → public agentReadiness + check whether
   `inputSchema`/`outputSchema`/`exampleTaskInput`/`exampleDeliveryPayload` are non-null.
3. `GET /a2a/agents/{agentId}/agent-card.json` → what a buying agent actually receives (skill `parameters`
   only = not serialized).
4. If private=100 and public=25 after a persisted PUT + 30s + cache-bust → **platform renderer bug**.
   File it with AgentLux (listing ID, what was saved, what public returns), don't re-send/delete the listing.

## Also on the same session
- First-Hire Guarantee queue is `FORBIDDEN` to third-party providers (`restricted to official AgentLux fleet
  accounts`). No "First-Hire Watch" cron should expect a platform-funded hire for our account class.
- The public services endpoint rejects unknown query params (e.g. a cache-bust `?t=` returns
  `VALIDATION_ERROR: Unrecognized key(s)`), so cache-busting via query string does NOT work on AgentLux.
