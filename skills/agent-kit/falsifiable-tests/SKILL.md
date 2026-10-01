---
name: falsifiable-tests
description: "Use when writing or debugging a test, guard, or assertion."
trigger: "Writing a new test or assertion, adding a regression guard, or when a test FAILS and you are about to change the code it covers."
tags: [testing, verification, assertions, false-red, harness]
version: 1.0.0
author: Gentech
---

# Falsifiable Tests

A test earns its place by being able to go RED for the right reason and GREEN for the right reason.
**A test that fails on CORRECT code costs as much as one that passes on broken code** — it sends you
to "fix" something that was never wrong, and it teaches the reader to distrust the whole suite.

Every rule below was hit while verifying a guard that was already correct.

**First reflex when a new test fails: suspect the ASSERTION, not the code.** Especially on a guard you
just wrote and reasoned about carefully — read the assertion again before touching the implementation.

## Compare like with like — a DEFINITION is not an INVOCATION

Ordering assertions are the most common false-red. A `def`, signature, or module-level constant sits
where it was **written**, not where it **runs**.

```python
# WRONG — _gas_precondition is a `def` near the top of the file. It sorts before main() regardless of
# runtime order, so this measures nothing and FAILS on a correctly-placed guard.
assert src.index("acquire_lock()") < src.index("def _gas_precondition")

# RIGHT — compare against the first statement that actually EXECUTES after the guard.
# (start the search AFTER the guard, or you may match an earlier unrelated call)
assert src.index("acquire_lock()") < src.index("subprocess.run(", src.index("acquire_lock()"))
```

A definition site says where code was **written**; only a call site says when it **runs**.

This applies to every source-order assertion: import-before-use, guard-before-side-effect,
config-before-read, lock-before-sign. **Grep for the CALL form, not the declaration form** — and
search from the right offset so you measure the intended occurrence.

### A MENTION is prose — and writing documentation can turn your own guard red

The same trap one step further out: a **comment or docstring that merely names the label** sits earlier
in the file than the code that emits it, so a bare-substring anchor matches the prose.

Measured: `src.find("[4a] PROVISION GAS")` matched a docstring at char 20,500 while the real `print(`
sat at 111,742 — an ORDERING assertion went red while the execution order was untouched. Worse, the
person who wrote that docstring was the person who had just changed the code, which is exactly when you
are least likely to suspect the test.

**The tell: your two operands are one MENTION site and one call site.**

- **Anchor on the statement that EMITS the label**, not on the label:
  `re.search(r'print\(\s*f?"[^"]*' + re.escape(label), src)`. Only real code can satisfy that; a bare
  substring also matches docs, comments, and dead text.
- **Do NOT delete the comment to make the test pass.** That is the tempting one-line fix and it trades
  real documentation for a green. The guard was wrong, not the prose. If the assertion changes at all
  it gets STRICTER or stays identical — never looser.
- **State the anchor's property as its own check** — "the anchors are PRINT statements, not comments or
  docstrings" — so the guard cannot quietly drift back to reading prose.
- **Then falsify the meta-check itself.** `SRC[:i].rstrip().endswith('print(')` never matches when `i`
  lands *at* `print(`; a green meta-check you never tested is one more unfalsifiable assertion.
- **Adding docs to a file is a change like any other — re-run the suites that parse it.** Source-order
  guards read the whole file, so a comment is load-bearing whether or not you meant it to be.

## Do not assert on state an earlier section deliberately MOVED

A suite whose sections share one state object fails when a preceding section legitimately changes that
state — and the failure names the wrong culprit.

Measured: a check read a counter immediately after the prior section had, **by design**, cleared it in
order to test the clear. Correct code, reported as broken, with a `None` that sent the reader hunting
a bug that did not exist.

- **Give each section its OWN fixture** (`tmp/b.json`, `tmp/key.json`), or explicitly re-establish the
  precondition at the top of the section.
- **A section that proves a CLEAR / RESET / RE-ARM destroys the evidence the next section wants.**
  That is the point of the section, which is exactly why the next one needs its own copy.
- **Read the value where you just wrote it.** If the check needs the entry that `refused()` created,
  create it in that section — do not reach for whatever is lying around.
- Sections that depend on each other's leftovers test the ORDER of your sections, not the code.

