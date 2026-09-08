# Demand-First Monetization — Don't Build Payment Plumbing Before Proven Usage

> Jordan's correction, Aug 24 2026: "If we do the subscription, the business has to
> be taken off for me to think it's worth the investment." When asked to build
> Stripe/card checkout for paid subscription tiers, the honest answer was **not yet** —
> build infrastructure only when there is proven paying demand.

## The principle
**Build the revenue loop BEFORE the revenue plumbing.** The gate for "is the
subscription worth building" is *demand* (first real paying customer / repeated
calls), NOT infrastructure readiness. Adding Stripe webhooks, card checkout, billing
on zero usage = investing in the plumbing before the water arrives.

- **Free tier + x402 = the on-ramp** (zero-cost, already works). Keep it.
- **Paid subscription/Stripe tier = hold until there's proof of paying usage.**
- Reorient from "set up payments" to "find the first paying customer" — because that
  gate makes the subscription worth building at all.

## Why our current API portfolio under-earns (the honest diagnosis)
We have 10+ live services (token security, wallet analysis, market intel, DeFi LP
analytics, NFT search…) priced $0.01–0.10/call on 6 chains, listed on multiple
marketplaces — **and make zero revenue.** Listing ≠ being bought.

The proven earners on x402 are **high-frequency utilities agents call constantly**,
not niche analytics a crypto agent pings occasionally:

| Service type | Why it earns | Real example |
|---|---|---|
| **LLM inference resale** | Agents call 1000s×/day | blockrun ~$820/day (~$25K/mo), cost+5% |
| **Market/price data** | Every trading agent needs live prices | Bloomberg, CoinGecko on Agent.market |
| **Web search/scraping** | Agents research constantly | Linkup, Apify |
| **Media/thumbnail gen** | Built-in Coinbase demo | x402 Thumbnail Generator |

**Reposition at least one service to a high-frequency category agents actually buy
in volume (inference resale, live market data) rather than only $0.02 analytics.**

## The demand-discovery lever (first paying customer)
1. **Get discovered where agents actually browse** — Coinbase Agent.market
   (69K active agents, $50M cumulative volume, where Agentic Wallets plug in
   by default), x402scan manual registration. We're validator-compliant.
2. **Drive traffic to listings** — fresh registrations climb "Most Used" rankings
   once they get request volume; that surfaces us to agents.
3. **Real settlements land first** — the first on-chain paid call is the proof
   that justifies building paid-plan plumbing on top.

## Application to the Human Pricing gateway (#56)
- Free tier (50 calls/mo) + x402 are LIVE and earning-capable — good on-ramp.
- Paid $69/$269 plans need Jordan's Stripe account + webhook.
- **Decision: defer Stripe build until there's proven paying usage.** When a real
  customer starts paying, Stripe is a short add-on, not a speculative build.

## x402scan revenue-listing-map correction
The earlier `revenue-listing-map.md` said x402scan "auto-indexes from /openapi.json."
That is FALSE as the listing path — settlement/openapi crawling does NOT list us
(0.015 USDC settled Aug 19, stayed 0). The working path is the **manual "Add API"
form** (see `platform-registration` skill → `references/x402scan-manual-registration.md`).
