# Retention purges that delete what records point at — and sole copies

Scope: any automated archive or retention sweep that deletes files based on age, especially when
a separate record layer can reference those files or when the files may be the last copy on disk.

## The hazard in two sentences

A sweep that deletes on age alone will eventually remove a file that something still depends on.
Two dependencies are independent and must both be checked: **records that point at the file**, and
**whether the file is the last remaining copy**.

## The two tests

| test | implementation | protects against |
|---|---|---|
| **Record target** | Build the set of filenames/paths referenced by live records (`_closed/`, index files, closure metadata) and withhold any match. | Dangling pointers: a record names a note that no longer exists anywhere. |
| **Sole copy** | Count **CONTENT** — `sha256` of every file across the whole tree — and withhold any digest whose count is 1. | Silent loss: a file that no record names, but which has no duplicate elsewhere. |

A file is **debris** only when it fails BOTH tests: nothing points at it, AND another copy exists.

**Compare DIGESTS, not basenames.** A dated aggregate REPEATS ITS NAME across lanes while the
documents share nothing — measured 2026-09-29: three copies of `2026-09-21-fleet-checkpoint-before-update.md`
in three lanes, two byte-identical (`88d6cf7b9f45`) and one unique (`2f7f1886e8ee`) — **and the unique
one is the one a basename test marks as a duplicate and deletes.** A name collision is not a copy.

**Fail toward HOLDING.** An unreadable file must read as *sole*. A false positive leaves a note
visibly held; a false negative destroys a last copy.

## The index is a SNAPSHOT; the purge is a SEQUENCE

A digest index built ONCE before the delete loop does not decrement as the loop deletes. With
exactly **two** copies of a content, both due, each reads "not sole" — **the guard whose whole
purpose is to keep the last copy deletes BOTH.** Measured on the live pair: remaining 0 as shipped,
1 with a one-line decrement. Decrement the count at every delete, or re-derive it at each test.

Corollary: **verify a loop guard by simulating the loop, never by reading the predicate at rest.**
A guard correct at one INSTANT can be wrong across a SEQUENCE.

## Where to place the guard

- Place the guard at the **purge** call (`os.remove`, `shutil.rmtree`, `git rm`), not at the
  **archive/move** call. Moving preserves content; deleting destroys it.
- If multiple scripts touch the same archive directory, every one of them needs the same guard.
  One guarded script and one unguarded script is the same as no guard.
- **A guard in one place and not its twin is not a guard, it is a habit.** Enumerate every
  destructive call in the file; the count of sites is the thing a fix never prints.

## What to print

A silent guard cannot be falsified. Print at least:

```
_archive PURGED >7d (3):
  path/one.md
  path/two.md
  path/three.md

_archive WITHHELD — a record names these, or they are sole copies (38):
  path/four.md   [record target]
  path/five.md   [sole copy]
  ...
  (NOT deleted — deleting one turns a record into a pointer to nothing, or loses the only copy)
```

## Fixture recipe

**NEVER run the destructive entry point to prove a guard.** Measured 2026-09-29: a "hermetic" test
sealed by replacing a path literal ran `--apply` against the real tree twice, moving 215 notes and
purging 3 — because the script set `VAULT_DIR = VAULT` and read `VAULT = os.environ.get("VAULT_ROOT", ...)`,
so the seal targeted **a string the code never reads**.

1. Build a throwaway tree:
   - `targeted.md` — referenced by a record in `_closed/`
   - `sole.md` — no record, only copy on disk
   - `pair-a.md` / `pair-b.md` — same content, no record, **both due** (the sequence case)
   - `debris.md` — no record, and a byte-identical second copy exists
2. **Seal via the constant the code actually reads**, then ASSERT IT FROM INSIDE THE SEALED PROCESS:

   ```python
   os.environ["VAULT_ROOT"] = tmpdir          # the name the script reads
   spec = importlib.util.spec_from_file_location("sweep", SWEEP)
   m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
   assert m.VAULT_DIR == tmpdir, "SEAL FAILED — this would have run against production"
   ```

   Without that assert the fake seal fails **quietly**, which is how a test becomes a production write.
3. **Import sealed and simulate the loop** — call the predicate and the decrement over the fixture in
   the tool's own order. Assert `targeted.md`, `sole.md` and `pair-b.md` are withheld and only
   `debris.md` is purged.
4. Remove the guard in a scratch copy and confirm the dangerous cases are no longer withheld.

## The pre-commit mutation trap

A sweep that deletes files and then commits later leaves the shared working tree mutated before
the explanation is in git. Any reader of the filesystem between those moments sees files gone and
has no commit to explain why.

- Delete and commit in the same transaction.
- `--dry-run` must not mutate the tree at all: no moves, no mtime updates, no temporary files.
- If the sweep must move files before purge, commit the moves too; do not leave deletes
  uncommitted while moves are committed.
- **A dry run that writes is not a dry run** — and it is worse than none, because a reader trusts it
  and therefore runs it freely. Audit every subprocess a "read-only" mode can reach: `ob sync`,
  `git pull`, a fleet sync, a repo push, a regenerated report. Measured 2026-09-29: an ungated
  `git -c rebase.autoStash=true pull --rebase` inside a maintenance job rewrote shared history twice
  in twenty minutes, triggered by the verifications meant to be safe.

## When a record points at a file that is already gone

If the guard discovers a record pointing at a missing file, do not silently ignore it. That is a
pre-existing defect: the pointer already dangles. Surface it in the report so it can be repaired
separately; otherwise the record stays as a false claim of closure.

## Checklist

- [ ] Every purge path in the codebase reaches both tests.
- [ ] Record targets are built from the live record tree, not a cached or hardcoded list.
- [ ] Sole-copy counts cover the whole tree, by DIGEST, not basename.
- [ ] The index is decremented (or re-derived) on each delete — the sequence case.
- [ ] The guard sits at `os.remove`, not at the archive/move.
- [ ] `--dry-run` prints both the purge set and the withheld set, with reasons.
- [ ] `--dry-run` provably writes nothing — tree hash and seat digests unchanged after a run.
- [ ] The fixture ASSERTS the resolved constant, so a bad seal fails loudly.
- [ ] The guard was proven by simulation, not by running the destructive entry point.
- [ ] Deletes and commits happen in the same transaction.
