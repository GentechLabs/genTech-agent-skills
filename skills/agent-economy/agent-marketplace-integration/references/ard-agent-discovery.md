# ARD (Agentic Resource Discovery) — get our x402 gateway discoverable by AI clients

**When to use:** getting a paid agentic resource (x402 gateway, MCP server, A2A agent, skill, API) discoverable by AI clients (Claude/ChatGPT/Copilot/Gemini) via the ARD standard. ARD is the *discovery* layer; x402 is the *payment* layer — complementary. Validated end-to-end 2026-08-26 (GenTech x402 gateway live at `/.well-known/ard.json`).

## What ARD is
- Open, federated discovery protocol for agentic resources. Backed by Cisco, Databricks, GitHub, Google, Hugging Face, Microsoft, Nvidia, Salesforce, ServiceNow, Snowflake.
- Repos: `ards-project/ard-spec` (canonical spec, ~435★, Apache-2.0, active), `ards-project/ard-connectors` (client-side connectors).
- Spec README explicitly welcomes PRs for: examples, conformance tooling, reference implementations, docs, typo/link fixes. Normative spec changes need an issue first.

## The 4-step contribution path (validated 2026-08-26)
1. **Build a validated ARD manifest** — `conformance/examples/<name>/ard.json`. Entry format:
   ```json
   {
     "specVersion": "1.0",
     "host": { "displayName": "...", "identifier": "did:web:<domain>", "documentationUrl": "..." },
     "entries": [{
       "identifier": "urn:air:<domain>:api:<name>",
       "displayName": "...",
       "type": "application/mcp-server-card+json",
       "url": "https://<domain>/.well-known/<manifest>",
       "description": "...",
       "tags": [...],
       "representativeQueries": ["..."],
       "capabilities": [...],
       "metadata": { "key": "scalar-only" },
       "trustManifest": { "identity": "did:web:<domain>", "identityType": "did", "attestations": [...] }
     }]
   }
   ```
2. **Validate with their conformance CLI** (zero-dependency, stdlib Python):
   ```bash
   python3 conformance/bin/conformance-test manifest <file-or-live-url>
   ```
   **Pitfall:** `metadata` only allows scalar values — arrays fail conformance. Use comma-joined strings, not arrays.
3. **Open a reference-publisher issue** — title `Reference publisher: <Name> — <description>`. Body: Publisher (org, domain, catalog URL, identity, docs) + Description + Why ARD + Conformance result. This is the established pattern (see issues #51, #14, #13, #11, #10).
4. **Open a conformance-example PR** — fork, add `conformance/examples/<name>/ard.json`, PR titled `feat(conformance): add <Name> as reference example`. Include the conformance PASS output + AI disclosure in the body.

## Deploying the live manifest
- Serve at `/.well-known/ard.json` (canonical well-known path). If nginx already serves `/.well-known/` from a static dir (e.g. `/var/www/gentechlabs`), just drop the file there — no config change needed.
- Verify live: `curl -s https://<domain>/.well-known/ard.json` → HTTP 200 + valid JSON, then re-run the conformance CLI against the **live URL** to prove prod compliance.
- Comment on the reference-publisher issue that the manifest is now live + passes conformance in production.

## Independent-publisher listing
Issue #67 tracks "how do independent (non-Azure, non-MCP) publishers get listed in GitHub Agent Finder's curated catalog?" — the seed-list path is still being defined. Comment on it with a concrete, validated case to stay in the thread.

## Tracking
The GitHub Contribution & Inbox Watch cron (`gh search prs --author @me`) auto-surfaces any open PR from our account — no separate tracking needed. Per Jordan's PR cadence rule, let clean+mergeable PRs sit (no nudging) unless they stall or Jordan flags them.
