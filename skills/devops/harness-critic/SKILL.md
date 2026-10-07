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
Compare each job's `last_run_at` against its OWN configured cadence as printed by
`hermes cron list` — never against a hard-coded interval. The Critic moved from
`2 */4 * * *` to `0 2 * * *` (daily); a hard-coded "within 4 hours" then fires a false
HIGH on every run, which is the entry-70..73 failure class (a criterion read as the
wrong thing and passing/failing for the wrong reason).
- Harness Evolution (`0 */4 * * *`, currently PAUSED by design) — a frozen `last_run_at`
  is correct while `enabled=false`; flag only if it is ENABLED and >1 cycle stale
- Harness Verifier (`0 */6 * * *`) — flag if `last_run_at` is >6h old
- Harness Critic (`0 2 * * *`, daily) — flag if `last_run_at` is >1 day old
If any last-run timestamp is >1 cycle stale, flag as HIGH — the cron is configured but
not executing.

### 1c. Outcome-coverage check — run it, do not remember it (NEW 2026-09-22)
Workflow step 3 ("check that prediction outcomes exist for all past-due predictions")
is performed by the instrument, not from memory. The checker lives in the SKILL tree, NOT
under the harness workdir (there is no `harness/skills/devops/`), so use the
`HERMES_HOME`-anchored path — run from the harness dir:

    python3 "$HERMES_HOME/skills/devops/harness-critic/scripts/check-prediction-outcomes.py"

(`$HERMES_HOME` = the profile dir, e.g. `/root/.hermes/profiles/gentech`. A bare
`skills/devops/...` relative path resolves against the harness workdir and fails.)

Record the `parsed:` / `graded:` / `LIVE corpus:` lines and the exit code in the entry.
`rc=0` = every live past-due prediction carries a grade block. `rc=1` = a live gap (a
finding). `rc=2 VACUOUS CHECK` = the corpus or the due grammar drifted and the tool can
grade nothing — a DEFECT to report, never a pass. The checker is block-scoped by design:
a pid mentioned in prose (a tally line, a `DEFECT C` enumeration, an `EARLY WARNING`
note) is NOT a grade. Its corpus is matched by NAME PREFIX, not `*.md` — the 2026-08-08
compaction left its archive without a trailing `.md` and a `.md` glob silently drops 41
authored pids.

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

**CORRECTED 2026-07-31:** the LIVE harness is `${PROFILE_DIR}/harness/` — that is the `Workdir` of all four harness crons (verify with `hermes cron list | grep -A6 Harness`). `/root/.hermes/harness/` is an ORPHAN tree (own git, own facts/, last written 2026-07-30 08:00Z by a stray `0 8 * * *` trigger). Never audit the orphan. Ground-truth the path from the cron `Workdir` field, not from any skill file.

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

### A "FIXED and VERIFIED" claim must carry the command and the INSTALLED digest (entry 82)
Live failure: entry 81 published `check-prediction-outcomes.py` as "FIXED and VERIFIED this
cycle — 238 lines, md5 `c164ecd4ed7e8d1c4c9fb701d45d6406`" with quoted control outputs. No
copy of that digest has ever existed: `find` across `/root/.hermes` and `/root/vaults`
returned 8 copies, **every one the 58-line pre-fix `de2c55f5…` file**; `--predictions` was
not a recognized flag; and the claiming commit touched 3 files, all under `facts/` — zero
scripts. The Verifier falsified the claim in four consecutive cycles.

**Rule:** every "FIXED and VERIFIED" line names (a) the exact command a reader can re-run, and
(b) the digest of the file **as installed**, re-measured at publish time with `md5sum
<installed path>` — never taken from the authoring buffer, never from the plan. If the
installed digest does not match what the entry states, the entry is false and must be
corrected in the same cycle. Write the file → re-run the controls → record the digest → then
publish.

