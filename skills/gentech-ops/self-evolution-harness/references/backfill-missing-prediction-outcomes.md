# Backfill Missing Prediction Outcomes

When the Verifier cron is too slow to check 1-cycle predictions, or when predictions were never recorded, the Evolution agent must backfill outcomes itself.

## When to Backfill

- The Critic flags "prediction outcomes going unrecorded" for predictions past their DUE date
- `prediction-outcomes.md` has entries for recent predictions but older ones are missing
- The Verifier's schedule is too infrequent (e.g., every 2 days) to catch 1-cycle predictions

## How to Verify Each Prediction

Each prediction in `predictions.md` has a `METRIC` field — a shell command that returns true/false. Run it to determine the verdict.

### Common verification patterns

**Build queue changes:**
```bash
jq '.items | length' /root/vaults/gentech/scripts/build_queue.json
jq '.summary.blocked' /root/vaults/gentech/scripts/build_queue.json
```

**Credential health probes:**
```bash
grep -c '^\[2026-07-26' /root/.hermes/profiles/gentech/harness/facts/credential-health.log
grep 'pay=' /root/.hermes/profiles/gentech/harness/facts/credential-health.log | tail -1
grep 'q402=' /root/.hermes/profiles/gentech/harness/facts/credential-health.log | tail -1
```

**Script changes:**
```bash
grep -c 'hermes-harness' /root/.hermes/profiles/gentech/harness/scripts/*.sh
bash /root/.hermes/profiles/gentech/harness/scripts/credential-health.sh 2>&1 | grep -q 'FATAL'
```

**Git state:**
```bash
cd /root/.hermes/profiles/gentech/harness && git log --oneline | head -3
```

## Outcome Format

Append to `prediction-outcomes.md`:

```
## PREDICTION #N — <ISO8601>
VERDICT: CONFIRMED | FAILED | INCONCLUSIVE
METRIC: <the metric command> → PASS/FAIL (<actual result>)
NOTE: <one sentence explaining the evidence>
```

## Real-World Example (evolve-12)

Predictions #1-#5 were past-due for 2+ days. Each was verified:

| # | Metric | Result |
|---|--------|--------|
| 1 | build_queue blocked=0 | PASS (blocked=0) |
| 2 | credential-health.log has Jul 26 entries | PASS (8 entries) |
| 3 | no hermes-harness refs, FORMAT_OK in log | PASS (all 0, FORMAT_OK) |
| 4 | pay= in last 3 log lines | PASS (pay=NO_ACCOUNT) |
| 5 | q402= with valid status | PASS (q402=PAY_OK) |

All 5 were CONFIRMED. The backfill closed the oldest data gap in the harness.
