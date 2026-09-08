# Agentic.Market — Validation & Listing Reference

**Date:** 2026-07-03
**Source:** Hands-on validation session via browser

---

## Status: NOT LISTED

Confirmed: `curl "https://api.agentic.market/v1/services/search?q=gentech"` returns empty.
`curl "https://api.agentic.market/v1/services/search?q=0x7ebff188"` returns empty.

## How Listing Works

From the validator FAQ:
> "If your service/endpoints are indexed on the Bazaar, you'll automatically show up on agentic.market."

**The Bazaar** is the x402 protocol-level discovery index. Agentic.Market is a front-end that pulls from it. Services are indexed by the Bazaar crawler when:

1. A valid x402 manifest is served at `/.well-known/x402` or `/.well-known/x402-bazaar`
2. **At least one real verify+settle transaction has completed** on a paywalled endpoint

**The first verified payment triggers Bazaar indexing**, not the presence of the manifest alone. This means we need someone (even ourselves) to make a real USDC payment to one of our endpoints to appear in search results.

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `https://api.agentic.market/v1/services` | GET | Full service list |
| `https://api.agentic.market/v1/services/search?q={query}` | GET | Search by name/keyword |
| `https://agentic.market/validate` | Web | Validation tool |
| `https://agentic.market/validate/setup/endpoint` | Web | Setup wizard (new services) |
| `https://agentic.market/api/markdown` | GET | Full catalog as markdown |
| `https://agentic.market/llms.txt` | GET | LLM-readable docs |

## Validator Behavior

The validator at `agentic.market/validate` checks a single endpoint URL (without protocol prefix):

1. Enter URL like `api.gentechlabs.net/api/token/risk`
2. Select HTTP method (default GET)
3. Click "Validate"

**Results observed:**

| Endpoint | Result | Status |
|----------|--------|--------|
| `api.gentechlabs.net/.well-known/x402-bazaar` | ❌ "No x402 Setup Detected" | Returns 200 (correct for discovery), but validator expects 402 |
| `api.gentechlabs.net/api/token/risk` | ✅ "Implementation Looks Correct" | Proper 402 with payment manifest |
| `api.gentechlabs.net/api/agentscan` | ❌ "No x402 Setup Detected" | Returns 500 (em dash btoa() bug) |

The passing validation message: **"All checks pass and the SDK would index this endpoint. It just needs its first verify+settle to appear in the Bazaar."**

## Full Catalog

Full service catalog available as markdown at `https://agentic.market/api/markdown` (353K chars, ~1,494 services listed as of Jul 3, 2026).

Categories include: Inference, Data, MCP/Server, Productivity, Email, Communication, Ecommerce, Media, Storage, Travel.

## Action Items to Get Listed

1. [ ] **Fix agentscan 500** — Deploy the em dash fix to production (needs Cloudflare API token)
2. [ ] **Trigger first payment** — Send a tiny USDC payment (e.g. $0.001) to one of our endpoints using the x402 protocol
3. [ ] **Verify listing** — After payment settles, check `https://api.agentic.market/v1/services/search?q=gentech` every few minutes
