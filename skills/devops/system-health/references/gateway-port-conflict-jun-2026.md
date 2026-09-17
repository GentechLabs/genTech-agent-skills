# Gateway Port Conflict Incident - June 26, 2026

## Incident Summary
Multiple gateway processes attempting to bind to port 8088, causing "address already in use" failures and preventing remote gateway startup.

## Root Cause Analysis
1. **Background Script Spawning**: Multiple scripts (`open_gateway.py`) spawning gateways without coordination
2. **Stale PID Files**: Gateway lock files persisting after crashes
3. **Process Coordination Failure**: No single source of truth for gateway lifecycle management

## Diagnostic Commands Used

### Step 1: Identify Conflicting Processes
```bash
netstat -tlnp | grep :8088
# Output: tcp 0 0 0.0.0.0:8088 0.0.0.0:* LISTEN 2034195/python3

ps aux | grep 2034195
# Output: root 2034195 0.7 0.3 173960 60028 ? Ssl 12:08 0:00 ${INSTALL_DIR}/venv/bin/python3 -m uvicorn server:app --host 0.0.0.0 --port 8088
```

### Step 2: Force Kill Conflicting Process
```bash
kill -9 2034195
# Confirmed termination with no process found after kill
```

### Step 3: Clean Stale Lock Files
```bash
find ${PROFILES_DIR} -name "gateway.*" -delete
```

### Step 4: Verify Port Availability
```bash
netstat -tlnp | grep :8088
# Output: (no matches - port now free)
```

## Resolution Sequence
1. **Identified** conflicting PID 2034195 via `lsof -ti:8088`
2. **Killed** process with `kill -9` to force termination
3. **Cleaned** stale gateway lock files across all profiles
4. **Restarted** gateway with proper port coordination

## Prevention Strategy
- Implement process coordination before spawning new gateways
- Use unique ports per gateway instance
- Monitor for background script spawning conflicts
- Implement lock file cleanup as part of startup sequence

## Related Patterns
- Similar to systemd service collision patterns (§3q)
- Relates to process uptime verification (§3k)
- Complements gateway health monitoring (§1)

## Key Learning
Gateway lifecycle management requires coordination across multiple startup methods (CLI, systemd, scripts). Always check for port conflicts before starting new gateways, and use `ps` + `netstat` rather than relying on CLI status reports.

---

**Incident Timeline**:
- 12:08: First port conflict observed
- 12:09: Identified conflicting PID 2034195
- 12:10: Force kill and cleanup completed
- 12:10: Gateway successfully restarted on port 8089