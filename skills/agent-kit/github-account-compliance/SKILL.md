---
name: github-account-compliance
description: "Use BEFORE any GitHub API write (repo create, PATCH, fork, PR, comment, delete) or any burst of API reads. Hard STOP rules that keep our GitHub account un-flagged. Load this whenever GitHub work is about to happen."
version: 1.0.0
author: Gentech
tags: [github, api, compliance, rate-limit, flagging, safety]
---

# GitHub Account Compliance — the hard rules

**Load this before ANY GitHub API work.** These are not guidelines. Violating them risks the
whole account (repos, Pages, hackathon submissions, portfolio) going dark.

## ⚠️ The budget is TINY: **60 requests/hour** (verified 2026-09-16)

```
x-ratelimit-limit: 60     # authenticated — NOT the 5,000 our older docs assumed
```

**One unspaced burst of ~40 writes eats two thirds of an entire hour.** Do not trust the
"5,000/hr" figure you may find in older notes — measure it (`check_quota("core")`).

**A rate-limited 403 can surface to unauthenticated callers as a 404** — which looks exactly like
a deleted/flagged account and will send you chasing the wrong problem. If you see 404 on
web/API *while `git ls-remote` still works*, suspect **rate limiting first**, wait for the
reset window, then re-check with ONE call. Do not diagnose a flag from 404s alone.


## 🛑 The STOP rules (absolute)

1. **403 / 429 = STOP. Immediately.**
   Stop every API call. Do not retry. Do not "just check one more thing". Do not switch to curl
   to see if it works better. Retrying through a block is **the** documented way accounts get flagged.
   Report what you were doing, then wait for the next cycle (or the reset time).

2. **No bursts. Ever.**
   Space **every write 3+ seconds apart**. No loops that fire N writes back-to-back. A tight burst of
   ~40 writes is what tripped our account on 2026-09-16.

3. **No ad-hoc repo creation. No mass forking.**
   Repo churn is GitHub's #1 flag trigger. Repo creation goes through the scheduler
   (`github-rate-limit-scheduler`) or an explicit Jordan decision — never improvised mid-task.

4. **Hard cap: ~30 API calls per task** (unless a written cap in the task says otherwise).
   Note the count when you're done. If the task needs more, batch/cache it or split it across cycles.

5. **Use the shared helper — never raw `gh api` in a loop.**
   **`/root/.hermes/profiles/gentech/scripts/github_api.py`** — authenticated REST, 1h response cache, quota guard, spam-flag detection.
   *(Give the absolute path: a bare `scripts/github_api.py` resolves differently from different cwds, and
   there is a stale second copy under `~/.hermes/profiles/*/home/.config/` — see the trap below.)*
   Raw `gh api` bypasses the cache and the guard.

6. **git for bytes, web for scanning.**
   `git push/pull/clone/fetch` costs **zero** API quota. Reading `github.com` pages via `web_extract`
   costs **zero** API calls. Move data with git; read with the web — not the API.

7. **Never touch the GraphQL / search quotas casually.**
   GraphQL is a separate tiny budget (`gh repo create`, `gh pr create` use it). Search burns the
   secondary limit fast. Use REST and the helper instead.

## Pre-flight checklist (run this in your head before the first call)

- [ ] Am I about to make **more than ~5 writes**? → slow down to 3s spacing, or queue them.
- [ ] Am I **creating a repo / forking**? → STOP, route via the scheduler, not ad-hoc.
- [ ] Am I **in a loop**? → it must be capped, cached, and spaced.
- [ ] Have I checked quota? → `check_quota("core")` from `github_api.py`.
- [ ] If I get a 403/429 → **stop and report**. No retries.

## Why these exist (the mechanism)

GitHub flags accounts for automated/inauthentic activity and secondary rate-limit abuse
(Acceptable Use §4). The triggers:

- **Bulk content creation**: >80 content-generating requests/min, >500/hr (repos, releases,
  issues, PRs, comments). Repo churn is the #1 flag.
- **Concurrent requests**: >100 simultaneous REST+GraphQL.
- **Per-endpoint bursts**: >900 points/min (a POST/PUT/DELETE costs 5 points; GET costs 1).
- **Secondary-limit cooldown**: 403/429 → stop ALL calls. Continuing = integration ban.

When an account is flagged it can return **404 on web + API while `git ls-remote` still works**,
and stored tokens read as **invalid**. That's the signature — the repos are fine, the account is
hidden. The fix is owner-only (unflag appeal), cannot be done by an agent.

## Case study — 2026-09-16 (why this skill exists)

While "improving the GitHub profile", an agent fired ~40 unspaced API writes, **created a repo
ad-hoc**, hit the rate limit, and **kept probing** — then the account went 404 on web+API.
Every one of the four STOP rules was broken. Full write-up:
`00-HQ/incident-github-account-404-2026-09-16.md`.

**The lesson is not "be careful." It's: these rules must be in front of you at the moment of action.**
That is why this skill is loaded on GitHub work rather than filed in a handoff somewhere.

## A "200" on your own content proves nothing about public visibility

**An authenticated call shows the OWNER's view — and the owner always sees their own flagged/hidden
account.** So "I called the API with our token and got 200" is not evidence the account is publicly
healthy; it is the *expected* behaviour of a hidden one.