## The first red from a new test usually indicts the test, not the code

When a test fails on code you have just reasoned about carefully, **read the assertion before you
read the implementation** — especially when the implementation is a guard. The guard may be fine;
the test may be measuring the wrong thing.

Measured twice in one session:
- **Source order vs runtime order:** a test asserted the refspec validator was called before a
  function definition near the top of the file. A `def` is written where it is declared; it executes
  when called. The check failed on correct code because it compared a call site to a declaration
  site. The fix was to compare against the first statement that actually executes after the guard.
- **Prose vs emitted text:** a test searched the whole source file for the retired flag name and
  failed because the word appeared in a docstring explaining the retirement. The search matched
  a MENTION instead of an EMISSION. The fix was to anchor on the `argparse.add_argument()` call or
  the actual parse result, not on the bare word.

**Procedure when a new test fails:**
1. **Identify the two anchors.** One is the thing the test says happens; the other is the thing it
   says happens before/after.
2. **Classify each anchor as:** definition / mention (comment, docstring, string literal) / emission
   (statement that actually runs and produces the value or side effect).
3. **If either anchor is a definition or mention, replace it with the emission.** A definition site
   is where code is written; an emission site is where it has effect. Tests must measure effect.
4. **If the test becomes looser to make it pass, stop.** Loosening is not a fix; it is a downgrade.
   Either the code is wrong (change the code) or the test is wrong (change the test to a stricter
   emission-based check), but the assertion must not move toward always-passing.
5. **Re-prove the negative control after correcting the test.** A test whose false red came from a
   bad anchor may also be unable to catch the real defect. Plant the defect and confirm red.

## A bounded read turns its OWN BOUNDARY into a defect

A check that reads a fixed-size window out of a larger artifact manufactures a defect at the seam.
Anything just outside the window is invisible, so a record that legitimately continues the one above
it reads as "orphaned" — a false red on a correct artifact, produced entirely by the reader's slice.

Measured: a structure guard read a 260-line window while its "look back one line to see whether this
header is glued to the previous entry" rule needed a 60-line lookback, so a valid entry sitting one
line above the window's start was reported as orphaned. The document was clean; the window was not.

**The deeper mechanism:** the guard sliced `lines[-(260+70):]` intending 70 lines of context, then
searched only `range(max(0, i-60), i)` **inside that slice**. The context lines were present, but the
lookback search could not see past the slice's own first line — so a header six lines above the
window's start was invisible. **The 70-line context must be added to the EVALUATION window, not merely
to the printed snippet; the lookback must be able to reach N lines above the first judged line.**
A verdict that depends on the file's length is reporting length, not structure.

- **Size the read to the QUESTION, not to the file.** If the assertion needs context N lines above a
  match, the read must extend at least N lines beyond every match it evaluates — or read the whole
  artifact and slice only for printing.
- **Do not judge anything at the window EDGE.** The first and last records of any bounded read are
  where a seam artifact lives; either widen so they are interior, or skip them explicitly.
- **Re-run the fixed guard against a REAL defect before trusting the green.** A false-red fix that is
  never re-tested against a genuine violation can just as easily have made the guard blind.

## A fixture copied from a MOVING system tests the moment, not the rule

A live system's values change. Hardcoding one — "the book has 12 bins", "the wallet holds 0.0153",
"the position resolves to a curve" — makes the assertion depend on a state that was true when you
looked. Correct code then FAILS, and the failure names the wrong culprit.

Measured: a suite hardcoded a 12-bin book and expected it to resolve to the recorded shape. 12 bins
is a PARTIAL — correctly not that shape — so the check failed. The book had been 45 bins, was 13 at
one point, and 25 by the time the suite ran. The fixture was a snapshot wearing a fixture's name.

- **Derive the fixture from the RULE, not from a reading of the system.** If the shape must be a
  curve, construct a book that IS one; never copy whatever the live object happens to be.
- **A fixture reused by several sections should be the MINIMAL one for each question.** A section
  proving "unrecognised geometry classifies as empty" needs a partial; a section proving "the record
  shape resolves" needs a full one. One shared fixture cannot be both, and whichever section it
  fails names an innocent. Give each section the fixture its own question requires.
- **Assert the PROPERTY, never the current value.** "Every supported token's address is well-formed"
  survives a token being added; "token X is absent" does not.
