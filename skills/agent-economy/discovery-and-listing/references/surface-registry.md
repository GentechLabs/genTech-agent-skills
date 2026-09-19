# Surface registry — every surface we track, its gate, and how to prove conformance

Rule: a surface without a recorded gate is a surface we will fail again. When a gate is discovered, it
lands here in the same session, with the exact probe that proves it.

## The gates we have hit, with the failure text

| Surface | Layer | Gate | Exact failure we saw | Proof command |
|---|---|---|---|---|
| **8004scan** (8004scan.io) | directory | registration file needs top-level `type` + `services[].endpoint` | `[WA001] Missing required field: type` · `[WA008] Service missing 'endpoint' URL field` ×10 · `services: null` | `curl -s https://api.8004scan.io/api/v1/agents/<chain>/<token>` |
| **8004scan** refresh | directory | owner-signed auth + 600 s cooldown, 5/day | `401 Authentication required` · `409 cooling down` | `POST /api/v1/agents/{chain}/{token}/metadata-refresh` with Bearer |
| **8004scan** endpoint store | directory | separate from the metadata parse | `400 Agent has no endpoints configured` even with 0 parse warnings | `POST /api/v1/agents/verify-endpoint/{chain}/{token}` |
| **CDP Bazaar** | facilitator | advertised `resource.url` must equal the route that challenges — no 307 | indexed nothing until the 307 was removed; their reply confirmed payer/payee gating was never the cause | `curl -sI <advertised resource>` → expect **402**, never 307 |
| **OKX A2MCP** | facilitator | single-network `accepts[]`, no unknown extension blocks | rejected multi-rail challenges 3× before the `/v1/okx/*` alias with `okx=True` | decode the PAYMENT-REQUIRED envelope on the okx alias |
| **x402-list.com** | directory | graded compliance + ownership proof at a well-known path | grade C capture when the EIP-712 `extra` block went missing for ~35 h | check `last 402 captured` + decode `extra` |
| **GitHub catalogs** (pay-skills etc.) | directory | the fork account must be visible to logged-out readers | PR 404s to logged-out and to crawlers while 200 authenticated → catalog has 0 hits for us | `curl -s https://github.com/<account>` (logged out) |
| **MCP directories** | protocol | a live `POST /mcp` answering `tools/list` | `api.gentechlabs.net/mcp` → 404 while our card claimed `metadata.mcp: true` | `curl -sX POST <host>/mcp -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'` |
| **ERC-8004 reputation** | identity | feedback written on-chain by a real client address | 0 feedbacks vs a leaderboard mean of 111 | `GET /api/v1/agents/{chain}/{token}` → `total_feedbacks` |

## What the leaders actually have (measured 2026-09-18, n=25 leaderboard vs n=200 random)

- declare protocols: **25/25 leaders** vs 59/200 crowd
- mean score: **92.99** leaders; crowd **9.76 with** protocols, **0.00 without**
- mean feedbacks: **111** leaders (max 700) vs **0.0** crowd
- `services` populated: **0/25** leaders · `is_verified`: **0/25** leaders

⇒ Two levers only: **declare protocols** and **earn feedback**. Neither `services` nor `is_verified`
appears on any leader, so chasing those buys no rank.

## Probing helpers

- A surface's **own parser output** is the best spec you will ever get. Find the endpoint that returns
  warnings/errors about your artifact and read it per-item.
- Refresh/ingest is usually **asynchronous**: accepted ≠ applied. Poll the artifact, not the submit
  response.
- Keep a **throwaway state file** when re-running local watchers/probes so a probe does not consume a
  cooldown or suppress a real alert.
- Prefer the **published OpenAPI spec** over prose docs when a platform has one — it gives exact request
  schemas and auth requirements.
