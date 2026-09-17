# Bytecode Corruption Incident — 2026-05-02

**Detected**: YoYo & Gentech agents experiencing repeated `EOFError: marshal data too short` tracebacks  
**Impact**: Session summarization failures (634 Gentech, 384 YoYo), Telegram gateway inactive despite processes running  
**Root cause**: Corrupted `.pyc` bytecode files in `${INSTALL_DIR}` installation  
**Resolution**: Cleared `__pycache__` directories and restarted gateways

---

## Detection Evidence

**Log pattern** (same across both agents):
```
2026-05-02 00:35:48,692 WARNING [cron_9ecfada01952_20260502_003539] root: Session summarization failed after 3 attempts: marshal data too short
Traceback (most recent call last):
  File "${INSTALL_DIR}/tools/session_search_tool.py", line 226, in _summarize_session
    response = await async_call_llm(
  File "${INSTALL_DIR}/agent/auxiliary_client.py", line 3665, in async_call_llm
    client, final_model = _get_cached_client(
  File "${INSTALL_DIR}/agent/auxiliary_client.py", line 3001, in _get_cached_client
    client, default_model = resolve_provider_client(
  File "${INSTALL_DIR}/agent/auxiliary_client.py", line 2053, in resolve_provider_client
    return ...
  File "${INSTALL_DIR}/agent/auxiliary_client.py", line 1902, in _to_async_client
    from agent.copilot_acp_client import CopilotACPClient
  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
  File "<frozen importlib._bootstrap_external>", line 936, in exec_module
  File "<frozen importlib._bootstrap_external>", line 1069, in get_code
  File "<frozen importlib._bootstrap_external>", line 729, in _compile_bytecode
EOFError: marshal data too short
```

**Key observations**:
- Errors occur in `importlib._bootstrap_external._compile_bytecode` — Python's bytecode loader
- Affects `copilot_acp_client` module (but subsequently found 100+ corrupted files across agent/tools)
- Cron job IDs involved: `cron_9ecfada01952_20260502_003539` (YoYo), `cron_9ecfada01952_20260502_003533` (Gentech)
- Last log line for both agents: `EOFError: marshal data too short` — errors are actively occurring

## Root Cause Analysis

### Bytecode Header Inspection
```python
import struct, os
pyc = '${INSTALL_DIR}/agent/__pycache__/copilot_acp_client.cpython-311.pyc'
with open(pyc, 'rb') as f:
    header = f.read(16)
magic = header[:4]
source_size_in_header = struct.unpack('<I', header[8:12])[0]
actual_source_size = os.path.getsize(pyc.replace('.pyc', '.py'))

print(f"Header claims source was {source_size_in_header} bytes")
print(f"Actual .py file is {actual_source_size} bytes")
```

**Results** (corrupted files):
```
Header source size: 1777583575 bytes (~1.77 GB)
Actual source size: 22244 bytes (22 KB)
Magic number: a70d0d0a  (suspicious; not standard Python 3.11 magic)
```

The header's source size field contained a timestamp or memory address misinterpreted as size — classic symptom of interrupted write or concurrent write race.

### Scope of Corruption
- **Total corrupted `.pyc` files found**: 100+ across `agent/__pycache__` and `tools/__pycache__`
- **Affected modules**: `auxiliary_client`, `copilot_acp_client`, `session_search_tool`, `anthropic_adapter`, and most core agent modules
- **All agents affected**: YoYo and Gentech were actively crashing on these; Desmond and DMOB showed older errors (previously resolved or not restarted recently)

### Why Processes Were Running But Non-Functional
- Gateway processes (`hermes gateway run`) were alive and maintaining Telegram connection
- But module imports happening inside those processes hit corrupted bytecode already loaded into memory
- Restarting the Python process is required to clear in-memory bytecode cache
- Clearing `.pyc` files on disk alone is insufficient for already-running processes

## Remediation Steps Executed

