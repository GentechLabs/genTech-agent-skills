# Metric and loop pitfalls — full detail

Extracted from `harness-self-evolution/SKILL.md` on 2026-09-26 because the skill had reached
99,997 chars against a 100,000-char limit — within three characters of becoming UNEDITABLE
(every `skill_manage` write is rejected past the limit). No content was deleted; the detailed
per-evolve write-ups moved here and the SKILL.md keeps the rules they taught.

These are the *why* and the reproduction steps behind the condensed rules in the skill.

---

### evolve-34: the gate now FAILS CLOSED — and the whitelist silently drops non-grep metrics
`:282` was replaced (evolve-34) with a fail-closed branch: an empty metric set now prints
`METRIC: NONE DECLARED — plan block matched no `grep|awk|wc` expression [FAIL]` and returns 1,
so "no metrics ran" downgrades the row to `partial(metrics-failed)` instead of reading `ok`.
A `PLAN MISSING DETAIL` guard was added after the `action_type` parse for the same reason.
Both are proven by `scripts/selftest-detail-metric-gate.sh` (4 asserted cases, rc=0).

**Residual hole — declare metrics ONLY as `grep`/`awk`/`wc`.** The selector whitelist is
literally `(grep|awk|wc)`; a metric written as `` `bash scripts/selftest-foo.sh` == 0 `` matches
nothing and is *silently skipped* (the `continue` on an empty `expr`), so a 4-metric plan lands
3 `[PASS]` tokens with no complaint. Dropping a metric is a smaller sibling of the fail-open
family. Until the whitelist is widened, express script-based checks in whitelisted form, e.g.
`` `bash scripts/x.sh >/dev/null 2>&1; echo $?` `` will NOT parse — instead assert on an artifact
the script produces, or run the script yourself and report the divergence in the cycle report.

### evolve-36: COVERAGE is now enforced IN THE LOOP — and how to count it correctly
Because skipped metrics are silent, "every metric in the row passed" is NOT the same claim as
"every declared metric ran". As of evolve-36 `_verify_recommendation_metrics` enforces parity
itself: it counts `^- ` lines in the `## Measurable improvement expected` block as *declared*,
increments an `executed` counter **inside the emit loop**, and on `executed < declared` prints
`METRIC: COVERAGE SHORTFALL <n>/<m> [FAIL]` + `rc=1`, downgrading the row to
`partial(metrics-failed)`. Proven by `scripts/selftest-detail-metric-gate.sh` (6 asserted cases:
`assert_e` = 3 declared / 1 parseable → shortfall fires rc=1; `assert_f` = 2/2 → rc=0).

**Two counting rules that are load-bearing — both were violated by the cycles that shipped them:**

1. **Count executed metrics AT THE EMITTER, never by re-grepping the log.** The log will contain
   this very row's detail prose, which quotes the metric strings, inflating the count. evolve-35's
   parity falsifier used `grep -o 'METRIC:' | wc -l` and read **5** against 4 real results because
   the detail contains the `; METRIC:` chain. If you must count from the log post-hoc, use a
   prose-immune pattern matching only emitted result lines:
   `awk '/^## evolve-N/,0' facts/execution-log.md | grep -oE 'METRIC: [^|;]+ -> ' | wc -l`
2. **Any declared metric whose pattern can appear in its own row's detail must be `>= 1`, or
   `awk`-scoped to the target row.** A metric declared `== 1` that the gate evaluates *before*
   `_append_execution_log` runs will PASS at gate time and FAIL for the user re-running it one
   second later, because the append created a second occurrence. This is the self-referential-count
   class biting at row level rather than prediction level.

**MANDATORY: re-run every declared metric AFTER dispatch and report the results in the cycle
report.** A metric that passes only before its own row exists is not a metric. This is the single
most-repeated Critic finding across evolve-33..36 — the work was real every time; the instruments
measuring it were not re-run.

**Meta-lesson: a Critic counter-recommendation can be wrong in its specifics.** The
evolve-32 critique instructed "prefix each metric with `METRIC:`"; followed literally
that produces zero parsed metrics. Execute the counter-recommendation's *intent*,
verify the mechanism against the actual parser, and report the divergence in your
cycle report rather than silently complying or silently deviating.

### evolve-37: a counter that matches BOTH a definition and its call site double-counts
`grep -c '^assert_' scripts/selftest-detail-metric-gate.sh` published **12** for a selftest
that runs **6** assertions — the pattern matched 6 function definitions (`assert_a() {`) AND
6 invocations (`assert_a`). The file's own runner printed `ALL 6 ASSERTIONS HOLD` on the same
line of output. Worse, two thresholds had already been *calibrated to the broken counter*
(evolve-34 shipped `>= 4` against 8, evolve-36 `>= 10` against 12), so the lie propagated into
the pass criteria of later cycles.

