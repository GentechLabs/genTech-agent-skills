---
name: opportunity-scanner-template
category: gentech
description: Reusable cron template for scanning DeFi, AI agent, and web3 opportunities — jobs, hackathons, grants, and startup roles. Designed for Agent Kit users.
tags: [opportunity, scanner, cron, template, defi, ai-agents, web3]
trigger: "When setting up or modifying an opportunity scanner cron job. Also triggers when the user asks to find web3 jobs, DeFi roles, AI agent positions, or startup opportunities."
---

# Opportunity Scanner — DeFi / AI Agent / Web3 Focus

## Purpose
Reusable template for scanning opportunities that match the modern web3/AI agent stack. Replaces traditional job board scanners that surface irrelevant traditional roles.

## Core Philosophy
**"Don't compete — integrate."** We're founders building in the agent economy. Jobs are a means to an end — funding our platform, not building someone else's. Scan for opportunities where our stack IS the value prop.

## Opportunity Categories (Priority Order)

### 1. AI Agent Infrastructure Companies
Companies building agent frameworks, MCP tools, x402 payments, agent wallets, agent marketplaces.
- **Why:** Our AAE stack IS their product category. We bring a living platform, not just a resume.
- **Search terms:** "AI agent engineer", "agent infrastructure", "MCP developer", "agentic AI", "AI agent framework"
- **Target companies:** Virtuals, ElizaOS, MyShell, Nous Research, Langchain, CrewAI, AutoGen, BlockRun, Binance (Tech Seeds / Pioneer Talent programs — rare entry-level AI agent roles at a major exchange)

**Job titles to search (Sep 8 research — the real titles):**
- **AI Agent Engineer** — builds/operationalizes autonomous agents (multi-step workflows, tool use, function calling). Most-searched title; remote-friendly.
- **Software Engineer, Agent Infrastructure** — builds the platform/SDKs/sandboxed execution agents run on. The "rails" role (OpenAI, Anthropic use verbatim).
- **Agent Platform Engineer** — full-stack on the team shipping the agent platform to customers.
- **AI Infrastructure Engineer** — distributed systems, model-serving, memory, orchestration powering agents.
- **Applied AI Engineer** — integrates agents into real products; production-grade agent infra, retrieval, eval. Very remote-friendly.
- **LLM Engineer** — products on LLMs: chatbots, copilots, RAG, agentic layers.
- **AI Systems Engineer** — systems programming for large-scale distributed AI/agent systems.
- **Forward Deployed Engineer (AI)** — ships agent solutions directly with customers. Strong fit for "building agents for other people."
- **Web3 AI Agent Engineer** — AI systems/agents for crypto orgs (Binance posts this exact title).
- **AI Agent Observability Engineer** — monitors/debugs/instruments agent fleets in production.
- **Staff AI Engineer (AI & Automation)** — owns agent infra + automation platform at scale (Grafana Labs).

**Best boards (Sep 8 research):**
- https://cryptocurrencyjobs.co/ai — best crypto+AI board; remote DeFi/AI agent roles (Nascent, Recall, Ethena, CoW DAO, 0x)
- https://ai-jobs.net — cleanest dedicated AI/ML/agent vertical, 800+ listings, strong remote filter
- https://web3.career — Web3 board with "AI Agent Engineer" category (Binance posts here)
- https://wellfound.com/role/r/artificial-intelligence-engineer — startup AI roles, salary+equity transparency
- https://work.mercor.com — hourly contract AI Agent Infrastructure gigs (individual-friendly, remote)
- https://ai.engineer/jobs — agent-platform-specific engineering jobs
- https://remotive.com — vetted remote-only board, AI/engineering section
- https://news.ycombinator.com/item?id=whoishiring — "Who is Hiring" monthly thread; highest-signal for early-stage AI agent startups
- https://jobstash.xyz — Web3/crypto jobs with agent-orchestration + AI filters
- https://builtin.com/jobs — AI Engineer category, strong remote filters

