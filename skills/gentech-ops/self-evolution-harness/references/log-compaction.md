# Log Compaction (Gardener)

The Gardener compacts append-only fact/log files that have grown past 200 lines.
Convention: archive the head to `facts/.tmp/`, keep the last 100 lines, preserve
any doc header at the top of the kept tail, then append a dated entry to
`facts/cleanup-log.md`.

## Rule
Any file in `facts/` or `logs/` over 200 lines gets compacted. Files at or under
200 lines are left alone. Keep the last 100 lines; archive everything before that.

## Steps
1. **Inventory** — `wc -l` every `facts/*.md` and `facts/*.log`; flag files > 200.
2. **Identify doc headers** — files with a header block (e.g. `credential-health.log`
   has a `# Credential Health Log` + `## Format` block through line ~24; `execution-log.md`
   has a 3-line header; `prediction-outcomes.md` has a 2-line header). `critique-log.md`
   and `predictions.md` have no header to preserve.
3. **Archive head** — write lines `[0:-100]` to `facts/.tmp/<base>-archive-<ISO8601>.md`.
4. **Write compacted file** — keep the last 100 lines, prepending the preserved doc
   header if it isn't already inside the tail.
5. **Verify** — re-`wc -l` each file; confirm the header is intact at the top and the
   newest entries (e.g. `# Last verified:` lines in credential-health.log) survived.
6. **Record** — append a `## Cleanup Run — <ISO8601>` block to `facts/cleanup-log.md`
   listing files compacted (before -> after), archive names, total lines archived,
   dormant-skill count, and credential-probe status.

## Pitfall: header-preservation dedup can DROP a header
When prepending a preserved header, guard against duplication by checking whether the
header's last line is already inside the kept tail. **A blank line is a bad sentinel**:
if the header's final line is blank (e.g. `prediction-outcomes.md` header is
`# Prediction Outcomes` + a blank line), the "is it already in the tail?" check can
match the blank line and skip prepending the whole header — silently losing it.

Fix: key the dedup check on a **non-blank, unique header line** (e.g. the `# Title`
line), not the trailing blank. After compaction, always `head -3` the file to confirm
the title survived. In this run the `prediction-outcomes.md` title was dropped and had
to be restored with a `patch` after the fact.

## Pitfall: don't fabricate prediction outcomes during compaction
Compaction is bookkeeping, not adjudication. If `prediction-outcomes.md` has entries
with no recorded outcome, do NOT grade them during a Gardener run — the Verifier cron
adjudicates at each prediction's due epoch. Only append a dated deferral note if one is
needed. (See `backfill-missing-prediction-outcomes.md` for the Verifier's role.)
