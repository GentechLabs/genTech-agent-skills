# GenTech API Safety Suite — Reference Implementation

**Script location:** `${PROFILE_DIR}/scripts/api-safety-suite/run_safety_suite.py`
**Golden files:** `${PROFILE_DIR}/scripts/api-safety-suite/golden/`

## What It Tests

The endpoint list is **derived at runtime from the gateway's own
`/.well-known/x402` manifest** — never hardcoded. One check per advertised
service, plus health, CORS preflight, and a manifest-fetch check.

| Test | Count | Verifies |
|------|-------|----------|
| Health endpoint | 1 | 200 + `status: ok` |
| CORS preflight | 1 | OPTIONS → `Access-Control-Allow-Origin: *` |
| Manifest fetch | 1 | `/.well-known/x402` is reachable and parses |
| Advertised services | 1 each | 402 + x402-v2 shape + `accepts[]` |

**Live count as of 2026-09-14: 12 checks (2 fixed + 10 advertised services),
12/12 passing.**

## Gateway Details

- **Base URL:** `https://api.gentechlabs.net/v1`
- **Discovery:** `https://api.gentechlabs.net/.well-known/x402` (this is the source of truth for services)
- **Version:** 9.4.x (manifest is version-scoped — do not pin paths in this doc)
- **Token:** USDC · rails advertised per service in `accepts[]`

## Cron Schedule

```
0 2,8,14,20 * * *  → api-safety-suite/run_safety_suite.py (no_agent, job 59283121321a)
```

## Adding an endpoint

**You don't.** Add the service to the gateway manifest and it is covered on the
next run. Only add a `PLACEHOLDERS` entry if the new endpoint template uses a
`{variable}` that isn't already mapped (e.g. a new id type).

## Pitfalls

- **NEVER hardcode gateway endpoint paths in a consumer.** The gateway's URL
  scheme is version-scoped and has changed at least twice (`/v1/games/search`
  → `/v1/deals/games/*` → `/v1/{service}/{path}`). A hardcoded list rots
  silently and turns a healthy product RED. Derive from `/.well-known/x402`.
  (Labs filed the same lesson the same day for the dsh plugin — it is a class
  defect, not two bugs.)
- **`git pull --rebase` refuses to run on a dirty tree.** Anything that pushes
  from a multi-writer repo must stash and pop around the rebase. See
  `push_with_retry()` in `scripts/git_repo_lock.py`.
- **Python's urllib needs a User-Agent header** — Cloudflare blocks default
  urllib requests. Always set `User-Agent: GenTech-SafetySuite/1.0`.
- **Do not double up `/v1/`** — `BASE_URL` already ends in `/v1`; strip a
  leading `/v1/` off any manifest endpoint before appending.
- **Unknown `/v1/{segment}` now returns 404, not 402**, by design (Sep 14
  Council): the gateway refuses to issue a payable challenge for a service it
  cannot deliver. A 404 on a path you expected to be paid means the *path is
  wrong*, not that the paywall is down.

## History

- **Jul 18, 2026** — Built and tested. 12/12 passing. Wired as context feed for x402 Compliance Scout.
- **Sep 14, 2026** — Hardcoded v7-era list (`/games/*`, `/movies/*`, `/intel/*`,
  `/airdrops/*`) had been permanently RED since the 04:07 gateway restart; 7 of
  12 checks were false alarms. Rewritten to derive every endpoint from the live
  manifest. 12/12 passing, verified by real run.
