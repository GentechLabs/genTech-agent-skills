# Unblocking `ABORTED: <verdict> <severity> unaddressed`

## Symptom

```
[ts] external feedback: verdict=DEGRADATION severity=critical
[ts] ✗ must_act=true — unaddressed critical critique
ABORTED: DEGRADATION critical unaddressed
```

`scripts/execution-loop.sh evolve` exits rc=2 before running any action. Nothing is
dispatched, no prediction is executed, the cycle is wasted.

## Cause

`read-external-feedback()` greps the LAST `- Verdict:`, `- Severity:` and `- Action:`
lines in `facts/critique-log.md`. It aborts when severity is `critical|high` AND the
last `- Action:` value is not literally `ADDRESSED`. Doing the fix on disk is not
enough — the guard reads the log, not the filesystem.

## Correct sequence (evolve-21, 2026-07-31)

1. Actually perform the counter-recommendation's remaining items.
2. Append a Resolution Entry to `facts/critique-log.md` **with all four guard fields**:

```markdown
## Resolution Entry — <ISO8601>
- Cycle: evolve-N
- Responds to: Critique Entry <timestamp> (<VERDICT> / <severity>)
- Verdict: RESOLVED
- Severity: low
- Action: ADDRESSED

### What was done
1. ...  (one numbered item per counter-recommendation bullet, including the
        ones deliberately NOT done and why)
```

3. Re-run `bash scripts/execution-loop.sh evolve` — the log line should now read
   `external feedback: verdict=RESOLVED severity=low` and the dispatch proceeds.

## Pitfall: do not blindly execute a stale counter-recommendation

The Critic writes counter-recommendations against the state at ITS run time, which can
be hours old. **Re-verify each bullet against live state first.**

evolve-21 example: the critique demanded repointing all four harness crons off
`ollama-cloud` because the Critic was dead on HTTP 429, and demanded deleting batch job
`090e6c76e407`. By the time Evolution ran, the weekly quota had reset — Critic's last
run was `ok`, all four crons were active, and `090e6c76e407` no longer existed in
`hermes cron list`. Executing the counter-recommendation would have changed the cost
and latency profile of four jobs for no reason.

Rule: for each counter-recommendation bullet, run the cheap read-only check first
(`hermes cron list | grep -A7 <job_id>`, `ls <path>`, `grep -n <pattern> <file>`), then
mark it DONE / NOT-APPLICABLE in the Resolution Entry. Both outcomes count as addressed.

## Pitfall: verify no cron depends on a tree before archiving it

Before `mv`-ing a split-brain / orphan harness tree:

```bash
hermes cron list | grep "Workdir" | sort | uniq -c
```

Only archive when the orphan path has zero rows. Log the move in `facts/cleanup-log.md`.
