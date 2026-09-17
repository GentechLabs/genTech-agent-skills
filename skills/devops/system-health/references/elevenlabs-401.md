# ElevenLabs TTS 401 Invalid API Key

## Symptom
Errors in agent logs (repeated):
```
elevenlabs.core.api_error.ApiError: status_code: 401, body: {'detail': {'status': 'invalid_api_key', 'message': 'Invalid API key'}}
2026-05-01 17:22:58,731 ERROR [20260501_102014_c12efb4a] tools.tts_tool: TTS generation failed (elevenlabs): status_code: 401, body: {'detail': {'status': 'invalid_api_key', 'message': 'Invalid API key'}}
```

Multiple timestamps for both DMOB and Desmond agents (May 1, 2026 between 17:16–21:52).

## Cause
Expired, revoked, or misconfigured `ELEVENLABS_API_KEY` environment variable. The key may have:
- Expired due to billing issues
- Been rotated in the ElevenLabs dashboard
- Never been set in the agent's environment
- Been set with wrong scope/permissions

## Affected Agents
- DMOB (profile: dmob)
- Desmond (profile: desmond)
Any agent using the TTS tool with ElevenLabs provider.

## Fix
**1. Obtain a valid API key:**
   - Log into ElevenLabs dashboard
   - Navigate to Profile → API Key
   - Copy the active key (starts with `eleven_` or similar)

**2. Update environment:**
```bash
# If using systemd user services:
cat ~/.config/systemd/user/hermes-gateway-<agent>.service | grep ELEVENLABS
# Update Environment line or EnvironmentFile

# If using hermes profile env:
export ELEVENLABS_API_KEY="your-new-key-here"
hermes -p <agent> gateway restart
```

**3. For system-wide install:**
```bash
# Edit hermes service environment
sudo systemctl edit hermes-gateway-<agent> --full
# Add/update:
[Service]
Environment="ELEVENLABS_API_KEY=your-key"
# Then restart:
systemctl --user daemon-reload
systemctl restart hermes-gateway-<agent>
```

**4. Verify:**
```bash
# Trigger a TTS operation or check agent log clears
tail -f ${PROFILES_DIR}/<agent>/logs/errors.log
```
No new 401 errors should appear.

## Alternative: Switch TTS Provider
If ElevenLabs is not required, change agent's default TTS provider via config or prompt:
```yaml
tools:
  tts:
    provider: openai  # or coqui, azure, etc.
```

## Prevention
- Store API keys in encrypted credential manager (e.g., `hermes auth` integration)
- Set up rotation reminders before key expiry
- Monitor ElevenLabs dashboard for usage limits/expiry notifications

## Related Issues
- OpenAI TTS 401: same fix, different env var (`OPENAI_API_KEY`)
- Multiple agents sharing same key → ensure all profiles updated

