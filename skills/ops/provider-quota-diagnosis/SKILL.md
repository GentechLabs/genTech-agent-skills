---
name: provider-quota-diagnosis
description: "Diagnose provider usage, rate limits, and quota resets across Hermes providers (Z.AI, OpenCode Go, Nous, Gemini, etc.). Decodes stale credential-pool status, finds real reset times, and live-tests endpoints before declaring a provider down."
author: Gentech
category: ops
tags: [usage, rate-limit, quota, diagnostics, auth, providers]
---

# Provider Quota & Rate-Limit Diagnosis

Answer the recurring questions — "how's our usage?", "when does the rate limit reset?", "is Z.AI down?" — with evidence, not stale status screens.

## When This Skill Applies

Trigger conditions (any one):
- User asks about usage, quota, spend, or rate-limit status
- `hermes auth list` shows `rate-limited` / `exhausted` for a provider
- A provider's requests are failing with HTTP 429 / quota errors
- Planning heavy work (cron batch, big build) and need to know which providers are actually usable

## Core Principle

**The credential pool in `auth.json` is a snapshot of the LAST failure, not a live probe.**
`last_status: exhausted` + `last_error_code: 429` does NOT prove a provider is down.
The status persists indefinitely until a successful retry — it can be weeks stale
(observed: error recorded Jul 9, reset Jul 11, status still showed "rate-limited" on Jul 31).

Never escalate, switch providers, or tell the user a provider is down based on status alone.

## Diagnosis Recipe

### Step 1 — Read the real error detail from auth.json

The read_file tool guard blocks `auth.json` (credential store), but terminal can read it:

```bash
cd /root/.hermes/profiles/gentech && python3 -c "
import json
d = json.load(open('auth.json'))
for prov, creds in d.get('credential_pool', {}).items():
    for c in creds:
        print(f'{prov}: {c.get(\"last_status\")} — {c.get(\"last_error_message\", \"OK\")} — {c.get(\"last_status_at\")}')
"
```

- `last_error_reason` values like `"1310"` are opaque codes — ignore them
- The actionable detail is in `last_error_message` (e.g. "Your limit will reset at 2026-07-11 04:38:41")
- `last_status_at` is a unix epoch — convert to compare with now

### Step 2 — Compare the stored reset time to now

If the reset timestamp in `last_error_message` is in the PAST, the key is very likely usable again.
The status is stale, not the limit.

### Step 3 — Live-test the endpoint before trusting either status

Tiny, cheap inference call — a valid response proves the key works NOW:

```bash
# Z.AI example (~11 tokens, negligible cost)
KEY=$(grep -E "^GLM_API_KEY=" .env | head -1 | cut -d= -f2-)
curl -s --max-time 45 https://api.z.ai/api/coding/paas/v4/chat/completions \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"model":"glm-4.5-flash","messages":[{"role":"user","content":"ping"}],"max_tokens":5}'
```
A `choices` array in the response = key works.

## Provider-Specific Notes

### Z.AI / GLM
- Coding endpoint: `https://api.z.ai/api/coding/paas/v4/chat/completions` (base_url shown in auth.json credential pool)
- **Misleading endpoint:** `https://api.z.ai/api/monitor/usage/quota/limit` returns `{"code":500,"msg":"当前用户不存在coding plan"}` for coding-plan keys — NOT proof the key is dead. Test the inference endpoint instead.
- Keys live in `.env` as `GLM_API_KEY` and `ZAI_API_KEY`
- `check-zai-usage.sh` falls back to "check dashboard manually" when the key isn't in shell env — source `.env` first or use the live-test above
- Coding-plan limits are 5-hour rolling (10M) + daily (50M); see `zai-usage-monitor` skill for threshold guidance

### OpenCode Go
- Error shape: `GoUsageLimitError`, message includes "Resets in N days" — that's the real reset window (e.g. monthly limit hit Jul 30 → resets ~Aug 8)
- `last_status: exhausted` with that message = genuine quota exhaustion, unlike stale Z.AI flags
- **No usage endpoint.** `/v1/usage`, `/api/usage`, `/v1/limits` all return the dashboard HTML (SPA), not JSON. Detect state by **live-testing a model call** instead: `POST {base}/chat/completions` with a small prompt. A `GoUsageLimitError` / "usage limit" in the error body = exhausted; a `choices` array = usable.
- **Model names are bare** (`deepseek-v4-flash`, `minimax-m3`), NOT slash-prefixed (`deepseek/deepseek-v4-flash` returns `ModelError: not supported`).
- **Use a non-China-hosted probe model** (e.g. `minimax-m3`) — `deepseek-v4-flash` may return a `RegionError` (China-hosted, needs opt-in) that is NOT a quota signal. Pick a model that returns either a completion or a clean `GoUsageLimitError`.
- **Monthly is the binding constraint** (resets ~30 days); weekly/rolling are separate and usually fine. The dashboard shows Monthly/Weekly/Rolling — the monthly cap is what exhausts.

