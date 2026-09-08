# Pipeline Audit Methodology — Jul 3, 2026

## When to Use

Fee numbers are wrong, cron output doesn't match LFJ UI, and the cause isn't obvious. Instead of guessing, trace the entire pipeline end-to-end.

## The Method

### Step 1: Read every file in the pipeline path

For the fee system, the chain is:

```
lp-monitor-v2.py (no_agent cron)
    ↓ reads
defi-data.json (fees.dailyFees)
    ↑ written by
reader.mjs or manual update
    ↓ also reads
.lfj-aae-config.json (position amounts, range)
.lfj-position-tracker.json (entry price)
```

Read each file and trace what value flows where. The cron script says `daily_fees = dash_fees.get("dailyFees", 0)` — you need to know what `defi-data.json` actually has in that field.

### Step 2: Run the cron manually

Execute the script directly:
```bash
python3 /root/.hermes/profiles/gentech/scripts/lp-monitor-v2.py
```

Check its output against the LFJ UI. If the numbers don't match, the script is reading stale input or calculating incorrectly.

### Step 3: Verify the input file

Check what `defi-data.json` actually contains:
```bash
python3 -c "import json; d=json.load(open('/root/ProtoJay4789.github.io/DeFi/defi-data.json')); print(d.get('fees', {}))"
```

If `dailyFees` is stale (e.g. 0.204 vs 0.24 from LFJ UI), the pipeline is correct math on stale input. **The cron is not the problem.**

### Step 4: Audit with a reasoning model

When the trace is complex (3+ files, multiple calculation steps), use a strong reasoning model. Jordan specifies:
- **GLM 5.2** via `zai/glm-5` on BlockRun
- Feed the full source code of every script in the pipeline
- Feed the full content of every data file
- Ask: "Trace the calculation chain end-to-end. What value ends up where, and why doesn't it match the UI?"

The model will spot stale-input problems that look like logic bugs. In the Jul 3 audit, GLM 5.2 correctly identified that `0.204` was a static snapshot and the pipeline was executing correctly on stale input.

### Step 5: Fix root, not symptom

- **Symptom:** Cron shows $0.10 instead of $0.24
- **Wrong fix:** Change the proration formula in the cron
- **Root cause:** defi-data.json had stale dailyFees = 0.204
- **Right fix:** Calculate fees from a live source (position value × yield rate) and write back to defi-data.json

### Step 6: Make it self-healing

After fixing, add a write-back: the cron script should update `defi-data.json` with its calculated value so the next tick reads fresh data. This eliminates the "stale cache that never updates" pattern.

```python
# After calculating live_daily:
dash_data = load_json(DASHBOARD_DATA_PATH, {})
dash_data["fees"]["dailyFees"] = live_daily
save_json(DASHBOARD_DATA_PATH, dash_data)
```

### Step 7: Single-step repair

Change ONE thing → test → verify. If you change the cron, the config, AND defi-data.json simultaneously and the output is still wrong, you have N possible causes. Test each fix independently.

**Verification = run the script and check output.** If the output matches LFJ UI, the fix is confirmed. Don't assume — verify.

## Worked Example: Jul 3, 2026 Fee Discrepancy

1. **Observe:** Cron at 11:53 EDT shows Today: $0.1010, Year: $74.46. LFJ UI shows $0.24/day.
2. **Trace:** lp-monitor-v2.py reads `dailyFees` from defi-data.json → prorates by time of day.
3. **Check input:** defi-data.json has `dailyFees: 0.204`.
4. **Audit:** `0.204 * (11.88h / 24h) = $0.1010` ✅ Math correct. Input is the problem.
5. **Root cause:** defi-data.json dailyFees was a static snapshot, never refreshed. No live calculation.
6. **Fix:** Add yield-rate calculation to cron: `DAILY_YIELD_RATE = 0.00515; live_daily = lp_value * rate`
7. **Verify:** Cron at 12:02 shows Today: $0.1203, Year: $87.60. $0.24 * (12.03/24) = $0.1203 ✅
8. **Self-heal:** Cron now writes `dailyFees = 0.24` back to defi-data.json on every tick.

## Anti-Pattern: "It Must Be X"

When the user says "the cron is wrong," default answer is NOT to change the cron. First verify the cron is correct by reading its source and checking its inputs. The most common bug in the LP monitoring system is stale data in a cache file, not a logic error in the script.
