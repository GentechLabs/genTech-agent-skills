---
name: one-way-sync-tree-discipline
description: "Use when editing files in a one-way sync tree."
version: 1.0.0
author: gentech
category: gentech-ops
tags: [sync, source-of-truth, vault, seat-copy, propagation, verification]
related_skills:
  - gentech-ops/git-repo-coordination
  - gentech-ops/fleet-rollout-verification
  - gentech-ops/deploy-and-verify
---

# One-Way Sync Tree Discipline

Use when a file is propagated from one upstream source to multiple downstream copies, and the
upstream is supposed to be the authority. The most common failure is not a merge conflict — it is
an edit made in the wrong direction, or a verification that compares a copy to itself.

## The rule

**Edit the upstream copy. Never edit a downstream copy.**

A downstream copy is a build artifact. The next sync overwrites it. An edit made only downstream is
destroyed with no trace and nobody notices until the symptom reappears.

## Procedure

### 1. Identify the upstream before touching anything

For GenTech vault scripts, the upstream is the vault copy under `/root/vaults/gentech/`.
`sync-treasury-scripts.sh` propagates `VAULT/10-Labs/agent-kit-self-tracking/` → `REPOS` +
`PROFILE` (treasury-only). It does **not** write seat copies back to the vault. Direction is one-way.

Verify the file you are about to edit:
```bash
readlink -f scripts/my-script.py | grep -q "^/root/vaults/gentech" && echo "OK: upstream copy" || echo "WRONG: downstream copy"
```

If the path does not start with the upstream root, stop. Find the upstream copy or ask the owner.
A downstream patch is always the wrong patch.

### 2. Commit only the paths you touched

A one-way sync tree is usually a shared working tree written by multiple agents. `git add -A`
stages every change in the tree — including another agent's in-flight work, logs, tests, and
money-path scripts — and commits them under your identity.

**Use named paths only.** If a wrapper exists that enforces this, use it:
```bash
python3 /root/.hermes/scripts/vault-commit.py -m "msg" -- scripts/my-script.py 01-HANDOFFS/gentech-to-x/my-note.md
```

Before committing, inspect the staged set:
```bash
git diff --cached --name-only
```
If it contains files you did not change, reset them.

### 3. Exclude money-path files from any automated sweep

Money-path files move capital, sign transactions, or control positions. A sweep that stages one
of them without review can commit a half-written state that signs a transaction. Automated
commit scripts must fail closed, not open:

```python
import json, subprocess
excl = ""
try:
    with open(f"{VAULT_DIR}/00-System/FILE-OWNERSHIP.json") as f:
        for p in json.load(f)["money_path"]["files"]:
            excl += f" ':(exclude)10-Labs/agent-kit-self-tracking/{p}'"
except Exception:
    excl = " ':(exclude)10-Labs/agent-kit-self-tracking/'"  # fail closed
subprocess.run(f"cd {VAULT_DIR} && git add -- .{excl} && git commit -m '{msg}'", shell=True)
```

Then print what was left unstaged. A sweep must never be silent.

### 4. Atomic replace when updating a live file

If the downstream copy is read by a running process (cron, watcher, service), plain `cp` is a
torn read — a reader can see a half-written file. Use write-temp + rename:

```bash
cp -p "$SRC" "$DST.tmp-$$" && mv -f "$DST.tmp-$$" "$DST"
```

Rename is atomic within a filesystem. A reader sees the old file or the new file, never a half.

### 5. Verify downstream against the upstream, not against itself

The green check must be load-bearing. The worst shape is a verify loop that includes the source
copy when the deployer never updates the source copy — it compares the source to itself and can
never fail.

Good verify loop:
```bash
TARGET=$(md5sum "$SRC" | cut -c1-10)
for s in gentech gentech-treasury gizmo pixel; do
  f="/root/.hermes/profiles/$s/scripts/my-script.py"
  m=$(md5sum "$f" | cut -c1-10)
  if [ "$m" = "$TARGET" ]; then printf "  %s ✅ %s\n" "$s" "$m"
  else printf "  %s ❌ %s (upstream %s)\n" "$s" "$m" "$TARGET"; DIVERGED=$((DIVERGED+1)); fi
done
[ "$DIVERGED" -gt 0 ] && exit 2
```

