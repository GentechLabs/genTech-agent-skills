# x402scan Manual Registration — Proven Working Flow (Aug 24, 2026)

## Why this is the reliable path
The **settle→auto-index theory FAILED empirically.** We paid 0.015 USDC on-chain (Aug 19)
to trigger the "settlement-gated" auto-index, and 6+ hours later the verification job found
`api.gentechlabs.net` at **0 results on Agentic.Market AND not listed on x402scan/OpenDexter**
(see the `x402-Settlement-Index-Verify` cron output, 1c0e40ea445b). Do NOT keep paying
self-settlements expecting auto-listing — the passive theory is dead for these venues.

**Manual registration on x402scan is the reliable path** — it's a browser form with no
review queue, and it genuinely worked.

## The flow (worked, Aug 24)
1. Go to `https://www.x402scan.com/resources/register` in a real browser (the SPA is
   JS-rendered — `curl`/`web_extract` get only the Next.js boilerplate; use `browser_exec`).
2. Set the URL input (placeholder `api.example.com`) to `api.gentechlabs.net` via
   `Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set` +
   dispatch an `input` event (React-controlled input — plain `.value=` won't stick).
3. The "Add API" submit button shows `Checking 0/9 endpoints...` and is DISABLED while it
   scans/validates your live endpoints (it probes `/health`, `/status`, `/openapi.json`,
   `/well-known/x402`, `/x402-bazaar`, `/agent-card.json`, service routes). Wait for it to
   finish — the button text becomes `Add API (9 resources)` when enabled.
4. Click submit. Result: **"Successfully registered 9 of 9 resources"**.
5. It gives a merchant share link `tryponcho.com/m/<your-host>` (may lag/404 at first —
   don't treat a 404 there as failure; the registration itself is confirmed by the success
   message).

## Gotchas
- **Don't confuse the Add-API form's live preview with being listed.** Filling the form
  renders your gateway's full details (name, 9 endpoints, description) as a *preview of
  what will register* — that is NOT proof you're already on the public list. Only the
  explicit success message + a live resources-page hit are real.
- **Fresh listings don't show on the `/resources` "most used" pages right away.** Those
  rank by request volume; a just-registered merchant appears only once it has activity.
  Search the live resources page for your host to confirm, not the featured pages.
- **x402scan ecosystem page ≠ resource register.** `/ecosystem` requires being in the
  `coinbase/x402` repo's ecosystem directory; the `/resources/register` URL registration
  does NOT put you there. Check both independently.

## Revenue framing (Jordan, Aug 24)
"Listed" ≠ "bought." We had 10 services live + registered on multiple marketplaces and
still $0 revenue — because nobody pings niche analytics (token security, DeFi LP) at
volume. The proven earners on x402 are **high-frequency utilities agents call repeatedly**:
LLM inference resale (cost+5%; e.g. BlockRun ~$820/day), live market data (Bloomberg,
CoinGecko on Agentic.Market), web search/scrape, media generation. When the goal is revenue
(not presence), prioritize getting a high-frequency service discoverable + driving real
traffic to it, and defer speculative infra (e.g. Stripe/card paid tiers) until real paying
usage exists. Coinbase's own 3-step monetize path: Coinbase Business account (USDC settle
address) → CDP x402 Facilitator (managed verify+settle) → wrap endpoint with x402
middleware + set per-call price.
