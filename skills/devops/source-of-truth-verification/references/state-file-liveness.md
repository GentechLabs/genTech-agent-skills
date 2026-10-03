# State-File Liveness

A state file's name does not tell you whether it is live, stale, or orphaned. Two files with the same basename in different locations may disagree by orders of magnitude, and nothing in the filename records which one is authoritative.

## The hazard

- A file that *looks* dead may be written every minute by a cron prompt or an external service — its producer is unnameable from a simple `grep`.
- A file that *looks* live may be named by no script and no job definition — it is an orphan that something once wrote and no longer maintains.
- Two copies of the same state file (for example, a profile scripts directory and a synced vault) can diverge by 400× with no registry saying which copy wins.

A name-based audit will therefore reach wrong conclusions: it may delete evidence, chase a stale copy, or report a working job as broken.

## Liveness = producer + freshness

A state file is **LIVE** when a script or cron job names it AND it has been written recently.

A state file is **STALE** when a script or cron job names it but it has not been written recently.

A state file is **ORPHAN** when no script or job names it — regardless of mtime. A fresh orphan is worse than a stale live file, because it has no discoverable producer.

## The registry pattern

Build a small, read-only probe that reports, for every state file:

1. **Who names it** — every script that contains the basename.
2. **Which jobs name it** — every cron job definition that contains the basename.
3. **How fresh it is** — newest mtime across all copies.
4. **Whether copies agree** — same-named files in different locations, with size spread.

Run the probe before acting on a "dead file" claim. The output is the input to a decision, not the decision itself.

## What to do with the verdicts

| Verdict | Meaning | Action |
|---|---|---|
| LIVE | Producer exists, file is fresh | Nothing — the file is doing work. |
| STALE | Producer exists, file is old | Investigate the producer; the job may be stuck or retired. |
| ORPHAN | No producer found | Do not delete immediately. It may be evidence of a retired job, or produced by something outside the scanned code (external service, manual run, a prompt not in `jobs.json`). Determine the producer before removing. |
| DIVERGENT | Same basename, very different sizes | Authoritative copy must be decided and recorded. Until it is, any audit that picks one half of the pair is guessing. |

## Guard mode

`scripts/state-file-liveness.py` exits 1 when it finds orphans or divergent copies. This lets a cron job or CI step surface the condition without deleting anything.

Example invocation for a treasury seat:

```bash
python3 state-file-liveness.py \
  --state-dirs ~/.hermes/profiles/gentech-treasury/scripts \
                 ~/.hermes/profiles/gentech-treasury/state \
                 /root/vaults/gentech/scripts \
                 /root/vaults/gentech/10-Labs/agent-kit-self-tracking \
  --code-dirs ~/.hermes/profiles/gentech-treasury/scripts \
               /root/vaults/gentech/scripts \
               /root/vaults/gentech/10-Labs/agent-kit-self-tracking \
  --jobs-json ~/.hermes/profiles/gentech-treasury/cron/jobs.json
```

## Anti-patterns

- **Deleting "dead" files by name.** A dead file is often the only record that a job existed. Delete only after identifying the producer and confirming retirement.
- **Assuming the larger copy is authoritative.** Size is not authority. The authoritative copy is the one the producer writes to.
- **Treating mtime as proof of liveness.** A file can be fresh and unattributable (an orphan written by an external actor).
