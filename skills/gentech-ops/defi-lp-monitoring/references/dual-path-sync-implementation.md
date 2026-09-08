# Dual-Path Sync Implementation

## The Problem

Hermes runs from `/root/.hermes/profiles/gentech/` (HERMES_HOME), but Jordan's manual rebalances update files at `/root/.hermes/scripts/` (global). Cron scripts read from the profile path. If they drift, the monitor reports stale ranges and false "OUT OF RANGE" alerts.

**Root cause (Jun 24, 2026):** Jordan rebalanced to $6.30–$6.559 on June 23, updating the global tracker. The profile tracker still had $9.30–$9.60 from June 21. The cron script read the stale profile file and reported "OUT OF RANGE" with 0% efficiency.

## The Fix

Add `sync_tracker()` and `sync_config()` functions to `defi-lp-consolidated.py` that write to BOTH paths simultaneously:

```python
# Add near the top of defi-lp-consolidated.py, after path resolution

GLOBAL_SCRIPTS_DIR = os.path.join(os.path.expanduser("~/.hermes"), "scripts")

def sync_tracker(data: dict):
    """Write position tracker to BOTH profile and global paths to prevent drift."""
    for path in [POSITION_TRACKER_PATH, os.path.join(GLOBAL_SCRIPTS_DIR, ".lfj-position-tracker.json")]:
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

def sync_config(data: dict):
    """Write AAE config to BOTH profile and global paths to prevent drift."""
    for path in [AAE_CONFIG_PATH, os.path.join(GLOBAL_SCRIPTS_DIR, ".lfj-aae-config.json")]:
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
```

## Where to Use

Replace ALL `with open(POSITION_TRACKER_PATH, "w")` and `with open(AAE_CONFIG_PATH, "w")` calls with `sync_tracker()` and `sync_config()` respectively.

In `verify_on_chain()`:
- Range auto-correction: `sync_tracker(tracker)` instead of direct file write
- Config auto-correction: `sync_config(cfg)` instead of direct file write
- Shape auto-correction: `sync_tracker(tracker)` instead of direct file write

## Manual Rebalancing

When Jordan rebalances manually, always update BOTH paths:

```bash
# After extracting new values from LFJ screenshot
cp /root/.hermes/scripts/.lfj-position-tracker.json /root/.hermes/profiles/gentech/scripts/.lfj-position-tracker.json
cp /root/.hermes/scripts/.lfj-aae-config.json /root/.hermes/profiles/gentech/scripts/.lfj-aae-config.json
```

Or use the `sync_tracker()` function in Python.
