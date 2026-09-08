# Stateful Watcher — Implementation Pitfalls (learned live, Aug 2026)

Non-obvious traps hit while building the handoff stalled-task watchdog
(`handoff-watcher.py`). These apply to ANY stateful watcher that reports only
NEW changes and stays silent otherwise. Durable — they'll bite again.

## 1. Age must come from a stable source, NOT file mtime
Git sync/commit/checkout re-touches file mtimes. A file written Aug 12 can
show "8h old" by mtime after a sync. If the file's name carries a date prefix
(`YYYY-MM-DD-...`), derive age from that instead, anchored at midday so
same-day ≈ 12h:

```python
m = re.match(r"^(20\d\d-\d\d-\d\d)", name)
d = datetime.strptime(m.group(1), "%Y-%m-%d").replace(hour=12, minute=0, second=0)
hours_open = max(0.0, (now - d.timestamp()) / 3600)
```

## 2. Dedup across mirrored source dirs — use a `seen` set, not `if key in dict`
When scanning two mirrored roots (e.g. `root/` and `mirror/`), the naive
`if key in result` check compares a tuple against dict keys (which are rel
paths) — it NEVER matches, so every item appears twice. Fix: track a separate
`seen = set()` of the dedup key and skip if already seen, BEFORE the other
filters.

## 3. Seed the state file when you add a NEW detection type
A stateful watcher keeps a JSON state of what it already reported. When you
first add a new detection (returns, in_progress, stalled), the state file
won't have that key yet, so the FIRST run dumps the whole backlog at the user.
Seed the state with the current set so only genuinely NEW items fire:

```python
d = json.load(open('watcher.state.json'))
d['stalled'] = sorted(find_stalled().keys())
json.dump(d, open('watcher.state.json','w'), indent=2)
```

## 4. A hyphen in the module name breaks `import`
`handoff-watcher.py` can't be `import handoff_watcher` (ModuleNotFoundError).
When another script needs its functions, load by file path via importlib:

```python
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "handoff_watcher_nightly",
    "/root/.hermes/profiles/gentech/scripts/handoff-watcher.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
stalled_rel = set(_mod.find_stalled().keys())
```

## 5. Status matchers are literal — synonyms/emojis don't match
A `is_resolved()`-style matcher checks for exact substrings (`resolved|done|closed|[x]`).
A note marked `Status: ⏸ EXPIRED` or `Status: shipped + blocked` is NOT caught
and keeps showing as open/stalled. When closing a note, use the literal word
the matcher knows (e.g. `**Status:** resolved — EXPIRED, ...`), not a synonym
or emoji.

## 6. A routing/response note you create is itself a new open item
When you route a flagged item by writing a new note, that note is itself
"open" and appears in the view until the recipient returns on it. Correct
behavior — don't be surprised by it.

## 7. Never auto-delete what the watcher flags — hold for review
If a nightly/cleanup job auto-archives stale items, it will silently sweep up
items the watcher flagged as needing attention. Pull the live flagged set into
the cleanup job and HOLD those (guard runs BEFORE the age check, so it holds
regardless of age). Surface them in the report under a "held for review — NOT
archived" section until resolved. The watchdog flags; a human sorts.
