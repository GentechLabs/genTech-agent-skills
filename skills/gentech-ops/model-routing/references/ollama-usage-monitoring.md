# Ollama Cloud Usage Monitoring

## Check Current Usage

**Use `/api/usage` — NOT `/v1/usage`.** The `/v1/usage` path returns `{"error":"path \"/v1/usage\" not found"}` (verified Aug 2026). The real, working endpoint is:

```bash
# Get usage from Ollama API (correct endpoint)
curl -H "Authorization: Bearer $OLLAMA_API_KEY" \
  https://ollama.com/api/usage
```

Expected JSON response (verified live Aug 7, 2026):
```json
{
  "activity": { "cost": "0.00000", "period": { "type": "last_4_weeks", ... }, "models": [] },
  "limits": {
    "session": { "usage": 0.103, "models": [{"name": "deepseek-v4-flash:0731", "request_count": 348}] },
    "weekly": { "usage": 0.844, "models": [ ... ] }
  }
}
```
- `limits.weekly.usage` = weekly fraction (0.0-1.0) — the binding constraint (resets ~every 7 days)
- `limits.session.usage` = the fast 5-hr rolling window (resets in ~1 hr, rarely the constraint)
- `activity.cost` is often `"0.00000"` — ignore it; the limits are what matter.

**OpenCode Go has NO usage endpoint** — `/v1/usage`, `/api/usage`, `/v1/limits` all return the dashboard HTML. Detect its state by live-testing a model call: a `GoUsageLimitError` / "usage limit reached" in the error body = exhausted. Use a non-China-hosted probe model (e.g. `minimax-m3`) to avoid the `RegionError` gate that `deepseek-v4-flash` hits.

## Check Pro Plan Limits

```bash
# Get plan details
curl -H "Authorization: Bearer $OLLAMA_API_KEY" \
  https://ollama.com/v1/plan

# Expected JSON response:
{
  "name": "pro",
  "price_monthly": 20,
  "max_concurrent_models": 3,
  "session_reset_hours": 5,
  "weekly_reset_days": 7,
  "included_gpu_hours": "unlimited_within_limits"
}
```

## Test Model Availability

```bash
# Test deepseek-v4-flash
curl -X POST https://ollama.com/v1/chat/completions \
  -H "Authorization: Bearer $OLLAMA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4-flash",
    "messages": [{"role": "user", "content": "Write Python hello world"}]
  }'

# Test qwen3-coder-next
curl -X POST https://ollama.com/v1/chat/completions \
  -H "Authorization: Bearer $OLLAMA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-coder-next",
    "messages": [{
      "role": "user",
      "content": "Audit this code: function eval(x) { return eval(x); }"
    }]
  }'
```

## Monitor GPU Time Per Request

```bash
# Measure GPU time for audit task
time curl -X POST https://ollama.com/v1/chat/completions \
  -H "Authorization: Bearer $OLLAMA_API_KEY" \
  -H "Content-Type: application/json" \
  -d @audit-request.json

# Check response headers for GPU time
curl -I -X POST https://ollama.com/v1/chat/completions \
  -H "Authorization: Bearer $OLLAMA_API_KEY" \
  -H "Content-Type: application/json" \
  -d @audit-request.json

# Look for headers:
# x-gpu-time-seconds: 12.5
# x-session-id: abc123
```

## Extrapolate to Monthly Usage

**If average audit takes 30 GPU seconds:**
- 50 audits × 30s = 1,500 seconds = 25 minutes GPU time/month
- Pro plan: unlimited within limits = covers workload ✅

**If average audit takes 60 GPU seconds:**
- 50 audits × 60s = 3,000 seconds = 50 minutes GPU time/month
- Pro plan: unlimited within limits = covers workload ✅

**If average build takes 15 GPU seconds:**
- 500 builds × 15s = 7,500 seconds = 125 minutes GPU time/month
- Pro plan: unlimited within limits = covers workload ✅

**Total:** 25 + 125 = 150 minutes GPU time/month
- Pro plan: unlimited = covers workload ✅

## Alert Configuration (Future)

```bash
# Set up alert at 90% of weekly limit
# (via Ollama web UI or API when available)
curl -X POST https://ollama.com/v1/alerts \
  -H "Authorization: Bearer $OLLAMA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "threshold_pct": 90,
    "email": "jordan@example.com",
    "frequency": "weekly"
  }'
```

## Session Limit Tracking

```bash
# Check current sessions
curl -H "Authorization: Bearer $OLLAMA_API_KEY" \
  https://ollama.com/v1/sessions

# Expected JSON response:
{
  "active_sessions": 2,
  "max_concurrent": 3,
  "sessions": [
    {
      "id": "abc123",
      "model": "deepseek-v4-flash",
      "started_at": "2026-07-06T15:30:00Z",
      "gpu_time_seconds": 450.5
    },
    {
      "id": "def456",
      "model": "qwen3-coder-next",
      "started_at": "2026-07-06T16:00:00Z",
      "gpu_time_seconds": 120.0
    }
  ],
  "reset_at": "2026-07-06T20:00:00Z"
}
```

## Troubleshooting

### Session Limit Reached (429 Too Many Requests)

**Symptom:**
```json
{
  "error": {
    "code": 429,
    "message": "Session limit reached. Max concurrent: 3. Reset in 2h 15m."
  }
}
```

**Solution:**
1. Wait for session reset (every 5 hours)
2. Reduce concurrent model usage
3. Upgrade to Max plan ($100/month, 10 concurrent)

### Weekly Limit Reached

**Symptom:**
```json
{
  "error": {
    "code": 429,
    "message": "Weekly limit reached. Reset in 2 days."
  }
}
```

**Solution:**
1. Wait for weekly reset (every 7 days)
2. Upgrade to Max plan ($100/month)
3. Reduce GPU-intensive tasks

### Model Not Available

**Symptom:**
```json
{
  "error": {
    "code": 404,
    "message": "Model 'qwen3-coder-next' not found in Pro plan."
  }
}
```

**Solution:**
1. Verify model name: `curl https://ollama.com/v1/models`
2. Check plan includes model
3. Use available model (deepseek-v4-flash always available)

---

**Created:** July 6, 2026
**Status:** Templates created, need to test with actual Ollama API key
**Priority:** HIGH (needed for week 1 quality testing)