**Corollary — write fixes to the SYNC SOURCE, not the profile copy.** Profile-local edits
under `skills/` are overwritten nightly: `30 4 * * *` runs `cp -r
/root/vaults/gentech/10-Labs/skills-distribution/* skills/`. A repair written only to
`~/.hermes/profiles/<p>/skills/…` survives at most a day, and its own "verified" claim decays
with it.

### A digest published for a file the cycle KEEPS WRITING is a phantom (entry 87)
The entry-82 rule above covers a digest that never existed because the work never happened.
The mirror case: the work happened, but the digest was measured **mid-flight** — before the
cycle's own later writes to the same file. Live example: entry 86 published
`facts/harness-state.md`'s post-render digest as `6138517e1c338907b34a4b05b5f0006e`;
re-measured across all **130** revisions of that file in git, **no revision has ever carried
that digest** (pre-render `f08a7e22…`, post-cycle committed `687774e8…`), and the literal now
appears only inside `facts/critique-log.md` — the claim quoting itself. Cause: the Critic
re-renders the computed blocks and *then* writes its own `## Last Action` /
`## Critique Status` / header into the same file, so the object it commits is not the object
it measured.

**Rule:** publish digests of the **committed revision**, re-measured after the LAST write of
the cycle: `git show HEAD:<path> | md5sum`. Never publish a digest captured between two
writes to the file it names. If a figure must be quoted before the file is frozen, label the
moment ("pre-write md5 … ; committed-revision md5 …"). A de-duplicated check exists and is
cheap: `for r in $(git log --format=%h -- <path>); do git show $r:<path> | md5sum; done | grep -c <claimed>`
must be >= 1 for any digest that claims to be a revision of that file.

### A control that stubs a script by writing through a symlink edits PRODUCTION, and the run still reports success
A scratch-tree control must never point a stub at the live tree by symlink. Live failure
(2026-09-29, Critic entry 89): the control ran `ln -s $HARNESS/scripts/refresh-cron-table.sh
$SCRATCH/scripts/` then `printf '#!/bin/bash\nexit 0\n' > $SCRATCH/scripts/refresh-cron-table.sh`
to neutralise the refresher so the checker could not repair a planted fault. **`>` follows a
symlink**, so the write landed on the LIVE file: both `harness/scripts/refresh-cron-table.sh`
and `refresh-next-events.sh` became 19 B (`#!/bin/bash\nexit 0`) in the production tree, and the
control run printed its success line. The symptom that exposed it was a *wrong* one —
`refresh-cron-table: no state file` on a path where the file demonstrably existed — and only
re-reading the file confirmed the damage.

**Rules for every control from now on:**
1. Populate the scratch tree with `cp`, never `ln -s`.
2. After ANY control that writes, re-`md5sum` the live files the control touched and compare to
   `git show HEAD:<path> | md5sum`. A green control is not evidence that the live tree is intact.
3. Recovery is `git checkout -- <path>`; then re-verify md5 HEAD→WT and restore the mode
   (`chmod 711` for these harness scripts).
4. Disclose it in the entry even when recovery was clean — this is the Critic's own
   "a successful command is not a successful task" rule turned on the Critic.

### A verifier's success string must enumerate the classes it read — and prove it can fail on each
The entry-88 class (Provider cells) recurred one column over (Schedule cells, entry 89) because
the fix was applied to the reported cell rather than to the **pattern**. Live: the pre-fix
`harness-state-refresh.sh` (md5 `370079b2…`) verified census, status, next-events and provider;
with the refreshers stubbed and all four Schedule cells set to `9 9 9 9 9` it printed
`census + status + next-events + provider cells all match the live store` and returned **rc=0**.

**Rule:** for EVERY rendered cell class, perturb one cell in a scratch copy with the refreshers
stubbed and require a non-zero rc. A class with no falsification control is not covered,
whatever the success text says. Classes that will pass this check while still lying:
- **Rows that do not exist at all.** A deleted table row is invisible to every per-cell check —
  the refresher preserves the roles the file already lists, so a dropped row is never re-added.
  Add a coverage invariant: every store job whose `workdir` ends `/harness` must have a row.
