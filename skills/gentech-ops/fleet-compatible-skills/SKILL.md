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
- [ ] **Tests and guard scripts ship in the SAME deploy manifest as the artifact they verify** — a test with no sanctioned propagation path is a seat-only build artifact and will drift silently

## The gate (step (c) — a check that runs, not a convention)

The checklist above is a promise. These two tools are the enforcement:

```bash
cd /root/vaults/gentech/00-System/agent-profiles
python3 fleet_compat_scan.py    # exit 1 = a skill references another seat's filesystem
python3 fleet_compat_fix.py     # dry-run plan; --apply rewrites only what it can prove resolves
```

**Why a new tool was needed (measured 2026-09-17):** the drift audit compares seat to seat, so a
defect present in *every* copy reads as `identical` — healthy. It reported a clean fleet while
**731 references on the three worker seats told their reader to use HQ's filesystem**
(`/root/.hermes/profiles/<the-HQ-seat>/…`), 452 of them in executable context. Pixel's own copy of
`github-api-helper` inserted the HQ seat's `scripts` directory on `sys.path`; pixel's
`arc-cli-tooling.md` told the reader to run the HQ seat's `arc-canteen`. Add the scan to the pre-ship
check: if it names a seat that is not the reader's, it is not fleet-compatible, however many
copies agree.

The fixer refuses rather than guesses, and the refusals are the interesting part:
- a path that does not resolve on the reading seat (222 hits reference files that exist only on the
  HQ seat — substituting them would produce a path that resolves to nothing: a green light pointing
  at nothing);
- code files (`.py`/`.sh`) — `${PROFILE_DIR}` is not a variable there, so the substitution that
  fixes a `SKILL.md` would break a script;
- a seat copy whose skill also lives in the shared core, when the core copy would refuse the same
  substitution — a seat-only edit is a build artifact and the next sync replaces it;
- a line that names a second seat, or a file not already written portably.

Full finding: `00-HQ/fleet-compat-2026-09-17.md`.

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

## Lessons that cost a session each (measured 2026-09-26)

**1. A drift gate is a detector, not a cure.** It reached **0**, then read **3 eleven hours
later on the same day** — every one a seat that had *learned something* since the last pass.
Regrowth is the expected behaviour of a working fleet, so a green 0 is a **moment, not a
state**: re-run the audit, then **act** on it. Promoting the newer seat copy *into the core*
is the only edit that persists; a seat-only edit is reverted at the next sync.

**2. Measure direction per file before promoting — "superset" is a claim, not a fact.** A run
that had identified five residuals as strict supersets was wrong **twice**: one held genuine
halves (43 lines only on one seat, 54 only on the other) and another was a union. A blind
promote would have silently deleted live procedure. Diff **every** candidate, then merge.

**3. Never promote a skill as `SKILL.md` alone.** The sync's unit is the *directory*
(`rmtree` + `copytree`), so a core copy holding one file while a seat holds five will **delete
the other four, on a schedule, reported as a routine `updated`.** Copy the whole directory and
the union of its references.

**4. A size in a hygiene report is not a saving until the inode is checked.** Two overlapping
false positives in one run: a **symlinked directory** measured as its target (a "648 MB stale
artifact" was a 0-byte link to the *live* cache — `os.walk` descends symlinked dirs even when
`dirsize()` skips symlinked files), and a **hardlinked** toolchain counted as a duplicate copy
(**true reclaimable 0**). Group by inode, check `st_nlink`, and never recommend a delete from a
size alone.

**5. A test without a deploy manifest drifts exactly like the code it tests.** The canonical
`test-handoff-watcher-closure.py` was **6 checks behind** in gizmo's seat copy because the test
had no sanctioned propagation path while the watcher it validated was deployed fleet-wide. A
verification asset that lives in the same logical package as the artifact must share the same
deploy mechanism, or it will become stale and then the artifact can drift with a green suite.

- Tests are source-of-truth assets, not ad-hoc probes. Add them to the same fleet deploy script
  as the artifact they cover, and write a manifest that records which seats received them.
- A `--check` mode must be able to report seat drift by comparing the manifest digest against
  the live file — a green result is only evidence when the checker would have gone red if drifted.
- If the test is a file that cron executes, do **not** make it a symlink; cron refuses paths that
  resolve outside the profile's `scripts/` dir. Use a byte-identical copy inside `scripts/` and
  guard it against the canonical test in the core.
- Prove the drift checker can actually fail by injecting a controlled mutation (append one byte
  to a seat copy), running `--check`, confirming it reports the divergence, then restoring and
  re-confirming green. An unfalsifiable guard is worse than no guard.

**6. Fleet verification tools must be testable without touching production.** A guard that can
only be validated by mutating the live artifact risks leaving a real defect behind if the run
is interrupted between plant and restore. Test the guard against a scratch copy or a temporary
seat path, never against the canonical deployed file.

