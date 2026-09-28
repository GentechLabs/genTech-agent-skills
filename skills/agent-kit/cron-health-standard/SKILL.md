---
name: cron-health-standard
description: "Fleet-wide standard for cron health: every job declares its INTENT, every ring ships a self-healing sentinel that retries once before it speaks, alerts ONCE per distinct problem and re-arms on success, and a monitor that cannot read its own job list reports UNKNOWN — never healthy."
tags: [cron, health, self-healing, intent, monitoring, debounce, agent-kit, fleet-standard]
trigger: "When creating, registering or auditing ANY cron job, in ANY profile — and whenever a cron job fails, goes quiet, repeats an alert, or someone asks 'is everything still running?'."
related_skills:
  - ../cron-truth-layer/SKILL.md          # verify data before acting; this verifies the JOB
  - ../verify-after-every-action/SKILL.md # a change is not done until it is re-read
  - ../../devops/cron-delivery-audit/SKILL.md
  - ../../devops/stateful-alert-monitoring/SKILL.md   # the debounce pattern, generalized
version: 2.0.0
author: Gentech
---

# Cron Health Standard (fleet-wide)

**Every cron job in every profile declares what it is FOR, is watched by a sentinel that reads
its recorded outcome, is retried once before anyone is woken up, and is reported ONCE per
distinct problem instead of once per run.** A job that fails silently is indistinguishable from
a job that never ran — and nobody finds out by being asked afterwards.

This is the generalization of the one-profile treasury sentinel. Measured before it existed:
**130 jobs across 4 profiles, and the health sentinel lived in ONE ring.** Every other ring had
exactly the blind spot the treasury had.

---

## The rules

### 1. DECLARE INTENT — every job says what it is FOR, machine-readably

**Rule: every cron job has a one-line `intent` resolvable by machine.** A failure is triaged
against *purpose*, never reported as an opaque error string. `last_error: "exit code 1"` tells a
human nothing; `INTENT: weekly country-adoption scan for the AVAX laggard thesis` tells them
whether to care at 3am.

**Where intent is recorded — the registry.** `/root/vaults/gentech/10-Labs/agent-kit-self-tracking/cron-intents.json`
(vault canonical; a copy ships next to the sentinel in each profile's `scripts/`):

```json
{ "by_id":     { "<job id>": { "intent": "…", "profile": "…", "source": "curated" } },
  "by_name":   [ { "profile": "*", "match": "^Wake ", "intent": "…" } ],
  "lookup_order": ["job.intent", "by_id[<id>].intent", "by_name[].match regex", "derived (flagged)"] }
```

**How a job's intent is looked up — deterministic order** (implemented in
`cron_health_fleet.py::intent_for`, do not invent a second scheme):