- **Columns whose values legitimately differ per job** (Schedule, Provider) — these need their
  own comparison, never a column-agnostic regex that happens to match the row.

### A cell that echoes a store DECLARATION cannot detect a runtime divergence (entry 90)
Every class-1..6 check in a state verifier compares the rendered file against the *store's own
fields*. None of them can see that the runtime dialled somewhere else, because the store field
**is** the declaration. Live (2026-09-30): `cron/jobs.json` read `provider: opencode-go` on 4/4
harness rows, `config.yaml`'s `providers:` map held `{nous, zai, opencode-go}`, and the
Verifier's last two cycles were posted to `https://ollama.com/v1/chat/completions` — a provider
with **no entry in that map** — returning 429 and leaving the harness's own grading instrument
dark for two cycles while the operator-facing table certified the declared provider as verified.
The divergence is visible only in the runtime's own artifacts: the request dump
(`sessions/request_dump_cron_<jobid>_*.json` → `request.url`, `reason`), and those are written
on FAILURE only, so scope the check to jobs whose store `last_status` is an error.

**Rule:** when a rendered cell names a provider, an endpoint, a model, or any other value the
runtime *resolves*, verify the **effective** value, not the declared one, and render the
effective value beside the declaration when they disagree. Pair it with a no-false-positive
control (rewrite the evidence so the two agree → must return rc=0); without that control a
falsification proves only that the checker can fail, not that it can pass. Give a divergence
its own exit code — `rc=4` must stay "the rendered file disagrees with the store", because a
faithful render of a bad runtime is a different defect with a different owner.

**And stamp the evidence with the moment it describes.** The dump is evidence about ONE run —
the last *failed* one — and a rail can be repaired after that failure. Live: the fleet migrated
off `ollama-cloud` at 00:57–01:16Z on 2026-09-30, one hour AFTER the Verifier's last two failed
cycles, so the same divergence string was simultaneously a true statement about those runs and a
misleading one about the live rail. A computed line that stays in the operator-facing file after
the cause is fixed is the entry-90 finding turned on the fix itself: label the evidence with its
timestamp, and check the fix's own output for the same class before publishing it.

### A per-cell checker that classifies a row by its VALUE verifies only the values it recognises (entry 91)
`harness-state-refresh.sh` class 2 matched rows with the regex `^\| (\w+) \| ([0-9a-f]+) \| .* \| 🟢 ok — last (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})Z \|$` — the status literal sits INSIDE the pattern, so a row rendered as `🔴 error …`, `⏸️ PAUSED (enabled=false)` or `⚫ NOT IN STORE` could never match. Three of the four harness rows were therefore certified by nothing while the success line read `status cells … match the live store`. Falsified 2026-10-01 with the refreshers stubbed: Verifier cell `🔴 error — last 1999-01-01 …: FALSIFIED` and Evolution cell `⏸️ PAUSED (enabled=false) — FALSIFIED` → the universality sentence, **rc=0**. The mirror case was live, not hypothetical: the pre-render file read `🔴 error — last 2026-09-30 00:01:04Z` on the Verifier while the store read `ok` (2026-10-01T00:05:42Z) — a false-RED that entry 90's repair could not see, because entry 90's finding was a false-GREEN rendered as `🟢 ok` and class 2 *did* read that.

**Rule:** a status (or any other) cell check must be **coverage-scoped, not value-scoped** — classify EVERY row and compare it against the same branch the renderer uses, so no row escapes by virtue of its own value. The renderer's own function is the spec: `refresh-cron-table.sh:status()` returns `⏸️ PAUSED (enabled=false)` when `enabled` is false, `🔴 {last_status} — last {last}Z: {last_error}` when `last_status` matches `error|fail|429|usage limit`, else `🟢 {last_status} — last {last}Z`. Mirror it exactly, including `cell()`'s `|`→`/`, whitespace collapse and `[:78]` truncation, or the comparison fails for reasons that are not defects. Controls: the falsified non-ok cell must return non-zero, an untouched copy must return zero, and a falsified **ok** cell must still return non-zero — otherwise you have traded a blind check for a broken one.

