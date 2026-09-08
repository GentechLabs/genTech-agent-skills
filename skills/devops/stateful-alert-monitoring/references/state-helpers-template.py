#!/usr/bin/env python3
"""
State helpers template — copy into any stateful monitoring script.
Implements atomic load/save with migration support.
"""

import json
import os
import tempfile
from datetime import datetime, timezone
from typing import Any, Dict

DEFAULT_STATE = {
    "version": 1,
    "last_run": None,
    "pending_breakout": {},
    "last_alert_sent": None,
    "alert_history": [],
    "counters": {
        "total_runs": 0,
        "alerts_sent": 0,
        "false_positives_cancelled": 0
    }
}

def load_state(path: str) -> Dict[str, Any]:
    """Load state from JSON file, creating default if missing."""
    try:
        with open(path, 'r') as f:
            state = json.load(f)
        # Migration: ensure all keys present
        for k, v in DEFAULT_STATE.items():
            if k not in state:
                state[k] = v
        return state
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_STATE.copy()

def save_state(path: str, state: Dict[str, Any]) -> None:
    """Atomically write state to disk (write to tmp, then rename)."""
    dir_name = os.path.dirname(path)
    os.makedirs(dir_name, exist_ok=True)
    # Write to temp file in same directory (atomic on same filesystem)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix='.tmp')
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(state, f, indent=2)
        os.replace(tmp_path, path)  # atomic
    except Exception:
        os.unlink(tmp_path)
        raise

def now_iso() -> str:
    """Current timestamp in ISO format with timezone."""
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')

def minutes_elapsed(timestamp: str) -> float:
    """Minutes elapsed since given ISO timestamp."""
    if not timestamp:
        return float('inf')
    t = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S%z')
    return (datetime.now(timezone.utc) - t).total_seconds() / 60

def prune_alert_history(state: Dict[str, Any], max_age_hours: int = 24) -> None:
    """Remove alert_history entries older than max_age_hours."""
    cutoff = datetime.now(timezone.utc).timestamp() - (max_age_hours * 3600)
    state['alert_history'] = [
        e for e in state['alert_history']
        if datetime.strptime(e['sent_at'], '%Y-%m-%dT%H:%M:%S%z').timestamp() > cutoff
    ]

# Example usage inside script:
# STATE_PATH = os.path.expanduser('~/.hermes/scripts/.defi-master-state.json')
# state = load_state(STATE_PATH)
# state['last_run'] = now_iso()
# state['counters']['total_runs'] += 1
# save_state(STATE_PATH, state)
