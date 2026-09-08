---
name: harness-critic
description: Run a meta-learner critic that audits another agent's output for stagnation, data corruption, stale state, and action-type monoculture. Produces structured, evidence-based critique entries in an append-only log. The audited agent MUST read the critique before its next cycle (INVARIANT).
version: 1.8.0
created: 2026-07-28
updated: 2026-08-07
status: active
---

# Harness Critic v1.2

**Purpose:** Audit another agent's output (recommendation.md + execution-log + state files) for stagnation, degradation, data corruption, and action-type monoculture. Produce evidence-based diagnosis + actionable counter-recommendation. The audited agent MUST read the critique before its next cycle — either implement it or show evidence for rejecting it.

## Architecture

- **Separate cron:** Offset from the audited agent's schedule (e.g., +2h in a 4h cycle)
- **Verifier convergence:** The Verifier cron (`0 */6 * * *`) also produces critique entries in the same run, checking prediction outcomes + data integrity. This is deliberate — the Verifier's 6-hour cadence catches stale state faster than the Critic's 4-hour offset. The Critic focuses on deeper stagnation analysis (action-type monoculture, recommendation stagnation).
- **Output:** Append-only critique log (e.g., `facts/critique-log.md`)
- **Reader:** The audited agent (INVARIANT — must read before next cycle)
- **Tone:** Evidence-based, no padding, no flattery. Doubt → CRITICAL.

## Workflow (each run)

### 1. Snapshot
- `git log --oneline -20` (if git exists; flag if missing)
- `git diff HEAD~3 -- facts/recommendation.md` (if git exists)
- `cat facts/recommendation.md`
- `tail -50 facts/execution-log.md`
- `ls -la facts/`
- `tail -100 facts/critique-log.md` (last 2-3 entries for unaddressed check)
- `wc -l facts/*.md`
- `cat facts/.dispatch-state` (if exists)

### 1b. Cron Last-Run Check (NEW in v1.4)
After the snapshot, verify that the Evolution and Verifier crons actually ran on their last scheduled slot — not just that they're configured on the right schedule. A cron that's configured but never fires (e.g. due to a provider outage or job corruption) will show a stale last-run timestamp. Check:
- `hermes cron list | grep -A 8 'Harness Evolution'` — last run should be within the last 4 hours
- `hermes cron list | grep -A 8 'Harness Verifier'` — last run should be within the last 6 hours
- `hermes cron list | grep -A 8 'Harness Critic'` — last run should be within the last 4 hours
If any last-run timestamp is >1 cycle stale, flag as HIGH — the cron is configured but not executing.

### 2. Six Measurements

| # | Measurement | Threshold | Severity |
|---|-------------|-----------|----------|
| 1 | recommendation.md unchanged across last 3 runs? | 3/3 identical | CRITICAL |
| 2 | Unique RECOMMENDED_ACTION types in last 7 days | < 3 | CRITICAL |
| 3 | Agent ran but no tracked file changed? | true | HIGH |
| 4 | Previous critique unaddressed by audited agent? | ≥ high unaddressed | HIGH |
| 5 | Observation starvation: new signal but recommendation is no-op? | true | HIGH |
| 6 | State file staleness: harness-state.md, prediction-outcomes.md, or similar state files outdated by >1 cycle? | true | MEDIUM |

