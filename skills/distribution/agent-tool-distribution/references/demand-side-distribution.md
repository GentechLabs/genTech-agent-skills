# Demand-Side API Distribution — Where Buyers Actually Spend (Aug 20, 2026)

Jordan's standing correction: **stop listing on empty supply directories; go
where the DEMAND is.** Listing on x402-list, the402.dev, 8004scan, AgentLux,
APIHub, RelAI, Toku, dealwork earned $0 — all sellers, no buyers.

## The two channels that beat all the empty directories

### 1. Your OWN gateway's buyer-facing `skill.md` (PRIMARY, deployed Aug 20)
A one-file integration an agent `set up`s to discover + pay + call our APIs
over x402. Modeled on Syra (`https://api.syraa.fun/skill.md`).

**Our live version:** `https://api.gentechlabs.net/skill.md` (HTTP 200,
text/markdown). Content mirrors Syra's shape: name/version/description frontmatter
+ "set up <url>/skill.md" one-liner + service catalog table + payment rails +
"how to drive" (402 → sign → retry → answer) + discovery links.

**Discovery endpoints our gateway serves** (all verified live):
- `/.well-known/x402` (200) — well-known protocol endpoint
- `/.well-known/x402-bazaar` (200) — bazaar manifest, 11 services, 5+ networks
- `/openapi.json` (200) — full API spec
- `/docs` (200) — human-readable docs
- `/health` → `{"status":"ok","gateway":"x402-v2","services":11}`

**Real 402 prices verified (Base USDC, treasury 0xF9dc...e734):**
- market_intelligence `/v1/market/price/{sym}` = $0.005 (amount 5000)
- token_security `/v1/security/score/{addr}` = $0.01 (amount 10000)
- agent_research `/v1/agent/research` = $0.01 (amount 10000)

### 2. Apify Store — the one marketplace with real paying agents
20,000+ Actors x402-payable (10x jump Jun 30 2026, with Coinbase). $1.4M/mo
paid to Actor devs. Agents buy web data/automation with USDC on Base, no key.
Examples: ~380 Instagram profiles / ~250 Google Maps / ~2,500 X posts for $1.
Not yet listed (needs Apify account + Docker Actor packaging) — flagged
"NEEDS HUMAN" Aug 14, never actioned. This is the highest-leverage unlisted
demand channel.

## Market context (from live research, Aug 20)
- x402: 195M+ txs, $52.4M settled, 844K unique buyers (x402scan via AgentCash).
- Real per-call prices run from fractions of a cent to ~$1 (CoinGecko $0.01,
  IPinfo $0.006, Groq $0.50-1.00).
- Top providers all ship `llms.txt`/`llms-full.txt` at root (Syra, AgentCash,
  Hansa) so search engines + LLM crawlers index their catalog. **We don't yet —
  this is the concrete remaining gap.**

## The nginx deployment gotcha (VPS-specific, cost ~15 min to debug)
`/etc/nginx/sites-enabled/gentech` is a **standalone file, NOT a symlink** to
`sites-available/gentech`. Editing sites-available alone leaves the live config
unchanged — the gateway proxies `/skill.md` and returns 404. You MUST edit the
file under `sites-enabled/` directly (back it up first), add a
`location = /skill.md` static block to BOTH the 80 and 443 server blocks for
`api.gentechlabs.net`, then `nginx -t` + `systemctl reload nginx`.
Verify with `grep -c "skill.md" /etc/nginx/sites-enabled/gentech` and a curl
content-type check.