1. the job spec's own `intent` field, if a job ever carries one;
2. `by_id["<job id>"]` in the registry;
3. the first `by_name[]` rule whose `match` regex hits the job name (`profile` `*` or the job's own);
4. otherwise **derived from the job's own prompt** (`derive_intent`) and **flagged `DERIVED`** in
   every report, with a standing instruction to curate it.

**Curation is the job author's, at authoring time.** A derived intent is a starting point, never
a substitute. When you register a job, add its `by_id` entry in the same change — an intent that
is not written down is an intent nobody can triage against.

### 2. EVERY RING SHIPS A SENTINEL THAT READS, HEALS, THEN SPEAKS

**Rule: every profile's cron ring runs a health sentinel on a ~30-minute cadence.** In order:

1. **READ** every job's recorded outcome — `last_status`, `last_error`, `last_delivery_error`,
   `failure_streak`, `enabled`. These fields already exist; **a field nobody reads is not a
   monitor, it is a diary.**
2. **CLASSIFY** — apply self-exemption, then the paused-broken rule, then the healthy-silent rule
   before any heal or speak step. (See the sub-rules below for the exact ordering.)
3. **HEAL** — re-fire a failed **SCRIPT** job **once**, immediately. Most failures are transient
   (lagging RPC, rate limit, node timeout) and the retry clears them.
4. **SPEAK** only about what healing could not fix — and only once per distinct problem (rule 3).

#### The classification rules (applied in this order)

**PAUSED IS NOT RETIRED — a disabled job with a failure record is still a finding.**

`enabled: false` ends retries, not accountability. A paused job that left a `failure_streak`
behind it is a broken thing we stopped trying to fix. Report it as `PAUSED_BROKEN` with its intent
and last error, **unless** the pause carries an explicit, machine-readable reason that says it was
deliberately retired (`archived`, `deprecated`, `migrated`, `user_paused`).

Why: a sentinel that skips every disabled job cannot distinguish "we turned this off on purpose"
from "this thing broke, we hit pause, and now it rots silently." The latter is how a money cron
disappears for three days while everyone assumes it is healthy.

**Classification order, hard:**
1. `is_self()` — sentinel/health jobs: exempt, never report on itself.
2. `enabled == false`:
   - reason in `{"archived", "deprecated", "migrated", "user_paused"}` → **silent** (legitimate retirement);
   - any other reason or no reason, and `failure_streak > 0` or `last_status == "error"` → **PAUSED_BROKEN finding**;
   - otherwise → silent.
3. `last_status == "ok"` and no error → silent.
4. `heal` branch — retry once if script exists and idempotent.
5. Remaining unhealed failures → finding.

The PAUSED_BROKEN branch must run **before** the heal branch, so a paused job can never be
re-fired. A refactor that moves the `is_self()` or pause checks below the heal call re-introduces
the exact outage this ordering prevents. Pin the ordering with a test that asserts `is_self()` and
`PAUSED_BROKEN` return before the heal call site.

**Rule: every deliberate pause must declare its reason.** A pause with no reason is a bug report
waiting to happen. Write the reason into the job's metadata (`pause_reason`) or registry entry at
the same moment you pause it; a reason added afterwards is indistinguishable from a cover-up.

**Rule: a PAUSED_BROKEN finding uses the same debounce as any other finding.** It is not a special
class that re-alerts every tick; it alerts once, then stays silent until the condition changes or
the job is unpaused and fails again.

**Rule: HEAL BEFORE SPEAKING, and treat a silent successful retry as the ideal outcome.** The
fleet repaired itself and nobody was woken up for it. An alarm that fires on a transient blip
teaches the humans to ignore alarms.

**Rule: a ring heals only its OWN profile's jobs.** The ring that owns a job is the one that
re-fires it, so a money script is never double-fired by two rings seeing the same failure. A
wedged ring's jobs are still detected and reported by the others.

**Rule: register it as `no_agent: true` with `--quiet-unless-bad`.** Empty stdout delivers
nothing, so a healthy fleet is literally zero notifications. Silence means *nothing changed*.

**Rule: a sentinel must not grade its own report.** Exclude every health job from its own scan
(by name / id / script). A sentinel that exits non-zero when it finds a problem records *itself*
as a failed job, and the next run sees a permanent failure it can never heal — an alarm that can
never be cleared. The report states the exemptions it made.

**Rule: an agent-prompt job has no script and CANNOT be re-fired mechanically.** Report it as
`cannot retry: no script (agent-prompt job)`. Never print a retry that did not happen.

**Rule: idempotency is the job author's call, not the monitor's.** A job that must never be
double-fired (a partially-executed money action) sets `"heal": false` in its registry entry or
`heal: false` in its spec; the sentinel then reports `retry suppressed: job is marked
non-idempotent` instead of firing it. The sentinel exports `HERMES_HEAL=1` / `STEWARD_HEAL=1` on
every retry so a money script can behave conservatively when it knows it is a heal.

### 3. ALERT ONCE PER DISTINCT PROBLEM, RE-ARM ON SUCCESS

**Rule: a monitor that reports the same unresolved failure on every tick trains its reader to
ignore it.** At a 30-minute cadence that is 48 identical messages per day for one problem. The
sentinel is therefore **quiet by default even when something IS broken** — it speaks when the
problem is NEW, and then stops.

This is a first-class requirement of the standard, not an implementation detail:

- **DEDUP BY SIGNATURE.** The debounce state (`<state dir>/cron-health-fleet.json`, key
  `<profile>:<job id>`) records the failure signature already reported — the normalized error
  text plus the escalation bucket. Same signature next tick → **silent**, recorded, no message.
- **RE-ARM ON SUCCESS.** When a job is healthy again its entry is cleared, so the NEXT failure
  alerts again. *A problem that recurs after being fixed is news; one that never stopped is not.*
- **ESCALATION IS A CHANGE.** Re-alert when the streak crosses a threshold (3, 6, 12, 24, 48, 96),
  not on every increment.
- **THE DEBOUNCE MUST NOT BE ABLE TO HIDE A NEW PROBLEM.** Suppression is keyed per job id and
  signature: job B failing while job A is silenced alerts normally. Prove this two-directionally
  whenever you touch the logic.
- **ONE VOICE.** All four rings run the same scan and read the SAME state file, and all deliver to
  the same place (Gentech HQ). The first ring to observe a new problem claims it and speaks; the
  others find it claimed and stay silent. That is **one message per distinct problem, from a
  single destination, with four independent readers** — so one wedged scheduler cannot blind the
  fleet and cannot multiply the noise either. (If a ring ever genuinely needs its own lane, give
  it its own `--state` file and destination; do not let four rings each alert to four rooms.)
- **A RING RUNS ONE HEALTH SENTINEL, NOT TWO.** When the fleet sentinel lands in a ring that
  already had a local health job, SUPERSEDE the local one (pause it) — two sentinels for one
  problem is two voices, and the older one usually has no debounce. (Live example: the treasury's
  original 30-minute sentinel would have repeated one known failure 48 times a day; it was paused
  when this standard landed.)
- **THE DEBOUNCE STATE IS SHARED AND ATOMIC.** The state file is read-modify-written under
  `flock`; the claim is what makes "first one wins" true rather than racy.

### 4. QUIET HOURS APPLY TO THE SENTINEL TOO

**Rule: outside working hours, RECORD and HEAL — do not deliver.** A failure discovered at 04:00
is still read, still retried, still recorded in the state file; only the MESSAGE waits, and it is
flushed by the first run after the window (default `00:00–08:00 America/New_York`, override with
`HERMES_CRON_QUIET_HOURS` / `HERMES_CRON_QUIET_TZ`). Discipline is not an exemption from the
hours it is protecting: waking the founder at 04:00 for something the morning digest can carry is
the same noise failure as a repeated alert.

### 5. A MONITOR MUST BE ABLE TO SAY "I DO NOT KNOW"

**Rule: an unreadable job list reports UNKNOWN and exits non-zero — never healthy.** The two
states that must never look alike:

```
"nothing is wrong"   -> silence (exit 0)
"I could not tell"   -> SPEAKS, exit 2, and it speaks EVEN UNDER --quiet-unless-bad
```

This is the same trap as a failed `eth_call` reading as a real zero: a monitor blind to its own
blindness reports perfect health, which is worse than reporting nothing. **Silence doctrine
protects against noise from good news; it must never be used to hide blindness.**

Exit codes: `0` healthy, or nothing new · `1` a NEW/unresolved problem needs a human ·
`2` UNKNOWN.

### 6. REPORT A FAILURE WITH ITS INTENT AND ITS ERROR

**Rule: every failing job is reported as `name / id / profile / INTENT / failure_streak /
last_error`** — plus one line saying what the retry did or why none was possible. Name alone is a
page with no information; intent is what makes it triageable by whoever reads it.

### 7. SAFETY — A MONITOR NEVER MOVES MONEY, AND YOU NEVER TEST ON LIVE MONEY

- A health script performs exactly one action: the read-only retry of a job's own script.
  It never reads keys, never signs, never invents a money action.
- **Never prove the heal path by re-firing a real money job.** Build a throwaway job — a script
  that exits 1 the first run and 0 afterwards, off a state file, in a scratch dir — and prove the
  heal on that.
- Registering a job in a profile's own `cron/jobs.json` is expected. Nothing else in another
  profile is in scope.

### 8. WHERE IT LIVES (paths are part of the standard)

| Thing | Path |
|---|---|
| Fleet sentinel tool (canonical) | `/root/vaults/gentech/10-Labs/agent-kit-self-tracking/cron_health_fleet.py` |
| `no_agent` wrapper registered per ring | `…/agent-kit-self-tracking/cron-health-fleet.sh` |
| INTENT registry (canonical) | `…/agent-kit-self-tracking/cron-intents.json` |
| **Debounce state (shared by all rings)** | `/root/.hermes/state/cron-health-fleet.json` |
| Deployed copies (a cron `--script` must resolve inside the profile) | `/root/.hermes/profiles/<profile>/scripts/` |
| Sync manifest (vault → repos + profile, md5-verified) | `…/agent-kit-self-tracking/sync-treasury-scripts.sh` |
| Per-ring sentinel job | `Fleet Cron Health Sentinel (self-healing, 30m)`, `*/30 * * * *`, `no_agent: true`, deliver → Gentech HQ |
| Nightly fleet-wide record | `/root/.hermes/scripts/nightly-maintenance.py` → `00-System/nightly-reports/` |
| **HQ escalation path** | `/root/vaults/gentech/01-HANDOFFS/gentech-treasury-to-gentech/<date>.md` (append-only) + a dated line in `gentech-treasury-completions.md` |

---

## Operating it

```bash
# the cron invocation (what the registered job runs)
python3 /root/.hermes/profiles/<profile>/scripts/cron_health_fleet.py --heal --quiet-unless-bad

# right now, would it heal anything? (never delivers)
python3 …/cron_health_fleet.py --heal --dry-run

# what is failing and why it is currently quiet
python3 …/cron_health_fleet.py --show-silenced --no-quiet-hours

# the whole fleet, machine-readable
python3 …/cron_health_fleet.py --json

# one ring only
python3 …/cron_health_fleet.py --profiles gentech-treasury

# after adding jobs: seed intents for anything unrecorded (curated entries are never overwritten)
python3 …/cron_health_fleet.py --emit-intents

# make the next run speak again about a known problem (ops)
python3 …/cron_health_fleet.py --no-debounce          # once
python3 …/cron_health_fleet.py --reset-state          # forget everything
```

## Anti-patterns (each one cost real time)

- **Repeating an unresolved failure on every tick** — 48 messages a day for one problem, and the
  founder learns to ignore the channel. Alert once per distinct problem; re-arm on success.
- **A monitor whose output nobody reads** is a diary. Read `last_status`/`last_error` or do not
  claim to monitor.
- **Exiting non-zero on an alert without self-exemption** → the sentinel becomes the permanent
  failure it can never heal (live example: the treasury sentinel flagged an agent-prompt job,
  exited 1, and was itself the next failing job with `failure_streak=1`).
- **Reporting a retry that could not happen** on an agent-prompt job — say `no script`.
- **Treating "I could not read the list" as healthy** — the blindness failure this standard exists
  to prevent.
- **Letting the debounce state be per-ring while four rings alert** — you get 4 different rooms
  reporting the same problem, each of which then goes quiet on its own. One state, one voice.
- **A new file not in the sync manifest** never reaches the executed copy; it looks written and
  does nothing. Enrol the tool, the wrapper and the registry together, then verify md5.
- **Skipping disabled jobs blindly** — `enabled: false` hides both deliberate retirement AND a
  broken job we paused in panic. Distinguish them by `pause_reason`; report the latter as
  `PAUSED_BROKEN`.
- **Moving the classification checks below the heal call** — a refactor that reorders `is_self()`
  or `PAUSED_BROKEN` after `heal()` can re-fire a paused or non-idempotent money job. Pin the
  ordering with a test that targets the heal **call site**, not the function definition.
