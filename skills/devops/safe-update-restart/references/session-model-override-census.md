# Session model override — census, clear, and verify (measured 2026-09-27)

A persisted `/model` override outranks `config.yaml` and **skips the fallback chain**. It survives a
restart. Two storage locations. This is the recipe.

## 1. Census — every profile, both locations

```python
import sqlite3, json, os, glob

roots = [("(default)", "/root/.hermes")]
for d in sorted(glob.glob("/root/.hermes/profiles/*/")):
    roots.append((d.rstrip("/").split("/")[-1], d.rstrip("/")))

for name, root in roots:
    # sessions.json sits at <root>/sessions/sessions.json for the default profile but under
    # <root>/sessions/<profile>/sessions.json when the profile has its own dir. Do not assume
    # the layout — resolve it, or run the canonical script from the seat itself (gizmo, Sep 30).
    db = f"{root}/state.db"
    mir = f"{root}/sessions/sessions.json"
    if not os.path.exists(mir):
        mir = f"{root}/sessions/{name}/sessions.json"
    dbp, mp = [], []
    if os.path.exists(db):
        c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)      # read-only: never lock a live gateway
        for k, ej in c.execute("select session_key, entry_json from gateway_routing"):
            o = json.loads(ej)
            if o.get("model_override"): dbp.append((k, o["model_override"]))
        c.close()
    if os.path.exists(mir):
        d = json.load(open(mir))
        mp = [(k, v["model_override"]) for k, v in d.items()
              if isinstance(v, dict) and v.get("model_override")]
    print(f"{name:18} DB={len(dbp)} mirror={len(mp)}")
    for k, mo in dbp + mp:
        print(f"    {k} -> {mo.get('provider')}/{mo.get('model')}  base_url={mo.get('base_url')}")
```

`scope` in `gateway_routing` is the resolved sessions dir — one row per session key, not per profile.

## 1.5 Verify a zero count is a real zero, not a missing table (Pixel, Sep 30)

`DB=0` can mean 'no session carries a model_override' OR 'the gateway_routing table was
absent or unread'. A census that finds no table also prints zero, and trusting the wrong zero
creates false confidence. Before accepting a zero count:

1. Confirm the table exists and the query reached it:
   ```python
   tables = {r[0] for r in cur.execute(
       "SELECT name FROM sqlite_master WHERE type='table'")}
   assert 'gateway_routing' in tables
   ```
2. Confirm the field being counted is the right field. The census counts
   `entry_json.model_override` (the pin), not the recorded `model` of each session. A
   session's stored `model` value is a receipt, not an override; counting it would
   over-report pins.
3. If the table exists and the field is correct, then zero means zero.

This same rule applies to any 'none found' census: verify the denominator before acting on the count.

## 2. Decide, do not assume — compare against the healthy rail

An override is only a defect if it routes somewhere `config.yaml` would not. Compare
`override.provider/model` against `config.yaml → model.provider/default`. Same value + same base_url =
a no-op; leave it visible rather than silently deleting it.

## 3. Clear — key REMOVED, not nulled

A healthy entry has **no** `model_override` key at all. Match that shape, and back up first:

```python
import json, os, shutil, time
STALE = "opencode-go"            # the provider you are clearing
for p in ["gizmo", "pixel"]:
    path = f"/root/.hermes/profiles/{p}/sessions/sessions.json"
    shutil.copy2(path, f"{path}.bak-staleoverride-{time.strftime('%Y%m%d-%H%M%S')}")
    d = json.load(open(path))
    for k, v in d.items():
        if k.startswith("_") or not isinstance(v, dict): continue
        mo = v.get("model_override")
        if isinstance(mo, dict) and (mo.get("provider") or "").lower() == STALE:
            v.pop("model_override", None)          # remove the key, do not set None
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(d, fh, indent=2); fh.flush(); os.fsync(fh.fileno())
    os.replace(tmp, path)                          # atomic
```

For the DB, prefer the runtime API (`store.set_model_override(session_key, None)`). A direct write is a
**3-place edit** — the `gateway_routing` row, its `entry_json`, and the mirror — or it is half-done.

## 4. Clear, THEN restart, THEN verify

The restart is what makes the clear take effect (`_rehydrate` is a no-op while an in-memory override
exists). After it, check the DB **and** the mirror, and confirm a new `MainPID` +
`ExecMainStartTimestamp`.

## 5. Why the mirror matters — and how to prove it rather than guess

`_import_legacy_sessions_json` folds in only `keys the DB lacks`, so the mirror is **shadowed** while the
DB row exists and **resurrects the pin if that row is lost**. Replicate the branch instead of arguing:

```python
# DB row present -> imported {}  (shadowed, safe)
# DB row LOST    -> imports the stale pin  (the override returns)
```