- **An assertion that a fact is false because it is NOT YET true expires the moment it becomes
  true.** A check asserting "this must be unsupported until verified" passes until someone verifies
  it, then fails forever on a correct system. Write what must ALWAYS hold (no malformed addresses;
  unlisted symbols are refused), not the current status of an open question — and when such a test
  goes red, suspect the FIXTURE or the ASSERTION before the code, then verify the claim against
  ground truth (read the chain, the file, the API) BEFORE editing either side.
- **A comment that calls a hardcoded constant a live measurement does not make it one.**
  `AMOUNT_IN = 0.744 * 1e18  # half of the idle WAVAX` is a snapshot wearing a caption. The
  comment says it was derived from balance, so it reads like a rule; it is still frozen at the
  moment it was written. Name the constant honestly (`FROZEN_`, `SNAPSHOT_`) or derive it at
  runtime. When you remove a frozen constant, grep its name in comments and output strings —
  prose describing a mechanism you deleted is a false claim.

## Count suite health by EXIT CODE, never by grepping the output

A suite tree is not homogeneous. Some suites are `unittest` (they print `OK`), some print a custom
`RESULT: PASS — n/m` footer, some print only a summary line. Grepping for ONE of those shapes across
the whole tree silently scores every other kind as a failure.

Measured: a full-tree sweep reported 15 of 27 passing. Twelve "failures" had never failed — several
were `unittest` printing `OK`. Re-run by exit code: 25 of 27. The audit itself was the defect, and it
was one command away from a false alarm about a healthy tree.

- **Run each suite and read `$?`:** `timeout 400 python3 "$t" > out 2>&1; rc=$?` — that is the
  verdict the suite actually publishes.
- **Grep the output only for DETAIL (which checks failed), never for the VERDICT.**
- **Spot-check ONE reported failure by hand before publishing a tree-wide count.** If it passes,
  your counter is wrong, not the tree.

### A runner that DISCARDS a failing test's output makes every red a dead end

The runner captures each test's transcript and then throws it away on failure. The verdict is then
the only artifact — and the verdict is the one thing you already have, because you know it failed.

Measured: the runner wrote `printf '%s\trc=%s' "$f" "$rc"` on failure while the cannot-judge branch
right below it mined the SAME captured output for a reason. So a red test reported a filename and an
exit code and **nothing else**, and the only way to learn why was to reproduce the run by hand, blind.
The asymmetry was the bug: one branch used the evidence it had, the other discarded it.

- **A failure must print its evidence OR its path.** Mine the test's own most informative line
  (`FAIL|RESULT|Traceback|Error|assert`) into the summary, and write the full transcript to a named
  file. A verdict whose supporting output is discarded cannot be audited — and an auditor who must
  reproduce a run to see the reason will eventually stop reproducing it.
- **The same rule applies to every aggregated verdict**, not just test runners: a monitor, a sweep, a
  fleet audit. **If the summary is the only thing that leaves the machine, the detail must be in the
  summary or on disk.** `rc=1` with no reason is a refusal to explain, not a report.
- **A red from a non-hermetic test run during a live operation is a transient, not a regression — and
  "probably flake" is not a diagnosis.** Re-run the suspect tests individually, then re-run the whole
  suite once the system is quiet, and compare. Measured: a suite went `fail=2` while a live capital
  operation was in flight — its own summary showed a third test skipped because "the wallet went busy
  mid-section" — and the quiet re-run came back `40/0/0`. Both failing tests read live state, so they
  are **non-hermetic by design**; that is worth knowing before the next live operation, not after.
- **Do not let a red suite run unattended alongside a live operation.** It manufactures failures that
  teach the reader to ignore the suite, which is the same damage as a flake — and it can mask a real
  red that arrives in the same window.

## Prove the HARNESS before believing a green

A broken stub or fake can return the same verdict on every input — and when that verdict is a refusal,
it reads as a passing guard.

Measured: a hand-rolled fake delegated to a real object for an attribute the real one did not have, so
**every** case returned "unmeasurable" — which the first version of the test scored as PASS. Eight
identical refusals looked like eight successful refusals.

**Assert the harness can produce a KNOWN-GOOD case before asserting it refuses the bad ones.** Give the
test its own section for this. If every input path yields one verdict, the harness is broken, not the
code.

