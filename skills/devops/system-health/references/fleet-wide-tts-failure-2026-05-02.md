# Fleet-Wide TTS Failure (ElevenLabs 401) — 2026-05-02

**Pattern**: All agents simultaneously logging `elevenlabs.core.api_error.ApiError: status_code: 401`  
**Root cause**: Shared invalid/expired ElevenLabs API key across all agent `.env` files  
**Impact**: Text-to-speech completely non-operational fleet-wide  
**Detection date**: May 2, 2026  
**Status**: Credentials identified but not yet rotated

---

## Error Signature

```
elevenlabs.core.api_error.ApiError: status_code: 401, body: {'detail': {'status': 'invalid_api_key', 'message': 'Invalid API key'}}
```

Occurs at:
- `${INSTALL_DIR}/tools/tts_tool.py:801` (_generate_elevenlabs)
- `${INSTALL_DIR}/tools/tts_tool.py:1637` (text_to_speech_tool wrapper)

## Evidence of Fleet-Wide Scope

Counts logged per agent (cumulative, measured May 2 afternoon):

| Agent | 401 Error Count | Notes |
|-------|-----------------|-------|
| YoYo | 96 | Process terminated 13:39; errors accumulated prior |
| DMOB | 244 | Actively running; errors ongoing |
| Desmond | 220 | Process down; errors from prior runtime |
| Gentech | 30 | Actively running; fewer TTS calls |

All agents use **same invalid key** → systemic credential failure, not isolated agent issue.

## Investigation

### Step 1: Confirm error pattern across profiles
```bash
for agent in yoyo dmob desmond gentech; do
  grep -c 'status_code: 401' ${PROFILES_DIR}/$agent/logs/errors.log
done
```

### Step 2: Inspect `.env` files for shared key
```bash
for agent in yoyo dmob desmond gentech; do
  echo "=== $agent ==="
  grep ELEVENLABS ${PROFILES_DIR}/$agent/.env 2>/dev/null || echo "NOT SET"
done
```

**Expected finding**: All show identical `ELEVENLABS_API_KEY=<same-invalid-value>`

### Step 3: Validate key via API test (optional)
```bash
curl -H "xi-api-key: <key>" https://api.elevenlabs.io/v1/voices
# 401 response confirms invalid
```

## Recovery Procedure

**⚠️ Do NOT fix only one agent — rotate source key and update all profiles.**

1. Generate new ElevenLabs API key from dashboard (elevenlabs.io → profile → API keys)
2. Update each agent's `.env` independently:
   ```bash
   echo "ELEVENLABS_API_KEY=<new-valid-key>" >> ${PROFILES_DIR}/yoyo/.env
   echo "ELEVENLABS_API_KEY=<new-valid-key>" >> ${PROFILES_DIR}/dmob/.env
   echo "ELEVENLABS_API_KEY=<new-valid-key>" >> ${PROFILES_DIR}/desmond/.env
   echo "ELEVENLABS_API_KEY=<new-valid-key>" >> ${PROFILE_DIR}/.env
   ```
3. Restart gateways to ensure new env vars loaded:
   ```bash
   hermes gateway restart --profile yoyo
   hermes gateway restart --profile dmob
   hermes gateway restart --profile desmond
   hermes gateway restart --profile gentech
   ```
   (Or: `hermes gateway stop --profile <p> && hermes gateway run --profile <p> --replace`)
4. Verify errors stop:
   ```bash
   tail -f ${PROFILES_DIR}/<agent>/logs/errors.log
   # Should see no new 401s; TTS tool should succeed
   ```

## Prevention

- **Never share API keys across profiles** — each agent should have its own API key or use a secret-management layer (Vault, AWS Secrets Manager) that provisions per-agent credentials
- Use distinct ElevenLabs sub-accounts or API keys per agent to contain credential expiration to single profile
- Set up credential expiry monitoring: `grep -r 'ELEVENLABS_API_KEY' ${PROFILES_DIR}/*/.env | sort -u` weekly audit

## Related Incidents

- **2026-05-01**: Earlier bytecode corruption incident (separate issue)
- Pattern: Fleet-wide cascade due to shared credentials is recurring failure mode — review all shared secrets (Anthropic, OpenRouter, etc.) for same risk

## Correlation Note

This credential failure **co-occurred** with:
- Master gateway service failure (cron jobs frozen) — unrelated root cause
- Bytecode corruption in YoYo/Gentech — unrelated
- DMOB missing Anthropic credentials — separate credential gap

Multiple simultaneous systemic failures created compound degradation.
