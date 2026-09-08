# The Metadata Trap + Per-Site Schema — listing audit (Aug 26, 2026)

## The metadata trap (why a healthy gateway can earn zero)

**A listing is a promise. If the route or chain it advertises doesn't resolve to a real,
working endpoint, the listing is dead — regardless of how healthy the underlying gateway is.**

Distinct from the placeholder trap (`x402-api-compliance`): placeholder = endpoint exists but
returns garbage; **metadata trap = endpoint doesn't exist at all (404)** yet the listing claims
it does.

### Real incident — Bankr (Aug 26, 2026)
Our Bankr skill advertised `GET /api/v1/treasury` on the Robinhood chain. That route never
existed (404) and Robinhood wasn't a settleable rail. Real rails: base/solana/avalanche/
xlayer/algorand. It also listed services (AgentScan, Airdrop Checker, Shipping Tracker) not in
the live manifest. Result: **zero traction**. The gateway itself was healthy (v9.4.0, 10 live
services) a floor away.

### How metadata drifts
- Route renames (`/api/v1/agentscan` → `/v1/agents/search`) without updating the listing
- Chains added/dropped but the listing keeps the old list (we told Bankr "Robinhood" but never
  settled there)
- Services deprecated but the catalog entry lingers
- Skill built once, never re-checked against the live manifest

### The One-Source-of-Truth rule
**Never hand-write service metadata — derive it from the live manifest
(`/.well-known/x402-bazaar`).** A listing that says "see the live manifest for services" can't
go stale. The moment you hand-maintain an endpoint list, it drifts the day the gateway changes.

### Audit recipe
1. Fetch the live manifest (routes/prices/chains/services).
2. For EVERY marketplace listing, probe every advertised route:
   `curl -o /dev/null -w "%{http_code}"` → expect **402** (paid) or **200** (free), NEVER 404.
3. Confirm advertised chains are ones the service actually settles on.
4. Fix + re-verify until every advertised route resolves.
5. Re-audit on a cadence, not once.

## Per-site schema — NEVER copy-paste a listing format across marketplaces

**Content (services/routes/chains) is the same everywhere; FORMAT differs per marketplace.**
A listing audit is a **per-site** audit, not a one-size-fits-all paste.

| Marketplace | Catalog schema |
|---|---|
| Bankr | `catalog.json` (slug must = folder) + `SKILL.md` frontmatter — schema-validated, wrong slug = skipped entirely |
| gold-402 | markdown table row in `directory/apis.md` (free-form text + links) |
| OKX | A2MCP agent listing + live A2A node + correct x402 challenge header (rejects if offline) |
| Swarms | manual profile edit (no API) — Jordan logs in, toggles x402, edits fields |
| Atelier | API-key agent profile, Solana-focused |
| CDP Bazaar / Dexter | settle → auto-index (no manual listing at all) |

**Rule:** for each marketplace, FIRST read its own docs/schema, THEN map the live manifest into
that schema. Do NOT reuse the Bankr `catalog.json` format on gold-402 — it won't validate. Our
own protocol-by-protocol reference: `10-Labs/x402-gateway/connectors/` (docs the per-protocol
cataloging rules we've hit live).

## Academy lesson
This is codified for students as GenTech Academy Module 5, Lesson 5.4 "The Metadata Trap":
`gentech-academy/modules/05-auditing-your-apis/README.md`. Reuse it when teaching or explaining
why a listing earned nothing.
