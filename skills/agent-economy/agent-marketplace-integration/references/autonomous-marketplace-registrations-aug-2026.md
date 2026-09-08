# Autonomous Marketplace Registrations — Aug 13, 2026 (all verified working)

Four sell-side marketplaces registered **fully autonomously** (no human step) in one session.
All credentials saved to `/root/.blockrun/` (chmod 600). Registry rows updated to ✅ REGISTERED.

## 1. APIHub (apihub.io) — x402/USDC-on-Base, wallet-sign
- **Docs:** `https://apihub.io/llms.txt` (clean, agent-readable)
- **Flow:** `GET /v1/register/challenge` → sign exact `message` with EVM wallet (personal_sign) → `POST /v1/register {wallet_address, signature, nonce}` → `api_key` (prefix `ahk_`)
- **No email/human.** The wallet IS your identity.
- **CLI:** `npx @apihubio/cli` — `apihub add <url>` saves an x402 service to your toolset. Probes the URL: `402 - x402-protected, ready to use` = good; `405` = recorded but not a standard x402 response.
- **Verified:** registered agent `85888284-...`, added `https://api.gentechlabs.net/v1/sie/embeddings` (returned 402 → confirmed x402-protected).
- **Key:** `ahk_cx67YH2p...` in `/root/.blockrun/apihub-credentials.env`

## 2. RelAI (relai.fi) — multi-chain x402, wallet-sign
- **Docs:** `https://relai.fi/llms.txt`
- **Flow:** `POST /mcp/management/bootstrap/agent {publicKey}` → response `{message, step:2}` → sign message → `POST ... {publicKey, signature, message, label}` → `sk_live_` key. Use as `X-Service-Key` header.
- **Supports** Solana (ed25519) OR EVM (secp256k1). Multi-chain: Solana/Base/SKALE/Avalanche/ETH/Polygon.
- **List an API:** `POST /v1/apis` with `{name, baseUrl, network, merchantWallet, endpoints:[{path, method, usdPrice}]}`.
- **⚠️ Rate limit:** `POST /v1/apis` caps at **10 per 24h per IP** (`{"error":"rate_limited"}`). If you hit it, the service key is still valid — retry the API listing later, don't re-bootstrap.
- **Verified:** service key `sk_live_92544c...` obtained; API listing rate-limited (retry later).

## 3. Toku (toku.agency) — real USD payouts, API
- **Docs:** `https://toku.agency/docs` is a JS SPA — probe the API directly at `https://www.toku.agency/api/...` (note the `www.` — bare domain 307-redirects).
- **Register:** `POST /api/agents/register {name, description, email?}` → `{agent:{id, slug, apiKey, profileUrl, referralCode}}`. `name` is required (empty body → `{"error":"name is required"}`).
- **List a service:** `POST /api/services` with `Authorization: Bearer <apiKey>`, body `{title, description, category, tags[], priceCents, pricingModel, deliveryDays}`.
- **⚠️ Pricing models:** Toku only supports `FIXED` (verified — `set(s.get('pricingModel'))` = `{'FIXED'}`). A `PER_CALL` model returns `{"error":"Something went wrong"}`. Use FIXED with a per-call-ish price.
- **Verified:** agent `cmsrlcezo0003l704nj9wg0dm` (slug `gentech-labs`), 2 services live (AI DeFi Market Analysis $10, x402 API Gateway $1). Profile: `toku.agency/agents/gentech-labs`.
- **Key:** `/root/.blockrun/toku-credentials.json`

## 4. dealwork.ai — hybrid human+AI work marketplace, API
- **Docs:** `https://dealwork.ai/skill.md` (rich, versioned)
- **Onboard:** `POST /api/v1/agents/onboard {autonomous:true, agentName, description, capabilityTags[], identityKey}` → `{data:{agentAccountId, apiKey, hmacSecret, claimUrl}}`.
- **`identityKey` (8-256 chars) is STRONGLY recommended** — a stable identifier (agent id, Moltbook id) that lets you RECOVER the account on a sandbox reset instead of creating a duplicate. Use the same key to re-onboard after losing `~/.openwork/credentials.json`.
- **Duplicate guard:** onboarding WITHOUT identityKey + identical name/description within 24h → `409 DUPLICATE_REGISTRATION`. Re-onboard with identityKey to recover.
- **This is a bid-on-jobs marketplace, NOT a service-listing one.** There's no `POST /services` — you bid on jobs (`POST /api/v1/jobs/{id}/bids`). Registration + capability tags are the listing.
- **Income endpoint:** `GET /api/v1/contracts?role=provider` (Bearer apiKey) → `{data:[...]}`. **NOT** `/api/v1/agents/me/contracts` (404s). Poll this in the Revenue Monitor for active provider contracts worth money.
- **Bid rate limits ENFORCED:** 10 bid creations/hour, 3 attempts/job/24h. Honor `Retry-After`. Don't retry a rejected bid.
- **Webhooks** preferred over polling: `POST /api/v1/agents/{agent_id}/webhooks {url, events:[...]}` — wildcard `"*"` NOT supported (400).
- **Verified:** agent `3166b64e-...`, identityKey `gentech-labs-vps-2026`, capability tags live.
- **Key:** `/root/.blockrun/dealwork-credentials.json`

## General pattern (reusable)
1. **Probe the docs first** — most agent marketplaces publish an `llms.txt` or `skill.md` that is clean, agent-readable, and has the exact registration flow. Prefer it over the JS SPA.
2. **Wallet-sign challenge-response is the universal autonomous auth** — `GET challenge → sign exact message → POST signature`. Works on APIHub, RelAI, AgentLux, and most x402-native marketplaces. Use a throwaway EVM wallet (`/root/.blockrun/remit-test-wallet.json`).
3. **Save credentials immediately** to `/root/.blockrun/<platform>-credentials.{json,env}` with `chmod 600`. Never echo keys back.
4. **Update the registry row** (`11-Mess Hall/marketplace-listings-registry.md`) to ✅ REGISTERED with agent id + what's live, then `git commit + push`.
5. **Wire the rail into the Revenue Monitor** so income is tracked (per Jordan's Aug 12 directive).
6. **Rate limits are per-IP and real** — if you hit one, the account/key is still valid; retry the listing later, don't re-register.
