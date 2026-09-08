# facts/recommendation.md — the parser contract

Derived from reading `scripts/execution-loop.sh` directly (evolve-33, 2026-08-02).
When in doubt, re-read the parser rather than trusting a prose instruction — a Critic
counter-recommendation got this wrong and the literal reading produced a green row
with zero metrics.

## What the loop actually reads

| Field | Parsed by | Guarded? | Failure if absent |
|---|---|---|---|
| `RECOMMENDED_ACTION:` | `_parse_field "RECOMMENDED_ACTION"` | **yes** (`action_type`) | loop refuses |
| `CONFIDENCE:` | `_parse_field` | no | blank in log |
| `DETAIL:` | `_parse_field "DETAIL"` (:353) | **NO** (as of evolve-33) | writes `- detail:  \|\| METRIC: …` — a content-free audit row |
| `REASONING:` | `_parse_field` | no | blank |
| `RISK:` | `_parse_field` | no | blank |
| metrics | `_verify_recommendation_metrics` (:276-301) | **NO** — `return 0` on no-match (:282) | zero metrics captured, row still `ok` |

Fields must be **bare lines** starting at column 0. `## RECOMMENDED_ACTION:` is not
matched — the parser stops at `^#`.

## The metric selector, exactly

```bash
mapfile -t lines < <(sed -n '/^## Measurable improvement expected/,/^## /p' "$RECOMMENDATION_FILE" \
    | grep -E '`(grep|awk|wc)[^`]*`')
[[ ${#lines[@]} -gt 0 ]] || return 0        # <-- fail-open: no metrics == pass
```

Consequences:
- The section header must be **exactly** `## Measurable improvement expected`.
- The range ends at the next `^## ` — anything after a following header is invisible.
- Only `grep`, `awk`, `wc` are eligible commands.
- The expression must be inside **backticks**. Plain text is skipped silently.
- The comparison operator is pulled separately with
  `grep -oE '(>=|<=|==|>|<)[[:space:]]*[0-9]+'`. With no operator you get
  presence-only checking (any numeric output passes, including `0`).

## Known-good block

```markdown
## Measurable improvement expected
- `grep -c 'detail:  ||' facts/execution-log.md` == 0
- `grep -c 'Change: ||' facts/harness-state.md` == 0
- `grep -cE '^[[:space:]]*CYCLE_ID=' scripts/execution-loop.sh` >= 1
```

## The plan HEADER must carry the literal `Cycle evolve-N`

`_assert_cycle_trace` runs `grep -q "Cycle ${_cyc}" "$RECOMMENDATION_FILE"`. The token is
`Cycle evolve-37`, not `evolve-37`. A header reading `# Recommendation — evolve-37 (…)`
dispatches the action, then fails with `✗ STALE PLAN HEADER: plan does not name evolve-37`
AFTER the row is already appended. Write `# Recommendation — Cycle evolve-37 (…)`.

## Two rival declared-counters — make them agree before dispatching

| consumer | expression | terminates on |
|---|---|---|
| gate (`execution-loop.sh:294`) | `sed -n '/^## Measurable improvement expected/,/^## /p' \| grep -cE '^- '` | next `## ` header |
| prediction parity falsifiers | `awk '/Measurable improvement expected/,/^$/' \| grep -c '^-'` | first blank line |

They agree only if the block has **no blank lines between bullets** AND is **followed by a
`## ` header**. A blank line ⇒ awk undercounts ⇒ same row graded PASS by the gate and
FALSIFIED by the prediction. EOF termination ⇒ the sed range never closes ⇒ every trailing
`- ` bullet in the file inflates `declared`. Both clauses are now REQUIRED in
`prompts/evolution.md`.

## Pre-flight checks (run these before `bash scripts/execution-loop.sh evolve`)

Run these as **separate simple commands** (chained `&&` batches with quoted metacharacters
trip the hardline blocklist). Getting these right on the first pass matters: see
"phantom row" below — you do not get a free retry after a successful dispatch.

```bash
cd "$HERMES_HOME/harness"
grep -c '^RECOMMENDED_ACTION:' facts/recommendation.md        # expect 1
grep -c '^DETAIL:' facts/recommendation.md                    # expect 1
grep -c "Cycle evolve-$N" facts/recommendation.md             # expect >= 1
sed -n '/^## Measurable improvement expected/,/^## /p' facts/recommendation.md \
  | grep -cE '`(grep|awk|wc)[^`]*`'                           # expect == metrics declared
sed -n '/^## Measurable improvement expected/,/^## /p' facts/recommendation.md \
  | grep -cE '^- '                                            # gate counter
awk '/Measurable improvement expected/,/^$/' facts/recommendation.md \
  | grep -c '^-'                                              # awk counter — MUST equal the above
```

## Phantom rows: a successful dispatch is ONE-SHOT per cycle

`CYCLE_ID` derives from the highest `^## evolve-N` in `execution-log.md` + 1. Re-running
`execution-loop.sh evolve` after a successful dispatch therefore writes a **duplicate row
under the next cycle id** — real damage, because it also consumes a cycle slot that a
standing critique may have bound to a specific action.

- Runs that abort *before* `✓ action dispatched` (missing `DETAIL:`, `RECOMMENDED_ACTION:`
  count != 1) append nothing and are safe to iterate on.
- Runs that reach `✓ action dispatched` append a row **even if a later guard fails** —
  `STALE PLAN HEADER` fires after `_append_execution_log`. That combination (dispatch
  succeeds, guard fails, you fix the header and re-run) is exactly how a phantom lands.
- Recovery: back up the log, delete the phantom block, append a dated
  `<!-- phantom-row removal … -->` comment recording what was removed, the backup path,
  and why removal beat annotation. Then re-verify `grep -c '^## evolve-'`.

## Post-flight checks

```bash
grep -c 'detail:  ||' facts/execution-log.md                  # expect 0
grep -c 'Change: ||'  facts/harness-state.md                  # expect 0
tail -6 facts/execution-log.md                                # detail non-empty, metrics present
```

## The fail-open family

Three instances of one pattern found in this loop — **a check that reports success when
it has nothing to check**:

1. `_assert_cycle_trace` returned 0 on an empty cycle id (closed at evolve-32, :441).
2. The metric gate accepted any numeric output, including `0` against a `>= 1`
   threshold (closed at evolve-26).
3. `_verify_recommendation_metrics` returns 0 when the plan declares no parseable
   metrics (:282) — **open**, and `action_detail` is likewise unguarded at :356.

When auditing this harness, grep for early `return 0` on empty/zero-length input. That
is where the next one will be.