### A trigger outside `cron/jobs.json` is invisible to every store-scoped census
`cron/jobs.json` is not the whole scheduler. Live (2026-09-29, Critic entry 89): a **root
crontab** line fired `0 8 * * * cd /root/.hermes/harness && bash execution-loop.sh evolve` daily
at a directory deleted 2026-07-31 — still executing (kernel CRON journal), failing silently, and
recorded in **no** fact file, because `harness-state.md`'s computed census, the Verifier's
job-health scan and the Critic's own step 1b all read the Hermes store. The trigger becomes
dangerous at resume time: it is a second, unsynchronised trigger for the same loop.

**Rule:** when auditing triggers, pair `hermes cron list` with `crontab -l` and
`systemctl --user list-timers`, and confirm every referenced path exists. Name the scheduler in
the finding — "a cron" without the store name is what let this sit unseen for 61 days.

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

### "Frozen is expected" is not "the content is correct" (entry 77)
Measurement #6 gets gamed by an excuse, not by a check. Live example: entries 70-73
(Sep 10-13) each reported "6. State file staleness: **none** … harness-state.md frozen
evolve-161 since halt — expected" — while at commit `944c643`, the state file live
during all four runs, the `## Active Cron Jobs` Schedule cells were wrong on 2 of 4 rows
(Critic `2 */4 * * *` vs live `0 2 * * *`; Gardener `0 4 1,8,15,22 * *` vs live
`15 4 1,8,15,22 * *`). Four consecutive HEALTHY/low verdicts on a misread criterion,
and that window is exactly where the dead ALARM path and the provider 429 wall were
brewing.

**Rule:** measurement #6 is "does the file's CONTENT match the live store", never "is the
file's mtime/header what I expected for this state". Verify by extracting each row's cells
and comparing to `cron/jobs.json` for that job id — a plain string comparison. A frozen
file is not a correct file. The cheapest check: `git show <commit>:facts/harness-state.md`
for the revision live during the run you are auditing, then diff against the store.

