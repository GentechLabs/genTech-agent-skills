# Bazaar resource metadata + flagged-GitHub-account 404 (Aug 24, 2026)

Two durable diagnostics from the Agentic.Market / Agent Builders Cup work on Aug 24.

## 1. CDP Bazaar resource metadata — make services searchable on Agentic.Market

**Problem:** A service can have a correct 402 + client echo and still show up weak or
unfilterable on Agentic.Market if the 402 challenge's `resource` object omits the optional
metadata fields.

**Required `resource` fields (from x402-foundation Bazaar spec, "Service Metadata"):**
- `serviceName` — human-readable name, ≤32 printable ASCII characters
- `tags` — up to 5 topical tags, each ≤32 printable ASCII characters (used for facilitator-side filtering + search)
- `iconUrl` — absolute http/https URL to an icon, ≤2048 chars, NO IP literals / loopback (SSRF defense)

**Add them to the route's 402 `resource` block** alongside `url` / `description` / `mimeType`:
```python
"resource": {
    "url": f"https://api.gentechlabs.net/v1/{service_name.lower().replace(' ', '-')}",
    "description": f"GenTech Labs x402 — {service_name}",
    "mimeType": "application/json",
    "serviceName": f"GenTech {service_name}",
    "tags": ["x402", "treasury", "defi", "yield", "intelligence"],
    "iconUrl": "https://gentechlabs.net/gentech-logo.png"
},
```
Then `systemctl restart x402-api.service` and verify live by decoding the `payment-required`
header (base64 JSON) and confirming `resource.serviceName` / `resource.tags` / `resource.iconUrl`.

**Positioning note:** the `bazaar` extension's `info.description` (both in the manifest and in the
402 challenge) is the *positioning* surface the market reads. When the product story changes
(e.g. relisting from "token security" → "agentic treasury"), update BOTH:
- the manifest `description` (e.g. `/var/www/gentechlabs/.well-known/x402-bazaar`)
- the 402 `info.description` in `server.py`
or agents/discovery still see the stale story. This is the same metadata lesson as the
registry/marketplace-listing side: what you advertise is what agents can find, trust, and pay for.

**Config-source gotcha:** the live manifest is NOT the one in `server.py` — it is loaded at
runtime from `MANIFEST_PATH` (e.g. `/var/www/gentechlabs/.well-known/x402-bazaar`). Edit THAT
file (and reorder `services` if you want a new headline order), not just the code.

## 2. Flagged-GitHub-account 404 — "public" repo invisible to anonymous visitors

**The contradiction:** a repo can report `private=false` / `visibility=public` in the authed API
yet return **404 to anonymous visitors**:
- `raw.githubusercontent.com/<owner>/<repo>/main/README.md` → 404
- `github.com/<owner>/<repo>` HTML page → 404

**Why:** this is the **flagged/restricted-account signature** — the same GitHub flag that yields
60/hr core rate limits (vs 5000/hr) and fork-repo 404s. The flag is account-wide; no number of
visibility toggles on an individual repo fixes it.

**Why it matters:** it silently breaks hackathon / competition / sponsor evaluation. A sponsor who
says "the repo looks private" is seeing a real 404 on their side — even though the API says public.

**Diagnostic (definitive):**
```bash
# authed API says public
curl -s -H "Authorization: token $TOKEN" https://api.github.com/repos/<owner>/<repo> | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('private'), d.get('visibility'))"
# anonymous raw + HTML both 404 while API says public → flagged account
curl -s -o /dev/null -w "%{http_code}" https://raw.githubusercontent.com/<owner>/<repo>/main/README.md
curl -s -o /dev/null -w "%{http_code}" -L https://github.com/<owner>/<repo>
```
If authed=public BUT anonymous raw + HTML = 404 → flagged account, not a private repo.

**Fix (not a visibility toggle):** re-host the submission in a clean/untampered org (e.g.
Gentech-Labs — verified NOT flagged via a write test) or on the VPS behind a public URL
(`gentechlabs.net/<artifact>`), and hand that link to the reviewer. The durable fix is the GitHub
account migration; don't waste time toggling visibility on the flagged account.
