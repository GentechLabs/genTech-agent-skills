# x402 Ecosystem Scan — July 17, 2026

**Scout**: x402 Compliance Scout cron (daily 12:10 UTC)
**Model**: deepseek-v4-flash
**Scope**: Inbox duty (42 open PRs), new ecosystem targets, gateway compliance verification

---

## Inbox Duty — 3 Notifications Handled

| Notification | Reason | Action |
|---|---|---|
| solana-foundation/pay-skills#192 | PR activity (author) | Investigated — Greptile addressed (3 rounds). Mergeable ✅ |
| e2b-dev/awesome-ai-agents#1264 | @mention (cla-bot) | CLA signed and passed. PR mergeable ✅ |
| coinbase/agentkit#1375 | PR activity (author) | Heimdall 0/1 reviews. Normal waiting state ✅ |

All notifications marked read.

## PR Fleet Sweep — 42 Open PRs

**Key findings:**

| PR | Repo | Status | Action |
|---|---|---|---|
| solana-foundation/pay-skills#190 | pay-skills | MERGEABLE ✅ | Greptile addressed |
| solana-foundation/pay-skills#192 | pay-skills | MERGEABLE ✅ | Greptile addressed (3 rounds) |
| solana-foundation/solana-dev-skill#57 | solana-dev-skill | MERGEABLE ✅ | Greptile addressed |
| solana-foundation/awesome-solana-ai#197 | awesome-solana-ai | MERGEABLE ✅ | Greptile, clean |
| Scottcjn/awesome-agents#36 | awesome-agents | MERGEABLE ✅ | Line endings fixed, maintainer engaged |
| e2b-dev/awesome-ai-agents#1264 | awesome-ai-agents | MERGEABLE ✅ | CLA signed |
| coinbase/agentkit#1375 | agentkit | MERGEABLE ✅ | Heimdall 0/1 reviews |
| NousResearch/hermes-agent#50239 | hermes-agent | **CONFLICTING** ⚠️ | Needs rebase + teknium1 review |
| All other 34 | — | OPEN, no bot flags ✅ | Normal waiting state |

## New PR Submitted

| PR | Repo | Change | Status |
|---|---|---|---|
| [#35](https://github.com/Recall-Kitchen/awesome-x402-mcp-services/pull/35) | Recall-Kitchen/awesome-x402-mcp-services | Add GenTech Agent Kit (BlockRun MCP) to AI & Data section | ✅ OPEN, MERGEABLE, no bot flags |

## Gateway Compliance Check

**Target:** `gentech-x402-gateway.jordanjones0902.workers.dev`

| Endpoint | Status | Notes |
|---|---|---|
| `GET /` | 200 OK | Returns valid gateway metadata JSON |
| `GET /api/token/risk` | **500 Internal Server Error** ❌ | Should return 402 Payment Required with challenge |

**Root cause:** OpenAPI spec has `required: true` query params causing Cloudflare Workers framework crash before x402 middleware can respond with 402. Fix documented in x402-api-compliance skill.

**Blocks:** x402scan.com registration (build queue item #69). Source code not found locally — deployed via Cloudflare Workers dashboard (build queue item #70).

## New Targets Discovered

| Repo | Stars | Relevance | Decision |
|---|---|---|---|
| Recall-Kitchen/awesome-x402-mcp-services | 1★ | x402 + MCP services — perfect fit | ✅ PR #35 submitted |
| fffilimonov/awesome-x402-servers | 0★ | x402 servers list (stale, 1yr+) | ❌ Skip — too stale |
| Daehan-Base/awesome-x402-on-base | ? | Korean x402 on Base | ⏭️ Could not access |

## Tier Assignments

| Item | Tier | Action |
|---|---|---|
| Recall-Kitchen/awesome-x402-mcp-services PR | **Tier 1** | ✅ Submitted, clean |
| Gateway 500 → 402 fix | **Tier 2 (Gentech Only)** | Queue #70, needs worker source |
| x402scan registration | **Tier 2 (Gentech Only)** | Queue #69, blocked by #70 |
