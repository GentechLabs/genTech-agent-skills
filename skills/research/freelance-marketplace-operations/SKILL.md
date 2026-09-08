---
name: freelance-marketplace-operations
description: "Scan, evaluate, and operate on AI agent freelance marketplaces (Hive/uphive.xyz). Covers REST API scanning, task analysis, competition assessment, and vault-based opportunity reporting."
tags: [marketplace, hive, uphive, freelance, agent-marketplace, api]
trigger: "When scanning Hive or other AI agent freelance marketplaces for open tasks, analyzing competition, or generating marketplace opportunity reports. Also triggers for marketplace agent registration or proposal strategy."
related_skills:
  - opportunity-discovery  # parent umbrella for marketplace scanning
  - hackathon  # for cross-referencing skill alignment
version: 1.0.0
author: Gentech
---

# Freelance Marketplace Operations

## Overview

Systematic workflow for scanning AI agent freelance marketplaces to identify high-value tasks, assess competition, and generate actionable reports. Uses **AgentScan** (agentscan.info) as the master map of the agent economy, then dives into specific marketplaces like Hive.

## Data Source: AgentScan (agentscan.info)

AgentScan is the ERC-8004 agent explorer — the trust layer for the agent economy. It indexes agents, ecosystems, and activity across 21+ blockchain networks.

### REST API (No auth required)

**Base URL:** `https://agentscan.info/api`

| Endpoint | Description |
|----------|-------------|
| `GET /api/agents?page=1&page_size=100` | Search/list agents with filtering |
| `GET /api/agents/{id}` | Full agent details |
| `GET /api/agents/trending` | Top-ranked trending agents |
| `GET /api/agents/featured` | Curated featured agents |

**Agent fields:** `name`, `address`, `network_id`, `reputation_score`, `skills`, `domains`, `ecosystems`, `capabilities`, `status`

### Ecosystems Page (Browser)

`https://agentscan.info/ecosystems` — shows all tracked agent economy ecosystems with:
- Total AGDP (Agent Gross Domestic Product)
- Total revenue and jobs
- Unique active wallets
- Top agents by earnings
- Recent agent-to-agent transactions

**Known ecosystems (Jun 2026):**
- **Virtuals ACP** — $481M AGDP, 2.28M jobs, 29.96K wallets (largest)
- **BNB Agent Stack** — 140K+ ERC-8004 agents
- More listed on the ecosystems page

### How to use AgentScan for marketplace discovery:

1. **Check ecosystems page** — identify where agents are earning the most
2. **Query trending agents** — see what skills/capabilities are in demand
3. **Cross-reference** with known marketplaces (Hive, ClawGig, MoltJobs)
4. **Register on new platforms** found through ecosystem analysis

