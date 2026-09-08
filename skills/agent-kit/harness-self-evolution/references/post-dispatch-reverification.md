# Post-dispatch metric re-verification (`_reverify_published_metrics`)

Shipped evolve-39 to close the third recurrence (evolve-33, 35, 38) of the
**unreproducible-published-metric** class: a metric evaluated once mid-dispatch,
then invalidated by a later write to the same file, leaving a number published as
proof that returns something else when a human re-runs it.

## The failure it catches

evolve-38 published `METRIC: grep -c 'Cycle evolve-37' facts/harness-state.md -> 2 [PASS >= 2]`.
Live re-run: **0**. Cause — mtime ordering:

```
facts/recommendation.md   00:06:07.561   (plan written)
facts/.dispatch-state     00:06:07.600   (metric evaluated, value 2 true here)
facts/harness-state.md    00:06:07.808   (refresh-harness-state.sh rewrote it to evolve-38)
```

The receipt was true at evaluation and false at read time. A gate that counts
metrics but never re-reads them cannot see this.

## Working implementation

```bash
_reverify_published_metrics() {
    local cycle="${1:-${CYCLE_ID:-}}"
    local log_file="${2:-$EXECUTION_LOG}"
    [[ -n "$cycle" && -f "$log_file" ]] || return 0
    local row
    row="$(awk -v c="## ${cycle} " 'index($0,c)==1{f=1} f&&/^- detail:/{print;exit}' "$log_file")"
    [[ -n "$row" ]] || return 0
    local drift=0 pair expr published live op operand tag
    while IFS= read -r pair; do
        [[ -n "$pair" ]] || continue
        expr="${pair%$'\x01'*}"
        published="${pair##*$'\x01'}"
        tag="${published#*|}"; published="${published%%|*}"
        [[ "$published" == *[!0-9]* || -z "$published" ]] && continue
        live="$(cd "$HARNESS_DIR" && eval "$expr" 2>&1 | head -1)" || true
        [[ "$live" == "$published" ]] && continue
        op="$(printf '%s' "$tag" | grep -oE '(>=|<=|==|>|<)' | head -1)"
        operand="$(printf '%s' "$tag" | grep -oE '[0-9]+' | head -1)"
        if [[ -n "$op" && "$live" != *[!0-9]* && -n "$live" ]] \
            && _metric_compare "$live" "$op" "$operand"; then
            printf '<!-- METRIC SHIFT %s (%s): %s published %s, post-dispatch %s, criterion %s %s still holds -->\n' \
                "$cycle" "$(date -u +%FT%TZ)" "$expr" "$published" "$live" "$op" "$operand" >> "$log_file"
            log_warn "METRIC SHIFT ${cycle}: ${expr} ${published}->${live}, ${op} ${operand} still holds"
            continue
        fi
        printf '<!-- METRIC DRIFT %s (%s): %s published %s, post-dispatch %s -->\n' \
            "$cycle" "$(date -u +%FT%TZ)" "$expr" "$published" "$live" >> "$log_file"
        log_error "METRIC DRIFT ${cycle}: ${expr} published ${published}, post-dispatch ${live}"
        drift=1
    done < <(printf '%s\n' "$row" \
        | grep -oP 'METRIC: \K.*?\[[^]]*\]' \
        | sed -E 's/ -> ([0-9]+) \[([^]]*)\]$/\x01\1|\2/' \
        | grep -F "$(printf '\x01')")
    return $drift
}
```

Wiring — LAST statement of the evolve arm, after both refresh scripts:

```bash
if ! _reverify_published_metrics "${CYCLE_ID:-}"; then
    log_error "post-dispatch metric drift detected — see METRIC DRIFT comment in $EXECUTION_LOG"
    [[ $_ea_rc -eq 0 ]] && _ea_rc=1
fi
return $_ea_rc
```

## Parsing notes (each was a bug in the first draft)

- Capture the whole `METRIC: <expr> -> <val> [<tag>]` token including the bracketed
  tag; `grep -oP 'METRIC: \K.*?(?= \[)'` throws away the criterion you need.
- The detail field joins metrics with ` ; `, so a non-greedy match per token is required.
- `\x01` is used as an internal field separator because expressions legitimately
  contain `|`, `->`, quotes and spaces.
- Skip non-numeric published values rather than failing — the row can carry
  `[non-numeric FAIL]` tokens from the original gate.

## SHIFT vs DRIFT — why the distinction is load-bearing

First live firing was a **false positive**: metric `grep -c 'does not reproduce'
facts/execution-log.md` published `1`, post-dispatch `2`, because the evolve-39 row
(whose DETAIL contains the phrase) was appended to the very file being measured.
Criterion was `>= 1` and held throughout — the receipt was reproducible, the count
merely moved.

Rule: **fail only when the published pass criterion breaks.** A moved value under a
holding threshold is `METRIC SHIFT` (warning, rc=0). Without this split the gate
fails every cycle that measures its own log, and gets disabled — the worst outcome.

## Selftest case (h) shape

```bash
printf 'Cycle selftest-h\nCycle selftest-h\n' > "$measured"      # true at eval: 2
# write a fake row publishing "-> 2 [PASS >= 2]"
printf 'Cycle selftest-OTHER\n' > "$measured"                     # post-dispatch: 0
HARNESS_DIR="$TMP" _reverify_published_metrics "selftest-h" "$logf"
# expect rc!=0 AND grep -q 'METRIC DRIFT selftest-h' "$logf"
```
Pass both the cycle id and the log path as arguments so the case runs against
fixtures, never the real ledger.
