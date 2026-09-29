---
name: guard-verification
description: Harden guards so they fail on real defects, not fixtures.
trigger: Writing a new guard or watcher, adding a negative control, or when a guard/test/watcher produces a false red, false green, or silent miss.
tags: [guards, watchers, negative-control, tests, verification, false-value]
version: 1.0.0
author: Gentech
license: MIT
---

# Guard Verification

A guard is only useful if it goes red when the thing it protects is broken and stays green when it
is not. This skill covers the design, testing, and maintenance of guards, watchers, and negative
controls — the patterns that keep them honest and loud.

## Procedure

### 1. Design the verdict first

Before writing the guard, state the exact question it answers and the two ways it can be wrong:

| wrong direction | name | symptom |
|---|---|---|
| says broken when healthy | false red | wastes time, trains people to ignore the guard |
| says healthy when broken | false green | silent failure, usually worse |

A guard that cannot fail in either direction is a decoration. If you cannot describe both failure
modes, you are not done designing it.

### 1b. A guard's name and its enforcement can be two different things

**The declaration that carries the name may be inert while the actual protection has no name.**
This is the hardest guard defect to see, because the named symbol reads as enforcement to a
reviewer and the real enforcement looks like an implementation detail.

Measured: a script declared `NEVER_TOUCH = "main"` with a comment calling it "non-negotiable", and
referenced it zero times. The protection that actually held was a hardcoded refspec on the push
line. The thing with the name did nothing; the thing that did the work had no name. Two auditors
initially read the named guard as the enforcement.

**Rule:** grep the guard's identifier and count the READS. One occurrence (its own assignment) is the
alarm. A declaration plus a comment is indistinguishable from enforcement to the next reader.

**Fix:** make the named guard read the string the action actually uses, and order it
`build → validate → use`. The test should assert the ORDER, not the presence. A guard called after the
action is decoration; a guard called on a different string than the action uses is theatre.

**Prove it fires with the target-rewritten case.** A guard that only reads the declaration passes the
obvious tests and fails exactly where it matters: the target is rewritten to the forbidden value
while the variable still reads the permitted one. If that case does not fail, the guard is a name
without a mechanism.

**When retiring a dangerous word: remove it from the CLI surface, keep the reason in docs.** Rename a
flag (`--force-run` → `--now`) so it cannot be reached; leave the docstring explaining the
withdrawal. Assert against the emitted statement (the argparse call), never the whole file — a check
that forbids its own explanation pressures the next editor to delete the doctrine.

### 2. Read the field, not your own expectation of it

**A parser that reads the field it guards must be format-agnostic.** Real inputs declare state in
bold (`**Status:** open`), as list items (`- status: open`), inside blockquotes, and in table cells.
A reader that only matches a bare plaintext prefix misses real declarations and returns `none` for
a note that plainly has a status.

**Rule:** strip Markdown decoration before classifying. A reader that cannot see its own input is a
false-negative generator — the same class it exists to stop.

### 2a. A guard that demands a receipt must verify the receipt is FOLLOWABLE

**Requiring a `return_note` is not enough — the path it records must resolve for the next reader.**
A malformed path looks like diligence while being as untrustworthy as no note at all:

- Bare lane form with no `01-HANDOFFS/` prefix.
- Stale lane alias (`gentech-to-treasury` when the real lane is `gentech-treasury-to-gentech`).
- A file that was filed into `_archive/` or `_closed/` but the record still points at the live lane.

When a guard checks `answered` records against their note, **measure the live ledger's resolution rate**
before declaring the guard sufficient. If most paths do not resolve literally, the guard is catching
"no note" but missing "note that names nothing." Both are false receipts.

**Fix read-side and write-side together:**
- Provide `resolve_return_note(note, near=)` that walks the vault prefix, lane aliases, and filed
  subdirs so old records become followable WITHOUT rewriting them. A write-once record's hash must
  not be disturbed by a retrospective edit.
- Make `close()` write the COMPLETE resolved, vault-relative path (`01-HANDOFFS/<lane>/_archive/...`)
  so new records are followable by construction.
- Keep a canonical alias table (`gizmo==labs`, `pixel==entertainment`) in ONE place, not scattered
  across call sites.

**Negative control:** an absent reply must resolve to `None`. A resolver that fabricates a plausible
path for a missing file is worse than no resolver, because it turns "genuinely missing" into
"found it, trust me."

**Measure against the live corpus, not a fixture.** A test with only hand-crafted good paths cannot
prove the resolver handles the real historical mess.

### 3. Classify by leading word, not substring

**A classifier must test the LEADING WORD of the declared value, not a substring over free text.**
Substring tests are wrong in both directions:

- `closed — nothing open here` contains the target word and reads as open (false positive).
- `no further action — the one open class is a design question` describes an open item but contains
  no literal target word and reads as closed (false negative).

After fixing the parser, re-read the live corpus and count. The leading word is the verdict:
`open`, `closed`, `answered`, `acked`, etc. The target word should match exactly the genuine cases,
and every other leading word should map to its actual state.

### 4. Build a falsifiable negative control

**A guard without a negative control is a guard that has never been proven to bite.**

- **Neuter the guard, re-run the suite.** If it still passes, the suite is guarding nothing.
- **Run the control against the real artifact, not a fixture.** A control against a hardcoded dict
  proves the comparison arithmetic, not that the guard watches the source.
- **If the suite disables the guard by string-replacing an exact source line, a refactor of that line
  silently neuters the control.** Before touching the guarded call line, grep the test tree for any
  replacement of it. If one exists, keep the line byte-identical or update the control's target in
  the same commit. After any edit, run the control and prove it still bites.
- **Do not mutate production to plant a defect.** Write to a throwaway copy; make the guard's root
  injectable (`os.environ.get("X_ROOT", <default>)`) and strip any test marker found at startup.

### 5. Re-verify after hardening

A fix can make the suite unfalsifiable. After every hardening change:

1. Run the positive suite — it must pass.
2. Run the negative control — it must fail (or report the refusal).
3. Plant a real defect in a scratch copy — the guard must detect it.

### 6. Report near-misses honestly

**A green suite is not the same as a correct decision.** If reading stopped an action the guard
would have permitted, disclose the near-miss in the record rather than letting the suite imply
sufficiency. Say "I stopped this by reading, not by rule" when that is the truth.

## Pitfalls

- **A guard that validates a COPY of the thing is not a guard on the thing.** Pin the expected side;
  derive the actual side from the live artifact (import it, parse it, probe it).
- **A parser that only handles plaintext handles only its own test fixtures.** Real inputs carry
  formatting; ignore it and you miss real cases.
- **Substring classification fails in both directions at once.** Prefer a leading-word test with a
  strict word boundary.
- **A negative control that string-replaces an exact line is a coupling.** Refactoring that line
  turns the control into a no-op that still passes. Keep the line stable or update the control
  together.
- **Never report a hash mismatch as a state change.** Digests from different normalisation rules are
  incomparable; call it unverifiable, not edited.
- **A test that asserts success while doing nothing is the same bug class it exists to catch.** For
  every check, ask: "what would make this print a confident PASS while the thing it guards is broken?"

## Verification

- [ ] The guard's question and both failure modes are stated.
- [ ] The parser handles the real input formats the artifact uses.
- [ ] Classification is by leading word with a strict boundary.
- [ ] A negative control exists and is proven to bite.
- [ ] The control is not broken by a refactor of the guarded line.
- [ ] After hardening, the positive suite passes and the negative control fails.
- [ ] Near-misses are disclosed in the record, not hidden behind a green suite.

For verification under a throttled fleet write gate, see `references/gate-saturation.md`.
