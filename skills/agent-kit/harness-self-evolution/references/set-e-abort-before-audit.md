# `set -e` aborts that swallow the audit trail

Found at evolve-54 (2026-08-04) as the true root cause of five cycles of
"harness commits real code, writes no `## evolve-N` receipt". Four prior cycles
mis-attributed it to high-water counter placement and moved that write around
three times. This file is the reproduction recipe and the trap catalogue.

---

## The defect, minimally

```bash
#!/usr/bin/env bash
set -euo pipefail

verify() { return 1; }        # returns non-zero BY DESIGN when a check fails

run() {
    echo "✓ action dispatched"
    local out
    out="$(verify)"; local rc=$?   # ← function EXITS here. rc never read.
    echo "downgrade to partial"    # unreachable
    append_receipt                 # unreachable — the audit row is lost
}
run
echo "exit=$?"
```

Output is `✓ action dispatched` and nothing else. **No error message, and the
script's own exit status can still look clean** depending on how the caller
pipes it. The work already happened; only the record of it is gone.

## Why `; rc=$?` is a lie under `set -e`

`set -e` triggers on the **assignment statement** `out="$(verify)"` because the
command substitution exited non-zero. The shell leaves the function before the
`;` is ever reached. Authors read the `rc=$?` and believe the failure is
handled — it is the single most convincing-looking broken idiom in bash.

Correct forms, in order of preference:

```bash
out="$(verify)" || rc=$?          # best: preserves status, tolerated by set -e
out="$(verify)" || true           # when you only need the output
if ! out="$(verify)"; then ... fi # when you branch immediately
```

## Trap catalogue — every construct that can abort a `set -e` script

| Construct | Aborts? | Notes / fix |
|---|---|---|
| `x="$(cmd)"` | **yes** | `\|\| rc=$?` |
| `local x="$(cmd)"` | **no** | `local` masks the status — `$?` reads `local`, always 0. Split the declaration and the assignment onto separate lines when the status matters. |
| `((n++))` when `n==0` | **yes** | arithmetic result 0 → status 1. Use `n=$((n+1))` or `((n++)) \|\| true`. |
| `let n=0` | **yes** | same reason. |
| `grep -c 'x' f` with no match | **yes** | grep exits 1 on zero matches. Very common in metric code. |
| `cmd1 \| cmd2` | depends | with `pipefail`, any stage failing fails the pipe. |
| last command of a function | **yes** | its status becomes the function's status — and can abort the *caller*. |
| inside `if`/`&&`/`\|\|`/`!` | **no** | the whole point of the exemption. |

`grep` is the one to watch in any harness: **a legitimate count of zero is a
non-zero exit**, so metric and verification code is unusually prone to this.

## Diagnostic recipe

1. **Run it and note the last line printed.** A clean stop at a known-good log
   line, with no error text, is the signature. A silent early `return` looks
   the same from outside — distinguish them in step 2.
2. **Locate the next executable statement after that log line.** If it is an
   assignment, `local`, `let`, arithmetic, or a bare `grep -c`, suspect `set -e`.
3. **Confirm without editing the script:**
   ```bash
   bash -x scripts/execution-loop.sh evolve 2>&1 | tail -30
   ```
   The trace stops *on* the aborting statement. (Caution: `-x` output can
   pollute anything that captures stdout — never publish metrics from an
   `-x` run.)
4. **Prove the fix by differential run, not by reading.** Same tree, before and
   after:
   - before → `✓ action dispatched`, then nothing, no receipt row
   - after  → `⚠ declared metrics did not all pass — result downgraded to
     partial`, receipt row appended
   Assert the artifact, e.g. `grep -c '^## evolve-N' facts/execution-log.md` == 1.

## Structural rule

**A function that returns non-zero by design must never sit on the critical
path to an audit write.** Either append the receipt *before* calling it, or
guard every call site. A fail-closed verifier is correct; letting it kill the
record of the work it was verifying is not.

The general form: *the code that records what happened must be the code least
able to fail.* Put it first, or make every statement between the work and the
record abort-proof.

## Repo-specific pointers

- `scripts/execution-loop.sh:13` — `set -euo pipefail`
- `execute_action()` — the guarded assignment, ~line 707
- `_verify_recommendation_metrics()` — returns 1 on any failing/absent metric
- `_append_execution_log()` — the write that was being skipped; it also
  advances `facts/.cycle-highwater`, so an abort here freezes the cycle id too
  (which is why the symptom kept looking like a counter bug)