Key properties:
- `TARGET` is the upstream hash.
- Every downstream seat is compared to the upstream.
- A divergent seat is reported as a failure, not a warning.
- The script exits non-zero when divergence exists.

### 6. Test the negative control

A verification that cannot fail is decoration. Before trusting a fleet deployer, test it on a
scratch fleet where one seat is deliberately wrong or absent and prove it exits non-zero, naming
the failed seat. Then test the positive control (all uniform) and prove exit zero. If both
controls pass, the check is real.

### 7. After promotion, verify the upstream actually carries the skill — not just its name

Promoting a seat-only skill into the shared core is a one-way-sync move like any other: the
vault copy is now the authority and the seat copy becomes disposable. The promotion is not done
when the file lands in the core directory. It is done when:

- every file the skill references is also tracked in the core (`git ls-files` for SKILL.md **and**
  for `references/`, `templates/`, and `scripts/` files its body names);
- `git show HEAD:<path>` resolves and returns the new symbols for every referenced file;
- the fleet distributor (`fleet_skills_sync.py --check`) reports the skill as `would-add` or
  `updated` on the downstream seats, not absent and not a false conflict.

Run this check before archiving the seat copy:

```bash
SKILL=gentech-ops/one-way-sync-tree-discipline
V=/root/vaults/gentech/10-Labs/skills-distribution/$SKILL
S=/root/.hermes/profiles/gentech/skills/$SKILL

# 1. referenced files are tracked
git ls-files $V/SKILL.md | grep -q . || { echo "skill not tracked"; exit 1; }
grep -oE 'references/[^ ]+|templates/[^ ]+|scripts/[^ ]+' $V/SKILL.md | while read f; do
  git ls-files "$V/$f" | grep -q . || { echo "referenced file not tracked: $f"; exit 1; }
done

# 2. HEAD carries the new symbols
SYMBOLS=$(grep -c 'DERIVED copy' $V/SKILL.md)  # use a phrase the new content introduced
[ "$SYMBOLS" -gt 0 ] && echo "symbol present"

# 3. distributor sees it
timeout 120 python3 /root/vaults/gentech/00-System/agent-profiles/fleet_skills_sync.py --check
```

A skill whose template is uncommitted is a skill with a dangling reference: a seat rebuilding
from the repo gets instructions that point to a missing file. That is a half-promotion.

### 8. Check the shared tree is committable before claiming the change landed

In a multi-writer shared working tree, the file you edited may be fine while the tree itself is
blocked by someone else's unresolved conflict or stale stash pop. A commit failure here is not a
personal error — it is a fleet hazard. Run this before every commit on a shared tree:

```bash
git status --porcelain | grep -E '^(UU|AA|DD|AU|UA|DU|UD)' && {
  echo "BLOCKED: unmerged paths exist — no seat can commit until cleared"
  exit 1
} || echo "tree is committable"
```

If unmerged paths exist:

1. Confirm it is not an active merge: `test -f .git/MERGE_HEAD` — absence means a `git stash pop`
   conflict, not a real merge.
2. Identify the file: is it money-path-adjacent? Check `00-System/FILE-OWNERSHIP.json`.
3. If it is a peer's state file (wallet, position, credentials, ledger), do **not** choose between
   the conflicted values. Restore HEAD's committed bytes: `git checkout HEAD -- <path>`. This makes
   no content decision — it returns the file to the last committed state the whole fleet agreed on.
4. If the conflicted file is in your lane and the values are yours to reconcile, resolve with a
   temp-write + atomic rename.
5. After clearing, re-run the committable check and verify the file is valid (JSON parses, script
   syntax-checks, etc.).

A tree that cannot commit is a tree that cannot ship. Detect it before you report "done".

