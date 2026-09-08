# Diagnosing a dispatch that "succeeds" but writes no row

Symptom seen live at evolve-40: the arm logs `✓ action dispatched`,
`refresh-harness-state` runs, exit code 0 — and `grep -c '^## evolve-'
facts/execution-log.md` is unchanged. No error anywhere in the output.

## The technique: `bash -x` and read the trace, not the log

```bash
rm -f facts/.tmp/dispatched-evolve-N          # clear the sentinel first, or the lock refuses
bash -x scripts/execution-loop.sh evolve 2>&1 \
  | grep -nE '_append_execution_log|_verify_recommendation_metrics|_assert_cycle_trace|return|exit' \
  | tail -25
```

Read the LAST `return` before the trace ends. That is the function that bailed.
Then re-run and dump the raw trace around that line number:

```bash
rm -f facts/.tmp/dispatched-evolve-N
bash -x scripts/execution-loop.sh evolve 2>&1 | sed -n '560,640p'
```

The raw window is what actually solved it — the filtered view showed
`_verify_recommendation_metrics → return 1` but not WHY. The window showed:

```
++ operand=0
++ [[ >= == \>\= ]]
++ [[ 0 == \0 ]]
++ printf 'METRIC: … [UNFALSIFIABLE CRITERION >= 0 …'
```

…i.e. `op` was the real `>=` from the trailing threshold, but `operand` was `0`
scraped from the `>0` inside the awk program body. Whole-line parsing of a
declaration that embeds executable text.

## Two traps in this workflow

1. **`bash -x` pollutes command substitution output.** `out="$(eval "$expr")"`
   captures the trace lines too, so every metric reports `[non-numeric FAIL]`
   under `-x`. Those are ARTIFACTS — ignore them and read only the variable
   assignments (`++ operand=0`), never the `[FAIL]` verdicts, when tracing.
2. **The dispatch lock blocks your second trace run.** Every `bash -x` retry
   needs `rm -f facts/.tmp/dispatched-evolve-N` first, or you get
   `DISPATCH ALREADY RUNNING` and no trace at all.

## Silent-failure checklist (cheapest first)

| Symptom | Cause | Check |
|---|---|---|
| Dispatch logs fine, no row | `STALE PLAN HEADER` — plan names a different cycle than derived | `grep -c "Cycle evolve-$(( $(grep -oE '^## evolve-[0-9]+' facts/execution-log.md \| grep -oE '[0-9]+' \| sort -n \| tail -1) + 1 ))" facts/recommendation.md` == 1 |
| `0 RECOMMENDED_ACTION headers` | plan used `## RECOMMENDED_ACTION` markdown header | parser needs bare `^RECOMMENDED_ACTION:` — the `^#` rule makes awk `exit` |
| Row lands as `partial(metrics-failed)` | a threshold genuinely failed, OR operand mis-extraction | re-run each metric by hand from `$HARNESS_DIR` |
| `DISPATCH ALREADY RUNNING` | sentinel from a prior attempt | `rm -f facts/.tmp/dispatched-evolve-N` — only while still pre-dispatch |

## Verify without re-running the arm

Once a real dispatch has landed, further `evolve` runs are refused by design.
Source the loop and call functions directly:

```bash
source scripts/execution-loop.sh >/dev/null 2>&1
_reverify_published_metrics evolve-N
bash scripts/selftest-detail-metric-gate.sh 2>&1 | tail -3
```
