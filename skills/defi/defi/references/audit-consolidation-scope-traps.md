# Audit & Consolidation Scope Traps

Use when asked to audit cron jobs, health checks, sentinels, watchers, or any set of mechanisms
that share a name and might be declared "duplicates".

## The Trap

**Mechanisms that share a NAME often differ by SCOPE.** A consolidation decision made on a name
grep deletes coverage and calls it tidying. The most dangerous audit is the one that finds
"duplicates" that are not duplicates.

## Procedure

Before declaring two jobs/sentinels/watchers duplicates:

1. **Read each one's actual script.** The scope is usually explicit in the code (a `--profile`
   flag, a `--lanes` argument, a hardcoded list of directories, an `if self.name == ...` guard).
2. **Compare the DELIVERY target.** Two jobs with the same prompt that deliver to different groups
   are not duplicates — each wakes a different audience.
3. **Compare the DATA boundary.** One sentinel may scan this profile's jobs; another may scan the
   fleet. One watcher may report all lanes; another may report only its own lane by design.
4. **Check whether the script's own header explains why it is replicated.** A comment saying
   *"without this, four agents would each report the same thing"* is evidence of deliberate scope,
   not redundancy.
5. **Look at the schedule in context.** Two jobs firing every 15 minutes may be staggered on
   purpose (producer/consumer), or one may be the fleet superseder of a local job.
6. **For paused jobs, cluster by `paused_at` timestamp, exact to the minute.** A batch disabled in
   one second was one deliberate action. Record the batch, but do not invent the motive if it was
   not written down. Mark it `REASON UNRECOVERED` with an `ACTION NEEDED` flag rather than
   fabricating a plausible reason.

## Signs of Real Duplication

- Same script, same scope, same delivery target, no stagger.
- One is clearly a leftover local job superseded by a fleet standard.
- The script's header explicitly says it is being retired in favor of another.

## Signs of False Duplication

| Pattern | Meaning |
|---|---|
| Same script, different `--profile` / `--lanes` | Scope-deliberate, not duplicate |
| Same schedule, different `deliver` target | Audience-deliberate, not duplicate |
| Same name, one is `no_agent: true`, one is agent-prompt | Different execution models |
| One job's header says it prevents the other | Designed pair, not duplicate |
| Paused in the same minute as 3+ companions | One action, not independent jobs |

## Backfilling Missing Pause Reasons

When a job is paused with no reason recorded:

1. Read the `paused_at` timestamp.
2. Find all other paused jobs with the same timestamp (truncated to the minute).
3. Note the batch and each job's purpose.
4. Search the vault for the date and any mention of stand-down, pause, or notification-only.
5. State only what is proven: timestamp, batch, any proven consequence.
6. If the motive is not in the record, write `REASON UNRECOVERED` and add an explicit
   `ACTION NEEDED: decide keep-paused vs resume`.

**Never invent a plausible motive.** A fabricated reason is worse than an admitted gap because it
becomes the record.

## Proven Consequences Trump Inferences

A paused fee-history builder is a proven consequence: fees stop being collected. A paused action
job is an inference: we *think* the posture shifted to observation. Treat the first as fact and
the second as labelled speculation.
