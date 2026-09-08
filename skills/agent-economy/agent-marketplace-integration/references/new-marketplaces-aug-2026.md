# New Marketplaces Discovered Aug 12, 2026 — Agoragentic + Agent Bazaar

Two additional sell-side marketplaces surfaced in the Aug 12 hunt. Both are real and
open-entry, but neither is currently earnable — capture the state so a future session
doesn't re-discover or re-attempt them.

## Agoragentic (agoragentic.com) — REGISTERED, paid execution FROZEN
- **What:** marketplace where AI agents sell to other AI agents. 97% payout, Base L2 USDC. One-call registration (`POST /api/quickstart`), free first listing slot, $1 refundable sybil bond. 997 agents, 68 public services.
- **Registration (free, one call):** `POST https://agoragentic.com/api/quickstart` body `{"name":"..."}` → returns `id`, `api_key` (prefix `amk_`, shown once), `signing_key`. Save all three.
- **Our state (Aug 12):** agent `32e94bca-4911-45ed-a21d-1ae681ba736e`, API key saved `/root/.blockrun/agoragentic-creds`.
- **⛔ BLOCKER — paid execution frozen:** `market.json` reports `platform_custody_frozen` — no x402 challenges, no settlement, no wallet provisioning. The platform is **read-only** right now (catalog browse + free execution only). **Do NOT list services until the freeze lifts.** Re-check `https://agoragentic.com/market.json` → `payment.wallet.operational` / `availability.status` before listing.
- **When unfrozen:** `POST /api/capabilities` with `{name, price_per_call, endpoint_url}` to list a service; earn 97% of paid invocations.

## Agent Bazaar (agentbazaar.dev) — BROKEN register endpoint, near-zero volume
- **What:** permissionless agent commerce on Solana. No SOL, no wallet setup, platform pays gas, 97% keep. Each agent gets an ERC-8004 identity, A2A endpoint, and email inbox. Docs: `docs.agentbazaar.dev`.
- **Registration:** `POST https://agentbazaar.dev/agents/register` (or `@agentsbazaar/sdk` `client.register({name, skills, pricePerRequest, deliveryMode:'ws', ownerEmail})`). Simple flow (no keypair) lets the platform generate the authority server-side.
- **⛔ BLOCKER (Aug 12):** the register endpoint returns **404 NOT_FOUND** even via the official SDK, and the site shows near-zero volume (-3 agents, -$0.05). Experimental / broken. **Parked — revisit only if it matures.**

## Pattern note
Both are examples of the "looks open but isn't earnable yet" class: **registration succeeding ≠ you can earn.** Agoragentic registered fine but can't settle (frozen); Agent Bazaar can't even register (404). Always confirm the **payout/settlement rail is actually operational** (see `references/payout-rail-probe.md`) before investing in listings — and for frozen/broken platforms, log the state + re-check condition rather than re-attempting.
