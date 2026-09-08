---
name: source-of-truth-verification
description: "Before changing a running service or scoping a task, confirm you are looking at the artifact that actually runs and that the capabilities the task assumes actually exist. Covers locating live source via /proc, detecting stale mirrors, and verifying capability claims in queue items and specs."
version: 1.0.0
author: gentech
tags: [devops, verification, deployment, pre-flight, debugging]
---

# Source-of-Truth Verification

Two failure modes that both produce the same outcome — work that looks shipped
but changed nothing:

1. **You edited a stale mirror**, not the code that actually runs.
2. **You scoped off a capability claim** that turned out to be aspirational.

Both are cheap to prevent and expensive to discover late. Run these checks
before the first edit.

## When to Use

- Any change to a running service (API, gateway, daemon, worker)
- Any task scoped from a build queue item, spec, handoff, or prior session note
- Any time a task description says "config-only", "already supports X", "just
  needs a flag"
- When a fix you applied appears to have no effect in production
- When live behaviour disagrees with the code you're reading

## Part 1 — Find The Code That Actually Runs

A single service commonly has 3-5 copies on disk:

- `/root/vaults/<vault>/10-Labs/<svc>/` — vault working copy
- `/root/<user>.github.io/10-Labs/<svc>/` — portfolio mirror
- `/root/repos/<svc>/` — clone
- `/opt/<svc>/` — deploy copy

They drift. Only one is what systemd actually launched.

### The resolution sequence

```bash
# 1. Which process owns the port?
ps aux | grep -i "<port>\|<service-name>" | grep -v grep
# or
ss -lptn "sport = :<port>"

# 2. Ask the kernel where it runs from — authoritative
readlink /proc/<pid>/cwd

# 3. Confirm against the systemd unit
systemctl list-units --type=service | grep -i <name>
systemctl cat <service> | grep -E "WorkingDirectory|ExecStart"
```

`readlink /proc/<pid>/cwd` is the single most reliable command here. It reports
the real working directory of the live process regardless of how it was started,
what symlinks exist, or what the unit file claims.

### Cross-check before editing

Compare live behaviour against the file you're about to modify:

```bash
curl -s http://127.0.0.1:<port>/status | python3 -m json.tool
grep -c "<known-service-name>" <candidate-file>
```

A mismatch in counts, feature names, or version strings means you found a
mirror. Go back to step 2.

## Part 2 — Verify Capability Claims Before Scoping

Queue items, specs, and handoffs assert things like "config-only", "already
multi-chain", "just needs a flag flipped". **Treat every such claim as an
unverified assertion.** They are often aspirational — written when someone
intended to build it that way, or describing a design that was never finished.

```bash
grep -n "<the-thing-claimed-to-exist>" <source-file>
```

If the claim is false:

1. Say so plainly in the completion note — don't quietly paper over it
2. Then make it true
3. Only then mark the item shipped

Do **not** scope the task off the claim and mark it shipped. That produces a
queue that lies about what exists, which compounds — the next task scopes off
*your* note.

## Worked Example — x402 Gateway, Aug 4, 2026

Both failure modes fired in a single task.

### Stale mirror

| Check | Mirror (`ProtoJay4789.github.io/10-Labs/x402-gateway/`) | Live (`vaults/gentech/10-Labs/x402-gateway/`) |
|---|---|---|
| Services defined | 7 | 8 (adds `lineage_guard`) |
| `/status` health path | `f"{url}/health"` where `url` is a 3-tuple → always `down` | `route[0]` + `/v1/health` → correct |
| Reality | two revisions behind | what systemd runs |

`curl /status` on the live gateway returned 8 services all `ok`. The mirror
defined 7 and contained a bug that would have reported all backends `down`.
Editing the mirror would have produced a commit that changed nothing live, plus
a "fix" for a bug that no longer existed.

Resolved in one command:

```
readlink /proc/219465/cwd
→ /root/vaults/gentech/10-Labs/x402-gateway
```

