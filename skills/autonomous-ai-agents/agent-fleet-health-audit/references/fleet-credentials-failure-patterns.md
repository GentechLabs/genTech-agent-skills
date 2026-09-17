# Fleet-Wide Credential Failure Patterns

## ElevenLabs TTS Expiration (Fleet-Wide)
**Signature:** All agents log `elevenlabs.core.api_error.ApiError: status_code: 401` with body `{'detail': {'status': 'invalid_api_key', 'message': 'Invalid API key'}}`

**Impact:** Text-to-speech functionality completely broken across all agents.

**Detection:**
```bash
# Count 401 errors across all agent logs
grep -h "status_code: 401" ~/.hermes/profiles/*/logs/errors.log | wc -l
# Or inspect specific agent
grep "status_code: 401" ~/.hermes/profiles/yoyo/logs/errors.log
```

**Root Cause:** Shared ElevenLabs API key stored in each agent's `.env` (same key value `ELEVENLABS_API_KEY=bb158b...`). Key has expired or been revoked.

**Remediation:**
1. Obtain new ElevenLabs API key from dashboard
2. Update all agent `.env` files atomically:
   ```bash
   for agent in yoyo dmob desmond gentech; do
     sed -i "s/^ELEVENLABS_API_KEY=.*/ELEVENLABS_API_KEY=new_key_here/" ~/.hermes/profiles/$agent/.env
   done
   ```
3. Restart all agent gateways to clear cached auth state
4. Validate by triggering a TTS job in each agent

**Escalation:** If >100 total 401 errors across fleet within 1 hour → immediate key rotation required.

---

## Nous Refresh Session Revocation (Systemic)

**Signature:** `hermes_cli.auth.AuthError: Refresh session has been revoked` followed by `RuntimeError: Refresh session has been revoked Run \`hermes model\` to re-authenticate.`

**Impact:** All API calls requiring Nous authentication fail. Cron jobs fail on first LLM call. Gateway continues running with fallback providers if available, but most LLM-dependent features broken.

**Detection:**
```bash
# Count refresh session errors per agent
for agent in yoyo dmob desmond gentech; do
  count=$(grep -c "Refresh session has been revoked" ~/.hermes/profiles/$agent/logs/errors.log)
  echo "$agent: $count"
done
```

**Root Cause:** Master Nous refresh session expired or was revoked (manual revocation, security rotation, or session lifetime exceeded).

**Remediation:**
1. Re-authenticate each agent with Nous provider:
   ```bash
   for agent in yoyo dmob desmond gentech; do
     systemctl --user stop hermes-gateway-$agent
     hermes login --provider nous --profile $agent
     systemctl --user start hermes-gateway-$agent
   done
   ```
2. Alternatively, run `hermes model` within each agent profile to trigger interactive re-auth
3. Verify by checking gateway.log for successful auth: `"Primary provider auth succeeded"`

**Escalation:** If >10 "Refresh session revoked" errors per agent in last hour → Fleet-wide re-auth required.

---

## Anthropic Token Missing (Agent-Specific)

**Signature:** `RuntimeError: No Anthropic credentials found. Set ANTHROPIC_TOKEN or ANTHROPIC_API_KEY...`

**Impact:** Any job or workflow using Claude models fails immediately.

**Detection (DMOB-specific):**
```bash
grep -E "ANTHROPIC_(TOKEN|API_KEY)" ~/.hermes/profiles/dmob/.env
# Returns empty → missing credentials
```

**Remediation:**
1. Obtain Anthropic API key from dashboard
2. Add to DMOB `.env`:
   ```bash
   echo "ANTHROPIC_API_KEY=sk-ant-..." >> ~/.hermes/profiles/dmob/.env
   ```
3. Restart DMOB gateway: `systemctl --user restart hermes-gateway-dmob`

**Note:** Other agents may also lack Anthropic keys; check `.env` for `ANTHROPIC` substring if Claude-dependent jobs fail.
