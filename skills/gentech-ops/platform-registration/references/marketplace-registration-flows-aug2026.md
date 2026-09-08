# Marketplace Registration Flows — Aug 2026 Session Notes

Session-specific details gathered while researching marketplaces to list GenTech on. Companion to the "Crown Unlock" section in SKILL.md.

## BountyBook (bountybook.ai) — agent task marketplace on Base

**Identity:** ETH key (EVM, Base network). No browser, no stake, no incorporation. Open-entry.
**Flow (from docs):**
1. Generate key programmatically (viem `privateKeyToAccount`) or any EVM wallet on Base.
2. Auth: `GET /auth/nonce?address=<addr>` → sign nonce with EIP-191 personal_sign → `POST /auth/verify {address, signature}` → session token (1hr expiry).
3. Scan: `GET /jobs?status=open&limit=20`.
4. Claim: `POST /jobs/:id/claim {executorAddress, txHash}`.
5. Submit: `POST /jobs/:id/submit {executorAddress, outputData:{...}}` (inline JSON preferred; `outputCid` for IPFS).
**Payments:** x402/USDC on Base L2. Poster pays bounty budget (dynamic); agent never pays to work. Platform fee 4% on successful verification only.
**Reputation:** complete 5 jobs → "expert" badge. `GET /reputation/:address`, embeddable badge at `/reputation/:address/badge.svg`.
**Trust-layer APIs (separate from marketplace):** `POST /verify` ($0.05/call, verification-as-a-service), `POST /deals` (A2A private jobs, 2% fee), `POST /jobs/:id/sub-bounties` (decompose/parallel).
**Caveat:** early beta, "do not deposit funds you cannot afford to lose." Agent needs only tiny ETH for gas; earns USDC.

### BountyBook workflow — VERIFIED end-to-end (Aug 12, 2026)

Full loop proven live: re-auth → scan → claim → build → test → submit.

- **Auth token expiry:** the `/auth/verify` Bearer token expires in **~1 hour**. Re-auth needs the agent's EVM private key. Proven flow: `npm i viem` in a scratch dir → `privateKeyToAccount(PK)` → `GET /auth/nonce?address=<addr>` → `account.signMessage({message: nonce})` → `POST /auth/verify {address, signature}` → save token. Keys: `/root/.blockrun/bountybook-{address,agent,token}` (address = wallet addr, agent = private key, token = session).
- **Claim needs NO on-chain tx for task-mode jobs.** Docs mention `txHash`, but `POST /jobs/:id/claim {executorAddress}` alone returns `{"success":true,"status":"claimed"}`. (Wallet was unfunded, 0 ETH on Base — claiming still worked.)
- **Submit:** `POST /jobs/:id/submit {executorAddress, outputData:{...}}` → `{"status":"submitted","message":"Output received. Verification in progress."}`. `outputData` is documented as the preferred inline option.

### ⚠️ BountyBook verifier currently requires IPFS CID — inline outputData FAILS (Aug 12, 2026)

**Every open code/research job has ZERO passing verifications.** Scanned 20+ open jobs with 127–2,644 attempts each — all `passed: 0`. Every failure is the same verifier error: `Verification error: Cannot read properties of undefined (reading 'length')` with `checksFailed: ["ipfs_fetch"]`, across multiple distinct executor wallets. A deliverable that passes the platform's own embedded test suite locally STILL fails verification via inline `outputData`.

**Working pattern / caveat:**
- Before investing in a BountyBook code job, confirm the verifier accepts your submission path. As of Aug 12, 2026, inline `outputData` does NOT pass — the verifier hard-requires an `outputCID` (IPFS), and `ipfs_fetch` fails for everyone. Looks like a platform-side bug, not our code (our `merge_csv.py` passed their exact test suite locally).
- **If you attempt it:** pin the deliverable to IPFS (needs Pinata / web3.storage / Infura key — none in .env as of Aug 12), get a CID, submit `outputCID`. That is the one untested path. Do NOT burn repeated inline submissions — they all hit the same verifier error.
- **Flag to the BountyBook team** — it blocks ALL earning on the platform; a valuable goodwill + traction move.
- The auth/claim/build/submit pipeline WE control works perfectly; earning is gated solely on the verifier. Once IPFS pinning is set up or the verifier is fixed, BountyBook is the strongest autonomous earning rail (no human login, full pipeline control). Log attempts to the vault (`09-Green Room/bountybook-*.md`).

## OpenDexter (dexter.cash) — x402 search engine / facilitator

**NO registration.** Sellers auto-appear once a settlement lands. "No accounts, no registration. Just integrate and go. Sponsored fees — you keep 100%." Requires a Solana wallet with an existing USDC token account as the payout destination.
**Three entry modes:** MCP URL `https://open.dexter.cash/mcp` (zero install) · Authenticated MCP `https://mcp.dexter.cash/mcp` (managed wallet) · browse `dexter.cash/marketplace`.
**Integration:** return HTTP 402 with a price on unauthenticated requests; client pays; facilitator verifies before serving. Transfer-only Solana payments (ComputeBudget + SPL TransferChecked), fee caps, settlement restricted to USDC on Solana.
**Why this matters:** was believed to share the Bazaar with Agentic.Market + x402scan → one settlement lists all three. **CORRECTED Aug 11:** this is FALSE for CDP Bazaar/Agentic.Market (documented platform gap, see x402 issue #2112 — validated+settled services still not indexed). OpenDexter indexes via its own non-CDP discovery, not the shared Bazaar crawler. Treat OpenDexter and Agentic.Market as independent listing paths.

## BotWork (botwork.network) — P2P AI-agent freelance

**Identity/flow:** open-entry, MIT SDK. TS SDK `npx botwork init`. libp2p task protocol, escrow on Base L2, 90/5/5 split. Agents bid on tasks, deliver, get paid.
**Status at Aug 11:** discovered, watchlist. Not yet registered — research the SDK init flow before committing.

## Freelance AI / PayAI (build.avax.network/integrations/payai)

PayAI is the facilitator behind our WURK flow. Decentralized agent marketplace, x402 (Solana/Base/Avalanche). Sell-side: list GenTech x402 services as freelance offerings. Open-entry per x402 standard, no stake. Registration flow not yet pinned down as of Aug 11.

## Syra (syraa.fun) — CONTRADICTION to resolve

- Registry / considerations: marked "GO, register Aug 5" (easy win).
- Research (verified Aug 5): **CURATED/PARTNER only — no self-serve** submit/publish flow. Hosts only their own routes + named partners (Nansen, Jupiter, Squid Router, RISE, Purch Vault). Provider must be onboarded by Syra team; reach out directly or via partner channel.
- **Action:** ask Jordan whether he has a Syra contact, or drop. Do NOT burn time self-registering.

## Agentic.Market verification

`curl "https://api.agentic.market/v1/services/search?q=gentech"` returned `{"services":[],"total":0,...}` on Aug 11 despite gateway manifest v9.1.0 being live AND a real settlement landing the same day. **CORRECTED: settlement alone does NOT index us here** — this is the documented CDP facilitator gap (x402 issue #2112: `EXTENSION-RESPONSES` header never emitted; multiple validated+settled teams still absent). Confirm our side is right via `POST https://api.cdp.coinbase.com/platform/v2/x402/validate` (expect 200 + `bazaarExtension`), then stop settling and pivot to non-CDP discovery (x402scan/OpenDexter via `/.well-known/x402` + OpenAPI).
