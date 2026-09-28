---
name: bug-class-self-audit
description: "Use when hardening a system or after fixing bugs."
tags: [audit, self-healing, verification, core-pattern]
version: 1.1.0
author: Gentech
trigger: "When Jordan says 'audit', 'what could I be missing', 'self-heal', or after fixing any bug — turn the fix into a permanent check."
---

# Bug-Class Self-Audit

Audit by bug CLASS, not instance. Encode each mistake's shape as a permanent
check so the whole family can never return.

## The principle

**Auditing by instance produces a report. Auditing by CLASS produces a
ratchet.** A report is stale tomorrow. A check runs forever.

Every bug has a *shape* — the assumption that was wrong. Find the shape, write a
check for it, and that entire family is closed permanently.

## The root cause of nearly every bug

> **The code assumed something about the world that nobody verified against
> ground truth.**

Before writing any check, ask: *what did this code assume, and could I have
asked the system instead?* That question alone catches most of them.

## The universal verification principle

> **When the system can tell you the answer, ask it — don't compute it.**

- Validating a fee *formula* → simulate the chain's own `collect()` call.
- Validating a *valuation* → simulate `decreaseLiquidity` / `balanceOf`.
- Validating a *capability claim* → grep the actual source.

Every time the computed value and the system disagreed, **the system was
right**. Make simulation-vs-formula agreement the acceptance test.

## The recurring classes (start here)

1. **success-before-status** — a success message printed before verifying the
   operation actually succeeded (tx receipt status, HTTP code, non-empty result).
   *Check:* find success prints whose guard sits nowhere near them.
2. **index-selection** — selecting an item by loop index / list position instead
   of by the property that matters. *Fix:* rank by value, never by order.
3. **address-unverified** — a hardcoded address/id that doesn't exist.
   *Check:* resolve every hardcoded address against the live system.
4. **config-derived-value** — a number computed from config arithmetic instead
   of read from the source of truth. *Only flag on a LIVE path.*
5. **copy-divergence** — multiple copies of the same file drift apart.
   *Fix:* declare one source of truth, sync, hash-verify.
6. **balance-vs-claimable** — reads a stored balance where it means
   accrued/claimable. *Fix:* read the authoritative "what can I claim" call.
7. **api-shape** — assumes an external API's field path is stable.
   *Fix:* read both shapes defensively; re-validate on schema change.
8. **zero-denominator** — a checker reports "clean / none found" after examining
   NOTHING. A hard-coded root, a seat name absent from the list, a permission
   error, an empty glob — the loop runs zero times and the tool prints a
   confident pass. **"0 findings" and "0 things examined" are different results
   and must never render the same.** *Fix:* count what you actually read and
   refuse to pass on zero. Distinguish the zero states — no source dir at all
   (misconfiguration) vs source dir genuinely empty (a real clean) vs files
   present but unreadable (a silent miss). Only the middle one is a pass.
   **The near-miss variant — a search that finds nothing because the string was slightly
   wrong.** Measured twice in one session, from both sides: Treasury searched their own jobs for
   `x402` and got 0 (nearly reporting our x402 work did not exist); asked to explain why a
   sentinel looked dead, a `grep 'owner exited before finishing'` returned 0 while the DB
   literally contained `owner exited before a durable terminal state` — the real text, one clause
   longer. The tool answered correctly and the ANSWER WAS MEANINGLESS, because "matches 0" was
   read as "no such thing exists". *Fix:* a negative result from a PATTERN search is never
   evidence of absence — print the count of things EXAMINED, and when the count is 0 say
   "0 matched (this proves nothing about existence)", never "none found". Re-run with a shorter
   anchor before concluding anything is missing.
   **The mirror variant — a pattern rule cannot adjudicate prose that is ABOUT the pattern.**
   Same class, opposite direction: here the search finds things and the FINDINGS are meaningless.
   Measured 2026-09-28, with ground truth known: a thank-you note that *explains why keyword
   ask-detection fails* is itself flagged as owing an answer by the very rules it describes —
   `your call` (L20, praise: "your call to merge the union was right"), plus `can you` / `please` /
   `?` where the note is **quoting the false positives it is describing**. Both the narrow and the
   wide net flag it. The reverse also held the same night: the pixel note whose header read
   `1 question for you` was missed because no list contained that phrase.
   *Both directions are the same defect:* a document that DISCUSSES asks contains the vocabulary of
   asks, and a document that merely MENTIONS a question reads exactly like one that asks it.
   *Fix:* never parse intent from prose. A closure's truth lives in an explicit machine field
   (outcome + return_note), or in a human read — not in a regex over sentences. If a rule must scan
   prose, it may only ever RAISE FOR REVIEW, never decide.