**Companies hiring (Sep 8 research — fit for our stack):**
- **Olas (autonolas)** — autonomous-agent infrastructure, agent ownership/coordination, Mech Marketplace
- **Giza Protocol** — AI agent platform for autonomous DeFi agents (monitoring, execution, rebalancing)
- **Griffain** — Solana on-chain agents / automation
- **Kite AI** — AI-agent payment infrastructure (Agent Passport)
- **Amadeus Protocol / Bitte.ai** — agent marketplace + cross-chain agent infrastructure
- **QuickNode** — MCP server + x402 agent payments for RPC compute (DIRECTLY our x402 stack)
- **Ethena Labs, CoW DAO, 0x, Nascent, Recall** — DeFi/crypto orgs hiring AI+DeFi engineers (remote)
- **Xpander AI** — Solutions Architect, AI Agents Platform
- **AI Acquisition** — senior full-stack for an AI agent platform (AI SDRs, autonomous account management)
- **Grafana Labs** — Staff AI Engineer (AI & Automation)
- **Temporal Technologies** — Staff SWE, AI Foundations (durable execution for agents)
- **GitLab** — Backend Engineer, AI Engineering (Duo Chat)
- **CrowdStrike** — Sr. AI Growth Engineer (remote)
- **Binance** — Web3 AI Agent Engineer, AI Agent Observability Engineer (remote APAC)
- **Anthropic / OpenAI** — exact "Agent Infrastructure" titles but hybrid/onsite + W-2 → screened out by remote directive

**Portfolio evidence that wins (our actual stack):**
- **x402 payment rail/middleware** — maps directly to agent-payment infra roles (QuickNode, Kite, Olas). Show live per-tx-fee middleware with receipts/proofs.
- **ERC-8004 agent identity** — the trust/identity layer; rare + differentiating for crypto agent-platform roles.
- **Multi-agent fleet ops** (Hermes on VPS + desktop) — production agent orchestration, observability, reliability → AI Agent Observability + Agent Infrastructure roles.
- **DeFi/treasury automation** — maps to Giza/Griffain/Olas autonomous DeFi agent roles; show live strategies + rebalancing.
- **Hackathon wins** — strong signal for startup/agent-platform hiring; list with links + working demos.
- **Public, runnable artifacts over resumes** — agent-platform + crypto startups hire on shipped, working code. A GitHub with live agent demos + a deployed x402 endpoint beats a resume.
- **MCP server + A2A protocol experience** — directly relevant to agent-interoperability roles (QuickNode, agent marketplaces).

**Caveats (Sep 8 research):**
- OpenAI/Anthropic agent-infra roles are hybrid/onsite (SF/NYC/London) + W-2 → screen out per remote directive.
- Crypto/DeFi agent platforms (Olas, Giza, Griffain, Kite, Amadeus) are the MOST individual-friendly: many hire contractors, pay in crypto, remote-first — no C-corp needed to start (a US LLC helps for invoicing/tax).
- Mercor + similar hourly-contract agent-infra gigs are genuinely individual-friendly (no incorporation) + remote — best near-term fit for an unincorporated solo builder.
- Binance agent roles are remote but APAC-timed + often internship/accelerator — check timezone fit.
- No C-corp required for any W-2 or contract role; incorporation only matters if selling GenTech services as a business or taking equity-heavy startup comp.
- Many crypto agent-platform roles are early-stage, may pay partially in tokens/equity — evaluate total comp.
- Remote AI engineering is one of the most remote-friendly fields (52%+ remote-first) — the remote filter is not a constraint for most of these.

Full reference: `09-Green Room/job-apps/ai-agent-infrastructure-jobs-reference.md`

### 2. DeFi Protocol Teams
Protocols building LP automation, yield optimization, cross-chain agents, or DeFi dashboards.
- **Why:** Our Compound vs Extract protocol, regime detector, and LP monitoring are production-grade.
- **Search terms:** "DeFi engineer", "smart contract developer", "protocol engineer", "yield strategy", "LP automation"
- **Target ecosystems:** Avalanche, Solana, Base, Arbitrum, Sui

