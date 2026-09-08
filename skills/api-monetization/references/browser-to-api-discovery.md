# Reverse-Engineer Undocumented Website APIs → OpenAPI → Paid API

**Source of the technique:** Shubham Saboo (Nous Research) X post, Aug 15 2026 —
"Hermes can turn any website into an API. Run the operation once in the browser.
Hermes watches the calls and creates a static API for your agent."

**What it actually is:** a two-skill pair from Browserbase's skills repo, installable
via the Hermes skills hub. It captures a browser session's network traffic and
auto-generates an OpenAPI 3.1 spec for the site's (often undocumented) XHR/fetch
surface. This is a **new sourcing path for our API-monetization play**: instead of
hand-wrapping a known API, we can discover + spec an undocumented one, then wrap it
as a billable x402 endpoint.

## The two skills

| Skill | Role |
|-------|------|
| `browser-trace` | CAPTURES traffic. Full DevTools-protocol trace of any browser session → `.o11y/<run>/cdp/network/{requests,responses}.jsonl` (+ optional request/response bodies). |
| `browser-to-api` | OFFLINE post-processing. Consumes a `browser-trace` capture, pairs CDP request/response events, templatizes observed URLs, infers JSON schemas from samples, emits **OpenAPI 3.1** (`openapi.yaml`) + a coverage report (`index.html`) + a `client.mjs`. |

Composition:
```
browser-trace   →  .o11y/<run>/cdp/network/{requests,responses}.jsonl
browser-to-api  →  .o11y/<run>/api-spec/index.html + openapi.yaml + client.mjs
```

## Install

```bash
hermes skills search "browser-to-api"     # shows both browse-sh and skills-sh sources
hermes skills install skills-sh/browserbase/skills/browser-to-api
hermes skills install skills-sh/browserbase/skills/browser-trace
```

`browser-to-api` requires Node 18+ and a `browser-trace` run directory. Its scripts
use only the Node standard library (no `npm install`). `jq` is referenced in docs for
ad-hoc querying but not required by the scripts. `allowed-tools: Bash, Read, Grep`.

## Workflow (from the skill)

1. **Capture** with `browser-trace` against a debuggable Chrome target (CDP port):
   ```bash
   TARGET=9222
   node ../browser-trace/scripts/start-capture.mjs "$TARGET" my-site
   browse open about:blank --cdp "$TARGET"
   browse network on          # capture request/response bodies
   browse open https://example.com
   # ...drive whatever flows you want covered...
   # Snapshot the bodies dir BEFORE turning capture off (temp dir is shared per-session):
   cp -r "$(browse network path | jq -r .path)" .o11y/my-site/cdp/network/bodies/
   browse network off
   node ../browser-trace/scripts/stop-capture.mjs my-site
   node ../browser-trace/scripts/bisect-cdp.mjs my-site
   ```
2. **Generate** the spec with `browser-to-api` (offline, no capture).

## Key facts / pitfalls

- `browser-to-api` **does not capture traffic** — it is purely offline post-processing
  on top of `browser-trace`'s `cdp/network/*.jsonl` buckets. If the user wants to
  capture, send them to `browser-trace` first.
- The generated spec is **best-effort** — coverage depends on which flows you drove
  during capture. The coverage report shows which flows would broaden the spec.
- `browser-trace` is the capture half; `browser-to-api` is the spec half. They compose.

## Why this matters for GenTech

- **New API-sourcing path:** discover + spec undocumented third-party APIs, then wrap
  them as paid x402 endpoints (Pattern 1: Single-Provider Wrapper in the umbrella
  SKILL.md). A scraper becomes a clean, spec'd, billable endpoint.
- **x402scan / pay-skills listing** needs a real OpenAPI spec — this generates one
  from traffic instead of hand-writing it.
- **Agent Search / aggregator play:** spec multiple undocumented sources, then
  aggregate them (Pattern 2).

## Related

- `browse-sh` source also lists `browser-trace` and `browser-to-api` (community trust).
- The `scrape-job-companies` browse-sh skill reverse-engineers Algolia XHR/fetch —
  same family of "discover the hidden API behind a site" work.
