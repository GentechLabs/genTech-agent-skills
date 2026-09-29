# Automated git-sweep boundary: argv fall-through, allow-list ownership, and pathspec traps

Scope: any script that runs `git add` + `git commit` + `git push` on a schedule against a
multi-writer repository.

## The three failure classes

| Failure class | What it looks like | Why it happens |
|---|---|---|
| **argv fall-through** | `--help`, a typo, or a CI probe publishes an unexpected commit | `main()` has no argv dispatch; any invocation runs the full job |
| **deny-list leak** | A commit carries a ledger from another lane | `git add -A` stages everything; exclusions cover only known paths |
| **pathspec backfire** | Either the allow-list is ignored, or the sweeper silently stops | `git add -- . <globs>` unions `.` with the globs; a non-matching glob aborts the whole command |

## The argv guard

A production maintenance script is not a library. The top-level dispatch must be an allow-list:

```python
def _usage():
    print("Usage: nightly-maintenance.py [--dry-run | --selftest | -h | --help]", file=sys.stderr)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if not argv or set(argv) & {"-h", "--help"}:
        _usage()
        return 0
    if set(argv) == {"--selftest"}:
        return selftest()
    if set(argv) == {"--dry-run"}:
        return run_all(dry_run=True)
    # Anything else is an error BEFORE touching anything.
    print(f"REFUSING unknown argument(s): {argv}", file=sys.stderr)
    return os.EX_USAGE  # 64
```

Why `EX_USAGE`: it is the standard shell signal for "bad command line", and it prevents callers from
interpreting the exit as a successful empty run. The same return code is used by `git` and `grep` for
bad invocations.

Add `--dry-run` deliberately. If the only safe way to observe a script is to run it for real, users
will run it for real. `--dry-run` must print the `Would stage:` set and the `LEFT UNCOMMITTED` report
without reaching commit or push.

## Ownership allow-list

A deny-list is a promise that you have already thought of every place another agent can write. The
next ledger, the next lane, the next seat, the next refactor — all break that promise.

Build the list from evidence, not memory:

```bash
grep -n "open(.*['\"]w\|shutil.move\|subprocess.run\|subprocess.check_output\|subprocess.check_call" script.py
grep -n "\.write\|\.writelines" script.py
```

For each writer, note the directory or file. For helpers that write, follow them too. The resulting
`OWNED_GLOBS` should stage only those paths. Example shape:

```python
OWNED_GLOBS = (
    "01-HANDOFFS/**/_archive/**",
    "*/_archive/**",
    "nightly-report-*.md",
    "HQ/jordan-queue.md",
    "11-Mess Hall/privacy-sweeps/**",
    "scripts/build_queue.json",
)
```

Fail-closed: if the filtered live set is empty, the sweep commits nothing. Do not fall back to `.` or
to `git add -A`.

Reporting: list only the non-owned namespaces a reader would worry about (`11-Mess Hall/`,
`Treasury/`, money-path names) rather than dumping every uncommitted file, which becomes noise once
the allow-list is correct.

## Pathspec traps

**Trap 1: the leading `.` unions everything back in.**

```bash
# WRONG — this stages the whole repository regardless of the globs
git add -- . path1 path2

# RIGHT — the globs stand alone
git add -- path1 path2
```

Verify with `--dry-run`: a non-owned ledger must not appear in the `Would stage:` list.

**Trap 2: a non-matching glob aborts the whole command.**

```bash
$ git add -- 'nightly-report-*.md' 'no-such-glob/**'
fatal: pathspec 'no-such-glob/**' did not match any files
# nothing is staged, including the valid nightly-report file
```

Filter first:

```python
def _live_owned_globs():
    import fnmatch, subprocess
    tracked = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
    out = []
    for g in OWNED_GLOBS:
        if any(fnmatch.fnmatch(p, g) for p in tracked) or glob.glob(g, recursive=True):
            out.append(g)
        else:
            print(f"SKIP non-matching owned glob: {g}")
    return out
```

Then run `git add -- <live globs>`. Print dropped globs so a future change that accidentally
invalidates a glob is visible.

## Falsification recipe

A selftest that only runs the correct code proves the happy path. Mutate the script in a throwaway
copy and assert RED. Recommended cases:

| Mutation | Expected red result |
|---|---|
| Restore `git add -- . <globs>` | Non-owned ledger appears in staged set |
| Add `11-Mess Hall/fee-ledger.log` to `OWNED_GLOBS` | Ledger is staged |
| Replace `if _unknown:` with `if False:` | `script.py --nonsense` runs the job instead of exiting EX_USAGE |

After each red run, restore the correct script and re-run green. Automate this in the selftest so it
cannot rot.

## End-to-end proof on the real source of truth

Before committing the fix:

```bash
cd /root/vaults/gentech
python3 10-Labs/nightly-maintenance.py --dry-run
```

Inspect the output:
- `Would stage:` contains only owned paths
- `LEFT UNCOMMITTED` names the namespaces of concern, not every untracked file
- no ledger, no money-path file, no other-lane artifact appears under `Would stage:`

Only after this real-vault proof should the change be committed.

## Checklist

- [ ] `main()` validates argv before any write
- [ ] `--help` / `-h` print usage and touch nothing
- [ ] `--dry-run` prints the true stage set without committing
- [ ] Unknown argv exits `64` (`EX_USAGE`)
- [ ] Sweep uses an ownership allow-list, not a deny-list
- [ ] Allow-list is evidence-based from the script's own writers
- [ ] No leading `.` in the `git add` invocation
- [ ] Non-matching globs are filtered and reported, not passed to git
- [ ] Selftest red/greens each defect class
- [ ] `--dry-run` on the live vault shows zero unwanted staged paths