### Ollama Cloud
- **Usage endpoint is `/api/usage`, NOT `/v1/usage`.** `https://ollama.com/v1/usage` returns `{"error":"path \"/v1/usage\" not found"}`. The real endpoint `https://ollama.com/api/usage` (Bearer `OLLAMA_API_KEY`) returns `limits.weekly.usage` and `limits.session.usage` as fractions (0.0-1.0) plus per-model request counts. Verified Aug 2026.
- **Weekly is the binding constraint** (resets every 7 days); session resets every ~5h. The dashboard shows "Weekly usage" and "Session usage" — read both from `/api/usage`.
- **No `/v1/plan` endpoint either** — the plan/limits live in `/api/usage`'s `limits` object, not a separate call.

### Nous Portal (primary provider)
- Check `hermes status` — shows access token expiry; refresh BEFORE long cron batches
- **The visible "Access exp" is the HOURLY OAuth access-token rotation, NOT a balance problem.** The JWT `exp - iat == 3600` (1 hour); it auto-renews via the refresh token stored alongside it. Do not alarm the user about it — it is not a spend or quota signal.
- **Balance lives in the JWT claims, not the API.** The inference API returns 404 for `/v1/usage`, `/v1/balance`, `/v1/me`, `/v1/account/usage`. Read `member_spend_usd` (spend this period), `paid_access`, `member_spend_cap_exceeded`, `subscription_tier` from the access token:
```bash
python3 -c "
import json, base64
d = json.load(open('/root/.hermes/shared/nous_auth.json'))
def find(o):
    if isinstance(o, dict):
        for k,v in o.items():
            if 'access' in k.lower() and isinstance(v,str) and len(v)>50: return v
            r = find(v)
            if r: return r
    return None
t = find(d)
p = t.split('.')[1]; p += '=' * (-len(p) % 4)
for k,v in json.loads(base64.urlsafe_b64decode(p)).items():
    if 'spend' in k or 'paid' in k or 'tier' in k or 'cap' in k: print(f'{k}: {v}')
"
```
- `paid_access: true` + `subscription_tier: 2` + spend ~$1 → the account is active; no top-up needed. The portal dashboard may show a different balance than the API — when user asks about dollars, quote the JWT number AND tell them the dashboard is authoritative for top-ups.
- **Terminology:** the Nous balance is the research-portal subscription balance — NEVER call it "the grant." User explicitly corrected this (Aug 2026). It is not grant funding and it is not "spent" in the grant sense.
- See `hermes-auth-incident-response` for actual OAuth recovery.

## Pitfalls

| Pitfall | How to avoid |
|---------|--------------|
| Trusting `hermes auth list` rate-limit status | It's the last failure snapshot, possibly weeks old. Decode `last_error_message` reset time, then live-test |
| Reading `last_error_reason` ("1310") as meaningful | It's an opaque code. The reset time lives in `last_error_message` |
| Concluding a key is dead from a quota-monitor endpoint 500 | Monitor endpoints often don't serve coding-plan keys. Test the actual inference endpoint |
| Quoting a provider as "down" to the user without a live test | Always verify with a real request first; a live 200 changes the whole answer |
|| Reporting reset as "someday" | Convert timestamps to a concrete date (UTC + ET) so the user gets a real answer |
| `credits_notices: true` spamming free-model responses | When Hermes is on a free tier (Nous `solar-pro4:free`, BlockRun `free/gpt-oss-120b`, etc.), the global `credits_notices` flag prepends a cost/balance notice to every response. This can produce incoherent warnings like "⚠️ Insufficient balance — send USDC to `0xebc8...`" even when no wallet is funded or no real spend is happening. To silence: set `credits_notices: false` in the profile's `display:` block (`~/.hermes/profiles/<profile>/config.yaml`). Keep it `true` only when actively spending a paid provider and the user wants per-turn cost visibility. For finer control, `show_cost: false` suppresses the cost line without the full balance preamble. Each profile has its own `display:` block — silencing it in one profile does not affect others. |

## Related Skills

- `zai-usage-monitor` — Z.AI quota thresholds and alerting (manually authored; do not auto-edit)
- `hermes-auth-incident-response` — OAuth token expiry recovery (manually authored; do not auto-edit)
- `cron-truth-layer` — verify cron data before reporting it

## References

- `references/stale-rate-limit-diagnosis-2026-07-31.md` — full worked example: stale Z.AI status, reset-time decoding, live-test proof, companion findings
- `references/provider-auto-switch-pattern.md` — reusable pattern for automatically failing over between Ollama Cloud (weekly reset) and OpenCode Go (monthly reset) based on live usage, with the context-save-before-restart safety step
