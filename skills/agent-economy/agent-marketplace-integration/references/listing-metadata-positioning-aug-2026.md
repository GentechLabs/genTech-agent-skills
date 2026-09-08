# Metadata & Positioning — "List what the market should SEE, not just what you built" (Aug 24, 2026)

## The lesson (Jordan, explicit)
> "We can also add this as a lesson that metadata is important as well for listing your APIs correctly."

GenTech's canonical product is the **Agentic Treasury + x402 infrastructure** (the under-served gap in the
agent economy). But the live public metadata led with **"Rugcheck v2 / Token security"** — the SATURATED
category (GoPlus, RugCheck, RugCheck AI own it). We built treasury-first but LISTED security-first, so the
market saw a generic security API instead of a differentiated treasury. No traction, because the market
saw a crowded commodity.

**Rule:** whenever the product story changes, audit EVERY public-facing metadata surface, not just the code.
A service re-positioned in code but not in registry/metadata is invisible.

## What to audit per listing surface
- **Name** — lead with the differentiated category, not a commodity label.
  - ❌ `"name": "GenTech Labs"` (ambiguous) / `"Token Security API"`
  - ✅ `"name": "GenTech Labs — Agentic Treasury + x402 Rail"`
- **Description** — open with the under-served value prop; name saturated categories only as supporting services.
- **Service order** — put differentiated services FIRST (yield scan, treasury wallet deploy, ERC-8004 identity),
  commodity ones last (token security).
- **tags / domains** — reflect new positioning (treasury, yield, payments, infrastructure) so search/filter surfaces it.

## Files fixed Aug 24 (all three, keep in sync)
1. `gentech-avax-metadata.json` — the ERC-8004 agent metadata (name, description, service order, tags).
2. `/var/www/gentechlabs/.well-known/x402-bazaar` — the LIVE bazaar manifest the gateway serves.
3. `gentech-gateway-skill.md` — the SKILL.md agents read to learn the gateway.

## PITFALL — edit the manifest the gateway SERVES, not the `server.py` strings
`server.py` loads the manifest from `MANIFEST_PATH = "/var/www/gentechlabs/.well-known/x402-bazaar"` at startup.
The `description` strings hardcoded in `server.py` are the GENERIC OpenAPI info, NOT what
`GET /.well-known/x402-bazaar` returns. To change the served listing:
1. Edit `/var/www/gentechlabs/.well-known/x402-bazaar` (the JSON file on disk).
2. `systemctl restart x402-api.service`.
3. Re-verify the live 402 challenge / `GET /.well-known/x402-bazaar`.
`grep server.py` for the served string finds NOTHING — it's read from disk, not inlined. Same for the earlier
description edits: verify against the LIVE endpoint, not the source.

## agentic.market / Bazaar resource-level metadata
The 402 `resource` block should carry 3 optional Bazaar fields for searchability/filterability:
```python
"resource": {
    "url": "...",
    "description": "...",
    "mimeType": "application/json",
    "serviceName": "Tech <Service>",                     # ≤32 printable ASCII
    "tags": ["x402","treasury","defi","yield","intelligence"],  # ≤5, each ≤32 ASCII
    "iconUrl": "https://gentechlabs.net/gentech-logo.png" # absolute https, no IP literal (SSRF defense)
}
```
Validation: facilitators apply soft-drop — a bad field is silently discarded, rest preserved.

## Catalog trigger (reiterate — already in SKILL.md Pitfalls)
Server-side declaration + real on-chain settlement is STILL not enough if the buyer's client drops the
`extensions.bazaar` object from the PaymentPayload. The facilitator only catalogs what it sees echoed in the
payload. Check the facilitator `/settle`/`/verify` response for `EXTENSION-RESPONSES`:
- `{"bazaar":{"status":"processing"}}` = accepted (may index async, wait up to ~6h)
- `{"status":"rejected","rejectedReason":...}` = schema fail
- **no header at all** = client dropped the extension → nothing catalogs
The self-settle client MUST register the bazaar extension (`enrichPaymentPayloadWithExtensions` returns early
when `registeredExtensions.size === 0`; registering only `ExactEvmScheme` is not enough).
