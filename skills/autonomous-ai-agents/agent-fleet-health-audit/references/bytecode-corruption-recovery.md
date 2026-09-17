# Bytecode Corruption Recovery — Marshal Data Too Short

## Problem
Repeated `EOFError: marshal data too short` exceptions during module imports, typically from files in `__pycache__/` with malformed headers.

**Observed in session:** `gemini_native_adapter.cpython-311.pyc` had source size fields showing gigabyte values, causing import failures across YoYo and Gentech.

## Immediate Diagnosis

```bash
# 1. Confirm corrupted file location from error log
grep -oP "~?/.*\.pyc" ~/.hermes/profiles/<agent>/logs/errors.log | head -1

# 2. Check file size and modification time
ls -lh <corrupted-file>

# 3. Try to recompile manually (will fail if corrupted)
python -m py_compile <corrupted-file>
```

## Recovery Sequence

### Step 1 — Stop all agent gateways
```bash
# Graceful shutdown all running agents
hermes -p yoyo gateway stop
hermes -p dmob gateway stop
hermes -p desmond gateway stop
hermes -p gentech gateway stop

# Or kill all hermes gateway processes
pkill -f "hermes_cli.main.*gateway run"
```

### Step 2 — Delete all shared bytecode caches
```bash
# Primary shared library
rm -rf ${INSTALL_DIR}/agent/__pycache__/
rm -rf ${INSTALL_DIR}/tools/__pycache__/

# Also clear any per-profile caches (if present)
find ~/.hermes -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
```

### Step 3 — Restart the master orchestration service
```bash
systemctl --user daemon-reload
systemctl --user start hermes-gateway.service
```

### Step 4 — Restart each agent gateway
```bash
hermes -p yoyo gateway run --replace &
hermes -p dmob gateway run --replace &
hermes -p desmond gateway run --replace &
hermes -p gentech gateway run --replace &
```

### Step 5 — Validate clean state
```bash
# Wait 30 seconds, then check logs
tail -n 50 ~/.hermes/profiles/<agent>/logs/errors.log | grep -i marshal
# Should return empty

# Run a test session search to trigger import
hermes -p yoyo session search "test" 2>&1 | head -20
# Should succeed without traceback
```

## Why Deletion from Disk Isn't Enough

Corrupted bytecode remains **in memory** of any running Python process that already imported the module. That's why a full gateway restart is mandatory — not just file deletion.

## Prevention

- Keep disk usage below 80%: `df -h` should show healthy margin
- Avoid interrupting `hermes gateway run` or deployment processes
- Regular session vacuum: `hermes sessions vacuum --days 7` to reduce disk pressure
- Monitor `${INSTALL_DIR}/` for unexpected `.pyc` modification times

## Automation Script

The `agent-fleet-health-audit` skill includes a `scripts/` bundle you can call:
```bash
# Not yet implemented — will be added in future skill update
```
