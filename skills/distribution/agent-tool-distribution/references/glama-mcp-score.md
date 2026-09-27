# Glama MCP Server Quality Score — Mechanics & Fixes

> Verified Aug 4, 2026 against genTech-shop (scored 17%). Generalizes to ANY MCP server we publish on glama.ai/mcp/servers/<owner>/<repo>.

## Why a low Glama score is usually a stale-scan + missing-release problem, not bad code

Glama's overall score = **Tool Definition Quality (70%)** + **Server Coherence (30%)**. Both components **score zero until the server has a "release"**. That's why a well-maintained repo with a MIT license, README, glama.json, and recent commits still shows ~17% — the maintenance profile is fine, but TDQS + Coherence (the only two scored dimensions) are locked at zero behind the release gate.

## The score breakdown (what each item is really checking)

- **Release** — the GATE. No Glama release = TDQS (70%) + Coherence (30%) both zero. A "Glama release" ≠ a GitHub release. It's created on Glama's side.
- **License** — repo must have a LICENSE file GitHub recognizes. MIT is fine. Glama rescans periodically (hours), so a freshly-pushed license may show as "missing" until resync.
- **glama.json** — repo-root metadata: name, description, author, repository, categories, related servers, badges. Presence + accuracy improves discoverability.
- **Tool Definition Quality** — each tool scored 1–5 on SIX dimensions: Purpose Clarity (25%), Usage Guidelines (20%), Behavioral Transparency (20%), Parameter Semantics (15%), Conciseness & Structure (10%), Contextual Completeness (10%). Server-level = **60% mean + 40% minimum**, so ONE poorly-described tool drags the whole server down. This is the lever for pushing A-tier.
- **Server Coherence** — four equal dimensions: Disambiguation (can agents tell tools apart?), Naming Consistency, Tool Count Appropriateness, Completeness (gaps in tool surface).
- **Tiers:** A ≥3.5, B ≥3.0 (passing), C ≥2.0, D ≥1.0, F <1.0.

## Fix workflow (what a human must do on Glama's web console — agent cannot click these)

1. **Create a release**: go to `glama.ai/mcp/servers/<owner>/<repo>/admin/dockerfile` → configure the build spec → **Deploy** → once the build test passes → **Make Release** → enter a version → **publish**. Requires a Dockerfile OR a build spec configurable on that page (if no Dockerfile exists, configure the spec in the admin UI).
2. **Resync** so freshly-pushed license / glama.json / related-servers register: click **"Sync Server"** in the `.../admin` interface (also auto-syncs ~daily).
3. After rescan (~24h), if score still isn't A-tier, **audit tool descriptions against the TDQS rubric** (60% mean + 40% min means fix the weakest tool first). Check `server.py` tool docstrings/schemas for clear purpose, usage guidelines, parameter semantics.

## Dockerfile — the concrete release blocker (proven Aug 4, 2026)

A repo-root `Dockerfile` is what Glama's admin build spec needs to run the
"Deploy → Make Release" flow. Without it there's no build, no release, tools
stay unindexed, and the score is stuck. A known-good FastMCP Dockerfile:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py .
COPY plugin.json .
ENTRYPOINT ["python", "-m", "fastmcp", "run", "server.py:mcp"]
```

- **Default transport must be stdio** — it's what MCP clients and Glama's build
  test expect. Do NOT put an SSE/HTTP `CMD` as the default; it can make the
  build test hang. For remote/SSE, document an override (`docker run <img>
  --transport sse --port 8000 --host 0.0.0.0`), don't bake it in.
- FastMCP CLI syntax: `fastmcp run <file>:<object>` (the `:mcp` object ref is
  required). `--transport sse --port 8000 --host 0.0.0.0` are the override flags.

## Diagnostic signature: stale scan / no release (vs a real repo regression)

The Glama MCP API is authoritative, not the web page:
```bash
curl -s 'https://glama.ai/api/mcp/v1/servers/<owner>/<repo>'
```
- `tools: []` AND `spdxLicense: null` while `server.py` defines tools and MIT is
  committed+pushed → **stale scan and/or no release**, NOT a repo problem. Verify
  the repo is correct on `main` (`git ls-files | grep -iE "LICENSE|glama"`,
  `git log --oneline origin/main`), then the fix is Sync + Deploy + Release.
- If the score DROPPED and previously-green items flipped red (e.g. license,
  glama.json, author-verified), it's a re-scan catching the missing release —
  same fix chain, not a regression.

## Pitfalls / notes

- Glama's scan lags local git state. Before assuming a real deficiency, verify what's actually committed+pushed (`git log --oneline origin/main`, `git ls-files | grep -iE "LICENSE|glama"`) — Glama may simply be showing stale data.
- A GitHub repo with a LICENSE and a committed glama.json is usually *already fine*; the only true blocker is the missing release (unlocks ~85% of the score).
- Badges: `glama.ai/mcp/servers/<owner>/<repo>/badges/card.svg` and `.../score.svg` — embed in README for visibility.
- Score page URL pattern: `glama.ai/mcp/servers/<owner>/<repo>/score`.
- API to check server state directly: `curl -X GET 'https://glama.ai/api/mcp/v1/servers/<owner>/<repo>'`.

## The badge gate: directory bots require the badge line, and a resolving badge ≠ a listing
GitHub awesome-list CI bots for MCP servers check the entry for a Glama badge line and label missing ones within minutes of a PR opening — effectively every merged entry carries one, so push the badge line into the PR branch immediately rather than waiting for the listing to exist. But the badge SVG returns HTTP 200 with a "not listed" placeholder body until Glama actually indexes the server — a 200 status proves nothing; fetch the SVG body and confirm it isn't the placeholder.

Repo-side prep that lets Glama's crawler list the server: LICENSE (MIT), a repo-root Dockerfile (stdio default transport), and `glama.json` in the OFFICIAL schema — `{"$schema": "https://glama.ai/schemas/glama.json", "maintainers": ["<github-username>"]}`. Free-form metadata keys (name/description/author/categories) do NOT satisfy the schema and silently fail the crawl. Crawler detection also requires the repo name, description, or topics to contain "mcp" — add the `mcp` topic for robustness.