9. **partial-coverage green** — the aggregate hides a dead component. A check
   that passes on a TOTAL can still be covering 3 of 4 sources: one source's dir
   moves, empties, or becomes unreadable, the others keep the total non-zero, and
   the verdict reads green. **One green source must never certify a dead one.**
   *Fix:* report PER-SOURCE coverage and name every source that contributed
   nothing, in every output path — not just when the whole run comes up empty.
   A per-source gap test must key on "read nothing from it", not on "had no files":
   files-present-but-unreadable is the same silent skip one level down.

10. **read-failure-as-value** — a read that FAILED renders identically to a read that
   returned a real value, and every downstream decision inherits it silently.
   Measured, one hour, four defects: a failed `eth_call` returns `0x` and `int('0x',16)`-style
   decoding makes it **0** (our own probe printed "LP shares 0" for a live position — the
   call had REVERTED); a lagging node answers with the PRE-transaction value; a wrong
   selector reverts and reads as "this function does not exist"; a tool that CRASHES after
   broadcasting exits non-zero and reads as "nothing was sent". *Fix:* every value that can
   be unread must be able to say **UNKNOWN + why** and must NEVER render as a zero. Ask the
   CHAIN, not the tool's exit code — and re-read before believing a write took effect.
   **A single read of a value a transaction just changed is not evidence** — poll the tx's
   own block (measured: an approve MINED but a one-shot re-read returned the OLD value, so a
   fail-closed refused a leg that should have landed).

11. **zero-headroom** — a value is computed to be EXACTLY enough, leaving no slack for the gap
   between the READ that sized it and the ACTION that spends it. Measured twice in one day on
   this system, two different rails, one shape:
   - **gas price**: `eth_gasPrice` sits exactly ON the current base fee, and the base fee moves
     every block. Tx built one tick later is BELOW the floor -> invalid -> never propagates.
     The node still returns a hash and the caller waits out a 200s receipt timeout for a receipt
     that cannot arrive (measured: 0.097612 vs a 0.100841 floor).
   - **allowance**: `approve(router, exactly_what_we_plan_to_spend)`. The router sizes its pull
     from live pool state at execution time; one bin of drift upward and the pull exceeds the
     allowance. WAVAX answers a short pull by REVERTING, which the router reports as
     `TokenHelper__TransferFailed()` (**0x32e2717a**) -- an error that names the token helper and
     sends the reader hunting a token bug that does not exist (measured: approved exactly
     0.051992, reverted; the same leg simulated clean minutes later with slack).
   *Rule:* **never price an action at the floor.** The gas PRICE (not just the limit) carries a
   multiplier; an allowance is a CEILING, not a spend, so approve the wallet's full balance --
   it cannot over-spend and it absorbs all drift. *Check:* grep every send path for a raw
   `eth_gas_price` and every `approve(` for an exact amount. A correct fix lands as ONE shared
   helper (`_gp(w3)` / `gas_reserve.gas_price_wei()`), never as a per-file copy.
   *Tell:* when a fix is small, cheap, and mechanical, sweep the WHOLE domain in the same pass --
   two instances found apart are two incidents reported apart.

## Seam rules (where these bugs actually live)

- **A guard implemented STRICTER than its purpose turns a small miss into a total outage.**
  A re-center guard meant "never deploy a one-sided book" was written as "abort if the ratio
  optimisation failed" — so a ratio miss emptied the whole position. Ask what the guard
  MEANS, not what is convenient to test.
- **A selector that is silently ignored behaves exactly like a correct one.** `TENANT=x`
  where the code reads `STEWARD_TENANT` sent three runs to the WRONG wallet, printing nothing.
  Same shape as a fix that only fires behind a non-default flag. Make identity resolution
  PRINT what it resolved, and refuse on a mismatch rather than defaulting.
- **A recovery path can manufacture the fault it repairs.** A flat-book recovery that read
  `"curve" if shape=="curve" else "ask"` deployed HALF a two-sided book, so every repair
  reproduced the one-sided state the guard existed to prevent. Walk the repair path and ask
  whether it can produce the condition it is fixing.
- **Catching a failure ≠ preserving its cause.** A subprocess run WITHOUT `capture_output`
  left a failed deploy recorded as one line, `exit=1`, with no leg output — undiagnosable
  tomorrow. Always capture the child's stdout+stderr, print its tail, and on failure name
  the cause or state plainly that none was preserved.

## Tune for false positives — or the audit gets ignored

A self-audit that cries wolf is worse than none: it trains everyone to ignore
it. Expect your first run to be noisy, then tighten:

- **Known-benign values** — skip your own wallet/EOA, other-chain address maps.
- **Scan both directions** for a guard — a correct check may sit *before* the
  line you flagged, not after.
- **Recognise legitimate fallbacks** — an explicit "find a DIFFERENT id" branch
  after a re-create is correct, not index-selection.
- **Downgrade dead code to INFO** — retired rails aren't live risk.

