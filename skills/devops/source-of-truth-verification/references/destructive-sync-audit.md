# Auditing Destructive Syncs and Seat-Only Files

**What this is:** how to tell whether a sync tool that applies a blind replace actually destroyed data, whether the alarm points at the right path, and whether the instrument's counts are meaningful.

## Two paths, not one

A sync tool can describe three behaviours that are really two different code paths:

1. **Normal per-skill replace** — warns, then `shutil.rmtree(dest)` + `shutil.copytree(src, dest)`. This DESTROYS anything present only in the destination.
2. **Shadow/namespace block** — detects that a destination directory is a strict superset of a registered namespace and BLOCKS the apply, exiting with a warning.

A bug report that conflates them will be aimed at the wrong target. Read the function that handles the directory in question before interpreting a `would-update` count or a `BLOCKED` message.

## Survivors are the falsification

A replace path cannot leave seat-only files behind: after `rmtree` + `copytree`, the destination contains exactly the source's list. If files that should have been destroyed are still present — and their mtimes predate the sync window — the destructive path did not execute there.

To use this control:
- Count substantive seat-only files in the destination tree, not metadata like `.skill_id`.
- Check their mtimes against the last sync run.
- Confirm they are inside the directory the tool labels as at risk.

A survivor does not prove the tool is safe everywhere; it proves the alarm is false for that directory.

## Counts that do not move

If you remove a seat-only file and the tool's `seat-only` count stays the same, the instrument is measuring something other than `present only`. Common cause: the count includes files that DIFFER from the source as well as files absent from it, so removing an absence leaves a difference behind.

Fix: make the tool print the names of the files it counts, not just the number. A count without a list cannot be debugged, and a count that does not move when the set moves is the instrument, not the population.

## Promote, do not leave in the destruction path

A seat-only file inside a registered skill directory is not a durable home. Promote it to the core distribution (`10-Labs/skills-distribution/<cat>/<skill>/`) byte-identically, then sync. The promotion itself should reduce the seat-only set; if the count does not move, see `Counts that do not move` above.