**Rule: count the RUNTIME ARTIFACT, never the source text.** A test's emitted output has exactly
one line per executed assertion; its source has two mentions per assertion.
`bash scripts/selftest-X.sh 2>&1 | grep -cE '^PASS: '` cannot double-count.
FORBIDDEN in any metric or falsifier: a pattern that can match both a function definition and an
invocation of that same function. Before publishing any count, sanity-check it against a second
independent statement of the same quantity (here, the runner's own summary line) — if two numbers
for one quantity differ by a factor of two, the counter is wrong, not the code.

### evolve-37: the metric block needs a terminator and no blank lines (two rival counters)
Two different counters for "how many metrics did the plan declare" are live in the tree and they
are NOT the same expression:
- the gate, `execution-loop.sh:294`: `sed -n '/^## Measurable improvement expected/,/^## /p' | grep -cE '^- '` — terminates on the next `## ` header
- the predictions' parity falsifiers: `awk '/Measurable improvement expected/,/^$/' | grep -c '^-'` — terminates on the first BLANK LINE

They agree only when the metric block contains no blank line AND is followed by a `## ` header —
neither property was enforced. A blank-line-separated block makes awk undercount, so the same row
grades PASS by the gate and FALSIFIED by the prediction. An EOF-terminated block makes the sed
range never close, so every trailing `- ` bullet in the file inflates `declared`.

Therefore, when writing `facts/recommendation.md`:
- ALWAYS follow the metric block with a `## ` header (add a throwaway `## Block terminator` if the block would otherwise end the file).
- NEVER put a blank line between `- ` metric bullets.
- Pre-flight both counters and confirm they agree before dispatching:
  `sed -n '/^## Measurable improvement expected/,/^## /p' facts/recommendation.md | grep -cE '^- '`
  and `awk '/Measurable improvement expected/,/^$/' facts/recommendation.md | grep -c '^-'`.
These clauses are now written into the `== Metric block contract ==` section of `prompts/evolution.md`.

### evolve-38: the two rival counters are now ONE — `_count_declared_metrics()`
The sed/awk split above is CLOSED. `scripts/execution-loop.sh` now defines a single
`_count_declared_metrics()` (awk, block starts at `## Measurable improvement expected`,
terminated on the next `^## ` **and** by an explicit EOF guard — the `END { print n+0 }`
rule fires unconditionally), and the gate calls it. Predictions grading declared-vs-executed
coverage MUST call/quote that same expression rather than inventing a second one.
`scripts/selftest-detail-metric-gate.sh` assertion **(g)** proves fn-path and awk-path agree
(=2) on a block containing a blank line between bullets. Keep writing blocks with no blank
lines and a trailing `## ` header anyway — that is the contract the counter is asserted against.
Regression guard: any future cycle that reintroduces an independent declared-metric counter
instead of calling `_count_declared_metrics` is a falsifier hit (PREDICTION #37 f7).

### The plan file must contain the dispatch tokens EXACTLY ONCE — including inside prose
`execution-loop.sh` refuses to dispatch with
`✗ recommendation.md carries 2 RECOMMENDED_ACTION headers — refusing to dispatch a possibly
stale plan`. This fires on **any** occurrence of the token, including one buried in your own
`DETAIL:` narrative (seen live at evolve-38: the DETAIL described rewriting a state file's
`RECOMMENDED_ACTION: facts-cleanup` field and tripped the guard). When a plan's prose needs to
refer to a dispatch field, write it as *action type* `` `facts-cleanup` `` — never as the bare
`FIELD:` token. Pre-flight: `grep -c 'RECOMMENDED_ACTION' facts/recommendation.md` == 1
(count the token, not just `^RECOMMENDED_ACTION:`).

### evolve-39: post-dispatch re-verification is now IN THE LOOP (`_reverify_published_metrics`)
The "re-run every declared metric AFTER dispatch" rule below is no longer manual.
`scripts/execution-loop.sh` defines `_reverify_published_metrics <cycle> [log]`, wired as the
**last statement of the evolve arm** — after `refresh-next-events.sh` and
`refresh-harness-state.sh`. It parses `METRIC: <expr> -> <value> [<tag>]` triples out of the
current cycle's `- detail:` row, re-runs each expr from `$HARNESS_DIR`, and compares.

**Design rule that makes it usable — judge the CRITERION, not the value.** The naive version
(fail on any value change) fired a false positive on its very first live run: the measured file
was `facts/execution-log.md` itself, which grew because the row containing the measured phrase
was appended to it. So:
- live value differs but the published `[PASS >= N]` criterion **still holds** → emit
  `<!-- METRIC SHIFT … criterion >= N still holds -->`, `log_warn`, **rc unchanged**.
- criterion **broken**, or no comparison was declared → emit `<!-- METRIC DRIFT … -->`,
  `log_error`, **rc=1** (the cycle fails; the receipt is unreproducible).
Reuse `_metric_compare` for the arithmetic — do not write a second comparator (same
one-counter rule as `_count_declared_metrics`).
Asserted by `scripts/selftest-detail-metric-gate.sh` case **(h)**: published 2, criterion `>= 2`,
post-dispatch value 0 → rc!=0 + drift comment. Runner now prints `ALL 8 ASSERTIONS HOLD`.
Full implementation, parser traps, and the SHIFT-vs-DRIFT rationale:
`references/post-dispatch-reverification.md`.

**Corollary for authoring metrics:** any metric whose pattern can appear in its own audit row
MUST be declared `>= N`, never `== N`. With `==`, the row's own text moves the count and the
new gate correctly fails the cycle.

### evolve-51: the in-loop re-verifier CANNOT see writes made after the loop exits
`_reverify_published_metrics` is the last statement of the evolve arm, so it only observes
writes made **inside that process**. When you (the agent) edit `facts/predictions.md` or any
measured file *after* `bash scripts/execution-loop.sh evolve` returns — which is the normal
shape of a hand-executed cycle — the gate is structurally blind. That is how evolve-42
published `grep -c '!= 6' facts/predictions.md -> 0 [PASS == 0]` against a live value of **2**
with no `METRIC DRIFT` annotation. The function was never broken: re-running it by hand on the
same row emitted DRIFT and returned 1.

**Diagnose before you "fix".** The obvious remedy (move the call later in the arm) changes
nothing — it was already last. Source the function and run it against the suspect row first:
```bash
source <(awk '/^_metric_compare\(\)/,/^}/' scripts/execution-loop.sh)
source <(awk '/^_reverify_published_metrics\(\)/,/^}/' scripts/execution-loop.sh)
_reverify_published_metrics evolve-N /tmp/copy-of-log.md; echo "rc=$?"
```
If it fires by hand but not in the run, the bug is REACHABILITY, not logic.
Packaged as `scripts/reverify-row-probe.sh` in this skill — run
`bash scripts/reverify-row-probe.sh evolve-N [harness_dir]`; it works on a COPY of the ledger
so it can never annotate the real one.

**Fix shape: re-verify at the CYCLE BOUNDARY, where every write from the prior cycle has
landed regardless of which process made it.** `_reverify_prior_cycle` runs at the start of the
evolve arm against the last `^## evolve-N` row, annotating but never aborting (the prior cycle
is already shipped; aborting deadlocks the harness). Plus a standalone
`bash scripts/execution-loop.sh reverify [evolve-N]` arm for manual checks. Make the drift
annotation **idempotent** (skip if a `METRIC DRIFT <cycle>` line already names that expr),
otherwise the boundary check accretes one duplicate comment per cycle forever.

**Generalised rule: a self-check that only runs inside one process cannot police artefacts
that other processes write. Put the check at the boundary the artefact must cross.**

### evolve-51: the self-matching-criterion ban now lives in the PARSER, not in prose
Four consecutive recurrences (#34 f3, #36 f3/f4, #37 f4) of "criterion greps the file it is
written into, so writing it changes its own value" proved prose rules do not hold. The gate now
emits `SELF-MATCHING CRITERION` + `rc=1` for an unscoped `grep` whose target is
`facts/predictions.md`. `awk '/range/,/range/' … | grep …` forms are artefact-scoped and pass.

> ⚠️ **SUPERSEDED (evolve-52) — the "scope such a clause narrowly" advice below was WRONG
> and directly caused the FIFTH recurrence.** evolve-51 hard-coded the gate to the single
> filename `facts/predictions.md`, and in the very same receipt published a criterion of
> exactly the banned form against a *different* ledger
> (`grep -c '<phrase>' facts/execution-log.md`), whose value then climbed 1 → 2 → 3 because
> each annotation of it re-emitted the literal it counts. **Fix the CLASS, not the instance.**
> The gate is now scoped to every ledger the loop writes:
> ```bash
> _self_target="$(printf '%s' "$expr" \
>   | grep -oE 'facts/(predictions|execution-log|critique-log|harness-state|prediction-outcomes)\.md' | head -1)"
> ```
> The feared false-positive never materialised: the guard only fires on an **unscoped `grep`**,
> so anchored counts like `grep -c '^## evolve-41' facts/execution-log.md` still trip it and
> must be written awk-scoped — which is correct, because an anchored count of a growing ledger
> is still measuring the file the receipt lands in. The `awk '/range/,/range/' … | grep` escape
> hatch covers every legitimate case. Asserted by selftest case **(o)**; runner now prints
> `ALL 10 ASSERTIONS HOLD`.
>
> **Generalised rule, now five recurrences deep (#34 f3, #36 f3/f4, #42 f4, evolve-51 metric 5):
> when a defect class has been "fixed" 3+ times and keeps reappearing one filename / one field /
> one call-site over, the fix was scoped to the instance. Widen the guard to the set of artefacts
> that share the property, and add a selftest case that reproduces the NEW location, not the old
> one.** Fear of a hypothetical false positive is not a reason to under-scope a guard that has
> already failed five times — ship the wide version and let a real false positive, if one ever
> appears, narrow it with evidence.

Also: when rewording an Article V amendment note, the note itself
must not contain the literal it describes — that note was one of the two live matches that
made the evolve-42 receipt false. Corollary for **voiding** an already-published self-matching
metric: append an Article V `VOID self-matching` note to the offending row explaining that the
metric counted the act of reporting rather than the fix, restate the claim artefact-scoped, and
**do not write the counted literal anywhere in the correction** — otherwise the correction
inflates the very number it retracts.

### evolve-51: `.cycle-highwater` advances on ATTEMPT, so aborted pre-flights burn cycle ids

> ✅ **FIXED (evolve-52), then RE-FIXED (evolve-53) — the evolve-52 placement was itself
> the leak.** The high-water write originally ran unconditionally in the *derivation*
> block, so every `source`, selftest and aborted pre-flight burned an id — **53 issued
> for 23 real receipts**. evolve-52 moved it to the top of `_record_dispatch()` — but
> `_record_dispatch` records the *arm*, and in that very commit the evolve-52 dispatch
> advanced the high-water to 52 while writing **no `## evolve-52` row** (the ledger gap
> the Critic immediately caught). `_record_dispatch` runs on a dispatch *attempt*, which
> is still not the same as an actual row append. **The durable fix (evolve-53, Critic
> evolve-52 item A): an id is spent iff a ledger row is written.** The high-water write
> lives in `_append_execution_log`, executed only AFTER the `## <cycle>` block is appended
> AND verified present:
> ```bash
> # in _append_execution_log, after the append block:
> if grep -q "^## ${cycle} — " "$EXECUTION_LOG"; then   # row verified, THEN burn id
>     printf '%s\n' "$_hw_n" > "$_hw_file"
> fi
> ```
> `_record_dispatch()` must NOT touch the high-water — it only records the arm into
> `facts/.dispatch-state`. Verify the relocation held:
> `grep -A10 '_record_dispatch()' scripts/execution-loop.sh | grep -c 'cycle-highwater'` == 0
> AND `grep -c 'cycle-highwater' scripts/execution-loop.sh` >= 2 (the read + the
> append-site write). Selftest case **(p)** asserts both halves: `_record_dispatch` alone
> must NOT advance the counter; `_append_execution_log` after a real append MUST. Runner
> prints `ALL 11 ASSERTIONS HOLD`.
> The `LEDGER GAP` **read** at derivation time is untouched — that is the whole point of the
> two-ledger design (one advanced at issue, one appended only on real completion; their disagreement is the signal).
>
> **Generalised rule: a counter that certifies work must be incremented by the code path that
> performs the work — and 'records the arm' is not 'performs the work'. It must be the code
> path that actually appends the receipt row, gated on a verified append.** This is the mirror
> of the evolve-42 rule (a no-work path must not increment the work counter) and the two belong
> together. Note the *diagnosis* Evolution itself wrote at evolve-51 named this exact fix and
> then didn't do it, burning two further ids within minutes of writing the note — **when you
> document a one-line fix in a receipt, do it in that same cycle or it becomes the next
> critique.**

Historical behaviour (pre-evolve-52): the high-water mark was written at derivation, before
any gate ran. Three aborted
pre-dispatch attempts in one session (`PLAN MISSING DETAIL` → `NONE DECLARED` →
`STALE PLAN HEADER`) each consumed an id, so a cycle authored as `evolve-43` dispatched as
`evolve-51` with 43–50 empty. Nothing is lost, but the Critic will read an 8-cycle gap.

- **Pre-flight the plan file COMPLETELY before the first invocation** (see
  `references/plan-file-contract.md`): `^DETAIL:` == 1, `^RECOMMENDED_ACTION:` == 1 token,
  `Cycle evolve-N` present, and the metric block parses — verify the last one by sourcing
  `_verify_recommendation_metrics` and running it directly rather than by launching the arm.
- **The metric block heading is load-bearing**: metrics under a `## Verify` heading are
  invisible. They must sit under `## Measurable improvement expected`, as backticked
  `grep|awk|wc` expressions with a trailing comparison, followed by a `## ` terminator.
- Each retry needs `rm -f facts/.dispatch-sentinels/dispatched-evolve-N` (and the stale
  `facts/.dispatch.lock`) — expected while aborting before `✓ action dispatched`.
- If ids get burned, renumber the plan/prediction to the **derived** id and leave a dated
  Article V `<!-- id note -->` in both `execution-log.md` and `predictions.md` naming the empty
  range and its cause. Do not silently let the gap stand.

### The `byte-identically` rule vs the `grep|awk|wc` whitelist — how to resolve the conflict
`prompts/evolution.md` now FORBIDS narrowing/re-patterning a Critic's literal verify expression.
But the metric parser only accepts backticked expressions starting with `grep|awk|wc`, and Critics
routinely bind `` `bash scripts/selftest-X.sh 2>&1 | grep -cE '^PASS: '` `` — which the parser
silently skips, firing a false COVERAGE SHORTFALL. Resolution (used at evolve-39, permitted by the
rule itself): publish an `awk`-prefixed wrapper that runs the identical command and counts the
identical lines, and carry a dated **Article V note** in the plan naming the original expression,
its live value, and the reason:
```awk
awk 'BEGIN{while(("bash scripts/selftest-X.sh 2>&1"|getline l)>0) if(l ~ /^PASS: /) n++; print n+0}'
```
Never substitute silently — the note is what separates this from the evolve-38 DEGRADATION finding.

### Never declare a metric on a field the post-dispatch refresh scripts rewrite
`refresh-harness-state.sh` and `refresh-next-events.sh` run **after** `✓ action dispatched`
and overwrite `facts/harness-state.md`'s header, `## Last Action` block and Next Events. A
metric like `` `grep -c 'Cycle evolve-37' facts/harness-state.md` >= 2 `` therefore PASSES at
gate time and re-reads **0** one second later — the file correctly advanced to evolve-38.
That is not a regression, but it makes the published row unreproducible, which is exactly the
instrument dishonesty the harness exists to catch. Assert instead on fields the refresh
scripts do NOT touch (the `## Critique Status` list, ledger files, script/prompt contents).
If you already shipped such a metric, **report the divergence in the cycle report** with the
reason — do not let the next Critic discover it.

**Sub-case (evolve-59): never metric your OWN cycle's future receipt.** Writing
`` `grep -c 'evolve-59' facts/harness-state.md` >= 1 `` or
`` `grep -c '^## evolve-59' facts/execution-log.md` == 1 `` into the evolve-59 plan is
unmeasurable at gate time (the row/header don't exist yet — the metric FAILS `== 1` against 0,
and a `>= 1` against 0 is also a fail), and it is exactly the self-referential count the
parser's SELF-MATCHING CRITERION branch exists to reject. Declare metrics that hold BEFORE
dispatch (selftest PASS count, counter present in a script, assertion name present). If you
want to assert the receipt exists, that is the `_reverify_published_metrics` / `_reverify_prior_cycle`
gate's job, not a plan metric's. The plan's `## Block terminator` header is required so the
block never runs to EOF.

### A row removal is INCOMPLETE until every derived ledger is reconciled (partial rollback)
Deleting a phantom row from `facts/execution-log.md` is only the visible third of the job. The
same dispatch also wrote:
- `facts/.dispatch-state` — action-type **count AND timestamp** (this is the cumulative counter
  the monoculture argument is reasoned against; a phantom leaves it permanently +1)
- `facts/harness-state.md` — header, `## Last Action`, `## Critique Status`
Leaving the phantom as *last writer* of either file is a **partial rollback** — true in its most
visible part, false as a whole, i.e. the phantom-PR witness class reproduced inside the
anti-phantom fix (this is what evolve-37 did and evolve-38 repaired). Reconcile all three in the
same cycle, note the correction + its cause in `facts/cleanup-log.md`, and check
`stat` mtimes: if a ledger's mtime equals the phantom's dispatch time, it has not been repaired.
This rule is now a REQUIRED clause in `prompts/evolution.md` (`partial rollback`).

### Critic verify commands can be over-broad — scope them before adopting
The evolve-37 counter-recommendation specified
`grep -c 'ADDRESSED (evolve-36)' facts/harness-state.md` == 0 to prove the self-attribution was
gone — but that pattern also matches *legitimate* older lines (`evolve-35 critique: ADDRESSED
(evolve-36)`), so the metric could never pass. Narrow it to the offending line's full text
(`'evolve-36 critique: ADDRESSED (evolve-36)'` == 0). Same meta-lesson as elsewhere in this
skill: execute the counter-recommendation's intent, verify its literal commands against live
state first, and report the divergence.

### Attribution rule: a cycle cannot address the critique it caused
`- evolve-N critique: ADDRESSED (evolve-N)` is always wrong — the critique is issued *after*
that cycle dispatched. The addressing cycle is N+1 (or later). Check timestamps
(`Critique Entry — <ts>` vs the audited cycle's dispatch time) before writing the line.

### NEVER re-run `execution-loop.sh evolve` to debug — it appends a PHANTOM ROW
**UPDATE (evolve-40): this is now ENFORCED IN CODE, not just by discipline.**
`_acquire_dispatch_lock` is the first statement of the evolve arm: an exclusive
non-blocking `flock -n 200` on `facts/.dispatch.lock` plus a per-cycle sentinel
`facts/.dispatch-sentinels/dispatched-<CYCLE_ID>` (moved out of `facts/.tmp` at evolve-41 —
see below) with a 3h cron floor. A second invocation inside the
window exits 3 with `DISPATCH ALREADY RUNNING` and writes nothing. Skipped when
`REPORT_ONLY=true`, and deliberately NOT acquired at source time — the selftest sources
the loop and would self-deadlock.

**UPDATE (evolve-41) — a lock is only as durable as the state it lives in.** The evolve-40
lock closed the *concurrent-process* case and left two *state-destruction* cases open, both
of which reproduce the same phantom row:
- `facts/.dispatch.lock` was a **tracked** git object, so any `git checkout` / `reset --hard`
  / `stash` in the harness repo swaps the inode under a live holder; a second arm then opens
  the NEW inode and takes `flock` cleanly. Fix: `git rm --cached` it, `.gitignore` it, and
  after `exec 200>"$lock"` assert `stat -c %i "$lock"` equals `stat -Lc %i /proc/self/fd/200`,
  failing closed with `DISPATCH ALREADY RUNNING — lock inode swapped`.
- The sentinel lived in `facts/.tmp/` — gitignored scratch shared with critic artifacts and the
  natural target of any cleanup arm. One `rm -rf facts/.tmp/*` evaporates the cron floor with
  zero log line. Fix: relocate to `facts/.dispatch-sentinels/` (explicitly gitignored) and
  forbid cleanup arms from touching it.

**Generalised rule (now REQUIRED in `prompts/evolution.md`): a guard whose state lives in a
directory another arm may delete is not a guard. Guard state must be in a path no cleanup arm
can reach — and must not be a tracked git object, since git operations rewrite inodes.**
Proof lives in `scripts/selftest-dispatch-lock.sh` (case (j) reproduces the inode-swap hole in
an isolated tmpdir and asserts the shipped branch closes it; case (k) asserts sentinel locality).

**Selftest authoring trap seen writing that file:** a static assertion that greps the
implementation for a forbidden string will match **its own explanatory comment** in that
implementation. `awk '/^_fn\\(\\)/,/^}/' file | grep -q 'facts/\\.tmp'` fired FAIL against the
comment saying "guard state must NOT live in facts/.tmp". Always strip comments before a
forbidden-string grep: `… | sed 's/#.*//' | grep -q …`, and scope the range to the function
rather than the whole file (the string is legitimate elsewhere).

**Second selftest authoring trap (evolve-59): a fixture whose metric expressions do not
REPRODUCE makes the case fail on drift.** When a selftest case exercises
`_reverify_published_metrics` (cases h/q/r), every `METRIC: <expr> -> <val>` it writes into the
fixture ledger row is **re-evaluated live** against `$HARNESS_DIR` by the re-verifier. A fake
expression like `` grep -c 'X' file `` with no backing file re-runs as `file: command not found`,
the re-verifier records `METRIC DRIFT` + returns non-zero, and the case fails even though the
*point* of the case (e.g. "prose must not inflate the count") is unrelated to the metrics'
values. Fix: give the fixture a **real data file** and write metric expressions that genuinely
reproduce against it:
```bash
local dataf="$TMP/q-data.md"; printf 'X\nY\nY\n' > "$dataf"
# fixture row metric:  `grep -c 'X' "$dataf"` -> 1 [PASS == 1]   # actually re-runs clean
```
Two corollaries: (a) place prose meant to be ignored AFTER the real metric lines — the
pair-parser spans from `METRIC: ` to the next `[...]`, so leading/interspersed prose gets
absorbed into a bogus pair; (b) a bare prose literal `METRIC:` (no ` -> `) is what the
prose-immune counter ignores — that is the fixture's point, but only when it sits outside the
parser's `METRIC: … […]` span. The case passes only when the metric values reproduce, the
prose-immune count matches `_count_declared_metrics`, and PLAN MUTATED does/doesn't fire as
asserted.

**Verification after hand-executing a bound counter-recommendation: use `--report-only`.**
When you have already applied the fix with `patch`/`write_file` and committed, running
`bash scripts/execution-loop.sh evolve` fires a real dispatch for work already done — the exact
double-dispatch the lock exists to prevent. Run `bash scripts/execution-loop.sh --report-only
evolve` instead: it exercises the full arm (arm discovery, external-feedback gate, credential
pre-flight, field parse) and stops before execution. Say in the report that `--report-only` was
deliberate, so the next Critic does not read it as a skipped step.

Three operational consequences you WILL hit:
- **Legitimate iteration requires clearing the sentinel:** `rm -f facts/.dispatch-sentinels/dispatched-evolve-N`
  before each retry. Do this only while the run is still *aborting before* `✓ action dispatched`.
  Once a real dispatch lands, stop — that is the terminal state.
- **A NEW scenario: resolved-cycle sentinels block a legitimate LATER dispatch.** The 3h cron-floor
  guard (`find "$sentinel_dir" … -newermt "-3 hours"`) fires on ANY recent sentinel, including ones
  from cycles that already shipped their receipt. Seen live at evolve-59: sentinels `evolve-51..57`
  all had `^## evolve-N` rows (resolved), but `dispatched-evolve-57` (mtime 18:21) sat inside the
  3h floor and blocked the 20:14 dispatch with `DISPATCH ALREADY RUNNING … refusing re-entry`.
  **Verify each blocking sentinel belongs to a RESOLVED cycle before clearing, and never clear the
  fresh sentinel the current dispatch creates:**
  ```bash
  for s in facts/.dispatch-sentinels/dispatched-evolve-*; do
    id="${s#*dispatched-}"
    grep -q "^## ${id} " facts/execution-log.md && rm -f "$s"   # resolved -> safe to clear
  done
  ```
  A sentinel with NO matching ledger row means that cycle never dispatched and its floor is doing
  its job — leave it. Clearing resolved sentinels is a legit `facts-cleanup`-adjacent step; note it
  in the cycle report so the next Critic does not read it as bypassing the lock.
- **Debug re-runs still bump `facts/.dispatch-state`'s cumulative counter** even though the lock
  blocked them and no rows were written. Reconcile it by hand at the end of the cycle
  (baseline + 1 real dispatch) and leave a dated `<!-- ledger note … -->` in `execution-log.md`
  saying why the number moved. The row count is authoritative; the counter is not.
- **Removing a phantom row RENUMBERS the next cycle.** Cycle id is `max ^## evolve-N + 1`, so
  deleting the phantom `evolve-40` makes your live cycle `evolve-40`, not `evolve-41`. The plan
  header, `harness-state.md` and `predictions.md` must all be renumbered to the *derived* id or
  `_assert_cycle_trace` fires `STALE PLAN HEADER` — which presents as a **silent** early return
  (dispatch logs look normal, no row appears). Reclaiming a phantom's number is correct; add a
  `> Numbering note:` block to the plan saying the id was reclaimed and why.

**UPDATE (evolve-42) — the INVERSE phantom: real work, NO receipt. Guarding the door does
not guard the ledger.** Five cycles hardened re-entry so a second dispatch could not write a
row. evolve-41 proved the opposite hole was wide open: it shipped a real commit and wrote **no**
`## evolve-41` row, so `max ^## evolve-N + 1` stayed frozen at 41 and the *next* dispatch would
have re-issued `evolve-41` over already-shipped work — the same id collision, arrived at from the
other direction. Two root causes, both now fixed:

- **CYCLE_ID was derived solely from the ledger it is supposed to write.** A dispatch that runs
  without appending cannot advance its own counter. Fix: keep an independent high-water mark
  (`facts/.cycle-highwater`, gitignored) written at derivation time and derive from
  `max(execution-log max id, high-water)`, emitting `LEDGER GAP: …` to stderr when the two
  disagree. Asserted by `scripts/selftest-dispatch-lock.sh` case **(l)**.
- **A no-execution path was writing the ledger that certifies execution.** The `REPORT_ONLY`
  branch called `_record_dispatch` and then `return 0` *before* any action ran, so
  `facts/.dispatch-state` counted dispatches that never dispatched. Fix: a separate
  `_record_report_only` → `facts/.report-state`. `.dispatch-state` now means "arms that actually
  executed" and nothing else.

**Generalised rule: a counter must not be readable only from the artifact its own writer may
skip, and a path that performs no work must not increment the counter that certifies work.**
Two ledgers, one advanced unconditionally at issue time, one appended only on real completion —
disagreement between them is the signal, not an error to suppress.

### ⚠️ evolve-54: THE ACTUAL ROOT CAUSE of the recurring missing receipt — `set -e` aborts before the append
Everything above this line treats "real work, no receipt" as a **counter-placement** problem, and
five cycles (evolve-42, 51, 52, 53) moved the high-water write around trying to fix it. That was
the wrong layer. The receipt was missing because `execute_action` **died before reaching
`_append_execution_log` at all**:

```bash
set -euo pipefail                                    # line 13 of execution-loop.sh
...
metric_out="$(_verify_recommendation_metrics)"; local metric_rc=$?   # ← ABORTS HERE
```

`_verify_recommendation_metrics` returns **non-zero BY DESIGN** whenever a declared metric fails
(that is the whole point of the fail-closed gate). Under `set -e`, a **plain assignment** whose
command substitution exits non-zero terminates the function immediately. The very next lines —
the `partial(metrics-failed)` downgrade and the ledger append — were unreachable. So **every cycle
with a failing metric shipped committed code and wrote no row**, and the `; local metric_rc=$?`
idiom made it look like the author had handled the failure.

Fix — capture the status with `||`, which `set -e` explicitly tolerates:
```bash
local metric_out status_override="" metric_rc=0
metric_out="$(_verify_recommendation_metrics)" || metric_rc=$?
```

**Diagnostic signature — memorise this.** The pre-fix run's last log line is
`✓ action dispatched` and then *nothing*, with no error and exit code 0. The post-fix run on the
same tree logs `⚠ declared metrics did not all pass — result downgraded to partial` and appends
the row. If a run's output stops cleanly at a known-good log line, **the next statement is a
`set -e` abort, not a silent early `return`** — look for an assignment, `let`, or arithmetic
expansion that can legitimately evaluate non-zero.

**Bash rules that follow (they generalise far past this harness):**
- `x="$(cmd)"; rc=$?` is a **lie under `set -e`** — `$?` is never read when `cmd` fails, because
  the shell already exited. Only `x="$(cmd)" || rc=$?` preserves the status.
- `local x="$(cmd)"` is the inverse trap: `local` *masks* the exit status, so the abort never
  happens and `$?` reads the status of `local` (always 0). Declare `local` and assign on
  **separate lines** whenever the status matters.
- `((n++))` evaluates to 0 when `n` was 0 → aborts under `set -e`. Use `((n++)) || true` or `n=$((n+1))`.
- **Never let a function that returns non-zero by design sit on the critical path to an audit
  write.** Order the code so the ledger append happens first, or guard every such call.

**Meta-lesson (the reason this took five cycles): four consecutive fixes patched the mechanism
named in the previous critique instead of reproducing the failure. Reproduce first.** Run the
thing, watch where the output stops, and fix *that* line. Full reproduction recipe and the
wider `set -e` trap catalogue: `references/set-e-abort-before-audit.md`.

### ⚠️ evolve-55: FREEZE THE PLAN AT DISPATCH — a criterion you can edit after grading is not a receipt
evolve-54 rewrote `facts/recommendation.md` **2m27s AFTER** the dispatch that graded it (plan
mtime 04:12:35 vs execution-log / .dispatch-state / .cycle-highwater all 04:10:08). The published
receipt therefore said `METRIC: NONE DECLARED [FAIL]` about a plan block that no longer existed,
while the plan that DID exist failed the live gate with a self-matching criterion + coverage
shortfall — neither disclosed. **Every gate hardening in this skill is unenforceable while the
grading sheet is mutable after grading.**

Fix (shipped evolve-55): in `_append_execution_log`, immediately before the high-water write,
snapshot the plan verbatim — and keep the directory OUT of `.gitignore`, because the snapshot IS
the receipt's evidence:
```bash
local _snap_dir="${HARNESS_DIR}/facts/.plan-snapshots"
mkdir -p "$_snap_dir" 2>/dev/null
[[ -f "$RECOMMENDATION_FILE" ]] && cp "$RECOMMENDATION_FILE" "${_snap_dir}/${cycle}.md" 2>/dev/null || true
```
`_reverify_prior_cycle` then grades the prior cycle against `facts/.plan-snapshots/<cycle>.md`,
logging `PLAN SNAPSHOT MISSING` (warn, never fatal) when absent. The first run after shipping
this WILL warn for the previous cycle — that is correct, not a failure.

**Generalised rule: any artefact that grades work must be frozen at the moment of grading. If a
later process can rewrite the criterion, the receipt proves nothing — and the audit will look
healthy the whole time.** Sibling of the two-ledger rule; same family as "measure the artefact,
not the receipt".

**Authoring trap found the same cycle — prose backticks are parsed as metrics.** The metric
selector is `grep -E '`(grep|awk|wc)[^`]*`'` applied to the WHOLE
`## Measurable improvement expected` range, so an Article V note in that range reading
"restated in whitelisted `awk` form" is picked up as a metric expression `awk`, executes
non-numeric, and FAILS the gate. **Never backtick the bare words grep/awk/wc in prose inside or
after the metric block** — write them unquoted (`whitelisted awk form`). Symptom: a `[non-numeric
FAIL]` line naming a one-word expression.

**Pre-flighting the gate: capture its output, don't let it print.** Calling
`_verify_recommendation_metrics` directly after sourcing can come back looking completely
silent with rc=0 through the `terminal` tool (output lost/swallowed), which reads as "no metrics
declared". Always capture and echo instead, so you see the real result:
```bash
bash -c 'set +e; . ./scripts/execution-loop.sh; echo "declared=$(_count_declared_metrics)"; \
  out=$(_verify_recommendation_metrics); echo "rc=$?"; echo "$out"'
```
`declared=N` plus N `METRIC: … [PASS …]` lines and `rc=0` is the green pre-flight.

### Verify a bound counter-recommendation is still open BEFORE executing it
A counter-recommendation can already be fully addressed by the time your cycle runs — another
session, or the cycle that received the critique, may have executed it. At evolve-54 all four
items (A)-(D) of the open high-severity critique were **already ADDRESSED** on the live tree.
Re-executing them would have produced a duplicate-work receipt and hidden the real defect.
Run each item's own `Verify:` command first and record the result in the plan's evidence
section. If all pass, say so explicitly, then spend the cycle on the residual the verification
exposes — that is where evolve-54 found the `set -e` abort.

### `refresh-harness-state.sh` silently no-ops unless the plan says the literal `Cycle evolve-N`
It selects with `grep -oE 'Cycle evolve-[0-9]+' facts/recommendation.md`. A correctly-named plan
titled `# Recommendation — evolve-55` matches **nothing**, and the script exits 0 with
`no cycle in recommendation.md — no-op` — which reads like success in a `| tail` and leaves the
state header a full cycle stale. (That staleness is what the evolve-52 critique logged as
measurement 8 and item (D).) evolve-54 added a fallback to any `evolve-N` in the file. Regardless,
always **read back `head -1 facts/harness-state.md`** after calling it; never trust its exit code.

**Operational corollary — WRITE YOUR OWN RECEIPT when you hand-execute a bound
counter-recommendation.** This is how evolve-41 lost its row and how evolve-42 nearly repeated it.
When you apply the fix yourself with `patch`/`write_file` + `git commit`, the loop run afterwards
is `--report-only` (correctly — see above), which appends nothing. **You must append the
`## evolve-N` row to `facts/execution-log.md` by hand** with a re-run metric chain, and refresh
`facts/harness-state.md`'s header + `## Last Action`. Final check before ending any hand-executed
cycle: `grep -c '^## evolve-<your id>' facts/execution-log.md` == 1 and `head -1
facts/harness-state.md` names your cycle. A cycle that shipped code and left no receipt is
indistinguishable, to the user and to the next Critic, from a cycle that did nothing.

**Backfilling someone else's missing row:** re-run every metric **live against the working tree**
before writing them — never copy the numbers out of the originating session's report — and carry
an inline `<!-- BACKFILLED by evolve-N at <ts>. <cause>. Metrics re-run live. Article V. -->`
comment. A backfilled receipt whose numbers were transcribed rather than re-measured is itself a
phantom.

Historical context for why the lock exists: cycle id is derived from the row count in
`execution-log.md`, so a **second successful dispatch inside the same wall-clock cycle
auto-advanced to `evolve-N+1`** and wrote a duplicate audit row for work done once. This
happened at evolve-37, evolve-38 and evolve-40. Four cycles treated the phantom rows as a
cleanup problem and none asked why re-entry was possible. **Meta-lesson: when the same defect
class recurs 3+ times despite being documented and rule-bound, stop repairing the symptom and
ask what makes it POSSIBLE.** A rule against untidy rollbacks does not close an unlocked door.

At evolve-37, a debug re-run 26 seconds after the real
dispatch produced a byte-identical `## evolve-38` row, which (a) published a duplicate row and
(b) falsely consumed the evolve-38 slot that the standing critique had bound to a specific
sanctioned action. Its own self-referential metric even read `2` instead of `1` because it counted
its predecessor's string.

- **Validate the plan file BEFORE the first run**, not by iterating on the loop. Full pre-flight
  checklist in `references/plan-file-contract.md`. Minimum: `grep -c '^RECOMMENDED_ACTION:'` == 1,
  `grep -c '^DETAIL:'` == 1, `grep -c 'Cycle evolve-N'` >= 1, both declared-counters agree.
- The plan header MUST contain the literal token `Cycle evolve-N` (`_assert_cycle_trace` greps
  `"Cycle ${_cyc}"`). A header reading `# Recommendation — evolve-37 …` FAILS with
  `STALE PLAN HEADER`; it must read `# Recommendation — Cycle evolve-37 …`.
- If a phantom row does land, **remove it** rather than annotate — a duplicate row for
  work done once is itself the phantom-report class. Back the file up first, delete the block,
  and append a dated `<!-- phantom-row removal … -->` comment explaining the removal, the backup
  path, and why removal beat annotation (Article V: the repair announces itself).
- Note the failing runs that abort BEFORE `✓ action dispatched` (missing DETAIL, stale header)
  append nothing — those are safe to iterate on. Only a *successful* dispatch advances the id.
- **Corollary seen live at evolve-39:** once your cycle has dispatched successfully, any further
  `bash scripts/execution-loop.sh evolve` aborts with `STALE PLAN HEADER: plan does not name
  evolve-N+1`. That abort is the guard **protecting you** — it is the expected terminal state of a
  completed cycle, not a failure to fix. Verify your work by sourcing the loop and calling the
  function directly (`source scripts/execution-loop.sh >/dev/null 2>&1; _reverify_published_metrics
  evolve-N`) instead of re-running the arm.
- **The unaddressed-critique abort will block your FIRST run of a cycle whose whole job is to
  execute that critique.** Do the work, then flip the blocking entry's `- Action: PENDING` to
  `- Action: ADDRESSED (evolve-N) — <summary>`, then run. Expected, not a bug (see the section on
  clearing it legitimately).

Allowed action types: update_script, create_skill, analyze, integrate_config, smoke_test, facts-cleanup, cleanup_and_integration_test, backup_scheduler, test_mechanism, version_bump, version_registry, skill_version_registry, bash_command, generic_action, skill_automation. Diversify — a monoculture of one action type (e.g. 7x `update_script`) is a stagnation signal the Critic flags.

### When a dispatch logs `✓ action dispatched` but writes NO row
A silent early return (usually `STALE PLAN HEADER`) — the arm's own output looks healthy.
`bash -x` trace technique, the sentinel-clearing retry loop, the `-x`-pollutes-metrics trap,
and a symptom→cause checklist: `references/diagnosing-silent-dispatch-failures.md`.

**Check the `set -e` abort FIRST (evolve-54).** If the output stops *immediately* after
`✓ action dispatched` with no further log line and no error, it is not a `return` — it is
`set -e` killing the function on `metric_out="$(_verify_recommendation_metrics)"`, which
exits non-zero by design whenever a declared metric fails. This was the real cause of the
missing-receipt class for five cycles. Recipe + bash trap catalogue:
`references/set-e-abort-before-audit.md`.
