# API Safety Suite — Golden Test Harness for x402 Endpoints

A regression test suite that validates every x402 endpoint every 6 hours. Silent when passing, loud on failure.

## Location

- Suite: `/root/.hermes/profiles/gentech/scripts/api-safety-suite/run_safety_suite.py`
- Cron: job_id `59283121321a`, schedule `0 2,8,14,20 * * *`
- Context consumer: x402 Compliance Scout (`f2105e16a83b`) receives results via `context_from`

## What It Tests Per Endpoint

1. **HTTP 402 returned** — not 403, 404, or 200 (proves x402 paywall is active)
2. **Response body shape** — required x402 v2 fields present: status, x402version, accepts[], network, asset, amount, payment_address
3. **Version check** — x402version is `2`, `"2"`, or `"x402-v2"`
4. **Amount validity** — amount is a positive integer string (weis)
5. **Accepts array** — at least one payment option with type, scheme, network, amount, asset, payTo
6. **Network set** — network is non-empty
7. **CORS headers** — `Access-Control-Allow-Origin: *`
8. **Health endpoint** — gateway `/health` returns status "ok"
9. **CORS preflight** — OPTIONS request handles CORS correctly

## How to Add a New Endpoint

Edit `run_safety_suite.py` and add it to the `endpoint_groups` list:

```python
("── MyGroup ──", [
    ("My endpoint", "/v1/my-endpoint"),
]),
```

The suite automatically:
- Sends GET request (add method="POST" + body dict for POST endpoints)
- Validates 402 response
- Saves a golden response shape to `golden/` on first run
- On subsequent runs, diffs against golden set

## Integration

The safety suite runs 10 minutes before the x402 Compliance Scout (both at 08,14,20 UTC). The Scout receives the suite's output via `context_from`, so a failing endpoint is reported in the next Scout delivery.

## Pitfalls

- **Python's urllib needs a User-Agent header** — Cloudflare blocks default urllib requests. Always set `User-Agent: GenTech-SafetySuite/1.0`.
- **Endpoint paths must match BASE_URL** — don't double-up `/v1/`. `BASE_URL = "https://api.gentechlabs.net/v1"` + path `/games/search` = correct. `/v1/games/search` = double /v1.
- **402 response fields differ by gateway version** — v7 gateway uses `x402version: "x402-v2"` string, not integer `2`. Validate both.
- **The `accepts[]` fields are `type`, `scheme`, `network`, `amount`, `asset`, `payTo`** — not `schema` or `payment_address`.
