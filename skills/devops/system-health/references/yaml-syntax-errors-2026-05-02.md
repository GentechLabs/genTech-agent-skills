# YAML Syntax Error Blocking Gateway Startup — 2026-05-02

**Agent affected**: YoYo  
**Error**: `mapping values are not allowed here` at line 130, column 13  
**Impact**: Gateway fails to start; process terminated without graceful shutdown  
**Discovery**: May 2, 2026 health check

---

## Symptom

```
2026-05-02 13:38:26,xxx ERROR config: YAML parse error in ${PROFILES_DIR}/yoyo/config.yaml
yaml.parser.ParserError: while parsing a block mapping
  in "${PROFILES_DIR}/yoyo/config.yaml", line 130, column 13
expected <block end>, but found ':'
mapping values are not allowed here
```

**Result**: Gateway logs `Gateway stopped` shortly after; process exits.

## Diagnostic Steps

### 1. Extract problematic line
```bash
sed -n '130p' ${PROFILES_DIR}/yoyo/config.yaml
```

Typical output:
```
some_key:value   # <- missing space after colon
```
or
```
  subkey:subvalue  # <- tab character or wrong indent
```

### 2. Validate entire YAML file
```bash
python3 -c "import yaml; yaml.safe_load(open('${PROFILES_DIR}/yoyo/config.yaml'))"
```
This will fail on first syntax error encountered.

### 3. Check for common YAML pitfalls
```bash
# Detect tabs
cat -A ${PROFILES_DIR}/yoyo/config.yaml | grep '\t'

# Validate with yamllint (if installed)
yamllint ${PROFILES_DIR}/yoyo/config.yaml
```

## Common Causes

| Pattern | Wrong | Right |
|---------|-------|-------|
| No space after colon | `key:value` | `key: value` |
| Tab for indentation | `\tkey: value` | `  key: value` (2 spaces) |
| Mixed tabs/spaces in same file | `  key:\n\t subkey: val` | consistent spaces only |
| Unclosed quote | `key: "unterminated` | `key: "terminated"` |
| Trailing colon without value | `key:` (when value required) | `key: null` or `key: ""` |

## Fix Workflow

1. **Backup** the current config:
   ```bash
   cp ${PROFILES_DIR}/yoyo/config.yaml ${PROFILES_DIR}/yoyo/config.yaml.bak
   ```

2. **Edit** the specific line flagged in error (line 130 in this case):
   ```bash
   nano +130 ${PROFILES_DIR}/yoyo/config.yaml
   ```
   Ensure proper spacing: `key: value` (colon followed by space)

3. **Validate** entire file:
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('${PROFILES_DIR}/yoyo/config.yaml')); print('VALID')"
   ```

4. **Restart** the agent gateway:
   ```bash
   hermes gateway stop --profile yoyo
   hermes gateway run --profile yoyo --replace
   ```

5. **Verify** gateway started cleanly:
   ```bash
   tail -20 ${PROFILES_DIR}/yoyo/logs/gateway.log
   # Should see: "cron ticker started" without YAML errors
   ```

## Prevention

- Run `yamllint` on all config files pre-commit
- Use editor with YAML syntax highlighting and space-only indentation
- Store config templates in `skills/system-health/templates/` for safe copying
- Add pre-start validation hook:
  ```bash
  python3 -c "import yaml; yaml.safe_load(open('config.yaml'))" || { echo "CONFIG INVALID"; exit 1; }
  ```

## Interaction with Other Failures

In the May 2 incident, YoYo's YAML error **compounded** with:
- Pre-existing bytecode corruption (process already unstable)
- Invalid ElevenLabs credentials (TTS still broken after YAML fix)
- Master cron service failure (cron jobs still won't run even after YAML fix)

→ Fix YAML FIRST, then proceed with other remediation steps.
