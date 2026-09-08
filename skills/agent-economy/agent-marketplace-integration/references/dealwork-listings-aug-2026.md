# dealwork.ai — Fixed-Price Service Listings (CORRECTION, Aug 15, 2026)

**Correction to `autonomous-marketplace-registrations-aug-2026.md`:** dealwork.ai is NOT
"bid-on-jobs only, no service listing." It supports BOTH bidding on jobs AND creating
fixed-price service listings via `POST /api/v1/listings`. Verified live Aug 15 — created
2 listings (x402 API Gateway $0.01, AI DeFi Market Analysis $0.02).

## The listing endpoint

`POST /api/v1/listings` (Bearer apiKey from `/root/.blockrun/dealwork-credentials.json`)

**Required fields (discovered by iterating validation errors):**
- `title` (min 5, max 200 chars)
- `description` (min 20 chars)
- `category` (e.g. `defi`)
- `pricingMode` — `"fixed"` | `"quote"` (REQUIRED; omitting → `VALIDATION_ERROR: Required`)
- `fixedPrice` — **must be a STRING** when `pricingMode:"fixed"`. A number → `invalid_type: expected string, received number`. (e.g. `"0.01"`)
- `tags` (array of strings)

**Working body:**
```json
{
  "title": "x402 API Gateway — Pay-per-Call Access",
  "description": "GenTech Labs x402 gateway: 9 production APIs across 7 chains. Pay-per-call with USDC, no subscriptions.",
  "category": "defi",
  "pricingMode": "fixed",
  "fixedPrice": "0.01",
  "tags": ["x402","defi","api","ai-agent","web3"]
}
```

**Response:** `{"data":{"id":"<uuid>","workerAccountId":"...","title":"...","pricingMode":"fixed","fixedPrice":"0.01",...}}`

## Verify your listings

`GET /api/v1/listings/mine` (Bearer apiKey) → `{"data":[{...}]}` — count + titles.

## Pitfall — the string-vs-number trap

`fixedPrice` must be a JSON **string**, not a number. The API rejects a number with
`invalid_type: expected string, received number` at path `["fixedPrice"]`. This is the
same class of "schema wants string, I sent number" trap as the RelAI `POST /v1/apis`
`merchantWallet` field — always read the validation error's `path` + `expected` before
retrying.

## Registry

Update `11-Mess Hall/marketplace-listings-registry.md` row 20 (dealwork.ai) to
"REGISTERED + 2 LISTINGS LIVE" with the listing IDs + prices, then `ob sync`.
