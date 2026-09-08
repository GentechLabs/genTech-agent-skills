---
name: api-safety-testing
description: "Build and run regression test harnesses for paid API endpoints. Covers golden test sets, 402 response validation, schema drift detection, CORS checks, and cron-based automated safety suites."
---

# API Safety Testing

Build regression test harnesses for paid (x402) API endpoints. The pattern: curl each endpoint → validate response shape → check required headers → verify drift against golden sets → alert on failure.

## When to Use

- Before and after gateway deploys
- As a cron job for continuous monitoring
- When adding new endpoints to an existing x402 gateway
- When auditing third-party APIs for compliance

## Core Pattern

```
run_safety_suite.py
├── tests/          # Individual endpoint tests (optional sub-files)
├── golden/         # Known-good response snapshots for drift detection
└── run.py           # Runner script
```

### Test Shape

Each test should verify:

1. **HTTP status** — endpoint returns 402 (not 403/404/200)
2. **Response body** — contains the x402 **v2 gateway shape** (live as of gateway v9). The exact field set is gateway-version dependent — see the diagnostic pitfall below. Current live shape:
   - `x402Version` — integer `2` (camelCase, not snake_case)
   - `resource` — object with `url`, `description`, `mimeType`
   - `accepts[]` — array with valid payment options
   - `extensions` — optional bazaar/x402 metadata
   - `schema` — response schema description
   - NOTE: older gateway versions used a *different* shape (`status`, snake_case `x402version`, top-level `network`/`asset`/`amount`, `payment_address`). Do NOT hardcode either — verify the live response first.
3. **Accepts array** — first entry has `scheme`, `network`, `asset`, `amount`, `payTo` (amount = positive integer string)
4. **CORS headers** — `Access-Control-Allow-Origin: *`
5. **Health endpoint** — returns 200 with `status: "ok"` and often a `gateway` field naming the version
6. **CORS preflight** — OPTIONS request returns proper CORS headers

### Runner Script Template

```python
#!/usr/bin/env python3
import json, os, sys, urllib.request, urllib.error

BASE_URL = "https://api.example.com/v1"
GOLDEN_DIR = os.path.join(os.path.dirname(__file__), "golden")

def check_endpoint(url, method="GET", body=None):
    req = urllib.request.Request(f"{BASE_URL}{url}", method=method,
        headers={"Content-Type": "application/json",
                 "User-Agent": "SafetySuite/1.0",
                 "Accept": "application/json"})
    if body:
        req.data = json.dumps(body).encode()
    try:
        with urllib.request.urlopen(req, timeout=10):
            raise AssertionError(f"{url}: expected 402, got 200")
    except urllib.error.HTTPError as e:
        if e.code != 402:
            raise AssertionError(f"{url}: expected 402, got {e.code}")
        body = json.loads(e.read())
        # Validate required fields — x402-v2 gateway format. VERIFY the live shape
        # before relying on this (see Pitfall: "wholesale 'missing field' failures").
        if "x402Version" not in body:
            raise AssertionError(f"{url}: missing 'x402Version'")
        assert int(body.get("x402Version")) == 2, "unexpected x402 version"
        resource = body.get("resource")
        assert isinstance(resource, dict) and resource.get("url"), "missing resource.url"
        # Validate accepts array
        accepts = body.get("accepts", [])
        assert isinstance(accepts, list) and len(accepts) > 0
        for f in ["scheme", "network", "asset", "amount", "payTo"]:
            assert f in accepts[0], f"{url}: accepts[0] missing '{f}'"
        # Validate amount (inside accepts[0] in v2)
        amt = accepts[0].get("amount", "0")
        assert str(amt).isdigit() and int(amt) > 0, f"{url}: invalid amount"
        # Check CORS
        cors = e.headers.get("Access-Control-Allow-Origin")
        assert cors == "*", f"{url}: CORS not set"
        return body
```

### Endpoint Discovery

Before building tests, discover actual endpoint paths from the gateway:

```bash
# Get endpoint list from OpenAPI spec
curl -s "https://api.example.com/openapi.json" | python3 -c "
import json, sys
d = json.load(sys.stdin)
for p in sorted(d.get('paths', {}).keys()):
    print(p)
"

# Get count from health endpoint
curl -s "https://api.example.com/health" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(f\"{d.get('paid_endpoints', '?')} endpoints\")
print(f\"Free: {d.get('free_endpoints', [])}\")
"
```

### Structure Tests by Group

Group endpoints by domain so failures are easy to localize:

```python
endpoint_groups = [
    ("── Market Data ──", [
        ("Price query", "/market/price?symbol=BTC"),
    ]),
    ("── DeFi ──", [
        ("Protocols", "/defi/protocols"),
    ]),
]
```

## Cron Integration

### Standalone Cron (no_agent=True)

```bash
# Every 6 hours, silent unless failures
hermes cron create \
  --schedule "0 2,8,14,20 * * *" \
  --script "api-safety-suite/run_safety_suite.py" \
  --workdir "/path/to/scripts" \
  --no-agent
```

### Context Feed for Compliance Scout

Chain the safety suite's output into an LLM-driven compliance cron:

```bash
# The compliance cron receives safety results as context
hermes cron update <compliance-job-id> \
  --context-from <safety-suite-job-id>
```

## Continuous Improvement

- **New endpoints** — add to the runner script when deployed
- **Goldens** — update when response schema is intentionally changed
- **Failure alerts** — use `deliver: origin` for standalone cron, or route to Telegram, Discord, etc.

