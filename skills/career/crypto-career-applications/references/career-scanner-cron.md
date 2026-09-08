# Career Scanner Cron — Pattern Reference

## Job ID
`459c861626a9`

## Schedule
Every Tuesday at 10 AM ET (`0 10 * * 2`)

## Manual Trigger
Jordan can request a career scan at any time. When he says "run the career scanner" or "look for jobs":
1. Don't wait for Tuesday — run immediately
2. Use the same search strategy and scoring criteria
3. Save results to vault: `Labs/Hackathons/career-scan-YYYY-MM-DD.md`
4. Deliver top matches (4-5 stars) to Jordan
5. Include application deadline urgency in the report

## Delivery
Telegram HQ (`-1003863540828`)

## Design Principle: "Silent When Nothing Found"
The scanner only delivers results if it finds genuine 4-5 star matches. If nothing meets the quality threshold, it sends nothing. This prevents spam and ensures Jordan only sees roles worth his time.

**Why this matters:** Most job scanners spam daily with low-quality matches. Jordan explicitly said "if none exist, keep quiet." The silence IS the signal — it means the market doesn't have what we're looking for this week.

## Search Sources

### Source Reliability (verified May-June 2026)

| Source | Reliability | Notes |
|--------|-------------|-------|
| `web3.career` | ★★★★★ | Most reliable. Structured data, recent postings, accessible via browser. 780+ remote AI jobs. |
| `Remotive.com` | ★★★★ | Good for AI/ML remote roles at crypto companies. Clean listings. |
| `crypto.jobs` | ★★★ | Large volume (3500+), but listing quality varies. Use for discovery, verify recency. |
| `cryptojobslist.com` | ★☆☆☆ | **BLOCKED** — aggressive Cloudflare bot detection. Cannot access via browser tools. Skip. |
| `workatastartup.com` | ★★☆☆ | YC company listings. URLs decay after ~3 months (404). Treat as unreliable for older postings. |
| `LinkedIn` | ★★★ | Use for discovery only. Apply via company career pages. |

### Tool Workarounds (discovered May-Jun 2026)

- **`web_extract` does NOT work** with DuckDuckGo backend (search-only). Use `browser_navigate` + `browser_snapshot` for page content extraction from job listings.
- **`cryptojobslist.com` is blocked** — Cloudflare challenge cannot be bypassed with stealth mode. Rely on web3.career and Remotive instead.
- **Use `browser_console` with JS selectors** to extract structured table data from job boards when snapshots are truncated. Example: `document.querySelectorAll('table tr')` to get rows.
- **YC Work at a Startup** job URLs frequently 404 after a few months. Always verify the listing is still live before including in results.
- **web3.career page structure**: Job listings are in `<table>` rows. Each row has: title (h2), company (h4), salary, location, tags, posting date (time element).
- **`web_search` timeouts (Jun 2026):** Parallel search backend sometimes times out on complex queries. Fallback strategy:
  1. Try simpler query: `"web3.career AI agent remote"` instead of `site:web3.career AI agent remote 2026`
  2. If web_search fails 3x, switch to `web_extract` on known URLs: `https://web3.career/remote+AI+agent+jobs`, `https://remotive.com/remote-crypto-jobs`
  3. For Binance roles: search `himalayas.app/companies/binance/jobs/` directly
  4. Don't block on search failures — extract from known job boards instead

### Recommended Search Strategy

1. Start with `web3.career` — filter by `ai+remote-jobs` or `entry-level+remote-jobs`
2. Check `Remotive.com` for AI/ML roles at crypto companies
3. Search `crypto.jobs` for discovery (large volume)
4. Search LinkedIn for "AI agent developer remote crypto" for additional leads
5. For each lead, navigate to the job page via browser to extract full details
6. Verify recency: check the `<time>` element — if >3 months old, likely filled

## Match Criteria (ALL must be true)
1. **100% REMOTE — work from anywhere in the world** (not hybrid, not remote-US-only, not remote-with-travel-restrictions, not "remote with quarterly on-site"). Jordan travels full-time (Thailand, Philippines). Fully distributed, async-friendly teams ONLY.
2. No "3+ years experience" requirement (entry-to-mid level)
3. Matches Jordan's tech stack (Solidity, Python, agents, DeFi)
4. At crypto/web3/AI companies (not TradFi, not enterprise)
5. Currently accepting applications (not expired)

**Critical: Verify recency.** Many listings on job boards are months old and likely filled. Always check the posting date. If >3 months old, exclude from results unless confirmed active.

## Scoring
- ★★★★★ = Perfect match (agent + blockchain + DeFi + remote + entry-level)
- ★★★★☆ = Strong match (4/5 criteria met, good growth potential)
- ≤★★★☆☆ = Skip (don't deliver)

## Target Roles
- AI Agent Engineer / Developer
- Smart Contract Developer
- DeFi Protocol Engineer
- AI Systems Automation Engineer
- AI/ML Platform Engineer (agent focus)
- Blockchain Developer (agent economy)

## Jordan's Skill Stack (for matching)
- Multi-agent orchestration (Hermes, agent-to-agent commerce)
- Smart contracts (Solidity, deployed on Avalanche/Somnia/Base)
- DeFi integration (x402, LP monitoring, yield optimization, AgentEscrow)
- Agent infrastructure (ERC-8004, ERC-8226/RAMS, identity + compliance)
- Python automation (data pipelines, API integrations, cron systems)
- Blockchain development (EVM, Solana, multi-chain)
- Bot/Telegram development (multi-agent voice, dashboards)

## Market Intelligence (June 2026)

- AI agent hiring is real but **heavily skewed senior** (Principal/Staff at OKX, Zscaler). Entry-level AI agent roles are rare.
- The "AI Agent Engineer" title is now standard at major exchanges (Binance, OKX) — validates Jordan's positioning.
- **Binance Pioneer Talent Program (Tech Seeds 2026)** is a standout for entry-level:
  - 0-3 years experience, remote Asia (HK, SG, TW, UAE)
  - Python/Java, AI agents, LLMs, production systems
  - Deadline: June 22, 2026 — apply ASAP
  - Apply: https://himalayas.app/companies/binance/jobs/pioneer-talent-program-ai-agent-developer
- Most crypto AI roles require Python + LLM experience — Jordan's Python automation stack is directly relevant.
- "Hackathon experience" listed as bonus on multiple listings — frame concurrent hackathon participation as a strength.
- Remote-first is now the default in Web3 (78% of blockchain jobs per crypto.jobs report).

## Output Format

The scanner should produce a structured report with:
1. **Top Matches (4-5 stars)** — Company, Role, Pay, Remote status, Why it matches, Apply link
2. **Noted but Not Delivered** — Table of roles that were found but didn't meet criteria (too senior, too old, wrong stack)
3. **Market Signals** — Brief observations about the job market this week
4. **Recommendation** — Which role to apply to first and why

## Related Skills
- `career-application-execution` — drafting and submitting applications
- `crypto-career-applications` — portfolio-first application strategy