**Rule:** for any PUBLIC-visibility question (is our repo/issue/profile visible to outsiders?), measure
**logged out**, or with a second account. Authenticated results may be reported only as
"visible-to-owner", never as "public".

Symptom this explains: anon `404` on every artifact we author, while controls (someone else's repo) return
`200` in the same batch, and auth `200` on our own. That split is *content-scoped*, not caller-scoped — so
it is not rate limiting, which is applied to the caller and returns `403`, not `404`.

## Stale credential files — test the LIVE one, or you will call a valid credential "invalid"

**⚠️ This is a FLEET pattern, not a GitHub one. Two instances in one week.**

Before concluding ANY credential is dead, **enumerate every copy on the box and test each one**:

```bash
find / -name "hosts.yml" -o -name "*composio*key*" -o -name "*.env" 2>/dev/null | head
```

Then test each candidate against a cheap authenticated endpoint and report **which path** you tested.

| Instance | Live copy | Stale copy | Symptom of reading the stale one |
|---|---|---|---|
| GitHub (2026-09-18) | `~/.config/gh/hosts.yml` | `~/.hermes/profiles/<p>/home/.config/gh/hosts.yml` (Aug 31) | declared a working token "invalid" → wrote it into an incident note |
| Composio (2026-09-19) | `COMPOSIO_API_KEY` in the profile `.env` (`ak_`, 23 ch) | `/root/composio-key.txt` (`COMPOSIO…`, 40 ch) | 401 `Invalid API key` → declared Drive blocked (it was live) |

**Never generalise from one file to "the credential".** A dead token and a restricted/hidden account
look identical from outside — so testing the wrong file manufactures a problem that does not exist, while
the real one stays available.

### GitHub-specific detail

There is a **live** credential file and at least one **stale** copy:

- LIVE: `~/.config/gh/hosts.yml`
- STALE: `~/.hermes/profiles/<profile>/home/.config/gh/hosts.yml` (older; silently `401`s)

Reading the stale one produced a false "our token has been invalidated" conclusion that went into an
incident note. **Before concluding a credential is dead:**

1. List every candidate file (`find` for `hosts.yml`) and compare mtimes.
2. Test each one against `GET /user` (`200` + the expected `login` = alive).
3. Report which path was tested. Never generalise from one file to "the token".

Note the direction of the risk: a dead token and a hidden account look similar from outside. Testing the
wrong file manufactures a credential problem that does not exist — which is why this belongs in the
pre-flight, next to the quota check.

## A dead `secrets/github-token` shadows the live `gh` credential — and `check_quota` hides it

`scripts/github_api.py` resolves its token from `${PROFILE_DIR}/secrets/github-token` **before** falling back to
`gh auth token`. Those two credentials can **diverge** (measured 2026-09-18: secrets file → **401 Bad credentials**,
live `gh` token → **200 `GentechLabs`**), and then every `gh_get` / `check_quota` call fails 401 while `gh api`
works perfectly.

**The trap:** `check_quota("core")` reports **`0/0`** when the token is rejected — it reads as *"quota exhausted"*,
not *"bad credential"*, so a blocked script looks like a rate limit.

**Rule:** when the helper 401s but `gh api user` returns our login, the helper's **credential is stale** — the API
is fine. Test each credential's file with its own `GET /user` call; never generalise from one source. (This is the
reverse direction of the Aug-2 case, where `gh` reported the token invalid while the secrets file still worked.)
Fix by replacing the file's contents — `pr-submission-rules` → `references/token-death-recovery.md`.

## The fleet WRITE gate — every `git push` is paced

`/root/.hermes/scripts/github-write-gate.py`, enforced by `.git/hooks/pre-push` in the vault
repo. One writer at a time, 25 s minimum spacing, **20 writes per rolling hour** across ALL
profiles (state: `/root/.hermes/state/github-write-gate.json`, shared box-wide — the risk is
the ACCOUNT's total write shape, not one profile's).

- Check `status` before a push you care about: it prints `remaining` / `used_last_hour`.
- On saturation it prints `GITHUB-GATE: deferred (push) — budget saturated, retry next tick`
  and exits 3. **That is the gate working, not an error.**
- A caller is only held `MAX_WAIT_S = 120 s`; longer and it defers rather than blocking a
  cron forever. A retry therefore succeeds once the OLDEST write in the window has aged
  enough for the computed wait to drop under 120 s — read the oldest `ts` from the state
  file and retry at `oldest + 3600 - 120`.
- **Do NOT set `GITHUB_GATE_BYPASS=1` for convenience.** Unpaced pushes are the lane that
  got the account flagged; a saturated budget is usually our own agents pushing, and
  bypassing recreates exactly the burst shape being prevented. Emergencies only — and say
  so in the log.
- **A deferred push loses no work** — the commit is safe on disk; only the push waits.
- A rejected push when local is AHEAD and nothing is incoming is usually this gate, NOT a
  conflict. Check `status` before assuming a rebase is needed.

## See also
- `devops/github-rate-limit-scheduler` — the budget-aware scheduler that owns repo_create/fork/PR ops
- `github/github-api-helper` — the helper's API surface and wiring pattern
