# OpenConnector Self-Host Spike — Build/Fork Decision Recipe

Deployed `oomol-lab/open-connector` (Apache-2.0, auth gateway, 1000+ SaaS providers to AI agents via SDK/CLI/MCP/HTTP/OpenAPI) as a live spike to ground the GTA "Composio cloud vs self-host" fork decision. Aug 23, 2026.

## Why spike instead of README-reading
The decision hinged on whether the full-custody self-host path (our "trust moat") was a from-scratch build or cheaply adoptable. Only a live boot proved it: **1,395 providers live, MCP surface up, a real action executed with real data.** Turns out the hard part (custody auth boundary, SSRF-guarded egress) is already built and shipped.

## Exact commands that worked

```bash
# 1. Pull the published image (docker-compose.yml references it)
docker pull ghcr.io/oomol-lab/open-connector:latest
# 2. Boot (background — foreground triggers the long-lived guard)
#    terminal(background=true), then poll readiness separately
docker compose up -d
# 3. Verify container healthy
docker ps --filter name=open-connector
```

## Probing the LIVE surface (the discipline)

```bash
# Health + docs + openapi all 200
curl -s -o /dev/null -w "root %{http_code}\n" http://localhost:3000/
curl -s -o /dev/null -w "docs %{http_code}\n" http://localhost:3000/docs
curl -s -o /dev/null -w "openapi %{http_code}\n" http://localhost:3000/openapi.json

# REAL endpoints — README sample 404s. Grep docs/runtime-api.md.
#  /v1/catalog -> 404 {error:not_found}
#  /v1/providers -> real catalog
curl -s http://localhost:3000/v1/providers | python3 -c \
  "import json,sys; d=json.load(sys.stdin)['data']; print('providers:',len(d)); print('auth types:', sorted({a for p in d for a in p.get('authTypes',[])}))"
# -> 1395 providers; auth types: api_key, custom_credential, no_auth, oauth2

# MCP surface (confirms agent-host plug-and-play)
curl -s http://localhost:3000/mcp/tools   # -> list_apps, search_actions, get_action_guide...
# note: POST /mcp, GET /mcp/tools (405 on bare /mcp)

# EXECUTE a real no-auth action end-to-end (arxiv = no_auth)
curl -s -X POST http://localhost:3000/v1/actions/arxiv.search_papers \
  -H "Content-Type: application/json" \
  -d '{"input":{"query":"agentic AI","maxResults":2}}'
# -> live arxiv data back (totalResults 128288). Execution proven, not a mock.
```

### Find no_auth providers for a quick real-execution test
```bash
curl -s http://localhost:3000/v1/providers | python3 -c "
import json,sys
d=json.load(sys.stdin)['data']
print([p['service'] for p in d if 'no_auth' in p.get('authTypes',[])][:15])
"   # arxiv, hackernews, crossref, europe_pmc, etc.
```

## Security posture to read (AGENTS.md / SECURITY.md) for custody claims
- SSRF-guarded egress: all provider egress via `context.fetcher`/`providerFetch`; validates URL + every redirect + DNS-resolved addresses; cloud-metadata/loopback blocked.
- Policy controls: connection identity, scopes, runtime tokens, action allow/block, redacted run logs.

## The honest adoption gate (decides the fork)
Self-hosted OAuth requires **registering OAuth client apps per provider** — a real setup cost the managed/hosted path (Composio cloud, OOMOL-hosted) absorbs by providing those apps. Middle path: OOMOL-hosted runtime (managed OAuth + credits) with a clean path back to private self-host — same provider/action contracts.

## Vault wiring done
- Spike note: `09-Green Room/specs/openconnector-spike.md`
- Decision entry: `11-Mess Hall/considerations.md` Composio fork → added OpenConnector as third option, marked self-host spike verified.
