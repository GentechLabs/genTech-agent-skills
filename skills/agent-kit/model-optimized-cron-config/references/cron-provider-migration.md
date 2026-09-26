# Cron Provider Migration — Config Drift

## The Problem

When the global inference config changes (provider and/or model), cron jobs that were created without explicit model/provider pins have the old global config baked in. On the next scheduled run, the drift detection guard blocks execution:

```
Skipped to prevent unintended spend: global inference config drifted
since this job was created (provider 'zai' -> 'nous'; model 'glm-4.7' -> 'deepseek/deepseek-v4-flash')
```

## The Manual Fix

Each job needs its model/provider pinned to the current config:

```bash
cronjob(action='update', job_id='abc123', model={'provider':'nous', 'model':'deepseek/deepseek-v4-flash'})
```

For 30 jobs, this takes ~15 minutes of manual cronjob calls.

## The Feature Request

Filed as Hermes Agent issue #61404:
- **Option A** — Auto-accept drift for null/null jobs
- **Option B (preferred)** — `cronjob action=sync-global` batch command
- **Option C** — Late binding at fire time

## Detection

Cron jobs with `last_status: error` and no explicit model/provider change are likely drift failures. Check with:

```bash
cronjob(action='list') | grep 'status.*error'
```

## Jobs Affected

All jobs where `provider` is pinned to a provider no longer in use. In the ZAI → Nous migration (Jul 2026), this was ~25 jobs including:

- Brain Backup
- Context Snapshot
- Build Queue Standup
- Revenue Monitor
- Hub Nightly Sync
- Sunday Review
- Social Media Engine
- Game Release Intelligence (both Jordan + Vanito)
- GitHub Contribution Crunch
- Hive Marketplace Monitor
- 5-Star Opportunity Scanner
- Gaming Hub Sync
- POE2 Build Health
- Rate Limit Monitor
- Vanito Music Sync
- Various [Vacation] paused jobs
- Daily Session Reset
- Cron Health Monitor
