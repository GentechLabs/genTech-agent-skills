---
name: destructive-write-guards
description: "Use when automating an overwrite, sync, prune or cleanup."
version: 1.0.0
tags: [guards, data-loss, sync, idempotency, verification]
---

# Destructive Write Guards

Automations that replace, prune, or overwrite content are the ones that lose data silently. They
report success while destroying something, because a blind replace that produces the intended result
for the files it *knows about* looks identical to one that also removed what it did not.

Applies to: content sync to multiple targets, nightly maintenance/prune scripts, cache and artifact
cleanup, deploy overwrites, any `rmtree` + `copy` propagation.

## Rules

**1. Put the guard on every path that performs the operation — find them by grepping the OPERATION,
not the helper name.** A helper that does the work and an inline loop that does the same work are
two independent paths. A guard added inside the helper never runs on the inline path.

```bash
grep -n 'rmtree\|os.remove\|unlink\|shutil.move\|\bcopy\b' <file>   # the paths, not the function
grep -n 'def .*sync\|def .*prune\|def .*clean' <file>               # the tempting-but-wrong grep
```

**2. A guard must compare WHAT IS THERE against WHAT WILL BE THERE, not merely that they differ.**
Any replace of a differing artifact destroys the difference — and the difference may be the whole
point of the local copy. Compute the set of content that exists only on the receiving side and would
be lost, and name it.

**3. Warn, do not block — unless blocking is the stated intent.** For propagation (source of truth →
replicas) the source must win or drift accumulates. The fix is a loss that cannot be missed, not a
frozen pipeline. If you do block, say so explicitly and provide the override, or the next operator
disables the guard entirely to get unstuck.

**4. Never decorate a return value that other code MATCHES ON.** If a caller does
`if result in ('a', 'b')`, returning `'a (detail: N)'` matches nothing — the item silently drops out
of the caller's list while looking handled. Keep matched tokens byte-exact; report detail on a side
channel (log line, separate field). This is the guard hiding the item it warns about.

**5. Drive the REAL entry point in the test.** A test that calls the guarded helper is circular — it
exercises the code you wrote, not the code that runs. Call the same top-level function production
calls, with paths pointed at a throwaway tree, and assert the guard fires there.

**6. Make the scope injectable.** A check whose root/paths are hardcoded cannot be tested without
touching the thing it checks. Read the target from an env var or parameter, defaulting to production.

**7. Never mutate the thing under test.** Plant defects in a scratch copy, never in the live artifact.
A run killed between plant and restore leaves the mutation in production with nobody watching. Add a
startup restore-check that strips any test marker it finds — that is the only recovery for a run that
already died mid-window.

**8. Prove it can go BOTH ways.** Positive cases (real risk detected and named) and negative cases
(identical input, receiver merely behind, absent receiver, `__pycache__`/dotfile noise → clean), plus a
control proving the warning can stay silent. A guard that only ever fires is as useless as one that
never does, and only the negative cases catch a false positive that will get the guard disabled.

**9. When a rule exists to prevent a loss, verify the loss is DETECTED — not merely that the rule is
written down.** Ask which check would go red for this specific loss. If the answer is "none", the
missing artifact is the detection.

**10. An artifact that must NEVER be rewritten needs a STRUCTURAL refusal, not a conditional skip.**
Some subjects are legitimately excluded from an automated repair — human-authored marketing copy, a
contract, anything whose wording is a judgement rather than derived data. Excluding them by skipping
a check *inside* the repair is a behavioural guard, and it is one refactor away from being bypassed:
the next pattern someone adds runs before that skip. Return from the repair function **before any
pattern executes** when the subject is excluded, so no future pattern can reach it at all.

Prove it the way you would prove any other loss is impossible: run the REAL repair entry point over
the excluded subject and assert **byte-identity of the artifact** AND that **no backup file was
written** (a backup appearing is proof the write path was entered). Asserting only "the content looks
right" passes on a run that entered the path and happened to write identical bytes.

