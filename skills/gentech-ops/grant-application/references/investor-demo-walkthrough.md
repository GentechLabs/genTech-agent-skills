# Investor / Grant Demo Walkthrough — Structured Script

**Context:** Prepared for GOAT Network meeting (Jul 29, 2026). Reusable template for any investor, grant committee, or accelerator pitch where you show live products.

## Structure: 10-15 Minutes

### 1. The Problem (1 min)
Lead with a striking stat or observation that frames the gap. Make it concrete, not abstract.

*Example: "57.5% of web traffic is bots. Agents are already the majority of the internet — but they can't pay each other. No wallet, no credit card, no bank account. We built the payment rail they need."*

### 2. The Demo — Start at the Demo Hub (5 min)
Open `demo.gentechlabs.net` (or equivalent suite hub) and walk through each product in order. Show live, running systems — not slides.

**Walkthrough order:**
1. **Payment Infrastructure** — x402 Gateway (live APIs), Q402 Gasless (12 chains, zero gas), Agent Kit (open source)
2. **DeFi Intelligence** — Yield Rainbow (live dashboard), GTA Arb Monitor (real-time arbitrage data)
3. **Agent Infrastructure** — Self-Evolution Harness (4 cron jobs, autonomous improvement), Agent Credit Score (ERC-8004)

### 3. Live Dashboards (3 min)
Open specific subdomain dashboards to show real-time data:

- `yield.gentechlabs.net` — DeFi yield monitoring with rainbow bands
- `arb.gentechlabs.net` — Cross-venue basis scanner with live arbitrage opportunities

### 4. The Ask (2 min)
Frame what you've built on limited resources and what funding unlocks. Be specific about milestones, not vague about "growth."

*"We've built this on a $10K bridge loan and a $795/month apartment. With funding, we can: [specific milestones]. We're not asking for a million dollars because we have a deck. We're asking because we have production infrastructure, real users, and a system that's already making money."*

### 5. Close (1 min)
One sentence summary + open invitation.

*"Demo suite is live at demo.gentechlabs.net. Everything you saw is running right now. We'd love to show you what we can build with your support."*

## Tips for the Call

- **Lead with the demo** — open the live URL and walk through it. Don't read slides.
- **Don't read slides** — show the actual products running.
- **If they ask about team:** "Solo builder with an AI orchestrator. I ship faster than most teams."
- **If they ask about revenue:** "x402 microtransactions + contract work. Enough to keep building, not enough to go full-time yet."
- **If they ask about competition:** "Nobody's doing agent-to-agent payments with zero gas. Stripe doesn't work for bots."

## Pre-Meeting Checklist

- [ ] All demo pages return HTTP 200
- [ ] Subdomain DNS records are set (yield, arb, demo)
- [ ] Portfolio nav links to demo hub
- [ ] Demo video placeholder is ready (or actual video)
- [ ] Yield data cron is running (every 30min)
- [ ] GTA arb data is live
- [ ] Test the full walkthrough from a fresh browser (no cached auth)
- [ ] Have backup screenshots in case live demo fails
