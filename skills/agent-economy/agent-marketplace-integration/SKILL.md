---
name: agent-marketplace-integration
description: Systematic research, positioning, and integration for AI agent marketplaces. Greenfield opportunity identification, competitive analysis, technical integration, and revenue strategy for emerging agent commerce platforms.

---

# Agent Marketplace Integration

## Trigger Conditions
- User shares a new AI agent marketplace link (Twitter/X, docs, or platform)
- Discussion about listing agents for sale/hire on a platform
- Interest in agent-to-agent commerce, escrow payments, or agent reputation
- Questions about OKX.AI, AgentGPT, or similar platforms

---

## Core Principle: Greenfield Advantage

**First movers establish reputation before competition arrives**. Most agent marketplaces are in early beta (1K-10K transactions total). Early entrants get:
- Reputation advantage (high ratings, sales history)
- Category dominance (first in niche = default choice)
- Price setting power (no established benchmarks)
- Feedback loop advantage (learn from real users early)

---

## Research Framework

### 1. Market State Assessment
- **Volume metrics**: Total transactions, active agents, task completion rate
- **Pricing patterns**: What are agents charging? (often 0.01-10 USDT in early stages)
- **Category saturation**: Which verticals are crowded? Which are empty?
- **Technical barriers**: Installation complexity, SDK requirements, chain support

### 2. Competitive Analysis
- **What exists**: List agents in target category with ratings, sales, pricing
- **Gaps identification**: Services no one offers yet
- **Differentiation points**: Our advantages vs existing providers

### 3. Technical Stack Evaluation
- **Installation requirements**: npm packages, SDKs, wallet setup
- **Payment modes**: Instant pay-per-call, escrow, subscriptions
- **Chain support**: EVM-only, Solana, cross-chain
- **Agent compatibility**: Does it work with Hermes? Claude Code? Codex?

---

## Integration Strategy: 3-Phase Rollout

### Phase 1: Provider Registration (Week 1)
- Install platform's skill/package in agent environment
- Create platform-specific wallet/identity if required
- Register as ASP (Agent Service Provider)
- Prepare agent descriptions, pricing, and examples

### Phase 2: First Agents Live (Week 2)
- List 3 core agents in distinct categories
- Mix payment modes: simple → instant, complex → escrow
- Test end-to-end payment flows
- Monitor initial sales and feedback

### Phase 3: Optimization & Expansion (Week 3+)
- Track reputation growth and adjust pricing
- Add more agents based on demand signals
- Optimize descriptions and examples based on user questions
- Consider cross-platform integration if multiple marketplaces emerge

---

## Agent Selection Criteria

**Ideal first agents**:
1. ✅ **Live and proven** — already working in production
2. ✅ **Distinct value prop** — something no one else offers
3. ✅ **Clear pricing model** — pay-per-call OR subscription OR performance
4. ✅ **Low integration friction** — works with platform's payment rails
5. ✅ **Continuous value** — ongoing service, not one-off information dump

**Examples from Gentech context**:
- LP Shape Detector (unique DeFi analysis)
- DCA Rebalancing Agent (continuous value)
- Cross-chain Yield Scanner (multi-chain advantage)

---

## Competitive Positioning Playbook

| Dimension | Most Agents | Gentech Play |
|---|---|---|
| Service type | One-off information (report) | Continuous value (ongoing service) |
| Payment rails | Platform SDK only | Multi-protocol (x402 + Q402 + platform) |
| Chain support | EVM-only | EVM + Solana bridge |
| Escrow | Coming or missing | ✅ Ready (Q402, platform-native) |
| Reputation | New or none | 100M+ payment track record |
| Support | Basic | Premium (examples, updates, customization) |

**Key message**: We don't just sell information — we sell outcomes that compound over time.

---

## The first real x402 settlement is the traction unlock (Aug 2026)

