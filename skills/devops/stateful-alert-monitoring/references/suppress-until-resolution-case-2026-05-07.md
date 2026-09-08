# Suppress-Until-Resolution Pattern — Implementation Case
## Session: 2026-05-07 (Jordan + Gentech)

### Context
Jordan requested a change to the LP monitoring alert logic:
> "There can be one notification... but after that, everything else could be silent until there's an action done."

This differs from the standard debounce pattern (alert → rate-limit → alert again). The new pattern is: **alert once → silence → re-arm only when condition resolves**.

### Implementation in defi-lp-consolidated.py

#### State Fields Added
```json
{
  "oor_alerted": false,
  "oor_alert_time": null,
  "eff_alerted": false,
  "eff_alert_time": null
}
```

#### Logic in check_alerts()
```python
# Track condition resolution
oor_alerted = state.get("oor_alerted", False)
eff_alerted = state.get("eff_alerted", False)

# Reset flags when conditions resolve
if oor_alerted and not out_of_range:
    state["oor_alerted"] = False
    state["oor_alert_time"] = None

if eff_alerted and efficiency >= EFFICIENCY_CRITICAL_PCT:
    state["eff_alerted"] = False
    state["eff_alert_time"] = None

# Only alert if not already alerted for this condition instance
if out_of_range and not oor_alerted:
    # ... send alert ...
    state["oor_alerted"] = True
    state["oor_alert_time"] = now

if efficiency < EFFICIENCY_CRITICAL_PCT and not eff_alerted:
    # ... send alert ...
    state["eff_alerted"] = True
    state["eff_alert_time"] = now
```

### Why This Works
1. **One alert per condition instance** — the boolean flag prevents re-alerting
2. **Automatic re-arming** — flag resets only when condition resolves (price returns to range OR efficiency recovers above 30%)
3. **Clean cycle** — detect → alert → suppress → resolve → re-arm → next occurrence

### Comparison with Other Patterns

| Pattern | Behavior | Use Case |
|---------|----------|----------|
| **Standard Debounce** | Alert → rate-limit → alert again after interval | When repeat alerts add value (trending conditions) |
| **Suppress-Until-Resolution** | Alert → silence → re-arm on resolution | When repeat alerts are noise (static conditions) |
| **Immediate + Rate-Limit** | Alert every time, but cap frequency | Safety-critical systems |

### Jordan's Rule
Monitoring cron jobs should:
1. Alert ONCE per condition change
2. Stay silent otherwise
3. Re-arm only when the condition resolves and could recur

This prevents notification fatigue while ensuring each new condition instance gets attention.
