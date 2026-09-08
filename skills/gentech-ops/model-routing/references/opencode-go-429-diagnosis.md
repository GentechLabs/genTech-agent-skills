# OpenCode Go Free-Tier 429 Diagnosis Pattern

**Class:** Cron jobs fail with HTTP 429, but interactive sessions work fine.

## Detection

```
HTTP 429: Free model capacity exhausted — retry shortly, or use a paid model 
(from $0.002/request). Message @bc1max on Telegram for help.
```

This means the OpenCode Go free tier for `deepseek-v4-flash` hit capacity. The paid tier (V4 Pro, Kimi, etc.) is unaffected.

## Differential Diagnosis

If interactive sessions work but cron jobs fail:

1. **Check model pinning:** `hermes config get model` shows session model → `cronjob list` shows cron models. If they differ, the user switched models interactively but `cron-provider-sync.py` hasn't run yet. Fix: `python3 /root/.hermes/profiles/gentech/scripts/cron-provider-sync.py`

2. **Check provider:** If session is on `opencode-go` but crons are on `nous` or `clawrouter`, same root cause. Sync fixes it.

3. **If models match but still 429:** The user is on the free tier. Switch to paid: `hermes config set model.default deepseek-v4-pro` then re-sync crons.

## Fix Sequence

```bash
# 1. Confirm session model
hermes config get model

# 2. Switch to paid model (if needed)
hermes config set model.default deepseek-v4-pro

# 3. Sync all 41 LLM cron jobs
python3 /root/.hermes/profiles/gentech/scripts/cron-provider-sync.py

# 4. Re-run any jobs that failed during the stale window
cronjob action=run job_id=<id>
```

## Observed Aug 9, 2026

Hub Nightly Sync, Revenue Monitor, and Harness Evolution all failed at 20:00 UTC with 429. Root cause: crons still pinned to `deepseek-v4-flash` (free) while Jordan's session was on `deepseek-v4-pro` (paid). The `cron-provider-sync` job only runs at 06:00 + 18:00 UTC — the switch happened between windows. Manual sync fixed all 41 jobs in one pass. Three re-runs confirmed green on V4 Pro.
