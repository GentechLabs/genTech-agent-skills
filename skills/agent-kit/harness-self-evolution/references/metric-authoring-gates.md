# Metric-Authoring Gates — the full guard stack (evolve-67)

The harness's `_verify_recommendation_metrics` in `scripts/execution-loop.sh` has accumulated a
stack of authoring-time gates that reject bad declared metrics BEFORE they can publish a false
value. Each was added to close a distinct recurrence of metric mis-authoring. Order matters.

## The guard stack (in execution order)

1. **UNPARSEABLE-METRIC GATE** (`_reject_unparseable_metric`, evolve-67) — rejects any declared
   metric line whose backtick content is non-empty and does NOT start with `grep|awk|wc`. The
   extractor regex `grep -oP '(?<=`)(grep|awk|wc)[^`]*(?=`)'` only parses grep/awk/wc-prefixed
   forms, so a `bash ... 2>&1 | grep -c '^PASS: '` pipeline is counted as DECLARED by
   `_count_declared_metrics` (which counts every `- ` line) but silently dropped by the loop
   (`[[ -n "$expr" ]] || continue`), forcing a false COVERAGE SHORTFALL bandaged in-cycle.
2. **NONE-DECLARED early-return** (evolve-34) — FAIL CLOSED when the plan block matched no
   `grep|awk|wc` expression.
3. **UNFALSIFIABLE CRITERION** (evolve-41) — `>= 0` on a counter, or any negative operand, can
   never fail; reject.
4. **SELF-MATCHING CRITERION** (evolve-43/52) — an unscoped grep of the file the criterion is
   written into measures itself; awk-range-scoped forms are allowed.
5. **RECEIPT-EXISTS SELF-CHECK** (evolve-62) — a grep for the current cycle's own header
   `^## ${CYCLE_ID}` against execution-log.md measures whether the receipt was written.
6. **SELF-ADVANCING-STATE METRIC** (evolve-66) — greps a ledger the dispatch writes
   (execution-log.md / harness-state.md) for a literal the dispatch advances (`- Result:`,
   `PLAN MUTATED`, or the current CYCLE_ID). Passes pre-dispatch (state points at PREVIOUS
   cycle) then always drifts post-dispatch.
7. **PHANTOM-LITERAL METRIC** (`_reject_phantom_literal_metric`, evolve-70) — SEMANTIC gate.
   A grep of a literal the target never emits is syntactically valid (grep-prefixed) but
   semantically wrong: the literal never matches, the receipt downgrades to
   partial(metrics-failed), and the cycle bandages with PLAN MUTATED. This was the 7th
   consecutive metric-authoring miss (evolve-61/63/64/65/66/68/69) — the syntax gate could not
   catch it. Rejects iff: the metric is a `grep` form AND the literal is ABSENT from the
   target file AND the target is NOT named in the action's DETAIL as a file the action will
   modify. The "target in DETAIL modify list" guard is the discriminator — without it the
   gate false-positives on every legitimate forward-looking grep (e.g. `grep -c
   'isinstance(raw, list)'` on a script the action edits). Wired into `_pre_dispatch_metric_gate`
   so it aborts the evolve arm BEFORE `execute_action` (return 2, log `PHANTOM LITERAL METRIC —
   aborting before dispatch`).

## CRITICAL ordering pitfall (evolve-67)

The UNPARSEABLE scan MUST run BEFORE the NONE-DECLARED early-return. If it runs after, a plan
whose ONLY declared metric is a bash-pipeline form hits the `[[ ${#lines[@]} -eq 0 ]]` check
first (the bash line isn't grep|awk|wc-prefixed, so `lines` is empty) and is misreported as
`NONE DECLARED` instead of `UNPARSEABLE`. The selftest case `z` fixture A catches this exact
regression.

## Selftest cases

- `assert_y_self_advancing_state_metric_fires` (evolve-66) — proves the SELF-ADVANCING gate
  fires on the exact degenerate forms and that a stable script-grep metric passes.
- `assert_z_unparseable_metric_fires` (evolve-67) — proves the UNPARSEABLE gate fires on the
  exact `bash ... | grep -c` form and that a grep-prefixed metric passes.
- `assert_ab_phantom_literal_metric_fires` (evolve-70) — proves the PHANTOM-LITERAL gate fires
  on a grep of an absent literal (rc=2 abort) and that a forward-looking grep of a file the
  action WILL modify passes (rc=0).

## PITFALL — proving a literal is ABSENT from a file (evolve-70)

When writing a selftest case that asserts a phantom-literal metric is rejected, the "absent
literal" must be **built at runtime**, never written literally into the selftest file. If the
literal appears in the selftest's own comment or heredoc, `grep -qF` finds it and the test
cannot prove absence — the gate silently passes and the case FAILs.

```bash
# WRONG — literal appears in the file's comment/heredoc, grep finds it:
#   - `grep -c 'q7x2m9v4p1' scripts/selftest-detail-metric-gate.sh` >= 1

# RIGHT — literal built at runtime so it never appears literally in the file:
local _phantom="q7x2m9v4p1_$(date +%s)"
cat > "$TMP/plan-ab1.md" <<EOF
RECOMMENDED_ACTION: update_script
DETAIL: (A) add a new helper to scripts/execution-loop.sh. No selftest change.
## Measurable improvement expected
- \`grep -c '$_phantom' scripts/selftest-detail-metric-gate.sh\` >= 1
## Next section
EOF
```

Also: when the gate's own comment text names the example literal (e.g. "rejects `grep -c
'ALL ASSERTIONS HOLD'`"), that literal is now IN the file — so a fixture using the same
literal will not be "absent". Use a distinct runtime-built token for the fixture.

## Metric count discipline (evolve-70)

Declare the metric threshold to match the ACTUAL reference count, not an aspirational one.
`grep -c '_reject_phantom_literal_metric'` returned 2 (def + wire), not 3 — the recommendation
and prediction had to be corrected from `>= 3` to `>= 2` before the cycle would pass clean.
Count real references (def + call sites), not "def + wire + comment".

## The correct metric form

Declared metrics must be stable, grep|awk|wc-prefixed greps of `scripts/` (or awk-range-scoped
greps of a PREVIOUS cycle's row for a stable artifact). Example that always passes:
`grep -c 'assert_z_unparseable_metric_fires' scripts/selftest-detail-metric-gate.sh` >= 1.
Never declare a `bash ... | grep -c` pipeline — the extractor cannot parse it.
