# Tactical Retreat — Breakout Detection & Defense Timer

Added: 2026-07-18  
Pattern: Out-of-range breakout timer → SENTINEL → RETREATED → RECOVERED  
State file: `.lfj-defi-state.json`

## The Loop

```
IN RANGE → ✅ NORMAL (defense_mode: null)
    ↓ price exits range
SENTINEL — counting down (default 3 min threshold)
    ↓ stays out > 3 min
BREAKOUT CONFIRMED → 🛡️ RETREATED (defense_mode: "RETREATED")
    ↓ price re-enters
RECOVERED → reset everything (defense_mode: null)
```

## Implementation

The `check_defense()` function lives in `lp-monitor-v2.py` and runs every cron tick:

```python
def check_defense(state, in_range, now=None):
    """
    Returns (status, elapsed_seconds)
    Status: IN_RANGE | SENTINEL | BREAKOUT_CONFIRMED | RECOVERED
    """
    threshold = state.get("breakout_threshold_seconds", 180)  # default 3 min
    # ... tracks continuous out-of-range duration
    # ... when threshold exceeded, sets defense_mode = "RETREATED"
```

## State Fields (`.lfj-defi-state.json`)

| Field | Type | Description |
|-------|------|-------------|
| `defense_mode` | string or null | `null` | `"SENTINEL"` | `"RETREATED"` |
| `breakout_start` | ISO string or null | When continuous out-of-range began |
| `breakout_confirmed` | bool | True when timer exceeded threshold |
| `breakout_threshold_seconds` | int | Configurable, default 180 (3 min) |
| `last_defense_action` | ISO string or null | Last retreat/entry timestamp |

## Report Integration

The LP report now shows a defense status line:

```
Defense: 🛡️ RETREATED — BREAKOUT CONFIRMED
Defense: 👁️ SENTINEL — watching (45s elapsed)
Defense: ✅ NORMAL
```

Confirmed breakouts **always trigger a report** (overrides debounce).

## FOMC Auto-Defense

The `fed-event-tracker.py` auto-sets SENTINEL mode 24h before FOMC:

```python
set_defense_mode("SENTINEL", "FOMC tomorrow (Hold)")
# Clears to normal post-FOMC when market stabilizes
```

## Configuration

| Parameter | Default | Location |
|-----------|---------|----------|
| `breakout_threshold_seconds` | 180 (3 min) | `.lfj-defi-state.json` |
| FOMC auto-defense | Enabled | `fed-event-tracker.py` |

## Pitfalls

- **Don't set threshold too low** — 30s catches noise. 2-5 min filters real breakouts.
- **Don't set too high either** — 10+ min means the breakout already happened. 3 min is calibrated.
- **State file must be writable** — `check_defense` writes to `.lfj-defi-state.json` every tick. If the file is read-only or path is wrong, defense silently fails.
- **Post-FOMC recovery is manual** — Currently SENTINEL stays set 24h after FOMC. Auto-recovery signals when prices stabilize is future work.
