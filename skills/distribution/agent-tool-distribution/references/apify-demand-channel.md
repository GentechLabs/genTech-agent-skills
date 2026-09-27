# Apify Store — The Demand-Side x402 Channel (researched Aug 20 2026)

## Why this is the one that matters
Apify Store is the **largest marketplace of tools for AI agents** and the only x402
channel with real, proven buyer volume. We listed on a dozen supply-side directories
(x402-list, the402.dev, 8004scan, AgentLux, APIHub, RelAI, Toku, dealwork, AgentCash,
Nevermined, AgentPact, OpenDexter, Agentic.Market, x402scan) and earned **$0**. Apify is
where the paying agents actually are.

## Key facts (from Apify blog, Jun 30 2026)
- **20,000+ Actors now x402-payable** — a 10x jump from the ~2,000 endpoints the protocol
  had before. In partnership with Coinbase.
- **$1.4M paid out last month** to Actor developers (per our registry, Aug 14).
- Agents buy web data/automation with **USDC on Base**, no API key, no account, no human.
- Real $1.00 value examples:
  - ~380 Instagram profiles via `apify/instagram-profile-scraper`
  - ~250 Google Maps places via `compass/crawler-google-places`
  - ~165 Amazon/e-commerce products via `apify/e-commerce-scraping-tool`
  - ~330 viral TikTok videos via `clockworks/tiktok-video-scraper`
  - ~2,500 X posts on a topic via `apidojo/tweet-scraper`

## How x402 payment works on Apify
- Every Actor is callable at a plain REST endpoint, e.g.
  `POST https://api.apify.com/v2/actors/{actorId}/run-sync-get-dataset-items`
- Call without credentials (optionally signal with `X-APIFY-PAYMENT-PROTOCOL: X402` header)
  → server replies `402 Payment Required` with a base64 `PAYMENT-REQUIRED` header + JSON body.
- The challenge lists accepted schemes (`upto` and `exact`) in USDC on Base (eip155:8453).
- Client signs an authorization from its wallet, retries with `PAYMENT-SIGNATURE` header.
- `upto` scheme (x402 v2, Permit2 `permitWitnessTransferFrom`): authorize a max, pay only
  for actual usage — best for variable-cost batch runs.
- `exact` scheme (x402 v1, EIP-3009 `TransferWithAuthorization`): fixed price; Apify layers
  a $1.00 prepaid deposit + refund flow on top.
- The signed `PAYMENT-SIGNATURE` stays valid while the prepaid balance lasts — reused on
  later calls with no new signing until it runs out.

## Agent-side tooling (how buyers consume)
- **Coinbase Agentic Wallet CLI** (`npx awal`): reads the 402 challenge, signs with an
  on-chain wallet, runs the Actor. Works in Claude Code, Codex, Droid, OpenCode.
- **`mcpc`** (Apify's universal MCP CLI): one of the first MCP clients with native x402
  support — agents pay compatible MCP servers directly.
- Drop-in skill: `apify.it/x402-awal` (tells an agent how to use `awal`, check balance,
  request funds, run paid Actors over x402).

## How to publish an Actor (our path)
- **Needs an Apify account + Actor packaging** (Docker/containerized scraper) — this is the
  human-gated step. Not our x402-gateway model; it's a per-Actor container.
- Publish flow: `apify.com/partners/actor-developers` → create Actor → package as Docker →
  set pricing → publish to Store.
- **New (Jun 9 2026):** Actor creators can publish "tasks" — each task gets its own
  Store page indexed by search engines and readable by AI agents. Name tasks around what
  users actually search for (e.g. "RAG Web Browser" → tasks `site`, etc.).
- **New (Jun 24 2026):** x402 support for Actors is live.
- **New (Jun 26 2026):** Apify AI — plain-English search on Store picks the right Actor,
  fills inputs, runs it, returns the dataset. Improves discoverability of well-named Actors.

## Candidate GenTech Actors to package
- **Token security / Rugcheck** (Solana risk scoring) — our existing 8088 backend.
- **DeFi LP analyzer** — our defi_lp_analytics backend.
- **Wallet portfolio analysis** — our wallet_analysis backend.
- **agent_research** (the $0.05/call paid endpoint we shipped Aug 18) — package as an Actor
  so agents can buy it without an API key.

## Status
- Flagged in our marketplace registry as "NEEDS HUMAN" (Aug 14) — never acted on.
- **This is the single highest-leverage listing target for actual revenue.** Scope the
  Actor packaging + get Jordan's Apify account before proceeding.
