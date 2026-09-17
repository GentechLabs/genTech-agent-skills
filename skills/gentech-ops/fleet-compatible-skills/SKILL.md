---
name: fleet-compatible-skills
description: "Use when building or changing a skill, script or cron."
version: "1.0.0"
---

# Fleet-Compatible by Default

Jordan, Sep 17: *"We need to make all of us consider making all of our skills fleet
compatible... there are times where we're doing something that everybody needs to be able
to do, and I didn't even think about compatibility."*

**The default is: every seat needs this.** Seat-specific is the exception, and it must be
declared out loud — never the silent result of who happened to write the file.

## The rule

Before writing a new skill or script, answer one question:

> **Would the other three seats ever need this?**

If yes (and the honest answer is usually yes), it goes in the shared core and works
fleet-wide from the first commit. Do not build it in one profile and hope.

## The failure this prevents (measured, not hypothetical)

Three real incidents, all the same bug:

| artifact | what happened |
|---|---|
| handoff-watcher.py | **4 copies, 2 designs, 4 md5s.** HQ ran one without noise control; workers ran one without detection |
| verification-preset-system.md | auditor pointed at a dead provider on all 4 seats; each needed hand-editing |
| skills generally | **272 files diverged across 4 profiles**; 24 of them are pure drift with no seat concept at all |

Each cost real time to discover and re-fix. None needed to happen.

## The pattern that works: ONE artifact, seat-aware config derived from context

Reference implementation — `handoff-watcher.py`:

```python
SEAT_LANES = {
    "gentech": [],                                 # HQ sees all lanes
    "gizmo": ["labs", "gizmo"],
    "pixel": ["entertainment", "pixel"],
    "gentech-treasury": ["treasury", "strategies", "gentech-treasury"],
}

def _seat_from_path():
    """Identity comes from where the file lives, not from a hardcoded constant."""
    parts = os.path.dirname(os.path.abspath(__file__)).split(os.sep)
    return parts[parts.index("profiles") + 1] if "profiles" in parts else "gentech"
```

One file, four seats, zero forks. Behaviour differs; the artifact does not.

**Cron has no script-args field** — you cannot pass `--seat` from the job. Deriving from
the path is the only mechanism that works fleet-wide without editing every cron entry.

## Checklist before shipping

- [ ] **No absolute profile path** hardcoded (`/root/.hermes/profiles/<one-seat>/…`)
- [ ] **No seat name as a constant** — derive it, or make it a config map keyed by seat
- [ ] **No credentials** in the artifact; read them from the profile `.env` at runtime
- [ ] **Silent when idle** — a fleet-wide job that prints on every run nags four seats at once
- [ ] **Declares its own degradation** rather than silently using a weaker path
- [ ] **Placed in the shared core**, not one profile's `skills/`
- [ ] **Verified on more than one seat** before calling it done

## Where the shared core is

```
/root/vaults/gentech/10-Labs/skills-distribution/     <- SHARED_CORE (source of truth)
/root/vaults/gentech/00-System/agent-profiles/fleet_skills_sync.py
```

```bash
python3 fleet_skills_sync.py --check    # report drift, change nothing
python3 fleet_skills_sync.py            # apply
```

Nightly propagation is `nightly-skills-sync.py` — silent on 0 changes, prints the DELTA.

## Editing rules

**Edit the shared core, never the profile copy.** A profile copy is a build artifact; the
next sync overwrites it. This is the same trap as the vault being the source of truth for
scripts — a per-profile edit gets silently reverted.

**If a skill is genuinely seat-specific**, say so in the skill itself (a `seats:` field or a
one-line note) so the next person does not "fix" the divergence by syncing it.

## Known-open debts (re-measured 2026-09-17, Council Overnight)

- **Pure drift: 0.** It was 6 (not 24 — four of that count were Hermes machine state, not
  skills). All six are unified in the core and byte-identical on all four seats. Triage:
  `00-HQ/skill-drift-triage-2026-09-17.md`.
- **52 pending sync changes across 21 skills** — visible only since the sync stopped
  comparing `SKILL.md` alone. **18 of the differing files are seat-aware**, so this is a
  review batch, not an apply batch. The sync now refuses an unattended run above 25 changes
  (`--max-changes`, exit 2) and `nightly-skills-sync.py` reports that as *"HELD, not broken"*.
- **278 files exist in only one profile** — some are legitimately seat-specific; the rest
  never got shared.
- **The detector:** `fleet_skill_drift_audit.py` (same dir as the sync). Sync answers "does
  the fleet match the core?"; the audit answers "are there files on every seat that should be
  identical and are not?" Run the audit before trusting a green `--check`.