### False capability claim

Build queue item #7 asserted:

> "Our x402 gateway already supports multi-chain — config-only for ALGO."

Actual code:

```python
"accepts": [
    {"scheme": "exact", "network": "eip155:8453", ...}   # single hardcoded entry
],
```

Hardcoded to one Base entry. The claim was aspirational. Scoping off it would
have produced a `shipped` item that shipped nothing. The honest path — state the
claim was false, build the real multi-network registry, then ship — took one
session and left the queue accurate.

## Pitfalls

- **`git log` on the mirror looks healthy.** A stale mirror can have recent
  commits (nightly sync jobs touch it) while still being behind on the file you
  care about. Recent commit activity is not evidence you found the live source.
- **The systemd unit file can also be stale.** `WorkingDirectory` may point at a
  path that was later moved, with the service still running from the old
  inode. `/proc/<pid>/cwd` reflects reality; the unit file reflects intent.
  When they disagree, trust `/proc` for *what is running* and fix the unit file
  before the next restart.
- **Restarting before confirming the source** loses the evidence. Once you
  `systemctl restart`, the new process picks up whatever the unit file points
  at. Read `/proc/<pid>/cwd` on the *currently running* process first.
- **A capability claim written by you last session is still a claim.** Notes
  degrade. Re-grep rather than trusting your own prior summary.
- **Don't fix bugs you find in the mirror.** If the mirror is stale, its bugs
  are usually already fixed upstream. Diff against the live copy before
  "fixing" anything you spot there.
- **Two live writers, one remote (verified Sep 4, 2026).** Stale data can come
  from TWO clones of the same repo both pushing successfully to `origin/main`.
  Each writer's pushes succeed, every job reports `ok`, but each clone only
  sees its own commits — data consumers see stale or missing work. When stale
  data has no obvious cause: list every clone of the repo on disk
  (`ls -d /root/*<repo>* /root/repos/*<repo>*`), map which cron jobs write to
  which, and check `git rev-list --left-right --count HEAD...origin/main` per
  clone. Nonzero left = stranded work; nonzero right = behind. A green cron
  status means "my push worked", not "the remote is current".
- **Webroot orphans are the inverse of mirrors (Sep 4, 2026).** A webroot file
  may have NO repo source at all — deployed straight into `/var/www/` and never
  committed. Overwriting it from a repo copy that merely shares the name
  clobbers the only copy: vanito.html's 87KB dashboard was replaced with an
  unrelated 20KB profile page and the original was unrecoverable (no git
  history, no Wayback snapshot). **Fingerprint before overwriting**: grep the
  webroot file for a unique asset path/content marker, compare size+hash with
  the candidate source. No true source → fix in place, then codify into the
  repo so the next deploy can't orphan it. Sep 4 sweep found 11 orphans
  (demo, portfolio, jordan, concept*, hub-backup, hub-launcher...).
- **Repo, webroot, and Pages copies of the same page can all be different
  generations** — `md5sum` all three before assuming any is in sync. The
  webroot being newer than the repo is normal after hand-fixes; the fix is
  back-porting to the repo, not re-deploying stale repo content over it.

## Support Files

- `scripts/find-live-source.sh` — re-runnable probe. `./find-live-source.sh <port>
  [candidate-file]` resolves the live source dir via `/proc/<pid>/cwd`, compares it
  against the systemd unit's `WorkingDirectory`, lists other copies on disk as
  potential mirrors, and exits 2 if the candidate file you're about to edit sits
  outside the live directory. Run this instead of hand-typing the sequence.

## Rule

Before the first edit to any running service:

1. `readlink /proc/<pid>/cwd` — find the real source
2. `curl` a live introspection endpoint — confirm the file matches reality
3. `grep` any capability the task assumes already exists

Three commands. They cost about thirty seconds and routinely save an entire
session's work from being written to a file nobody reads.