## A state override can invert a test

A test that simulates an input or a wallet balance can make the probe pass for a state you do not
actually hold, and fail for the state you do. The verdict is then **backwards**: the code is
reported broken in the real condition and reported working in an imaginary one.

Measured: a swap-route probe set `AMOUNT_IN = 0.744 WAVAX` while the wallet held 0.0186, then added
a state override that faked a 5 WAVAX balance so the oversized probe would clear. The result:
- 0.744 WAVAX (a size we cannot fund) quoted successfully;
- 0.018 WAVAX (a size we actually hold) failed the input transfer and reported
  "the route is genuinely down".

**Rule: a state override must represent a condition the real system can actually be in, and the
probe must be sized to a live value you hold.** If the test has to fake the balance to ask
"can WE swap?", it is not asking about you. Remove the override and size the probe from the live
state; a balance too small to probe is a READ failure (2), never a verdict (1).

**Corollary: when you remove an override, grep its name in the output text.** A message that still
says "simulated with a funded balance override" after the override is deleted reports a mechanism
that no longer exists, and a reader who trusts the message will believe the test is doing something
it is not.

## Every check needs a NEGATIVE CONTROL on the REAL artifact

The strongest guard is worthless if it can only fail on its own fixture. Prove it goes red by making
the genuine defect recur in the genuine source — then revert.

- **Neuter the guard, re-run the suite.** If it still passes, the suite is guarding nothing.
- **A control against a fixture copy proves nothing about the shipped artifact** — run the real entry
  point, re-invoking `__file__` as a subprocess if needed.
- **Do not mutate production to plant the defect.** Write to a throwaway copy; a test killed between
  plant and restore leaves the mutation live with nobody watching. Make the guard's root injectable
  (`os.environ.get("X_ROOT", <default>)`), and have the test **strip any test marker it finds at
  startup** — that is the only recovery path for a run that already died mid-window.
- **After hardening a check, re-run the negative control.** A hermeticity fix can quietly make the
  suite unfalsifiable.

## A falsification must not POINT at the real protected resource

The rule above — write to a throwaway copy — covers mutating the **code**. It does not cover the test's
**target**. A test that disables a guard to prove the guard works will, in that run, do whatever the guard
prevented — **at whatever path the test handed it.** If that path is the live resource, the falsification
CREATES the hazard it was written to rule out.

Measured, and it cost real material: a key generator refused to write private keys into the synced vault. The
guard **hardcoded the real vault root**, so the test exercising it passed the **live vault path**. The mutation
itself lived in a throwaway copy, exactly as this skill prescribes — and the mutated build still wrote two real
private keys into the vault, which a later sync carried off-box before anyone noticed. The failing SUITE
noticed, not the author.

**Parameterise the protected root and inject a scratch one in tests.** Production keeps the real default; the
test hands the guard a temp tree that merely *stands in* for the resource.

```python
def assert_outside(path, *, vault_root=None):     # default = the real vault
    root = (vault_root or VAULT_ROOT).rstrip("/")
    ...

# exercises the guard, and cannot reach production even when the guard is disabled
generate("seat", str(scratch / "vault" / "keys"), vault_root=str(scratch / "vault"))
```

- **A test that must break the thing it protects in order to prove it protects is a hazard, not a test.**
- **Check the guard DIRECTLY for the real resource** — `pytest.raises(G): assert_outside(REAL_ROOT)`. A pure
  check has no write path, so it stays safe under mutation and still goes red when the guard is removed.
- **Add a TRIPWIRE for the hazard itself, with a test that FIRES it** — scan the real resource for the thing
  that must never be in it and fail loudly. A guard nobody has watched fail is a guard nobody knows works.
- **Prove the fix by re-running the falsification, not by reading the cleanup.** After the fix, disabling the
  guard must still turn the tests red **and leave the real resource untouched**; that is the difference between
  a hazard fixed and a hazard merely swept.
- **Report the incident even when the cleanup is complete.** The artifact may already be in git history or
  off-box, and a quietly removed exposure is an unassessed one. State the severity and the evidence for it
  (here: never published in a roster, never used, and a different key from the real one) rather than "cleaned".

## A test must not PIN the bug it exists to catch