The inverse also holds: a repair must not be the only thing policing the excluded subject. Give it a
separate RED-only check anchored to that subject's own source, and **print what was excluded** — an
exemption that is silent gets read as coverage.

## The tell that you have one of these bugs

- A count that goes **DOWN** right after you added something.
- A report of **"0 changes" / "nothing to do"** immediately after you edited the source.
- Two audits reporting **clean** over a window in which content demonstrably disappeared.

All three mean: re-read the artifact, do not trust the summary.

## Auditing an existing overwrite path

1. `grep` every destructive call — list the paths that actually act.
2. Diff one receiver against the source and list what exists only on the receiver. If it is non-empty,
   that content is one sync away from gone.
3. Check whether any current audit compares receiver-vs-source, receiver-vs-receiver, and
   upstream-vs-receiver. Map which losses each one can and cannot see (table in the reference file).
4. Add the guard to every acting path, then prove it with the real entry point.

## Automated git commits: the sweep boundary + argv fall-through class

A script that calls `git add` and `git push` on a schedule is a destructive sync whose "receiving
side" is the same repository it is reading from. The damage is not loss to disk — it is attribution
corruption, silent cross-lane commits, and a production run triggered by `--help`. Apply every rule
above plus the following four.

**11. Add an allow-list argv dispatch before any step that can write or commit.** A maintenance script
with no argument guard treats `--help`, a typo, an editor's syntax check, and a CI health probe as
identical to "run the full job and push". Dispatch on `sys.argv` explicitly:
- `--help` / `-h` print usage and touch nothing;
- `--dry-run` exercises every step but skips commit and push;
- `--selftest` runs the built-in guard test;
- anything else exits `64` (`EX_USAGE`) with a loud `REFUSING unknown argument(s)` and zero side
effects.

Add `--dry-run` as a first-class citizen, because the only reason anyone reached for `--help` was
that there was no safe way to observe the script's behaviour. The mechanism: argv parsing is not a
user-experience nicety; it is the gate between "observing the tool" and "modifying the source of
truth."

**12. Replace the deny-list boundary with an ownership allow-list.** `git add -A` stages every
dirty file in the tree. A deny-list that excludes `Treasury/**` and `11-Mess Hall/**` can only block
paths the author already knows about; the next ledger, the next lane, the next seat artifact will
pass straight through. Build an `OWNED_GLOBS` list from what the script and its subprocesses actually
write, then stage **only** those globs. Every other path is skipped by default. Fail-closed on an
empty ownership set (stage nothing rather than "fall back to all").

The allow-list must be evidence-based — grep the script for `open(..., 'w')`, `shutil.move`,
`subprocess.run(..., output file)`, and any spawned helper that writes. A guessed list is a deny-list
with fewer entries.

**13. Treat `git add` pathspecs as a second attack surface, not syntax sugar.** Two traps turn a
seemingly correct allow-list into a silent pass:
- `git add -- . <globs>` **unions** `.` with the globs. The allow-list becomes decorative and the
  fee-ledger is staged again. Pass the globs alone: `git add -- <globs>`.
- A glob that matches nothing makes `git add` abort the whole invocation (`fatal: pathspec ... did
  not match any files`). That fails safe, but a sweeper that quietly stops sweeping is its own
  outage. Filter the globs to the ones that actually match, print the dropped globs in the report,
  and add a regression check that asserts a non-matching glob does not kill the sweep.

**14. Selftest must falsify every defect class, and the failures must be RED.** A green selftest
that only runs the correct code proves the happy path, not the guard. Mutate the production script
in a scratch copy and assert each of these goes red:
- restore a leading `.` in the `git add` invocation → a non-owned ledger is staged;
- re-add the ledger to the owned list → it is staged;
- neuter the argv guard → an unknown flag runs the job instead of exiting EX_USAGE.

After each red run, restore the correct copy and confirm green again. A guard that cannot be
provoked into a red result is not a guard.

