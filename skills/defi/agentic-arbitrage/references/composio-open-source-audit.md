# Composio — Open-Source Reality Check (for GTA authorized-proxy layer, Aug 3, 2026)

Context: Jordan shared `ComposioHQ/composio` claiming "Composio made their main
skill open source." Initial assessment under-counted it (said "just skill docs").
This is the corrected, verified finding + the generalizable lesson.

## What IS open source
`ComposioHQ/composio` (29.5k★, **MIT**, active, `next` branch) — the full SDK:
- **Python SDK** (`python/`) and **TypeScript SDK** (`ts/`)
- Tool calling, `auth_configs`, `connected_accounts`, MCP support, `tool_router`,
  provider adapters (OpenAI/Anthropic/Gemini/CrewAI/LangChain/Google etc.)
- Verified locally: cloned `next`, MIT license, auth/connected-accounts/tool-router
  code all present.

## The nuance that decides the architecture
**The client SDK is fully self-hostable; the AUTH/EXECUTION BACKEND is not in the
open repo.**
- `python/composio/sdk.py` defaults to `environment="production"` (Composio's hosted
  API) and reads `COMPOSIO_BASE_URL` only if set.
- The repo has **no self-hostable server** — no docker-compose, no `backend/` dir,
  no local execution engine.
- So the SDK still routes OAuth-token storage + tool execution through Composio's
  cloud via `COMPOSIO_API_KEY`.

## Implication for GTA's authorized-proxy layer
- The open SDK is far more useful than "just skill docs" — we can build the GTA
  client on it.
- But if we want zero-third-party credential custody, we must **build the OAuth
  server side ourselves** (the hard part Composio solves), OR point the SDK at
  Composio's cloud.

## Generalizable lesson (the real takeaway)
**"Open-sourced a SDK" ≠ self-hostable backend.** When a vendor open-sources its
SDK, verify (a) the license, (b) whether the *server/backend* is in the repo, and
(c) what the SDK defaults to (cloud base URL vs self-host). Many "open source AI
agent platforms" open the client and keep the auth/execution server as SaaS — the
credential-custody + per-call cost decision is where the moat (and the lock-in)
lives. Clone and grep for `docker-compose`, `environment=`, `base_url`,
`COMPOSIO_*` before deciding build-vs-compose.

## Decision options for GTA's authorized-proxy layer (staged)
- **A (fast demo):** Composio free tier — link one account, agent acts on it.
  Cheap validation. Creds live in Composio cloud.
- **B (product/self-custody):** build OAuth ourselves (we already did Robinhood
  PKCE); credentials never touch a third party. More build, owns the trust moat.
- Coinbase CDP + Robinhood MCP are already direct rails — no Composio needed there.