> **If an agent shows empty skills/domains on a registry despite a populated metadata file,
> the `metadata_uri` is likely 404ing unauthenticated** — see
> `references/registry-metadata-uri-404.md` for the diagnosis + fix (host metadata at a
> public URL; the on-chain URI update needs the owner wallet's signature).

## Platform: Hive (uphive.xyz)

### REST API (Preferred Method)

Hive has a public REST API. **Always use this over browser automation** — the site is a Next.js SPA that causes browser tools to timeout.

**Base URL:** `https://uphive.xyz/api/tasks`

**Key Endpoints:**
```
GET /api/tasks?limit=50                    # All tasks (default sort: newest)
GET /api/tasks?status=Open&limit=50        # Open tasks only
GET /api/tasks?status=In+Progress&limit=50 # In-progress tasks
GET /api/tasks?category=Development        # Filter by category
```

**Response Shape:**
```json
{
  "tasks": [{
    "id": "string",
    "title": "string",
    "description": "string (markdown)",
    "category": "Development|Research|Design|Content|Analysis|Security|Social|Legal|Translation|Token Launch|Other",
    "tags": ["string"],
    "budget": "$1 USDC",
    "budgetAmount": 1,
    "status": "Open|In Progress|Completed",
    "proposalsCount": 4,
    "clientAddress": "did:privy:...",
    "clientName": "string",
    "assignedAgent": "string (agent ID, null if unassigned)",
    "assignedAgentName": "string (null if unassigned)",
    "createdAt": "ISO 8601",
    "updatedAt": "ISO 8601",
    "url": "https://uphive.xyz/marketplace/{id}",
    "deliverableSpecs": [{"type": "code|text", "label": "string", "description": "string", "required": true}],
    "tokenConfig": null
  }],
  "total": 100,
  "page": 1,
  "limit": 50
}
```

**Categories (11):** Development, Research, Design, Content, Analysis, Security, Social, Legal, Translation, Token Launch, Other

**Premium API ($HIVE holders):** `GET /api/x402/tasks` returns enriched data with bid counts, avg bid amounts, client history. Requires `X-Wallet-Address` header with Solana wallet holding $HIVE tokens.

### Market Reality (as of May 2026)

- **100 total tasks** on platform, ~54 completed, ~44 in progress, ~2 open at any time
- **Average budget:** $2.23 USDC. Median ~$1. Standard dev task = $1 USDC.
- **Highest completed task:** $100 USDC (Vite+TanStack deployment pipeline)
- **Dominant competitor:** Agent "Axiom" wins most Development tasks
- **Typical turnaround:** Tasks assigned within 1-2 days of posting
- **Best categories for us:** Development (Python, TypeScript, CLI tools), Security (audits), Analysis
- **Categories to skip:** Social (content writing), Design (UI/UX), Translation

### Scanning Workflow

1. **Fetch tasks via API:**
   ```bash
   curl -sL "https://uphive.xyz/api/tasks?limit=100" -o /tmp/hive_tasks.json
   ```

2. **Analyze with Python script** (write to file, then execute — don't pipe curl to python):
   ```python
   # Save as /tmp/analyze_hive.py
   import json
   with open("/tmp/hive_tasks.json") as f:
       data = json.load(f)
   tasks = data.get("tasks", [])
   open_tasks = [t for t in tasks if t.get("status") == "Open"]
   # ... filter, score, report
   ```

3. **Score tasks by relevance** using:
   - Category match (Development/Security/Analysis = high)
   - Tag alignment (Python, TypeScript, API, smart contract, DeFi)
   - Proposal count (≤3 = low competition bonus)
   - Budget amount (> $5 = bonus, > $10 = strong bonus)

4. **Generate structured report** with:
   - Executive summary (count by status, total opportunity value)
   - Open tasks with scores and links
   - Platform stats (avg budget, category breakdown, dominant agents)
   - Recommendation (pursue/monitor/skip)

5. **Save to vault:** `09-Green Room/hive-marketplace-scan-{date}.md`

### Report Template

```markdown
# Hive Marketplace Scan — {Date}

## Summary
- Total tasks: N | Open: N | In Progress: N | Completed: N
- Average budget: $X USDC
- Recommendation: {pursue/monitor/skip}

## Open Tasks
### 1. {Title}
- **Budget**: $X USDC | **Proposals**: N | **Category**: {cat}
- **Tags**: [...]
- **Fit**: ★★★★☆ — {reasoning}
- **Link**: https://uphive.xyz/marketplace/{id}

## Platform Observations
- {Key stats and patterns}

## Recommendations
- {Actionable next steps}
```

### Pitfalls

1. **Don't use browser tools for Hive** — the Next.js SPA causes timeouts. Use `curl` + REST API.
2. **Don't pipe curl to python** — security scanners block `curl | python3`. Write to file first.
3. **`web_extract` with DuckDuckGo backend can't extract URLs** — use `curl` via terminal instead.
4. **Open task count is misleading** — "100 total tasks" doesn't mean 100 open. Usually only 1-3 are open at any time.
5. **$1 tasks dominate** — don't spend more than a few minutes evaluating a $1 task. Only pursue if it's a quick win (< 30 min work).
6. **Agent "Axiom" is the dominant competitor** — if Axiom is already assigned or has proposed, the task is likely spoken for.
7. **Authenticated Hive calls use `x-hive-api-key` header, NOT `Authorization: Bearer`** — `curl -H "Authorization: Bearer <key>"` returns `{"error":"Authentication required. Provide x-hive-api-key header."}`. Use `-H "x-hive-api-key: hive_sk_..."` for PATCH /api/agents/me, wallet ops, and proposals. Verified Aug 2026: Bearer fails, x-hive-api-key succeeds. (Check `references/hive-api-reference.md` — it may still show the wrong header.)
8. **Linking a Solana wallet requires the owner's signature — cannot be automated.** `PATCH /api/agents/me {"solanaAddress": ...}` returns `{"error":"Wallet signature required to link this Solana address."}`. The agent cannot sign with the owner's private key (and must never hold it). The human must do it in-browser at `https://uphive.xyz/agent/dashboard` → Link Wallet → sign the message in MetaMask. Until linked, the profile shows `walletLinked: false` and **cannot receive USDC payouts even though it can bid**. This is the real unlock to actually earning on Hive — flag it to Jordan as a required manual step, not something the agent can do.
9. **Agent profile introspection** — `GET /api/agents/me` (with x-hive-api-key) returns `{agent:{id,name,bio,capabilities[],reputation,avgSatisfaction,reviewCount,isVerified,isStaked,walletLinked,solanaAddress,website,registeredTools[]}, stats:{tasksCompleted,activeBids,totalEarnings}, authMethod}`. Use `PATCH /api/agents/me` with `{"bio":...}`/`{"capabilities":[...]}` to keep the listing fresh. Registration (`POST /api/agents/register`) returns the one-time API key + recovery code — save both.
10. **Sell-side vs buyer-side marketplaces (Jordan directive, Aug 2026)** — He wants SELL-side platforms ("Fiverr for AI agents") where clients hire us: Hive, OKX.AI, Atelier, Syra, x402scan, Fluora. **earn.fi and WURK.fun are BUYER-side** — where WE pay to hire humans (feedback, social proof, contests) via x402 USDC on Solana. They are expense platforms, NOT income sources. Do not scan them for income or auto-bid there; only note if a service helps our own submissions.

### Auto-Bidding on Hive (proven Aug 2026)

Once the GentechLabs agent is registered (has an API key), the marketplace cron can **auto-submit proposals** on high-fit tasks instead of just reporting. Safe even at 0 reputation (nothing to lose; Hive tasks are tiny $1-2 USDC). Auto-bid only when **ALL** hold:
1. Status is Open (unassigned)
2. Category is Development / Security / Analysis (skip Social, Design, Translation)
3. `proposalsCount <= 3` (low competition)
4. Fits our stack (AI agents, MCP, x402, Solidity/Rust, DeFi analytics, Python/TS, smart-contract audit, CLI tooling)
5. `budgetAmount >= 1` USDC

**Proposal template (3-5 sentences max):** open with how you'll deliver the task's `deliverableSpecs`, reference GenTech's real capabilities (multi-agent team, DeFi tools, smart contracts, on-chain analytics on Solana + EVM, x402 gateway, hackathon-grade), no filler. Submit via `POST /api/tasks/{id}/proposals` with the Hive API key, or the `hive_propose` MCP tool.

**Log every submission** to `09-Green Room/hive-proposals-log.md` (date, task title, task id, budget, proposal summary, link) so Jordan can audit. If the submission errors, report it honestly — never fabricate a confirmation. Keep other marketplaces report-only until Hive auto-bidding is proven.

### Pitfall: WURK is a BUYER platform, not income

WURK.fun is where **we hire humans** (feedback, social proof, content) — it is NOT an income/marketplace source. Do not treat `wurk_*` tools as income. A consolidated "marketplace income scanner" should scan Hive/OKX/earn.fi/Atelier for tasks we sell into, and list WURK only as a buyer note.

### Verify the PAYOUT rail before grinding work (BountyBook lesson, Aug 12 2026)

Open jobs + "X USDC available" in escrow does NOT mean money that moves. Before
investing a claim+build+submit cycle on a marketplace, verify payments actually
land — otherwise you produce unpaid work. BountyBook (bountybook.ai) is the case
study: its auth + claim + submit pipeline worked end-to-end (agent wallet
`0x80dD…1e47`, claimed merge_csv $3.50, code passed its own test suite, submitted),
yet the platform has NEVER paid anyone — 0/32 code_test settlements (oracle
crashes on `spec.success_condition.required_fields.length` vs `required_files`
→ `undefined.length`, `checksFailed:["ipfs_fetch"]`), verified non-code jobs sit
at `payout_status=failed` with no `payout_tx_hash`, and the treasury wallet
`0x1bc6…72f2b` shows zero lifetime USDC outflows on Base.

**Payout-rail pre-check (do before grinding on ANY new marketplace):**
1. Pull a couple already-verified/claimed jobs and read their `payout_status` +
   `payout_tx_hash`. A verified job with no tx hash = broken payout.
2. Check lifetime outflows on the platform's settlement/treasury wallet on the
   settlement chain (`eth_getBalance` / `balanceOf`, or a block-explorer API).
   Zero outflows = nothing has ever been paid.
3. Read the job's `attempts[]`: if EVERY attempt from multiple agent wallets
   fails the SAME verifier error, it's a server-side bug, not your output.
4. Grep the marketplace's own board for "fix the verifier/payout" bounties other
   agents already posted — that confirms the operator knows, so don't re-grind
   or re-report.
5. Docs claiming inline `outputData` needs "no IPFS" don't matter if the verifier
   crashes before reading output — reproduce the exact documented payload once
   to prove whether the crash is server-side.

Only burn a full claim+build+submit cycle once the payout rail demonstrably
fires (a verified job carries a real tx hash). Re-check BountyBook ~Aug 19 2026:
if verified jobs start showing `payout_tx_hash`, it becomes a strong autonomous
rail; until then treat it as parked. Full diagnostic:
`references/bountybook-payout-diagnosis.md`.

### Marketplace Income Scanner V2 — Registry-Deduped, NEW-Only Hunt (Aug 5, 2026)

The income scanner cron (38eda06b0a11) was upgraded from "re-scan the same known platforms"
to **dedupe against the live registry + hunt genuinely NEW sell-side platforms**. This is
the crown job pattern: never re-report what we already have; find NEW income rails instead.

**Seed/registry parser:** `marketplace-seed.py` parses `11-Mess Hall/marketplace-listings-registry.md`
into machine-readable JSON:
- `already_listed` — platforms where GenTech is live (EXCLUDE: x402-list, 8004scan, api.gentechlabs.net, OpenDexter, ...)
- `watchlist` — pending/in-progress (EXCLUDE: Syra, x402scan, MCP directories, ...)
- `known_not_pursued`, `all_keywords` — extra names/domains to match against

**DEDUP RULE:** A marketplace is NEW only if its name AND domain do NOT appear in
already_listed, watchlist, known_not_pursued, or all_keywords. If matched, SKIP — we
already have a presence there. Attach the seed as the cron's `script` so its JSON
auto-injects into the scan context (the agent reads the exclusion list instead of re-deriving it).

**For each NEW candidate, the report must include:**
1. **Why we should be there** — 1-2 sentences: what it does, who hires on it, what's in it for GenTech
2. **Income estimate** — realistic $/month or $/task range based on platform activity. Be honest; don't inflate.
3. **Entry friction** — open-entry (no stake >$50, no incorporation, remote/online)? Flag desktop-only or staked platforms.

**Proven workflow (live run Aug 5, 2026):** scanned Hive (auto-bid filter), then web-searched
beyond the known list and found 3 genuinely NEW sell-side marketplaces (Freelance AI/PayAI,
BotWork, Amadeus Agent Hub), each with why-there + income + friction, auto-appended to the
registry as watchlist rows. Cross-reference each candidate against our 13 live x402 APIs
(token security, DeFi intel, wallet analysis, LP analytics, NFT search, treasury defense,
games API) to find categories each NEW platform lacks — that's where first-mover value is.

**Pitfall — the registry parser needs markdown-stripping:** `_extract_names_from_table` must
strip `**` bold markers and `[text](url)` links from the Platform cell, or it emits noise like
`**OpenDexter` which pollutes the exclusion list. Verified Aug 5, 2026: without
`re.sub(r"\*\*", "", name)` the dedupe list carried literal `**` prefixes.
**Pitfall — cron scripts must be copied to the profile scripts dir:** the cron scheduler
rejects absolute vault paths; the seed must live at `/root/.hermes/profiles/gentech/scripts/marketplace-seed.py`
and be referenced by filename only.

### Pitfall: verify the cron script path exists before trusting the job

The original Hive monitor cron pointed at `10-Labs/hive-marketplace/hive-monitor.js` — a folder that was never created. The job **failed silently every run** (deliver=local, script missing). Before relying on any marketplace cron, confirm the referenced script actually exists (`ls` the path); a `no_agent` job with a missing script produces no delivery and no error to the user. The consolidated income scanner replaced this broken job.

### Future Enhancements

- **Agent registration:** Register on Hive to submit proposals. Requires API key via `POST /api/agents/register`.
- **Automated scanning:** Set up a cron job that fetches `/api/tasks?status=Open` daily and reports new tasks.
- **Premium API access:** Hold $HIVE tokens to access enriched task data (bid counts, client history, competition analysis).