**15. Prove the real entry point on the real source of truth with `--dry-run` before declaring the
fix shipped.** Running a helper in a fixture repo is necessary but not sufficient. The live tree has
state, dirty files from other agents, submodules, and edge cases no fixture replays. Run the script
with `--dry-run` against the actual vault, read the `Would stage:` list, and assert the unwanted
paths are absent. Only then commit.

**16. A destructive git command dressed as a reconcile is still a destructive write.**
`git reset --hard <remote>/<branch>`, `git checkout --theirs -- .`, and `git push --force` all replace
local content with something else. On a multi-writer tree they are subject to the same guard rules as
`rm -rf` + `cp`:

- **Verify the premise before agreeing.** "It's just a re-hash" or "the remote is source of truth"
  must be proven, not assumed. A divergence number says branches differ; it does not say the local
  side is empty.
- **Measure the unique side.** Run `git cherry <remote>/<branch> HEAD~n..HEAD` and count `+` (unique
  local commits with no remote equivalent). Any `+` means a reset deletes real commits.
- **Name the files that would vanish.** `git diff --name-status HEAD <remote>/<branch> | awk '$1=="D"'`
  lists files in local HEAD but not on the remote; if any exist on disk, a reset removes them.
- **Check whether live processes read those files from this tree.** A file read by a running script or
  systemd unit is not merely uncommitted work — removing it changes live behaviour.
- **Refuse as written when the local side holds anything unique.** The safe reconcile is a normal
  merge (merge base exists) or a documented manual recovery, not a reset.

A reset is correct only when the local side holds nothing unique. Treat every other case as data loss
until proven otherwise.

**17. Before refusing an all-or-nothing write, check whether the tool can be SCOPED — "apply versus
decline" is often a false binary.** A refusal to run a fleet-wide replace is usually the right instinct and
the wrong conclusion, because the decision has three outcomes, not two: apply, decline, or **apply scoped to
the carrier**. Refusing without looking for a scope flag hands the operator a choice between two bad options
when a third was on the command line the whole time. Measured 2026-10-01: a fleet skills sync was declined on
solid grounds — its seat-only-content guard WARNS rather than BLOCKS, so an apply would destroy seat-only
files in every lane — and *the same tool* offered `--only <relpath>` and printed its own advice to "apply in
review-sized slices with `--only`". Run scoped, it delivered one corrected skill to all four seats with a
blast radius of ONE skill, and the 79 seat-only files in the neighbouring seat were untouched.

```bash
<tool> --check                                        # what it WOULD do, and to what
<tool> --help | grep -iE "only|scope|path|filter"     # is the blast radius injectable?
```

- **The refusal and the scope are not in tension.** Declining an unscoped replace is correct; declining to
  LOOK for the scope is what turns it into a false binary.
- **A tool that advises "apply in slices" is telling you it expects to be scoped.** Read its own output
  before concluding it has no safe mode.
- **Small blast radius is not small verification.** Re-check every destination afterwards: the scoped run
  touched four, and the count of changes it reported was the number of DESTINATIONS, not of edits.

## References

- `references/seat-sync-clobber.md` — the multi-target sync case in depth: why three audits all read
  green across a real loss, the controlled experiment that attributes a disappearance to a program
  rather than a person, and the recovery procedure.
- `references/git-sweep-boundary.md` — automated git-sweep scripts: argv fall-through, deny-list vs
  allow-list ownership boundaries, `git add` pathspec traps, and a falsification recipe for the
  selftest.

## Naming a mechanism you do not need puts it in reach on the day it is harmful

Measured 2026-09-28. A safe offer was drafted as *"force-push only the backup ref, never main."* The operation was
**already a fast-forward** (`git merge-base --is-ancestor <ref> HEAD` returned 0), so `--force` was never required —
yet the plan said the word. The reviewer's correction is the rule:

> **A plan that says *force* invites a reader to reach for `--force` on the day it is NOT a fast-forward — which is
> exactly the day forcing would destroy work.**

