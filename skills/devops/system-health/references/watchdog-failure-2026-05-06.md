# Watchdog Failure Incident - May 6, 2026

**Incident Summary**: Gentech Watchdog cron job failed for approximately 96 hours (since May 2nd), leaving the entire agent fleet unmonitored. All four agents (YoYo, DMOB, Desmond, Gentech) experienced widespread cron job failures due to systemic issues.

## Timeline

- **May 2nd**: Watchdog first reported failures: "Hermes is not logged into Nous Portal"
- **May 6th, early morning**: Failures evolved to "HTTP 429: quota exhausted"
- **May 6th, ~03:00 UTC**: Failures changed to "Refresh session has been revoked"
- **May 6th, 03:41 UTC**: Watchdog last attempted run (failed)
- **May 6th, 03:45 UTC**: Manual health check initiated (this session)

## Root Causes

### 1. Nous OAuth Token Revocation (Primary)
- All agents' Nous Portal refresh tokens were revoked
- `hermes model` required for re-authentication, but this is interactive-only
- Result: Agents could not authenticate with Nous Portal, causing API calls to fail

### 2. API Key Exhaustion (Secondary)
- ElevenLabs API key hit quota limit (0 credits remaining)
- Multiple agents reported HTTP 429 "quota exhausted"
- Affected TTS functionality and some cron jobs

### 3. Missing LLM Provider Configuration
- Several agents lacked fallback LLM providers
- Errors: "No LLM provider configured. Run `hermes model` to select a provider"
- Aggravated the impact of Nous token revocation

## Impact Scope

**Affected Agents**: All four profiles (YoYo, DMOB, Desmond, Gentech)

**Failed Cron Jobs**:
- **YoYo** (31 jobs): Multiple failures including Omni-Summary, College.xyz scan
- **DMOB** (8 jobs): Sunday Skill Update, brain-backup, LayerZero monitor, Defi Milestone morning, LP Position Monitor hourly
- **Desmond** (6 jobs): Memory & Profile Backup (HTTP 429)
- **Gentech** (31+ jobs): Dozens of failures across Mess Hall, security pipeline, hackathon checks, etc.

**Systemic Error Patterns**:
```
"RuntimeError: No LLM provider configured. Run `hermes model` to select a provider"
"RuntimeError: Refresh session has been revoked Run `hermes model` to re-authenticate."
"RuntimeError: Error code: 401 - {'status': 401, 'message': 'Your API key is invalid, blocked or out of funds."
"RuntimeError: HTTP 429: quota exhausted"
"RuntimeError: Error code: 400 - {'error': {'code': '400', 'message': 'Not supported model mimo-2.5-pro'}"
"ValueError: I/O operation on closed file."
```

## Detection Gap

**Critical Finding**: The watchdog itself was failing, but because it was the monitoring mechanism, these failures went undetected. The system was operating "blind" for nearly 4 days.

This reveals a meta-monitoring gap: the watchdog must be monitored separately to ensure it remains operational.

## Recovery Actions Required

### Immediate (Manual Intervention Required)
1. **Re-authenticate all agents** with Nous Portal:
   ```bash
   hermes model --profile yoyo
   hermes model --profile dmob
   hermes model --profile desmond
   hermes model --profile gentech
   ```
   (Each requires interactive terminal session)

2. **Rotate API keys** for exhausted providers:
   - Generate new ElevenLabs API key
   - Update `.env` in each agent profile:
     ```bash
     echo "ELEVENLABS_API_KEY=<newkey>" >> ${PROFILES_DIR}/<agent>/.env
     ```
   - Restart gateways to load new credentials

3. **Configure fallback LLM providers** for all agents lacking them:
   ```bash
   hermes model --profile <agent> --set default <provider>
   ```

4. **Restart all gateways** to apply changes:
   ```bash
   hermes gateway stop --profile yoyo
   hermes gateway stop --profile dmob
   hermes gateway stop --profile desmond
   hermes gateway stop --profile gentech
   sleep 5
   hermes gateway run --profile yoyo --replace &
   hermes gateway run --profile dmob --replace &
   hermes gateway run --profile desmond --replace &
   hermes gateway run --profile gentech --replace &
   ```

5. **Verify watchdog recovery** after one schedule interval (5 minutes):
   ```bash
   hermes cron list --profile gentech | grep -A2 "Gentech Watchdog"
   # Should show recent last_run_at and ok status
   ```

### Medium-term (Automation & Prevention)
1. **Implement external watchdog for watchdog**: Set up independent monitoring (e.g., separate script or external service) to check if Gentech Watchdog is running
2. **Schedule regular Nous token refreshes**: Set calendar reminders for token expiration dates
3. **Implement API key rotation policies**: Auto-rotate keys before expiration
4. **Maintain configured fallback LLM providers**: Ensure all agents have working backup providers
5. **Add disk pressure monitoring**: Early warning for corruption cascades (correlated with .pyc errors)

## Key Lessons

1. **Monitor the monitor**: Critical monitoring systems themselves require oversight
2. **Systemic failures are correlated**: When one component fails (Nous auth), it often cascades to others
3. **Interactive commands can't be cron'd**: `hermes model` requires manual intervention; plan accordingly
4. **Watchdog blindness is dangerous**: 96 hours of unmonitored operation allowed issues to compound
5. **Early warning signs were present**: Disk pressure and .pyc corruption preceded this incident

## Error Pattern Reference

### Common Failure Messages
- `"Hermes is not logged into Nous Portal. Run \`hermes model\` to re-authenticate."`
- `"HTTP 429: quota exhausted"`
- `"Refresh session has been revoked"`
- `"No LLM provider configured"`
- `"Error code: 401 - Invalid API key"`

### Affected Services
- Nous Portal (authentication)
- ElevenLabs (TTS)
- Vision tool (auxiliary model)
- Various LLM providers

### Diagnostic Commands Used
```bash
hermes cron list --profile gentech
ps aux | grep hermes
grep 'Gentech Watchdog' /var/log/syslog
hermes gateway status --profile <agent>
df -h /
```

## Follow-up Actions

- [ ] Schedule Nous re-authentication sessions for all four profiles
- [ ] Rotate ElevenLabs API key and update all .env files
- [ ] Configure fallback LLM providers for YoYo and Desmond
- [ ] Set up external monitoring for Gentech Watchdog
- [ ] Review and clean disk space (>80% pressure observed)
- [ ] Verify all .pyc caches are clean and gateways restarted
- [ ] Document this incident in onboarding materials

---
**Detected**: May 6, 2026 at 03:46 AM (during scheduled cron job)
**Report generated**: May 6, 2026 at 04:12 AM
**Next watchdog run**: Scheduled for 04:50 AM (if recovered)