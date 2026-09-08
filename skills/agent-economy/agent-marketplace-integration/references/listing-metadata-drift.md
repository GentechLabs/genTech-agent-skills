# Listing Metadata Drift — the "wrong sign on the door" trap

**Date:** 2026-08-26
**Source incident:** Bankr skill zero-traction diagnosis + fix
**Also taught as:** GenTech Academy Module 5, Lesson 5.4 "The Metadata Trap"

## The core lesson

A marketplace listing is a **promise**. If the route or chain it advertises
doesn't resolve to a real, working endpoint, the listing is dead — no matter
how healthy the underlying gateway is. Health checks passing on your real
gateway is NOT the same as your listing converting. The listing is the
*contract* agents see first; if that contract is wrong, nothing else matters.

Distinct from the **placeholder trap** (endpoint exists but returns garbage):
in the metadata trap the endpoint *doesn't exist at all* but the listing
claims it does → agents get 404 and bounce → zero traction, zero revenue.

## Real incident (Bankr, Aug 26 2026)

| Metadata field | What it advertised | Reality |
|----------------|-------------------|---------|
| Route | `GET /api/v1/treasury` | Returned **404** — no such route ever existed |
| Chain | `robinhood` | Gateway settles on base/solana/avalanche/xlayer/algorand — Robinhood not on it |
| Services | AgentScan, Airdrop Checker, Shipping Tracker | Not in the live manifest at all |
| Actual services | (silent) | 10 real live services: token_security, wallet_analysis, defi_lp_analytics, etc. |

The skill *looked* complete. Every advertised route 404'd on a chain the
gateway didn't serve. Agents who tried it bounced.

## How metadata drifts

1. You rename a route (`/api/v1/agentscan` → `/v1/agents/search`) but forget to update the listing.
2. You add/drop a chain but the listing still says the old list.
3. You deprecate a service but the old entry stays in the catalog.
4. You build the skill once and never re-check it against the live manifest.

Metadata is written once at launch, then the gateway keeps evolving and the
listing freezes. That's the drift.

## The audit recipe (per listing)

1. **Fetch the live manifest** — `curl /.well-known/x402-bazaar`. Single source of truth: routes, prices, chains, services.
2. **Diff the manifest against every listing.** For each: every advertised route returns a real status (200/402) not 404; every advertised chain is one the service actually settles on; price matches; no dead services still advertised.
3. **Probe the actual endpoints** — `curl -o /dev/null -w "%{http_code}"` → want **402** (paid, healthy) or **200** (free), NEVER 404.
4. **Fix and re-verify** — update the listing, push, re-probe until every advertised route resolves.

## The one-source-of-truth rule

> **Never hand-write service metadata. Derive it from the live manifest.**

The moment you hand-maintain a list of endpoints in a skill or listing, it
starts drifting the day you change the gateway. A listing that says "see the
live manifest for services" can never go stale.

## Per-site schema — NOT copy-paste

The content (services/routes/chains) is the same everywhere, but the FORMAT
differs per marketplace. Do NOT reuse one site's format on another — it won't
validate. For each marketplace, FIRST read its own docs/schema, THEN map the
live manifest into that schema. A sweep is **one manifest → N schemas**.

| Marketplace | Catalog format | The gotcha |
|---|---|---|
| Bankr | `catalog.json` (slug must = folder) + `SKILL.md` frontmatter | Schema-validated; wrong slug = skipped entirely |
| gold-402 | Markdown table row in `directory/apis.md` | Free-form text |
| OKX | A2MCP agent listing + x402 challenge compliance | Requires live A2A node + correct challenge header; rejects if offline |
| CDP Bazaar / Dexter | Settle → auto-index | Indexes on settlement, not on listing |
| Swarms | Manual profile edit (no API) | Human logs in, toggles x402, edits fields |
| Atelier | API-key agent profile | Credentials-based, Solana-focused |

Reference our own per-protocol connector guides: `10-Labs/x402-gateway/connectors/`.

## Shipping checklist

- [ ] Every advertised route returns 200 or 402 (never 404)
- [ ] Advertised chains match what the gateway actually settles on
- [ ] Prices match the live manifest
- [ ] No dead/renamed services still advertised
- [ ] The listing points at the live manifest as the source of truth
- [ ] Re-audit scheduled (metadata drifts; check on a cadence, not once)

## PR-from-private-fork pitfall (same session)

Opening a PR to a public repo from a **private** fork fails with
`GraphQL: not all refs are readable (createPullRequest)` — GitHub can't expose
a private fork's refs. Fix: create a **public** fork under the clean account
(`gh api -X POST repos/<upstream>/forks`), push the branch there, then
`gh pr create --head <clean-account>:<branch>`. Verify the fork is public +
has the branch before opening the PR.
