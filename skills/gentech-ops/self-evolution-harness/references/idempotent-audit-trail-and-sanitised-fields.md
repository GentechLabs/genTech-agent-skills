# Idempotent audit trail + sanitised computed fields (evolve-24, Jul 31 2026)

Third consecutive cycle where a "computed field" fix broke the adjacent line.
The mechanism was the fault, not the content. Two root causes, two fixes.

## 1. Never paste raw internal DETAIL into a user-facing file

`scripts/refresh-harness-state.sh` substituted `sys.argv[2]` (the raw `- detail:`
line from execution-log.md) verbatim into the `- Change:` line of
`facts/harness-state.md`. Result: internal batch-job IDs and code spans leaked
into the file Jordan reads, and a false provider-migration claim survived three
cycles.

Fix — sanitise before substitution:

```python
det = re.sub(r'`[^`]*`', '', sys.argv[2])      # strip code spans
det = re.sub(r'\s+', ' ', det).strip()[:180]   # collapse whitespace + cap
body = ("- RECOMMENDED_ACTION: %s\n- Change: %s\n- Result: %s\n"
        % (sys.argv[1], det, sys.argv[3] or "ok"))
```

Verify: `grep -c '090e6c76e407' facts/harness-state.md` → 0, and the Change line
contains no backticks.

**Rule:** any value that flows from an internal log into a user-facing file gets
stripped, collapsed, and length-capped at the boundary. Don't fix the leaked
string — fix the pipe.

## 2. Make the execution-log append idempotent

`_append_execution_log()` was called unconditionally on every dispatch. Running
`evolve` more than once in a cycle (which happens routinely — re-run after a
fix) left phantom duplicate stubs: `grep -c '^## evolve-23'` returned **3**, two
of them with empty or half-written detail.

Fix — fingerprint on (cycle, action, detail), emit it as an HTML comment, and
skip on match:

```bash
local fp
fp="$(printf '%s|%s|%s' "$cycle" "$a_type" "$a_detail" | md5sum | cut -c1-12)"
if grep -q "^<!-- fp:${fp} -->$" "$EXECUTION_LOG" 2>/dev/null; then
    echo "execution-log: entry for ${cycle}/${a_type} already present, skipping"
    return 0
fi
{
    printf '<!-- fp:%s -->\n' "$fp"
    printf '\n## %s — %s\n' "$cycle" "$ts"
    ...
```

Do NOT key on the dispatch-state sequence number — field 3 of
`facts/.dispatch-state` is a per-arm counter, not a global sequence, so it
collides across arms.

Verify by running `bash scripts/execution-loop.sh evolve` twice; the second run
must print `already present, skipping` and the `^## evolve-N` count must stay 1.

## 3. A missing DETAIL field logs silently empty

`recommendation.md` written without a `DETAIL:` field parses to empty, and the
cycle logs `- detail:` with nothing after it — which then propagates into the
blank `- Change:` line in harness-state.md. The parser does not warn.

Always include a plain `DETAIL:` line (not a markdown heading) in
recommendation.md before running `evolve`. If a cycle already ran with it
missing, backfill both files and re-run `bash scripts/refresh-harness-state.sh`.

## 4. Shell-command shape when driving the harness through the agent

The command layer rejects long compound one-liners that chain `&&` with
`$(...)` substitution and multiple `grep -c` in a single line. Keep harness
commands simple and split them:

- one `bash -n` syntax check per call, or chained with plain `&&` only
- verification greps as a short list of bare `grep -c` invocations, not
  `echo "x=$(grep -c ...)"` interpolations
- heredocs (`python3 - <<'PY'`) work fine on their own line

This is a shape constraint, not a broken tool — restructure and it runs.
