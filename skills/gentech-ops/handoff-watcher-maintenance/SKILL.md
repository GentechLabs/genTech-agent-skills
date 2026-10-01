---
name: handoff-watcher-maintenance
description: "Use when a watcher cron repeats alerts or nags."
version: "1.0.0"
---

> # ⛔ RETIRED 2026-09-30 — DO NOT RE-CREATE
>
> All four Handoff Watcher jobs are **disabled** (gentech `058ecaad8ca3`, gentech-treasury
> `066eb8c8024`, gizmo `577dce1eecdb`, pixel `dad3fbe6663a`). Jordan: *"yes good idea. it's in
> every group."* Full reasoning: `00-HQ/RETIRED-handoff-watcher-2026-09-30.md`.
>
> **Three structural defects, none fixable by tuning:**
>
> 1. **Its wake path could never succeed from cron.** Every firing read `📣 WOKE THE SEAT (0 sent)`
>    then `dm … timed out after 60 seconds`. `hermes peer dm` works fine from a shell and **times
>    out from cron context** — so the same handoffs were re-reported for days (39h, 55h, 31h).
>    **The cycling was the noise.** A watcher whose action cannot succeed is a nag with a receipt.
> 2. **It watched files that are not handoffs** — daily-generated `*-forge-tasks.md` flagged at 0h.
> 3. **Its truth check was a category error** — it diffed a point-in-time handoff against the LIVE
>    build queue and called time passing "a stale claim". It flagged a queue item that had shipped
>    20 minutes earlier. It fires on every completion, forever.
>
> **Replaced by nothing scheduled, deliberately.** The vault is the record, the mesh surfaces
> unopened notes, peer DMs work when an agent chooses to send one, and work state is answered by
> `10-Labs/build_queue_query.py` (pull, not push).
>
> **Before rebuilding:** ask what a nudge adds that the record does not already have. If you build
> one anyway, it MUST verify its own delivery and report failure AS failure — never a header
> claiming success above a body reporting zero sent.



Stateful no-agent cron scripts that report exceptions. One script per seat, same logic,
per-seat config.

## Rule 1 — One script, many seats. Never fork per seat.
A watcher copied per seat and edited per seat WILL diverge. Found 2026-09-17: four copies,
two designs (992-line vs 274-line), four md5s. HQ ran the one without noise control and
nagged the human for weeks; the workers had noise control but no detection.
**When you fix one seat's copy, propagate it to every seat in the same change.**

## Rule 2 — Eligibility and DISPLAY are separate. A cap gates display ONLY.
The bug that produced the actual complaint:
```python
shown = stuck[:MAX_PER_RUN]
alerted += [r for ... in shown]     # WRONG - only the shown ones get stamped
```
Run 1 shows 5 and stamps 5; run 2 shows the *next* 5. The cap **defers** the backlog
instead of suppressing it — visually identical to no dedup at all.
```python
eligible = []                        # stamp EVERYTHING past threshold + out of cooldown
for item in candidates:
    if cooled(item): continue
    eligible.append(item)
    ...                              # collect for display separately
shown = items[:MAX_PER_RUN]          # cap display only
```

## Rule 3 — Cooldown beats set-difference dedup.
`cur - prev` re-alerts whenever an item leaves the set and comes back (e.g. a reply note
gets archived, so the item re-enters the "no reply" set). Store `{rel: last_alerted_iso}`
and suppress while `now - last < RENAG_HOURS`. A new item alerts immediately; an old one
reminds daily, never every 15 minutes.

## Rule 4 — Lane scope every seat.
Without scope, N agents scan one vault and mail N copies of one fact. Each seat reports
only lanes it can act on; the coordination seat sees all.

## Rule 5 — Separate human lanes from agent transit.
A handoff moving between two agents is the system working, not news. Only two things earn
a human's attention: a NEW handoff addressed to a human, and something STUCK.

## Rule 6 — Age from the filename date, never mtime.
Git sync/commit/checkout re-touches every mtime. A `YYYY-MM-DD` filename prefix is the only
reliable "how long has this been open" signal. Midday-anchor it so same-day ≈ 12h.

## Rule 7 — Respect desktop seats' sleep.
A laptop that powers down overnight is not late. Measure age in *awake* hours inside
explicit availability windows, or you train the human to ignore the alert.

## Rule 8 — Cron has no script-args field.
You cannot pass `--own-lanes` from the job. Derive the seat from the script's own path:
```python
parts = os.path.dirname(os.path.abspath(__file__)).split(os.sep)
seat = parts[parts.index("profiles") + 1] if "profiles" in parts else "gentech"
```

## Rule 9 — Identical scripts are NOT identical seats. Audit the JOB CONFIG too.
Found 2026-09-18, after a fleet audit prompted by "gizmo's watcher doesn't look updated".
All four copies were byte-identical (same md5) — the propagation rule had been obeyed — yet
the seats behaved differently, because the drift had moved into the cron job config:
- **Cadence** — HQ ran `*/20`, every worker ran `*/15`. The seat that reports the most was the slowest.
- **Window** — one seat's hour range ended an hour early (`0-2` vs `0-3`).
- **A `display` string that contradicted its own `expr`** (`*/10` displayed, `*/20` actual) while the
  job NAME said a third number. Three values, one job.
- **A retired model** left on a `no_agent` job — harmless until the flag is flipped.
- **Names that lie** — `handoff-watcher-hourly` running every 15 minutes. This is what makes a human
  conclude a watcher "wasn't updated".
After any script fix, diff the JOB CONFIG across seats: expr, schedule.display, name, deliver,
model/provider, no_agent, enabled. Unify it in the same change, then read every job back.
`hermes cron doctor` reports NO issues on all of the above — it checks health, not sameness.

## Rule 10 — Separate "quiet because clear" from "quiet because blind".
A silent seat is not evidence of a working seat. To prove it, probe the script with a throwaway state
so the real cooldown state is untouched, then cross-check what it reported against what is actually in
the lanes:
```
python3 <seat>/scripts/handoff-watcher.py --state /tmp/probe-<seat>.json
ls /root/vaults/gentech/01-HANDOFFS/INBOX/<seat>/
```
A seat reporting zero FOR YOU while its INBOX holds items is broken; a seat reporting zero with an empty
INBOX is working. The `--state` trick also proves an alert fired without spending a cooldown stamp.

## Deploying a fix to all seats
1. Back up the existing script AND state file per seat (`*.bak-<change>-<stamp>`).
2. Copy the one good script to every seat's `scripts/`.
3. Reset the state file when the state schema changes.
4. Run each seat's copy directly — run 1 alerts, **run 2 must be silent**.
5. Run the real scheduled job (`hermes -p <seat> cron run <id>`) — `hermes cron run` by
   NAME fails; use the job **id**, and pass `-p <profile>` for non-default seats.

## Test harness pitfall
`exec(open(f).read())` has no `__file__` — seat auto-detection raises NameError. Use
`importlib.util.spec_from_file_location` when testing path-derived logic.

## Lane verifiability — a stuck item may be an unverifiable seat, not an ignored one
Found 2026-09-18: two handoffs to forge read as "stuck 4d" while forge was working. Its lane state
declared `lane_state_verifiable: false` — the desktop clone had diverged from the shared vault
(deleted 873, untracked 612, behind 1,260). Its resolutions landed in `_closed/` and never synced back.
Before escalating a stuck handoff, check the RECEIVER's lane state file. "No reply in lane" and "no reply"
are different findings, and only one of them is the other agent's fault. Never auto-delete the items to
clear the alert — the fix is a lane-reconciliation decision by the owning seat.
