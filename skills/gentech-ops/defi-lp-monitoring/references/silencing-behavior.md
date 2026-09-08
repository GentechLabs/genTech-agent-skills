# DeFi LP Monitor Silencing Behavior

**Updated**: June 27, 2026

## Rule: Silence Resets on Material Movement

When price moves ≥1% OR ≥$0.20, the monitor **must reset silence** and resume 10-minute reporting.

**Why**: Jordan wants visibility during volatile periods. Silence is for stagnant periods, not when the market is moving.

### Implementation

In `should_send_report()`:

```python
# Material movement: 1% or $0.20 threshold → reset silence, resume 10-min reporting
if price_change_pct >= 1.0 or price_change_abs >= 0.20:
    reasons.append(f"price {price_change_pct:.1f}%")
    state["consecutive_quiet_runs"] = 0  # RESET: movement clears silence
    state["last_report_hour"] = now_dt.hour
```

**What changed**:
- REMOVED: `<0.2% and <$0.05` instant-silence rule (was blocking reports on micro-moves)
- ADDED: Silence counter resets when material movement detected

---

## Two-Tier Efficiency Alerts

| Threshold | Type | Behavior |
|-----------|------|----------|
| **<50%** | Warning | Alert once, then stay quiet until efficiency recovers ≥50% |
| **<30%** | Critical | Alert once, then stay quiet until efficiency recovers ≥30% |

**Why**: Jordan wants to know when efficiency drops below 50%, but doesn't want repeated warnings. One alert is enough to confirm awareness.

### Implementation

**Constants**:
```python
EFFICIENCY_CRITICAL_PCT = 30.0
EFFICIENCY_LOW_DEBOUNCE_SEC = 300
EFFICIENCY_WARNING_PCT = 50.0  # NEW
```

**State flags** (added to default state):
```python
{
    "oor_alerted": False,
    "eff_alerted": False,
    "eff_warn_alerted": False,      # NEW
    "efficiency_warn_start": None,  # NEW
}
```

**Warning alert logic** (inserted before critical alert):

```python
eff_warn_alerted = state.get("eff_warn_alerted", False)

if efficiency < EFFICIENCY_WARNING_PCT:
    if state.get("efficiency_warn_start") is None:
        state["efficiency_warn_start"] = now
    else:
        elapsed = now - state["efficiency_warn_start"]
        if elapsed >= EFFICIENCY_LOW_DEBOUNCE_SEC:
            if not eff_warn_alerted:
                alerts.append({
                    "severity": "LOW",
                    "type": "EFFICIENCY_WARNING",
                    "message": f"Fee efficiency {efficiency:.1f}% below 50% — monitor position",
                    "action": "No action needed, just aware"
                })
                state["eff_warn_alerted"] = True
                state["eff_warn_time"] = now
else:
    state["efficiency_warn_start"] = None
    if eff_warn_alerted:
        state["eff_warn_alerted"] = False
        state["eff_warn_time"] = None
```

**Critical alert** (30%) keeps existing logic but adds resolution reset.

---

## Alert Severity Icons

Report formatting updated to handle LOW severity:

```python
icon = "🔴" if sev == "HIGH" else "🟡" if sev == "MEDIUM" else "🟢" if sev == "LOW" else "⚪"
```

- 🔴 HIGH: Out of range, immediate action
- 🟡 MEDIUM: <30% efficiency, consider rebalance
- 🟢 LOW: <50% efficiency, monitor (NEW)
- ⚪ INFO: Default

---

## When to Stay Silent

- Price moves <1% AND <$0.20 AND
- Efficiency ≥50% (no warning threshold triggered) AND
- In range (no OOR alert) AND
- 2+ consecutive quiet runs this hour

**NOT silent when**:
- Price moves ≥1% or ≥$0.20 → **resume reporting**
- New alert condition triggers → send report
- Hour rolls over → counter resets