A test that asserts the **exact buggy expression** is present will happily re-introduce the bug
whenever someone "tidies" the implementation. It is a green that depends on the defect surviving.

Measured: a gas-topup test checked that `unwrap_need - (plan_wei / 1e18)` appeared in the source.
That was the **float-subtraction bug** that invented phantom swap legs from binary dust. The tool was
fixed to use integer wei subtraction, the test went red, and the only honest repair was to assert the
integer form was present **and** the float form was **gone**. Re-planting the old float form made the
updated test fail; the real source made it pass.

- **When a check fails after a code fix, inspect the assertion for the old defect shape.** The failing
  assertion may be a fixture-rot check that was actually pinning the bug.
- **Assert the fixed SHAPE and the absence of the old shape.** "Integer remainder exists" AND
  "float subtraction of wei counts is absent" is a strictly stronger check than either alone.
- **A test updated to match a bug fix should be harder to pass, not easier.** If the new assertion
  is looser than the old one, the test was not updated — it was downgraded.
- **A test that goes red on a correct fix is reporting on itself.** Fix the test, not the code,
  but verify that the updated test still catches the reintroduced bug.

## A test must be HERMETIC — never assert against the host environment

A positive control that reads the real installation path only passes on machines with that layout, so
it fails everywhere else for a tool that is fine. Build fixtures in a temp tree the test owns.

- Want to report host state anyway? Emit it as an INFO line that is **never AND-ed into the result**
  — and wrap it, or an exception in an informational probe becomes a failure and the false red returns
  through another door.
- **Test both directions of every refusal.** A boundary never tested in the direction it BLOCKS is not
  known to work; a boundary never tested in the direction it ALLOWS will happily block legitimate work.
- **State the denominator.** "No issues found" is unfalsifiable without a count — it renders the same
  whether you examined 400 files or 0. Print how many you read and fail when that number is zero.

## Testing a permission/read-failure path

- **Never use `chmod 000` while running as root** — root reads through it, so the test passes for the
  wrong reason. Use a **directory named `*.py`**: `open()` raises `OSError` for any uid.
- **`py_compile` / `ast.parse` passing is NOT the module importing.** A syntax check is blind to name
  resolution. A file compiles cleanly and still dies on import when a function is called at module
  scope but defined further down. Verify by importing:
  ```python
  import importlib.util as u
  s = u.spec_from_file_location('m', path); m = u.module_from_spec(s)
  s.loader.exec_module(m)          # the real check
  ```
  Better: run the tool's own `--help` or a dry run. A sweep reporting "N/N compile" has proven
  nothing about whether those files can RUN.

## A branch your fixture cannot REACH is untested — perturb the boundary to find it

Coverage is not a property of the assertions you wrote; it is a property of the STATES your fixture
can produce. A branch that only opens under a different state is invisible: every check passes, and
the branch was never executed at all.

Measured: a tool's "cannot proceed" branch was the one path that emitted none of the
machine-readable decision tokens its test asserted on. The test passed for months because its
fixture wallet held liquid balance, and the branch only opens when the balance is fully deployed.
Changing a boundary constant routed execution down an untested path and the check went red at once.

- **Change a boundary constant and re-run the suite.** Moving a threshold, a floor, or a default is
  the cheapest way to force execution down branches your fixtures never took. A suite that stays
  green through a genuine boundary change is not reaching the boundary.
- **Enumerate branches by STATE, then require a fixture per state** — not a fixture per function.
  "Has liquid balance / has none", "file present / absent / stale", "first run / repeated".
- **When a check goes red after a threshold change, suspect the FIXTURE before the code.** The code
  is often doing exactly what it always did; the suite simply never ran there.
- **A decision branch must emit its decision.** If a path answers "no", it still has to print the
  machine-readable token saying so — absent output is indistinguishable from a crash, and a
  consumer of that output cannot tell refuse from fail.
- **When a branch goes red after a threshold change, grep the test for the TOKEN LIST before
  touching the branch.** The failing assertion is usually a membership test over a set of verdict
  words, and the honest repair is to add the missing word, not to widen the check. Two traps, and
  they pull in opposite directions:
  - **Do not delete the assertion.** It is the one guard that catches a silent branch, and removing
    it because a real branch lacked a token trades a caught defect for a covered-up one.
  - **Do not rewrite the membership test into something that cannot fail** (`if out:` or a bare
    non-empty check). A check widened until it always passes is the same defect as one that never
    fires.
  Add the token to the SOURCE and keep the strict check. If the assertion is being changed at all,
  it must get STRICTER or stay identical — never looser.