**Write the guard as a QUESTION THE GRAPH ANSWERS, not as a capability you might use.** Ask
`git merge-base --is-ancestor <remote-ref> HEAD`; treat non-zero as **STOP and alarm**, never as "escalate to
force." A fast-forward check is decidable before the operation and cannot be deferred, so there is no case in which
the fallback is needed.

**Two corollaries:**
- **A destructive capability named in a plan is a loaded gun in the reader's hands.** If `--force` is not required,
  do not put the flag in the sentence, the variable, or the comment. Silent, footgun-shaped words are how a safe
  procedure becomes an unsafe one two maintainers later.
- **The alarm branch must RETURN NON-ZERO.** This guard's whole value is that a STOPPED state is loud: exit 1 on
  refusal, exit 0 on every quiet outcome (up-to-date / too-soon / deferred / pushed). Verify the exit code **without a
  pipe** — `cmd | sed` reports `sed`'s status, so a refusal can look like success to the scheduler that reads it.

### A declared guard that is never READ is not a guard — and the one that works may have no name

Measured 2026-09-28: a script declared `NEVER_TOUCH = "main"` with a comment calling it
"non-negotiable" — and **referenced it zero times.** The protection that actually held was a
hardcoded refspec on the push line. **The thing that had the name did nothing; the thing that did
the work had no name** — and two agents auditing it initially read the named guard as the
enforcement. This is the destructive-write variant of the same defect, and it is worse here:
a destructive guard that is inert reads as a refusal that will never come.

- **Grep the guard's own identifier and count the reads.** One occurrence (its own assignment) is
  the alarm. A declaration plus a comment is indistinguishable, to a reviewer, from enforcement.
- **Make the named guard read the string the action actually uses**, and order it
  build → validate → use. **Assert the ORDER in a test, not the presence.** A guard called after
  the action is decoration, and one called on a different string than the action uses is theatre.
- **Prove it FIRES, with the case that matters most: the target rewritten to the forbidden value
  while the variable still reads the permitted one.** A guard that only reads the declaration
  passes the obvious tests and fails exactly there. Asserting the guard *exists* is the same
  mistake one level down.
- **When retiring a dangerous word: remove it from the SURFACE, keep the reason.** Rename the flag
  (`--force-run` -> `--now`) so it cannot be reached; leave the docstring explaining the
  withdrawal. **Assert against the CLI surface (argparse), never the whole file** — a check that
  forbids its own explanation pressures the next editor to delete the doctrine.

### The danger is a by-product being read as a state

Verified 2026-09-28: a divergence detector inferred "forked" from the **push rejection**. When the
write gate defers, git is never invoked, so **no rejection is ever observed** and a permanently
diverged branch fell through to "retry next tick" — a permanent condition reported as a wait, and
the detection was gone in the same hour the fix shipped. **Never derive a state from the by-product
of an operation you are allowed to skip.** Ask the source of truth directly
(`git merge-base --is-ancestor`), because that question cannot be skipped.

### A LIST'S LENGTH IS NOT EVIDENCE OF THE DEFECT — check what else adds to it

Measured 2026-09-28: an exclusion list holding a genuine bug (a bare folder name that failed to match nested
copies) was 63 entries long, and the length was reported as "the defect's fingerprint". **It was not.** Only **5 of
the 54 nested entries** existed because a name failed; the other **49 were auto-discovered caches** the client would
enumerate regardless. **The list's length mostly measured cache discovery, not the failure.**

- **Before using a size as evidence of a cause, enumerate the entry origins.** If most entries come from a
  different process, the size is that process's readout.
- **A number that grows for reasons unrelated to your finding is not a fingerprint of it** — and it will grow
  tomorrow too, so it cannot distinguish fixed from unfixed.
- **The real fingerprint is the SCAFFOLDING: a name and its own enumeration in the same list.** `node_modules`
  appearing bare AND as three paths is a fix left visible, specific to the failure in a way a count is not.
