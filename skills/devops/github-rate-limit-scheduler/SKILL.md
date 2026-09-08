---
name: github-rate-limit-scheduler
description: Budget-aware GitHub operation scheduling. Use whenever GitHub work (repo create, fork, PR, search) needs pacing or quota checking. Works on the clean GentechLabs account (5000/hr).
---

# GitHub Rate-Limit Scheduler

## When to use
- Creating repos, opening PRs, forking, or searching GitHub API on ProtoJay4789
- Any GitHub work that 403s or exhausts quota
- Planning GitHub-dependent queue items

## The core facts (account is FLAGGED)
- Authenticated REST = **60 req/hr** (not the normal 5,000)
- GraphQL = **hard-capped 0/0** — never use `gh repo create`/`gh pr create` (GraphQL). Use REST: `curl -X POST https://api.github.com/user/repos` and raw git for pushes
- Forks via API = **403 blocked** — mark `needs_manual`, Jordan forks via web UI
- **git push/clone does NOT consume API quota** — brain backup, hub syncs, vault syncs run free

## The scheduler (V4)
- Script: `scripts/github_sync_scheduler.py` (cron `17 */1 * * *`, no_agent, silent when idle)
- State: `/root/.hermes/profiles/gentech/state/github_sync_state.json`
- Log: `/root/vaults/gentech/11-Mess Hall/github-sync-log.md`
- Ops: `repo_create`, `repo_check`, `pr_check`, `fork_attempt` (403 → `needs_manual`)
- Budget: min(3 per tick, remaining−4 buffer). Drains queue over successive hourly ticks
- Build-queue wiring: items with `github_op` + `github_repo` fields get auto-queued by `build_queue_tick.py` (`queue_github_ops`)

## How to queue new GitHub work
1. Add op to the scheduler state queue:
   ```python
   import sys; sys.path.insert(0, "/root/.hermes/profiles/gentech/scripts")
   from github_sync_scheduler import STATE_PATH, load_state, save_state
   s = load_state(); s["queue"].append({"kind":"repo_create","name":"x","description":"d"}); save_state(s)
   ```
2. Or tag a build-queue item with `github_op` + `github_repo` — the tick pushes it automatically

## Why accounts get FLAGGED (GitHub's own documented rules, Apr 2026 ToS)
GitHub flags an account for automated/inauthentic activity (Acceptable Use §4) and secondary rate-limit abuse. The NEW account (GentechLabs, 5000/hr) MUST NOT repeat what tripped ProtoJay4789:

**Dangerous automation patterns (what triggers a flag / secondary limit):**
- **Bulk content creation**: >80 content-generating requests/min, >500/hr (repos, releases, issues, PRs, comments). Repo churn is the #1 flag.
- **Concurrent requests**: >100 simultaneous REST+GraphQL. Our cron batches must serialize.
- **Per-endpoint bursts**: >900 points/min REST. A POST/PUT/DELETE costs 5 points; GET costs 1. Don't hammer one endpoint in a loop.
- **Automated starring/following, inauthentic activity, fake-engagement**: instantly flagged.
- **Secondary limit cooldown**: 403/429 → stop ALL calls, wait 24-72h, exponential backoff, then throw. Continuing = integration ban.
- **Excessive bandwidth**: don't store big files (videos, binaries) in repos — use git LFS or host on VPS.

**What's SAFE on the clean account:**
- git push/clone/pull (git protocol, NOT REST — never counted against API)
- Authenticated REST within 5000/hr, spaced, <100 concurrent, <900 pts/min
- Normal human-ish rhythm: don't create/fork dozens of repos in an hour

**Why ProtoJay4789 likely got flagged:** automated repo/fork churn + concurrent agent calls (multiple crons hitting REST in bursts) = "automated excessive bulk activity / rank abuse." The fix going forward: **gate ALL API write ops through the scheduler queue (1-3/tick, spaced), never fire ad-hoc.**

## Rules
- **ALWAYS run GitHub API work through the scheduler queue — never ad-hoc bursts** (this is what got the old account flagged)
- Never retry a fork via API — it's account-blocked, not transient
- Keep a 4-request safety buffer in quota checks
- Prefer git protocol for anything that moves bytes (push/clone/fetch)
- Search API is also restricted (422 spammy flag) — prefer direct `/repos/{owner}/{name}` calls
- Valid token lives at `secrets/github-token`; the env `GITHUB_TOKEN` was stale and must match it

## Verification
- `curl -s https://api.github.com/rate_limit` with token → check `resources.core.remaining`
- After any op: confirm via `curl -s https://api.github.com/repos/{owner}/{name}`
- Log shows every attempt with ✅/❌/🙋 status

## Pitfalls
- Do NOT update the token in `.env` without matching `secrets/github-token` — gh CLI compares them
- A 404 on `repos/{owner}/{name}` via unauthenticated curl is a red herring — always auth
- `gh repo create/fork` silently routes through GraphQL (0/0) — always REST + raw git