## Placeholder-Data Audit (the silent revenue leak)

**A payment gate working ≠ endpoint earning.** An API can return a perfect 402
challenge, pass health checks, and sit indexed on the marketplace — yet return
hardcoded placeholder data (`price:0.0`, `"source":"placeholder"`, `"score":0`,
`"level":"unknown"`, `[]`) when the client actually pays. That listing looks
live but converts nothing. Auditing for 402-compliance (above) is NOT the same
as auditing for real data. Do both.

Real incident (Aug 3 2026): deal-tracker `/v1/deals` returned `{"deals":[]}`,
crypto-price returned `price:0.0 placeholder`, gas-price returned all-zero,
token-security returned `score:0 unknown` — all while showing live and green.

### The Placeholder-Data Audit Recipe

1. **Probe every service** — `curl` each data endpoint (not just health).
   Capture: HTTP status, response body length, first ~150 chars.
2. **Classify the response body:**
   - ✅ HEALTHY — real data, OR a proper `402` payment challenge (the 402 IS
     healthy for a paid endpoint)
   - ❌ PLACEHOLDER — hardcoded zeros / `"placeholder"` / `"level":"unknown"`
   - ⚠️ STUB — empty array `[]` / empty dict `{}` shell
   - 🔗 REDIRECT — 3xx, follow it
3. **Flag placeholders FIRST** — they're the silent revenue leaks. A 402
   challenge means the gate works (good). A hardcoded `0`/`[]` means the data
   layer is dead (fix).
4. **Fix the data layer** — replace placeholder bodies with a real source:
   - A public API (CoinGecko, Etherscan, free REST endpoint)
   - A live RPC call (`eth_gasPrice`, etc.)
   - **A working internal engine you already built — don't duplicate, reuse.**
5. **Add a test** — a pytest asserting "not placeholder" prevents regression.
6. **Restart + re-audit** — confirm the endpoint now returns real data.

### Reuse, Don't Duplicate (proxy pattern)

The fastest fix for a placeholder API is often a **thin proxy to an engine you
already have running**, not a from-scratch rebuild. token-security-api was a
hardcoded stub; the working Rugcheck v2 engine (port 8088) already scored
Solana tokens with real logic + caching + 402 compliance. Fix: forward
`/v1/score/{mint}` to Rugcheck, preserve its 402 challenge. One source of truth,
inherits the engine's caching/errors/compliance, far less code.

### Detection pitfall — match EXACT zeros, not decimals

A naive `"price":0` regex flags real low-value responses (`"price":0.09` — real
data) as placeholder. Match exact zero tokens only: `"price":0}`, `"price":0,`,
`"price": 0}`, `"price": 0,` (and the `level":"unknown"`, `[]`, `{}` signals).
This exact-matching rule is built into the kit's `services/api-audit.py`.

### The reusable tool

The agent kit ships `services/api-audit.py` (in `Gentech-Labs/genTech-agent-kit`)
— a ready auditor that probes defined targets and classifies HEALTHY /
PLACEHOLDER / STUB / REDIRECT. Add targets, run, fix placeholders, re-run.
Full worked incident + detection-token list: `references/api-placeholder-audit.md`.

## Pitfalls

- **User-Agent required:** Many gateways (behind Cloudflare) block Python urllib requests that lack a User-Agent header. Always set `User-Agent: SafetySuite/1.0`.
- **Path prefix mismatch:** If `BASE_URL` already includes `/v1`, don't prefix endpoint paths with `/v1/` again — that creates `//v1/v1/` doubling.
- **x402-payment header not always present:** Some gateways embed payment metadata in the body's `accepts[]` array rather than a response header. Check both.
- **Timeout on large payloads:** Set `timeout=5` for health/CORS checks (always fast), `timeout=10` for paid endpoints.
- **Rate limiting:** Running suite every 6h is fine. Running every minute will get you rate-limited or blocked.
- **Golden set aging:** Stale goldens cause false positives. Update them when endpoints intentionally change schema.
- **Wholesale "missing field" / "schema drift" failures = stale harness, not outage.** When EVERY paid endpoint fails at once with `402 response missing '<field>'` or `schema drift — missing key '<field>'`, while health + CORS still pass, the gateway almost certainly upgraded its response format and the harness (or its golden snapshots) is validating against an old schema. Do NOT treat it as an outage. Diagnosis:
  1. `curl -si <BASE_URL>/<any-paid-endpoint>` and inspect the **actual live 402 body + `payment-required` header**.
  2. Check `/health` — it usually reports the live `gateway` version (e.g. `"gateway":"x402-v2"`).
  3. Compare the live field names to what the validator demands. If they differ (e.g. live uses camelCase `x402Version`/`resource`/`accepts[].payTo`, harness expects snake_case `x402version`/`payment_address`), the harness is stale — patch `check_402()` to the live shape.
  4. If the schema-drift check still fails after fixing the validator, the **golden files** themselves hold the old snapshot. `ls golden/` and delete them; the harness regenerates goldens from the live response on next run. Re-run to confirm 0 failures.
- **Never hardcode a gateway schema.** Field casing and layout (`snake_case` vs `camelCase`, `status` vs `resource`) change across gateway versions. Every "expected field" in a validator and every golden snapshot is version-dependent — verify the live response before trusting either. A health-check `gateway` field naming the version is your best anchor.