- **Corollary for guards: count the entries that MATCH something.** A bare top-level name can only exclude a
  top-level folder — so a bare name for a folder that no longer exists **excludes nothing while having the exact
  form of one that works.** An auditor cannot tell the live guards from the dead ones by looking.
- **Separate the failure modes of a name-based rule** rather than calling them all "wrong": (1) matches a folder but
  not its nested copies — a LEAK; (2) names a folder that no longer exists — a NO-OP that looks like protection;
  (3) correct. **Only (1) leaks; only (2) needs deleting; and only a match test separates them.**

### An acquittal is only as good as the UNIT it was computed in

Measured 2026-09-28: a source folder was acquitted of carrying sync payload because its files are unsupported
classes — **while the server's own table held two entries for it, both FOLDERS, both zero bytes.** The structure
synced and no file content did. **Class filters drop FILES; they do not drop FOLDERS.**

- **"It carries nothing" retires an investigation that should stay open.** The bytes claim was true and the shape
  claim was never made — **the second is what a folder-exclusion failure leaks through.**
- **Verify an acquittal at the CLASS level, not the instance level:** walk every instance of the excluded pattern
  and count the ones a match test misses. Here: 688 directories, 0 leaks — a class check that passed.
- **Two fields can answer confidently in the wrong unit at the same time** — a disk size given a transfer universe,
  and a file-class filter given a folder-structure question.

### The five rungs of a guard claim — and only the last one is sufficient

A guard can be satisfied at five levels, each strictly weaker than the one below. A green test at any rung tells
you nothing about the rungs beneath it. Measured on one function (`assert_target_safe`, 2026-09-28), which passed
the first three and could not fire at all:

| rung | the claim | how it fails |
|---|---|---|
| 1 | the guard **exists** | it can be inert — declared and referenced zero times |
| 2 | the guard **is read** | it can read the wrong thing — a refspec *derived from* the input instead of the input |
| 3 | the guard **is ordered** before the dangerous action | it can sit after an earlier `return` that always fires first |
| 4 | the guard **is reachable** | it can be reachable only by hand-editing the subject |
| 5 | the guard **fires on a case a test can invoke** | **this is the only sufficient rung** |

**Rung 3 is the trap, because it looks like proof.** The test asserted the guard's call preceded the push, and it
**passed on the broken code** — the order was true and the reachability was false. **Order is about where a call
sits; reachability is about whether control arrives.**

**Two further rules that fall out of this:**

- **An assertion that a value is IN A SET does not assert WHICH branch produced it.** The negative control checked
  the status was in `(STOPPED_NOT_FAST_FORWARD|STOPPED_UNSAFE_REFSPEC|MAIN_WINS_SLOT)` — so a *different* refusal
  satisfied it while the guard never ran. Assert the **exact** status, and assert the guard's **own reason string**
  is present.
- **A guard's conditions must be able to VARY.** If the checked value is derived from the input by the same line
  that builds the thing being checked, the comparison is a tautology (`name != ref` where `ref` built the refspec;
  `name not in dest` where `dest = "refs/heads/" + name`). Check the **input**, not a value derived from it.

**The only proof is the negative control at rung 5: revert the fix in a scratch copy and watch the new cases go
red while the old ones stay green.** That difference — new cases failing, order case passing — is the defect made
visible.

### Grepping the whole file matches PROSE — strip comments and docstrings before a source-inspection test

A test that greps a source file for a pattern will match the **docstring explaining the defect it is checking
for**. Two assertions false-failed this way on the same day: a line-number check read the FF status from the
comment describing the previous version, and a flag check matched the retired flag's story in the header.

**A pattern that matches text is not a check on code.** Extract code only — parse with `ast`, drop every docstring
and comment, grep the result — and if the extraction yields nothing, **fall back to the raw file and say so** rather
than passing on an empty subject. Same family as a `*.log` glob, an `--author` field, and a `name in dest`
tautology: **the unit of the check decides what the check can see.**
