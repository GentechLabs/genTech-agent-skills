# Stale Rate-Limit Diagnosis — Worked Example (2026-07-31)

## Symptom
`hermes auth list` showed:
```
zai (2 credentials):
  #1  GLM_API_KEY          api_key env:GLM_API_KEY rate-limited 1310 (429) (ready to retry) ←
  #2  ZAI_API_KEY          api_key env:ZAI_API_KEY rate-limited 1310 (429) (ready to retry)
```
Both Z.AI keys looked dead, and the zai-usage-monitor script fell back to "check the
dashboard manually" because the key wasn't in shell env.

## What auth.json actually said
```json
"last_status": "exhausted",
"last_error_code": 429,
"last_error_reason": "1310",
"last_error_message": "Weekly/Monthly Limit Exhausted. Your limit will reset at 2026-07-11 04:38:41",
"last_status_at": 1783584028
```
- `last_status_at` → 2026-07-09T08:00:28Z (failure moment)
- **Reset timestamp: 2026-07-11 04:38:41 — already 20 days past by Jul 31**

So the status was a stale snapshot, not a live state.

## Verification (live test)
```bash
KEY=$(grep -E "^GLM_API_KEY=" .env | head -1 | cut -d= -f2-)
curl -s --max-time 45 https://api.z.ai/api/coding/paas/v4/chat/completions \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"model":"glm-4.5-flash","messages":[{"role":"user","content":"ping"}],"max_tokens":5}'
```
Response: 200 with `choices`, model `glm-4.5-flash`, 11 total tokens. Key fully usable.

## Misleading endpoint
`https://api.z.ai/api/monitor/usage/quota/limit` returned:
```json
{"code":500,"msg":"当前用户不存在coding plan","success":false}
```
Reads like "account broken" but actually means the monitor endpoint doesn't serve
coding-plan keys. Do NOT conclude the key is dead from it — use the inference endpoint.

## Companion findings (same session)
- OpenCode Go: `GoUsageLimitError`, monthly usage limit reached 2026-07-30T21:47Z,
  "Resets in 9 days" → ~2026-08-08. This one is a genuine exhaustion, not stale.
- Nous Portal (active provider): access token exp `2026-07-31T03:27:51Z` —
  check `hermes status` before long cron batches; refresh before expiry.

## Lesson
The credential pool's rate-limit status is a snapshot of the LAST failure, not a live
probe. When the stored reset time has passed, treat the status as stale and live-test
the endpoint before escalating, switching providers, or telling the user the provider is down.
