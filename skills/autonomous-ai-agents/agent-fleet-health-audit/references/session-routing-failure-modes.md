# Session Routing Failure Modes

## Two Distinct Signatures

Session routing failures manifest in two ways with different severity levels:

### Level 1: `agent: "unknown"` (Moderate)
- Session file contains `"agent": "unknown"` and `"profile": "unknown"` as string values
- Indicates the routing pipeline is broken but the session writer is still running
- Likely cause: hermes-cron not injecting agent context, or session writer failing to resolve agent tag
- Check gateway.log for "agent tag" parsing errors

### Level 2: `agent` key MISSING entirely (Severe)
- Session JSON lacks the `agent` and `profile` keys completely (not set to any value)
- Indicates cron dispatch without ANY context injection — the session was created but no agent metadata was attached
- More severe than "unknown" because it means the context injection pipeline is entirely absent
- Common when cron daemon is missing but jobs are still being dispatched through gateway processes directly

## Detection Method

```python
# Inspect a cron session file:
python3 -c "
import json
f = '${PROFILES_DIR}/<agent>/sessions/<session_file>.json'
with open(f) as fh:
    d = json.load(fh)
print(f'agent: {d.get(\"agent\", \"MISSING\")}')
print(f'profile: {d.get(\"profile\", \"MISSING\")}')
"
```

If output shows `agent: MISSING` (the Python default for missing key), the key doesn't exist in the JSON at all.

## Impact
- Sessions without agent context cannot be properly attributed in search/indexing
- Cron jobs may still execute but results won't appear in agent-specific queries
- Memory and session history become unreliable for affected agents

## Recovery
1. Verify hermes-cron daemon is running (or gateway-level cron dispatch is properly configured)
2. Check that session writer injects agent/profile metadata
3. After fix, new sessions should contain proper `"agent": "<name>"` and `"profile": "<name>"` fields
