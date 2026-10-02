---
name: claim-provenance
description: "Use when reporting a number, finding, or status."
version: 1.0.0
author: Gentech
tags: [verification, reporting, evidence, coordination, trust]
trigger: "Before sending any report, handoff, completion note, or answer that asserts a number, a status, or a finding."
---

# Claim Provenance — Every Claim Carries Its Instrument

A report is read by someone who cannot see your session. They can only check what you wrote down.
So the job is not "be accurate" — it is **make each claim checkable by a stranger**, and mark
plainly which claims you actually measured.

## The Core Rule

> **Every number carries its call. Every finding carries its boundary. Every status carries its revision.**

If a claim cannot be checked by the reader, it is not evidence — it is a sentence that happens to
contain digits. No instrument, no number.

**And naming the instrument is only half the claim — the instrument must measure the THING BEING
CLAIMED.** A working, correctly-quoted, perfectly reproducible call aimed at the wrong quantity, the
wrong timescale, or the wrong subject yields a number the reader has no way to doubt. So complete a
second sentence before the claim goes out: *"&lt;instrument&gt; measures &lt;quantity&gt;, over
&lt;window&gt;, for &lt;subject&gt; — which is what this claim is about."*

## Procedure

### 1. Before writing a claim, name the instrument that produced it

For each figure and each finding, be able to complete: *"measured by <command/endpoint/call>, at
<revision>."* If you cannot complete that sentence, you do not yet have the claim — go measure, or
write it as an assumption out loud.

### 1a. A class-based acquittal is only as good as the unit it was computed in

A ledger that counts file content cannot see a **structure** leak. A sync drop may stop unsupported-class
files from crossing while still pushing the **directory entries** that carry them — and the two states
look identical to a content-only measurement.

Measured: a sync excluded `node_modules` by bare name while the real exclusions matched full paths. A
content audit reported "zero unsupported files uploaded" and was correct. But the log showed hundreds of
`Uploading <junk path>` lines and a real `Push: .../node_modules/content-type (updated)` — directory
structure was moving. The acquittal was true about **files** and false about **shape**.

**Rule:** before declaring "nothing leaked", enumerate the unit you measured and the unit you did not.
If your check is class-based, say so; if it cannot see directories, state that limitation. A green
result in one unit is not a green result in every unit.

**A negative finding with the wrong unit is as dangerous as a false positive** — it reads as "no action
needed" when the truth is "the action is happening at a granularity my check cannot see." This is the
same family as "scope your claim to what you measured" and "state the metric".

### 2. Read a derived value from the SAME call that validates its source

Never validate a credential in one request and report a value *derived* from it in the same breath
without a request behind it. One call, both facts — so the two can never separate.

### 3. Label each claim's state explicitly

See `references/claim-states.md`. A reader must be able to tell verified from inherited from
superseded **without asking you**. Unverified work is marked unverified — not omitted, not
inflated with a confident tone.

### 4. Print the RAW pair, never only the derived ratio

Report `used`, `limit`, and the subtraction — not just a percentage. A ratio hides which of the two
inputs moved, and it is precisely the form an unsourced figure hides in.

### 5. Retract in place, struck with a marker — never silently delete

When a claim is shown false, edit the artifact that contains it: strike it, mark the date, state
the measured value beside it. Deleting leaves the reader unable to tell a retraction from an
omission, and a neighbouring file with the same wrong claim will keep being believed.

## Pitfalls

- **A VERIFIED claim sitting next to an UNVERIFIED one makes the invented one look verified.** This
  is the single most believable form a fabricated figure takes. A key validated by a real call
  lends its credibility to the next sentence, and prose carries no per-claim proof — the reader
  cannot tell which claims were measured and which were composed. **Name the instrument for every
  number in the same sentence that states it.**
- **An unsourced number is worse than arithmetic.** If asked "which field did you read?" and the
  honest answer is "I cannot reproduce it", say exactly that. Arithmetic at least has a
  derivation; an unsourced figure has none, and inventing a tidy provenance to close the question
  is the defect, not the fix.
- **Mark the state, do not rely on tone.** "Approximately", "roughly", or a confident declarative
  voice do not encode whether you measured. Only an explicit label does.
- **Scope every claim to the boundary you searched.** A single-tree or single-seat observation is
  not a fleet-wide fact. Write "absent from <the domain I checked>" — never a bare "does not exist".
  A negative from an unstated boundary is byte-identical in output to a sweep that genuinely had
  nothing to find, so the reader cannot distinguish them.
- **A search that failed on FORMAT is not a search that found nothing.** Strengthening the boundary
  rule above: before writing "X does not exist", resolve where X is *configured* to live. Proven:
  "no keypair exists" was reported as fact while a valid keypair did exist — reachable only through
  an env var whose line the first greps missed on FORMAT, not on content. Read the variable out of
  `.env` with a real parser, follow it to the path, then `stat` the path. And keep the two verdicts
  apart: an artifact that EXISTS but is empty/unfunded is a different claim from one that is MISSING
  — say which one you actually measured.
