# x402scan Manual Registration — Working Recipe (verified Aug 24, 2026)

The manual "Add API" form at `x402scan.com/resources/register` is the **reliable**
listing path. Do NOT wait for a settlement to auto-index you — the CDP settle→index
path is a proven-broken platform gap (x402-foundation #2112, #3045). Manual works.

## Why this corrects the earlier belief
The skill previously said x402scan was "activity-driven — servers appear after real
on-chain usage." That is FALSE for listing. We settled 0.015 USDC on Aug 19 to test
the settle→index theory and stayed at 0 on every marketplace. The manual form listed
us immediately. Manual registration is the working path.

## The recipe (proven with the browser tool)
1. `new_tab("https://www.x402scan.com/resources/register")` — page title "🐴 Add API".
2. Set the URL field (placeholder `api.example.com`) to `api.gentechlabs.net`:
   use the native value setter + dispatch `input` event (React-controlled input).
3. The form auto-scans the URL and renders a **PREVIEW** of all endpoints
   (description, GET routes, etc.). This preview looks like "you're already listed"
   — it is NOT a listing, it's the form reflecting the scanned manifest. Do not
   conclude "already listed" from the preview.
4. The Add API button is **disabled** with text "Checking 0/9 endpoints..." until
   validation completes (scans each live endpoint). Wait for the count to finish;
   the button text becomes "Add API (9 resources)" and re-enables.
5. Click the enabled Add API button. Success response: **"Successfully registered
   9 of 9 resources"** plus a merchant share link (e.g. `tryponcho.com/m/api.gentechlabs.net`).
6. Verify separately: the platform's "Most Used"/featured marketplace page ranks by
   request volume, so a fresh registration may NOT appear there immediately. Confirm
   the registration via the platform's own success confirmation rather than expecting
   instant visibility on ranking pages. There is no public `/docs` page (404) and
   merchant-page URL patterns (`/resources/<url>`, `/merchant/<url>`) 404; the
   registration is verified by the platform's success message, not a public profile.

## Pitfalls
- **The preview is NOT a listing** — a form that auto-scanned and displays your 9
  endpoints is not proof you're registered. You must click the real submit button.
- **Don't use curl** for the register page — it's a Next.js SPA; the API endpoints
  aren't server-side-rendered. Use the browser tool.
- **Multi-facilitator gateway is the right setup** for this marketplace: CDP
  (Coinbase) is the #1 volume facilitator on x402scan (100K txns / $36K / 24h).
  Our gateway wires CDP `/verify`+`/settle` for Base/EVM plus PayAI + GoPlausible
  for Avalanche. Verify CDP vars are set in the live service env
  (`EnvironmentFile=/root/.hermes/profiles/gentech/.env`): `CDP_API_KEY`,
  `CDP_API_KEY_ID`, `CDP_API_KEY_SECRET`, `CDP_WALLET_SECRET`.
- **PayTo check**: confirm live `X402_PAYTO_*` env points to the wallet we control
  (0x7ebf…1296a) across all chains.

## Demand / discovery context (why listing matters)
x402scan global stats (Aug 24): 13.29M txns, $1.24M volume, 22K buyers, 29K sellers.
Top facilitator is Coinbase CDP. Fresh registrations climb "Most Used" ranking once
they get request volume — that's the discovery lever for first paying customer.
