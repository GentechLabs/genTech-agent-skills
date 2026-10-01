# Operator Shape Directive

When the operator chooses a shape and split, the machine must hold that choice and escalate rather
than override. This reference describes the directive record, how it interacts with the efficiency
model, and how to verify it is working.

## Why it exists

The autonomous LP loop optimizes fee efficiency. A bid-ask near its junction reads low efficiency
(~25%) while a curve at the same spot reads high (~75%). If the operator deployed a bid-ask because
they expect a breakout and possible rejection, the efficiency model will want to flip the book to a
curve. Without a directive, the machine silently undoes the operator's call on its next cycle.

## Directive record

A durable record the re-centering loop reads before acting. Suggested path per tenant:

```
${PROFILE_DIR}/scripts/.operator-shape-directive.json
```

Fields:

| Field | Required | Meaning |
|---|---|---|
| `shape` | yes | `curve`, `bid-ask`, `spot`, or another supported shape |
| `split` | yes | Token/stable target as percentages, e.g. `{"token_pct": 50, "stable_pct": 50}` |
| `set_at` | yes | ISO-8601 timestamp when the operator issued it |
| `reason` | yes | One-line operator rationale |
| `escalate_if` | no | List of conditions that should surface for confirmation |
| `expires_at` | no | ISO-8601 timestamp; after this the machine resumes autonomous selection |
| `auto_clear_on` | no | Event that clears the directive, e.g. `{"regime_confirms": "bid-ask", "for_minutes": 30}` |

## Behaviour

1. **Read before every shape decision.** The re-centering loop checks for an active directive before
   selecting a shape from efficiency or regime.
2. **Hold the shape.** If the current on-chain shape matches the directive, no rebuild is triggered
   for efficiency reasons alone.
3. **Still report.** Efficiency, divergence, range status, and what the alternative shape would read
   are still reported — the operator needs to see the trade-off.
4. **Escalate on material conflict.** If an `escalate_if` condition is met, the loop pauses and
   surfaces a concise fork summary.
5. **Clear explicitly.** The directive persists until the operator clears it or an expiry/event fires.
   Never infer expiry from "the market moved."

## Verification

After setting a directive:

```bash
python3 fee_efficiency.py --tenant jordan
```

Expected output when the directive holds:

```
shape directive: bid-ask (50/50) — operator override active
fee efficiency: 24.5%  🟠 Watch
scenario: HOLD — operator directive holds bid-ask; curve would read 75% at same spot
```

If the output instead proposes a shape switch, the directive is not being read.

## Integration with the watchdog

The watchdog's re-center path should:
- Read `.operator-shape-directive.json` before computing the target shape.
- If active and current shape ≠ directive shape, rebuild to the directive shape once, then hold.
- If active and current shape = directive shape, skip efficiency-driven rebuilds and report
  `SHAPE OVERRIDE HELD`.
- If `escalate_if` conditions fire, pause and notify instead of rebuilding.

### Sync and execution path

The directive file is DATA the watchdog reads, so it must follow the same vault↔profile sync path as
the scripts. Add it to the sync manifest at creation time, run the sync twice when the manifest itself
changes (the first run may have already read the old manifest), and md5-verify the deployed copy
before trusting it. A directive that only exists in the vault is invisible to the cron; one that only
exists in the profile is erased by the next sync.

After deploying a directive, fire the watchdog once and inspect its stdout for the directive line. The
operator's instruction is not live until the running copy says so out loud.

### Materiality-reset hazard

A script that sets a "material" flag early and then resets it later in the same scope, with no
restoring path for the override, silently demotes the operator's condition. The restoring grep may
also be unable to see a branch that never produces the output it searches for (e.g. a cascade path
where the re-center never runs). If the directive is meant to bypass quiet-hours or debounce gates,
restore the flag explicitly after every reset, or decide materiality once at the very end using the
output that proves the condition fired.

## When NOT to use a directive

- Routine re-centering inside an approved shape (the normal re-center path handles this).
- A temporary market read you are not confident about (use the normal autonomous path).
- A shape you want the machine to try and then revert if inefficient (use a backtest or paper rule
  instead).

Use a directive when the operator has a specific thesis that the efficiency model cannot see: a
breakout, a rejection, a macro event, or a level that just retired.