Target: **0 HIGH/MED findings** on a healthy system. Report only HIGH/MED;
keep INFO for context.

## Wire it to run without being asked

1. Write the checker as a script with `--json` output and a non-zero exit on
   findings.
2. **Wrap it in silence doctrine:** fingerprint the finding set and speak ONLY
   when that fingerprint changes. A standing known issue must stay quiet; a NEW
   class must speak immediately.
3. Schedule it on a cron delivering to the group's channel.
4. Verify the silence behaviour explicitly — run it twice; the second run must
   produce **no output**.

## The loop that makes it evolution

```
detect (self-audit) → fix (audit-fix-verify) → verify (ground truth)
   → encode the lesson as a NEW check → that class can never return
```

The last step is the difference between maintenance and evolution. Every bug
should leave behind a check that closes its entire class.

## Pitfalls

- **Don't ship a report when Jordan says "audit."** Fix every instance in one
  pass, verify, then report what changed. See `audit-fix-verify`.
- **Verify you're editing what actually runs.** Editing a stale mirror or a
  synced copy that gets overwritten produces work that changes nothing. See
  `source-of-truth-verification`.
## Catching a failure ≠ preserving the cause: check WHICH STREAM carries it

A wrapper that captures stderr is necessary and **not sufficient**. The cause may be printed to
**stdout** — and a wrapper that suppresses stdout while keeping stderr preserves a stream that
carries nothing, then honestly reports *"no stderr — the cause is missing upstream"*.

Measured: `lfj-fee-snapshot.sh` captured `rc=$?` inside the `else` (correct) and kept stderr (correct),
but the reader emitted its failure via a plain `print(...)` to **stdout**, which the wrapper sent to
`/dev/null`. With every provider dead the record showed `exit 2` and **zero bytes** of cause.

**Rule:** when a wrapper silences one stream to suppress success noise, the child's FAILURE path must
be on the stream that survives. Either send causes to stderr in the child (`print(..., file=sys.stderr)`)
or capture **both** streams in the wrapper and surface whichever is non-empty.

**Prove it with a negative control on the OLD shape**: run the previous wrapper against a child that
prints its cause to stdout only, and confirm it reports the cause as missing. If the old shape still
shows the cause, your test is not exercising the gap.

```bash
OUT=$(mktemp); ERR=$(mktemp)
python3 reader.py >"$OUT" 2>"$ERR"; rc=$?
[ -s "$ERR" ] && tail -20 "$ERR"      # cause may be here
[ -s "$OUT" ] && tail -5  "$OUT"      # ...or here. Capture both.
```

- **A check that can't fail is not a check.** Prove each check catches its bug
  by pointing it at the real (unfixed) code once.
- **Prove a scan RAN before trusting its zero — assert a NON-ZERO count on a string you know
  is present.** `[ -n "${VAR}" ]` proves the variable exists; it does not prove the search
  had anywhere to look. A count of 0 from a tree you believe contains the string is the
  signal, not the answer. Measured: the weak check passes when the variable is set but the
  path is wrong (grep count 0, still "pass"); the strong check goes RED. Same shape as a
  wrong corpus filename silently parsing 0 blocks instead of 117. **A zero is only
  trustworthy once you have proved the search had somewhere to look.**
- **An UNDEFINED variable used in a command FAILS SILENTLY — it is not a soft failure.**
  `${VAR}/x` with VAR unset expands to `/x`, producing no output and no error, which is
  indistinguishable from "nothing found". A portability refactor that swaps a literal path
  for `${VAR}` without defining the variable therefore converts working commands into
  silent no-ops, including security scans that then read as "clean". After any such
  refactor, assert the expansion resolves — `echo "${VAR:-UNSET}"` must print a value, and
  the real command must produce its expected output. A drift scan comparing file content
  cannot see this: 150/150 files can match while 110 of them are broken at runtime.
- **Hermeticity has TWO halves: the VERDICT and the TRANSCRIPT.** A check can be provably
  unable to flip a result (inert, never AND-ed into the verdict, exception path dead) and
  STILL not be machine-independent — if it prints host-specific output, on-machine and
  off-machine transcripts differ and the proof is broken. Safety ≠ hermeticity. Prove the
  transcript half by diffing full stdout from both machines, not just comparing exit codes.
- **Informational output belongs on stderr.** If a diagnostic must stay visible but is
  machine-dependent, route it to stderr: stdout then carries only the portable assertions
  and stays byte-identical everywhere, while the picture is still there for a human.
- **On a non-hermetic revision there is no such thing as "the" transcript hash.** If a check
  prints machine-specific output, every seat computes its own hash — so two honest seats
  reporting different values are BOTH right, and chasing the "discrepancy" is wasted work.
  Before treating a hash disagreement as a defect, ask whether the artifact can even be
  machine-independent; if it can't, the disagreement IS the defect, not noise around it.
