# Process Uptime Verification Post-Remediation — 2026-05-02

**Use case**: After any systemic fix (bytecode cleanup, credential rotation, config edit), verify gateways are running fresh instances, not stale pre-fix processes holding corrupted state.

**Date added**: May 2, 2026 incident  
**Discovery**: Post-byetcode-corruption cleanup, YoYo & Desmond processes remained down; DMOB & Gentech uptime showed they restarted at ~00:55 (clean state) vs YoYo (still dead)

---

## Why Uptime Matters

- Corrupted bytecode resides **in memory** of running Python process
- Deleting `.pyc` files on disk **does NOT** clear in-memory cache
- Old processes will continue using corrupted bytecode until restart
- Uptime >1 hour = likely pre-fix instance (needs restart)
- Uptime <5 min = freshly started post-fix (good)

## Diagnostic Command

```bash
ps -eo pid,etimes,cmd | grep hermes | grep gateway
```

Sample output:
```
922890 Ssl     14:32:08 ${INSTALL_DIR}/venv/bin/python -m hermes_cli.main --profile dmob gateway run --replace
923094 Ssl     14:30:37 ${INSTALL_DIR}/venv/bin/python -m hermes_cli.main --profile gentech gateway run --replace
```

Column breakdown:
- `PID` — process ID
- `etimes` — elapsed time in **seconds**
- `cmd` — command line (includes `--profile <name>`)

## Interpretation Table

| etimes (seconds) | Interpretation | Action |
|------------------|----------------|--------|
| `< 60` | Just restarted (<1 min) | ✓ Fresh post-remediation |
| `60 – 300` | Restarted within last 5 min | ✓ Acceptable |
| `300 – 1800` | Restarted 5–30 min ago | ⚠ May be post-fix but monitor |
| `> 1800` (>30 min) | Old process (pre-fix likely) | ✗ **Should restart** |
| `> 3600` (>1 hr) | Definitely pre-fix state | ✗ **Restart immediately** |

## Bulk Restart All Gateways (Recommended After Systemic Fix)

```bash
# Stop all agents
hermes gateway stop --profile yoyo
hermes gateway stop --profile dmob
hermes gateway stop --profile desmond
hermes gateway stop --profile gentech

# Wait for clean shutdown (5–10s)
sleep 5

# Restart all with --replace (fresh interpreter, clean bytecode cache)
hermes gateway run --profile yoyo --replace &
hermes gateway run --profile dmob --replace &
hermes gateway run --profile desmond --replace &
hermes gateway run --profile gentech --replace &

# Verify uptimes are low
sleep 2
ps -eo pid,etimes,cmd | grep hermes | grep gateway | awk '{print $2, $4}'
```

## Quick-check script (paste in shell)

```bash
#!/bin/bash
echo "=== Gateway Process Uptimes ==="
ps -eo pid,etimes,cmd | grep hermes | grep gateway | while read pid etimes rest; do
  profile=$(echo $rest | grep -o '--profile [^ ]*' | cut -d' ' -f2)
  uptime_min=$((etimes / 60))
  if [ "$etimes" -lt 300 ]; then
    status="✓ FRESH"
  elif [ "$etimes" -lt 1800 ]; then
    status="⚠ RECENT"
  else
    status="✗ STALE (RESTART NEEDED)"
  fi
  echo "PID $pid ($profile): ${uptime_min}m ago — $status"
done
```

## Part of Post-Incident Checklist

See `system-health` §6 (Verification Checklist). Add:
- [ ] All gateway processes have `etimes < 300` (restarted within last 5 minutes)
- [ ] No process shows uptime >1 hour after remediation

## Related Finding

Combined with `references/bytecode-corruption-2026-05-02.md` — uptime check confirms whether in-memory corruption has been purged via restart.