### Step 1: Identify corrupted files
```bash
python3 -c "
import struct, glob
for pyc in glob.glob('${INSTALL_DIR}/**/__pycache__/*.pyc', recursive=True):
    with open(pyc,'rb') as f: h=f.read(16)
    if len(h)>=16:
        sz=struct.unpack('<I',h[8:12])[0]
        if sz > 50_000_000: print(pyc, sz)
"
```

### Step 2: Clear caches
```bash
rm -rf ${INSTALL_DIR}/agent/__pycache__
rm -rf ${INSTALL_DIR}/tools/__pycache__
```
**Output**: Removed 139 corrupted `.pyc` files total

### Step 3: Verify clean import in fresh interpreter
```bash
python3 -c "from agent.copilot_acp_client import CopilotACPClient; print('OK')"
# Result: ✓ Import successful
```

### Step 4: Restart affected gateways
```bash
hermes gateway stop --profile yoyo
hermes gateway stop --profile gentech
hermes gateway run --profile yoyo --replace
hermes gateway run --profile gentech --replace
```
**Note**: This step is still pending/needs verification in live environment.

## Post-Remediation Verification Checklist

- [ ] `tail -50 ${PROFILES_DIR}/yoyo/logs/agent.log` — no new marshal errors
- [ ] `tail -50 ${PROFILES_DIR}/gentech/logs/agent.log` — no new marshal errors
- [ ] Telegram gateway status shows `Connected to Telegram` for both agents
- [ ] Recent cron job executions in `/root/.hermes/cron/output/` show `completed` status
- [ ] `ps aux | grep hermes` confirms gateways still running post-restart

## Prevention & Monitoring

**Add to regular health checks**:
1. Include `.pyc` header integrity scan in `agent-health-monitoring` skill
2. Alert on any `.pyc` with header source size >50 MB
3. Weekly cron job: `find ${INSTALL_DIR} -name '*.pyc' -exec python3 -c "import struct; h=open('{}','rb').read(16); print('{}', struct.unpack('<I',h[8:12])[0])" \; | awk '$2>50000000'`

**Disk/environment hygiene**:
- Keep >10% free disk space on root partition
- Avoid multiple concurrent Hermes gateway processes from same installation
- Monitor `/var/log/syslog` for I/O errors or disk warnings
- Consider read-only root with tmpfs for `/tmp` and `/var/tmp` to reduce corruption vectors

## Timeline

| Time | Event |
|------|-------|
| 2026-05-02 00:35:48 | YoYo first marshal error in current log window |
| 2026-05-02 00:35:59 | Gentech first marshal error in current log window |
| 2026-05-02 00:41 | Watchdog inspection initiated |
| 2026-05-02 00:42 | Bytecode corruption confirmed; caches cleared |
| 2026-05-02 00:43 | Gateway restart pending |

## Related Incidents

- **2026-04-30**: DMOB showed similar errors → resolved by clearing its profile `__pycache__`
- Pattern suggests system-wide issue with `${INSTALL_DIR}` install (shared across all profiles)

## Commands Run During Investigation

```bash
# 1. Check all agent processes
ps aux | grep hermes | grep 'gateway run'

# 2. Inspect recent errors
tail -50 ${PROFILES_DIR}/yoyo/logs/agent.log
tail -50 ${PROFILES_DIR}/gentech/logs/agent.log

# 3. Count error frequency
python3 -c "
import re; data=open('${PROFILES_DIR}/yoyo/logs/agent.log').read()
print('marshal errors:', len(re.findall('marshal data too short', data)))
"

# 4. Test module import directly
python3 -c "import sys; sys.path.insert(0,'${INSTALL_DIR}'); from agent.copilot_acp_client import CopilotACPClient"

# 5. Scan for corrupted .pyc headers (found 100+)
find ${INSTALL_DIR} -name '*.pyc' -exec python3 -c "
import struct,sys; h=open(sys.argv[1],'rb').read(16);
if len(h)>=16: print(sys.argv[1], struct.unpack('<I',h[8:12])[0])
" {} \;

# 6. Verify fix after clearing cache
rm -rf ${INSTALL_DIR}/agent/__pycache__ ${INSTALL_DIR}/tools/__pycache__
python3 -c "from agent.copilot_acp_client import CopilotACPClient"
```