- **After any change that routes execution down a new path, list which of your fixtures reach it.**
  The count is usually zero, and that is the finding: the suite was green because nothing it owned
  ever went there.

## A test that dies on a transient external read is reporting a verdict, not a failure

A test that touches the network, chain, disk, or database and does not wrap every such call teaches
people to ignore failures — and then it hides real ones. A provider blip, RPC lag, or timeout that
raises an unhandled exception exits the process with a traceback and a non-zero code that looks
exactly like a real defect. Re-running it five minutes later passes. This is the worst kind of flake:
it trains the reader that "the suite is red again, probably nothing" and collapses the signal.

Measured: a swap-route probe wrapped every `eth_call` except `w3.eth.get_code()` and
`w3.eth.get_block("latest")`. One public-RPC hiccup killed the whole run with exit 1, no verdict,
no machine-readable status — indistinguishable from "no route exists." Five subsequent runs passed
unchanged.

- **Wrap EVERY external call in the test, not just the ones that usually fail.** The calls you
  skipped are the ones that will flake at 3am. A read that cannot complete must return an explicit
  READ-failure code (e.g., 2), never the same code as a real verdict (e.g., 1).
- **Distinguish "I could not measure" from "I measured and the answer is no."** The latter is a
  verdict; the former is a probe failure. They must not share an exit code, and the output must say
  which one happened.
- **Run the suspect test multiple times in a row before trusting it.** A test that passes 5/5 after a
  single failure is flakier than a test that always passes, but it is also evidence that the
  implementation is fine and the harness is the problem.
- **A flake is worse than a bug** — it is a bug that teaches the team to stop trusting the suite.
  Fix the harness first; only then interpret a red result as a defect in the code under test.

## Prove the negative control by REVERTING the fix in a throwaway copy

A negative control that you never saw fail is a claim, not a control. The strongest proof is to take the
shipped fix out of the equation, run the suite, and watch the relevant case go RED — then restore.

Measured: a verifier was parameterised so each §4 case could run with its responsible check removed.
The harness looked good, but the real proof came from copying the module to a temp dir, mutating it back
to the pre-fix shape, and running the tests there:

```
real code        -> 11 passed
pre-fix mutation -> 2 failed, including the regression test
```

That showed the regression test was not just a restatement of the fix; it died when the fix was absent.

**Procedure:**
1. Keep the fix in production code.
2. Create a temp dir and copy the module + tests there.
3. Apply the **inverse patch** (mechanical if the fix was small, or save the original hunk before
   patching and re-apply it).
4. Run the suite in the temp dir.
5. Confirm the case(s) that should fail DO fail.
6. Delete the temp dir; do NOT leave the mutation anywhere persistent.

**Do not mutate the real source to plant the defect.** A test killed between plant and restore leaves
the defect live. A throwaway copy is the only safe way to prove the control.

## A check that RECORDS while it CHECKS consumes evidence a later step still needs

A check that writes state while deciding whether to refuse can burn a token that a later step then needs.
If every step must agree before the request is accepted, then **recording the outcome must happen AFTER
all steps have agreed**, not during an early one.

Measured: a replay check inserted the `jti` into the store at the moment it verified uniqueness. A token
that was then refused by a later step (stale roster) had already consumed its `jti`, so when the roster
refreshed and the caller re-presented the same valid token, it was refused as a replay — for a call that
never happened. A stale roster silently invalidated every in-flight peer call.

**Rule:** separate the *read* (`is_seen`) from the *claim* (`claim`). Check early, record last. The atomic
claim stays the real accept-once gate under concurrency; the early read is for promptness and the right
error message.

**Regression test it:** present a valid token, refuse it at a late step, then present the same token again
and assert it is still accepted. If the check records early, this test fails.

## Module names can shadow the standard library and break the import chain BEFORE your code runs

A file named `token.py` looks harmless until `dataclasses → inspect → tokenize → from token import
EXACT_TOKEN_TYPES` tries to import the real `token` module and finds yours instead. The error points at
`dataclasses`, not at your file, and the code never executes a line.