- **A negative claim from a TRUNCATED read is not a search that found nothing.** When output is
  RANKED, the item you are reasoning about may sit in the slice you cut off — so piping a sorted
  list through `tail` (or `head`) and then concluding "the largest X is Y / there are none" asserts
  a boundary you never read. Proven: a checker that sorts DESCENDING by liquidity was piped through
  `tail -20`; the top-ranked entry was truncated away and reported as absent ("the deepest pool is
  ~$5K, everything else is dust") while a $722K pool sat at the head of that very output — and the
  tool was correct all along. Before any "biggest / smallest / none" claim, read the HEAD of a
  descending sort or re-run untruncated, and state the denominator the truncation actually covered.
  Corollary: the same `tail` habit silently truncates any long output, so a defect you are about to
  report in a peer tool must be reproduced against its UNTRUNCATED output first.
- **A pattern that matches the wrong field is not a count of the event you claim.** A grep for HTTP
  status codes (`429`, `301`) on unstructured logs also matches millisecond timestamps, line numbers,
  or byte offsets that happen to contain the same digits — so a "rate-limit event count" can be
  almost entirely false positives. Proven: `grep -E "429|301"` on agent logs reported 301 events
  for one seat and 64 for another; almost every hit was the millisecond field of a timestamp
  (`17:51:13,429`). **Anchor the pattern to the actual field** (`HTTP (429|301)`, `status=429`,
  `rpc error: code = 429`, or parse structured logs with `jq`/Python), and **print every matching
  line before counting** so you can see whether the hit is a status code or a timestamp. The same
  shape appears with exit codes: a bare `cmd | tail -5; echo "exit=$?"` reports the exit code of
  `tail`, not of `cmd` — use `out=$(cmd); rc=$?` or `set -o pipefail` when the command's real exit
  status determines the finding.

- **A negative from a filter you never verified is not a search that found nothing.** Third member
  of the same family: the inert parameter. An API whose `search` argument is silently IGNORED returns
  its unfiltered default payload — real rows, plausible shape — so "no matching record" and "the
  filter did nothing" are indistinguishable in the output. Proven live: a markets endpoint returned
  the identical top-N-by-volume payload for every search term, which would have supported a confident
  "no market exists for this" from a query that never filtered at all. Before reporting a negative
  from any service you have not calibrated, **run it twice with deliberately different terms (include
  one you expect to MATCH) and confirm the response actually changes** — if it does not, the filter is
  inert and the search was never performed. Then cross-check a second, independent source.
- **A search that failed on VOCABULARY is not a search that found nothing.** Fourth member of the
  family: grepping the obvious word and getting zero hits proves THAT TERM is absent, not that the
  mechanism is. Proven: a platform's fee mechanism went out as "not documented anywhere" after a
  zero-hit search for `revenue` through the full docs — the fee was fully documented, priced, and
  settable, under a name describing HOW it is charged (`swapBps`, an "integrator fee", 0.3%–3%, via
  `PATCH tenant fees`). The null result was reported upward as a finding about the platform when it
  was a finding about the search word. **Before reporting any absence, enumerate the synonyms and
  mechanism names and search each** — a charge can be named for its unit (`bps`, `pct`), its role
  (`fee`, `integrator`, `commission`, `take rate`, `cut`), or its movement (`payout`, `settle`,
  `accrue`, `claim`). Then **state which terms you searched**, so the reader can widen the boundary
  you actually covered.
- **A keyword COUNT is not a search — inspect each hit for substring collisions, in both directions.**
  Tallying matches manufactures evidence whether or not the mechanism exists. Proven: searching a peer
  platform for monetization terms surfaced `our_liquidity_share` for `share` and matched `referr`
  inside **`preferred_bridge`** — incidental tokens that would have been reported as distribution
  terms had they not been read in context. Print the surrounding text of every hit and classify it
  (real term / substring artifact / unrelated field) before any count enters a finding; the count
  alone cannot distinguish a monetization term from a coincidence inside another word.
- **The ABSENCE of a number is itself a finding, and it outranks the authority of a headline.** Where
  a claim is normally priced — a prediction market, an order book, a funding rate — then "there is no
  live market for this" is the strongest available answer, and it deserves the same treatment as a
  number: stated plainly and pinned to its instrument. A source asserting an unpriced claim while its
  own venue lists nothing is borrowing the authority of a price that does not exist. Size conviction
  with LIVE liquidity, not lifetime volume — large lifetime volume beside a passed expiry and
  near-zero liquidity is a husk, and it reads as a busy market to anyone skimming.
- **A surface that REWRITES a measurement into a STRONGER claim is the false-value family, not a
  style choice.** A renderer that mapped a sourced zone string onto its own wording turned "low
  efficiency" into "low — SHAPE MISMATCH" for every low reading — while the same payload carried a
  field stating the label DID match the distribution. A low number and a wrong shape are two different
  findings, and the display converted one into the other; the user read it as the system telling him
  his position was wrong, and asked what was actually true. **Before a display restates a measured
  value, name the claim the new wording makes and check the field that could contradict it.** If the
  stronger claim has real evidence behind it (a genuine mismatch flag), gate the wording on that flag;
  otherwise print the sourced text unchanged. A rewrite that ignores a contradicting field is a
  fabricated finding produced by formatting — and it carries the credibility of the number it replaced.
  **And when a surface contradicts ITSELF — a green note beside an amber warning — the cause is often
  not the display at all: it is the RULE, implemented twice.** Two readers re-derived the same
  classification independently and drifted, so the label came from one implementation and the number
  printed beside it was scored with the other's arithmetic. Before editing either message, grep for a
  SECOND implementation of the rule (a private `_shape_of`, a local `min(..., key=...)`, a ternary
  naming the outputs) and collapse both onto the shared module — otherwise you will fix the wording on
  one side and the two will diverge again on the next change. One rule, one implementation, every reader
  imports it.
- **Novelty is itself a claim, and it needs a search for the LESSON.** Before reporting a finding as
  newly discovered, search the vault and the relevant `scripts/` tree for the rule you are about to
  state — by its MECHANISM (`apy`, `annualis*`, `inflated`), not by the subject of the day. Proven:
  an "aggregator APY is inflated; annualising one day of fees is a fantasy-APR trap" finding was
  reported as new while a script written weeks earlier documented that exact trap in those words and
  already computed the honest number. The arithmetic was right; the novelty claim was false — and the
  false novelty claim is the part the reader remembers. "I re-derived a known lesson" is the honest
  form, and it is worth more than an unearned discovery. **This includes the user's own prior
  decisions:** when he says *"check the brain, I had rules in place for this"*, that is a CLAIM about
  the record and the search is the deliverable — grep the vault and the `scripts/` tree for the rule's
  mechanism, quote what it actually says, and answer from that. Measured: the same doctrine he was
  describing from memory was already written down in full, with a gap explicitly named and left open,
  while two answers had already gone out reasoning about it from first principles. Finding his own
  words changed what the right answer was — the open gap in his file, not the behaviour he was
  observing, was the defect. **Search for the rule before reasoning about the rule.**
  **The mirror also holds: RECURRENCE is not novelty either.** Before presenting a story as new, read its DATES — a headline repeating across
  weeks ("talks are close", "reopening imminent") is evidence the situation is STALE, not that the
  event is near, and reporting the latest instance as fresh multiplies the reader's sense of
  imminence with no measurement behind it. Where a claim is normally priced, the absence of a market
  reaction to a repeated headline is itself the measurement.
- **Pin an artifact claim to its revision** (`<hash> @ <commit>`), never a bare hash. A file that
  changed legitimately between your measurement and your reader's makes a correct report look like
  an error, and a bare hash leaves no way to tell which of you is wrong.
- **A DERIVED surface is a cache with no timestamp — read the SOURCE, not the render.** A dashboard, a
generated JSON or a published page is computed at render time, so the moment you change the state it
describes it is stale — and it will return the PRE-change value in a confident, well-formatted way.
Proven: an efficiency figure was quoted from a hub render assembled BEFORE a redeploy, so the report
carried the old book's `97%` while the live book read `37%`. Note which way the error ran: the stale
number was the FLATTERING one, which is exactly why it went unquestioned — a stale reading that
flatters is the one that survives. **After any state-changing action, re-read the authoritative source
(the chain, the live value, the API) before quoting a number**; if you must quote a derived artifact,
state its render time. A render that cannot say when it was computed is not evidence of the state you
just created. And when this bites, correct it in place and say you corrected it — see the retraction
rule above.
- **A rate you REMEMBER is not a rate you measured — price recurring costs from a receipt.** A
  gas/cost/fee figure quoted from a stored constant inherits the constant's staleness while carrying
  your authority. Proven: a per-action cost was published as ~$0.41 off an assumed gas price that the
  chain had moved ~400x away from, and it was repeated across several reports before anyone measured
  one. Note which way the error ran: it AGREED with the conclusion it was supporting, which is how it
  survived. Read the price from the receipt (`gasUsed * effectiveGasPrice`), or quote the live rate and
  state when you read it.
- **An UNPRICED cost is not a cheap cost — "this is expensive" is a claim, and it needs a receipt.**
  The sibling of the rule above, and worse, because it needs no stale constant: a recurring cost can be
  asserted with no measurement behind it at all, as the REASON to stop doing something. Proven: a
  rebuild cost was called an expensive churn and used to argue against rebalancing frequency, without
  ever pricing one. Measured off the chain it was **$0.010 per rebuild (~3 txs)** against **$1.70-$4.28
  a day** of fees — **0.2-0.6% of a day's earnings**. The argument was not merely weak, it was
  backwards, and it almost talked the operator out of a deliberate edge. **A cost estimate used to
  argue FOR or AGAINST an action is a claim under this whole skill.** Before it goes out: read the
  actual per-transaction cost from receipts (`gasUsed * effectiveGasPrice`), multiply by the count of
  operations in one cycle, and state it as a fraction of the thing it is being weighed against. Note
  the direction again — this error also ran TOWARD the conclusion already being argued, which is why
  nobody questioned it. Where the user's stated doctrine is to act MORE often than others, the burden
  is on the measurement, not on the intuition.
- **A comparison against a CACHED reference is a claim about your cache.** Counting outstanding work as
  `<remote>/main..HEAD` reports what your last fetch saw, not what the remote holds — so a stale ref
  yields a confident "N items stuck" while the remote is already complete, and the misdiagnosis sends
  you to repair a working pipeline. Fetch before counting, and prefer the derived state (ahead/behind
  from the tool) over a stored pointer you are reasoning about yourself.
- **A discrepancy you FOUND may be a discrepancy you CAUSED — check which copy is yours before escalating.**
  The rule above guards against naming a cause too early; this one guards against raising an ALARM
  too early. When a comparison surfaces two different values (two addresses, two paths, two configs),
  the first question is not *which is right* but ***which one did I type*** — because a value you
  transcribed by hand into a probe or a shell one-liner is a fresh artifact with its own typo rate,
  and it fails in the direction that looks like a real defect. Proven: two versions of a funding
  address differed, one failed its checksum, and it was escalated as “STOP — before you send
  anything.” The failing copy was the one hand-typed into the diagnostic command (41 hex chars, one
  short); every script read the correct 42-char address from `tenants.json` and was never affected.
  **Two rules come out of it.** (1) *Prefer reading a stored value over re-typing it* — take the
  address from the file the system uses, never from your own transcription of it; a hand-copied
  constant is the hand-typed-equivalent trap in its most dangerous form, because the thing being
  transcribed is the thing money moves to. (2) *A validity check tells you a string is invalid; it
  never tells you which of two strings is the real one.* A checksum, a length test, a linter — all of
  them can only reject. Resolve identity against the AUTHORITATIVE SOURCE (the chain: does this
  address hold the balance and the position?), then report. An alarm that turns out to be your own
  typo spends credibility you will want for the real finding, and it costs the reader the one thing
  you cannot give back: the reflex to believe the next one.
- **A metric's NAME is a claim about what it measures.** A number published under a label implying a
  different quantity will be read and challenged as that quantity — correctly, by the reader. Proven: a
  band-placement score (how far spot sits from the trough) went out as "fee efficiency — is this shape
  earning?", so the user asked why it was not zero while price sat mid-band; **the score was right and
  the name was the fabricated claim.** Name every metric for the quantity its instrument actually
  reads, and where the quantity a reader cares about has NO reader, say so plainly rather than letting
  a neighbouring number stand in for it. **And where a system has more than one MODE, the description
  must name which mode you are in** — the same number means opposite things under different geometry
  (a high placement score is good for one shape and bad for the other), so identical wording for both
  modes leaves the reader unable to tell praise from a warning without already knowing which mode they
  own. Each band's text must state the geometry that produced it, so the sentence is true standing
  alone.
- **An uncalibrated probe reports a healthy service as dead.** A probe is an instrument, so the failure
  it returns is evidence about the probe until you have shown the probe can succeed. Proven: a
  synthetic request drew an edge-block response (a bot filter refusing an unrecognisable client) and a
  harness-shaped 400 for a header it never sent — both surfaced as an AUTH failure on a rail that was
  answering 200 throughout, while the rail actually carrying the traffic went unwatched. **Point a
  monitor at the source that carries the traffic**, give the probe the identity and headers a real
  client sends, and confirm it can return success before believing any failure it reports.
- **An inbound request that asserts YOUR exposure is a claim about your own state — reproduce it
  before you act on it, and answer with what you VERIFIED, not with agreement.** "Safe for you, one
  service, ~10s, your stuff untouched" is written by someone who cannot see your box. Check each part
  against your own system (which process owns the target resource; whether any job of YOURS calls it;
  whether the change touches your config or your dependency graph), then state the residual in your
  own numbers. Repeating their estimate back as an ACK launders their guess into your confirmation.
- **A requested change is a claim that the change is NEEDED — verify that too.** The counterpart to
  the above: an asked-for restart/refresh/reload is only warranted if the running state is actually
  older than the artifact. Compare the artifact's mtime against the running process's start time;
  **an artifact newer than the process consuming it is the real gap**, and an artifact OLDER is an
  ask to be questioned rather than performed. "Somebody requested it" is not evidence it will do
  anything — a no-op change that reports success is the same false-value shape as a failed one that
  reports success.
- **Verify a peer's DISCLOSURE of their own mistake before accepting it — a self-report is a claim
  like any other.** Reproduce each part rather than accepting the apology's shape: praise is not
  evidence, and an error report can be wrong in your favour as easily as against you. **To prove work
  was not LOST when commits interleave, check ANCESTRY, not a diff of two copies.**
  `git log --format='%p' -1 <later-commit>` names the parent — if the other agent's commit IS the
  parent of yours, your work was committed ON TOP of it and the content is in the lineage, a stronger
  and simpler proof than comparing file copies (which shows only that they differ). Corroborate with
  that commit's own `--stat` and with the count of a distinctive symbol the swept work introduced: it
  must be present, and should have GROWN. Then close it plainly and say what you checked.
- **Before calling a peer's finding stale, reproduce it against the revision they named.**
  "Superseded" and "wrong" are different verdicts, and only the reproduction distinguishes them.
- **Re-run a number you inherited before building on it.** A figure passed to you was not verified
  by you; carrying it forward into a third party's report propagates someone else's error with your
  authority attached.
- **Correct your own wrong explanation in place, and say that you corrected it.** A plausible cause
  that was not the measured one is the same defect as a wrong number — leaving it standing is worse
  than having never written it, because the next reader builds on it.
- **Naming a CAUSE is a claim, and the instrument must be able to tell the cause from its
  LOOKALIKE.** A diagnosis assembled from an observation that BOTH hypotheses explain is evidence
  for neither. Proven: a funded book found emptied was attributed to concurrent writers because a
  process list showed several running — reading that list showed READERS (a ledger snapshot, a
  collector, a bin reader), and the actual writer was never identified, so the cause had to be
  retracted. Before a cause goes out, name the observation that would look DIFFERENT if the
  alternative were true; if none exists, you have a hunch. **"I do not yet know what did this, and
  here is the lookup that will tell me" is a complete and honest finding** — it costs far less than
  a retraction, and a cause-claim carries the authority of a measurement it never had.
- **An empty or clean result is a claim like any other.** "Nothing found" needs the same proof as a
  filled result: confirm the command's inputs actually resolved and state the denominator. A check
  that never ran and a check that found nothing produce identical output.
- **A tool that reports zero matches silently is not evidence of absence.** Some search/index tools
  return an empty result set when they fail to traverse a path, when their index is stale, or when
  their query parser silently drops the term — and the output is identical to a genuine empty search.
  Proven: `search_files(pattern='x402', path='/root/vaults/gentech')` returned **0 matches** while
  `grep -ril 'x402'` on the same tree returned **2,378 files**. The tool produced a confident absence
  that was false, and that false absence was reported as a finding about the organization. **Before
  you write "X does not exist" from any tool, confirm with a second instrument that uses a different
  mechanism** — typically `grep -ril` for text in a filesystem, or a direct API/list call for a
  remote catalog. State both instruments and their disagreement; if they agree, you have a boundary,
  not a guess.
- **A monitor that SKIPS the broken state can never report it.** Before trusting a health check,
  confirm it actually inspects the state that goes wrong. A cron health monitor contained
  `if not enabled: continue` and zero occurrences of the word "paused"; a doorbell job had been
  paused for 14 hours; the monitor reported "ok" at the end of it. The check was not wrong — it was
  structurally blind, because the failure mode *was* the state it skipped. Enumerate the states your
  check never visits, and ask which of them would be a failure; then either test them or state plainly
  that they are uncovered. This is the same family as a probe that only hits `:443` while the leak
  lives on `:80`, or a test that only runs on the happy path.
- **Never derive a state from the by-product of an operation you are allowed to skip.** When the
  write gate defers, git is never invoked, so **no push rejection is ever observed**. A "forked"
  detector that inferred forked-ness from the rejection therefore fell through to "retry next tick"
  whenever the gate was saturated — a permanently diverged branch reported as a temporary wait.
  Ask the source of truth directly (`git merge-base --is-ancestor`), not the by-product of the
  action you might skip. The by-product is conditional on the action running; the direct question is
  not. Any state inferred from a side effect that only appears on one branch of a conditional is a
  false negative waiting to happen.
- **"The fix is missing" is a finding, and a text search cannot support it.** Never prove a fix
  landed — or failed to land — by grepping for the fix's own text. The check is wrong in both
  directions and both readings look authoritative: it matches the **comment you wrote describing
  the bug** (false "still broken"), and a pattern containing `(`, `)`, `[`, `]` or `|` is
  interpreted by the shell/regex engine, silently narrowing the match (false "missing"). The second
  sends you back to re-fix correct code. Report a fix as verified only when you **caused the failure
  it prevents** — feed the bad input, assert the bad output, keep it as a regression suite — and
  quote that instrument with the claim. Where text search is genuinely the only option, strip
  comments first and match a symbol/AST rather than a raw string, then say which you did. **Same
  rule as any other claim: name the instrument, and make sure it can give the other answer.**
- **"It ran" is not "it worked" — prove the mechanism can SUCCEED.** Every rule above guards against
  a check that cannot go red; this one guards the mirror: an action that cannot go green. A rail whose
  command line is never accepted by its own callee reports as a normal run — the job starts, exits
  non-zero at argument parsing, and nothing in any status view distinguishes it from a job that did its
  work. Proven: an autonomous rebalance passed `--shape CURVE`/`--BID_ASK` into an argparse whose
  `choices=['curve','bid-ask']` **and** `--mode withdraw-redeploy` into a parser with no `--mode` — both
  parse-time errors, so its shape logic, gas guard and dry-run never executed once, ever. Before writing
  that any mechanism runs, **run the EXACT command the caller builds** (never a hand-typed equivalent —
  re-typing from the docs is how the mismatch stays hidden) and **diff the caller's argument vector
  against the callee's parser**: every flag must exist (`grep -n add_argument <callee>`), every value
  must be in `choices`. Widen and canonicalise the vocabulary rather than enumerating spellings, and
  treat an exit code that NEVER VARIES as the tell — **check the last SUCCESS artifact, not the last run
  timestamp.**
- **The hand-typed equivalent is wrong in BOTH directions.** Above it hides a real mismatch (false
  pass); it can also **manufacture** one. Transcribing a fragment into a probe — nested heredocs,
  re-escaped `"` and `'` — makes it a *different program*: the quoting collapses differently, the
  branch you meant to exercise falls through to its `except`, and the fallback value comes back
  looking like a measurement. Proven live: a resolver re-typed into a nested-heredoc probe returned
  the neutral fallback and read as a genuine defect; run **verbatim** (extract the range with
  `sed -n`/`awk`, or invoke the real entry point) it returned the correct value. **A false failure
  costs what a false pass costs** — it sends you to fix correct code, and it spends the credibility
  you will need for the real finding you report next. Extract the block; never transcribe it.
  **And extracting correctly is not sufficient if you ASSERT in a different process.** A block
  extracted verbatim into a temp file and run as `bash file.sh` sets its variables in the CHILD
  shell — a parent `echo "$VAR"` then prints empty and reads as "the block produces nothing", a
  second false failure from a harness that was already done right. Append the assertion to the
  extracted range and run it in ONE invocation (`{ sed -n ...; echo "VAR=$VAR"; } | bash`). State
  the process boundary the value crossed before calling a variable empty.
- **A HARNESS that reports "nothing happened" in BOTH directions is broken, not evidence.** When
  proving a gated action fires, the test must include a POSITIVE CONTROL — a run in which the action
  MUST happen — because a harness that silently fails to observe an action is indistinguishable from a
  mechanism that never fires, and "0 occurrences" reads identically either way. Proven: faking the
  clock to an overnight hour returned no invocation and was read as "the run is gated overnight" —
  wrong, as the daytime control also returned zero; the harness had been watching the wrong stream the
  whole time, because the action's output is captured into a variable and printed only if the script
  decides to speak, so grepping stdout finds nothing whether the action ran or not. **The working
  recipe for a time-gated or cron-driven action:** shim the clock (a `date` executable first on `PATH`
  that answers `+%H` with the hour under test), stub the side-effecting tool so it **WRITES A FILE**
  (the file is the observation — stdout is not), and run it once in an hour where the action must fire
  and once where it must not. Only a pair of DIFFERING results is evidence; a single zero is not.
- **"Fixed and verified" is a claim about a DIFF — check the commit, not the message.** Extending the
  rule above into the direction the author reports: a peer reported a fix to a reader, quoted its exact
  patched output, and attached a plausible commit hash — the file on disk still held the original bug
  and the commit **never touched that path**. The fix existed only in a commit message. Quoted output
  proves the author RAN something; it does not prove the artifact was written, and a patch can live in
  an editor, a scratch copy or terminal history and never reach the shared tree — after which the next
  sync has nothing to carry and the claim rots into a false belief about live state. The instrument,
  which settles it in one command and is unambiguous when empty:
  `git show <commit> -- <path>` (empty diff = the file is NOT in this commit),
  `git show --name-only <commit>` (what it actually touched),
  `git log --all --oneline -S'<distinctive string from the claimed fix>' -- <path>`.
  **Cite the commit that CONTAINS the diff when you report a fix; `git show` it when you receive one.**
  A commit message describes an intended future, not a recorded past.
- **A withdrawn NUMBER is easier to sweep than a withdrawn CONSTANT — a constant gets baked into an
  artifact that no longer looks like a claim.** Retraction discipline normally stops at prose: strike
  the figure, mark the date, move on. But a number that was *published* is also a number that gets
  *adopted*, and the lifecycle runs: published → adopted as a constant → hardened into a TESTED control
  (with a negative control and a fail-closed exit) → the original number WITHDRAWN → **and the tool
  built from it keeps asserting it, in a docstring or a comment that now reads as measured.** Proven: a
  per-file limit went out as 5 MiB, was built into a tested instrument as a literal, and survived the
  withdrawal of the 5 MiB figure — while the client's real value was 199 MiB set by a server at login
  and the "silent" skip was logged per path by a function literally named `logSkip`. So sweep CODE, not
  only notes, and expect four traps when you do: **vendored trees are other people's constants, not your
  claims** (an SDK docstring saying "5 MiB" about its own chunk; a build artifact matching your number
  as a substring); **match a standalone token**, or your constant hides inside a longer one (`5242880`
  inside `52428800` — the exact error being swept); **look for the EXPRESSION, not just the literal**,
  because the defective value was written `5 * 1024 * 1024` and the literal appears in no file, so a
  registry keyed on the evaluated value is blind to the form the value actually took; and **use stems in
  the marker vocabulary** — requiring a phrase like "CORRECTED IN PLACE" reports a properly-corrected
  note as unmarked, and a false alarm spends the trust the real finding needs. Report both surfaces and
  keep the marker visible rather than deleting the claim: a number printed with its own warning cannot
  be quoted by accident. **And sweep the ASSERTION, not the numeral:** a bare token matches
  MEASUREMENTS — `files >5MB → 102` is a legitimate count of files over a threshold, not a claim that
  the threshold is a limit — so keying on the number produced 13 fleet-wide false positives inside our
  own investigation notes. Key on the sentence that makes the claim ("hard per-file limit", "silently
  never uploaded") and the number can be discussed freely. **Corollary:** a constant you inherited in
  someone else's tool is theirs to audit as much as yours — when you fix it, announce it rather than
  argue about it.
- **A CONTROL WHOSE INPUT IS DATA GOES INERT WHEN THE DATA STOPS BEING NARROW — re-run a peer's
  control after you change the data it depends on.** A guard's reachability can be a property of the
  REGISTRY, not the code, so a correct fix becomes unreachable the moment the fixture stops triggering
  it — and re-reading the diff will not show it, because the diff is still correct. Proven: a
  fail-closed check ("no record's scope engaged ⇒ exit 2") was fixed and verified, then seven new
  fleet-wide records — each legitimately applicable to every file — made the engagement count
  non-zero in every tree, so the condition never fired and a lane the tool cannot see returned a
  PASS. **Only RE-RUNNING the original control exposed it.** So when you change a check's data (a
  threshold, a scope, a registry, a default), re-run that check's NEGATIVE control in the same
  session, and treat "the test still passes" as the reason it is invisible rather than the reason it
  is fine. **And a fail-closed check must distinguish "nothing looked" from "everything looked"** —
  print the coverage that produced the verdict, because a false BLOCKER costs the same credibility as
  a false pass, and both read as confidence.
- **AN OUTPUT CANNOT VALIDATE THE MODEL THAT PRODUCED IT WHEN TWO MODELS COINCIDE — carry the
  derivation, not just the figure.** Two different computations can land on the same number, and then
  the number is evidence for neither. Proven: a projection published as "8.0 and 12.1 months" was
  attributed by a peer to a specific divisor; recomputing both candidate models — `remaining headroom
  / 30.44-day calendar month` and `full cap / 35-day period` — gave `(8.03, 12.22)` and `(8.02,
  12.21)`, **agreeing to 0.006**, because `891.38/1024 = 0.8705` and `30.44/35 = 0.8697`. The two
  ratios match to four decimals, so the numerator's scale factor cancels the divisor's. **Neither
  party could tell from the published pair which model had run — including its own author.** The
  correction was therefore unfalsifiable, and the honest reply was to name the coincidence and state
  the model, not to accept or reject it. **Two lessons:** (1) when two derivations can produce one
  output, publish the NUMERATOR and the DIVISOR, because a projection is a claim about its inputs and
  a bare total hides which ones moved; (2) before attributing a peer's figure to a mechanism,
  check whether an alternative mechanism reproduces it exactly — a coinciding model is
  unfalsifiable from the number, and "your figure means X" is a claim like any other.
- **A constant per-file offset between two versions of a size is CONTAINER overhead, not content.**
  When the same file measures N bytes larger in one column than another and the difference is
  CONSTANT across thousands of files, that is envelope overhead (a length prefix, an IV/tag, a
  checksum) — not a change in the data. Proven: `server_size - disk_size = +28` for 3,349 of 3,364
  files, so the remote column is the ENCRYPTED size and the local column is plaintext. **Direction
  matters: reading the plaintext column and calling it "the payload" makes every figure 28 B/file
  low — not wrong arithmetic, the WRONG COLUMN.** Measure the offset before choosing a column, and
  treat the outliers (13 singletons here) as the interesting set rather than noise.
- **A DETECTOR CANNOT TELL ASSERTING FROM QUOTING — SO A FINDING ON THE NOTE THAT DESCRIBES THE
  DEFECT IS THE TOOL AT THE WRONG ADDRESS, NOT A BROKEN TOOL.** A sweep keyed on a withdrawn figure
  fired twice on the very note documenting the withdrawal, because the note quotes the claim to
  explain the fix. **Three levels of reach, and each was found by a different person: (1) FORM — a
  registry keyed on one rendering (`5 MiB`) cannot see another (`5 MB`); fix: match ANY alias.
  (2) CONTEXT — a form alone cannot tell a CLAIM from a MEASUREMENT (`files over 5 MB: 102` is a
  count); fix: require an assertion cue. (3) META — form + cue cannot tell ASSERTING from QUOTING;
  this one is a LIMIT, not a bug.** **The remedy is to MARK THE ARTIFACT, never to weaken the
  detector:** its verdict ("carries the form with no correction marker") was literally true of the
  note, which contained zero marker words. **Resist the tempting carve-out** — "a code span means it
  is quoted" — measured across one vault, **142 of 590 occurrences sat entirely inside backticks
  across 34 notes, and the original defect had been published in BOTH forms**, so the carve-out would
  have created a false NEGATIVE on the very claim the tool caught. **A code span is a formatting
  accident, not a truth claim.** Silencing a large class to quiet one artifact trades a true positive
  for a blind spot. **Corollary: a measurement is true of its own moment.** A clean sweep read, then
  invalidated by a note written afterwards, is a VINTAGE — say so, and re-run rather than defending it.
- **A GUARD ON ONE MATCHER IS NOT A GUARD ON THE FAMILY — CHECK THE SIBLING.** One file held two
  matchers for the same record: the FIGURE matcher was boundary-guarded (`(?<![\w.])` + escaped token +
  `(?![\w.])`), while the EXPRESSION matcher two hundred lines down was a **raw substring test on
  normalised text**. Normalisation strips spacing and underscores, so `25 * 1024 * 1024` becomes
  `25*1024*1024`, **which CONTAINS `5*1024*1024`** — a perfectly correct 25 MiB threshold was reported
  as the withdrawn 5 MiB cap, in nine places, for months of runtime. **The fix was one predicate, and
  the class was already known: this was the sixth appearance of "a substring wearing a number's
  clothes" (`429` in a numeric field, `5242880` in `52428800`, `348` in `1,348`).** **When you harden a
  matcher, grep for its siblings: same record, same loop, different syntax — and normalisation is
  where boundaries go to die, because the characters the guard relies on may not survive it.**
- **MATCH ON CODE, READ CONTEXT FROM THE SOURCE.** A scanner that checks code for a banned constant
  must not match its own **docstrings and comments** — documentation necessarily SHOWS the form, so the
  tool reports itself. **Blank comments and docstrings before matching, indices preserved; then read
  the CONTEXT WINDOW from the ORIGINAL lines**, so a comment that defensibly names the value a
  conservative pre-filter still suppresses the hit. **Two surfaces, two sources: match the artifact's
  code, judge it by its prose.**
- **AN ARTIFACT THAT REPORTS A DENOMINATOR MUST REPORT THE SCOPE THAT PRODUCED IT.** A `--json` mode
  reported `files_scanned` and `code_files_scanned` with **no root**, while the default scan directory
  was a fraction of the documented scope — so a peer read 773 files, reasonably called it "the whole
  tree", and drew a false conclusion from a true number. **A count with no root is a numerator whose
  denominator never appears.** Emit `root` (and every scan root) alongside every count; the reader
  cannot infer the boundary you silently defaulted to.
- **An instrument failure rendered as a zero is a fabricated measurement.** The read never happened
  and the output reports the quantity as EMPTY — a reverted call, a missing method, a `None` result,
  or an exception caught into a `default 0`. **Never `or '0x0'` / `or 0` / `except: 0` a read on a
  live path.** Proven: an ERC-20 `balanceOf(address)` selector sent to an ERC-1155 LBToken reverts;
  `.get('result')` was `None`; `or '0x0'` turned *a method that does not exist* into *"you own zero
  LP"* and it was reported outward as a fact about the wallet, twice. **A method that does not exist
  and a balance that is zero produce the same characters on screen** — distinguish them by whether the
  call returned a result at all, never by the numeric value. Carry an explicit UNKNOWN state, and
  refuse to emit a total that silently EXCLUDES a leg you could not read: a total missing an owned
  component is the same lie as a zero. **And a fix inside a fix is still a fix** — after patching a
  reader to say UNKNOWN instead of a false zero, the patched code printed `UNKNOWN (read failed)`
  because a broad `except` swallowed an `AttributeError`; print the exception while debugging a repair,
  or the handler will hide the bug you are fixing inside the fix.
  > **Short form:** "A failed eth_call returns 0x → a FAILED READ reads as a real zero."
- **A duplicated constant is not a backup — it is a coin-flip every run.** Every copy of a shared
  endpoint/URL/config value shares the same failure, so one outage disables all of them at once while
  the duplication reads as coverage. When a defect is reported "in your script", grep the whole tree
  for the SHAPE and classify every hit, then report the count fixed against the count found — a fix one
  site short is the normal failure. Patching the VALUE is temporary; collapsing to a single shared
  source is the permanent fix.
- **A provider CAPABILITY limit is not a chain answer.** A rate-limit or block-range cap (`limited to
  0 - 50 blocks range`) looks exactly like an empty result, and a revert looks like a dead provider.
  Classify before acting: a capability limit must ROTATE to the next provider; a revert is a CHAIN
  ANSWER that must not rotate and must not become a zero. Getting this backwards yields either a fake
  outage across every provider or a confident false negative. **A shared client must assert both
  directions in its selftest** so neither reading can silently return. `py_compile` and `ast.parse`
  verify SYNTAX, not name RESOLUTION, so they cannot support a claim that code works. A module calling a
  helper 60 lines above its `def` compiles clean and raises `NameError` the instant anything imports it;
  a whole-repo "all files compile, 0 failures" sweep therefore passes while the tool cannot run AT ALL.
  Proven: an 86-file migration reported 100% green and left a module that could not be imported. The
  instrument for "it works" is a load probe — `python3 -c "import <mod>"` or the script's `--help` — not
  a compile sweep. For anything called at module scope, confirm the `def` precedes every call site.
  **Same rule as every claim here: quote the instrument that can give the other answer.**
- **A WRONG instrument carries its call as convincingly as a right one — and it is the harder defect
  to catch, because every part of it works.** The rules above guard against a check that cannot give
  the other answer; this one guards against a check that answers a *different question*. Four shapes,
  each of which produced a number that would survive any reader's audit:
  - **A classifier whose table no longer contains what the system EMITS.** The instrument was written
    against a fixed set of expected values and a later feature widened the set of values the producer
    can actually output — so a real, in-house geometry fell outside the table and the classifier
    returned its NEAREST MATCH, naming a shape the book was not. Nothing errored; the number was
    plausible and wrong, and in this codebase a wrong shape label had already triggered a rebuild on a
    healthy book. **A nearest-match classifier never fails — it only lies.** Enumerate the full domain
    the producer can emit (import the producer's own constants and vary them; never re-type the
    table), and let the classifier say **"matches no legal geometry"** rather than guessing. Then make
    every caller handle that answer by falling back to the RECORDED label and SAYING SO. Whenever you
    widen what one part of a system can produce, re-read every fixed table that classifies it.
  - **Wrong field.** A verifier checked the RANGE END (`block_range_half_open[1]`) and flagged three
    correct rows as "out of day" — but the range end is BY CONSTRUCTION the next day's first block.
    The field that actually needed verification was `last_block_with_swap`. The verifier was wrong,
    not the ledger; fixing the verifier is part of shipping the claim.
  - **Wrong computation — a number with the SHAPE of a fact.** A cross-bin "pool share" computed by
    summing balances across bins and dividing by summed totals looks like a percentage, but bins hold
    different token mixes (e.g. WAVAX 18dp vs USDC 6dp), so the sum mixes units. The per-bin share is
    well-defined; the aggregate is not. **A number that borrows the form of a valid measurement is worse
    than no number** because it will be used as one. When an aggregate cannot be honest, set it to `null`
    and record why — never publish a plausible-looking placeholder.
  - **A filter that excludes the actual data shape produces a confident zero.** An instrument that
    expects scalar values and silently drops dicts will report `0` even when every real measurement is
    non-zero — the filter was wrong, not the system. The output reads as "nothing found" and is reported
    as a fact. Match the data shape before filtering, and treat a sudden drop to zero as a signal that
    the filter or the reader broke, not that the underlying quantity vanished.
  - **Wrong timescale** — sampling a live price for ~20 seconds to call the tape "quiet" cannot
    describe what the asset did overnight; the verdict was an artifact of the window. Where a source
    already accumulates over the period you care about (a pool's own decayed counter, an oracle's
    rolling window), read THAT rather than starting a stopwatch of your own.
  - **Wrong reference point** — "has it moved too far" measured from a low weeks back turned a slow
    grind into a fresh vertical move, and the system proposed EXITING a position that was quietly
    chopping inside a narrow range. Anchor on what the decision is actually about (distance past the
    range we earn in), not on whichever series happened to be nearest to hand.
  - **Wrong subject** — a per-pool decision driven by a market-wide label sourced from a DIFFERENT
    asset, so a coarse statement about the market silently chose one pool's strategy. Check that the
    instrument's scope matches the claim's subject; a per-pool read beats a per-market label.
  **A guessed API name belongs to this family too.** Assuming a helper called `price_of` raised
  `AttributeError` and fell through to a weaker anchor, which then reported a plausible number all the
  way to the reader. Search for the existing reader before writing or importing one, and never let a
    failed lookup downgrade SILENTLY — a fallback must announce itself in the output, or a degraded read
  is indistinguishable from a healthy one. Same discipline as the boundary rules: say which
  instrument, and say when the one you wanted was not available.
  **And print what a verdict REJECTED, not only what it chose.** A rule with a scope, freshness or
  readability condition that silently drops a case is indistinguishable from a rule that never ran.
  When a signal is near-threshold but excluded for a second reason — too stale, wrong window,
  unreadable input — emit the exclusion. Otherwise the next reader cannot tell "considered and
  dismissed" from "never evaluated", which is its own false negative.
- **A source can be authoritative for its own fields and SILENT on the one you were sent to read.**
  "Get it from the contract" names a source, not a quantity — and the quantity may not exist there.
  Corporate the request before hunting for the call: the contract exposes its fee CONFIGURATION and
  its reserves, but an APR is `fee rate x turnover`, and turnover (volume, history) is nowhere on
  chain in any AMM. So the honest answer has two halves — **what the source does expose** (state it,
  with the call) and **why the requested number is absent** (say it plainly) — and then the number
  from whatever instrument actually measures it. Two traps in the alternative: a published figure
  from a third party carries its own stated assumption (*"assumes full-time in range"*), which is
  precisely what a badly-placed-but-in-range book violates, so it is an UPPER BOUND rather than a
  measurement; and a derived figure you compute yourself inherits the assumption silently unless you
  label it. **Never let "read it from X" turn into a number that X cannot produce.** A wrong source
  and a missing field are different findings, and only one of them is your caller's mistake.

- **A named thing the user asks about is a claim about its existence.** Before building a strategy,
  handoff, or report around something the user names (a council, a project, a protocol, a file), verify
  it actually lives where the name implies. A mandate that cites "the X402 Council" while the vault
  contains zero files for it is a reference to a non-existent artifact — and answering as if it exists
  spreads the false premise. State what you searched, what you found, and whether the named thing is
  real before proceeding.

- **A rate is a claim about a DENOMINATOR — quoting one from a single event is fabrication with
  arithmetic behind it.** When you report that a signal precedes an outcome, the reader is being handed
  a proportion, and a proportion is only as good as the sample beneath it. Count EVERY occurrence
  across a basket of comparable instruments — never just the instrument the question happened to name
  — and print the denominator beside the rate (`3/11`, `59 events across 18 assets`). If the named
  instrument has only one historical instance, that IS the finding: say "one prior instance — not a
  base rate", then widen the sample or decline to give a rate at all. **This failure is most dangerous
  when the claim is one you WANT to be true**, because agreement with your own prior is what stops you
  counting — the discipline has to hold against your own side of the argument, not only against someone
  else's. And check the BASELINE the same way: a signal is only an edge if it beats the unconditional
  rate, so measure both and report the pair (`after signal X: 27%` vs `any week at all: 39%`). A
  "signal" that fires LESS often than chance is a finding, not a confirmation. Watch for the second
  version of this too: **a median is not a distribution** — a fat-tailed series can show a negative
  median with enormous outliers in both directions, and whichever statistic you quote decides which
  story the reader hears. Say which one you used and what it hides.
- **A refusal is a claim too — a blocker you produced by misreading a rule's SCOPE is a false blocker.**
  When a policy, guard list or config gate "refuses" something, that refusal is a finding you are about
  to hand the user as the reason they cannot proceed, so it earns the same proof as any other claim.
  Establish what AXIS the rule governs before concluding what it forbids: a list of approved VENUES
  (exchanges, pools, routers, position managers) is not a list of approved ASSETS, and reading it as one
  silently converts "buy through an approved venue" into the far stronger and far wronger "you may only
  own the tickers on this list". Proven: a rails table naming venues was read as an asset whitelist,
  and a token that was perfectly acquirable through an already-approved venue was reported as refused by
  policy — the user had to correct the scope himself before anything moved. **Before reporting a
  blocker, quote the rule verbatim, name the axis it governs, and check whether the thing you want is
  actually refused on THAT axis** — an unlisted item under a venue-scoped rule is not a refusal, it is
  an unapproved route. And keep the two verdicts apart: *"no approved route exists yet"* and *"the
  policy forbids this"* carry different remedies — the first is a decision to make, the second is a
  wall.
- **A TOOL's refusal is also a claim, and relaying it unread can cost the user real money.** The
  bullet above is a refusal you produced by misreading scope. This is the sibling: a script, guard or
  gate REFUSED an action, and you hand that refusal to the user as the reason they must do something
  — send funds, wait, abandon a plan. You are now the author of a claim whose instrument you never
  opened. Read the code that emitted it before it goes out, and check three things:
  - **Is there an OVERRIDE, and did anyone use it?** A gate whose module header states it *cannot*
    block a stated emergency case usually HAS the flag for it (`--rescue`, `--force`, a bypass arg).
    Measured: a hard `REFUSING TO START` was relayed to the operator as a wall and it talked him into
    funding a wallet — while the module's own doctrine said *"it cannot block a rescue… the reserve
    exists precisely to pay for repairing that"* and a dry run with the override **proceeded with no
    refusal at all**. The refusal was correct for the DEFAULT path and was never a statement about
    the case under discussion.
  - **Is the caller even passing the override?** A bypass that exists and that the scheduled job
    never passes means the automation cannot rescue itself either, and the manual path you tested is
    not the one that runs. `grep -c '<flag>' <the-scheduler-script>` — zero is a finding.
  - **Does the refusal's arithmetic price the operation it refuses?** A cost gate that charges a full
    cycle for an action that performs only part of one inflates the shortfall and can refuse a cheap
    action as if it were the expensive one. Read which steps the refused path actually performs
    before quoting its number.
  **And re-read the blocked CONDITION immediately before you escalate it.** A gate fires on a moment;
  the state can clear on its own between the refusal and the user reading your message. Measured: an
  out-of-range book was reported as *"earning zero, send 11 cents to unstick it"* — and a fresh read
  taken while composing the reply showed it had already re-entered on its own, at 83% efficiency.
  The action was real when it was measured and false when it was sent. **Quote the timestamp of the
  reading, or take a new one** — an escalation asks the reader to act, so it carries the same
  freshness burden as a number.

## Support Files

- `references/claim-states.md` — the state table (verified / inherited / superseded / unverifiable)
  and the label to use for each.

- **A SUPPRESSION MUST BE REPORTED, NOT SILENT.** A hint/tolerance list that lets a sweep drop a hit is
  a false-negative generator unless every drop is counted and attributed. **A false negative and a
  clean file look identical** in an artifact that only prints findings — so print the suppressions too:
  what was set aside, by which word, at which line. The reader can then judge the WORD.
- **A TOOL AND ITS READER CAN AGREE ON THE SAME WRONG ANSWER WHEN THEY ARE THE SAME COMPUTATION.**
  `close()` derived the record's lane by REVERSING the note's lane name and `is_closed()` recomputed the
  same reversal — so the writer found the record it had just written and reported CLOSED, while an agent
  reading their own lane saw zero records. **No disagreement can arise to reveal the error, because there
  is only one computation.** When a writer and a reader both DERIVE a location, the derivation is the
  thing to test — not the write, and not the read.
- **"UNIT COULD NOT BE FOUND" IS A SCOPE ANSWER, NOT A STATE.** `systemctl status X` reports
  "could not be found" for a service that is running and enabled, when X is a `--user` unit — the same
  words a genuinely absent unit produces. Measured: a converged gateway, active for 46 minutes with
  `Restart=always`, read as absent because the query ran in system scope; its cgroup was
  `/user.slice/user-0.slice/user@0.service/app.slice/...` the whole time. **Ask the DIGGING question
  before believing a negative: read the process's own cgroup (`/proc/<pid>/cgroup`), which names the
  manager that owns it and cannot be read in the wrong scope.** A negative from one namespace is a fact
  about the namespace.
- **THE UNIT OF THE CHECK DECIDES WHAT THE CHECK CAN SEE — AND THE UNIT IS OFTEN A SCOPE, NOT A FILE.**
  Tonight the same mistake appeared as a `HEAD~1` that already contained the fix, a regex that matched a
  different lane, and a `systemctl` that asked the wrong manager. **Three different instruments, one
  shape: the selector was wrong and the output looked like a measurement.**

- **A REGENERATED ARTIFACT MUST BE FILED BY ITS GENERATOR, NOT BY ITS CONTENT.** A produced reading
  (a map, a report, a census) changes on every run — three runs gave three hashes — so a record that
  cites the reading is stale the moment it is written, while a record that cites the RULE and the
  COMMAND stays true. **Cite the rule and the generator, plus the `as_of` of whatever reading you saw —
  never the reading alone. An artifact named for a thing that is true only for a second is the same
  defect class as a file whose name implies a state it does not have.**
- **VERIFYING AT THE ARTIFACT IS NOT ENOUGH IF THE ARTIFACT WAS REPLACED AFTER THE VERIFICATION.** A
  spot-check that parses correctly, hashes plausibly and cites the right bytes can still be a revision
  that has since been corrected — and the tell is the `as_of`, not the size. **Compare the reader's
  as-of against the file's, before the number enters a record.**
- **A GREP SEEKS THE REASON IN THE FILE THAT COMMITS THE ACT; THE REASON IS OFTEN IN A SIBLING.**
  A hardcoded path looked like an accident in the script that used it and was a documented decision —
  the comment lived in a *different* script that shared the constant. Searching above the resolving line
  found nothing and the tool still said UNDOCUMENTED. **Search the CORPUS for the rationale before
  filing a defect verdict, and split the class: DOCUMENTED (a decision) vs UNDOCUMENTED (a candidate
  defect) — they are opposite findings and only one is a bug.**
- **RIGHT FACT, WRONG NAMESPACE, COMMITTED WHILE FIXING THIS VERY CLASS.** The instrument error below
  was being written up as a lesson in the same hour it was repeated: a check of MY OWN seat's job list
  was reported as "neither script is scheduled" — a fleet-level claim from a seat-level query. **The rule
  holds for the person holding the rule: state the namespace you queried, every time, including when you
  are certain.**
- **AN INSTRUMENT PRESENT ONLY IN `--json` IS AVAILABLE TO THOSE WHO ALREADY SUSPECT THEY NEED IT.**
  The reader that most needs the provenance is the one reading the DEFAULT line and publishing the
  number; a machine-readable field it never opens does not reach it. Measured: source attribution and
  a 6.26% spread were added to the JSON while the text line still printed a bare `($10.97)` — so the
  human-facing output, the one most likely to be quoted, carried no sign that two sources disagreed.
  **When you add provenance to a structured output, add it to the human output in the same change:
  `($10.92 · coingecko · spread 6.51% ⚠)`. Ask which surface PUBLISHES the number and put it there,
  not only where it is easiest to store.**
- **TWO READERS OF ONE OUTPUT CAN AGREE ON A DEFECT THAT IS IN NEITHER OF THE FIELDS THEY READ.**
  Two agents spent a round comparing a market price with a spot price, agreeing that a valuation was
  unstable, when the valuation was stable in both and the wobble was in a THIRD field. **Name the
  field, not the feeling: "the number that moved" is not a measurement until it is a keypath.**
- **NAME A FILE BY THE READER'S SELECTOR, NOT BY YOUR OWN DESCRIPTION OF IT.** A handoff ACK named
  `ack-safe-to-restart-measured-1705z.md` was invisible to three separate readers who globbed for the
  convention (`*peer-mesh-shadow-window-ack*`) — **the file existed, was correct, and read as ABSENT,
  and the fault was the NAME.** The person who names a file already knows what it says, so the name
  describes the CONTENT; the reader who greps knows only the convention, so they need the CATEGORY.
  **Before saving a file another agent must find, check what THEY will search for — a distinctive
  self-description is a private label on a shared shelf.**
- **A FILTERED COUNT PUBLISHED AS A RAW COUNT IS THE SAME DEFECT AS A TOTAL WITHOUT ITS SELECTOR.** One
  tree gave 337 tracked / 341 on the filesystem / **55 after excluding archives, backups and dated records**
  — and the 55 was the number that got published. **The filter was deliberate and correct (it isolated live
  references from history, which was the question); the LABEL was wrong.** State the exclusion set in the
  same breath as the number, or the reader reconciles against a tree they were never measuring.

- **A COUNT IS ONLY AS GOOD AS ITS PREDICATE — PRINT THE SELECTION, NOT THE TOTAL.** The same one
  directory yielded **12, 9, 8 and 6** for the same question, with no disagreement about any fact, purely
  from three incidental choices: whether the citation had to be on a `Re:` line or anywhere in the body;
  whether the lane had to match one exact name or any name in the family; and whether the first match or
  the first EXISTING match counted. **Publishing the total without the selector makes all four look like
  measurements.** When two people disagree about a count, print the two file lists side by side before
  either defends a number — the difference is usually in the loop, and it is often not yours.
- **CHECK THE DIRECTION OF A CITATION BEFORE COUNTING IT AS EVIDENCE.** A note that quotes the reply is not
  a reply: three of the files in an inflated count were notes citing the ANSWER to them. **A reference to
  the answer is the opposite of evidence that a question was answered**, and both render as a path in a
  body.

- **ALIASING HALF OF A COMPOSITE KEY LEAVES THE OTHER HALF VERBATIM.** When a lookup is built from two
  parts that EACH have synonyms, resolving the ambiguity on one side and passing the other through
  unchanged produces a lookup that is correct for whichever part you happened to think about. Measured: a
  lane name `receiver-to-sender` had the receiver aliased (`entertainment`≡`pixel`) and the sender
  verbatim, so replies written to `entertainment-to-treasury` were invisible to handoffs sent from
  `gentech-treasury` — with the reply citing the handoff by filename. **Cross BOTH sides; then the answer
  set is a product, not a list.**
- **WIDENING A SEARCH EXPOSES WEAK MATCHES THAT WERE ALWAYS WRONG, ONLY UNREACHABLE.** Adding locations to
  a scan surfaces every loose predicate that never previously had anything to match in the new place. This
  is not a side effect of the widening; it is the widening's first useful output. Measured: aliasing the
  sender made a newly-reachable lane match a DATE-ONLY topic by substring, so `2026-09-28` "answered" a
  daily roundup via `2026-09-28-some-other-note.md`. **Budget for a second fix whenever you widen, and
  diff the verdicts rather than reasoning about the change.**
- **A GUARD HOISTED OUT OF ITS LOOP SILENTLY DISABLES EVERY ITERATION BUT THE FIRST.** A `seen` set
  declared above `for base in roots:` is fully populated after the first root, so every later root scans
  nothing — and a scan that stops early prints exactly what a scan that finds nothing prints. **Dedupe
  per iteration, and treat "the loop that searches everywhere" as a claim to test, not a structure to
  read.**

- **A CHECK THAT CANNOT PASS IS WORSE THAN NO CHECK, BECAUSE IT TEACHES THE READER TO SKIP IT.** A
  verification step whose expected output can no longer occur (a vault id that has been replaced, a host
  that has moved, a filename a tool no longer writes) is read once, fails, and thereafter is passed over.
  **The failure mode is not the false alarm — it is the trained habit of the reader.** When an identifier
  under a check changes, the check is part of what changed.
- **A VERIFICATION STEP'S EXPECTED OUTPUT IS A MEASUREMENT, NOT A QUOTATION.** Copying the expected value
  forward from the doc that documents it makes the check a restatement of its own source. Read it off the
  live system, and record which value is dead beside the live one so the next reader does not restore it.

- **A REMEDY CAN OUTLIVE THE TOOL IT WAS WRITTEN FOR — AND THEN THE SAME REMEDY IS THE DEFECT.**
  A return filed in `_archive/` could only be found by MOVING it back into the live lane; once the reader
  learned to read the pointer in filed dirs, moving it would have been the wrong act, and the filed
  location became the correct one. **The identical symptom had two opposite correct remedies, and which
  one is right depends on WHICH TOOL IS DEPLOYED.** So a remediation step is a claim about a tool version:
  when the tool changes, re-read every workaround that exists because of it, or the fix becomes the fault.

- **WIDENING WHERE YOU LOOK IS NOT THE SAME AS WIDENING WHAT COUNTS.** Extending a search to more
  directories does nothing if the TEST applied inside them is unchanged: a return filed in `_archive/`
  stayed invisible after `_archive/` was added to the search, because the only test that could match it —
  a body scan — was skipped there by design. When a fix adds locations, re-check the predicate that runs
  *in* the new location, not just the loop that reaches it.
- **TWO CORRECT GUARDS CAN CONJOIN INTO A FALSE NEGATIVE.** Each guard was right on its own (a filename
  test cannot see a differently-titled reply; a topic scan must not run in a filed dir, where a mere
  mention would answer a handoff it never addressed) — and together they made a genuinely answered handoff
  unfindable. **A conjunction of individually-justified guards is a place to look for blind spots; the
  remedy is usually a THIRD, more precise signal, not weakening either guard.**
- **ASK WHAT A DOCUMENT SAYS IT ANSWERS, NOT WHAT IT MENTIONS.** A `**Re:**` line naming the target by
  filename is a deliberate claim; a topic mention is not. Substituting the precise claim for the loose one
  closes the false negative without reopening the false positive the loose test was disabled to avoid.

- **DERIVE NOTHING YOU CAN LOOK UP.** A path built by transforming a NAME is a guess about a naming
  convention that can be asymmetric, and a name can have no inverse at all (`pixel-to-gizmo` has never had
  a `gizmo-to-pixel`). The note's own directory exists because the note does; anchor there. **A transform
  that fails loudly is safe; the same transform with `exist_ok=True` INVENTS the place it could not find,
  and nothing reports it.**
- **A PLACE THAT LOOKS LIKE DEBRIS CAN BE THE ONLY COPY.** A directory holding records and zero notes
  looks exactly like an empty one, so a "prune empties" sweep would delete the sole on-disk evidence that
  a handoff was ever closed. **Before deleting an "empty" structure, ask what made it empty** — and check
  whether anything POINTS INTO it. The record is the pointer, so the deletion destroys an index, not just
  a file.

- **A MARKER LIST ASSEMBLED FROM ORDINARY ENGLISH IS A SILENCE GENERATOR.** "error", "substring",
  "conservative", "assumed", "misread" appear by accident in ordinary commentary: measured, any of them
  within four lines silenced a genuine stale constant, and the stated justification for them (the tool
  matching its own docstring) was already handled by AST-blanking the prose. **Keep only phrases that
  name the ARTIFACT'S STATUS and cannot appear by accident.** When the exclusion is about the FILE
  rather than the value, exclude the file by path instead of widening the word list.
- **A BEFORE/AFTER IS NOT QUOTABLE WHEN BOTH TERMS MOVED.** "17 → 0" concealed four separate changes
  and an 8,285-file shrink in the denominator. Report the change and its universe; a fixed numerator in
  a changed denominator is not a result, it is a headline.