### 3. Web3 Startups (Early Stage)
Seed/Series A companies where being a founder is an asset, not a liability.
- **Why:** Early-stage teams value builders who ship. Our hackathon velocity = signal.
- **Search terms:** "founding engineer", "first engineer", "blockchain developer", "web3 startup"
- **Platforms:** wellfound.com, YC Work at a Startup, AngelList, crypto.jobs

### 4. Hackathons + Grants

**Active grant programs:** `references/active-grants-july-2026.md`

| Grant | Amount | Status |
|------|--------|--------|
| Circle Developer Grant | Milestone USDC (up to $100k) | **Open** — agentic AI focus, Questbook portal |
| Avalanche Team1 Builder Grants | $10k Mini / $30k Accelerator | **Open** — launched Jul 1, 2026 |
| Tether Developer Grants | Task-based USD₮/BTC | **Open** — local-first AI, wallet infra |
| GOAT Network AI Builder Grants | **$1M pool** | **Opens Jul 17** — x402 infrastructure focus |
| Stacks DeGrants | $3–5k | Deadline Jul 26 |

Competitive events and non-dilutive funding aligned with our stack.
- **Why:** Hackathons fund development AND build portfolio. Grants fund operations.
- **Search terms:** "AI agent hackathon 2026", "DeFi grant", "Solana hackathon", "Base ecosystem grant", "GOAT builder program"
- **Platforms:** Devpost, DoraHacks, Colosseum, ETHGlobal, MLH

### 5. Agent Marketplaces
Platforms where we deploy skills/agents for revenue.
- **Why:** Passive income while we build. Skills shippable to Hive, EvoMap, skills.sh.
- **Platforms:** Hive (uphive.xyz), EvoMap (evomap.ai), WURK.fun, skills.sh

## Search Strategy

