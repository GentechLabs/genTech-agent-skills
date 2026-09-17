# Ongoing System Health Issues - May 6, 2026

**Context**: This document records persistent health issues detected during the scheduled Gentech Watchdog run on May 6, 2026 at 04:38 AM UTC. Many of the same issues identified in the May 6th early morning incident remain unresolved.

## Current Active Failures

### 1. Nous OAuth Token Revocation (Systemic)
- **Status**: ALL FOUR AGENTS (YoYo, DMOB, Desmond, Gentech) still show "Refresh session has been revoked" for Nous Portal authentication.
- **Impact**: Prevents all Nous-dependent operations, including LLM functionality for many cron jobs.
- **Required Action**: Manual `hermes model` re-authentication for each profile (interactive only).

### 2. YoYo - Omni-Summary Master Brief
- **Job ID**: 1b8e2ea4c7c0
- **Schedule**: Daily at 11:30 UTC
- **Last Run**: May 5th, 11:30:37 (failed)
- **Error**: `RuntimeError: No LLM provider configured. Run 'hermes model' to select a provider`
- **Impact**: Daily brief not delivered to Jordan.

### 3. DMOB - brain-backup
- **Job ID**: 3044d70c58bc
- **Schedule**: Daily at 06:00 UTC
- **Last Run**: May 5th, 06:00:26 (failed)
- **Error**: `RuntimeError: Error code: 401 - {'status': 401, 'message': 'Your API key is invalid, blocked or out of funds...'}`
- **Impact**: No brain backups since May 4th.

### 4. Desmond - Memory & Profile Backup
- **Job ID**: 30c5350962d3
- **Schedule**: Every 6 hours
- **Last Run**: May 6th, 00:00:55 (failed)
- **Error**: `RuntimeError: HTTP 429: quota exhausted`
- **Impact**: Backup failures due to rate limiting.

### 5. Configuration Error - Incorrect HOME Path
- **Issue**: Cron jobs still using `/root/home/.hermes/` instead of `/root/.hermes/`
- **Evidence**: YoYo cron.log shows repeated errors: `AAE config missing: [Errno 2] No such file or directory: '/root/home/.hermes/scripts/.lfj-aae-config.json'`
- **Impact**: Configuration files not found, causing script failures.

## Root Cause Analysis

### Incomplete Recovery from May 6th Incident
The initial recovery actions from the May 6th early morning incident were not fully completed. While some issues were addressed (gateways running, some cron jobs working), the critical authentication problems and configuration errors remain.

### Interactive Authentication Bottleneck
The requirement for manual `hermes model` re-authentication per profile creates a bottleneck. No automation can perform this due to the interactive nature of OAuth device flow and rate limiting.

### Missing Fallback Providers
Several agents lack configured fallback LLM providers, making them vulnerable when primary providers fail.

## Recommended Recovery Actions

### Immediate (Within Next 24 Hours)
1. **Re-authenticate all agents** with Nous Portal:
   ```bash
   hermes model --profile yoyo
   hermes model --profile dmob
   hermes model --profile desmond
   hermes model --profile gentech
   ```
   (Each requires interactive terminal session)

2. **Fix HOME path configuration** in all agent profiles:
   - Update cron environment variables or script paths to use `/root/.hermes/` instead of `/root/home/.hermes/`

3. **Rotate API keys** for exhausted providers (ElevenLabs, etc.):
   - Generate new keys
   - Update each agent's `.env` file
   - Restart gateways

4. **Configure fallback LLM providers** for YoYo and Desmond.

### Medium-term
1. **Implement external watchdog for Gentech Watchdog** to ensure monitoring continuity
2. **Schedule regular credential audits** to catch expiring tokens
3. **Document recovery procedures** in a runbook format
4. **Set up disk pressure alerts** to prevent corruption cascades

## Verification Steps
After completing recovery actions:
- [ ] Verify all four agents show "logged in" for Nous Portal
- [ ] Confirm YoYo Omni-Summary runs successfully at next scheduled time (11:30 UTC)
- [ ] Check DMOB brain-backup runs at 06:00 UTC and produces output
- [ ] Verify Desmond backup runs at next interval (06:00 UTC)
- [ ] Confirm no AAE config missing errors in cron logs
- [ ] Check Gentech Watchdog runs successfully at next interval (05:00 UTC)

## Lessons Learned
- **Recovery must be complete**: Partial fixes leave the system vulnerable
- **Monitor the monitor**: The watchdog itself needs independent verification
- **Configuration drift happens**: Regular audits needed to catch path errors
- **Bottlenecks should be addressed**: Interactive auth requirements create single points of failure

--- 
**Detected**: May 6, 2026 at 04:38 AM UTC  
**Report generated**: May 6, 2026 at 04:45 AM UTC  
**Next scheduled watchdog**: 05:00 AM UTC (if recovered)