**Rule:** before naming a module, check whether it collides with a stdlib module. A quick probe:

```python
import sys, importlib.util
name = "token"
if importlib.util.find_spec(name) is not None and name not in sys.builtin_module_names:
    print(f"{name!r} is a real importable module — do not shadow it")
```

**If a file must live on `sys.path` and its natural name shadows the stdlib, rename it.** The test for the
renamed module then becomes: import it under the new name and assert it resolves to the expected path,
not to the stdlib one.

## Pitfalls

- **A test sample must come from the DOMAIN, not from the artifact under test.** Inputs drawn from the
  lookup table the code consults measure self-consistency and discriminate nothing. Include at least
  one input you expect to FAIL — a sample where every case passes cannot falsify anything.
- **A resolver test must prove it does NOT invent paths.** Test bare-lane forms, filed subdirs,
  and alias resolution, but also assert that genuinely absent files return `None` and that empty/None
  inputs return `None`. A resolver that fabricates a location for a missing file is a false-green
  machine. Run it against the live ledger and report the resolution rate; a fixture-only suite can
  pass while most real records are unfollowable.
- **Re-measure after you fix the measurement itself.** A parser, classifier, or resolver change can
  change the count as much as the underlying state. Re-run on the same corpus before and after,
  using the same denominator. If the new number contradicts the old, debug the MEASUREMENT before
  reporting the new finding. The first corrected measurement is a hypothesis, not a fact.
- **A guard that validates a COPY of the thing is not a guard on the thing.** If the "actual" side is a
  hardcoded dict rather than the live source, the guard reports green while the real source is broken.
  Pin the EXPECTED side; derive the ACTUAL side from the artifact (import it, parse it, probe it).
- **CLI subprocess tests get fresh state per invocation.** If test A creates data and test B reads it
  via `subprocess.run`, test B sees an empty world. Create and read within one script, or call the
  module's Python API directly.
- **Define helpers BEFORE the functions that call them** in inline (non-pytest) test scripts — Python
  executes top to bottom, so a helper used at module scope must be defined earlier in the file.
- **A test that asserts success while doing nothing is the same bug class it exists to catch.** Ask of
  every new check: *what would make this print a confident PASS while the thing it guards is broken?*
  If the answer is "nothing", you have not finished writing it.
- **A CLAUSE THAT SHARES ITS EXPRESSION WITH ANOTHER CLAUSE CANNOT FAIL INDEPENDENTLY — measure what
  the LABEL names, not what is nearby.** A suite line printed `read by assert_target_safe (N)` where
  `N` was computed by the *same command* as the total-occurrence count two lines above it. The label
  named a specific function; the expression counted the whole file. Proven: a subject whose guard body
  referenced the constant **zero** times, carrying two *unrelated* references elsewhere, still
  **PASSED** — the global threshold was satisfied by uses that had nothing to do with the assertion.
  **Scope the count to the artifact the label names** (extract the function's own body and count
  there), and **fail loud when that artifact cannot be found** — a guard that cannot be located must
  not read as a guard that is satisfied.
- **THE MECHANISM A TEST CANNOT REACH IS WHERE IT IS BLIND, AND FIXING ONE RUNG REVEALS THE NEXT.**
  In a single file, the same defect appeared three times, each one inside the fix for the last:
  **(1) matching PROSE** — the grep hit the docstring explaining the defect instead of the defect;
  **(2) matching the DEFINITION** — the pattern matched `def f(...)` so `head -1` returned the
  signature and the case passed with the call site deleted entirely; **(3) matching a GLOBAL
  THRESHOLD while wearing a clause's name** (above) — and then it reappeared *inside that fix*,
  because the newly scoped extraction still included the function's docstring, which discussed the
  constant. **Assume the class survives your fix and re-run the control after each repair; verify by
  watching the case go RED, not by reading the patch.**
- **THE PROOF IS THAT THE REVERT IS CHEAP.** A control nobody can re-run in a minute is a claim, not
  a control. Prefer a fixture swap plus a restore-by-hash over a hand-edited subject: if turning the
  fix back into the bug takes one block move, the next reader will actually do it, and the control
  stays alive. Snapshot the refs first, run, restore from the hash, and assert the restore.