### Primary Sources (most reliable)
| Source | Focus | Method |
|--------|-------|--------|
| web3.career | Remote web3 jobs | Browser extraction (use console JS for table scraping) |
| jobs.lever.co/binance | Binance roles | Browser extraction — renders full job descriptions cleanly; preferred over binance.com/careers (JS-heavy SPA that doesn't render) |
| jobs.solana.com | Solana ecosystem jobs | Browser extraction |
| crypto.jobs | Crypto-native roles | Browser extraction |
| Remotive.com | AI/ML remote roles | Browser extraction |
| sailonchain.com | Entry-level crypto | Browser extraction |
| Devpost | Hackathons | web_search |
| DoraHacks | Hackathons + grants | web_search |
| Colosseum | Solana hackathons | web_search + browser (colosseum.org/hackathon) |
| lablab.ai | AI agent hackathons | web_search (lablab.ai/ai-hackathons) |
| **himalayas.app** | Agentic AI / LLM jobs | **Sitemap bypass (Cloudflare-blocked pages)**: `curl -sL "https://himalayas.app/sitemap-jobs.xml.gz"` → index → fetch `sitemap-jobs{1,2,3}.xml.gz` → `gunzip` → parse `<loc>` URLs. ~110K jobs, filter by agent/agentic/llm/mcp in slug, then exclude noise (real-estate, call-center, sales-agent, 1099, insurance, freight, collections). Detail pages are Cloudflare-walled — verify via web_search of the exact title instead. **Binance caveat: ALL Binance AI/agent roles are Asia/HK/TW-based → hard reject per Jordan's filter.** |
| **Agentscan** | **Agent economy opportunities** | **REST API (`/api/agents`) — discover active agents, find integration partners, track ERC-8004 registrations. Also `/api/agents?page_size=5` for latest agents. Ecosystem data at `/ecosystems` page.** |

### Secondary Sources (discovery only)
| Source | Focus | Method |
|--------|-------|--------|
| wellfound.com | Startup jobs | web_search snippets (CAPTCHA-blocked) |
| LinkedIn | Discovery only | web_search |
| cryptojobslist.com | Crypto jobs | web_search snippets (Cloudflare-blocked) |
| ETHGlobal | Ethereum hackathons | web_search only (Cloudflare-blocked for browser) |

### Extraction Technique: Browser Console JS
When job board pages render structured tables, use `browser_console` with JavaScript to extract batch data instead of parsing snapshots:
```javascript
const rows = document.querySelectorAll('table tr');
const jobs = [];
rows.forEach((row, i) => {
  if (i === 0) return; // skip header
  const titleEl = row.querySelector('a');
  const title = titleEl?.textContent?.trim() || '';
  const url = titleEl?.href || '';
  if (title) jobs.push({ title, url });
});
JSON.stringify(jobs, null, 2);
```
Works well on: web3.career (table rows), jobs.lever.co (listing cards). Use when snapshots are truncated or you need batch data.

### Search Queries (rotate these)
```
"AI agent engineer" remote 2026
"DeFi protocol engineer" remote hiring
"smart contract developer" entry level 2026
"web3 founding engineer" startup
"agent infrastructure" hiring
"MCP developer" remote
"Solana developer" hiring 2026
"AI agent hackathon" 2026
"DeFi grant" application open
Binance "Pioneer Talent Program" OR "Tech Seeds" AI agent 2026
Binance "Accelerator Program" blockchain security remote
Binance "AI Agent" site:jobs.lever.co/binance
Colosseum hackathon 2026 schedule registration
lablab.ai AI agent hackathon 2026
```

### Agent Economy Discovery (Agentscan)
```bash
# Discover active agents for partnership/integration
curl "https://agentscan.info/api/agents?page=1&page_size=10&sort=reputation_score"
# Find agents by skill/domain
curl "https://agentscan.info/api/agents?skills=risk-scoring&domains=defi"
# Track ERC-8004 ecosystem growth
curl "https://agentscan.info/api/stats"
```

## CRITICAL: AGENT/ORCHESTRATOR-FRIENDLY FILTER — MANDATORY (added Jul 31, 2026)

Jordan's rule after a failed job interview (they quizzed him on traditional JS university skills instead of agent work): **the opportunity must be winnable with agent + orchestrator skills, not traditional human-only skills.**

**A role/opportunity is AGENT-FRIENDLY if ANY of these are true:**
- ✅ The work product is code, API, smart contract, content, or data output that an agent can produce/verify (not in-person interviews, whiteboard exams, or human-credential checks)
- ✅ The company explicitly values AI-agent workflows, automation, MCP, or agent orchestration in the role description
- ✅ It's a marketplace/microtask/grant where we submit deliverables (Hive, WURK.fun, EvoMap, skills.sh, hackathon submissions) — we can ship with agents
- ✅ The interview/selection process evaluates shipped work (portfolio, repo, demo) over trivia
- ✅ Early-stage/founder-friendly: they want builders who ship with tooling

**REJECT if the process demands traditional human-only credentials:**
- ❌ University-style technical exams/whiteboard interviews (the failed JS role pattern)
- ❌ "X years of professional experience in a specific stack" as the primary filter
- ❌ Roles where the interview tests textbook knowledge instead of shipped artifacts
- ❌ In-person interview loops that can't be done asynchronously
- ❌ Certifications/degrees required as hard gate

**When evaluating each opportunity, explicitly state:** "Agent-friendly: ✅/❌ — [one-line reason]". If ❌, SKIP it even if everything else matches.

## CRITICAL: RECENCY FILTER — STRICTLY ENFORCED

**Only deliver opportunities posted within the last 30 days.** Anything older than 30 days = SKIP, no exceptions.

**How to check recency:**
- Job boards: look for a "Posted X days/weeks ago" label, date stamp, or "Closing date" field
- Hackathons: check the actual start/end dates on Devpost, DoraHacks, or event page
- Grants: look for application window dates
- **If you cannot find a date, SKIP it.** No date = not recent enough to confidently recommend
- **If a posting says "Posted X weeks ago" and X ≥ 4, SKIP it**
- **If a listing shows only a year (e.g. "2026") without month, SKIP it**
- **Date verification comes before any other filter.** Check recency first before evaluating fit.

## Filtering Rules

### MUST BE (all must be true)
- ✅ Fully remote (no hybrid, no in-person)
- ✅ **Two-tier location rule (Jordan's policy, Jul 31 2026):**
  - **Tier 1 (preferred):** Worldwide / anywhere remote — work from any country. ⭐⭐⭐⭐⭐
  - **Tier 2 (acceptable fallback):** US-only remote — only if Tier 1 yields nothing. ⭐⭐⭐⭐ (flag the US work-authorization requirement in the report)
  - ❌ REJECT Canada-only (Jordan cannot relocate to Canada), REJECT Asia/HK/TW-only (Binance pattern), REJECT any other country-locked remote that isn't US
- ✅ Crypto/web3/AI company (not TradFi, not enterprise)
- ✅ Entry-to-mid level (no "5+ years" requirement)
- ✅ Currently accepting applications
- ✅ Posted within the last 30 days

### REJECT immediately
- ❌ Any posting older than 30 days (or no date visible = SKIP)
- ❌ Deadlines less than 5 days away — "too close to enter" (Jordan's rule). Unless the task is already complete and just needs submission.
- ❌ "3+ years professional experience" required
- ❌ Hybrid or in-person
- ❌ Asia-based companies (even if they say "remote")
- ❌ Non-crypto companies
- ❌ Expired listings

### Scoring (only deliver 4-5 stars)
- ⭐⭐⭐⭐⭐ = Agent + blockchain + DeFi + remote + entry-level + posted < 14 days ago
- ⭐⭐⭐⭐ = Strong match (4/5 criteria, good growth potential, posted < 30 days)
- ⭐⭐⭐ or below = SKIP (don't deliver)

**Any result that can't be date-verified becomes a ⭐⭐⭐ SKIP automatically.**

## Output Format

```markdown
# 🎯 Opportunity Scan — [Date]

## Executive Summary
[X] opportunities found. [Y] are 4-5 star matches.

## 🏆 Top Picks

### 1. [Company] — [Role]
- **Why it fits:** [1 line]
- **Stack match:** [technologies]
- **Remote:** ✅ Fully remote
- **Apply:** [link]
- **Fit score:** ⭐⭐⭐⭐⭐

## 🔍 Also Worth Looking
[3-5 runner-ups with brief notes]

## 📊 Sources Scanned
[List of platforms checked]

## ⏭️ Filtered Out
[1-liner per rejected opportunity + reason]
```

## Agent Kit Template Variables

Customize these when setting up the cron:
- `{schedule}` — How often to scan (recommended: weekly, Tuesdays 10 AM ET)
- `{deliver_to}` — Where to send results (chat ID or local)
- `{focus_areas}` — Comma-separated topics (e.g., "DeFi,AI agents,Solana")
- `{min_score}` — Minimum star rating to deliver (default: 4)
- `{exclusion_list}` — Things to skip (already tracking, applied, etc.)

## Cron Prompt Template

```
You are running the Opportunity Scanner for web3/AI agent roles.

**Focus areas:** {focus_areas}
**Minimum score:** {min_score} stars
**Exclusion list:** {exclusion_list}

**Search these sources:**
1. web3.career — extract remote AI/blockchain roles
2. crypto.jobs — scan for entry-level web3 positions
3. Remotive.com — AI/ML remote roles at crypto companies
4. web_search — "AI agent engineer remote 2026", "DeFi protocol developer hiring"
5. web_search — "AI agent hackathon 2026", "DeFi grant application"

**Filter rules:**
- FULLY REMOTE only (no hybrid, no in-person)
- Crypto/web3/AI companies only
- Entry-to-mid level (reject "5+ years")
- Currently accepting applications
- Score 4-5 stars only

**Output:** Structured report with Top Picks, Also Worth Looking, Sources Scanned, Filtered Out.
```

## Mandatory Validation Rules (ENFORCED ON EVERY SCAN)

**Before recommending ANY job, verify all three:**

1. **Is the job still active?** — Check posting date, look for "closed" or "expired" indicators. If the link 404s or the listing says "no longer accepting applications", SKIP IT. Don't recommend dead listings.
2. **Does "remote" actually mean remote?** — Some companies say "remote" but require Asia-based (China, Taiwan, India timezone overlap). If the company is primarily Asia-based or the listing mentions specific Asian time zones, SKIP IT even if it says "remote".
3. **Is the source site up?** — web3.career may be down for maintenance. If a site returns errors, note it in the report and skip — don't retry endlessly.

**Jordan's rejection filters (hard blocks):**
- Asia-based companies (even if they say "remote")
- 5+ years experience required
- Senior-level positions
- Full-stack React/Postgres heavy roles
- Java/C++ only roles

## Pitfalls
1. **CAPTCHA blocks on wellfound/cryptojobslist/ETHGlobal** — use web_search snippets only, don't burn browser retries. ETHGlobal events pages are Cloudflare-blocked; search for event details via web_search instead.
2. **Stale listings** — always verify the listing is still live before recommending. RemoteOK shows "CLOSED" status on filled roles; check for this. Some boards keep expired listings visible — always click through to confirm.
3. **"Remote" lie** — some listings say remote but require specific timezone overlap, quarterly on-site, or are actually Asia-based. Flag these. **ALWAYS verify the actual location field on the job page** — not just the description text. Check the location tag, company HQ, and timezone requirements.
4. **Traditional job mindset** — we're founders, not employees. Lead with what we BUILD, not what we studied.
5. **Credit waste** — use web_search (free) before paid APIs. Only use BlockRun/Exa when web_search fails.
6. **Binance portal routing** — Binance.com/careers is a JS-heavy SPA that doesn't render via browser tools. Always use jobs.lever.co/binance instead — it renders full job descriptions cleanly. Search Lever page with console JS: `document.querySelectorAll('a[href*="/binance/"]')` filtered by title keywords.
7. **Binance eligibility** — "Accelerator Program" roles require "Current University students and recent Graduates" with 6-month commitment. "Pioneer Talent Program" accepts up to 5 years experience. Both are remote. Check which program fits the candidate's career stage.
8. **Hackathon timing** — Colosseum runs two hackathons per year: Spring (Apr-May) and Fall (Sep-Nov). Colosseum Fall 2026 "Cypherpunk" runs Sep 25 – Nov 2. $500k+ prize pool. Register early at colosseum.org/hackathon. ETHGlobal NYC typically in June. LabLab runs continuous AI agent hackathons — Fall 2026 Dubai edition TBA with $60k+ pool.
9. **Grant programs are rolling** — Solana Foundation grants have no fixed deadline. Submit early in the quarter for better visibility. Coreum grants run in waves — check which wave is active.
10. **web_extract requires non-DuckDuckGo backend** — `web_extract` fails with "DuckDuckGo (ddgs) is a search-only backend" when trying to fetch non-text URLs. For extracting job descriptions from Lever/LinkedIn/etc., use `browser_navigate` + `browser_console` with JavaScript extraction instead. This is the reliable path for structured job board data.
11. **Binance Tech Seeds 2026 is a goldmine** — The Pioneer Talent Program (up to 5 yrs exp) and Accelerator Program (intern/recent grad) both have AI Agent Developer and AI Application Engineer roles. These are the highest-signal matches for agent-focused candidates. Apply to both Pioneer Talent tracks immediately — they're engineering-first roles building production agent systems, not demos.