**Rescued from a seat copy (2026-09-28).** This section existed for a few minutes in exactly one seat
and nowhere else — `grep -c committable` across every commit that ever touched this skill returned 0.
It survived only because its author handed the text over instead of trusting the seat copy to persist;
the next `30 4 * * *` sync would have replaced that directory wholesale. That is this skill's own
lesson applied to the skill: **an edit that exists only downstream is scheduled for deletion.** It also
carries a second, larger point — sections 1-6 are edits going to the WRONG copy; this one is an edit
going to the RIGHT copy that still did not land, because the TREE was blocked. Measured the night it
was written: an unmerged `UU` on the steward wallet baseline (a stale stash pop) made *every* seat's
commit fail while that file sat invalid JSON.

## Pitfalls

### Seat-only skills survive silently instead of failing loudly

`fleet_skills_sync.py` reads the canonical core and copies outward. By design it **does not
delete skills that exist only in a profile**. The consequence is asymmetric:

- a seat-only **script** is scheduled for deletion — it gets noticed and usually destroyed;
- a seat-only **skill** is never propagated **and** never destroyed — it just never reaches the
  other seats.

The writing seat looks documented, but four of five seats cannot load the lesson, so the bug the
skill documents keeps happening elsewhere while everyone thinks it is covered. Treat a skill
that is only on disk as a skill that does not exist for the fleet.

### A seat-only skill promoted without its referenced files lands as a dangling reference

SKILL.md often names `references/`, `templates/`, or `scripts/` files. If any of those is left
uncommitted as foreign, a seat rebuilding from the repo gets a skill that points to a missing
file. The skill appears complete on the writer's seat because the seat copy still has the
untracked file. Verify referenced files before calling the promotion done.

### Editing the DERIVED copy because it is the one under `scripts/`

The vault copy and the seat copy share a filename and often differ only by minutes in mtime.
Nothing in an editor tells you which one git tracks. If you edit the derived copy:

- `git status` stays clean for that file, so it looks like the change was never made;
- the next sync overwrites your fix with the stale upstream, leaving **no trace**;
- and the derived copy is briefly AHEAD of the brain, so a restore silently reintroduces the bug.

Detect it before claiming the fix landed — the two checks are cheap and catch it cold:

```bash
V=<vault path>; S=<seat path>
cmp -s "$V" "$S" && echo same || echo "DIFFERENT — which one did I edit?"
git log --oneline -1 -- "$V"     # is the vault copy's last commit the one carrying my change?
git show HEAD:"$V" | grep -c '<a string I only just added>'
```

A green `git show HEAD:<file> | grep -c` of your own new symbol is the only proof the brain
carries the change. An edited file on disk is not evidence, and a seat copy that *runs* is not
evidence either — it is the copy that is scheduled for deletion.

**Seen:** a fix was made in the seat copy and reported as done; the vault copy was two commits
behind and still carried the bug, and another agent caught it and had to move the change into
the vault. Cost: a near-miss on a silent reintroduction, plus the reviewer's time.

### Downstream edits feel like success before they disappear

- **Downstream edit looks like it worked.** It applies immediately, runs, and may even pass tests —
  then the next sync silently reverts it. The destruction is delayed, so the edit feels successful.
- **`git add -A` in a shared vault.** Multiple agents share one git identity and one working tree.
  A sweep commits another agent's money-path edits under your name. Stage named paths only.
- **Verification that includes the source copy when the source copy is not a target.** If the
  deployer writes to seats A, B, C but verifies A, B, C, D, and D is the source it never updates,
  row D compares the source to itself and always passes. Remove D from the verify loop or make
  D a real target.
- **Plain `cp` for a file that a live process reads.** A torn read can crash the process or
  corrupt its state. Use atomic replace.
- **Silent sweep success.** If an exclusion script does not print what it left behind, you will
  not know when it starts excluding too much or too little.
- **'CONFLICT — differs from canonical' on an identical duplicate.** `fleet_skills_sync.py`
  reports duplicates as conflicts even when their contents match, because it keys on path or
  manifest identity rather than file hash. Do not assume the report means the duplicate holds
  seat-specific content. Compare hash and file set first; only keep the duplicate if it actually
  differs from canonical.

## Related

- `templates/fleet-script-deploy-verify.sh` — a starter deploy-and-verify script for propagating a
  single file to multiple seats and checking it against the upstream source.
