# Computed Fields & Audit Integrity (evolve-22, 2026-07-31)

Three defects with one root cause: **a field that a human/agent is expected to hand-edit
will go stale.** Every recurring "state file is stale" critique is a missing computed field.

## 1. Compute the whole state header, not part of it

`scripts/refresh-next-events.sh` (added evolve-20) computed only the `## Next Events`
block. The header line and the `## Last Action — Cycle N` label stayed hand-edited, so
harness-state staleness recurred **5 times** and was each time declared "structurally
fixed". Partial automation is worse than none — it creates the appearance of a mechanism.

Fix (evolve-22): `scripts/refresh-harness-state.sh`

```bash
cyc="$(grep -oE 'Cycle evolve-[0-9]+' facts/recommendation.md | head -1 | grep -oE 'evolve-[0-9]+')"
[[ -n "$cyc" ]] || { echo "no cycle in recommendation.md — no-op"; exit 0; }
today="$(date -u +%F)"
sed -i "1s|.*|# Harness State — ${today} (Cycle ${cyc})|" facts/harness-state.md
sed -i "s|^## Last Action — Cycle evolve-[0-9]*.*|## Last Action — Cycle ${cyc} (${today})|" facts/harness-state.md
```

Wired into `execution-loop.sh` main() `evolve`, immediately after the
`refresh-next-events.sh` call, guarded by `[[ -f ... ]]`.

Rule of thumb: **if a critique names the same file stale twice, stop editing the file and
write the script that derives it.** Then enumerate *every* hand-edited field in that file,
not just the one that was flagged.

## 2. Never truncate the audit trail

`_append_execution_log()` wrote `"${a_detail:0:200}"`. The very first entry the new
mechanism produced was severed mid-token (`…/root/.hermes/har`). An audit trail that
truncates is an audit trail that lies. Removed the slice; backfilled the severed entry.

## 3. `_parse_field()` must read multi-line blocks

`DETAIL:` followed by a newline and an indented/numbered list parsed as **empty**, so the
execution log recorded `- detail:` with nothing after it. The original awk matched the
field line and printed only the same-line remainder.

```awk
!hit && tolower($0) ~ "^" tolower(name) ":" {
    sub(/^[^:]+:[ \t]*/, ""); sub(/[ \t]+$/, "")
    if (length($0)) { print; exit }
    hit = 1; next
}
hit {
    if ($0 ~ /^[A-Z_]+:/ || $0 ~ /^[ \t]*$/ || $0 ~ /^#/) exit
    sub(/^[ \t]+/, ""); sub(/[ \t]+$/, "")
    out = (out == "" ? $0 : out " " $0)
}
END { if (hit && out != "") print out }
```

Terminators: next ALLCAPS field, blank line, or a markdown heading. Test it in isolation
before committing:

```bash
RECOMMENDATION_FILE=facts/recommendation.md bash -c 'source /dev/stdin <<EOF
'"$(sed -n '151,171p' scripts/execution-loop.sh)"'
EOF
_parse_field DETAIL'
```

## 4. Verify the defect still exists before "fixing" it

The Critic's counter-recommendation was 3+ hours stale and described `pay=NO_ACCOUNT`
(gnome-keyring missing headless). Live re-probe found `pay=SKIP / pay_cli_not_installed`
— `which pay` returned nothing. The harness was about to install a keyring for a client
that no longer exists.

**Always re-probe the ground truth before executing a counter-recommendation that
describes external state.** Then rewrite the user-facing decision block to match reality —
a stale options list is worse than no options list, because the user acts on it.

## Verification (evolve-22)

```bash
head -1 facts/harness-state.md            # → # Harness State — <today> (Cycle evolve-22)
grep -n '## Last Action' facts/harness-state.md
grep -c 'a_detail:0:200' scripts/execution-loop.sh   # → 0
bash -n scripts/execution-loop.sh && bash -n scripts/refresh-harness-state.sh
```
