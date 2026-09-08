---
name: agent-economy
description: "Agent economy infrastructure — ERC-8004 registration, x402 Bazaar listing, Agentscan research, revenue modeling, and Virtuals ACP integration. Covers Deal Tracker, DeFi Intelligence API, Agent Arena. For Zyfai SDK, see references/zyfai-sdk-integration.md. For platform research, see references/platform-research-jun-2026.md. For BAGS token launch, see references/bags-robinhood-token-launch.md. For $TREASURY token launch, see references/treasury-robinhood-token-launch.md."
tags: [blockchain, erc-8004, x402, agentscan, agent-economy, revenue, infrastructure]
---

# Agent Economy Infrastructure

Participating in the AI agent economy — registering agents on-chain, listing services on payment rails, researching the ecosystem, and modeling revenue.

## Three-Pillar Business Model (Jul 2026)

GenTech Labs has three distinct revenue streams, each targeting a different audience:

| Pillar | Audience | Payment Model | Product |
|--------|----------|---------------|---------|
| **Human Subscriptions** | People | $3/$10/$25 monthly | Game deals, movie tracking, DeFi dashboards on gentechlabs.net |
| **Agent APIs (x402)** | AI Agents | Pay-per-call ($0.001-$0.10) | 16 x402 endpoints — DeFi, search, security, gaming |
| **$TREASURY Ecosystem** | Everyone | Free to use — earn from swap fees | Agentic Treasury token on Robinhood Chain. 0.7% swap fee, 95% to creator |

**Key insight:** The token IS the subscription for the Treasury. No paywall, no barrier to entry. Volume drives fees, fees drive token value. Separate from the paid API services and human subscriptions.

**See:** `references/treasury-robinhood-token-launch.md` for full $TREASURY launch details.

### 0. Agent Arena (Built — `10-Labs/agent-arena/`)

DeFi automation platform with gamified competition. Agents take roles, join factions, and compete in strategy matches.

**Roles:** Boss (60% revenue), Executive (25%), Partner (15%)
**Factions:** Iron (grid trading), Surge (DCA accumulation), Nova (yield farming), Shadow (MEV extraction)
**Features:** Agent registration with role limits, match lifecycle (start/complete/fail), leaderboard, faction standings, persistent state
**Files:** `arena.py` + `test_arena.py` — 16/16 tests passing

**Usage pattern:**
```python
from arena import Arena, Role, Faction
arena = Arena()
arena.register_agent("a1", "GridMaster", Role.BOSS, Faction.IRON, "0xwallet")
match = arena.start_match("grid", Faction.IRON, ["a1"], 1000.0)
arena.complete_match(match.match_id, pnl=150, fees=25)
```

### 0a. Deal Tracker (Built — `10-Labs/deal-tracker/`)

Game price comparison engine — compares prices across 35+ stores using CheapShark API (free, no key).

**Features:** Game search, deal comparison, price history, wishlist monitoring with price drop alerts, DealAnalyzer (rank by value/price/rating/discount), Telegram-ready output
**Revenue:** Freemium SaaS + x402 micropayments per query
**Files:** `deal_tracker.py` + `test_deal_tracker.py` — 12/12 tests passing

**Key API gotcha:** CheapShark game deals endpoint is `deals?gameID={id}`, NOT `games/{id}/deals` (returns 500). See `references/cheapshark-api.md` in gentech-build-workflow.

### 0b. DeFi Intelligence API (Built — `10-Labs/defi-intelligence-api/`)

Paid DeFi data API wrapping DefiLlama via x402 micropayments.

**Endpoints:** Protocol TVL, protocols list, chain TVL, yield pools, token prices
**Revenue:** $0.001-0.002 per call on x402
**Files:** `api/server.py`, `api/payment.py`, `api/cache.py`, `api/defi_client.py` + tests — 19/19 passing
**Stack:** FastAPI + x402 middleware + TTL cache + DefiLlama (free, no key)

### 0c. Rugcheck v2 API (Built + Refactored — `/root/rugcheck/api/`)

Token risk scoring API with x402 micropayments. **Refactored to v2.1.0** (Jun 2026).

**Endpoints:** `/v1/health`, `/v1/score/{mint}`, `/v1/stats`
**Revenue:** $0.01 per query on x402
**Tests:** 31/31 passing
**Stack:** FastAPI + x402 middleware + TTL cache + simulation mode

**v2.1.0 Improvements:**
- Input validation (Solana mint regex, length checks)
- Structured logging for every request
- Proper error handling (try/except, HTTP error codes)
- Pydantic response models for type safety
- Uptime tracking in health endpoint

**Code quality lesson:** Jordan asked "how is the quality of the code?" — audit found 0 try/except blocks, minimal type hints, no tests. MVP-grade works for launch but needs hardening before charging money. Always do a code quality sprint before x402 Bazaar listing.

### 1. ERC-8004 Agent Registration

Register an AI agent as an on-chain NFT via the ERC-8004 Identity Registry.

**Contract:** `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` (CREATE2, same on all 22 chains)
**Reputation:** `0x8004BAa17C55a88189AE136b182e5fdA19dE9b63`

#### Two Registration Paths

**Path A — Agentscan Web UI (recommended for first registration):**
1. Go to https://agentscan.info/create
2. Connect wallet (MetaMask) — ensure correct network is selected
3. Fill form: Name, Description, Image URL (optional)
4. Add MCP services (Endpoint URL + Tools)
5. Select OASF skills via skill picker (see pitfall below)
6. Tap "Create Agent" → confirm in MetaMask (~$0.01 gas)
7. Wait for confirmation (2-5 seconds on L2s)

**Path B — Script (for programmatic/bulk registration):**
1. Prepare OASF metadata JSON (see `references/oASF-metadata-format.md`)
2. Host metadata on GitHub raw URL
3. Run `scripts/register.py --network <chain> --dry-run` to preview
4. User signs transaction (~$0.01 gas on Base/Avax)
5. Verify on Agentscan

**Key decisions:**
- **Chain selection:** Base = x402 hub (226 resources), BNB = largest agent count (140K), Avalanche = x402 Challenge ($100K prize), Ethereum = prestige
- **Metadata format:** OASF v1.0 — name, description, version, services array with skills/domains/pricing
- **Services:** MCP endpoints for each API (Rugcheck, Travel Hub, Content Engine)
- **Skills:** OASF taxonomy — 136 skills, 204 domains. Use search bar in skill picker, don't scroll.

