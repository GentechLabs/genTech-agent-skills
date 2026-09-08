# Grantor / Investor Project-Status Update — Template

Ready-to-send honest template for replying to a funding partner (grantor, incubator, investor)
who checks in on a project. Verified pattern from the Victus Global exchange (Aug 13, 2026).

## Golden rules
1. **Never claim a live state you haven't verified.** Check on-chain balances, active positions,
   and cron/automation enabled-state BEFORE drafting.
2. **Separate "built & proven" from "currently live."** Infrastructure can be complete and
   verified while the live deployment is paused/empty. State both.
3. **When the user's intent-context explains a gap, lead with the honest story.** Jordan's
   fund-return test became a stronger message than the false "managing real money" claim.
4. **Verify all links** — HTTP 200 + content check + exact live endpoint count.

## Message skeleton

```
Hey, appreciate you checking in! <Project> is moving well. <KEY LIVE ARTIFACT> is live —
<one line on what it is + the differentiator>.

We've built out <THE REAL SUBSTANCE> — <2-3 lines on what it does, with a concrete proof
point (e.g. "it proved it can return real USDC to the owner on command")>.

Right now <HONEST CURRENT STATE — e.g. "the position is being redeployed after a test">,
and the whole thing sits on <THE PAYMENT RAIL / ECOSYSTEM> — <count>+ endpoints across
<chains>.

Happy to walk you through <the dashboard / live state> whenever. What's the best way to
keep you posted?
```

## Example (the actual message that worked)

> Hey, appreciate you checking in! The agentic treasury is moving well. **$TREASURY is live on
> Robinhood Chain** — 100B supply, Uniswap V4 pool, 95% creator fees, the first token
> purpose-built for agent treasuries.
>
> We've built out the full **Steward** — an autonomous treasury manager running in full-autonomy
> mode. It reads live market regime, manages LP positions, and auto-rebalances when out of range.
> Live dashboard at gentechlabs.net/Treasury.
>
> The best part — we just **proved the exit rail end-to-end**. I asked the treasury to send funds
> back to my wallet, and it did — real USDC landed in my Coinbase wallet. So it's not just a demo:
> the agent can both earn *and* return funds to the owner on command. That's the whole point of an
> agentic treasury.
>
> Right now the live position is being redeployed after that test, and the whole thing sits on our
> **x402 payment rail** — 15+ pay-per-call endpoints in USDC across Base, Polygon, and Arbitrum,
> Bazaar-indexed.
>
> Happy to walk you through the dashboard or the Steward's live state whenever. What's the best way
> to keep you posted?

## Verification checklist (run before sending any link or live-state claim)
- On-chain wallet balance matches what the message says (raw RPC `eth_getBalance`, `balanceOf`).
- Active positions / LP state confirmed from 2+ independent reads.
- Cron / automation jobs described as "live" are actually enabled (check the cron jobs list).
- Every URL: HTTP 200 + content confirms it's the right page (title/keywords).
- Live endpoint count in the message matches the manifest (e.g. `15+`, not an invented higher number).
