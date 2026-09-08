# Facts-Cleanup Pattern

## Problem

The harness accumulates stale state over time. Three common data-integrity issues:

1. **Stale harness-state.md** — the state file references an old cycle number, old cron job IDs, or old critique statuses. It falls behind the actual cycle because no one updates it.
2. **Missing prediction outcomes** — predictions pass their DUE date but no one records the verdict in `prediction-outcomes.md`. The Verifier and Critic then flag missing outcomes as a data-integrity issue.
3. **No git repository** — without `.git`, the Critic cannot use `git diff` for stagnation detection (measurement #1). The first cycle should initialize git.

## The Fix (evolve-11, Jul 28 2026)

Use action type `facts-cleanup` (not `update_script`) to address all three in one pass.

**Handler status (updated evolve-17, Jul 29 2026):** The `facts-cleanup` action now dispatches to `skill-automation.sh` which has a REAL handler. It updates:
- `harness-state.md` header to the current cycle
- The latest critique entry to the Critique Status section
- The Last Action section heading

**Known gap:** The handler does NOT update the Change/Result lines under the Last Action section. Those still show the previous cycle's detail text. After the dispatcher runs, you must manually fix the Last Action section text with a `patch` call. Example:
```
patch path=harness-state.md old_string="Change: <old text>" new_string="Change: <new text>"
```

**Also:** The handler does NOT commit to git. You must run `git add -A && git commit -m "evolve-N: <summary>"` manually after the dispatcher finishes.

### Step 1: Update harness-state.md
- Set "Last Action" to the current cycle
- Update any stale cron job IDs
- Mark the evolve-N critique as ADDRESSED
- Update the date in the header

### Step 2: Record prediction outcomes
For each past-due prediction in `predictions.md`:
1. Verify the metric with actual tool output
2. Write a CONFIRMED/FAILED/INCONCLUSIVE entry in `prediction-outcomes.md`
3. Include the metric result and a note explaining what happened

### Step 3: Initialize git
```bash
cd /root/.hermes/harness
git init
git add -A
git commit -m "harness baseline evolve-N"
```

Then after the execution loop runs:
```bash
git add -A
git commit -m "evolve-N: <summary of changes>"
```

## Verification

```bash
cd /root/.hermes/harness
# Metric 1: state file references current cycle
grep -c 'evolve-N' facts/harness-state.md
# Metric 2: prediction outcomes recorded
grep -c 'PREDICTION #M' facts/prediction-outcomes.md
# Metric 3: git baseline exists
git log --oneline | head -1 | grep -q 'harness baseline'
```

## When to Use

- After a Critic run flags stale state files (measurement #6)
- After a Critic run flags missing prediction outcomes
- After a Critic run flags no git repository
- When the action-type monoculture counter exceeds 3 (use `facts-cleanup` instead of another `update_script`)

## Action Type Diversity

The `facts-cleanup` action type is distinct from `update_script`. Use it to break monoculture streaks. The Critic tracks unique action types over 7 days and flags < 3 as CRITICAL.
