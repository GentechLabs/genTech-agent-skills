# AAE Tactical Retreat — Active Defense for LP Positions

> **Phase 1: ✅ BUILT and LIVE (Jul 18, 2026)**
> Implementation in `lp-monitor-v2.py` + `fed-event-tracker.py`
> Spec: `00-HQ/defense-phase1-spec.md`

## Core Loop

DEPLOY → EARNING → BREAKOUT → HOLD (3m timer) → BREAKOUT CONFIRMED → 🛡️ RETREAT → SENTINEL → RE-ENTER

## State Machine (Built)

Tracked in `.lfj-defi-state.json`:

| State | Field | Meaning |
|-------|-------|---------|
| `null` | `defense_mode` | Position in range, no defense active |
| `"SENTINEL"` | `defense_mode` | Out of range, timer counting down |
| `"RETREATED"` | `defense_mode` | Timer exceeded — retreat confirmed |
| ISO timestamp | `breakout_start` | When continuous out-of-range began |
| `true/false` | `breakout_confirmed` | True when timer >= threshold |
| 180 (default) | `breakout_threshold_seconds` | Configurable (2-5 min range) |

## Implementation

### `check_defense()` in `lp-monitor-v2.py`

```python
def check_defense(state, in_range, now=None):
    threshold = state.get("breakout_threshold_seconds", 180)
    breakout_start = state.get("breakout_start")
    
    if in_range:
        if breakout_start is not None:
            state["breakout_start"] = None
            state["breakout_confirmed"] = False
            state["defense_mode"] = None
            return "RECOVERED", 0
        return "IN_RANGE", 0
    
    if breakout_start is None:
        state["breakout_start"] = now.isoformat()
        state["defense_mode"] = "SENTINEL"
        return "SENTINEL", 0
    
    elapsed = (now - datetime.fromisoformat(breakout_start)).total_seconds()
    if elapsed >= threshold and not state.get("breakout_confirmed"):
        state["breakout_confirmed"] = True
        state["defense_mode"] = "RETREATED"
        return "BREAKOUT_CONFIRMED", int(elapsed)
    
    return "SENTINEL", int(elapsed)
```

### FOMC Auto-Defense

In `fed-event-tracker.py` — sets SENTINEL 24h before FOMC:

```python
if days_until == 1:
    set_defense_mode("SENTINEL", f"FOMC tomorrow ({meeting['decision']})")
elif days_until == 0:
    set_defense_mode("SENTINEL", f"FOMC today ({meeting['decision']})")
elif days_until == -1:
    set_defense_mode("SENTINEL", f"Post-FOMC ({meeting['decision']}) — awaiting clear signal")
```

### Report Line

Every LP report shows:
```
Defense: ✅ NORMAL | 👁️ SENTINEL — watching | 🛡️ RETREATED — BREAKOUT CONFIRMED
```

## Key Integration Points

| System | Role |
|--------|------|
| `lp-monitor-v2.py` | 10-min cadence, breakout detection + defense timer |
| `fed-event-tracker.py` | Macro calendar → auto-set SENTINEL 24h before FOMC |
| `.lfj-defi-state.json` | Defense state: mode, breakout_start, confirmed |
| LP report | Defense status line, confirmed breakouts always reported |

## Re-entry Signals

| Signal | Source | Threshold |
|--------|--------|-----------|
| Fear & Greed | Tradesta / CMC | Rising from 25 → 35+ |
| 1h volume | DexScreener | Returning to 24h average |
| Price consolidation | Pyth | 2+ hours narrow range |
| Macro calendar | fed-event-tracker | Next event > 48h away |
