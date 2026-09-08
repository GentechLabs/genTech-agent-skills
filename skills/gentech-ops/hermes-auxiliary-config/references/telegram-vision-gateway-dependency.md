# Telegram Vision Gateway Dependency

**Issue**: vision_analyze works in CLI but fails in Telegram with "model unknown" errors, despite correct auxiliary.vision configuration.

**Root Cause**: When `browser.use_gateway = true` or `web.use_gateway = true` but NO gateway server is running, Telegram gateway sessions cannot route vision requests. The tools attempt to use a nonexistent gateway, causing failures.

**Context**: This issue does NOT affect CLI sessions because CLI sessions don't route through gateway. It only affects:
- Telegram gateway sessions
- Discord gateway sessions  
- Any platform where the agent runs via gateway

**Symptoms**:
```
# Telegram session
User: [sends image]
Agent: vision_analyze(...)
Tool: ERROR: model unknown or timeout
```

```
# CLI session (same config)
$ hermes chat
User: vision_analyze(...)
Tool: ✓ Works correctly
```

**Diagnosis**:
```python
import yaml

config_path = "~/.hermes/profiles/gentech/config.yaml"

with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Check gateway settings
browser_gateway = config.get('browser', {}).get('use_gateway', False)
web_gateway = config.get('web', {}).get('use_gateway', False)

print(f"browser.use_gateway: {browser_gateway}")
print(f"web.use_gateway: {web_gateway}")

# Check if gateway server is running
import subprocess
result = subprocess.run(['hermes', 'gateway', 'status'], capture_output=True)
gateway_running = 'running' in result.stdout.decode().lower()

print(f"\nGateway server running: {gateway_running}")

if (browser_gateway or web_gateway) and not gateway_running:
    print("\n⚠️  GATEWAY DEPENDENCY DETECTED")
    print("   Vision will fail in Telegram/Discord until:")
    print("   1. Gateway server is started, OR")
    print("   2. Gateway routing is disabled")
```

**Fix - Disable Gateway Routing**:
```python
import yaml

config_path = "~/.hermes/profiles/gentech/config.yaml"

with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Disable gateway for browser and web
if 'browser' in config:
    config['browser']['use_gateway'] = False

if 'web' in config:
    config['web']['use_gateway'] = False

# Write back
with open(config_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False, indent=2, allow_unicode=True)

print("✓ Gateway routing disabled")
print("  Vision will now call ZAI directly from Telegram")
```

**Or via hermes config**:
```bash
hermes config set browser.use_gateway false
hermes config set web.use_gateway false
```

**When to Enable Gateway**:
- Gateway server IS running (`hermes gateway serve`)
- You want centralized tool routing across all platforms
- Multi-agent setup with shared gateway
- Need tool usage analytics via gateway

**When to Disable Gateway**:
- Single-agent setup (VPS only, desktop only)
- No gateway server running
- Direct provider access works fine
- Simpler config, fewer moving parts

**Session Example**:
```
User: Why is vision not working on Telegram?
Agent: Let me audit the config... ✓ auxiliary.vision looks correct
Agent: Checking gateway settings... Found browser.use_gateway=true
Agent: Gateway server is NOT running. That's the issue.
Agent: Disabling gateway routing...
User: Try again.
Agent: ✓ Vision now works in Telegram
```

**Related Configuration**:
```yaml
# CORRECT for single-agent setup
browser:
  use_gateway: false          # Direct provider access

web:
  use_gateway: false          # Direct provider access

auxiliary:
  vision:
    provider: zai             # Calls ZAI directly
    model: glm-5.2
```

```yaml
# CORRECT for multi-agent with gateway server
gateway:
  api_server:
    enabled: true
    host: 0.0.0.0
    port: 8648

browser:
  use_gateway: true           # Route through gateway server

web:
  use_gateway: true           # Route through gateway server

auxiliary:
  vision:
    provider: zai
    model: glm-5.2
```

**Verification**:
After fixing, test vision in Telegram:
1. Send an image
2. Agent should analyze it without errors
3. No "model unknown" or timeout messages

**Lesson Learned**: Auxiliary config is NOT the only failure point. Gateway routing settings can block tool execution even when auxiliary.* config is correct. Always check both when gateway sessions fail.

**Session Reference**: Gentech session (Jul 5, 2026) - vision worked in CLI but failed in Telegram. Root cause was browser.use_gateway=true with no gateway server. Fix: set browser.use_gateway=false and web.use_gateway=false.