### 3. Data Integrity Check (NEW in v1.2)
- Scan the critique log itself for corruption: embedded read_file line-number prefixes (`N|-` patterns), glued entries, missing trailing newlines
- Check that prediction outcomes exist for all past-due predictions
- Check that git repository exists (required for measurement #1)
- **Check Verifier cron schedule** — if the Verifier runs less frequently than every 6 hours (e.g., `0 4 */2 * *`), flag it as a MEDIUM finding. A Verifier that runs every 2 days cannot check 1-cycle predictions, and the missing-outcomes gap compounds every cycle. The fix is `hermes cron edit <job_id> --schedule "0 */6 * * *"`.
- If corruption found, repair it AND flag it in the diagnosis

### 4. Diagnosis
One sentence — what is wrong, why it is wrong, which file:line + evidence.

### Counter-Recommendation
Specific, executable action. Not "think more" — file name + function + what to do. Include:
- RECOMMENDED_ACTION: the action type (bash_command|update_script|facts-cleanup|diversify_action|...)
- DETAIL: exact command, file, flag, argument
- CONFIDENCE: high|medium|low
- REASONING: reference to critique entry
- RISK: low|medium|high

**facts-cleanup** is the preferred action type when the diagnosis is stale state files, missing prediction outcomes, or no git repository. It breaks `update_script` monoculture streaks while still being a concrete, executable action. See `self-evolution-harness/references/facts-cleanup-pattern.md` for the full recipe.

### 6. Verdict
STAGNATION | DEGRADATION | HEALTHY | WATCH

### 7. Output Format (append to critique log)

```
## Critique Entry — <ISO8601>
- Cycle: <cycle-id>
- Prediction #N: CONFIRMED|INCONCLUSIVE|FAILED
- Verdict: HEALTHY|WATCH|STAGNATION|DEGRADATION
- Severity: critical|high|medium|low

### Measurements
1. Recommendation stagnation: <hash> vs <hash3> — same/diff
2. Unique actions (7d): <count>
3. No-op run: yes/no
4. Unaddressed critique: <prev_entry_id> → addressed/unaddressed
5. Observation starvation: yes/no — <evidence>
6. State file staleness: <files> — stale/current

### Diagnosis
<one sentence, file:line + git SHA + byte evidence>

### Evidence
- <file>: <sha> mtime <ts>
- <file>: <N> entries, last <ts>
- git log since=<date>: <N> commits
- <file>: <N> previous entries

### Counter-Recommendation
RECOMMENDED_ACTION: <bash_command|update_script|facts-cleanup|diversify_action|...>
DETAIL: <specific command — file name + flag + argument>
CONFIDENCE: high|medium|low
REASONING: <direct reference to critique entry>
RISK: low|medium|high

### Operator Action Required
<none or human intervention needed>
```

## CRITIQUE_APPEND_LEADING_NEWLINE (Mandatory Protocol)

Before ANY append to the critique log:

1. Ensure trailing newline: `python -c "from pathlib import Path;p=Path('facts/critique-log.md');b=p.read_bytes();p.write_bytes(b+b'\\n') if not b.endswith(b'\\n') else None"`
2. Entry body MUST begin at beginning-of-line with `## Critique Entry` (never concatenate to prior last line).
3. Post-flight: `grep -c '^## Critique Entry' facts/critique-log.md` must increase by 1; `tail -c 40 facts/critique-log.md` must NOT show `text## Critique Entry` glued.
4. Prefer: write entry to `facts/.tmp/critique_entry_runN.md` then `printf '\\n' >> facts/critique-log.md; cat facts/.tmp/critique_entry_runN.md >> facts/critique-log.md`

**Blocklist-safe append (recommended since 2026-08-05):** the `printf '\\n' >> ...; cat ... >> ...` chain and shell heredocs (`cat > ... <<'ENTRY'`) trip the command-parser `&`/blocklist heuristics on some setups. The reliable path is a single `execute_code` call with `pathlib` byte ops — no shell quoting, no heredoc, no `>>`:

```python
from pathlib import Path
p = Path('facts/critique-log.md')
b = p.read_bytes()
if not b.endswith(b'\n'):
    p.write_bytes(b + b'\n')
entry = Path('facts/.tmp/critique_entry_63.md').read_bytes()
p.write_bytes(p.read_bytes() + b'\n' + entry)
Path('facts/.tmp/critique_entry_63.md').unlink()
text = p.read_text()
print("entries:", text.count('## Critique Entry'))
```

This both appends AND verifies in one atomic call, so the mandatory post-flight (count +1, no glue, trailing newline) runs in the same step. Never hand-verify a critique log you just appended with a shell `grep` chain that itself can be blocklisted.

## Pitfalls

### Read-file line-number corruption
When a prior Critic run reads the critique log with `read_file`, the tool prefixes each line with `N|`. If the Critic then appends its output using a tool that includes those prefixes (e.g., by copying from read_file output), the prefixes become embedded in the file content. This produces lines like `35|- Rationale: ...` instead of `- Rationale: ...`.

**Fix:** Before appending, scan the critique log for lines matching `^\d+\|` that are not legitimate content. Remove the prefix with:
```python
import re
text = re.sub(r'^\d+\|', '', line, flags=re.MULTILINE)
```
For double-corruption (`41|41|- ...`), loop until no more matches.

### Glued-entry false positive in Data Integrity section
When the Critic's own Data Integrity section quotes the phrase `text## Critique Entry` (e.g. "no glued entries (`text## Critique Entry` = 0 hits)"), `grep -c` will count it as a match even though it's a false positive — the text is inside a code span, not a real concatenation.

**Fix:** Before reporting glued entries, verify each match is NOT inside a backtick-quoted string or code block. Use a Python check:
```python
import re
text = open('facts/critique-log.md').read()
for m in re.finditer(r'text## Critique Entry', text):
    before = text[max(0,m.start()-200):m.start()]
    if '`' in before and '`' in before.split()[-1]:
        print('FALSE POSITIVE (quoted in prior text)')
    else:
        print('REAL CORRUPTION')
```
Alternatively, grep for the pattern at the start of a line only: `grep -c '^text## Critique Entry'` — real corruption always starts at column 0.

### No git repository
Without a `.git` directory, measurement #1 (recommendation stagnation via git diff) is impossible. The first cycle should initialize git: `git init && git add -A && git commit -m "harness baseline <cycle>"`. If git is missing, flag it as a HIGH finding.

### Harness path ambiguity (FIXED Jul 29, 2026)

**CORRECTED 2026-07-31:** the LIVE harness is `/root/.hermes/profiles/gentech/harness/` — that is the `Workdir` of all four harness crons (verify with `hermes cron list | grep -A6 Harness`). `/root/.hermes/harness/` is an ORPHAN tree (own git, own facts/, last written 2026-07-30 08:00Z by a stray `0 8 * * *` trigger). Never audit the orphan. Ground-truth the path from the cron `Workdir` field, not from any skill file.

### Stale state files
State files like `harness-state.md` and `prediction-outcomes.md` can fall behind the actual cycle. The Critic should check mtime vs last cycle timestamp and flag any file that hasn't been updated in >1 cycle.

**Specific harness-state.md header staleness check:** The header line (`# Harness State — <date> (Cycle evolve-N)`) can drift from the actual last action. Compare the cycle number in the header against the cycle number in the `## Last Action` section. If they differ by >1, flag as MEDIUM — the header is stale even if the file's mtime is current. This is a cosmetic issue but degrades the state file's value as a human-readable reference.

### Running the live gate: exports are mandatory, sourcing kills your shell (verified 2026-08-04)
`_verify_recommendation_metrics` returns 0 immediately and prints NOTHING when
`$RECOMMENDATION_FILE` is unset (`execution-loop.sh:414`), and the sourced script's
`set -euo pipefail` propagates into YOUR shell, so a non-zero return aborts before
your `echo rc` ever runs. A bare `source ...; _verify_recommendation_metrics`
produces empty output that *looks* like "the gate emits no metrics" but actually
means "you invoked it wrong". Always:

```bash
bash -c 'export HARNESS_DIR="$PWD" \
  RECOMMENDATION_FILE="$PWD/facts/recommendation.md" \
  EXECUTION_LOG="$PWD/facts/execution-log.md"
source scripts/execution-loop.sh
set +e +u +o pipefail          # MANDATORY — undo the sourced script'"'"'s set -e
out=$(_verify_recommendation_metrics); rc=$?
echo "GATE_RC=$rc"; echo "$out"
echo "DECLARED=$(_count_declared_metrics "$RECOMMENDATION_FILE")"'
```
Never report "the gate fails / emits nothing" without those three exports.

### CYCLE_ID is recomputed internally — exporting it is a no-op (verified 2026-08-05)
`execution-loop.sh:64` sets `CYCLE_ID="evolve-$(( ${_cycle_n:-0} + 1 ))"` from the last
cycle in the execution log — it OVERWRITES any `CYCLE_ID` you export, so a guard test
that exports `CYCLE_ID=evolve-62` actually runs the guard against `evolve-63` (last
real cycle 62 → internal 63). Symptom: a fixture targeting `^## evolve-62` "fails to
fire" the RECEIPT-EXISTS SELF-CHECK and you spend rounds convinced the guard is broken.
The guard is fine; your fixture targeted the wrong cycle id.

To test a guard that fires on the CURRENT cycle's own header, you must target the
**next** cycle number (internal `last+1`), not the cycle you're auditing:

```bash
# last logged cycle is evolve-62, so the internal CYCLE_ID resolves to evolve-63.
# A stealth receipt-exists metric grepping its own header ^## evolve-63 MUST fail the gate.
cat > /tmp/stealth.md <<'EOF'
## Measurable improvement expected
- `awk '/^## evolve-63/,/^- detail:/' facts/execution-log.md | grep -c '^## evolve-63'` >= 1
## Block terminator
EOF
bash -c 'export HARNESS_DIR="$PWD" EXECUTION_LOG="$PWD/facts/execution-log.md"
source scripts/execution-loop.sh
set +e +u +o pipefail
RECOMMENDATION_FILE="/tmp/stealth.md"
_verify_recommendation_metrics; echo "RC=$?"'   # expect RC=1 + RECEIPT-EXISTS SELF-CHECK marker
```

Note: exporting `RECOMMENDATION_FILE` before `source` is pointless — the script
re-assigns it at line 38. Set it AFTER sourcing to point the gate at a fixture. The
legitimate range-END form (`awk '/^## evolve-62/,/^## evolve-63/'…` measuring a PREVIOUS
row) must still pass — the guard's regex `grep[^|]*\^##[[:space:]]*${CYCLE_ID}` is scoped
to the current-cycle self-header, which is exactly why a wrong-cycle fixture reads as "no fire".

### Count emitted metrics after the `||` separator, not by `grep -oE 'METRIC:'`
A receipt's detail line embeds `METRIC: ` literals in its PROSE (quoting the metric
being removed, the awk program text, the renumbered block) — a whole-block
`grep -oE 'METRIC:'` or `gsub(/METRIC: /,"")` over-inflates the count and reads as
unplanned-metric drift when it's just quoting. The real emitted rows are the
semicolon-delimited chunk AFTER the last `||` in the detail line. Isolate them:

