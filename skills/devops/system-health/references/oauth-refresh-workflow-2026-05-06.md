# OAuth Token Refresh Workflow - May 6, 2026 Incident

## Incident Summary
Proactive cron job detected that the Nous OAuth refresh session had been revoked, requiring manual re-authentication.

## Root Cause
- Access token expired and could not be automatically refreshed
- Refresh token was either expired or revoked by the provider
- Required full re-authentication via device flow

## Resolution Steps

### 1. Run Proactive Refresh Script
```bash
python3 ${PROFILES_DIR}/gentech/scripts/refresh_nous_oauth.py
```

**Output:**
```json
{
  "success": false,
  "message": "Refresh session has been revoked Run `hermes model` to re-authenticate.",
  "tokens": {},
  "needs_reauth": true,
  "critical": false,
  "hermes_home": "${PROFILES_DIR}/gentech"
}
```

### 2. Initiate Device Flow (Interactive)
```bash
hermes model
```

This command must be run in an interactive terminal. It will:
- Generate a device code
- Save pending flow state to `pending_nous_device_flow_latest.json`
- Display verification URL and user code
- Wait for user to complete browser authentication

### 3. Complete Device Flow
After visiting the verification URL and entering the user code, run:

```bash
python3 ${PROFILES_DIR}/gentech/scripts/complete_nous_device_flow.py
```

This script will:
- Poll the OAuth token endpoint
- Save tokens to `auth.json`
- Remove the pending flow file

## Key Learnings

### Script Behavior
The `refresh_nous_oauth.py` script correctly handles the "needs_reauth" condition:
- Returns `success: false` but `needs_reauth: true`
- Exit code 0 to avoid false monitoring alerts
- Provides clear message with next steps

### System Design
- Automated refresh handles normal token expiry
- Device flow handles fully revoked sessions
- Clear separation between automated and manual steps
- Good error handling and user guidance

### Monitoring Integration
The script is well-designed for monitoring:
- Exit code 0 for expected maintenance states
- JSON output with `needs_reauth` flag
- No false alerts during normal maintenance

## Prevention
- Regular token refresh via cron prevents expiry
- Monitor `needs_reauth` flag in script output
- Keep `hermes model` command available for manual intervention
- Test the workflow periodically

## References
- Main refresh script: `${PROFILES_DIR}/gentech/scripts/refresh_nous_oauth.py`
- Device flow completion: `${PROFILES_DIR}/gentech/scripts/complete_nous_device_flow.py`
- Auth state: `${PROFILES_DIR}/gentech/auth.json`
- Configuration: `${PROFILES_DIR}/gentech/config.yaml`