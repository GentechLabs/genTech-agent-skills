# Harness Evolution — evolve-77 session notes (2026-08-08)

Durable operational lessons from running the evolve-77 facts-cleanup cycle.
These are class-level pitfalls, not one-off narratives.

## 1. The loop lives at `scripts/execution-loop.sh`, not the harness root

`cd ${HERMES_HOME}/harness && bash execution-loop.sh evolve` fails with
`bash: execution-loop.sh: No such file or directory`. The correct invocation is:

```bash
cd ${HERMES_HOME}/harness && bash scripts/execution-loop.sh evolve 2>&1 | tail -30
```

## 2. `read-external-feedback` Action-parser defect (CRITICAL — blocks ALL dispatch)

`read-external-feedback` (scripts/execution-loop.sh:326) took the FIRST token
after `action:` as the status word. The Critic's Action line format varies:

- `- Action: ADDRESSED (evolve-N)`  → first token is `ADDRESSED` ✓
- `- Action: evolve-N critical ADDRESSED (evolve-M)` → first token is `evolve-N` ✗

The second form made the gate read an already-addressed critique as
*unaddressed* and abort every evolve cycle with `ABORTED: WATCH high unaddressed`.

**Fix (applied evolve-77):** normalize after parsing — if the last critique
entry's Action line contains `ADDRESSED` anywhere, force `last_action=ADDRESSED`:

```bash
last_action=$(printf '%s' "$_last_entry" | grep -oiE '^(- )?action: *[A-Za-z0-9_-]+' | tail -1 | awk '{print $NF}')
if printf '%s' "$_last_entry" | grep -qiE '^(- )?action:.*ADDRESSED'; then
    last_action="ADDRESSED"
fi
```

**Symptom to watch for:** the loop logs
`external feedback: verdict=WATCH severity=high action=evolve-75` (a cycle id,
not a status word) and then `ABORTED: ... unaddressed`. If `action=` is a
cycle id like `evolve-N` instead of `ADDRESSED`/`NONE`, the parser is
misreading the Action line.

## 3. A stale dispatch sentinel survives an aborted run

When the loop aborts at the feedback gate (BEFORE `execute_action`), it still
leaves `facts/.dispatch-sentinels/dispatched-evolve-N` behind. The next run
then fails with `✗ DISPATCH ALREADY RUNNING — a dispatch sentinel
(dispatched-evolve-N) is newer than the 10800s cron floor`.

**Fix:** confirm no execution-log row was written for that cycle, then remove
the stale sentinel and re-run:

```bash
rm -f facts/.dispatch-sentinels/dispatched-evolve-N
```

## 4. The `facts-cleanup` arm is a bookkeeping stub — it does NOT run DETAIL

The loop's `facts-cleanup` arm only updates state files (harness-state.md,
dispatch-state). It does NOT execute the DETAIL items in the plan. The agent
must execute the real work (commits, log appends, ledger edits) manually
AFTER the loop writes the row, then correct the receipt.

**Consequence:** the loop stamps `- result: partial(metrics-failed)` because it
evaluates the declared metrics BEFORE the agent has done the work. After
executing the work, re-verify each metric and correct the execution-log row
from `partial(metrics-failed)` to `ok`, and fix harness-state.md's
`- Result:` line to match (the stale-state false-FAIL defect the harness has
fought repeatedly). Document the manual execution with a
`<!-- NOTE evolve-N ... -->` marker in the execution log.

## 5. Metric authoring — avoid self-matching and unparseable forms

- **Self-matching criterion:** a metric that greps the file the criterion is
  written into (e.g. `grep -c 'defer' facts/prediction-outcomes.md` when the
  deferral note is appended to that same file) measures itself and is flagged
  `SELF-MATCHING CRITERION`. Scope with awk range addressing or grep a
  different artifact.
- **Process-substitution form:** `grep -c 'X' <(git status --porcelain)` is
  not parseable by the metric extractor (which only matches
  `(?<=`)(grep|awk|wc)`). Use a plain `git status --porcelain | grep -c 'X'`
  form or a wc form.
- **Verify metrics AFTER doing the work**, not before — the loop evaluates
  them at dispatch time, before the agent's manual execution.

## 6. Prediction-outcome grading must respect the due-epoch rule

Do NOT fabricate outcomes for predictions that are not yet past-due. The
earliest-due prediction gates the whole batch. If none are past-due, append a
dated deferral note to facts/prediction-outcomes.md documenting the decision
and let the Verifier (0 */6 * * *) adjudicate at each due time.