```bash
awk '/^## <cycle>/{f=1} f&&/^- detail:/{print}' facts/execution-log.md \
  | sed 's/.*|| //' | grep -oE 'METRIC: ' | wc -l
```

That count must equal the plan's declared metric count. (This is the documented
"METRIC line's text can itself contain embedded METRIC tokens" pitfall from the
evolve-61 section — the `||`-after form is the reliable extraction, not a raw count.)

### String-presence metrics: the feature is grepped, not wired (evolve-55)
The late-stage failure mode is NOT false numbers — it is TRUE numbers about the
wrong thing. A plan declares `grep -c '<new-token>' script.sh >= 2`; the token is
present; the metric passes; the feature is never invoked. At evolve-55 the plan
snapshot was written, git-tracked and byte-verified — and read by nothing,
because `_snap` appeared only in an `[[ -f ]]` test and a `log` line while the
grader was still called as `_reverify_published_metrics "$prior"`.

When a cycle claims a new capability, never accept the grep count. Run
`grep -n '<new_var_or_token>' scripts/execution-loop.sh` and classify every hit:
**log line / existence test / comment = decorative**; **passed as an argument,
opened, parsed, compared = load-bearing**. If every hit is decorative the
capability does not exist — severity HIGH, and the counter-recommendation must
name the exact call site and the argument to add. Also diff the plan's STEP 0
prose against the code: a false capability claim in a user-inspectable file is an
Article V (Transparency of Influence) violation, not a wording nit.