- **Always state the capture recipe with any hash you quote**
  (`... 2>/dev/null | md5sum` = stdout only, the portable half; `... 2>&1 | md5sum` = for
  humans). Unstated recipes turn every cross-seat comparison into a round-trip.
- **Normalise line endings before comparing transcripts across platforms:**
  `--selftest 2>/dev/null | tr -d '\r' | md5sum`. Windows Python text mode translates `\n`
  to `\r\n` on a pipe and Linux does not, so a bare `md5sum` is not a portable instrument —
  it reports a correct hash of a correct transcript that can never equal the other seat's,
  which reads exactly like a defect in the tool. Reuse the existing `crlf2lf` stage in our
  own hash-normalisation layer (`NORM_ID`,
  `10-Labs/agent-kit-self-tracking/handoff_closure.py`) rather than inventing one.
- **Sweep by MECHANISM across the whole tree before calling a peer's claim unreproducible.**
  A narrow path sweep that comes back empty is a false negative, not evidence: grep the
  mechanism (e.g. `crlf` in any code file, any directory) — the implementation may live in
  `10-Labs/` or another dir outside the obvious `scripts/` pair.
- **State the sweep BOUNDARY in every negative claim, or sweep the whole domain.** A confident
  negative from an unstated boundary produces byte-identical output to a sweep that genuinely
  had nothing to find, so the reader cannot tell a real absence from a narrow search. Three
  separate false negatives in one thread shared this root cause: "not on any of the twenty
  refs" (refs never fetched), "18/77 vault paths absent" (one directory prefix searched),
  "crlf2lf isn't in our normalisation" (two of three dirs swept). Write "absent from <the
  domain I searched>" — never a bare "does not exist".
- **A guard inside a program needs its own negative control — and it must exercise the
  VERDICT, not the inputs.** A suite that asserts against the helper's return values never
  touches the code path that prints the verdict and sets the exit code, so the whole guard
  can be deleted while the suite goes on saying PASS. Reproduce it: neuter the guard, then
  run the suite — if it still passes, the suite is guarding nothing. The control must run
  the real entry point (re-run `__file__` as a subprocess if needed); testing a fixture
  copy proves nothing about the shipped artifact.
- **...and a check that can't PASS on a healthy machine is not a check either.** Both
  directions matter: a false GREEN (reports clean after examining nothing) and a false
  RED (reports FAIL on a working tool) are the same defect wearing opposite masks. A
  false red is often worse when a GATE depends on it — "run the selftest before trusting
  this" becomes unpassable on any host whose layout differs.
- **A self-test must be HERMETIC: never assert against the HOST's environment.** A
  positive control that reads the real installation path only passes on machines that
  share that layout, so it fails everywhere else for a tool that is fine. Build the
  fixture in a temp tree the test owns. If you still want to report host state, do it as
  an INFO line that is never AND-ed into the result — **and wrap it**, or an exception in
  an informational probe becomes a failure and the false red comes back through another
  door.
- **Prove hermeticity by running the suite TWICE, nothing changed in between.** A test can
  look hermetic and still escape its sandbox: if any helper derives a path by walking up
  from the fixture (e.g. `closure_path()` walking three dirs to find the vault), a fixture
  placed too high resolves to the SHARED scratch dir — so run 1 is 11/11 and run 2 is 9/11
  with nobody having touched the code. Interacting writes are the tell: a
  guard-DISABLED branch from case 4 survives and poisons case 1 on the next run. So the
  negative control can manufacture the very failure that looks like a broken merge.
  **Idempotence is part of hermeticity** — one clean run proves nothing. Assert the
  sandbox explicitly (`closure_path(fixture)` must land INSIDE the temp dir) so the
  layout cannot silently regress, and run it three times consecutively before claiming it.
- **After hardening a check, re-run the negative control.** A hermeticity fix can quietly
  make the suite unfalsifiable — green on a broken tool. Regress the thing the check
  guards, in a copy, and confirm the suite still goes RED.
- **A clean report must state its denominator.** "No issues found" with no count
  is unfalsifiable — it is the same output whether you scanned 400 files or 0.
  Print how many sources you read, and exit non-zero when that number is zero.
- **Don't swallow errors inside the auditor.** A `try/except: continue` around a
  detector turns a crashing check into silently FEWER findings — silent
  wrongness in the one place whose job is to catch it. Collect and surface
  them, and exit non-zero if the output contract says errors are signalled.
- **Never prove a permission/read-failure path with `chmod 000` while running as
  root.** Root reads through it, so the test passes for the wrong reason. Use a
  **directory named `*.py`** — `open()` raises `OSError` for any uid.
- **Beware edits that get clobbered by a sync job.** If a cron syncs
  source→copies, edit the SOURCE and re-run the sync; verify the hash after.