Several of the highest-value x402 marketplaces list **only via a real on-chain settlement** —
there is NO registration form. This makes the first settled x402 payment the single
highest-leverage marketplace action: one real payment through a settlement-gated facilitator
auto-registers us on **multiple** marketplaces at once, because they crawl the settlement
event. It is also the traction proof Jordan wants to show employers ("people are using our
rails").

**Settlement-gated (no form — get a real payment to settle):**
- **Agentic.Market (Coinbase Bazaar)** — auto-indexes when the CDP facilitator settles a payment. NOT-LISTED with zero settlements is *expected*; the action item is "get the first settled payment."
- **OpenDexter** — auto-catalogs any API that receives a real settled payment through its facilitator, then you claim the resource. Testnet USDC does NOT trigger it — must be real mainnet USDC (~$1 is enough).

**Autonomous registration (agent can do it, no human login):**
- **AgentLux** — **BEST autonomous rail (proven Aug 12, 2026).** Free challenge-sign auth (no API key, no signup), free identity + first quality service listing, and a **First-Hire Guarantee** (platform funds one escrowed hire within 24h, paid in USDC). Full flow: `references/agentlux-autonomous-onboarding.md`. **⚠️ TIER CORRECTION (Aug 14, 2026): the First-Hire Guarantee is restricted to OFFICIAL fleet accounts** — `GET /v1/services/first-hire-guarantee/queue` returns `FORBIDDEN: First-Hire Guarantee queue is restricted to official AgentLux fleet accounts`. Our agent is a **registered third-party provider**, so the 24h platform-funded hire NEVER fires. Do NOT keep a "First-Hire Watch" cron expecting a guarantee that won't trigger for our account class — that's noise. Rely on organic demand after fixing the public listing (below).
- **APIHub** — x402/USDC-on-Base, wallet-sign challenge → `ahk_` key. CLI `npx @apihubio/cli add <url>`. Verified Aug 13.
- **RelAI** — multi-chain x402, wallet-sign → `sk_live_` key. ⚠️ `POST /v1/apis` rate-limited 10/day/IP. Verified Aug 13.
- **Toku** — real USD payouts (Stripe), `POST /api/agents/register` + `POST /api/services`. FIXED pricing only. Verified Aug 13.
- **dealwork.ai** — hybrid human+AI work marketplace, `POST /api/v1/agents/onboard {autonomous:true, identityKey}`. Bid-on-jobs (no service listing). Verified Aug 13.
- **Syra** — email `support@syraa.fun` with service fields (Jordan said GO)
- **BotWork** — `npx botwork init` (TS SDK, MIT) to list an agent
- **Freelance AI / PayAI** — reuses the WURK facilitator we already use; register as seller

> **Full verified flows for the four Aug 13 registrations:** `references/autonomous-marketplace-registrations-aug-2026.md` — exact endpoints, request bodies, rate limits, and the reusable wallet-sign challenge-response pattern.

**Human-login required (agent CANNOT do it — hand Jordan a one-pass checklist):**
- **Swarms** — stale listing, needs swarms.world login
- **Atelier** — add new services, needs useatelier.ai login

**Rule of thumb:** when a marketplace needs an account login or wallet signature we don't have
programmatic access to, split the work — the agent stages what it can (endpoint verified,
manifest correct, submission drafted) and gives Jordan an exact one-pass action list, rather
than blocking everything on the human. The settlement-gated marketplaces, by contrast, only
need a funded mainnet wallet + one real payment — which is the funding, not an application.

## Wire every live rail into the Revenue Monitor (Aug 12, 2026)

**Onboarding a marketplace is NOT done when the listing is live — it's done when the Revenue Monitor ("crown job", `revenue-monitor.py`, runs 8am/8pm) polls it.** Jordan's directive: the crown job must pick up the marketplaces we put ourselves on. Otherwise you list on a rail and nobody ever tracks whether it earned.

### 🔴 Design rule (Jordan, Aug 12) — REVENUE JOB, not a status board

The Revenue Monitor records **income from jobs** — pending hires to accept, settled payouts, USDC received. It does **NOT** track marketplace status/health (which platforms we're listed on, whether a platform is frozen/broken, who's waiting on a key). Status lives in the marketplace registry + the scanner cron, NEVER in the revenue report.

**Wrong pattern (added then removed):** polling every marketplace for a `status` line (AgentLux `no_hire_yet`, Nevermined `needs_key`, Agoragentic `frozen`, BountyBook `parked`, BotWork `with_labs`) and printing a `🛒 Marketplace Income` block of per-platform status rows with status-emoji. Jordan: *"it's supposed to record the income from the jobs, not the places itself."*

**Correct pattern — only surface REAL money events in `get_marketplace_income()`:**
- A pending hire/offer worth a dollar amount → surface it ("🟢 X pending hire(s) worth ~$N — ACCEPT + deliver")
- A settled payout → already covered by the on-chain USDC scan (count it there, don't duplicate)
- No money event → emit ONE quiet line ("no pending hires/payouts") or nothing — do NOT fill the report with per-platform status rows.
- **Best-effort still applies:** wrap each poll in try/except so a failure never breaks the report.
- Rule of thumb: if a line does not represent money owed or money received, it does not belong in the revenue report. Keep it income-only.
- Keep the dedicated 6h `AgentLux First-Hire Watch` cron as the fast catcher; the revenue monitor just logs income. Overlap is fine (cron catches it fast, revenue monitor keeps the ledger) — only drop the monitor check if reports get noisy.

**Pitfall — vault sync divergence:** after editing `revenue-monitor.py` in the profile scripts dir, sync it to the vault (`cp` into `10-Labs/`) and commit. The vault repo can diverge from remote (other agents like Vanito push music/asset files); before a `git pull`, `git status` will show untracked local files (e.g. `music/vanito/*`) that a merge would overwrite — back them up to a temp dir, merge, push, then restore with `cp -n`. Don't force-push.

## Messaging grantors/investors — verify live state BEFORE drafting (Aug 13, 2026)

When a funding partner (grantor, incubator, investor) checks in and Jordan wants to reply with a
project-status update, **verify the claimed state against live on-chain/source data FIRST and
refuse to let him overstate if it isn't true.** Same honest-numbers discipline as the payout-rail
probe, applied to outbound comms.

**Concrete case:** Victus Global (OOBE/SAP partner, funded the Robinhood-Chain $TREASURY grant)
messaged "How is the project fairing?" The first reply draft said the Steward was "managing real
positions with real money." A live wallet check showed it was **empty** (0.2979 AVAX gas only,
0 USDC/WAVAX/LP — funds swept off Aug 11). Sending that draft would have misrepresented live state
to the grantor. Jordan then confirmed the sweep was intentional (a fund-return test — the treasury
proved it can send USDC back to the owner on command), which became the honest, compelling story.

**Workflow:**
1. **Before drafting, verify live state** — on-chain balances (`eth_getBalance`, `balanceOf`),
   active positions, cron job enabled/disabled state, endpoint HTTP status. The message must match reality.
2. **Separate "built & working" from "currently live."** Infrastructure can be complete and verified
   while the live deployment is paused/empty. State both honestly.
3. **If Jordan is about to overstate, flag it and give the truthful reframe** — don't just refuse.
   The honest story (e.g. "the treasury returned real USDC to the owner on command") often beats the
   overclaim.
4. **When Jordan has first-hand context the vault lacks** (e.g. "that move was intentional, I kept the
   funds"), incorporate it — the message becomes truthful once intent is confirmed.
5. **Verify every link you hand him** — HTTP 200 + content check (title/keywords) before sending.
   Confirm the live endpoint count matches the message (manifest says "15+", don't claim "16").
6. **Don't present disabled cron/automation as "live."** Describe the architecture as designed unless
   the jobs are actually enabled and firing.

Ready-to-send template: `references/grantor-project-status-update.md`.

## Marketplace Routing Rule (Jordan, Aug 12 2026) — MANDATORY for the income scanner

When the marketplace scanner finds a NEW marketplace, classify it by how much human help it
needs and ACT — don't just report:

1. **Fully autonomous (no human needed)** → GO LIST YOURSELF end-to-end right now. Register the
   agent, create the listing, wire the service. Free challenge-sign/wallet-sign auth, SDK
   registration, no email/GitHub login, no human API key. (AgentLux is the proven pattern —
   worked fully autonomously.)
2. **Needs human help (API key, email/GitHub login, wallet signature we can't do)** → DO NOT
   block. Stage everything you CAN (registration script, service list, builder address), then
   add the exact 3-5 steps to Jordan's action list (`01-HANDOFFS/<date>-jordan-items.md`).
   (Nevermined is the pattern — staged, just needs his API key.)
3. **Broken / frozen / never-paid** → Do NOT just park it. Find a way to CONTRIBUTE and help
   them fix it:
   - Has GitHub → open an issue/PR describing the bug (verify the repo is the REAL platform
     repo first — see pitfall below).
   - No GitHub → find the contact channel (Discord, X, email, Telegram) and draft a clear bug
     report Jordan can send.
   - Log the finding + contribution in the registry row.

**Pitfall — verify the GitHub repo is the actual platform before filing.** A search can surface
a *different* project with the same name (e.g. `The-Swarm-Corporation/agent-bazaar-implementation`
is a research-paper project, NOT the agentbazaar.dev platform; the SDK's `runningoffcode/agentbazaar`
is 404/private). Check the repo's `description`/`homepage` against the platform, and confirm the
SDK's `package.json` `repository` field. Filing into the wrong repo is noise and burns goodwill.

## Self-settling your own endpoint to trigger auto-indexing (Aug 2026)

**🔴 PROVEN ROOT CAUSE & FIX (Aug 19, 2026) — the settlement was NOT blocked on funding.** For months the registry blamed "wallet not funded / CDP indexing gap." A live diagnosis proved BOTH wrong:

1. **STALE GATEWAY PROCESS was the real killer.** The running `x402-api.service` process (started Aug 18) was executing an OLD `server.py` (deployed copy at `/root/repos/ProtoJay4789.github.io/10-Labs/x402-gateway/server.py`) that routed Base proofs through a **dead Dexter verify path** → every proof died `payment_proof_invalid / dexter unreachable`. The on-disk code in the service `WorkingDirectory` (`/root/vaults/gentech/10-Labs/x402-gateway/server.py`, edited Aug 19) had already removed Dexter and routes Base→CDP. **The fix was simply `systemctl restart x402-api.service`** to load the current code. **Rule: when the deployed code was edited, the running process is stale until restarted — verify the process start time + which server.py it loaded BEFORE debugging the protocol.** Check `ss -tlnp | grep 8090` → PID → `readlink /proc/PID/cwd` to find the ACTUAL loaded source; `grep -rl "dexter" <that file>` confirmed the stale path.
2. **Client base64 proof "not valid JSON" was a red herring.** The settle client's base64 proof parsed fine; the error was a response-handling artifact. Adding a temporary `logging.warning` in `verify_proof_via_cdp` showed `cdp returned valid=True reason='verified + settled'`. **Proof the settle landed (ground truth):** wallet Base USDC dropped 0.466002 → 0.451002 = **0.015 USDC settled on-chain**. On-chain balance delta is the only reliable success signal — the client's 200/payment-response header is not.

**Fix order when self-settle fails:** (1) confirm the running process loaded the current code (restart if edited since process start); (2) verify `PAYMENT_VERIFY_MODE=auto` + `CDP_API_KEY` present in the running process env (`/proc/PID/environ`); (3) add a debug log in the verify function to see the branch + actual reason; (4) confirm settlement via wallet USDC balance delta on Base RPC (`eth_call balanceOf`), not the client's status.

**The arb wallet IS funded (as of Aug 19):** `0x3d117Bf...ecB` holds ~0.45 USDC + gas on Base — enough for many settlements. The settle script at `/root/vaults/gentech/10-Labs/x402-gateway/cdp-settle/` now has `node_modules` installed (npm install) and fires with `EVM_PRIVATE_KEY=<pk> node cdp-settle.mjs`. After a settle, Agentic.Market indexing takes up to ~6h — verify by search, don't re-fire.

For settlement-gated marketplaces (Agentic.Market, OpenDexter), the unlock is **one real
on-chain x402 payment settling through the facilitator** — and you can fire it yourself by
paying your OWN endpoint with your own funded wallet. This is the "first settlement" traction
proof AND the auto-listing trigger in one action. The `cdp-settle.mjs` pattern (in
`10-Labs/x402-gateway/cdp-settle/`): use the vanilla `@x402/core` client + `ExactEvmScheme`
with your own EVM key (a Base wallet with a few USDC), `wrapFetchWithPayment` against your own
endpoint URL, expect 402 → paid → 200. ~$0.001-0.01 USDC is enough.

**The #1 blocker and fix — stale facilitator credentials in the running gateway.** If the
self-settle returns `payment_proof_invalid / facilitator returned 401: Unauthorized`, the
gateway process is almost certainly running with **stale CDP API credentials** (old
`CDP_API_KEY_ID`/`CDP_API_KEY_SECRET`), so the facilitator rejects its JWT. The `.env` may
have the correct keys but the running process was started before they were updated. **Fix:
restart the service** (`systemctl restart x402-api`) to load the current `.env` credentials,
then re-run the self-settle. Verify the fix by checking the new process env
(`cat /proc/<pid>/environ | grep CDP_API_KEY_ID`) matches the `.env`. **Diagnostic order:**
(1) confirm the gateway's `PAYMENT_VERIFY_MODE=cdp` (production, not simulation), (2) compare
the running process's CDP creds to the `.env`, (3) restart + re-settle. After a successful
settle, indexing takes **up to ~6h** — set a cron to verify the marketplace search returns your
resource, don't expect instant listing. The on-chain balance debit (raw RPC `balanceOf`) is the
ground-truth proof the settlement landed, since the facilitator may not return a tx hash.

**CRITICAL — an HTTP 200 from the self-settle is NOT proof of settlement (Aug 6, 2026).** The
`cdp-settle.mjs` script prints "✅ PAYMENT SETTLED" when it gets a `payment-response` header and a
200 — but that only means the facilitator *accepted* the payment at the HTTP layer. It does NOT
mean a settlement transaction was broadcast on-chain. Bazaar/Agentic.Market index on the
**settlement event**, not on the 200 response. A vault record that says "first settlement done"
can be wrong if no tx actually landed. **Always verify on-chain before declaring a settlement and
before expecting indexing:**
1. Check the payer/arb wallet's tx history for a tx on the claimed date — `base.blockscout.com/api/v2/addresses/<payer>/transactions` (last tx date must match the settlement date; a stale nonce means nothing settled).
2. Check the **seller/payTo wallet** for an incoming USDC transfer around that time — that's the actual settlement the facilitator should have broadcast.
3. Only then trust the "settlement done" record and set the ~6h indexing cron.
If the payer wallet's last on-chain tx predates the claimed settlement, the self-settle returned
200 but never broadcast — re-run it and watch for the tx to land. (Etherscan free tier returns
`NOTOK` for Base; use `base.blockscout.com` or raw RPC `eth_call balanceOf` instead.)

## Integration Reference: Bankr (bankr.bot)

**Bankr** is financial infrastructure for the agent economy on Base (Uniswap v4): agent wallets, a token launchpad, an LLM gateway, and **x402 Cloud**. $5.03B total volume, 71.6B LLM tokens served (Aug 2026). High-value distribution point for x402 services.

### Two entry paths (choose based on hosting)

| Path | Cost | What you get |
|---|---|---|
| **Skills marketplace** | Free (0%) | Publish a SKILL.md in a public GitHub repo → Bankr agents `install the <name> skill from <github URL>` → parsed, registered to wallet, discoverable. Agents then call your endpoints and pay via x402. |
| **x402 Cloud mirror** | 5% platform fee + their hosting | Deploy a thin mirror via `bankr x402 deploy` — auto-indexed in their discovery layer. Only needed if you want their hosting/auto-discovery; the skills path gets you into discovery free. |

**GenTech path (proven Aug 2, 2026):** published `gentech-x402-services` SKILL.md at `Gentech-Labs/genTech-agent-kit/master/skills/bankr/SKILL.md` (raw URL verified 200). Skills route preferred — 0% fee, keeps our own infra. Install command for agents: `install the gentech-x402-services skill from https://github.com/Gentech-Labs/genTech-agent-kit/tree/master/skills/bankr`.

### Pitfall — check PRIOR shipped work before declaring "NOT LISTED"
We already launched **$TREASURY via Bankr's token launchpad** on Jul 22 (contract `0x56D03C0f4167cC2c26B781dE47E608d660F13ba3`, 100B supply, Robinhood Chain) — but an Aug 2 registry pass marked Bankr "NOT LISTED yet" because it only looked at the x402/skill surface. **Before adding a marketplace as "NOT LISTED" in the registry, grep the vault git history + build queue for shipped items** (`git -C /root/vaults/gentech log --all --grep="<platform>"`, check `scripts/build_queue.json` status fields). A platform can be "listed" via one surface (token launch, agent identity) and unlisted via another (API skill) — record ALL surfaces in the registry row so the next pass doesn't re-discover the same thing.

### Compatibility check (before listing)
Bankr's clients are x402-native. Verify our 402 envelope matches what they expect: `accepts[0]` with `scheme: exact`, `network: eip155:8453`, USDC asset `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`, payTo, and EIP-712 `extra {name: "USD Coin", version: "2"}` — all present where the standard says. Bankr agents pay with `Authorization: x402 <proof>` — the standard flow.

### Skill file format (Bankr expects)
A directory containing `SKILL.md` with frontmatter (name, description, tags) + body teaching the agent: endpoints table (path, service, price), how to trigger the 402, how to sign EIP-3009, retry header, discovery URLs. Keep it self-contained — Bankr fetches the single file + companion references. See the GenTech example for the shape.

## Integration Reference: Circle Agent Marketplace (agents.circle.com)

**Circle** (USDC issuer) launched an agent marketplace at `agents.circle.com` with 41 services and 640 endpoints (Jul 2026).

### Market Stats (as of Jul 2026)
- **Total services:** 41 (direct + third-party)
- **Total endpoints:** 640
- **Pricing:** x402 nanopayments (USDC), $0.001-$0.05 per call
- **Chain:** Base mainnet (USDC), Robinhood Chain (USDG)
- **Featured providers:** BlockRun, CoinGecko, Exa, Perplexity, Alchemy, QuickNode, Google Maps, Twitter/X

### Seller Registration
- **Application form:** https://forms.gle/7YFzvdmMcn1JH5tF6 (Google sign-in required)
- **SDK:** `@circle-fin/x402-batching` with `createGatewayMiddleware` for Express
- **Docs:** https://developers.circle.com/gateway/nanopayments/quickstarts/seller
- **Settlement:** Batched via Gateway — settle thousands of payments in one on-chain tx

### Integration Pattern
```js
import { createGatewayMiddleware } from "@circle-fin/x402-batching/server";
const gateway = createGatewayMiddleware({ sellerAddress: "0xYOUR_WALLET" });
app.get("/api/data", gateway.require("$0.01"), handler);
// 402 unpaid → 200 paid. Circle settles.
```

### Competitive Gap
- 0 merchants on Base mainnet as of Jul 2026 — first-mover opportunity
- Our Agent Kit tools (CMC quotes, DeFi intel, token search) fit the data-service category directly

---

## Integration Reference: Nevermined (nevermined.app) — LIVE

**Nevermined** is a sell-side AI-payments infra: register your service/API as a merchant, connect Stripe/Braintree, get paid by AI agents (metered, x402-powered). PSP-agnostic. Partners AWS/Visa/Mastercard/Exa. Live 1.2M req/day, 342 active agents.

### Registration flow (proven live on mainnet, Aug 12, 2026)
1. Human gets an `NVM_API_KEY` from nevermined.app → Settings → Global NVM API Keys (the ONE thing we can't self-register).
2. The key is **prefixed** (`live:` or `sandbox:`). Store the FULL value including prefix — the SDK derives the environment from it.
3. Use `@nevermined-io/payments` (ESM). Register 5 GenTech services in one run via `payments.agents.registerAgentAndPlan(...)` with `getERC20PriceConfig(priceMicroUsdc, USDC_ADDRESS, BUILDER_ADDRESS)` + `getFixedCreditsConfig(1n, 1n)`. USDC 6 decimals → `BigInt(priceUsd * 1_000_000)`.
4. **Set environment from the key prefix, not hardcoded:** `const ENV = process.env.NVM_ENVIRONMENT || getEnvironmentFromApiKey(NVM_API_KEY) || 'sandbox';` — `getEnvironmentFromApiKey` maps `live:` → `live`, `sandbox:` → `sandbox`. Passing the deprecated `environment` option is ignored but prints a warning; removing it is cleanest.
5. **BUILDER_ADDRESS** = the settlement wallet that receives USDC payouts. Jordan's wallet `0x7ebf…96a`. Agent/plan IDs come back on registration — save them (they're huge uint256s) to `/root/.blockrun/nevermined-ids` + a vault copy under `09-Green Room/`.
6. Verify: run the script, confirm all 5 services return `agentId` + `planId` (a `❌` line means that service failed — don't assume partial success).

**Pitfall — the key has real minting capability.** A `live:` mainnet NVM key can mint tokens / move funds. Store it with `umask 077` + `chmod 600` (e.g. `/root/.blockrun/nevermined-api-key`), never echo it back, and coach Jordan to revoke it in nevermined.app if ever unused.

**Pitfall — verify the USDC contract address is the real one before wiring any revenue scan (Aug 12, 2026).** The revenue monitor's `USDC_CONTRACTS["base"]` held a **dead address** (`0x83358933e2…` — no contract deployed) while the correct Base USDC is `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`. Result: the on-chain USDC scan would silently never catch any Base payout (Nevermined, AgentLux, x402 settlements) — a silent revenue-blindness bug. A wrong contract address fails "closed" (empty results, no error), so it's easy to miss. **Always validate an ERC-20 address before scanning it for payments:**
```bash
# 1. Does any contract exist at the address? (empty = dead)
curl -s -X POST https://mainnet.base.org -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":["<addr>","latest"]}'
# → result "0x" or length ≤2 = NO CONTRACT at this address. Wrong address.
# 2. Confirm symbol/name/decimals match (USDC = "USDC Coin", 6 decimals)
#    symbol 0x95d89b41, name 0x06fdde03, decimals 0x313ce567 via eth_call
```
Trust the address that returns real symbol/name/decimals + has contract code — not a value copy-pasted from an old config. This applies to ANY chain's USDC/USDT address in the revenue scanner. (Verified Aug 2026: Base USDC = `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`.)

## Integration Reference: GoPlausible x402 Facilitator Bazaar

**GoPlausible** runs an x402 payment facilitator at `facilitator.goplausible.xyz` with a Bazaar discovery system. Focused on Algorand but also supports Base and Solana.

### Market Stats (as of Jul 2026)
- **Resources cataloged:** 41
- **Merchants listed:** 12
- **Networks:** Algorand (main), Base, Solana
- **Features:** Gasless (facilitator pays fees), MCP integration, open source (Apache 2.0)

### Discovery Endpoints
- `GET /discovery/resources` — List cataloged x402 resources
- `GET /discovery/all` — Aggregated discovery data (resources, merchants, facilitators)
- `GET /supported` — Supported payment schemes and networks

### Relevance
- **Algorand Global x402 Challenge** requires payments to route through GoPlausible for leaderboard tracking ($100K USDC + 500K ALGO prizes)
- Resources auto-discover when payment verifications happen — no manual listing needed
- Full MCP integration — agents can discover resources through their system

---

## Integration Reference: Pika MCP Creative Suite

**Pika** (AI video platform, $200M+ funded) launched an MCP server at `experiment.pika.art/mcp` (Jul 2026).

### Skills (15+ creative tools)
- `/4k-vfx` — Turn plain video into AI 4K effects
- `/app-sizzle` — 15-second launch video from app store link
- `/build-a-brand` — Full brand identity (logo, colors, fonts, tone, brand.md)
- `/founder-product-video` — Script + avatar + voice clone + lip-sync
- `/explainer` — URL/GitHub → polished explainer video
- `/podcast` — AI hosts discussing a brief
- `/ugc-ads` — Fast user-generated content style ads
- `/viral-hook` — Scroll-stopping attention assets

### Pricing
| Plan | Cost | Credits | What We Need |
|------|------|---------|-------------|
| Standard | **$8/mo** | 700/mo | ✅ Brand + launch video + explainer |

### MCP Installation
```bash
# URL: https://experiment-mcp.pika.art/api/mcp
# Auth: PIKA_TOKEN env var
# Skills: npx skills add Pika-Labs/Pika-Plugins
```

### Integration with Agent Kit
The Agent Kit Pika plugin proxies MCP tools — agents can generate videos, brand assets, and app store content through the same interface as data tools.

---

## Integration Reference: OKX.AI

### Market Stats (as of Jul 2026)
- Total tasks completed: 1,030
- Tasks posted: 3,565
- Tasks open: 1,539
- Average price: 0.01-10 USDT
- Chain support: EVM (Ethereum, Base, Arbitrum, X Layer) + Solana

---

## Integration Reference: Atelier (useatelier.ai)

### Market Stats (as of Jul 10, 2026)
- **Status**: Live marketplace with agents for hire
- **Token**: $ATELIER on Solana
- **Categories**: Image, video, code, research, trading, ops
- **Positioning**: "10x cheaper, 10x faster than human freelancers"
- **Features**: Agent marketplace, job posting system, skill discovery, API Docs, Litepaper, Launchpad, Bounties

### Major Update -- x402 Live on Robinhood Chain (Jul 10, 2026)
Every agent on Atelier can now be hired from **Robinhood Chain** with **USDG settlement** via **Naven Network** as the x402 facilitator. First order already paid on-chain.

**Key links:**
- Atelier announcement: https://x.com/useAtelier/status/2075728472635330950
- First tx: https://robinhoodchain.blockscout.com/tx/0xf7180c33598a6f5887262a59c5f1fad1877d3e6317c1dd44259463e54a8be8a6
- Naven facilitator: https://facilitator.naven.network
- Our agent credentials: in gentech profile .env (registered Jul 5)
- Full Naven/Robinhood research: references/naven-robinhood-chain-research.md

**GenTech action items:**
- Agent Kit Robinhood Chain plugin scoped (~3.5h build) -- see reference file
- Atelier credentials added to .env: ATELIER_AGENT_ID, ATELIER_API_KEY
- Update Atelier listing to include Robinhood Chain / USDG support

### Competitive Gaps Identified

| Feature | Atelier | Gentech Advantage |
|---|---|---|
| **x402 payments** | Not visible | ✅ Gateway live (Cloudflare) |
| **MCP/Tool Manifest** | Unknown (likely walled) | ✅ GOAT patterns documented |
| **Universal discovery** | Walled garden | ✅ AgentKit + BlockRun |
| **Revenue model** | Unknown | ✅ Clear monetization path |
| **Taste-driven curation** | Basic marketplace | ✅ Renaiss + collector economy |

### Integration Strategy: Piggyback → Upgrade → Compete

**Short-term (this week)**:
1. Study Atelier's agent listing format and job posting flow
2. Submit 1-2 GenTech agents as premium listings → free distribution
3. Reference in OKX hackathon submission as "existing market we're upgrading"

**Mid-term (next 2 weeks)**:
4. Build x402 payment wrapper for Atelier agents → make their agents better than native
5. Offer MCP integration to Atelier users → universal tool discovery

**Long-term (after OKX)**:
6. Ship Agent Arena with x402 + taste signals → superior marketplace

### Strategic Rationale

Atelier validates the agent marketplace model. Instead of head-on competition, we:
- **Piggyback** on their traffic now
- **Upgrade** their ecosystem with our infra (x402, MCP)
- **Compete** when our pieces are ready with superior value props

This is the "eat the meat, spit out the bones" pattern — leverage what's useful, ignore what's not, build on top with modular architecture.

- `references/jul-2026-ecosystem-developments.md` — After-Hours Oracle, VibeKit, Circle Starter Kits, Circle Marketplace, GoPlausible, Robinhood Chain

### Technical Stack
```bash
# Install Onchain OS skill
npm i @okx/onchainos-skills
```

Supported agents: Hermes, Claude Code, Codex, Cursor, Cline, Copilot, OpenClaw

### ASP Modes
1. **Agent-to-MCP**: Instant pay-per-call, requires OKX Payment SDK
2. **Agent-to-Agent**: Escrow commerce, requires Agentic Wallet

### Agent Lineup — First 3
| Agent | Service | Price | Mode |
|---|---|---|---|
| LP Shape Detector | Detect LP strategy shapes | 0.5 USDT/scan or 5 USDT/mo | MCP |
| DCA Rebalancing | Automated rebalancing | 10 USDT/setup or 20 USDT/mo | Escrow |
| Yield Scanner | Cross-chain yield optimization | 1 USDT/scan or 8 USDT/mo | MCP |

See `references/okx-ai-research.md` for full competitive analysis and deep dive.

---

## Integration Reference: SAP MCP (OOBE-PROTOCOL/sap-mcp)

**SAP MCP** is an MCP server for the Solana Agent Protocol — agent-to-agent chat, registry, payments, escrow, social gaming, and DeFi, all on Solana. 19 skills packaged as a Cursor plugin.

### Market Stats (as of Jul 2026)
- **Version:** v0.9.3 (189 commits, 35 tags)
- **Stars:** 3, **Forks:** 0, **Open Issues/PRs:** 0
- **Last commit:** 7 hours ago — actively maintained
- **Source:** https://github.com/OOBE-PROTOCOL/sap-mcp
- **Cursor Directory:** https://cursor.directory/plugins/sap-mcp
- **Skills:** 19 (chat, registry, payments-x402, escrow-settlement, social-gaming, agent-registry, memory-vault, defi, market-data, reputation-attestation, solana-token, nft-metaplex, staking, sns, tool-registry, ledger-session, discovery-indexing, operations, agentkit)

### Key Skills for Arcade Integration

| SAP Skill | What It Does | Arcade Connection |
|-----------|-------------|-------------------|
| **sap-social-gaming** | Blinks, Gibwork bounties, Send Arcade games | Agents discover and play arcade cabinets |
| **sap-payments-x402** | `sap_payments_call_external_x402` — call external x402 endpoints with Solana payment | Our Base gateway becomes payable from Solana agents |
| **sap-escrow-settlement** | Escrow V2 for deposits, settlement, disputes | Tournament entry — lock fee, winner claims pot |
| **sap-agent-registry** | Register, discover, list SAP agents | Gentech becomes discoverable on Solana |
| **sap-reputation-attestation** | Agent scoring and reputation | Win-rate tracking, leaderboard |

### External x402 Integration

The `sap_payments_call_external_x402` tool is designed to call non-SAP x402 endpoints. It fetches a 402 challenge, signs locally, retries with PAYMENT-SIGNATURE, and returns the response + receipt. Our x402 gateway on Base is directly callable from Solana agents — cross-chain without bridging.

### Setup Workflow

1. **Install Solana CLI** (if not present):
   ```bash
   sh -c "$(curl -sSfL https://release.anza.xyz/v2.1.0/install)"
   ```

2. **Create agent keypair**:
   ```bash
   mkdir -p ~/.config/mcp-sap/keypairs
   solana-keygen new --no-bip39-passphrase \
     --outfile ~/.config/mcp-sap/keypairs/gentech-keypair.json
   AGENT_ADDR=$(solana-keygen pubkey ~/.config/mcp-sap/keypairs/gentech-keypair.json)
   ```

3. **Fund the agent wallet** — Send ~0.01 SOL from the owner wallet to `$AGENT_ADDR`. Owner wallet is the main controlling wallet (Jordan's).

4. **Create agent metadata JSON** with fields: name, description, version, x402Version, owner (Jordan's Solana address), agentAddress (keypair pubkey), x402Endpoint (gateway bazaar URL), capabilities[] (each with name, description, endpoint, price), protocols, networks (CAIP-2), tags, revenue block.

5. **Configure SAP MCP** — `config.gentech.json` with mode, rpcUrl, programId, walletPath, maxTxValueSol.

6. **Register on-chain** — Via `sap_payments_register_agent` (local SAP MCP with private key). Hosted SAP MCP returns `hosted_local_signer_required` — needs local signing.

### Prerequisites
- Solana wallet with ≥0.01 SOL for SAP treasury registration fee
- Node.js installed
- Git clone of `OOBE-PROTOCOL/sap-mcp`

### Contribution Opportunity

Zero external contributions to date — first-mover advantage.
- **Base network support** in `sap-payments-x402` (currently Solana-only)
- **Arcade cabinet** as a Send Arcade game via `send-arcade_playGame`
- **Escrow tournament pattern** using V2 settlement pipeline

Strategy: fork → integrate (register agent, wire payment) → prove flow → PR improvements.

---

## Integration Reference: OpenDexter (open.dexter.cash)

**OpenDexter** is the first x402 **search engine / marketplace MCP** for AI agents. Any agent can search 5,000+ paid APIs, check pricing, and pay with one call. Run by Dexter — the x402 facilitator behind millions of settlements.

### Key insight: Auto-Discovery — no registration needed
Dexter's marketplace grows **passively from successful x402 settlements through its facilitator**. When ANY x402 payment settles through Dexter, the paid API is auto-cataloged:
- Resource URL + method from the payment payload
- Seller wallet from the payTo field
- Metadata (description, content type) + usage hit counts
- Appears as "discovered" status → seller can **claim** it to add branding/description/verification

So **the way to get listed is to settle a real x402 payment through Dexter's facilitator** — not to submit a form. Verify presence by searching `x402_search` for our host (e.g. `api.gentechlabs.net`). If we haven't settled a payment through Dexter, we won't appear.

### Access methods (three)
1. **MCP URL** (zero install): `https://open.dexter.cash/mcp` — ephemeral session wallet per connection
2. **npm package** (local wallet): `npx @dexterai/opendexter install` → `~/.dexterai-mcp/wallet.json`
3. **Authenticated MCP** (managed wallet): `https://mcp.dexter.cash/mcp` — OAuth, existing Dexter account

### ⚠️ Health-check the search backend BEFORE flagging "not listed" (Aug 14, 2026)
`capabilitySearch` from `@dexterai/x402/client` hits the **`x402.dexter.cash` search backend**, which can
return **HTTP 502 behind Cloudflare for long stretches** (observed all-day Aug 14 — every path 502). When it's
down, every query fails with `Capability search failed: 502` and the OpenDexter re-check cron reports a false
"not listed / still indexing." **Diagnose the outage first, not your listing:**

```bash
# If this is 502/5xx/000/timeout, the platform search backend is DOWN — you cannot verify listing status.
curl -s -m 15 -o /dev/null -w "%{http_code}" "https://x402.dexter.cash/search?q=gentech"
```

- The MCP endpoint itself (`open.dexter.cash/mcp`) can be alive (handshake returns `OpenDexter v0.5.0`) while
  the search engine behind `x402.dexter.cash` is down — separate surfaces, check both.
- **Set the re-check cron to health-check `x402.dexter.cash` FIRST**, and only run the actual search if it's up;
  otherwise report the outage (platform-side) and do NOT conclude "not listed."
- When the outage resolves, re-run the search — do NOT burn new self-settlements trying to force re-index.

### Five tools
`x402_search` (noauth, read-only), `x402_check` (inspect pricing, quote-only anonymous), `x402_fetch`/`x402_pay` (paid calls), `x402_wallet` (view wallet). OAuth-gated tools (`x402_wallet`, `dexter_portfolio`) need a passkey/Dexter account — the search + check are free/noauth.

### Probe before wiring (verified Aug 2026)
The endpoint returns MCP 400 ("No active session. Send POST to initialize") until you run the initialize handshake. Use the borrow-spit-out-evaluation "probe a remote MCP endpoint" pattern to enumerate tools + test a read-only `x402_search` call before adding to Hermes config.

---

## Integration Reference: Syra (syraa.fun)

**Syra** is an x402 API gateway with a built-in marketplace. 500+ AI agents already paying via their protocol.

### Market Stats (as of Jul 2026)
- **Activity:** 8.67K transactions / $245.42 volume / 23 buyers in 30 days
- **Resources:** 45 endpoints
- **Pricing:** $0.001-$0.08 per call via x402 v2
- **Chains:** Solana, Base
- **Also on x402scan:** Publicly traceable at `https://www.x402scan.com/server/{uuid}`
- **ERC-8004 support:** Has `8004/stats`, `8004/leaderboard` tools

### Third-Party Registration
Email `support@syraa.fun` with the following fields:
Service name, Website / API base URL, Short description, Category (analytics, defi, ai), Pricing per call (USD), Supported networks (Base / Solana)

### Our Opportunity
- No token security/rugcheck service on Syra yet — first mover advantage
- No agent credit/identity scoring — wide open category
- Syra's ERC-8004 tools + our identity expertise = deep integration

### Links
- API: https://api.syraa.fun
- Marketplace: https://syraa.fun/marketplace
- NPM: `@syra-ai/sdk`, `@syra-ai/x402-payer`, `@syra-ai/mcp-server`

---

## Integration Reference: x402scan (x402 Ecosystem Explorer)

**x402scan** is the block explorer and analytics dashboard for the x402 ecosystem. Also functions as a marketplace where agents discover and try APIs.

### Global Stats (30-day, Jul 2026)
- **Transactions:** 18.62M
- **Volume:** $863.98K
- **Buyers:** 58.13K
- **Sellers:** 46K

### Registration
Simple URL registration at `https://www.x402scan.com/resources/register` — enter your API URL, instantly listed. No review queue, no cost.

### Our Opportunity
- No token security/identity/gaming services listed — wide open
- Public stats serve as traction proof for grants

### Pitfall: Ecosystem Page vs Resource Register
The x402scan ecosystem page at `/ecosystem` lists projects registered in the `coinbase/x402` repository. Being on x402scan's resource register (URL-based registration at `/resources/register`) does NOT automatically put you on the ecosystem page. To appear on the ecosystem page, you need to be listed in the coinbase/x402 repo's ecosystem directory. Check both independently.

### Pitfall: `.well-known/x402.json` vs `.well-known/x402`
x402scan and Agentic.Market auto-indexing probes BOTH paths. If only `.well-known/x402` exists but `.well-known/x402.json` returns 404, auto-indexing fails silently. Ensure both paths serve the same discovery document, or add a redirect/alias from `.json` to the canonical path.

---

## Integration Reference: Fluora (fluora.ai)

**Fluora** is a peer-to-peer MCP marketplace where AI agents discover and purchase services programmatically. Listed on the x402scan ecosystem.

### Market Stats (as of Jul 2026)
- **Type:** Peer-to-peer MCP marketplace
- **Payment:** x402 via USDC
- **Positioning:** "No sign-ups, no API keys, no humans in the loop"
- **Links:** https://www.fluora.ai/marketplace

### Our Opportunity
- No token security/DeFi intelligence services listed yet — wide open category
- Early mover advantage on a new marketplace

---

## Integration Reference: AI Agent Store & AI Agent Index

**AI Agent Store** (`aiagentstore.ai`) — 1,300+ agents listed, free to submit. General-purpose AI agent directory.

**AI Agent Index** (`theaiagentindex.com`) — Free listings, structured data, discoverable by AI systems. $9.99/mo vendor tier for premium placement.

### Our Opportunity
- Low-effort distribution — free listings, no review queue
- SEO value for GenTech Labs brand presence
- Good for backlinks and discovery by human users

---

## Integration Reference: Pay-Skills Catalog (solana-foundation/pay-skills)

**Pay-Skills** is the canonical x402 API catalog at `github.com/solana-foundation/pay-skills`. 70+ providers listed as of Jul 2026.

### Status: Not Listed
GenTech Labs has no provider directory in the pay-skills repo. PR #190 (Jul 17, 2026) was never merged — the `providers/ProtoJay4789` directory doesn't exist on `main`.

### Pitfall: PRs Can Be Lost
A submitted PR that passes CI can still fail to merge if the fork is deleted or the PR is closed without merge. After submitting, verify the provider directory exists on `main` before considering it done. If the fork was deleted, the PR is orphaned — re-fork and re-submit.

### Registration
Submit a PR adding `providers/<operator>/<name>.md` with:
- YAML frontmatter: name, description, categories, url, openapi (inline spec)
- Populated `paths:` in the inline OpenAPI (empty paths cause Greptile bot rejection)
- At least one endpoint with operationId, summary, x-payment-info, and 402 response schema

---

## Integration Reference: Q402 Escrow (QuackAI)

### Capabilities
- Gasless USDC/USDT escrow for AI agents
- Buyer signs once → Q402 relays → funds lock on-chain
- Release on approval, refund after timeout, dispute arbiter
- Under the hood: EIP-7702 delegated execution, EIP-712 signatures

### Installation
```bash
npm i @quackai/q402-mcp
```

### Integration Play
Use Q402 as escrow layer for complex agent-to-agent jobs on ANY marketplace. Complements instant payment protocols (x402) with secure escrow when needed.

**Strategic value**: Most marketplaces lack escrow. Offering it day one gives instant credibility.

---

## Pricing Strategy

### Early Stage Rules
- **Start low** (0.01-1 USDT) to drive initial sales and reputation
- **Tier up** (5-20 USDT) after 10+ positive reviews
- **Subscription > one-off** for continuous services (higher LTV)

### Pricing Models
| Model | Use Case | Example |
|---|---|---|
| Pay-per-call | Simple, standardized tasks | Data queries, price feeds |
| Performance % | Revenue-generating agents | Yield optimization, arbitrage |
| Subscription | Continuous value | Monitoring, rebalancing |
| Project fee | Complex, one-off jobs | Research reports, strategy design |

### Competitive Signal
Check what similar agents charge. If market prices are 0.5-1 USDT, pricing at 10 USDT requires justification (better results, faster, continuous value).

---

## Pitfalls

- **⚠️ A marketplace can look open + payable yet NEVER pay anyone — verify the payout rail fires on-chain BEFORE committing work (Aug 12, 2026).** BountyBook (bountybook.ai) showed 118 open jobs / $638 "available" / "avg $12.68/hr", and our claim→submit pipeline worked end-to-end — but **zero USDC has EVER moved on the platform**. Two independent failures (code verifier crash + payout rail never fires) meant no worker ever got paid, and nobody could tell from the UI. **This is the #1 trap in agent marketplaces: "work available" ≠ "you can earn here."** Before investing time on ANY marketplace, run the PAYOUT-RAIL PROBE (full recipe: `references/payout-rail-probe.md`):
  1. **Check the treasury/settlement wallet on-chain** — `GET base.blockscout.com/api/v2/addresses/<platform-treasury>/transactions` (or the platform's escrow contract). If a live marketplace shows **zero lifetime USDC outflows**, treat all "available" balances as fiction.
  2. **Check completed jobs** — do "verified"/"completed" jobs carry a real `payout_tx_hash` and a moved balance? On BountyBook, verified jobs showed `payout_status=failed` with no tx — the payout rail never fired.
  3. **Check for a verifier bug that blocks ALL submissions** — e.g. BountyBook's oracle read `spec.success_condition.required_fields.length` while code jobs carried `required_files` → `undefined.length` crash on every code submission (lifetime code_test settlements 0/32). A verifier that fails for EVERY agent (independent of payload shape) is a platform bug, not your code.
  4. **Check whether the operator knows** — a marketplace that already has an open bounty to fix its own payout/verifier (BountyBook had a $150 fix offer) is a "park it" signal, not a "keep trying" one.
  5. **Do a cheap real claim once** — claim a $1–3 job, submit a genuinely-correct deliverable, and confirm the attempt lands + verifies. Our BountyBook claim/submit worked and the attempt logged, but verification crashed → that WAS the probe. If it crashes, stop.
  **Rule:** "available" balance + working API is necessary but NOT sufficient. Only commit real effort after you've confirmed a verified job actually moves USDC on-chain. Log the result in the registry row (LIVE / PARKED / NEVER-PAID).
- **CDP Bazaar / PayAI silent non-indexing — ROOT CAUSE is client extension echo (Aug 6, 2026):** Even with a correct discovery doc AND real on-chain settlements, a resource won't index if the **buyer's client drops the `extensions` object** when building the payment payload it sends to the facilitator's `/verify`/`/settle`. The facilitator only catalogs a resource from the declaration it sees in the payment payload — if the client doesn't echo `extensions.bazaar` from the 402 challenge, the facilitator settles the payment fine but never catalogs you. This is the documented #1 cause of "my resource never appears" (PayAI Bazaar docs; same mechanism on CDP/Agentic.Market). **Diagnose:** check the facilitator's `/verify` or `/settle` response for the `EXTENSION-RESPONSES` header — `{"bazaar":{"status":"processing"}}` = accepted, `rejected` = schema fail, **no header at all = client dropped the extension**. **Fix:** the self-settle client must register the bazaar extension so it echoes. In `@x402/core`, `enrichPaymentPayloadWithExtensions` returns early when `registeredExtensions.size === 0` — registering only the payment scheme (e.g. `ExactEvmScheme`) is NOT enough; the bazaar extension must be registered too. Pay once through an echoing client (any `@x402/*` 2.x, `x402-solana` ≥ 2.0.5). **PayAI catalogs on `/verify` too** (since 2026-07-29) — you can list/refresh with a verify-shaped payment that moves no funds, no settlement needed. There is no re-index endpoint; refresh is forward-only on the next extension-carrying payment.
- **CDP Bazaar silent non-indexing — discovery doc format (Aug 6, 2026):** A real on-chain settlement through the CDP facilitator is NOT sufficient to get indexed on Agentic.Market / CDP Bazaar. The `extensions.bazaar.info.input` block in the 402 challenge MUST include `type: "http"`, `method: "GET"` (or POST), and `bodyType: "json"` — plus a proper `schema` describing `input`/`output` (not `result`/`error`). If `info.input` only has `{"example": {...}}` (missing type/method/bodyType), the indexer silently drops the resource even after successful settles — this is the exact failure from x402-foundation issue #2207, confirmed by Coinbase collaborator ethanoroshiba. Fix: add the three fields + proper schema, restart the gateway, re-settle, then wait up to 6h. Verify with `GET /v2/x402/discovery/merchant?payTo=<seller>` and `search?query=gentech`. Also note: `extensions.bazaar.discoverable: true` is NOT a valid field and causes failed discovery — remove it. Use `agentic.market/validate` to check discoverability.
- **Seed-parser markdown noise (Aug 5, 2026):** when a registry-parsing seed script extracts platform names from table cells, strip markdown artifacts before dedup — `**bold**` wrapping and `[name](url)` link syntax. If you don't `re.sub(r"\*\*","",name)` and strip link-syntax, the exclusion set contains `**OpenDexter**` instead of `OpenDexter` and dedup silently misses it, so the scanner re-reports a platform we're already on. Also split the registry on the `## 🟢 LIVE` / `## 🟡 PENDING` / `## ⚪ KNOWN` headers so each row lands in the right bucket (already_listed vs watchlist vs known-not-pursued) instead of one undifferentiated blob.
- ❌ **Listing untested agents** — test end-to-end before going live
- ❌ **Overpricing early** — build reputation first, charge premium later
- ❌ **One-way integration** — only accepting platform payments reduces reach
- ❌ **Ignoring category selection** — list in niche where you can dominate
- ❌ **No examples** — buyers need to see what they're getting
- ❌ **Static descriptions** — update based on user questions and feedback
- ❌ **Empty OpenAPI paths in Pay-Skills provider files** — Every provider file submitted to `solana-foundation/pay-skills` must have populated OpenAPI paths in its inline `openapi` field. A skeleton with `"paths": {}` causes the build to fail because no endpoint schemas can be inlined into per-provider detail JSON. Greptile bot reviews and flags this automatically (as seen in PR #154). Before submitting, verify every provider file has at least one real path with operationId, summary, and x-payment-info.

## OpenAPI Spec Completeness Requirements

### Pay-Skills (solana-foundation/pay-skills)

**PR #154 blocker (Jul 2026):** All 12 provider files had `"paths": {}` skeletons. Greptile bot comment:

> "All 12 inline specs share the same skeleton — `"paths": {}`. With no paths the build has no endpoint schemas to inline into the per-provider detail JSON, so agents that introspect the spec will discover zero callable endpoints."

**Requirements per provider file:**
1. Frontmatter `name:` must match the filename stem (case-sensitive)
2. Frontmatter `openapi:` field must be present
3. `description:` must be non-empty
4. `categories:` must use underscore format (`ai_ml`, not `ai-agents`)
5. **Inline `openapi` object must have populated `paths:`** — at least one route with:
   - A valid OpenAPI path template (e.g. `/v1/games/search`)
   - `operationId` (unique across all files)
   - `summary` (human-readable)
   - `x-payment-info` block with price, mode, and protocol
   - Response schemas for 200 and 402 status codes
6. The `url` in frontmatter must point to a live, reachable endpoint

**Validation:** Greptile bot scans every PR. Structural issues (missing fields, wrong categories) are flagged at commit time. Missing paths are flagged at build time. Fix all structural issues first, then populate paths, to avoid multiple review rounds.

---

## Verification Steps

Before listing an agent:
1. ✅ Run the agent 10+ times successfully
2. ✅ Test platform payment flow end-to-end (small test amount)
3. ✅ Prepare 2-3 example outputs for buyers to preview
4. ✅ Write clear description of what's delivered (no vague promises)
5. ✅ Set pricing aligned with market (start low if uncertain)

After listing (week 1):
1. ✅ Monitor sales and refund rates
2. ✅ Track buyer questions (update FAQ if patterns emerge)
3. ✅ Check reputation score (aim for 95%+ positive)
4. ✅ Adjust pricing if 0 sales after 7 days (likely too high or wrong category)

---

## Marketplace Audit Pattern

Periodically audit every marketplace we're listed on. New endpoints, new services, and platform changes can make listings stale.

### Audit Checklist
1. **List all marketplaces** — OKX AI, Swarms, x402 Bazaar, Atelier, Agent Scan, Adelier, Coinbase Bazaar, Circle Marketplace, Syra, x402scan, Fluora, AI Agent Store, AI Agent Index, Pay-Skills Catalog, Virtuals ACP
2. **For each, check:**
   - Is the listing still live?
   - Does the description reflect our current capabilities?
   - Are new endpoints/services missing?
   - Has the platform changed its requirements? (e.g. OKX now requires `eip155:196` X Layer)
   - Is pricing still competitive?
3. **Document findings** in `10-Labs/marketplace-audit.md`
4. **Flag stale listings** for Jordan to update (many require manual login)
5. **Add new services** — if we shipped new endpoints since listing, add them

### Common Stale Listing Signs
- Description mentions old pricing or old endpoint count
- Platform added new features (x402 toggle, new chains) since we listed
- We shipped new services that aren't listed
- Platform changed its registration/listing flow

### Pitfall: Manual Updates
Most marketplaces require manual login to update listings (Swarms, OKX, Atelier). Document exactly what needs to change so Jordan can do it in one pass. Save as `10-Labs/<marketplace>-listing-update.md`.

---

## Related Skills
- `agent-economy` — ERC-8004, x402 protocol, OOBE Protocol
- `q402-escrow-integration` — Gasless escrow for agent-to-agent commerce
- `dual-protocol-payments` — x402 + Q402 dual payment routing

---

## Support Files
- `references/telegraph-miner-registration.md` — **wrap an API as a Telegraph Protocol Miner** (declarative YAML, canonical-intents mismatch, verify live API fields before on_chain transform, immutable registration, GitHub contribution angle). Use when registering on Telegraph Season I.
- `references/agentlux-autonomous-onboarding.md` — **AgentLux fully-autonomous onboarding** (free challenge-sign auth, no human key, First-Hire Guarantee). The proven 5-step flow + pitfalls + our live agent/listing state. Use when standing up an autonomous earning rail.
- `references/verify-marketplace-listing.md` — **verify a listing was posted correctly before nudging the platform** (AgentLux pattern). Public-visibility check, list-vs-detail endpoint schema echo pitfall, sample-URL resolution, profile flags. Use when a listing isn't producing hires/income.
- `references/autonomous-marketplace-registrations-aug-2026.md` — **verified autonomous registrations on APIHub, RelAI, Toku, dealwork.ai** (Aug 13). Exact endpoints, request bodies, rate limits, and the reusable wallet-sign challenge-response pattern. Use when registering on any of these four.
- `references/akindo-registration-flow.md` — **AKINDO login + verification code + account setup + join buildathon** (0G Bridge Wave 3 joined Aug 13). The one-time-code invalidation pitfall, the hidden-file-input icon-upload workaround (`DataTransfer` injection for React forms), and join verification. Use when registering for any AKINDO WaveHack (0G, Midnight).
- `references/payout-rail-probe.md` — **verify a marketplace actually pays on-chain before working it.** The 5-step probe (treasury on-chain check, completed-job payout_tx, universal-verifier-bug check). Proven on BountyBook (never-paid trap). Use before committing effort to ANY marketplace.
- `references/new-marketplaces-aug-2026.md` — **Agoragentic (registered, paid-execution FROZEN) + Agent Bazaar (register endpoint BROKEN).** Both open-entry but not earnable yet; capture the state + re-check conditions so a future session doesn't re-attempt. Pattern: registration succeeding ≠ you can earn.
- `references/marketplace-contribution-drafts-aug-2026.md` — **verified contribution targets + drafted bug reports** for broken/frozen/never-paid marketplaces (Agoragentic GitHub issue, Agent Bazaar X DM, BountyBook Discord post). Use when Jordan's routing rule says "contribute a fix" — file or hand to Jordan without re-researching.
- `references/marketplace-scanner-v2-deduped.md` — Deduped NEW-only marketplace hunting pattern (seed a scanner with an exclusion list from `marketplace-listings-registry.md`, then hunt ONLY new platforms with why/income/friction). Proven Aug 2026, queue #42. Includes "Forge = desktop lane" routing note.
- `references/okx-ai-research.md` — OKX.AI market analysis, competition, integration roadmap
- `references/q402-escrow-technical.md` — Q402 technical specs, EIP-7702 details, integration patterns
- `references/naven-robinhood-chain-research.md` — Naven Network, Robinhood Chain, USDG, plugin scope
- `references/july-22-2026-marketplace-scan-results.md` — Full marketplace scan results from Jul 22, 2026: Pay-Skills PR status, x402scan registration blockers, Circle Marketplace, Fluora, AI Agent Store, and all other tracked platforms
- `references/sap-mcp-agent-metadata-template.md` — SAP MCP agent metadata JSON template, config template, and registration workflow
- `references/algorand-usdc-optin.md` — Algorand USDC opt-in (ASA 31566704): why Coinbase refuses to send USDC to a non-opted-in Algorand address, the 0-unit self-transfer fix, and the `py-algorand-sdk` (not `algosdk`) gotcha. Use when funding an Algorand wallet for the x402 Challenge or any Algorand USDC settlement.
- `references/beep-sui-rail.md` — **Beep Sui payment rail (greenlit Aug 14)**: agentic finance on Sui, USDC-on-Sui, a402/x402. Jordan wants a Sui rail via Beep (NOT Monad — Beep is Sui-native). SDK (`@beep-it/sdk-core`, `beep_pk_`/`beep_sk_` keys), build plan (new settlement backend, not a `sui:` config line), and the human-signup blocker (app.justbeep.it keys on Jordan's list). Use when wiring a Sui settlement rail into the x402 gateway.