**Proven Registration (Jun 21, 2026):**
- **Wallet:** `0x7ebff188f2Eba16518C02864589b1403a5d1296a` (Jordan's main wallet, 5213 txs on Avalanche)
- **Chain:** Avalanche C-Chain
- **Token ID:** #1770
- **Agent ID:** `c455a06e-0d72-4847-8175-ece7f7daa3e3`
- **Services:** 3 MCP endpoints (Rugcheck v2, Travel Hub, Content Engine)
- **Created:** June 21, 2026 @ 11:40 PM UTC
- **Verification:** `GET https://agentscan.info/api/agents?search=Gentech`

**Note:** Jordan has TWO wallets. The EVM address `0xebc8c71970EEb6973bd87F1FF146B3Ec4a5972f8` was funded with $11 USDC on Base, but the actual registration used `0x7ebff188f2Eba16518C02864589b1403a5d1296a` (nonce 5213 on Avalanche — his active trading wallet). Always verify which wallet the user is connecting in MetaMask.

**Pitfalls:**
- Metadata URL must be a raw GitHub URL (not blob view) — the on-chain URI points here
- Gas estimation can fail if RPC is slow — always test with `--preview` first
- Same contract address on all chains (CREATE2) — no deployment needed
- **Agentscan skill picker:** Use the search bar — type one keyword, check box, clear, repeat. Scrolling through 136 skills is painful on mobile.
- Skills are optional: You can register with just name + description + MCP services. Add skills/domains later.
- **Can edit after registration:** Agent metadata can be updated via `setTokenURI()` on-chain
- Code quality audit before selling: Jordan asked "how is the quality of the code?" — audit found 0 try/except blocks, minimal type hints, no tests in Rugcheck API. MVP-grade works for launch but needs hardening (error handling, input validation, logging, tests) before charging money. Schedule a code quality sprint before x402 Bazaar listing.
- **Base RPC rate limits:** `mainnet.base.org` blocks direct requests from VPS
- **Verification:** Check via Agentscan API: `GET /api/agents?search=<name>` or via on-chain event logs
- **AgentScan is read-only:** No API endpoint to update skills/domains on an existing profile. All updates must go through on-chain `setTokenURI()` — upload new OASF metadata to IPFS, then call the contract with your private key. AgentScan auto-syncs within 24 hours. The `/create` page is for NEW agents only.
- **Skills/domains in metadata:** OASF metadata has skills/domains at BOTH the top level (agent-wide) AND inside each service. AgentScan reads from the top-level fields. If skills are only inside services, AgentScan shows them as empty. Always include top-level `skills` and `domains` arrays in OASF metadata. See `references/oASF-top-level-skills-fix.md` for the pattern.
- **Zyfai dashboard is API-key-only:** The Zyfai dashboard at sdk.zyf.ai only manages API keys. Safe wallet deployment and ERC-8004 registration are done programmatically via the SDK (requires private key on user's machine, not server-side).
- **ERC-8004 contract might be UUPS proxy:** The Identity Registry contract is likely deployed as a UUPS (Universal Upgradeable Proxy Standard) proxy. This means `Write Contract` functions are hidden on block explorer UI (snowtrace.io shows "no public Write functions"). Use Tenderly (tenderly.co) which supports proxy contracts, or call the contract directly via a transaction library.
- **AgentScan URL format:** Use `/agent/{agent_id}` where `{agent_id}` is the UUID (e.g., `c455a06e-0d72-4847-8175-ece7f7daa3e3`), NOT `/agent/avalanche/{tokenId}`. The agent ID is the UUID field from the Agentscan API response.
- **Cloudflare Workers KV must exist:** `wrangler.toml` cannot use placeholder KV namespace IDs. Run `wrangler kv:namespace create "NONCE_STORE"` first, or comment out the KV binding if replay protection isn't critical (x402 verification code should gracefully handle missing KV via `env?.NONCE_STORE` checks).
- **Cloudflare Worker name must match CI:** If using Cloudflare GitHub Integration, the Worker `name` in `wrangler.toml` must match the CI system's expectation (e.g., `gentechlabs-api` not `gentechlabs`). A name mismatch causes the CI to auto-override the config but won't catch missing KV bindings.
- **Cloudflare Workers KV placeholder:** Never deploy with `id = "your-kv-namespace-id"` — it causes `code: 10042` error. Either create the KV namespace first (`wrangler kv:namespace create "NONCE_STORE"`) or disable the binding entirely with a comment. Graceful degradation pattern: if `env?.NONCE_STORE` is undefined, skip nonce replay protection — core x402 verification still works.
- **Cloudflare CI worker name mismatch:** GitHub Builds expects `gentechlabs-api` (from repo name), but `wrangler.toml` had `gentechlabs`. The CI auto-overrides but warns: "Worker name mismatch. Overriding using the CI provided Worker name." Match the CI name to avoid confusion.
- **setTokenURI vs setAgentURI:** `setTokenURI(tokenId, "ipfs://...")` updates the public metadata that AgentScan displays. `setAgentURI(tokenId, "...")` updates internal contract metadata (for custom storage implementations). For AgentScan updates, always use `setTokenURI()`.
- **AgentScan shows EMPTY skills/domains even when the metadata JSON is fully populated — check the metadata_uri resolves.** The metadata file can have 41 skills + 15 domains + 10 services, but if the on-chain `metadata_uri` points at a URL that 404s (e.g. a `ProtoJay4789.github.io` raw URL on a flagged/private account), AgentScan fetches it, gets 404, and renders the structured fields blank — while the description still shows. **Diagnostic:** `curl -s -o /dev/null -w "%{http_code}" <metadata_uri>` — if not 200, that's the cause, not missing data. **Fix:** host the metadata in a public `Gentech-Labs/<repo>` raw URL (e.g. `https://raw.githubusercontent.com/Gentech-Labs/programmable-money-x402/main/gentech-avax-metadata.json`), then update the on-chain URI to point there. Note: `ProtoJay4789.github.io` raw URLs 404 even when the GitHub API reports the repo public — the flagged-account web-404 quirk applies to raw.githubusercontent too, not just the repo page. Confirmed Aug 7, 2026.

### 2. Agentscan Ecosystem Research

Research the agent economy landscape using agentscan.info.

**Key pages:**
- `/ecosystems` — live metrics for Virtuals ACP, BNB Chain, x402
- `/networks` — 22 supported chains, agent counts, contract addresses
- `/create` — wallet connect + registration flow
- `/docs` — REST API (no key required), MCP server, ERC-8004 spec

**Metrics to track:**
- x402: transactions, volume, buyers/sellers, Bazaar resources
- Virtuals: AGDP, revenue, jobs, active wallets
- BNB: registered agents, unique owners, SDK activity

**Revenue modeling approach:**
- Use live ecosystem metrics as TAM
- Model conservative/realistic/aggressive scenarios
- Focus on x402 API sales as fastest path (see `references/revenue-model.md`)

### 2a. 8004scan.io — Second ERC-8004 Explorer (Discovered Aug 1, 2026)

8004scan.io is a second block explorer for the ERC-8004 registry (like
Agentscan). Key facts:

- **Auto-indexes the same registry** — reads the same Identity Registry
  contract (`0x8004...a432`), so ANY agent registered on any supported chain
  appears there automatically. **No separate registration needed.**
- **URL scheme:** `/agents?chain=<id>` filters by chain; `/agents/<chain>/<tokenId>`
  shows an agent detail page.
- **Chain 1776 = Injective EVM chain ID.** Injective is a small early chain in
  the registry (~931 agents vs 247K+ on BNB) — low-competition positioning play.
- **API (no key):** `GET https://8004scan.io/api/v1/agents?limit=50&offset=0`
  returns `{items: [...], total}`. Items carry `name`, `description`,
  `x402_supported`, `chain_id`, `total_score`, `total_feedbacks`,
  `owner_address`, `created_at`, `id`.
- **Our agent is indexed:** GenTech Labs #1770 (Avalanche) shows at
  `/agents/avalanche/1770` — verified live.
- **Scale (Aug 2026):** 384K+ agents, 522K+ feedback, 357K+ users, ~695K
  total registrations.

**New-agent monitoring (discovery pipeline):**
- Live cron: `8004scan-monitor.py` in profile scripts (daily 1 AM UTC →
  Labs channel), uses `/api/v1/agents`, dedups via `last_seen_id` watermark.
- **Raw output is ~60% noise:** Ave.ai Trading Agent duplicates (20+/night),
  `Agent #xxxxx` generics, `smoke-*` test agents, testnet chains (84532,
  11155111, 1187947933, 97, 5).
- **Triage rules (built into kit `a2a/discovery/discovery.py`):** drop
  testnet chains + known noise names + smoke/Agent-# prefixes; score leads:
  x402 (+3), real description (+2), Base chain 8453 (+1), reputation ≥10 (+2);
  sort desc.
- **The outreach gap lesson:** scanning without outreach = zero value. The
  monitor finds agents; the outreach layer (OKX A2A, x402 endpoint ping, or
  Buzz/Nostr DM once relay is live) is what converts a lead. Triage FIRST so
  you don't spam 40 agents/night.

### 2b. Agent Kit a2a Module — discover → talk → self-audit (Aug 1, 2026)

The kit now ships a full agent-to-agent communication module (commit `d223e7b`):

| Component | Path | What It Does |
|-----------|------|-------------|
| discovery/ | `a2a/discovery/discovery.py` | ERC-8004 registry monitor with built-in triage (env-configurable: `A2A_DISCOVERY_API_URL/STATE/LOG`) |
| workspace/ | `a2a/workspace/buzz_seed.py` | Buzz bridge — seed any Hermes profile as a native Buzz agent (idempotent, stdlib-only, `--profile`/`--relay`) |
| self-audit/ | `a2a/self-audit/` | Harness pattern: 4 roles + `constitution.md` (generic, not Hermes-specific) |
| identity/ | `a2a/identity/register.py` | ERC-8004 registration 7 chains + Pinata `upload-to-ipfs.sh` |

**Canonical kit repo:** `/root/repos/genTech-agent-kit` on `main` — this is the
one that matches GitHub. `/root/genTech-agent-kit` is a STALE copy on `master`
pointing at the same GitHub repo with a different token. Always verify with
`gh api repos/ProtoJay4789/genTech-agent-kit/git/trees/main?recursive=1` before
assuming a local copy is current. Two local copies of the same GitHub repo =
drift risk; fold missing files into the canonical one, don't maintain both.

**Pitfall — kit version claims vs shipped files:** v0.4.0's commit message and
README claim "self-evolution, Q402, wakeup-protocol, Obliteratus" but the repo
ships ZERO files for them (README/SKILL.md mentions only). Before referencing a
kit capability, `find . -iname '*<feature>*'` — a README line is not a shipped
component. The a2a module fixed this by shipping real scripts + docs per component.

**ARC hackathon packaging (Aug 1, 2026):** for Encode/Circle/Arc-style hackathons,
the submission repo is what judges see — consolidate the real working code into it
(not stub READMEs), add the buyer-side SDK + demo + playground, verify in the
consolidated location (free port, tests pass, SDK demo pays all endpoints), then
org-mirror the repo because `ProtoJay4789/` repos 404 on the web. Full worked
recipe: `references/arc-hackathon-submission-packaging.md`.

### 2c. Treasury Defender — Airdrop/Dust-Token Defense (Built Aug 2, 2026)

Paid x402 service (7th endpoint, port 8096, $0.01) that classifies any token
as KNOWN/UNKNOWN/SUSPICIOUS, quarantines flagged tokens, and returns safe
burn calldata. Born from the fake "RBTC.b" homoglyph airdrop that hit
Jordan's wallet.

**Core techniques (full recipe in `references/treasury-defender-scam-defense.md`):**
- **Homoglyph detection needs a confusables map** — NFKD normalization alone
  does NOT catch Cyrillic С/Ѕ (they survive NFKD as non-ASCII). Map
  `С→C, Ѕ→S, Ḍ→D, А→A, ...`, strip to ASCII letters, then compare.
- **eth_call string decode** — ABI-encoded `[offset][length][padded]`; skip
  the first 128 hex chars and use the length word, or you get `\x00` noise.
- **Never auto-sign burns** — return calldata for the owner to execute;
  signing a scam contract's transfer is how wallets get drained.
- **Port conflicts:** identify the squatter (`ss -tlnp` + check `/proc/<pid>/cwd`)
  before killing — the ARC gateway legitimately held 8095. Use a systemd
  drop-in `Environment=PORT=8096` instead of killing a live process.
- **x402 simulation proof format:** signature is a field INSIDE the JSON,
  HMAC over `amount:recipient:nonce:validAfter:validBefore`, keys are
  `chain`/`token` not `network`/`asset`, amount = `int(price * 1_000_000)`.
  Wrong format → "proof is not valid JSON"; wrong amount → 402 (verification
  working, not a bug).

**Registry cross-check rule:** before declaring a platform unlisted, grep the
build queue + vault git history for it — Bankr was already "shipped" (Jul 22
$TREASURY launch) and the registry row was never created.

### 3. x402 Bazaar Listing + Builder Codes

List APIs on the x402 Bazaar for agent-to-agent commerce. Use Builder Codes (ERC-8021) for on-chain attribution.

**Current server:** `gentechlabs.net` — v2.1.0, 13 APIs live (Deployed Jun 22, 2026)
- `gentechlabs.net` → AAE landing page (nginx static, Cloudflare-proxied, Flexible SSL)
- `api.gentechlabs.net` → x402 APIs v2.0 (FastAPI, port 8090)
- `rugcheck.gentechlabs.net` → Rugcheck API (port 8088)
- Files served from `/var/www/gentechlabs/` (NOT /root/ — nginx runs as www-data)

**Public website content policy (Jordan, Jun 2026):** The gentechlabs.net landing page is BUSINESS ONLY. No personal profiles, no DeFi dashboards, no gaming, no cookbook, no travel plans. The site represents the company, not the individual. Personal content stays on local hubs or private dashboard URLs. Only include: API suite, Agent Kit infrastructure, agent economy positioning, and code examples.

**Builder Code (ERC-8021):**
- Mint at base.dev → Settings → Builder Code
- Format: `^[a-z0-9_]{1,32}$` (e.g., `bc_gentech`)
- Set payout address to Jordan's wallet
- Python SDK doesn't have builder_code extension yet — manually add to response metadata
- The CDP facilitator handles CBOR encoding on settlement

**14 APIs (v2.1.1 — July 4, 2026):**

| # | Endpoint | Description | Price | Category |
|---|----------|-------------|-------|----------|
| 1 | `GET /v1/score/{mint}` | Token risk scoring — mint safety, holder distribution, LP status | $0.01 | blockchain |
| 2 | `GET /v1/defi/{protocol}` | DeFi protocol intelligence — TVL, yield, chain breakdown | $0.05 | finance |
| 3 | `GET /v1/travel/search` | Travel search — Google Maps places, restaurants, hotels | $0.01 | travel |
| 4 | `GET /v1/content/{platform}` | Content scraping — X, Reddit, YouTube, Instagram trends | $0.02 | media |
| 5 | `GET /v1/agent/search` | AI agent discovery — search by capability, chain, protocol | $0.005 | ai |
| 6 | `GET /v1/agent/{agent_id}` | Agent details — full profile, capabilities, reputation | $0.005 | ai |
| 7 | `GET /v1/identity/{address}` | ERC-8004 identity lookup — verify agent registration across chains | $0.001 | identity |
| 8 | `GET /v1/router/route` | Model router — route tasks to cheapest capable model (84.6% savings) | $0.001 | ai |
| 9 | `GET /v1/wallet/deploy` | Smart wallet deploy — Safe wallet via Zyfai SDK with yield optimization | $0.01 | finance |
| 10 | `GET /v1/yield/opportunities` | Yield opportunities via Zyfai SDK — top DeFi yields across protocols | $0.001 | finance |
| 11 | `GET /status` | Agent Search API health check (free) | Free | search |
| 12 | `POST /search` | Aggregated search across Exa, Grok, and Surf AI providers | $0.025 | search |
| 13 | `POST /search/exa` | Exa AI-powered semantic search | $0.01 | search |
| 14 | `POST /search/grok` | xAI Grok real-time web search | $0.01 | search |
| 15 | `POST /search/surf` | Surf AI web intelligence | $0.005 | search |

**Agent Search API (NEW — July 4, 2026):**
- Location: `/root/agent-search-api/`
- Domain: `https://search.gentechlabs.net`
- Port: 8091 (proxied via nginx)
- Stack: FastAPI + x402 + Exa + Grok/xAI + Surf AI
- Tests: 8/8 passing
- Pricing: $0.005-0.025 per call based on provider
- Revenue target: $1,200-18,000/year

**Pricing tiers (from ecosystem data):**
- Tier 1: $0.001 — simple data lookups
- Tier 2: $0.005 — search, analysis
- Tier 3: $0.01-0.03 — complex queries, risk scoring

**Agentic.Market (Coinbase) auto-indexing:** Services appear on Agentic.Market when the CDP Facilitator **settles** a payment (not on 402 alone). No manual registration. Our gateway returns correct x402 v2 format. **See:** `references/agentic-market-cdp-facilitator.md` for full indexing flow, protocol notes, and next steps.

**CDP Bazaar self-settlement (WORKING, Aug 4, 2026):** To get listed on the CDP Bazaar you must **SETTLE** a payment through the CDP facilitator — verify alone is not enough. Three gateway fixes are required: (1) `extract_proof` must read the `PAYMENT-SIGNATURE` header (CDP SDK v2 sends it there, base64 JSON), (2) `verify_proof_via_cdp` must base64-decode the proof, (3) add a `/settle` call after `/verify`. CDP auth is a **JWT** (EdDSA for base64 Ed25519 keys, ES256 for PEM EC) with a `uris` claim — NOT the old HMAC scheme (401). **The JWT is PATH-BOUND: mint a fresh one for `/verify` AND a separate one for `/settle`, or settle 401s and the money never moves.** The `paymentRequirements` field must be the accepted payment option object directly (with `scheme` top-level), not wrapped in `accepts`. A JWT-signed call returning 400 (not 401) confirms auth is correct. Confirm settlement on-chain by USDC balance delta (~0.02), not the gateway's 200. Full worked recipe, self-settle script, the `@dexterai/x402` vs `@coinbase/cdp-sdk` dependency-conflict workaround, the backend-routing trap (don't self-settle a Solana-only service with an EVM address), and the wallet-funding reality: **`references/cdp-bazaar-self-settlement.md`**.

**Listing requirements:**
- x402 payment endpoint configured
- OASF metadata with pricing info
- Active health endpoint
- Builder Code in response metadata for attribution
- **402 response when payment missing** — x402scan.com detects APIs by checking for proper 402 status codes. Endpoints that return 200 without payment won't be discovered. See `references/x402scan-compatibility.md` for the fix pattern.

**Jordan's directive (Jun 2026):** "Once we fix this compatibility, let's add it to the agent kit as well so that x402 is just covered." — x402 compliance (402 responses + OpenAPI spec with x402 annotations) should be **default behavior** in the Agent Kit. Every new API gets it from day one, not as an afterthought.

**x402scan.com discovery (proven Jun 2026):**
- Block explorer for x402 payments — 8.58M transactions, $1.11M volume, 119K buyers
- Auto-detects APIs that return proper 402 responses
- OpenAPI spec with `x402` annotations speeds up discovery
- Our APIs detected: "GenTech Labs — Agent-to-Agent Economy Infrastructure" with 12 endpoints
- **Key fix:** Payment check function must return HTTP 402 (not 200) when `X-PAYMENT` header is missing/invalid

### 3b. Hive MCP Marketplace (Configured Jun 2026)

AI agent freelance marketplace — browse tasks, submit proposals, deliver work, earn crypto.

**MCP Server:** `@luxenlabs/hive-mcp-server` v1.1.0 — configured in hermes.yaml
**API Key:** `hive_sk_fc58...` (configured)
**Website:** https://uphive.xyz
**Status:** Live, marketplace active but low task volume

**Tools available:**
| Tool | What It Does |
|------|-------------|
| `hive_list_tasks` | Browse open tasks |
| `hive_get_task` | Get task details |
| `hive_propose` | Submit proposals |
| `hive_deliver` | Submit completed work |
| `hive_agent_profile` | Check agent stats |

**Key difference from x402 Bazaar:**
- x402 Bazaar = sell our APIs (we're the seller)
- Hive = do other people's tasks (we're the worker)
- Both are revenue channels — Bazaar is passive, Hive is active

**Integration with our stack:** Our 13 APIs can fulfill Hive tasks (risk scoring, DeFi intel, content scraping). When a task matches one of our endpoints, we can propose to solve it automatically.

### 4. Virtuals ACP Integration

Integrate with Virtuals Agent Commerce Protocol for the largest prize ($481M AGDP, 45K+ agents, 1.48M jobs, $2.27M revenue).

**Status:** Registering now (Jul 22, 2026). Go to app.virtuals.io/acp/new, connect wallet, create agent identity. Then list x402 gateway as ACP offering.

**Integration points:**
- Risk scoring service for Virtuals agents
- Compliance layer (KYC/AML signals)
- Data access APIs
- $TREASURY listing in their capital markets layer

**Registration:** app.virtuals.io/acp/new — wallet connect required (Jordan action).

### 5. Wallet Funding Strategy

Multi-chain operations require funded wallets. Gas on L2s is pennies and lasts months.

**Minimum viable funding:**
| Chain | Amount | Lasts | Why |
|-------|--------|-------|-----|
| Base (ETH) | $2-5 | 6-12 months | ERC-8004 registration, x402 payments |
| Solana (SOL) | $5-10 | Years | Staking, boot camp, x402 |
| BNB (BNB) | $3-5 | Years | Largest agent ecosystem |
| Avalanche (AVAX) | $5-10 | Years | x402 Challenge ($100K prize) |

**Total: $15-30 to be active across all chains.**

**Monitoring:** Use `scripts/wallet-balance-check.py` (under `scripts/`) — checks ETH/SOL balances, alerts on low thresholds. Can be cron'd for daily checks.

**Pitfalls:**
- Same EVM address works on Base, BNB, Avalanche, Arbitrum, Polygon (just switch network in MetaMask)
- Solana uses a different address format (base58)
- Users often ask "do I need to keep funding?" — answer: no, L2 gas is fractions of a penny per tx

### 6. Zyfai SDK Integration (Analyzed Jun 2026)

**SDK:** `@zyfai/sdk` v0.2.37 — TypeScript SDK for yield optimization, Smart Wallets, and ERC-8004 registration on Base/Arbitrum/Plasma.

**What Zyfai gives us:**
| Feature | Zyfai | Us | Integration |
|---------|-------|-----|-------------|
| ERC-8004 | Base + Arbitrum native | Avalanche only | Cross-chain identity — register on all 3 |
| Smart Wallets | Safe (ERC-4337) deployment | None yet | Use their SDK for agent wallets |
| Yield Optimization | Automated rebalancing across protocols | Manual LP farming (LFJ) | Use their engine for AVAX/USDC positions |
| Session Keys | Built-in delegated execution | Agent Kit enforcement | Delegated trading without key exposure |
| Vault API | Shared pool deposits (USDC on Base) | Compound vs Extract (spec only) | Could use their vault layer |

**Integration path:**
1. Get API key from https://sdk.zyf.ai/ (free)
2. Register agent on Base + Arbitrum via `registerAgentOnIdentityRegistry()`
3. Deploy Safe wallet for yield optimization
4. Use Vault API for shared pool deposits

**Key methods:**
```typescript
// ERC-8004 registration
sdk.registerAgentOnIdentityRegistry("0xSmartWallet", 8453); // Base
sdk.registerAgentOnIdentityRegistry("0xSmartWallet", 42161); // Arbitrum

// Smart Wallet deployment
sdk.deploySafe(userAddress, 8453, "conservative"); // or "aggressive"

// Vault API
sdk.vaultDeposit("100", "USDC"); // Deposit to shared pool
sdk.vaultWithdraw(); // Withdraw from vault

// Session Keys (delegated execution)
sdk.createSessionKey(userAddress, 8453);
```

**Strategic positioning:** We own identity + payment + discovery layer. Zyfai is the DeFi execution layer. They optimize yield, we handle the agent economy. Distribution = discovery = revenue — every chain we're on is another surface area for agents to find us.

**Status:** SDK installed, API key configured, Smart Wallet address ready (`0x0F03566A33d1fF24C16E7a8D96db610D8773C67A` on Base). Yield data live on API. Pending: user must deploy Safe via Zyfai dashboard (requires wallet signature).

### 7. Chainlink CRE + x402 Integration (Discovered Jul 22, 2026)

**Chainlink Runtime Environment (CRE)** uses x402 as its first AI payments partner — announced at SmartCon, live on mainnet.

**What this means for us:**
- Chainlink CRE workflows can be triggered and paid for via x402
- AI agents can discover, trigger, and pay for CRE workflows autonomously
- Our x402 gateway is already compatible — we can offer CRE-triggerable services

**Key links:**
- Announcement: https://www.coinbase.com/developer-platform/discover/launches/chainlink-cre-x402
- Hackathon project (top 12): https://chain.link/hackathon/winners/x402-chainlink
- Demo repo: https://github.com/startup-dreamer/x402-chainlink
- Chainlink demo: https://github.com/smartcontractkit/cre_x402_smartcon_demo

**Chainlink Community Grant Program:**
- Funds open-source development of oracle integrations, developer tooling, and data feeds
- Apply at https://chain.link/community/grants
- Our angle: Build x402 + Chainlink oracle integrations (price feeds, compliance data, agent reputation)

**Strategic positioning:** Chainlink is the oracle standard. x402 is the payment standard. We sit at the intersection — our APIs provide data that Chainlink oracles can verify and x402 can pay for. This is a natural grant application target.

### 7c. Singularity Agent Pods — Treasury Integration (Discovered Jul 22, 2026)

**Singularity** (x402_Layer) launched Agent Pods — one-click, fully managed AI agents with built-in wallets, x402 commerce, and dedicated private compute.

**First deployment:** ClawPod on OpenClaw
**Free tier:** 24-hour free deployment (limited time)

**Integration points:**
- **$TREASURY as pre-installed module** — every Agent Pod ships with autonomous capital management
- **x402-Layer ClawHub Skill** (1 star, 2 contributors) — bridges OpenClaw agents to x402 payments. Supports Base, Ethereum, Polygon, BSC, Monad, Solana. Has ERC-8004 agent registration, marketplace discovery, webhooks, endpoint deployment.
- **Singularity SDK** (0 stars, 1 contributor) — receipt and webhook verification library for x402 payments. Node.js + Python, MIT licensed.

**Solo builder connection:** Ivaavi.eth (ivaavimusic) built both repos solo. Reach out as fellow builder — offer to contribute, maintain, list our gateway on their marketplace.

**See:** `references/singularity-agent-pods-integration.md`

### 7d. OpenClaw Distribution — 384k Stars (Discovered Jul 22, 2026)

**OpenClaw** (384k ⭐, 80.6k forks) — personal AI assistant framework. Runs everywhere, very active (commits every few minutes).

**The play:** Build a GenTech OpenClaw skill that gives 384k+ users access to our x402 gateway. Includes:
1. Payment integration — discover and pay for our 16 endpoints
2. Marketplace listing — list their own endpoints on our gateway
3. Self-improvement loop — port Hermes' learning loop to OpenClaw

**Also:** List our gateway on the x402-Layer ClawHub marketplace (1 star, 2 contributors — easy PR).

**See:** `references/openclaw-genTech-skill.md`

### 7e. Cursor Directory Listing (Discovered Jul 22, 2026)

**Cursor Directory** (cursor.directory) — plugin marketplace for Cursor AI editor. OOBE Protocol's SAP MCP just listed there.

**Submission:** cursor.directory/plugins/new — sign in with GitHub, fill plugin details (name, description, MCP server URL). Jordan action (needs auth).

**Our listing:** GenTech x402 Gateway as an installable MCP server for Cursor agents.

$100K USD + 500K ALGO prize pool. **Now live** — announced July 21, 2026. Ten finalists present at Devcon 8 in India.

**Register:** https://algorand.co/global-x402-challenge
**Blog:** https://algorand.co/blog/the-x402-global-challenge-is-live-how-to-build-submit-your-entry
**Facilitator:** GoPlausible (https://facilitator.goplausible.xyz/)
**Leaderboard:** https://facilitator.goplausible.xyz/dashboard
**Why us:** We already have production x402 infrastructure (16 endpoints, multi-facilitator example). Most teams are building from scratch.

**Three entry types:**
| Type | What | Best for us |
|------|------|-------------|
| **Standard** | One endpoint, one price | Single API entry |
| **Composite** | Multiple endpoints, same payTo, grouped on leaderboard | **Our 16 x402 endpoints** — all under one payTo |
| **Orchestrator** | Your agent calls other endpoints, pays on behalf of users | Our Agentic Treasury as a meta-service |

**Our play:** Enter as **Composite Entry** — all 16 x402 gateway endpoints grouped under one payTo address. Every call to any endpoint counts toward our leaderboard total.

**Requirements:**
- Algorand MainNet (not Testnet)
- GoPlausible facilitator (not local/other)
- Bazaar discovery extension enabled
- Tag: `x402-global-challenge` in resource server config
- Real Mainnet payment settled through GoPlausible
- Same payTo address for entire competition

**Timeline:**
- Submission opens: September 2026
- Leaderboard window: October 2026 (unannounced window)
- Finalists: Devcon 8 in India

**Action items:**
- [ ] Register on Algorand x402 Challenge page
- [ ] Study Algorand x402 integration docs (GoPlausible facilitator)
- [ ] Adapt our multi-facilitator example for Algorand AVM
- [ ] Deploy endpoint on Algorand MainNet with GoPlausible
- [ ] Add `x402-global-challenge` tag to resource server config
- [ ] Make one real Mainnet payment to verify end-to-end
- [ ] Run gateway through Latch402 (Agent 5577) for compliance check
- [ ] Run open-source checkers (suryast/x402-check, onescales/x402checker) as backup
- [ ] Drive volume to climb leaderboard before October window

**See:** `references/latch402-verification.md` for endpoint verification tools and workflow.

### 10. Networking & Grant Applications

**Framing directive (Jordan, July 4, 2026):** Frame GenTech as "ecosystem support / grants / dev adoption / remote builder opportunities," NOT as "startup fundraising." This is how ecosystem partners understand us.

**What this means:**
- Don't pitch as "we're raising money" or "startup needs funding"
- Pitch as "we've built infrastructure, looking for ecosystem support to expand"
- Focus on what we contribute: public goods, tools, other teams can plug into
- Mention we're bootstrapped, revenue-positive — no VC required

**One-pager pattern for networking/grant applications:**

Create a concise one-pager (`00-HQ/gentech-one-pager.md`) with these sections:

```markdown
# GenTech Labs — Agent Economy Infrastructure

## 🎯 What We Build
[One-line value proposition]

## 🚀 What's Live
[Table of services with endpoints + pricing]

## 🏔️ Avalanche Integration
[ERC-8004 token info, on-chain capabilities]

## 💡 Why This Matters
[Market context, problem statement, our solution]

## 🎯 Current Focus
[Ecosystem contribution, not fundraising + specific goals]

## 📊 Traction
[Metrics: endpoints, domains, Bazaar status, deployment stack, portfolio website]

## 🎨 Portfolio Website
[Portfolio URL, featured projects, tech stack]

## 👨‍💻 About
[Bio, philosophy, location, contact]

## 🔗 Resources
[Live infrastructure, portfolio website, GitHub, etc.]
```

**Key elements to include:**
- Token #1770 on Avalanche C-Chain (proves we shipped)
- 48 live endpoints (shows scale)
- Bazaar indexed (shows we're in the ecosystem)
- Portfolio website: protojay4789.github.io (shows we build)
- "No VC funding required" (shows we're serious, not desperate)
- "Ecosystem contribution" framing (appeals to grants)

**Sending the one-pager:**
- Forward as file from vault: `gentech-one-pager.md`
- Or share GitHub link: `https://github.com/ProtoJay4789/gentech-vault/blob/main/00-HQ/gentech-one-pager.md`

**Conversation style with ecosystem partners:**
- Concise, direct — they respect "builder grind" brevity
- Voice notes are fine and often preferred on Telegram
- End with a question to keep conversation going
- Be ready to act fast once they open doors

**Template response for networking:**
```
Thanks, [Name] — really appreciate the direction. You're right, framing this as ecosystem support makes way more sense.

Here's a quick one-pager on what we're building:
[gentech-one-pager.md or GitHub link]

The tl;dr:
- 48 x402 endpoints live (pay-per-call API infrastructure)
- ERC-8004 agent identity on Avalanche (Token #1770)
- All endpoints accepting CDP payments via Bazaar
- Portfolio website live: protojay4789.github.io
- No fundraising — focused on grants, hackathons, and dev adoption

The infrastructure is ready for other teams to plug into. Would love your take on which direction makes the most sense from an [ecosystem] perspective.
```

**See:** `00-HQ/gentech-one-pager.md` for the actual one-pager template

**SPC Founder Fellowship (Fall 2026):** $1M ($400K/7% SAFE + $600K guaranteed next
round). Deadline Aug 2, 11:59pm PT. **The live Airtable form is SHORTER than any
drafted version — only 12 fields** (journey stage, About You incl. phone/LinkedIn/
location/how-heard, proudest achievement <1000 chars, 2-3 artifacts, stay-in-touch).
Draft Q's on team/funding/problem-space are NOT on the form — keep as "Anything
else to add?" candidates. **Lesson: always `browser_navigate` the actual
`airtable.com/embed/...` form to read live fields — `web_extract` of the apply page
only returns the embed shell.** See `references/spc-founder-fellowship.md` for the
verified field list, terms, and Jordan's strong draft answers.

---

## Revenue Model Summary

| Stream | Year 1 | Year 2 | Year 3 |
|--------|--------|--------|--------|
| x402 API Sales | $18K | $54K | $135K |
| Agent Kit Licensing | $8.4K | $33.6K | $84K |
| Virtuals Integration | $57.7K | $288.6K | $577.2K |
| Compound/Extract | $10.3K | $206K | $2.06M |
| **Total** | **$94.4K** | **$582.2K** | **$2.86M** |

Full model: `references/revenue-model.md`

### 8b. Cloudflare Workers Deployment Pattern

Deploy x402 APIs via Cloudflare Workers with GitHub Integration for auto-deploy on push.

**GitHub Integration Setup (Cloudflare Dashboard):**

1. Navigate to Cloudflare Dashboard → Workers & Pages → Overview
2. Click "Connect to Git" → select `ProtoJay4789.github.io`
3. Configure project:
   - **Project name:** `gentechlabs-api` (matches CI expectations)
   - **Production branch:** `main`
   - **Framework preset:** None (for Classic Workers)
   - **Root directory:** `/` (or `/worker` if structured)
4. **Environment variables (optional):** Add `PAYOUT_ADDRESS`, `CLOUDFLARE_API_TOKEN`
5. **Build command:** `npm install` (or `npm run build`)
6. **Deploy command:** `npx wrangler deploy`

**wrangler.toml Configuration (Classic Worker):**

```toml
name = "gentechlabs-api"  # Must match Cloudflare CI name
compatibility_date = "2024-01-01"
account_id = "a618b777aff85c5360bd847629385b4d"
main = "src/worker.ts"

[vars]
ENVIRONMENT = "production"

# KV namespace (optional — can be disabled)
[[kv_namespaces]]
binding = "NONCE_STORE"
id = "your-kv-namespace-id"  # TODO: Create via wrangler kv:namespace create "NONCE_STORE"

[[routes]]
pattern = "https://gentechlabs.net/api/*"
zone_name = "gentechlabs.net"

[[routes]]
pattern = "https://gentechlabs.net/v1/*"
zone_name = "gentechlabs.net"
```

**Deploy workflow:**

1. **Local dev:** `npx wrangler dev --local` (runs on port 8787)
2. **TypeScript:** `npx tsc --noEmit` (catch errors before deploy)
3. **Create KV namespace (if needed):** `npx wrangler kv:namespace create "NONCE_STORE"` → copy ID into `wrangler.toml`
4. **Push to GitHub:** GitHub Integration triggers auto-deploy
5. **Verify:** Check `https://gentechlabs.net/v1/health`

**Graceful degradation pattern for KV:**

```typescript
// In worker.ts
if (env?.NONCE_STORE) {
  await env.NONCE_STORE.put(proof.nonce, JSON.stringify({...}), { expirationTtl: 86400 });
}
// Core x402 verification still works without KV — just skips replay protection
```

**Pitfalls:**
- KV placeholder `your-kv-namespace-id` causes deploy error (`code: 10042`). Either create the namespace or comment out the binding.
- Worker name mismatch: If `wrangler.toml` says `gentechlabs` but CI expects `gentechlabs-api`, CI auto-overrides but warns. Match the names.
- TypeScript errors block deploy: Always run `npx tsc --noEmit` before pushing.

**See:** `references/cloudflare-workers-x402.md` for full deployment transcript.

### 8d. x402 API Deployment Pattern (July 4, 2026)

Standard workflow for deploying x402-enabled APIs on the GenTech infrastructure.

**Prerequisites:**
- FastAPI application with x402 middleware
- Nginx reverse proxy configured
- Cloudflare Flexible SSL (no local cert management needed)
- Systemd service for process management

**Deployment Steps:**

1. **Build the API:**
   - Create FastAPI application with payment endpoints
   - Add x402 token verification middleware
   - Implement 402 Payment-Required responses
   - Write comprehensive tests (pytest)

2. **Configure Environment:**
   - Create `.env` with API keys (Exa, Grok, Surf, Bazaar)
   - Set `PAYMENT_STUB_MODE=true` for development
   - Set `PAYMENT_VERIFICATION_ENABLED=false` in dev mode

3. **Port Selection:**
   - Use ports in 8088-8099 range for APIs
   - Check port availability: `netstat -tlnp | grep <port>`
   - Kill conflicts: `lsof -ti:<port> | xargs kill -TERM`

4. **Nginx Configuration:**
   - Add server block to `/etc/nginx/sites-available/gentech`
   - Configure proxy_pass to local port
   - Set proper headers (Host, X-Real-IP, X-Forwarded-For)
   - Add timeout settings (proxy_read_timeout 60)
   - Test config: `nginx -t`
   - Reload: `systemctl reload nginx`

5. **Systemd Service:**
   - Create service file at `/etc/systemd/system/<api-name>.service`
   - Set `ExecStart` to uvicorn with correct port
   - Configure `Restart=always` for auto-restart
   - Set logging paths for stdout/stderr
   - Enable and start: `systemctl enable --now <api-name>`

6. **Auto-Discovery Setup:**
   - Create agent card at `/.well-known/agent-card.json`
   - Include endpoints, pricing, and capabilities
   - Add nginx location block with proper headers
   - Verify: `curl https://<domain>/.well-known/agent-card.json`

7. **Testing & Verification:**
   - Test status endpoint (should be free)
   - Test paid endpoints with x402 token
   - Verify 402 response without payment
   - Check logs: `tail -f /var/log/nginx/<domain>.error.log`

**Agent Card Format:**
```json
{
  "agent": {
    "id": "gentech-<api-name>",
    "name": "GenTech Labs — <API Name>",
    "version": "1.0.0",
    "description": "<One-line description>",
    "capabilities": [...],
    "skills": [...],
    "domains": [...],
    "endpoints": {
      "base": "https://<domain>",
      "api": {
        "<endpoint>": "<method> <path> ($<price>)"
      }
    },
    "pricing": {
      "currency": "USD",
      "unit": "per-call",
      "tiers": [...]
    },
    "payment": {
      "protocol": "x402",
      "network": "base",
      "currency": "USDC",
      "facilitator": "bazaar"
    },
    "contact": {
      "name": "GenTech Labs",
      "url": "https://gentechlabs.net"
    }
  }
}
```

**Nginx Pattern:**
```nginx
server {
    listen 80;
    server_name <domain>.gentechlabs.net;

    # Root endpoint
    location = / {
        proxy_pass http://127.0.0.1:<port>/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Status endpoint (free)
    location = /status {
        proxy_pass http://127.0.0.1:<port>/status;
        # ... headers
    }

    # Paid endpoints
    location /<path> {
        proxy_pass http://127.0.0.1:<port>;
        # ... headers + timeouts
    }

    # Agent card for discovery
    location /.well-known/agent-card.json {
        alias /root/gentechlabs/<api>/.well-known/agent-card.json;
        add_header Access-Control-Allow-Origin *;
    }

    access_log /var/log/nginx/<domain>.access.log;
    error_log /var/log/nginx/<domain>.error.log;
}
```

**Pitfalls:**
- **SSL certificates:** Don't create local certs. Use Cloudflare Flexible SSL — proxy over HTTP only.
- **Port conflicts:** Always check port availability with `netstat` before starting service.
- **API keys in .env:** Never commit .env. Use `.env.example` as template, keep actual keys secret.
- **Payment stub mode:** Always test with `PAYMENT_STUB_MODE=true` before enabling real payments.
- **Nginx reload:** Must reload nginx after config changes, not just restart service.
- **Agent card path:** Must be `/.well-known/agent-card.json` for auto-discovery registries to find it.
- **Background processes:** Use `background=true` with `notify_on_complete=true` for bounded tasks (tests, builds). Use without notify for long-lived servers (APIs).

**Example: Agent Search API Deployment:**
- Location: `/root/agent-search-api/`
- Port: 8091
- Domain: `search.gentechlabs.net`
- Tests: 8/8 passing
- Revenue: $0.005-0.025 per call

**See:** `references/x402-api-deployment-pattern-jul-2026.md` for full Agent Search API deployment transcript.

### 8c. Bankr Integration (June 2026)

**Platform:** Bankr — AI agent infrastructure for self-sustaining agents
**Website:** https://bankr.bot
**Docs:** https://docs.bankr.bot

**What Bankr offers:**
- **x402 Cloud** — Deploy paid API endpoints with x402 payments built in. Zero x402 knowledge required.
- **Token Launchpad** — Fair launch tokens, 57% trading fees to agent wallet
- **Agent API** — REST API with API key auth
- **Claude Plugins** — bankr-agent, bankr-agent-dev, bankr-x402-sdk-dev
- **LLM Gateway** — OpenAI-compatible proxy with usage tracking
- **$100K Inference Program** — Free inference credits for builders (apply: forms.gle/Pb7bWZGfynbHMw)

**Integration strategy:** Don't compete — integrate. We're the data layer, they're the payment layer.

**Our role:** APIs that Bankr agents call. Their x402 SDK charges $0.01/request. We provide:
- Rugcheck v2 (token risk scoring)
- DeFi Intelligence (protocol data)
- Token Security (11-factor scoring)
- Crypto Price, Gas Price, Deal Tracker

**Revenue path:**
- Bankr agents call our APIs → x402 micropayments → recurring revenue
- Bankr token launches → 57% trading fees → additional revenue
- $100K Inference Program → fund our compute costs

**Chain support:** Base, ETH, Polygon, Unichain, World Chain, Arbitrum, BNB, Solana, Hyperliquid

**SDK:** `@bankr/sdk` v0.1.0-alpha.8 (npm, MIT, 49.8KB)
**CLI:** `@bankr/cli` — `bankr login`, `bankr launch`, `bankr fees`

**Status:** SDK available, $100K program application pending. Add to build queue for deployment.

**CLI deployment flow (proven Jul 22, 2026):**
```bash
bun add -g @bankr/cli
bankr login  # paste API key from bankr.bot/settings
bankr x402 init
bankr x402 add <service-name>  # interactive: method, path, price
# Edit x402/<service-name>/index.ts with your handler logic
bankr x402 deploy  # deploys to https://x402.bankr.bot/<wallet>/<service-name>
```

**Pitfalls:**
- The `x402/` directory must be in the current working directory — `bankr x402 init` creates it in CWD, and all subsequent `x402` subcommands look for it there
- `bankr x402 add` is interactive (prompts for method, path, price, npm packages) — the `--ni` (not-interactive) flag does NOT suppress the interactive wizard for this subcommand. To bypass, write the config file directly at `x402/bankr.x402.json` with the service definition, then run `bankr x402 deploy`
- The scaffolded handler is a TypeScript `Request → Response` function — edit `x402/<service-name>/index.ts` before deploying
- Deployed URL format: `https://x402.bankr.bot/<wallet-address>/<service-name>`
- `bankr x402 deploy` with `BANKR_NOT_INTERACTIVE=1` works for non-interactive deployment
- The `bankr.x402.json` config file at the root level (`/root/bankr.x402.json`) is NOT the same as the one in the `x402/` directory — the CLI only reads from `x402/bankr.x402.json`

### 8c. Competitive Strategy: Integrate, Don't Compete

**Key directive (Jordan, June 24, 2026):** "We're not even going to fight them. We're just going to integrate. That's pretty much our job — make other people connect to us so they can touch our APIs and services and see us. We can have multiple giants."

**Competitor landscape:**
| Competitor | What They Do | Our Counter |
|-----------|--------------|-------------|
| Quack AI | Q402 payment protocol (7 chains) | We provide data APIs they don't have |
| Bankr | Token launchpad + agent infra | We integrate, not compete |
| Helixa | Agent credibility scanner | We have deeper risk scoring (Rugcheck v2) |

**Our moat:** 13 live APIs, Rugcheck v2 (11 factors), DeFi Intelligence, open-source AgentKit

**Integration playbook:**
1. Deploy on Bankr x402 Cloud → get discovered by their agents
2. List on pay-skills catalog → get discovered by x402 ecosystem
3. Register on Virtuals ACP → get discovered by $481M AGDP market
4. Complete AgentScan profile → get discovered by on-chain agents

### 9a. Agent Payment Stack (Built — June 24, 2026)

Three products shipped that form the payment layer of the agent economy:

**Receipt Generator** (`10-Labs/receipt-generator/`)
- HTML receipt template with GenTech dark theme branding
- Receipt dataclass, generate_receipt(), render_to_html(), save_receipt()
- 13/13 tests passing, no external deps (stdlib only)
- Revenue: Free (value-add for x402 ecosystem)

**Rugcheck Payment Classifier** (`10-Labs/rugcheck-payment-classifier/`)
- Classifies incoming transactions: PAYMENT, AIRDROP, SCAM, DUST, UNKNOWN, TRANSFER
- Pattern matching: known senders, known tokens, amount thresholds, scam keywords
- 13/13 tests passing, simulation mode for demos
- Revenue: $0.005/classify

**Agent-to-Agent Invoicing** (`10-Labs/agent-invoicing/`)
- Professional invoice generation with line items, payment links, overdue detection
- Invoice dataclass with create_invoice(), render_to_html(), mark_paid(), generate_payment_link()
- 18/18 tests passing, dark theme branding
- Revenue: Free (value-add for agent commerce)

**Stack architecture:**
```
Payment Event → Receipt Generator → HTML/PNG → Telegram Delivery
Incoming TX → Payment Classifier → PAYMENT/SCAM/DUST → Decision
Agent Service → Invoicing → Invoice → x402 Payment Link → Receipt
```

**Landing page updated:** gentechlabs.net now shows 13 services, 16 endpoints.

### 9b. A2A Agent Card Discovery (June 24, 2026) ✅ LIVE

Hosted at `/.well-known/agent-card.json` on gentechlabs.net for auto-discovery by A2A registries.

**Format:** A2A Agent Card spec with 15 skills declared
**File:** `/var/www/gentechlabs/.well-known/agent-card.json`
**Nginx requirement:** Explicit `location /.well-known/` block + `chmod 644` + `chown www-data:www-data`

**Auto-discovered by:**
- a2a-registry.org (scans well-known URI automatically)
- a2aregistry.org (validates agent card, indexes in registry)
- agenstry.com (indexes from well-known OR submission)

### 9g. Open Gateway API Server Setup (July 1, 2026) ✅ LIVE

Unified API gateway for Gentech agent economy with x402 payment integration.

**Architecture:**
- **Framework:** FastAPI + Uvicorn (Python 3.11)
- **Models:** GLM-4.5-flash, GLM-4.7, GLM-5.2, Claude-3.5-sonnet
- **Authentication:** Bearer token (`3eyVMQ-Ng6CiWV3128WiJhm8Z4VGmqYlj2WoOoidvCM`)
- **Payment:** x402 micropayment simulation with cost tracking
- **Port:** 8089 (shifted from 8088 due to conflicts)

**Endpoints:**
- `GET /v1/health` — Health check with version and status
- `GET /v1/models` — Available models with pricing
- `POST /v1/chat/completions` — Chat completions with payment verification
- `POST /v1/embeddings` — Embeddings generation
- `GET /v1/tools` — Available tools for agents
- `GET /v1/stats` — Request statistics and usage tracking

**Startup Process:**
1. Kill existing processes on port 8088/8089: `lsof -ti:8088,8089 | xargs kill -TERM`
2. Verify port is free: `netstat -tlnp | grep 8089`
3. Start server: `python3 -m uvicorn open_gateway:app --host 0.0.0.0 --port 8089`
4. Test endpoints: `curl -s http://localhost:8089/v1/health` (requires token)

**Key Implementation Notes:**
- Session token stored in environment variable for authentication
- Cost calculation per model and operation (input/output tokens)
- Simulation mode for development (full functionality without real payments)
- Proper error handling with HTTP status codes
- Usage statistics tracking for monitoring

**Pitfall Resolution:**
- Port conflicts require `kill -TERM` + verify with `netstat`
- Use different port (8089) when 8088 is occupied by legacy server
- Bearer token required for all protected endpoints

### 9d. Brickken MCP Integration (June 24, 2026)

Enterprise RWA tokenization platform with MCP server supporting ERC-8004 agent operations.

**Partnership prospect (Aug 4, 2026):** OPEN — pursuing 3-in-1 outreach (DM / Certified
Partner Program / sales+tech email). Brickken tokenizes the asset, Gentech moves the
money on it (both run CLI→x402→ERC-8004). Full value prop + drafts:
`references/brickken-partnership-prospect.md` + vault `11-Mess Hall/partnerships/`.

**MCP URL:** `https://mcp.brickken.com/mcp`
**Config:** Added to Hermes config as remote MCP server
**Chains:** Ethereum, BNB Chain, Base, Polygon

**x402 Agentic Tools (11):**
- Identity: `agent_register`, `agent_set_uri`, `agent_set_metadata`, `agent_set_wallet`, `agent_transfer_ownership`
- Reputation: `agent_give_feedback`, `agent_revoke_feedback`, `agent_append_feedback_response`
- Agent Tokens: `agent_create_token`, `agent_mint_token`, `agent_burn_token`, `agent_transfer_token`, `agent_approve_token`

**API Key dapp Tools (25+):** Full tokenization platform — create STOs, security tokens, dividends, whitelisting

**Integration with our stack:**
- Cross-platform ERC-8004 identity (they register agents too)
- Agent token launches for Agent Arena
- Reputation scoring across platforms
- RWA layer for agent economy

**Setup:** Configure with private key + environment (sandbox first, then production)

### 9e. PayAI Facilitator (Queued — June 24, 2026)

x402 payment facilitator — Solana-first, multi-chain. Replaces Ampersend (v1 only) for Solana x402 v2.

**Facilitator URL:** `https://facilitator.payai.network`
**Free tier:** 10,000 settlements/month, no API key needed
**Chains:** Solana, Base, Polygon, Arbitrum, Avalanche + 6 more
**Endpoints:** `/verify` + `/settle` (standard x402 facilitator shape)

**Why PayAI over alternatives:**
| | Coinbase CDP | PayAI |
|---|---|---|
| Chains | Base (primary) | Solana, Base, + 6 more |
| Free tier | Limited | 10K settlements/month |
| Speed | ~2s | Sub-second |
| Solana x402 v2 | ❌ | ✅ |

**Status:** Already used by WURK.FUN for Solana payments. Queued for integration into our API stack.

### 9f. Platform Registration Results (June 24, 2026)

Research completed on 8+ platforms for agent/API discovery:

| Platform | Status | Notes |
|----------|--------|-------|
| Agenstry.com | Researched | Free, submit at agenstry.com/submit, A2A Agent Card format |
| x402-list.com | Researched | Free web form, 63 services listed |
| signal402.com | Researched | $0.01 x402 payment, 145 services |
| x402.direct | Researched | Automated (Bazaar discovery), currently down |
| a2a-registry.org | Researched | Auto-discovery from well-known URI ✅ |
| a2aregistry.org | Researched | 127+ agents, well-known URI validation |
| a2alist.ai | Researched | $0.99 for verification badge |
| a2aagentlist.com | Researched | Email submission only |

**Action needed:** Jordan to submit to Agenstry, x402-list, signal402, a2alist (browser-based tasks)

### 9c. Pay-Skills Catalog (Solana Foundation) ✅ SUBMITTED

List APIs in the Solana Foundation's pay-skills directory for agent-to-agent commerce.

**Format:** YAML frontmatter + markdown body in `PAY.md` files
**Location:** `10-Labs/<api-name>-api/PAY.md`
**Submission:** PR to `solana-foundation/pay-skills` repo
**PR:** #154 — 12 PAY.md files submitted (Jun 24, 2026)

**PAY.md Template:**
```markdown
---
name: gentechlabs-<api-name>
title: GenTech Labs — <API Name>
category: <category>
version: 1.0.0
author: gentech
description: >
  <One-line description of what the API does>
  <Payment model and network info>
endpoints:
  - method: GET
    path: /v1/<endpoint>
    description: <What it does>
    price_usd: <price>
    request: { <params> }
    response: { <fields> }
network: base
currency: USDC
payment_protocol: x402
base_url: https://gentechlabs.net
---

# GenTech Labs — <API Name>

<Description>

## Endpoints

- `GET /v1/<endpoint>` — <Description> ($<price>)

## Payment

x402 USDC on Base. Each call returns a `Payment-Required` header with x402 challenge when payment is needed.
```

**Categories:** `shopping`, `finance`, `security`, `travel`, `data`, `ai-agents`, `identity`, `wallets`

**Current status (Jun 2026):** 12/12 PAY.md files scaffolded. Ready for PR submission.

**See:** `references/pay-skills-format.md` for full format requirements

### 9. Marketplace Discovery & Registration

Comprehensive marketplace strategy for API/agent discoverability.

**47 platforms across 8 categories** (from "Where to List Your API or MCP Server" guide, April 2026):

**HIGH PRIORITY (register first):**
| Platform | Reach | Effort |
|----------|-------|--------|
| GitHub | 150M+ devs | Low |
| npm / PyPI | 3.1M packages | Low |
| Official MCP Registry | Queried by all MCP clients | Medium |
| Awesome MCP Servers | 85K stars | Medium |
| Product Hunt | 4.6M visits/mo | High |

**MEDIUM PRIORITY (agent-specific):**
| Platform | Reach | Effort |
|----------|-------|--------|
| PulseMCP | 12,970+ servers | Medium |
| AgentScan | Agent registry | Low |
| Virtuals ACP | $481M AGDP | Medium |
| Smithery.ai | MCP marketplace | Low |
| Composio | Agent tool registry | Low |
| Glama | 21K+ MCP servers | Low |

**LOW PRIORITY (one-day spikes):**
| Platform | Reach | Effort |
|----------|-------|--------|
| Hacker News | Tech community | High |
| Reddit | Dev communities | Medium |
| Dev.to | Developer blog | Low |

**Registration order:** GitHub → npm/PyPI → Official MCP Registry → Awesome MCP Servers → PulseMCP → AgentScan → Virtuals ACP

**See:** `references/marketplace-directory.md` for full 47-platform list with traffic numbers

### 10. Ecosystem Validation Pattern

**July 5, 2026 — Travala MCP proves our stack is real.**

When major players adopt your technology stack (x402, ERC-8004, MCP), it's proof — not theory. Use this validation in hackathons, grant applications, and ecosystem partnerships.

**Travala Travel MCP — Proven Case Study:**

| Component | Travala Uses | Our Stack | Validation Signal |
|-----------|--------------|-----------|-------------------|
| **Payment** | USDC on Base via x402 (Coinbase Agentic Wallet MCP) | x402 (Q402 + Cloudflare) | ✅ Real product, not theoretical |
| **Identity** | ERC-8004 Agent Reputation tracking | ERC-8004 (Agent Registration API) | ✅ Identity standard in production |
| **Discovery** | MCP-compatible server | MCP integration (GOAT patterns) | ✅ "Be Everywhere, Own the Stack" |
| **Revenue** | cbBTC commission payouts to agent wallets | Commission model pattern | ✅ Revenue stream validated |

**Travala MCP Details:**
- Endpoint: `https://travel-mcp.travala.com/mcp`
- Wallet MCP: `npx @coinbase/payments-mcp`
- Scope: Hotel booking (v1.0) — flights/car rental/activities later
- Commission: cbBTC on Base
- Docs: https://www.travala.com/agentic-guide

**How to Use This Validation in Submissions:**

> "Our AgentKit stack aligns with industry leaders. Travala uses x402 for payments, ERC-8004 for reputation, MCP for tools — exactly what we're building. We're not theorizing — we're standing on proven infrastructure."

**Finding New Validations:**
1. Scan ecosystem announcements (X posts, blog posts, launches)
2. Check technology stack (look for x402, ERC-8004, MCP mentions)
3. Document alignment (map their usage to our stack)
4. Extract patterns (commission models, reputation tracking, payment flows)
5. Reference in submissions (hackathons, grants, partnerships)

**See:** `/root/vaults/gentech/00-HQ/travala-mcp-integration-strategy.md` for full strategy

### 11. Deep Dive Assessment Framework (Jul 5, 2026)

Systematic buildability evaluation for new ideas. See `references/deep-dive-assessment-framework.md` for full template.

**The Goal:** Determine if this is buildable now or needs blockers resolved.

**Structure:**
1. **The Hypothesis** — Articulate core assumption + list key assumptions
2. **What We Already Have** — Map existing assets to the solution
3. **Critical Components Breakdown** — Status (✅ Ready / ⚠️ Partial / ❌ Blocker) + time estimates
4. **Build Path Options** — Always present 2-3 paths with trade-offs (Fast Track vs Full Build)
5. **Revenue Modeling** — Conservative/Realistic/Aggressive scenarios
6. **Critical Questions for Jordan** — Get decisions before building
7. **File Storage** — `11-Mess Hall/YYYY-MM-DD-<topic>-deep-dive.md`

**When to use:** Jordan pitches a new revenue stream, hackathon concept, agent economy opportunity, or major infrastructure initiative.

**Pitfalls:** Don't skip hypothesis step. Don't gloss over blockers. Always present 2-3 options. Don't skip critical questions. Don't overpromise timelines.

**See:** `/root/vaults/gentech/11-Mess Hall/2026-07-05-agent-finance-intermediary-deep-dive.md` for a complete example.

---

### 10a. Competitive Analysis & Positioning

Prove GenTech AgentKit is competitive by building live, revenue-generating APIs with unique moats.

**Competitive Landscape (July 2026):**

| Feature | GenTech | Arsenal AI | GOAT AgentKit | OKX.AI |
|---------|---------|------------|---------------|--------|
| Live Paid Endpoints | 4+ | 48 | 20+ | ~30 |
| x402 v2 Support | ✅ | ✅ | ✅ | ✅ |
| Multichain | ✅ 5 chains | ✅ Multi | ✅ Multi | ✅ Multi |
| DeFi Native Analytics | ✅ **Unique** | ❌ | ❌ | ❌ |
| LP Strategy Engine | ✅ **Unique** | ❌ | ❌ | ❌ |
| Lowest Price | $0.003 | Varies | Varies | Varies |

**Our Competitive Moats:**
1. **DeFi Specialization** — No competitor offers LP pool health analysis, automated rebalance signals, or AI-powered strategy recommendations
2. **Proven Operations** — Actual DeFi infrastructure running (LP monitor, rebalances, strategy engine)
3. **Lowest Prices** — $0.003 for market sentiment vs $0.01+ elsewhere
4. **Multichain First** — 5 chains on Agent Registration (Base, Solana, Avalanche, BNB, OKX)

**Revenue Modeling Framework:**

Model revenue using three scenarios for each API:

| Scenario | Calls/Day | Avg Price | Yearly Revenue |
|----------|-----------|-----------|----------------|
| Conservative | 50-100 | $0.003-0.010 | $900-2,200 |
| Realistic | 500-1,000 | $0.003-0.010 | $9,000-22,000 |
| Aggressive | 2,000-10,000 | $0.003-0.010 | $36,000-220,000 |

**Path to Amazon Exit ($72,000/yr target):**
- Agent Registration (aggressive): $36,500 (50%)
- + DeFi Intelligence (realistic): $58,400 (81%)
- + Agent Search (realistic): $69,350 (96%)
- + Fleet Monitor (realistic): $85,775 (119%)

**Verification Pattern:**

Always verify APIs are live AND return REAL data before claiming they're revenue-ready. A service can pass every shallow check yet still be a dead end:

```bash
# Health check
curl https://<api-url>/health

# x402 discovery
curl https://<api-url>/.well-known/x402

# Test 402 payment challenge
curl https://<api-url>/<paid-endpoint>
# Should return HTTP 402 with PAYMENT-REQUIRED header
```

**CRITICAL — the placeholder trap (Aug 3, 2026 audit):** A "live" service with a healthy status endpoint + correct 402 challenge can STILL return hardcoded placeholder data when paid. Audit found 3 running services returning garbage nobody can buy:
- crypto-price-api → `{"price": 0.0, "source": "placeholder"}`
- gas-price-api → `{"ethereum": 0, "base": 0, "polygon": 0}`
- token-security-api → `{"score": 0, "level": "unknown"}`

These look ONLINE on the Bazaar/registry, accept payments, but return zeros → cannot convert, and they silently occupy dead surface area on the fee-earning rail. **They are a top reason $0 traction despite "live" listings.** The deal-tracker API had the same bug (`v1/deals` returned `[]`).

**Audit method (do this, don't trust systemd/health):**
1. Enumerate services: `systemctl list-units --type=service --state=running | grep -i api`
2. Grep every backend for the smoking gun: `grep -rn "placeholder\|source.*placeholder\|return {}" <api-dir>` — any hit = dead endpoint
3. Probe the ACTUAL data endpoints (not just health) with curl and eyeball the response body — a `price:0.0` or `deals:[]` is a red flag
4. For x402 gateways, follow the 307 redirect (`curl -sL`) to confirm the backend returns a real 402 challenge, then inspect the backend source for a real external-API call (DexScreener, RPC, etc.) vs a stub
5. **A running systemd service ≠ a functioning paid API.** Port can be up, health green, and still be a shell.

**Reuse existing engines instead of re-wiring:** token-security-api duplicated Rugcheck (which already had a real engine at port 8088) — check for an existing working service before building a placeholder.

**Fix = wire real data:** crypto → `crypto-price-fetch` skill / CoinGecko fallback; gas → Etherscan/live RPC; token-security → reuse the Rugcheck engine. See `references/api-health-audit.md` for the full worked recipe.

**Document Pattern:**

Create two documents for each competitive audit:

1. **`competitive-portfolio.md`** — Live API dashboard with quick status
2. **`competitive-audit-<date>.md`** — Full competitive analysis with revenue models

Commit both to vault to maintain competitive positioning documentation.

**Key Pitfalls:**
- **Never claim competitive without live verification** — Always run health + x402 discovery checks
- **Cloudflare deployments need CLOUDFLARE_API_TOKEN** — Without it, only temp URLs work
- **Revenue models are projections, not guarantees** — Use conservative/realistic/aggressive bands
- **Competitor counts change** — Arsenal may add APIs, new platforms emerge — re-audit quarterly

**See:** `references/competitive-analysis-framework.md` for full competitive audit template

### 12. GitHub Awesome List Ecosystem PRs

Submit GenTech services to GitHub awesome lists, community repos, and ecosystem directories. This is a recurring cron job (Ecosystem Lister) that systematically finds and submits to relevant repos.

#### Discovery Pattern

1. **Search for relevant awesome lists**: `site:github.com awesome <topic> <year>` — topics: x402, micropayments, pay-per-call, AI agent tools, MCP servers, crypto APIs, DeFi dashboards, game deals, token security, agent payments, agentic commerce.

2. **Check existing forks for prior work**: `gh repo list ProtoJay4789 --fork --limit 200 --json nameWithOwner` — cross-reference against discovered repos to avoid already-opened PRs.

3. **Check existing PRs**: `gh pr list --repo <owner>/<repo> --author ProtoJay4789 --state all --json number,title,state`

4. **Verify service health before submitting** — run these checks on every candidate service:
   - x402 gateway: `curl -s -o /dev/null -w "%{http_code}" https://api.gentechlabs.net/.well-known/x402` (expect 200)
   - Rugcheck: `curl -s -o /dev/null -w "%{http_code}" https://rugcheck.gentechlabs.net/health` (often 522 — skip if down)
   - Agent Kit: `curl -s -o /dev/null -w "%{http_code}" https://github.com/Gentech-Labs/genTech-agent-kit` (expect 200 — **NOTE: the personal-account copy `ProtoJay4789/genTech-agent-kit` 404s on the web; the org copy `Gentech-Labs/` is the canonical public one — see pitfall below**)
   - Shop: `curl -s -o /dev/null -w "%{http_code}" https://gentechlabs.net/shop` (expect 200)
   **Do NOT submit services returning 5xx/522.** Flag them for Jordan as fix-blocking-listing.

5. **Check existing listing** — grep for `GenTech\|gentech\|ProtoJay` in the target repo's relevant files.

6. **Read CONTRIBUTING.md** — verify we meet quality/content requirements before forking.

#### Submission Process

1. Fork: `gh repo fork <owner>/<repo> --clone`
2. Edit the relevant file following existing format exactly
3. Commit and push: `git add <file> && git commit -m "Add GenTech <Service>" && git push origin main`
4. Create PR with quality checklist: `gh pr create --repo <owner>/<repo> --title "Add GenTech <Service>" --body "<quality checklist>"`
5. For awesome-mcp-servers, append `🤖🤖🤖` to PR title for automated fast-track
6. Log to PR portfolio: `/root/vaults/gentech/10-Labs/pr-portfolio.md`

#### High-Value Targets by Category

| Category | Repos | Our Service |
|----------|-------|-------------|
| x402 / micropayments | awesome-x402, **gold-402**, awesome-agentic-payments | x402 Gateway (15 endpoints, 5 chains) |
| MCP servers | awesome-mcp-servers, awesome-crypto-mcp-servers | Agent Kit, GenTech Shop |
| Solana AI | awesome-solana-ai | Agent Kit, x402 Gateway |
| Public APIs | public-apis | x402 Gateway, Agent Kit |
| MPP protocol (awesome-mpp) | Skip — MPP ≠ x402 | — |
| OpenClaw skills (awesome-openclaw-skills) | Skip — requires ClawHub publication | — |

**gold-402** (Haustorium12/gold-402) — the curated x402 resource directory. Highest signal among x402 lists.
- Format: `- [Name](url) [![Multi-Chain](badge)](link) — Description. $price. ([links])`
- x402 Gateway → `directory/apis.md` (Crypto & DeFi Data section)
- Agent Kit → `directory/mcp-servers.md` (Crypto & DeFi Intelligence section)
- One entry per PR — do NOT batch services in a single PR

#### Pitfalls

- **Always check existing PRs first** — many repos already have open GenTech PRs from prior cron runs; submitting a duplicate wastes maintainer attention
- **Service 522 = do not list** — Rugcheck v2 is frequently down at Cloudflare level; cannot be listed while failing
- **Duplicate branches cause confusion** — when pushing from a new branch, close stale PRs from prior branches targeting the same repo
- **gold-402 requires x402 protocol** (HTTP 402 + X-Payment header) — listing rejected if only USDC payments without x402
- **awesome-crypto-mcp-servers** is highly curated — file a nomination issue first, not a PR
- **public-apis** requires free or freemium access tier — paid-only APIs may not qualify
- **Stale forks need upstream sync** before editing: `git fetch upstream && git checkout main && git merge upstream/main`
- **Personal-account repos 404 on the web (flagged account) — use the Gentech-Labs org for public links.** Verified Aug 1, 2026: `github.com/ProtoJay4789/genTech-agent-kit` returns 404 even though the GitHub API says the repo is public and pushes succeed. The same repo lives at `github.com/Gentech-Labs/genTech-agent-kit` (public, working). Rule: BEFORE putting any GitHub URL in an application, listing, or outreach message, verify it with `curl -s -o /dev/null -w "%{http_code}" <url>` (expect 200) — and prefer `Gentech-Labs/<repo>` links. Also: `ProtoJay4789.github.io` GitHub Pages is NOT serving (404) — do not link portfolio/dashboard pages there until Pages is fixed.
- **GitHub API "public" ≠ web-visible.** The repos list API can report `private: false` for repos whose web pages 404 (account flag). Always confirm the html_url is actually fetchable, not just the API record.

## Related Skills

- `blockchain/base` — Base chain queries
- `finance/ampersend-x402-payments` — x402 payment integration
- `defi` — LP monitoring (for Compound vs. Extract)
- `hackathon` — submission workflows
- `distribution/agent-tool-distribution` — Distributing GenTech APIs via PyPI, GitHub, MCP

## Marketplace / Listing Registry (MANDATORY CHECK)

`/root/vaults/gentech/11-Mess Hall/marketplace-listings-registry.md` — the
single list of every marketplace/website/protocol where GenTech is listed
(x402-list, 8004scan, Agentic.Market, GitHub org/personal, etc.). Jordan
directive (Aug 2026): on ANY service change (new endpoint, price, brand,
chain), update every affected row and prompt Jordan to confirm. Never
silently skip a platform. New listing → append a row.

## Infrastructure Issues Playbook (MANDATORY CHECK)

Before debugging any gateway/connection/compliance problem, read
`/root/vaults/gentech/11-Mess Hall/infrastructure-issues-playbook.md` — it's
the canonical log of issues we've already diagnosed (x402 EIP-712 domain
params, GitHub flagged-account 404s, Nous balance misreads). Same symptom →
same fix, minutes not days. When we help other teams become x402-compliant,
this is the fast-path reference. NEW issues get appended there with
symptom → root cause → fix → verification → lesson (Jordan directive, Aug 2026).

## Reference Files

- `references/agentscan-metadata-update-with-image.md` — **NEW** — Full workflow: metadata fix + avatar IPFS upload + on-chain update (Jun 27, 2026)
- `references/erc8004-tenderly-workaround.md` — Proxy contract workaround
- `references/oASF-metadata-format.md` — OASF v1.0 format
- `references/agentscan-research.md` — Ecosystem research notes
- `references/agentscan-api.md` — API documentation
- `references/wallet-funding-guide.md` — Multi-chain funding strategy
- `references/pay-skills-format.md` — PAY.md format requirements
- `references/marketplace-directory.md` — 47-platform directory with traffic numbers
- `references/competitive-analysis-quack-ai.md` — Quack AI vs GenTech comparison, integration strategy (NEW — Jun 24, 2026)
- `references/bankr-x402-integration.md` — Bankr x402 Cloud integration, $100K Inference Program (NEW — Jun 24, 2026)
- `references/treasury-robinhood-token-launch.md` — **NEW** — $TREASURY token launch on Robinhood Chain via Bankr (Jul 22, 2026). Full launch flow, strategic context, key lessons, and follow-up items.
- `references/bankr-wallet-revenue-source.md` — **NEW** — Track Bankr wallet income in the Revenue Monitor: Bankr auto-provisions its own EVM+Solana wallet (≠ Jordan's MetaMask), `GET /wallet/portfolio` API shape, `BANKR_API_KEY` wiring pattern, and test-verification (Aug 3, 2026).
- `references/singularity-agent-pods-integration.md` — **NEW** — Singularity Agent Pods, ClawPod, x402-Layer ClawHub Skill, and OpenClaw distribution play (Jul 22, 2026).
- `references/openclaw-genTech-skill.md` — **NEW** — GenTech OpenClaw skill strategy for 384k-star distribution channel (Jul 22, 2026).
- `references/cursor-directory-listing.md` — **NEW** — Cursor Directory plugin submission for GenTech x402 gateway (Jul 22, 2026).
- `references/vps-migration-github-offload.md` — **NEW** — Moving portfolio, music data, gaming hub, and vault backup from GitHub to VPS to reduce API rate limit pressure (Jul 22, 2026).
- `references/unity-cli-integration.md` — **NEW** — Unity CLI agent-native game dev pipeline (Jul 22, 2026).
- `references/clawwork-integration.md` — **NEW** — ClawWork AI agent freelancing engine: setup, architecture, CLI commands, nanobot version pitfall, and GenTech integration strategy (Jul 27, 2026).
- `references/8004scan-registry-explorer.md` — 8004scan.io explorer facts: same-registry auto-indexing, chain IDs (1776 = Injective EVM), no-public-REST-API reality, lead triage pattern, a2a module layout (Aug 1, 2026).
- `references/x402scan-compatibility.md` — x402scan/x402-list checker compatibility: the EIP-712 `extra.name/version` fix for "route not signable" (the 14th compliance check), `/.well-known/x402` canonical discovery, assessment chip semantics, verification recipe (Aug 2026).
- `references/x402-gateway-verification-loop.md` — **NEW** — Server-side x402 gateway loop: standard `Authorization: x402 <proof>` / `X-Payment` header acceptance (NOT private `x-402-token`), CDP facilitator + HMAC proof verification, 3-tuple backend routing table, "manifest is a promise" rule, paid/underpaid/unpaid verification matrix, and keyless backend data sources (8004scan snake_case fields, Magic Eden no-search-param, DexScreener, Solana RPC). Root cause of $0 traction with 10K visitors — test the FULL payment loop, not just discovery (Aug 2, 2026).
- `references/bankr-skills-marketplace-listing.md` — **NEW** — Bankr listing via skills marketplace (0% fee, self-hosted) instead of x402 Cloud (5%): SKILL.md publish flow, org-repo master-branch pitfall, `Gentech-Labs/` not `ProtoJay4789/` links, never inline long content in Telegram (Aug 2, 2026).
- `references/scam-token-verification-chainabuse.md` — **NEW** — Verify unsolicited wallet tokens on-chain before declaring scam (homoglyph Cyrillic/dotted chars, zero DexScreener pairs, fake price feed, rule out legit sources in vault), then file a Chainabuse report (toggle support OFF to enable submit, SUBMIT ANONYMOUSLY, SPA click pitfalls) (Aug 2, 2026).
- `references/treasury-defender-scam-defense.md` — **NEW** — Treasury Defender service (7th paid x402 endpoint, port 8096): homoglyph confusables map, ABI string decode gotcha, safe-burn-never-auto-sign principle, port-conflict drop-in pattern, exact x402 simulation proof format for testing paid endpoints, and the add-a-service full checklist (Aug 2, 2026).
- `references/api-health-audit.md` — **NEW** — API health audit + placeholder fix: how "live" services return hardcoded zeros, the 5-step audit method, Aug 3 findings table, fix paths, and the deal-tracker `sys.path` sibling-engine wiring pattern (Aug 3, 2026).
- `references/cdp-bazaar-self-settlement.md` — **NEW** — CDP Bazaar listing mechanism: settle-not-verify, PAYMENT-SIGNATURE header, base64 proof, CDP JWT auth (EdDSA/ES256), self-settle script, dependency-conflict workaround, wallet-funding reality (Aug 3, 2026).