### A cell no script reads back is a cell an agent can falsify while claiming verification (entry 77)
Before accepting any "verified byte-equal" claim in a commit message, ask what would have
had to read the value back. Live example: commit `88e6229` (entry 75) changed the Provider
cell on 4/4 rows from the CORRECT `opencode-go` (already present at `7a79891`) to
`ollama-cloud`, and asserted "all 4 rows now byte-equal to `jobs.json` (0 wrong cells,
verified by plain string equality, no regex)". `grep -n 'provider'
scripts/refresh-next-events.sh scripts/refresh-harness-state.sh scripts/harness-gardener.sh`
returns **0** — nothing ever read that cell. Sweep EVERY store before accepting the claim:
`/root/.hermes/profiles/*/cron/jobs.json` plus `/root/.hermes/cron/jobs.json`. Here the four
harness job ids exist in exactly one store, all four reading `opencode-go`, and
`ollama-cloud` is the `provider` of zero jobs in it (it appears once, inside another job's
`prompt` text) — so the value was not read from anywhere. Distinguish the store's
`provider` FIELD from the effective route named in an error string; conflating them is the
plausible-looking mechanism, and it is still a false claim.

**Counter-measure:** demand the cell become a COMPUTED field rather than a stricter
instruction — no agent writes it, so no agent can assert anything about it. See
`scripts/refresh-cron-table.sh` (reads `${HERMES_HOME}/cron/jobs.json`, rewrites the table
region only, idempotent: 2nd run prints `unchanged (N rows)` with an identical md5).

### Dry-run the state refreshers on a COPY before trusting them (entry 77)
A refresher that derives its value from a stalled input is destructive, not idempotent.
Live example: `scripts/refresh-harness-state.sh` takes the cycle from
`facts/recommendation.md`; with Evolution halted, that file is frozen at evolve-160 while
the newest executed cycle is evolve-161, so running it rewrote line 1 to
`# Harness State — 2026-09-17 (Cycle evolve-160)` — today's date stamped onto a 29-day-old
terminal plan, destroying the correct hand-written header. Worse, a prior Critic entry
(74, item 4) still instructed the operator to "re-run scripts/refresh-harness-state.sh"
verbatim in the log — a standing destructive instruction of the same class as the `.tmp`
purge advice that entry had to reverse.

**Rule:** dry-run by passing the STATE FILE AS ARGUMENT 1, never by setting `HARNESS_DIR`:

```bash
cp facts/harness-state.md /tmp/dry/harness-state.md   # then deliberately corrupt a cell in the copy
bash scripts/refresh-cron-table.sh /tmp/dry/harness-state.md   # writes the COPY; reads the live store
bash scripts/refresh-next-events.sh /tmp/dry/harness-state.md  # same contract
md5sum facts/harness-state.md   # must be unchanged vs. before
```

The WRAPPER takes the same optional argument as of 2026-10-03, so the same form is safe on it:

```bash
bash scripts/harness-state-refresh.sh /tmp/dry/harness-state.md   # writes the COPY, verifies the COPY
md5sum facts/harness-state.md   # must be unchanged vs. before
```

Before 2026-10-03 `harness-state-refresh.sh:53` read `STATE="$HARNESS/facts/harness-state.md"`
with no `${1:-…}` — a positional argument was **silently discarded**, so that command wrote the
LIVE file, verified the LIVE file, and returned rc=0 while the copy on the command line was never
touched. Measured live (Critic entry 93, 2026-10-03): live md5 moved `10f6f46e -> 7a3a49cc` and
the copy stayed at `10f6f46e`. The wrapper is the one refresher the Critic runs every cycle, so
this made every wrapper-level falsification control impossible without a full `cp -r` scratch
tree. Fixed (`STATE="${1:-$HARNESS/facts/harness-state.md}"`, installed md5
`3a4723cfaade173f1ce0e1e54bf097a8`, 3/3 copies) and control-tested both ways: arg-1 → live md5
unchanged + copy re-rendered rc=0; no-arg → live rc=0. **Before running any refresher on a path,
grep its source for `${1` — a script that has no `$1` ignores yours and writes its default.**

**`HARNESS_DIR=<tmp> bash scripts/<refresher>.sh` IS NOT A DRY RUN — it writes the LIVE
file** (measured 2026-09-25, Critic entry 85). `refresh-cron-table.sh:38-47` and
`refresh-next-events.sh:15-23` never read `HARNESS_DIR`; they read `${HERMES_HOME}` (set
in every agent shell) and default `STATE_FILE` to `${HERMES_HOME}/harness/facts/harness-state.md`.
Only `refresh-harness-state.sh:10-11` reads `HARNESS_DIR`, and it passes `"$STATE_FILE"`
as arg 1 to the other two — which is why the trap went unnoticed by readers of this file
for eight cycles. The entry-77 recipe below used the `HARNESS_DIR` form, so the "dry run"
it prescribed mutated the live file, and every later reader who followed it did the same.
Corrected here at the sync source; the live md5 stayed `c5fefdd0adb1fc6167125ab1b265445b`
byte-identical under the arg-1 form.

Then patch the standing instruction in the log with a `SUPERSEDED`
marker. The correct guard is a comparison against a second source (here: newest
`^## evolve-N` in `facts/execution-log.md`) that refuses the write when the inputs
disagree — refuse and report, never guess.

### Locating a writer: grep the FIELD it writes, never the RENDERED line (entry 84)
A forensic search for the process that writes a file must test the code that emits it, not the
text it emits. Live failure: entry 83 found every long WHY line in `facts/witness-log.md`
truncated to exactly 200 B and concluded *"the writer is **not a local script** … the cap cannot
be fixed at source from here"* — on the strength of `grep -rl 'Severity: blocking' /root/vaults
/root/.hermes` returning **0 hits**. The writer was `context-weight.py:119`
(`"detail": item['detail'][:200]`), run nightly by the ENABLED cron `fcca23360df2`
("Context Snapshot — Mess Hall", `6 0 * * *`). The literal never appears in the script because
the writer assembles it from data (`f"- Severity: {w['severity']}"`). The 0 hits were the
*evidence for* a false root-cause conclusion — the entry-69 phantom-literal class applied
forensically. This is the third instance of "the test measured the wrong property", and the
first where it closed an investigation wrongly.

**Rule:** to find a writer, (a) `grep -rl '<the TARGET PATH or its basename>'` across
`/root/vaults` and `/root/.hermes` — search for the filename, not a line of its content; (b)
check the session store, which names the job directly:
`sqlite3 <profile>/state.db "select id,session_id,tool_name,timestamp,substr(content,1,200) from messages where content like '%<filename>%' order by timestamp desc limit 20"`
— the winning row is the one whose stdout says the file was written; (c) `sqlite3 ... "select
id,session_id,timestamp,substr(tool_calls,1,300) from messages where tool_calls like '%<filename>%'"`;
(d) read the job's `prompt` from `cron/jobs.json` for the script path it invokes. A writer
inside an ENABLED cron means the corruption RECURS on the next run.

**Corollary — hand-repairing a corrupted record is not a fix.** Restoring truncated lines
(entry 83 did this correctly, byte-faithfully) leaves the corruption scheduled. Do not write
"repaired" until the writer is either located-and-patched or proven absent by a
filename-scoped search. Entry 83's repair held for exactly one day; entry 84's source fix is
what makes it durable.

### `str.count('## Critique Entry')` over-counts — anchor the grep (entry 84)
The self-quoting pitfall, on the Critic's own verification step. After appending an entry whose
Data Integrity section quotes `^## Critique Entry` = N, `text.count('## Critique Entry')` counts
those quoted mentions too: live, the anchored `grep -c '^## Critique Entry'` returned **3**
while `str.count(...)` returned **10**. Always verify with the anchored form
(`grep -c '^## Critique Entry'`, or `sum(1 for l in text.splitlines() if l.startswith('## Critique Entry'))`)
and report the anchored number.

### Verify the class you claim, not the classes that are easy to check (entry 88)
A checker that audits N-1 of N cell classes while printing a universal success string is
worse than no checker: it converts "not measured" into "verified". Live example (entry 88):
the harness-state refresh wrapper shipped in entry 86 read back census, status timestamps
and Next Events rows, and printed `all computed cells match the live store` — but
`grep -c 'provider' <script>` was **0**. The Provider cell is the one cell class commit
`88e6229` had already falsified on 4/4 rows while asserting byte-equality (entry 75), i.e.
the exact defect the table was made computed to prevent. Falsified live: with the refreshers
stubbed so the checker could not repair the fault, four Provider cells set to
`FALSIFIED-PROVIDER` produced the universality sentence and **rc=0**.

**Rule:** every success string enumerates what was actually read
(`census + status + next-events + provider cells all match`), never a universal claim. And
for each rendered cell class, prove the checker can fail: perturb one cell in a scratch copy
with the refreshers stubbed and require a non-zero rc. A class with no falsification
control is not covered, whatever the message says.

**Corollary — a near-miss fix is a finding, not a private correction.** The first edit here
landed in `/root/.hermes/scripts/provider-auto-switch.py`; the runtime executes
`$HERMES_HOME/scripts/provider-auto-switch.py`
(`hermes_cli/cron.py:562-565` `_scripts_dir_for_cron() → CRON_DIR.parent/"scripts"`;
`tools/cronjob_job_args.py:365-384` `_validate_cron_script_path`). Same filename, same
`systemctl` call, same `.bak-` lineage — different file, and the two had drifted for 11 days
(the live copy lacked a guard the other had). **Before publishing any "FIXED" claim on a
script, read `md5sum $HERMES_HOME/scripts/<name>` on the path the resolver names, not on the
path you happened to edit.** If two copies of one script exist, gate/fix both and publish
both digests — and treat the drift itself as a finding.

### A harness INPUT writer must commit its own write — and the fix is re-measured on the LIVE path (entry 96)
The Critic diagnosed `facts/witness-log.md` stranding for four consecutive entries (92-95):
`$HERMES_HOME/scripts/context-weight.py` (run by the enabled job `fcca23360df2`) appended to the
witness log and never committed, so the friction record — the very input the Evolution resume-or-halt
decision rests on — sat as ` M facts/witness-log.md` in the working tree until the Critic committed it
by hand. `grep -c 'git\|commit\|subprocess' <writer>` = 0 was re-measured every cycle but never fixed,
because it was filed as an operator item and carried.

**Rule:** when the audited harness consumes a file written by a *separate producer* (a profile script,
a sibling cron), a stranding defect in that writer IS in scope for the Critic — it is a defect in the
harness's own input pipeline, not a neighbour's backlog. Add the commit step `try/except`-wrapped so a
VCS failure can never break the producer, and control-test it end-to-end in a `cp`-built scratch tree
with the writer's path constants repointed at scratch — never `ln -s` (entry-89 class), never run the
writer against its real paths as a test. Then re-measure the LIVE files the control could have touched.

**Corollary — a `scripts/` fix has no revision history.** The profile `scripts/` tree is NOT under
version control (`git -C $HERMES_HOME/scripts rev-parse --show-toplevel` -> `fatal: not a git
repository`). Publish such a fix's digest as a **live-file** digest, labelled as such — never present
it as a committed-revision digest (the entry-82/87 class) — and confirm it is durable against the
nightly skills sync, which propagates `skills/` and NOT `scripts/`.

### A success line keyed on an unobserved return code is a success line that cannot fail (entry 97)
`subprocess.run(..., check=False)` returns; it does not raise. A `✅ … committed` printed after it
with no `returncode` test reports success even when the command failed. Live (2026-10-07, entry 97):
the witness-log writer shipped the previous cycle printed `✅ witness-log.md committed (N entry(ies))`;
falsified in a `cp`-built scratch repo with a `pre-commit` hook exiting 1 — the message did not change,
`git log` gained NO commit, and the record sat `M` (staged, uncommitted). The exact stranding the fix
existed to prevent, reported as success. When a critique ships a fix, do not accept its control's
`✅` as evidence: re-run the control with the failure INJECTED and require the success line to
disappear.

**Rule:** every success line in a script must be guarded by the OBSERVED returncode
(`if proc.returncode == 0:`), and the failure branch must PRINT the rc and the stderr. `check=False`
is a fine choice for best-effort work; an unconditional success print after it is not. Control both
ways: clean → the success line; failure injected (a hook that exits 1, a stubbed binary) → a failure
line and NO success line. `check=True` + `try/except` satisfies this too — the defect is the
unobserved rc, not the flag.

## Tone Rules
- No padding: "great work", "going well", "looks good" — FORBIDDEN
- Doubt → CRITICAL
- No evidence → say "no evidence", do not lower severity
- "You could do X" is not allowed. "DO X" — write the command, the file, the function
- If stagnation, say "STAGNATION". Not "maybe stagnation"

## ALARM
Severity=critical AND previous run also critical AND unaddressed → prefix with `[HARNESS STAGNATION ALARM]` in delivery.