### Content-deleting regexes in state refreshers
`re.sub(r'`[^`]*`', '', text)` deletes the code span **and its contents**; the
intent is almost always `re.sub(r'`([^`]*)`', r'\1', text)`. Seen live in
`scripts/refresh-harness-state.sh` — it silently stripped every filename and
function name out of `## Last Action — Change:` while mtimes stayed current, so
every staleness check passed. Read the *rendered* body, don't just stat the file.

### Prediction header drift
`facts/predictions.md` accretes header formats (`## PREDICTION #N`,
`## Prediction #N`, `## PRED#N`, `## evolve-N`). Any Verifier enumeration keyed on
one form under-counts silently. Audit with
`grep -oE '^## [A-Za-z]+ ?#?[0-9]*' facts/predictions.md | sort | uniq -c`
and flag MEDIUM when more than one form is present.

### Honour the audited agent's own pre-commitments
When a plan writes a conditional into its STEP 0 ("if evolve-56 is also
`update_script`, treat it as STAGNATION, not MEDIUM"), that is a binding
self-judgement. Quote it back and enforce it on the next cycle — do not re-derive
a softer severity. This is the cheapest available lever against monoculture.

### Action-type monoculture
Track the diversity of RECOMMENDED_ACTION types across the last 7 days. If all actions are the same type (e.g., all `update_script`), flag as CRITICAL even if each individual change is valid. The audited agent is not exploring its action space.

**Break monoculture by source, not by count.** Three-plus consecutive `facts-cleanup` cycles on *measurement-instrument hygiene* (prose-immune counter, selftest cases, state refresh) is the same monoculture as an `update_script` streak — the labels differ but the work is one theme. The dispatch heuristic: the evolve arm should assign RECOMMENDED_ACTION by **what the change touches** — an edit to `execution-loop.sh` or a selftest script is `update_script`, a state-file/ledger reconciliation is `facts-cleanup`. When the next cycle is bound to the same backlog theme as the prior two, demand either a real new source (see Article II drift below) or an explicit Article III no-op — never a fifth backlog item.

### Article II drift: the harness feeding on itself
Article II forbids treating internal bookkeeping as user value. When the harness spends **several consecutive cycles (5+) working only on its own measurement instruments with zero user-friction entries in witness-log.md / no `facts/observation-log.md` at all**, that is a governance violation brewing — flag WATCH/medium even though every mechanical gate passes. This is the failure mode that appears AFTER the loop starts enforcing its findings correctly (a genuinely-fixed gate is the prerequisite). Counter-recommendation must (A) create `facts/observation-log.md` with a dated "no user friction since <last>; self-referential for N cycles; Article II risk" entry, (B) force the next cycle to either cite a real friction item or emit an explicit `- result: noop` with reason "no user friction" — never manufacture work to justify existence.

### Self-referential grep invariants (audit-trail self-quoting)
Once the audit trail itself quotes a literal that a future check greps for, a whole-file count of that literal becomes unreachable-by-design and produces false FAILs. Live example: `grep -c '16:0xZ'` returns 3, all three are self-referential mentions inside the corrected-note, the Article V trail, and the receipt description — the real placeholder in the evolve-56 row block was fixed, but a global `== 0` invariant can now never pass. **A grep invariant must be scoped to the region it audits**, e.g. `awk '/^## evolve-56/,/^- detail:/' facts/execution-log.md | grep -c '16:0xZ'` == 0 — never a whole-file grep of a literal the ledger quotes in its own repair notes. Distinguish a real placeholder from an audit quote before flagging; check the file:line context of every hit.

### Compaction/archival must target git-tracked dirs, not gitignored temp dirs (evolve-77)
The Gardener (or any compaction job) truncates the audit-trail files (critique-log,
execution-log, predictions, prediction-outcomes) to ~100 lines and archives the full
content. If the archive target is a GITIGNORED temp dir, the full history is the ONLY
copy of the truncated content and one `rm -rf` permanently destroys the harness's memory.
Live example (evolve-77): the 2026-08-08T04:10:01Z compaction wrote archives to
`facts/.tmp/*-archive-20260808T041001Z` — `.gitignore:1` is `.tmp/`, so
`git ls-files facts/.tmp/` returns EMPTY. The 2026-08-01 compaction had correctly used
git-tracked `facts/history/` (both archives tracked). The 2026-08-08 run REGRESSED to
gitignored `.tmp/`. The truncation was also left UNCOMMITTED (6 modified files in the
working tree; the evolve-77 commit predated the compaction by 2 minutes).

**Critic detection protocol (evolve-77+):** when the snapshot shows a large
`git diff --numstat` deletion-only delta on the audit-trail files (e.g. critique-log
`0 1908`, execution-log `0 438` — zero additions), do NOT assume corruption. Check the
cleanup-log for a documented compaction run, then verify the archive target:
1. `grep -n '\.tmp\|history' .gitignore` — is the archive dir gitignored?
2. `git ls-files facts/.tmp/` — if empty, the archives are NOT durable.
3. `git status --short` — is the truncation committed or stranded?
4. Compare archive completeness: `wc -l facts/.tmp/<archive>` vs `git show HEAD:facts/<file> | wc -l` (archive + WT should equal HEAD; if so the move is lossless).
If the archive target is gitignored and/or the truncation is uncommitted, flag CRITICAL
(data-durability defect) and counter-recommend `facts-cleanup`: MOVE the archives to the
git-tracked `facts/history/` dir, COMMIT the truncated state + moved archives, and FIX
the compaction job to write archives to `facts/history/` (the tracked pattern) not
`.tmp/`. Note: the compaction logic may live in the cron job's PROMPT, not in a script —
`harness-gardener.sh` had no compaction code (81 lines, dormant-skill scan only).

### Stranded uncommitted work after a HEALTHY critique (evolve-63)
A critic/verifier commit that touches ONLY its own log (`critique-log.md`) can
leave the audited agent's verified work stranded in the working tree. Live
example: the evolve-62 critique commit `3a19d23` touched only
`facts/critique-log.md`, while the evolve-62 guard code, selftest case (w),
`## PREDICTION #49` renumber, and evolve-62 receipt sat uncommitted — at risk
of loss or re-dispatch. The next cycle's snapshot must check
`git status --short` and, when it shows modified tracked files that the
critique already verified live (metrics PASS, selftest PASS), commit them
rather than assume the audit trail is complete. A HEALTHY verdict does not
imply a clean working tree — verify `git status --short` is empty before
declaring the cycle closed. This is a data-integrity gap, not a code defect:
commit the stranded work as-is (no re-verification needed if the critique
already proved the metrics).

### Plan metric that greps a literal its own DETAIL prose contains (evolve-63)
The SELF-MATCHING gate also fires on the PLAN-AUTHORING side, not just the
receipt side. Live example (evolve-63): a plan declared
`grep -n "^- Result:" facts/harness-state.md` == `- Result: ok` to verify a
state-file repair — but the plan's own DETAIL text contained the literal
`- Result: ok` (it was describing the change it would make). The gate flagged
the metric `SELF-MATCHING CRITERION on facts/harness-state.md — an unscoped
grep of the file the criterion is written into measures itself`, downgraded
the receipt to `partial(metrics-failed)`, and `refresh-harness-state.sh` then
wrote that stale `partial` back into the state file — re-introducing the very
false-failure signal the plan was trying to remove.

**Rule:** when a plan metric greps a facts file for a literal that the plan's
own DETAIL/STEP-0 prose will contain (a value being set, a status being
changed, a token being added), the metric MUST be awk-range-scoped to the
region it audits so it cannot match the plan text itself. Correct form:
`awk '/^## Last Action/,/^## Critique Status/' facts/harness-state.md | grep -c '^- Result: ok'` == 1
— never a whole-file `grep -n` of a literal the plan quotes. This is the
plan-side mirror of the evolve-61 receipt-side self-grep: same defect class,
different authoring surface.

**Cascade to watch:** a SELF-MATCHING flag on a plan metric is not just a
receipt downgrade — the state refresher (`refresh-harness-state.sh`) reads the
receipt's `result:` and writes it into `harness-state.md`. So a self-inflicted
`partial` propagates into the human-readable state file and must be repaired in
BOTH places: (1) the receipt row (re-state `ok` with scoped metrics), and (2)
the state file's `- Result:` line. Repair both in the same commit.

### Undeclared receipt metric that self-counts its header (evolve-61)
A receipt row can carry a METRIC that was **never in the frozen plan snapshot** AND is structurally unpassable because its awk range opens at the very header it greps. Live example (evolve-61): `awk '/^## evolve-61/,/^- detail:/' facts/execution-log.md | grep -c '^## evolve-61' -> 0 [FAIL == 1]`. The range begins at the `^## evolve-61` header, the grep counts that literal, so the value is always >= 1 and `== 0` can never hold. It forced `result: partial(metrics-failed)` even though all plan-declared metrics PASSED live. A false FAIL is as corrosive as a false PASS — it makes the `partial(metrics-failed)` signal uninformative.

**Critic detection protocol (evolve-61+):**
1. Cross-reference the receipt's METRIC tokens against the plan snapshot: `awk '/## Measurable improvement expected/,/Block terminator/' facts/.plan-snapshots/<cycle>.md | grep -c '^- \`'` (plan count) vs `awk '/^## <cycle>/,/^## <prev>/' facts/execution-log.md | grep -oE 'METRIC:' | wc -l` (receipt count). Receipt count > plan count = an UNPLANNED metric — flag it. This catches drift at write time even when there's no `PLAN MUTATED` alarm (a metric can be invented in the row itself, not the plan).
2. For any receipt metric whose command references the execution-log, check whether its awk range starts at the same literal it counts. If so, the criterion (`== 0` etc.) is unreachable by construction — it's a self-counting no-op. The correct form counts rows strictly below the header: `awk 'NR>1 && /^## <cycle>/' ...`.
3. Re-run ALL plan-declared metrics live; if they pass, the FAIL is a receipt artifact, not a regression. Counter-recommendation: `facts-cleanup` — repair the row (re-state result as `ok` with N/N PASS), scope the emitter in `scripts/execution-loop.sh` (`grep -n '<header>' scripts/execution-loop.sh`), and re-run the gate to rc=0.
4. Always check whether the plan snapshot itself contains ANY reference to the file the metric greps (`grep -c 'execution-log.md' facts/.plan-snapshots/<cycle>.md`) — zero means the self-grep was invented post-dispatch.

**Pitfall for this check:** a METRIC line's text can itself contain embedded `METRIC: ` tokens, inflating the count. Count `grep -oE 'METRIC:'` occurrences and verify each distinct criterion against the plan before declaring a mismatch.

**Variant — receipt drops a snapshot metric AND adds unplanned ones, no PLAN MUTATED marker (evolve-63):** the evolve-61 protocol catches an *added* unplanned metric. A subtler form: the receipt can **drop a snapshot metric and add unplanned ones simultaneously**, with `grep -c 'PLAN MUTATED <cycle>'` == 0. Live example (evolve-63): the frozen snapshot `facts/.plan-snapshots/evolve-63.md` declared 3 metrics; the receipt published 4 — it dropped snapshot metric #2 (`git status --short | wc -l` == 0) and added 2 never in the snapshot (RECEIPT-EXISTS guard, selftest-18). The in-cycle SELF-MATCHING repair of one metric (documented in a `<!-- NOTE -->`) was legitimate, but the net effect was receipt-count(4) > plan-count(3) = 1 unplanned metric.

**Detection (evolve-63+):** compare three counts for the audited cycle:
1. Snapshot declared: `awk '/## Measurable improvement expected/,/Block terminator/' facts/.plan-snapshots/<cycle>.md | grep -c '^- \`'`
2. Receipt published (after `||`): `awk '/^## <cycle>/,/^## <next>/' facts/execution-log.md | sed 's/.*|| //' | grep -oE 'METRIC: ' | wc -l`
3. `grep -c 'PLAN MUTATED <cycle>' facts/execution-log.md`

If receipt-count != snapshot-count AND the PLAN MUTATED marker is absent, flag **MEDIUM** (process-hygiene gap) — even when every published metric passes live. The added metrics may be legitimate verification of committed work (not self-referential no-ops) and the dropped metric may verify clean (e.g. `git status` == 0), so this is NOT false-PASS/false-FAIL corruption; it is a plan-vs-receipt reconciliation gap that degrades the audit trail. Counter-recommendation: `facts-cleanup` — restore the dropped snapshot metric to the receipt's emitted set AND add the `<!-- PLAN MUTATED <cycle> ... -->` marker documenting the in-cycle additions; enforce receipt-count == snapshot-count with any divergence carrying the marker. Escalate to CRITICAL if the same cycle class drifts again (evolve-61 invented an 8th metric, evolve-63 dropped one and added two — a recurring pattern).

### Prediction outcomes going unrecorded
The Verifier or audited agent may fail to record outcomes for past-due predictions. The Critic should cross-reference predictions.md (entries past DUE) against prediction-outcomes.md and flag any missing outcomes.

### Metric-extractor-grammar gap: unparseable declared metric → false COVERAGE SHORTFALL (evolve-66)
A THIRD, distinct metric-mis-authoring root cause, orthogonal to the
self-advancing-state and SELF-MATCHING classes. The metric extractor regex in
`scripts/execution-loop.sh` is `grep -oP '(?<=`)(grep|awk|wc)[^`]*(?=`)'` — it only
matches a declared metric whose command **starts with** `grep|awk|wc`. A declared
metric written as a bash pipeline — e.g.
`bash scripts/selftest-detail-metric-gate.sh 2>&1 | grep -c '^PASS: '` — is silently
unparseable: the extractor drops it, the declared-count path diverges, and the
post-dispatch run emits a false `COVERAGE SHORTFALL N/M [FAIL]` that the cycle
bandages in-cycle with a PLAN MUTATED marker. The author gets **zero pre-dispatch
feedback** the metric is unparseable.

This was the 5th consecutive metric mis-authoring (evolve-61 invented an 8th,
evolve-63 dropped+added, evolve-64 mis-authored, evolve-65 mis-authored, evolve-66
mis-authored). When a cycle's NOTE admits "originally-declared metric used a
`bash ... | grep -c` form the metric extractor (grep|awk|wc-prefixed only) could not
parse", the root cause is the **extractor grammar**, NOT the self-advancing class
(that gate may already be separately fixed). Honoring a prior critique's escalation
clause ("if it mis-authors again, escalate to CRITICAL") is correct even when the
earlier root cause was closed — the authoring surface still leaks.

**Detection:** the plan snapshot's `## Measurable improvement expected` block (or
`Verify:` list) contains a backtick-quoted command that does NOT start with
`grep|awk|wc` (e.g. `bash … | grep -c`, `python …`). Grep the snapshot for
`^- \`(bash|python|cat|…)`. Also note: the same snapshot may carry stray duplicate
metric lines above the `## Measurable improvement expected` marker (in the DETAIL /
Verify prose) — count only the block between the marker and `## Block terminator`.

**Counter-recommendation (distinct from facts-cleanup):** `update_script` — add an
authoring-time `_reject_unparseable_metric` gate that FAILs any declared metric not
prefixed `grep|awk|wc` (author sees it pre-dispatch instead of a post-dispatch
COVERAGE SHORTFALL), plus a selftest case (z) asserting the exact `bash … | grep -c`
form is rejected and a wc/grep-prefixed control passes. This is the authoring-surface
mirror of the self-advancing gate: reject at authoring time, don't bandage
post-dispatch.

### Authoring-time gate must be PRE-dispatch, not post-dispatch (evolve-68)
When a critique demands an "authoring-time reject" gate (e.g. `_reject_unparseable_metric`
to stop a metric-authoring miss before the work happens), VERIFY the gate is actually
wired BEFORE the action dispatches — not inside `_verify_recommendation_metrics`.

Live failure (evolve-68): the evolve-67 critique demanded a pre-dispatch reject for
unparseable declared metrics. The gate was added, but it lives inside
`_verify_recommendation_metrics`, which is only invoked at `execution-loop.sh:978`
INSIDE `execute_action` — AFTER the action has already dispatched. The evolve arm calls
`execute_action` at line 423 with NO pre-dispatch metric gate. Result: the author gets
zero pre-dispatch feedback, the cycle still ships unparseable metrics, gets a false
COVERAGE SHORTFALL, and bandages with a PLAN MUTATED marker. evolve-68 re-offended the
exact class the evolve-67 critique declared CLOSED — the 6th consecutive metric-authoring
miss.

**Detection:** when a critique claims a metric-authoring gate is "shipped and verified,"
grep the call site. If `_verify_recommendation_metrics` (or the gate function) appears
ONLY inside `execute_action` / after the dispatch point, it is a post-hoc detector, not
an authoring-time guard. The correct wiring is a pre-dispatch scan of the frozen plan's
`## Measurable improvement expected` block immediately BEFORE `execute_action` in the
evolve arm, aborting with `return 2` on any unparseable line.

**Counter-recommendation:** `update_script` — move the gate pre-dispatch (before
`execute_action`), add a selftest case asserting the action's side-effect file is NOT
created when the plan declares an unparseable metric. Do NOT declare the pathology
"CLOSED" until you have verified the gate fires before the work, not after.

### Phantom-literal metric: a syntax gate cannot catch a semantic miss (evolve-69)
A metric-authoring gate that only rejects non-`grep|awk|wc`-prefixed metrics is a
**syntax** gate — it cannot catch a **semantic** miss: a grep of a literal the target
never emits. Live example (evolve-69, the 7th consecutive metric-authoring miss,
evolve-61/63/64/65/66/68/69): the plan declared `grep -c 'ALL ASSERTIONS HOLD'` but the
selftest prints `selftest-detail-metric-gate: ALL 24 ASSERTIONS HOLD` (count embedded,
`selftest-detail-metric-gate.sh:705`), so the literal never matches and the receipt
downgrades to `partial(metrics-failed)`. The pre-dispatch gate shipped THAT cycle did
not catch it — the metric is syntactically valid (grep-prefixed) but greps a phantom.

**Detection:** for each declared grep metric, extract the grep pattern's literal and the
target file. If the literal is ABSENT from the target file AND the target file is NOT
named in the action's DETAIL as a file the action will modify, it is a phantom-literal
metric. The "target file in the modify list" guard is the discriminator against
false-positives on legitimate forward-looking metrics (a grep of a literal the action
will ADD to a file it edits is valid).

**Counter-recommendation:** `update_script` — add a `_reject_phantom_literal_metric`
check to the pre-dispatch gate (alongside `_reject_unparseable_metric`), plus a selftest
case asserting a plan grepping a non-existent literal is REJECTED pre-dispatch while a
forward-looking grep of a file the action will modify PASSES. Do NOT declare the
metric-authoring pathology "CLOSED" until a phantom-literal metric is rejected before
dispatch — a syntax-only gate is insufficient.

### Duplicate dispatch: byte-identical consecutive rows + missing sentinels + un-consumed plan (evolve-73)
The evolve-41 re-entrancy lock can fail SILENTLY, producing two byte-identical
execution-log rows for the same plan. Live example (evolve-73): evolve-72
(`execution-log.md:498`, 16:03:37Z) and evolve-73 (`:505`, 16:03:46Z) carried the
SAME `update_script` action, same `result: ok`, same 3 metrics, and identical detail
text (md5 `c1918be1` for both) — 9 seconds apart. The same `recommendation.md`
(md5 `effc5976`) was dispatched twice.

**Three independent signals, any one warrants a CRITICAL:**
1. **Byte-identical consecutive rows.** `awk '/^## evolve-N/,/^## evolve-M/' facts/execution-log.md | grep '^- detail:' | md5sum` — if two adjacent cycles hash identically, it's a duplicate dispatch, not coincidence.
2. **Missing dispatch sentinels.** `ls facts/.dispatch-sentinels/` — if a cycle that has an execution-log row has NO `dispatched-evolve-N` sentinel, the sentinel mechanism failed to persist. The 3h floor check (`execution-loop.sh:111`) has nothing to block on → re-entrancy guard defeated. Sentinel creation (`execution-loop.sh:121` `: > "${sentinel_dir}/dispatched-${CYCLE_ID}"`) has NO post-write `[[ -f ]]` assertion, so a silent persistence failure is invisible.
3. **Un-consumed recommendation.** If `facts/recommendation.md` is not advanced/consumed after a successful dispatch (no `## CONSUMED` marker, no new plan written), the same plan re-dispatches next cycle. Check `ls facts/.plan-snapshots/ | grep -c 'evolve-<N+1>'` — zero means the plan was never consumed.

**Counter-recommendation:** `update_script` — (A) add a post-write existence assertion to sentinel creation (`[[ -f "${sentinel_dir}/dispatched-${CYCLE_ID}" ]]` else `log_error "SENTINEL WRITE FAILED"` + `return 3`); (B) add recommendation consumption (append `## CONSUMED <CYCLE_ID>` after successful `execute_action`, guard refusing dispatch of an already-consumed plan); (C) add a selftest case asserting a second dispatch of an already-consumed plan is refused rc=3. Key the `## CONSUMED` marker to the plan's own header cycle id so a genuinely new plan is not blocked.

Also check for **stale plan-snapshot headers**: `facts/.plan-snapshots/evolve-N.md` header lagging the filename by one (e.g. evolve-72.md says "Cycle evolve-71") is a symptom of the plan not being re-frozen per cycle.

### Evolve-action stub detection (NEW Jul 29, 2026)
When the Critic finds 3+ consecutive no-op cycles AND the previous critique was severity=critical AND unaddressed, the root cause is likely a structural defect in `execution-loop.sh` — the evolve action is a stub that checks file existence but never implements anything. The Critic should:
1. Read `execution-loop.sh` and check the `evolve` case arm — if it only prints "no friction found" without reading recommendation.md or implementing RECOMMENDED_ACTION, flag as CRITICAL
2. Note that the ALARM prefix (`[HARNESS STAGNATION ALARM]`) will fire on the 3rd consecutive critical unaddressed critique — this is the correct behavior, not a false positive
3. The counter-recommendation must be `update_script` (rewrite the evolve action), not `facts-cleanup` — facts-cleanup cannot fix a structural code defect

## Tone Rules
- No padding: "great work", "going well", "looks good" — FORBIDDEN
- Doubt → CRITICAL
- No evidence → say "no evidence", do not lower severity
- "You could do X" is not allowed. "DO X" — write the command, the file, the function
- If stagnation, say "STAGNATION". Not "maybe stagnation"

## ALARM
Severity=critical AND previous run also critical AND unaddressed → prefix with `[HARNESS STAGNATION ALARM]` in delivery.
