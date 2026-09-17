# EOFError: marshal data too short — Corrupted Python Bytecode

## Symptom
Repeated errors in agent logs:
```
File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
File "<frozen importlib._bootstrap_external>", line 936, in exec_module
File "<frozen importlib._bootstrap_external>", line 1069, in get_code
File "<frozen importlib._bootstrap_external>", line 729, in _compile_bytecode
EOFError: marshal data too short
```

Session summarization fails with: "Session summarization failed after 3 attempts: marshal data too short"

## Root Cause
Python `.pyc` bytecode cache file is corrupted (truncated/incomplete). Commonly affects:
- `${INSTALL_DIR}/agent/gemini_native_adapter.pyc`
- Agent-specific `__pycache__` directories

The `.pyc` file size is abnormally small vs. the corresponding `.py` source.

## Impact
- Session search and summarization completely broken
- Any operation requiring that module import fails
- Affects ALL agents sharing the same installation (system-wide) or single agent (profile-specific)

## Fix
**Automatic regeneration** (preferred):
Python detects corrupted bytecode and recompiles automatically on next import. Wait 1-2 minutes; verify by checking `.pyc` file timestamp and size (should increase to ~expected size).

**Manual regeneration** (if auto-fails):
```bash
# System-wide
rm -rf ${INSTALL_DIR}/agent/__pycache__

# Agent-specific (if bytecode lives in profile dir)
rm -rf ~/.hermes/profiles/<agent>/__pycache__
```

Then restart the agent gateway:
```bash
hermes -p <agent> gateway restart
```

**Reinstall** (last resort):
```bash
cd ${INSTALL_DIR}
pip install --force-reinstall -e .
```

## Verification
Check error log after fix:
```bash
tail -20 ${PROFILES_DIR}/<agent>/logs/errors.log
```
Should show no new EOFError entries. Test session search:
```bash
hermes sessions list --limit 5
```

## Prevention
- Avoid concurrent agent processes writing to same `.pyc` (rare)
- Ensure disk is not full during bytecode writes
- Regular package updates avoid known corruption bugs

## References
- Python import system: https://docs.python.org/3/library/importlib.html#the-machinery
- Marshal format: https://docs.python.org/3/library/marshal.html
