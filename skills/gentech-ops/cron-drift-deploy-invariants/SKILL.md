---
name: cron-drift-deploy-invariants
category: devops
description: Use when deploying cron scripts or fixing asset drift.
---

# Shared-script deployment, drift guards, and public-asset truth

## Deployment of scripts that cron executes

1. Pick the deploy target by dependency, not by finding one copy: the target directory must contain the script's real sibling imports (tools it imports via relative ABI), because `os.path.abspath(__file__)` resolves through symlinks without following them — a symlinked deploy may still load the wrong siblings.
2. Deploy a byte-identical regular-file COPY into each profile's `scripts/` dir as the entry point, from one canonical in `10-Labs/tooling/`. Never deploy a symlink for a cron-invoked script: the Hermes scheduler resolves each job's script and refuses any job whose real path leaves the profile's scripts dir, so a vault symlink is a job that never starts.
3. After deploying, verify by execution, not by listing: run the check and confirm the live output (counts, empty missing lists).

See `references/drift-guard-classes.md` for the working set of drift-guard classes, cron entry-point rules, and asset-verification probes.

## Copy-drift guards (the tool that watches copies)

- Byte-identical script copies are NOT a complete deployment. A cron entry point also depends on its RUNTIME DATA (caches, state files, generated JSON) — and those are written somewhere else, so the copy the cron actually executes can be missing them while every script hash matches. A cron entry point that resolves a data file relative to `__file__` will silently fall back to its degraded path in exactly the copy production runs. Fix: search every enrolled location for the data and pick by FRESHNESS (timestamp), never by path order or first-found; then prove it on the copy the cron invokes, not the one you edited. Symptom to watch for: a fix verified from the vault appears to do nothing in production, with no error — the classic false-value signature.
- Define ONE canonical; entry points anywhere else count as drift only if their bytes differ from it, a real file or symlink to it both pass. "Copy the newest file over" is not a deployment — it moves the drift.
- Falsifiability is mandatory: a guard that cannot fail is a second defect class. To prove one, mutate the target to an obviously bad state, confirm the check fires, then restore and confirm clean. Record the proof (fired + restored) whenever a new assertion is added.
- Extend an existing check instead of adding a duplicating one; keep result rows machine-readable (count fields plus explicit missing lists) so verdicts render cleanly.

## Public pages: asset truth

- Verify assets the way a logged-out visitor sees them: probe anonymously with a browser UA. Authenticated success (200 with a token) does NOT prove public reachability — the auth/anon split is the decisive test for visibility classes (dead assets, private repos, invisible issues).
- Scan served HTML for off-host and hard-coded raw-URL dependencies and probe own-domain assets as an anonymous browser; add such a check BEFORE shipping a repoint, because it typically finds more instances of the same defect than the report mentions.
- When substituting a replaced host or path (repointing, choosing a logo/contact), probe each candidate and take the first that answers 200 from the live tree — never trust a stored/previous value on the grounds that it used to work.
- Caveat on quick greps: a substring match like "gentechlabs.net/v1" also matches "api.gentechlabs.net/v1"; validate with an anchored check before reporting counts.
- Before repointing any served JSON, validate it parses first; a file can be served AND committed with unresolved merge-conflict markers, which makes it unparseable no matter where it is served from. Sweep the repo for further marker instances once one is found.

## Fixing a guardian tool from inside itself

- When the drift monitor flags a deployment, first check whether the flagged copy differs at all — byte-identical strays are still worth collapsing, but the FIX differs from a stale copy's fix (delete vs overwrite).
- If an installed fix changes how cron jobs execute (scripts, symlinks, paths), run the cron-script-path check immediately after; a fix may break its own scheduler entry.