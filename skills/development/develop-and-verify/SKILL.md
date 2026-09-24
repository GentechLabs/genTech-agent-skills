---
name: develop-and-verify
description: "Use when building, fixing, or changing ANY code or asset — and whenever you find a bug while working. The Jr/Sr default (DeepSeek V4 writes, Kimi K2.7-code audits), the fix-it-don't-ask rule for bugs found in scope, and the silent-wrongness checklist. Fleet standard, Jordan 2026-09-21."
version: 3.0.0
author: gentech
tags: [build, audit, workflow, jr-sr, bug-discovery, silent-wrongness, fleet-standard]
---

# Develop & Verify — Consolidated Pipeline

## Media Pre-Publish Verification (Video/Audio/Images) — added Aug 31, 2026

**Jordan's directive:** "make sure everything is being verified before we put it out for the final" — applies to animated/demo videos, narrated content, thumbnails, and any media shipped publicly (hackathon judges, YouTube, X). Same DONE-means-verified bar as code.

### Frame-level encoding audit (caught live: em-dash mojibake in 0G demo v1)
Every rendered frame/card gets a vision-model readback BEFORE video assembly:
- [ ] **Mojibake scan** — vision_analyze each rendered frame asking for ANY special characters, mojibake (â€", â€™, Ã©), tofu boxes (□), or U+FFFD. Em dashes, smart quotes, and arrows (→) are the repeat offenders.
- [ ] **Pure-ASCII rule for rendered text** — generated HTML/SVG frames MUST declare <meta charset="utf-8"> AND use ASCII-only copy (hyphens not em dashes, '>' not →). The demo runbook rule now applies to video frames.
- [ ] **Font-glyph check** — verify the rendering font actually contains every glyph used (DejaVu covers →, most terminal fonts do NOT).

### Fact/number verification against live sources (claims in frames)
- [ ] Every number rendered in the video is re-checked against the LIVE source in the same session (not memory): chain IDs, balances, prices, versions, amounts.
- [ ] Every claim ("4/4 tests pass", "TEE-verified") is traceable to a real captured artifact (log file, API response) stored alongside the project.

### Audio verification
- [ ] Duration check with ffprobe (>3s, matches intended length ±10%).
- [ ] Voice = intended voice (correct voice_id used), no truncation of the final sentence.
- [ ] Cloned voices: segments ≤35s, model eleven_multilingual_v2 (see elevenlabs-voice-generation skill).

### Assembly verification
- [ ] Final render watched end-to-end (or ffprobe duration == expected sum of cards).
- [ ] Audio/video lengths reconciled (-shortest artifacts checked — no abrupt cut).
- [ ] File delivered to ALL required surfaces: repo (raw 200 verified), vault commit, chat MEDIA delivery.
- [ ] Prior-version cleanup: superseded files removed or explicitly marked deprecated in README/repo.

### Pipeline placement
Media builds run the same 5 phases: PLAN (storyboard + fact list w/ sources) → BUILD (render frames/audio) → **REVIEW (vision-audit every frame + audio check — the AUDIT gate is where mojibake gets caught)** → FINISH (assemble, mux) → VERIFY (numbers re-checked live, raw URL 200, file sizes match).

## Core Pattern — Three Tiers

| Phase | Model | Provider | Cost | What |
|-------|-------|----------|------|------|
| **DEV (Jr)** | DeepSeek V4 Flash | **the active worker rail** (see below) | ~$0/M out | Draft code, make it functional, pass tests |
| **AUDIT (Sr)** | **Kimi K2.7-code** | **the OTHER rail** (resolved at call time) | ~$0-2/M out | Code tracing, bug hunting, security, architecture review |
| **BIG BOY** | Kimi K3 | either rail | ~$15/M out | Architecture decisions, security audits, design reviews, full-codebase analysis |

**DUAL-RAIL ROUTING (Jordan, Sep 21 2026 — this is the rule):**

> *"We need to be able to switch between providers depending on our situation. Last night we were
> using opencode-go but as soon as Ollama Cloud is back, we are back to our original and no longer
> using our fallback. So this rule needs to go for both providers that we use, so that when we
> switch between the two it just works."*

We run on **two rails, and we switch between them by circumstance** — not by editing docs:

| Rail | Role | Notes |
|------|------|-------|
| `ollama-cloud` | **primary / original** | the default. When it is healthy, we are here. |
| `opencode-go` | **fallback** | used while ollama-cloud is capped/degraded. NOT retired. |

**The auditor is ALWAYS resolved at call time on the rail the worker is NOT using.** That is what
makes verification genuinely cross-provider. Never hardcode the auditor to one provider — a
hardcoded rail is exactly the bug fixed on Sep 21 (see below).

**Resolve it, never assume it:**
```bash
python3 /root/.hermes/scripts/audit-model-resolve.py            # worker -> auditor
python3 /root/.hermes/scripts/audit-model-resolve.py --explain  # full candidate table
python3 /root/.hermes/scripts/audit-model-resolve.py --selftest # prove BOTH rails work
```
It reads the **active provider from the profile's own config.yaml**, picks the best auditor
against it, and **declares the downgrade when it cannot get a different provider**. If nothing is
available it exits non-zero — so no caller can claim a verified result on nothing.

> **⚠️ BUG FIXED Sep 21 2026 — the auditor rail was silently single-rail.** The resolver read
> `^provider:` **anchored at column 0**, but our configs nest the key under `model:` indented two
> spaces. The regex **never matched** and the function fell through to a **hardcoded default of
> `opencode-go`**. While we ran on opencode-go it was *coincidentally right*, so nothing looked
> wrong. The moment we switched back to ollama-cloud it was **wrong**: it believed the worker was
> opencode-go, excluded opencode-go from the candidates as if it were the worker's own rail, and
> then labelled a **same-rail auditor** as *"cross-provider + cross-model (strongest available)."*
> A false green in the one place whose entire job is to not produce false greens. Fixed to parse
> the YAML properly; now correct on **both** rails with no edit when we switch, guarded by
> `--selftest`. Related: the config is not the only column-0-anchored reader we have had — prefer
> a real parser over a regex for nested keys.

**Provider status history:** GLM-5.3-flash via **Z.AI is DEAD** (`1113 Insufficient balance`) —
**do NOT route to it or name it as the auditor.** Ollama Cloud previously hit a weekly cap (429,
resets weekly) — that cap is why the fallback rail exists and must keep working.

**Rule of thumb:** Start with Flash. If it fails or output is wrong, retry on K2.7. Only reach for K3 when the answer is worth $15. Jordan's directive (Jul 27, 2026).

## Modular Build Strategy

Build every component as a **pluggable module** — not a monolithic project. This lets us enter multiple hackathons without rebuilding from scratch.

**Core principle:** Each piece (x402 gateway, ERC-8004 identity, AgentEscrow, Agent Credit Score) is a standalone module. To enter a new hackathon, we swap the settlement layer (Arc, Solana, Base) and keep the agent logic. Config changes, not rewrites.

**Proven pattern (Jul 2026):**
- Arc Programmable Money Hackathon: x402 contracts deploy to Arc with config change + new deploy script. Agent logic unchanged.
- XPRIZE ($50K Circle Prize): Same stack, add Gemini API call + Google Cloud product. No rebuild.
- Future hackathons: Same modules, new chain config. Days, not weeks.

**Hackathon qualification shortcut:** When Jordan asks "do we need to build something or do we already have it?" — the answer is usually "we have it, just needs a config change." Our existing live infrastructure (x402 gateway, ERC-8004, AgentEscrow, Agent Credit Score) qualifies directly for agentic payments / agent economy hackathons. Don't plan a new build unless the specific track requires it.

## Big Brother Audits — Model Strategy

You don't need every model to be the best. You need a **cheap coder + a powerful auditor**.

| Pattern | Coder | Auditor | Cost vs using auditor for everything |
|---------|-------|---------|--------------------------------------|
| **Current** | DeepSeek V4 Flash (Jr) | Kimi K2.7-code (Sr) | Both free on Ollama Cloud |
| **Local fallback** | Nemo Tron 12B (free) | K3 (BlockRun — $3/M in, $15/M out) | ~90% cheaper than K3 for everything |
| **Emergency** | Mistral 7B (free) | Claude Opus (pay-per-call via Gata $20/mo) | ~95% cheaper than Opus for everything |

The auditor doesn't run every call — it spot-checks the important ones. The **AUDIT phase** in the build pipeline is where the expensive model goes. The **DEV phase** uses the cheap model for the bulk of the work.

For audits that need a frontier model (Opus 4.8, GPT-5):
- Use **blockrun_chat mode="coding"** or mode="powerful" for one-off reviews
- Use **Gata Starter ($20/mo)** as a fallback if OpenCode Go is down — gives access to Opus 4.8, GPT-5, Gemini 2.5 Pro with automatic failover

**Total infrastructure:** ~$62/mo ($20 Ollama Cloud Pro + $42 VPS) — OpenCode Go retired, Hermes portal (Nous) is the free fallback

## Fast-Track Rule

When Jordan provides a clear task list from prior context (status report, build queue, green-lit design doc), skip brainstorming. Jump straight to plan or build. **Karpathy gates still apply.**

## Build Pipeline (5 Phases)

### Phase 1: PLAN
- Check what already exists (`ls`, `find`, `pytest` existing tests)
- Break work into bite-sized tasks (2-5 min each)
- Each task: exact file paths, code outline, verification step
- **Karpathy Gate:** Every task has testable success criteria, not "make it work"

### Phase 2: BUILD (DEV — DeepSeek V4 Flash on Ollama Cloud)
- Write failing test FIRST (TDD: RED → GREEN → REFACTOR)
- Write minimal code to pass
- **Karpathy Gates:**
  - No features beyond what was asked
  - No speculative abstractions
  - Touch only what you must
  - No "improving" adjacent code

### Phase 3: REVIEW (Sr — Kimi K2.7-code on Ollama Cloud)
- Security scan (no hardcoded secrets, no injections)
- Plan compliance check
- **Specific audit checks that catch real bugs:**
  - **Error detail leakage** — `str(e)` in exception handlers leaks stack context to clients. Fix: log with `exc_info=True`, return generic error message without `detail=str(e)`.
  - **Log injection** — User-controlled input (URL params, headers) logged via f-strings allows log forging. Fix: sanitize with `safe = input[:64].replace("\n","").replace("\r","")`, use `%r` parameterized logging.
  - **Input length bounds** — Regex patterns without max-length pre-checks allow ReDoS-adjacent resource exhaustion. Fix: enforce max length before regex matching.
  - **Race conditions in async counters** — `global count; count += 1` is not atomic in async contexts. Use `asyncio.Lock` or a proper metrics library.
- **Weak randomness for identifiers (CWE-338)** — `random.randint()` or `hash(str(ts))` for scan/request IDs is predictable and collision-prone. Fix: use `secrets.token_hex(16)` or `uuid.uuid4()`. This applies to any generated ID that could be enumerated or guessed (scan reports, payment requests, session tokens).
- **Pre-compile regex patterns at module load** — `re.search(pattern_string, text)` in a loop recompiles the pattern on every call. For modules that scan many inputs (tool descriptions, URLs, configs), compile all patterns once at module level: `_COMPILED = [(re.compile(p), label) for p, label in RAW_PATTERNS]`. Then use `pattern.search(text)` in the hot path. Also prevents ReDoS by keeping compilation cost out of the per-input loop.
- **Individual try/except per sub-operation, not one big wrapper** — When orchestrating multiple independent sub-scans (identity check + MCP scan + x402 audit), wrap each in its own try/except. A failure in one sub-scan should not prevent the others from running. Log with `exc_info=True` and let the result be `None` — downstream checks handle `None` gracefully.
- **Operation ordering in security-sensitive code** — Signature verification, auth checks, and access control must execute BEFORE any state mutation (caching, persistence, database writes). A verify-then-cache ordering bug lets an attacker poison the cache with forged data even when their signature fails. Fix: verify first, then mutate state. This applies to payment middleware, webhook handlers, and any endpoint that validates then stores.
- **Runtime-only variable name errors after renaming a dict/var** — Renaming a module-level variable (e.g. `KNOWN_SERVICES` → `KNOWN_SENDERS`) leaves stale `Name` references in down-branch code paths. These pass `ast.parse` (the old name is still a syntactically valid Python identifier) but crash with `NameError` at runtime the first time that branch executes. Fix: after renaming any module-level variable, run `grep -n 'OLD_NAME' <file>` to catch every reference — don't trust that the linter caught them all. The linter is blind to this because the old name may still be assigned elsewhere, or the down-branch is enclosed in a `try/except Exception: pass` that swallows the error.
- **Persistence verification:** `cat` each modified file — does content match expectations? `git diff --stat` — verify changed files list matches what was modified
- **Karpathy Gate:** If something seems wrong, stop and name the confusion

### Phase 4: FINISH
- Run full test suite
- Commit and push
- Verify deployment (curl the URL, check the output)

### Phase 5: VERIFY (mandatory after every action)
**"Done" means verified, not declared.** Before declaring any task complete:
```bash
# File persistence
ls -la <file_path>
cat <file_path> | head -20

# Git persistence
git status
git diff --stat
git log -1 --oneline

# Deployment (static files behind CDN) — check BOTH origin and public URL
curl -s http://localhost/<path>          # Origin (nginx) — confirms file is served correctly
curl -s https://domain/<path>            # CDN — may be stale if Cloudflare caches
curl -s https://domain/<path> | grep -c "expected content"  # Content check, not just HTTP status
```
**⚠️ CDN verification gap:** An HTTP 200 from `curl https://domain/path` does NOT mean your new content is live. If Cloudflare (or any CDN) has a cached version of the old page, it returns the cached response even after nginx serves the updated file. The status code is correct but the content is wrong. Always:
1. Verify locally first (`http://localhost/path`) — confirms nginx + filesystem are correct
2. Then verify via CDN (`https://domain/path`) — but do a *content check*, not just a status check
3. If CDN is stale, you need to either:
   - Purge the Cloudflare cache (dashboard or API)
   - Remove any Worker route that intercepts the path on the root domain
   - Add a cache-busting query param (`?v=<timestamp>`)
4. File size comparison: if `curl -s https://domain/path | wc -c` differs significantly from the local file size, CDN is serving a different version (compressed or cached) — investigate.
- **Karpathy Gate:** If something seems wrong, stop and name the confusion
## Pre-Publish Audit Checklist

Run through **Kimi K2.7-code** (Ollama Cloud) before pushing to public repos:

### 1. Hardcoded Secrets
- [ ] Any hardcoded API keys, tokens, or passwords?
- [ ] Any wallet addresses (0x...) that shouldn't be there?
- [ ] Any personal names, emails, usernames?
- [ ] Any absolute paths (/root/, /home/, /Users/)?

### 2. Security
- [ ] API keys read from env vars, not hardcoded?
- [ ] Error messages sanitized (no raw exception leak)?
- [ ] Input validation present (regex, bounds, charset)?
- [ ] Startup failure if required config missing?

### 3. Code Quality
- [ ] Syntax errors checked?
- [ ] Proper HTTP client management (shared, not per-call)?
- [ ] Resources cleaned up in `finally` blocks?
- [ ] Unused imports removed?
- [ ] Type annotations complete?

### 4. Open-Source Readiness
- [ ] LICENSE file present (MIT)?
- [ ] README with install + config instructions?
- [ ] `.gitignore` excludes `__pycache__`, `.env`, `.venv/`?
- [ ] `.env.example` with placeholder values (no real secrets)?

## Anti-Temptation Rules

1. **No building beyond the plan** — If it's not in the plan, it doesn't get built
2. **Build easy to hard** — Quick wins first, they build momentum
3. **No optimizing before it works** — Make it work, then make it fast
4. **No refactoring without tests** — If there's no test, you can't refactor
5. **No skipping audit** — Every build gets a **Sr** pass (Kimi K2.7-code) before moving on
6. **No "just one more feature"** — Scope creep kills submissions
7. **No silent assumptions** — State what you're assuming in the log and keep going
   > The trailing "or ask" was removed on Jordan's directive (Sep 21, 2026). It sat there as
   > written permission to stop, and it produced ask-creep: 50 questions where the answer was
   > already obvious. An assumption is not a question.
8. **No drive-by improvements** — Touch only what you must
9. **No declaring done without proof** — Verify persistence before stopping

## Bug Discovery — Fix It, Do Not Ask (Jordan, Sep 21 2026)

> *"A lot of times we find stopping points pretty often and instead of just continuing through
> I'll be asked 50 questions to fix it… if we're actively doing stuff and you'll say 'hey, I
> discovered this bug, do you want me to go ahead and patch that?' — by the fall, we should
> already go ahead and do that."*

**When you find a bug while working, fix it. Then report what you fixed.**

Discovering a defect *inside work already in scope* is not a new decision — it is the work.
Do not stop to ask permission to do the thing you were already sent to do.

**What this looks like in practice:**
- Find it → fix it → verify the fix → **log it** (what broke, what you changed, the proof) → next item.
- The report is the deliverable. "I found X, fixed it as Y, verified by Z" — not "I found X, want me to fix it?"
- An honest blocker still gets reported. But a *bug you can fix* is not a blocker.

**Where planning DOES live** (and this is the distinction Jordan drew):
- **Build queue / Jordan's list / pending** — for bigger projects, plans, things needing his call.
- **Active work** — bugs found in flight get fixed in flight.
Planning is deliberate. Working is not.

**Stop and ask only for:** money movement · a public release · a legal/account/platform action ·
an approval gate Jordan explicitly owns · a hard blocker with no path forward.
Everything else: decide, act, log the assumption, continue.

## The Permanent-Fix Rule — fix the CLASS, not the instance (Jordan, Sep 23 2026)

> *"Whenever we're fixing something, we want to look for permanent solutions to the bugs and the problems
> that come up. So instead of fixing something in its temporary, we want to verify that it's a permanent
> solution. That should be how it is going forward — for everybody and all the groups."*

**Fleet-wide. Every seat, every fix.** A fix is not done when the symptom stops; it is done when the defect
**cannot recur** — and you can say **why**.

### The case that produced the rule (Treasury, Jun 30 2026)

A monitor reported the wrong LP shape and a stale price. **Fixing the numbers would have been the temporary
fix, and it would have come back the same day** — because the defect was not the numbers:

- **three** copies of `.lfj-aae-config.json` existed with different data (one correct, **two stale**);
- `HERMES_HOME` resolves differently in cron than in a shell, so scripts silently read a **stale** copy;
- **two** cron jobs wrote the same dashboard JSON, so a correct write was **overwritten seconds later**.

The permanent fix was `lp-monitor-v2.py`: hardcode the one true path, read only from config + live API, and
**delete the shared intermediate file entirely** so there is nothing left to race over. The old jobs were
**removed, not patched.** *"File locks and read-only flags are band-aids; removing the dependency is the
cure."*

### The test — run this before calling ANY fix done

| Temporary (a band-aid) | Permanent (the fix) |
|---|---|
| Corrects the value | Removes the path that produced it |
| Adds a lock / retry / flag around the race | **Removes the shared dependency** so no race exists |
| Patches the one call site reported | Patches the **transform**, then greps for the transform |
| Syncs the copies | **Deletes the stale copies — they ARE the bug** |
| Works in this shell, this context | Works in cron, in a shell, and **after a restart** |
| "Fixed" | "Fixed, **and here is why it cannot recur**" |

**The highest-value move is almost always: delete the duplicate.** A second copy is not a backup when
nobody knows which is authoritative — it is a coin-flip the code takes on every single run.

### Prove it, do not assert it

1. **State the class, not the instance.** *"This was not one wrong number; it was N readers of one file."*
2. **Kill the recurrence path, then search for the shape again** — `grep` the old read, the old path, the
   old helper. A fix one call site short of the end is the normal failure.
3. **Guard it.** Add a regression check to the selftest so the defect fails **loudly** if it returns —
   that is the step that converts "fixed" into "cannot silently recur."
4. **Verify BOTH directions** — it fires when it should, and stays silent when it shouldn't.
5. **Ask what a restart / update / redeploy would undo.** A fix that evaporates on the next deploy (an
   uncommitted live patch, or a vault-only edit while cron runs the *deployed* copy) is temporary no matter
   how correct it looks today.
6. **Say "permanent" only with the reason attached.** "Permanent" is a claim, and an unfalsifiable claim is
   the exact class this pipeline exists to catch. Write *why* it cannot come back — **if you cannot write
   that sentence, you have a temporary fix; label it one.**

**Boundary — what this must NOT be read as.** Permanence is a property of the *fix*, not a licence to
rebuild. Rewriting a working subsystem to make it "more permanent" is scope creep (anti-temptation rule 1).
The only question is *"will this defect return?"* — never *"could this be nicer?"*

## The Jr/Sr Default (fleet directive, Sep 21 2026)

**Every agent, on any build — not a Labs speciality.**

```
Jr  (DeepSeek V4 Flash)   write it, make it work, pass the tests      ~$0
Sr  (Kimi K2.7-code)      read it back, hunt what Jr cannot see       spot-check
```

**The division of labour is the point.** Jr produces; Sr distrusts. **The author of code is the
worst person to audit it** — they check it against what they *meant*, not what they *wrote*.
Sr reads it cold and asks: *"what would make this print a confident wrong answer?"*

### What Sr is for — and it is not style

Not formatting, not preferences. **Silent wrongness.** Every item below passes a linter and a
happy-path test, and every one produced a wrong answer in a single night:

| Bug | What it printed |
|---|---|
| bare `except: return {}` | an entire balance block vanished — looked like "nothing to report" |
| `0x`-prefixed topic filter | **"no rebalances"** with total confidence, having matched nothing ever |
| action fn with no expiry check | a **10-day-old** stand-down, reported as current, daily |
| hard-coded `int(21.33 * 1e6)` | the **wrong amount** sent, irreversibly |
| missing `positionUsd` after a rewrite | **`$0.00/day`** beside a 163% APR |
| stale "CONFIRMED" in a buy list | **"ZERO COQ pools above $50K"** — there was a $705K pool |

**Six bugs. Not one raised an error.**

### The checklist Sr runs

- **Never swallow an exception bare.** A swallowed error is a false negative that reads as a fact.
- **Empty because nothing happened, or empty because the check failed?** The output must say which.
  "Unknown" is valid. "Zero" is not, unless measured.
- **Verify the refusing direction.** A boundary never tested in the direction it blocks is not
  known to work.
- **Hard-coded value in an executing path?** Make it required, or give it an expiry that is checked.
- **After rewriting a function, diff its RETURN SHAPE.** Callers depend on fields that vanish silently.
- **After a fix, re-audit — and re-test what the OLD code gave you for free.** A fix for a bug in a
  text/data transformer silently drops behaviour the previous implementation had. Proven: replacing
  `str.title()` with a custom title-caser fixed substring corruption (`solana`→`SOLana`) but lost
  hyphen-boundary casing (`On-Demand`→`On-demand`) — a live regression in the same function, invisible
  because every check counted fields instead of reading text. Ask: *what did the thing I replaced do
  that I am no longer doing?*
- **A single audit pass is not an audit.** Round 1 found an original bug; round 2 found the regression
  introduced by fixing round 1. Audit the FIX, not just the original change.
- **Fixing a bug class one call site short of the end is the normal failure.** When an audit reports
  "`x or 0` on fields A, B, C", the fix belongs to the COERCION, not to A, B, C — otherwise the same
  bug survives on the neighbouring fields and re-audit finds it. Proven: a missing-field→0 fix landed on
  the four reported keys and left three adjacent ones bare; a later round found the *optional-field*
  helper doing the same thing, which also re-opened a crash class an earlier fix had closed. Two rounds
  lost to fixing call sites instead of the pattern. **Rule: fix the transform, then grep for the
  transform.**
- **A cross-check whose emitter does not exist is not a cross-check.** Adding a "wallet scanned must
  equal wallet named" guard in the parent is inert if the child never emits the scanned address —
  `.get()` returns None, the comparison is skipped, and the check can never fail while looking present
  in the code. After adding any guard, confirm the INPUT it reads is actually produced, and prove the
  guard fires by feeding it a mismatch. Same family: a tolerance scaled to the WRONG quantity (1% of
  total capital to compare two valuations of the DEPLOYED amount) passes almost any real divergence.
- **When you scale a threshold, check the direction and then check the OUTPUT.** A bin-step scaling
  written as `30*step/10` instead of `30/step` produced a window that swallowed the entire position;
  the code ran clean and nothing errored. The tell was the metric jumping 35.8% → 98.8%. A number that
  suddenly reads "everything is fine" is a signal to inspect the window, not a result to report.
- **Two independent valuations that agree are worth more than one confident number.** A "ledger says X"
  and a "chain scan says X" that reconcile to <0.1% closed a weeks-old "the ledger under-reports by 6.7%"
  ticket — the gap was a decode artifact, not a real discrepancy. Keep the cross-check LIVE (emit the
  delta) rather than resolving it once: a divergence alarm that never reaches a human is not an alarm,
  and a "we disagree" result must have its own display branch — otherwise it falls through to
  "unavailable" and a check that ran and FAILED reports as a check that did not run.
- **"Found a value" is not "found a working value."** A config/credential reader that returns the first
  match will happily return a dead one. Probe the candidate (auth call, parse, exec) and assert the
  outcome before using it. Proven: a dead 13-char key in a shared `.env` shadowed the live 57-char key in
  the profile `.env` for any first-match reader — a 401 with no error at the point of selection.
- **After a patch, re-read the file and re-run the output.** A patch that didn't apply looks
  identical to one that worked.
- **When you change a value's CONTENT, keep its TYPE.** Concretising a value is not the same as
  re-typing it. Proven 2026-09-22: a helper that replaced a RELATIVE path with a concrete one returned
  an ABSOLUTE url; every consumer of that field concatenates a base, so a verifier received
  `https://api.gentechlabs.nethttps://api.gentechlabs.net/v1/...` and 7 services that had passed one
  run earlier were rejected (DISCOVERY READINESS 14/14 -> 7 rejects). Assert the shape, not just the
  absence of the thing you removed — "no template remains" passes happily on a broken URL.
- **A rail can be PERMANENTLY dead because it requires an input its source cannot provide.** The
  worst member of the false-value family, because the refusal is CORRECT and therefore looks like
  good engineering. Proven 2026-09-22: the regime classifier demanded 7d momentum before it would
  name a regime ("a missing input is not a flat market" — right call). It read that momentum from
  DexScreener's `pair.priceChange.h7d`, and **DexScreener does not publish h7d** — it returns
  exactly `[m5,h1,h6,h24]`, verified live on both pools. So momentum was `None` on EVERY tick,
  forever: the classifier refused correctly every time, the regime sat UNKNOWN, and downstream
  `REGIME_SHAPE.get(unknown, "CURVE")` silently returned CURVE while a tilt map silently returned
  its neutral fallback. **A dead rail that looked calm instead of broken.** Rule: for every field a
  component REQUIRES, verify the producer actually emits it — do not infer it from the field's name
  appearing in a schema or a sibling. Then check the consuming lookup's DEFAULT: `.get(key, default)`
  on a decision table converts "we don't know" into "act as if the common case", which is how a
  broken classifier wears a working disguise. An UNKNOWN that maps to a safe posture is fine; an
  UNKNOWN that maps to the DEFAULT without saying so is a silent wrong answer.
- **A provenance label can be a hardcoded lie.** A dict field named `source` was literally
  `"source": "coingecko-btc"` — a constant in the writer — while the data came from a DexScreener
  pool read and (after the fix) a CoinGecko AVAX series. It read as fact, it persisted into the
  state file, and it sent a debugging session chasing BTC for an AVAX position. When a value's
  origin is knowable, DERIVE the label from the code path that fetched it (a `momentum_source`
  variable set at each branch), never type it once in the result dict. A stale label is worse than
  no label, because it is confidently wrong.
- **Never learn a value by scraping the SOURCE TEXT of the script that computes it.** Recurring
  (3rd occurrence, 2026-09-22): a reader regexed `lfj-curve-deploy.sh` for `BID_NEAR`/`ASK_FAR`.
  When that shell was changed to DERIVE those from a shared table and PRINT them, the numeric regex
  matched a Python expression instead, found no number, and the plan degraded to `"legs UNREADABLE
  — do not trust this plan"` 144x/day. A reader coupled to the *text* of its producer breaks the
  moment the producer is refactored, and it breaks SILENTLY. Import the shared module and call it.
  If a value must cross a language boundary, have the producer emit it as data (JSON/env), not as
  source text to be pattern-matched.
- **A monitor can be structurally blind to the EXACT condition it exists to catch — and it will
  look healthy. FEED THE CLASSIFIER THE FAILURE OUTPUT; do not read the code path.** Proven
  2026-09-23: both treasuries sat EMPTY all night and the Position Watchdog never spoke. The
  re-center hit its flat-book branch, printed `"nothing to withdraw — flat"`, and **returned before
  the idle and efficiency checks** — so it exited `rc=0` carrying text matching none of the
  classifier's patterns (`IDLE CAPITAL|DRIFTED|OUT OF RANGE|REBALANCE NOW|⚠️`). Feeding the real
  output to the classifier gave `ACTIONED=0 MATERIAL=0 ERROR=0` — silence on the one event the
  monitor was built for. An early return is the usual culprit: it is upstream of every check that
  could have flagged the condition, and it reads as harmless tidiness. Also note the inverse trap:
  the same watchdog gate spoke for a **routine** action at 3am while staying quiet for a **material**
  one — the urgency category was inverted. **Test rule: enumerate the conditions the monitor must
  fire on, synthesize each one's output, and assert the classifier fires. A monitor never tested in
  its firing direction is decoration.** Corollary: an hour mask on a cron suppresses the whole RUN,
  not just delivery — masking 'quiet hours' this way silently blinds monitoring for those hours.

### If Sr is unreachable

Say so, label the work **unaudited**, and do not call it verified. **An unaudited build is a
known state; an unaudited build called verified is how a bug ships.**

### Calling Sr directly over HTTP (the gotchas)

The `opencode-go` OpenAI-compatible endpoint (`https://opencode.ai/zen/go/v1/chat/completions`)
needs **two** things beyond `Authorization` + `Content-Type`, and both fail in confusing ways:

1. **`x-opencode-session: <uuid>` is REQUIRED.** Without it: `HTTP 400`
   `{"error":{"type":"MissingSessionID"...}}` — which reads like an auth/model problem and is not.
2. **The answer may be in `message.reasoning_content`, not `message.content`.** Kimi is a
   reasoning model: `content` comes back `null`/empty and the real analysis sits in
   `reasoning_content`. Reading only `content` yields a 0-char "successful" audit — a silent
   false green. Read `content or reasoning_content`, and set `max_tokens` generously (6000+).

Send a browser `User-Agent` too (Cloudflare bans bare client signatures).

**Never trust a 0-char audit as a pass.** An auditor that returned nothing did not clear the
work — treat empty output as unreachable and label the build unaudited.

### The bug class worth naming

**The false-value family** — a mechanism reporting success while doing nothing, or reporting a
number it cannot actually compute. **A green that cannot go red is not a signal.**

## Parallel Subagent Builds

When the build plan has **independent module groups** (e.g., engine + UI), delegate them to parallel subagents. Each subagent gets a self-contained prompt with exact file paths, API contracts, and acceptance criteria.

**When to parallelize:**
- Engine/logic and UI are independent
- Two unrelated features that share no code
- Test suite and implementation can be written simultaneously

**When NOT to parallelize:**
- Module B depends on Module A's internal implementation
- Shared state or configuration between modules
- Subagents would need to coordinate

## Reference Files

- `references/ecosystem-contribution.md` — Three-way scan pattern for evaluating and contributing to open-source ecosystems. Covers forking workarounds, execution flow, and repos scanned.
- `references/audit-findings-catalog.md` — Real bugs caught by Kimi K2.7 / Claude Opus 4.8 review sessions. CWE-338, CWE-1333, CWE-117, and exception isolation patterns with fixes and provenance.

## Pitfalls

- **Import paths when wrapping existing code** — Use `sys.path.insert()` or `Path.resolve().parent.parent` to import from sibling directories
- **CDN-clouded verification — static asset behind Cloudflare** — When deploying a static asset (HTML, JSON, image) through nginx to a domain proxied by Cloudflare, a successful `curl http://localhost/path` does NOT mean `https://domain/path` will serve the same content. Cloudflare Workers can intercept URL paths on the root domain even when wrangler.toml only routes `/api/*` and `/v1/*`. The Worker's catch-all handler (a `jsonResponse({ error: 'not_found' })` in the worker.ts `fetch()` fallthrough) returns 200 with API-style JSON for any unhandled path — which hides the error. Fix: (1) verify locally first, (2) verify externally with a content check, (3) if mismatched, check whether a Worker on the root domain is intercepting the path and remove the route from the Worker's wrangler.toml or add a passthrough in the Worker's fetch handler.
- **nginx `server_name` mismatch when testing via localhost** — `curl http://localhost/path` does NOT test the nginx server block for your domain. It hits the **default server block** (the first block that matches `listen 80 default_server`, or the alphabetically-first `sites-enabled` file). A 404 from `http://localhost/` is NOT evidence the site is down — it could mean the request matched a different server block entirely. Always use `curl -H "Host: yourdomain.net" http://localhost/path` to simulate the correct virtual host. Confirmed Jul 28, 2026: `curl http://localhost/frameforge.html` → 404 (wrong server block), `curl -H "Host: gentechlabs.net" http://localhost/frameforge.html` → 200 (correct).
- **Uvicorn module import path mismatch** — When running `uvicorn api.server:app`, Python resolves imports relative to the `api` package, NOT the project root. A `from cache import ScoreCache` in `api/server.py` fails because Python looks inside `api/` for a `cache` module, not at the project root. Fix: add `sys.path.insert(0, str(Path(__file__).resolve().parent))` at the top of `api/server.py` BEFORE the FastAPI imports. This makes sibling modules (`cache.py`, `payment.py`, `agent_identity.py`) importable whether the server is run as `uvicorn server:app` (from project root) or `uvicorn api.server:app` (from anywhere). Test this by running the server and hitting the health endpoint — if it starts but returns 404 on new endpoints, the import path is wrong.
- **Empty state file from tempfile** — `tempfile.mkstemp()` creates a 0-byte file. Guard with `if not content.strip(): return {}` before parsing
- **Writing code before tests** → harder to verify correctness
- **No plan saved to file** → subagents lose context, repeat work
- **Skipping audit** → security issues slip through
- **Phantom persistence** → "I saved the file" without verification. Always read-back after write
- **Overengineering** → 1000 lines when 100 would do. "Would a senior engineer say this is overcomplicated?"
- **Weak success criteria** → "make it work" is unverifiable. Transform to testable goals
- **Patch tool failure** — When patch fails repeatedly, switch to `write_file` to rewrite the entire file
- **Subagent timeout with partial output** — Subagents may timeout at 600s but have created all files. Verify with `find`, run tests, fix remaining issues manually
- **Re-read files after subagent build** — Subagents may have changed imports, function signatures, or branding
- **Subagent won't clean up stale files** — After a pivot or major refactor, manually remove old files
- **ES modules require a web server** — Games using `<script type="module">` won't work via `file://`. Serve via `python3 -m http.server 8080`
- **FastAPI/uvicorn port conflicts** — Port 8080 is commonly occupied. Use 8088 or scan first
- **FastAPI `request := Request` uses the class, not the instance** — `request := Request` in a route function assigns the `Request` class (a Starlette property object), not the injected request instance. FastAPI injects the request automatically when you add `request: Request` as a parameter. Fix: `async def get_price(request: Request, ...)` — never `request := Request` inside the function body
- **Python f-string backslash in expression** — `f"...{', '.join(f'{k} (${v["amount"]})' for ...)}"` fails because f-string expressions can't contain backslashes. Fix: extract the inner expression to a variable first: `tier_str = ", ".join(...)` then `f"...{tier_str}"`
- **`py_compile` passing is NOT the module importing** — A syntax check is blind to name resolution. A module compiles cleanly and still dies on import when a function is called at **module scope** but **defined further down the file** (Python runs top-to-bottom; a `def` below its first call is too late), or when a helper/global is referenced before it exists. A sweep reporting "N/N compile" has proven **nothing** about whether those files can RUN. Verify by importing, not compiling:
  ```python
  import importlib.util as u
  s = u.spec_from_file_location('m', path); m = u.module_from_spec(s)
  s.loader.exec_module(m)          # the real check
  ```
  Better still, run the tool's own `--help` or a dry-run. Caught live Sep 22 2026: a whole migration reported 86/86 files compiling while one could not be executed at all.
- **A "last resort" fallback that calls itself is infinite recursion, not a fallback** — `except Exception: return _helper()` where `_helper` is the function you are already inside recurses until the stack dies. The final branch must return a **literal**. A fallback path that has never been executed is not a fallback — test it by simulating the unavailable dependency (raise the ImportError) and asserting the literal comes back.
- **A caller in the deploy/sync manifest does not mean its CALLEE is** — When a wrapper script is enrolled for deployment but the script it *invokes* is not, the wrapper updates while the thing that actually runs stays stale — and the wrapper's own checks still pass. When enrolling a script, walk its **call graph** (what it `source`s, `bash`es, or `python`s) and enroll those too. Symptom: vault and deployed copies with **different line counts** — that is divergence, not formatting.
- **A single-RPC post-state read can print the PRE-action balances after a SUCCESSFUL action** — Re-reading balances on the same connection that just broadcast can show the old state, which reads exactly like a failed transaction. Never present that as fact. Read a **second, different provider** and print an explicit **delta** (`before -> after (+X)`), plus a hard warning when a tx reported SUCCESS but shows zero movement: that is a **lagging node, not a failed operation** — and explicitly say **do NOT re-send**, because re-sending doubles the action.
- **FastAPI module import side effects** — Extract business logic into standalone modules with no FastAPI dependencies
- **pytest-asyncio async fixture mode** — Add `asyncio_mode = "auto"` to `pyproject.toml` under `[tool.pytest.ini_options]`
- **SQLite `:memory:` path guard** — `os.path.dirname(":memory:")` returns `""`. Guard with `if dirname:` before `os.makedirs`
- **SQLite upsert pattern** — `UPDATE` does nothing if no row exists. Always `INSERT OR IGNORE` first
- **Python filenames with hyphens** — Can't be imported. Create underscore alias: `cp dry-powder-engine.py dry_powder_engine.py`
- **Bloomed node_modules block GitHub push** — Always `.gitignore` node_modules, build artifacts, and binary caches in the initial commit
- **`assert_close` defined after use in test files** — When writing inline test scripts (not pytest), define helper functions like `assert_close` BEFORE the test functions that call them. Python executes top-to-bottom, so a function used at module scope must be defined earlier in the file. Fix: move all helper definitions to the top of the file, right after imports.
- **CLI subprocess tests need fresh state per invocation** — Each `subprocess.run([sys.executable, "module.py", ...])` spawns a fresh Python process with a new in-memory state. If test A creates data and test B reads it via subprocess, test B won't see test A's data. Fix: either (a) create + read in a single `-c` script, or (b) use the module's Python API directly instead of subprocess. Proven on P2P Causes: flyer test failed because `cause-1` didn't exist in the subprocess's fresh engine.
- **Sequential build for medium independent tasks** — When the queue has 4-6 medium-sized independent tasks, sequential processing (one at a time, same session) is often faster than parallel subagents. No coordination overhead, no import-path confusion, no stale-file cleanup. Each task takes 2-5 minutes end-to-end. Use parallel subagents only when tasks are large enough (3+ files each) that wall-clock time savings outweigh setup overhead.
- **Phantom PRs — verify PR existence after creation** — `gh pr create` can exit 0 without the PR actually existing on GitHub. Forks can be silently deleted between sessions. Always verify with `gh pr view <number> -R <owner/repo> --json state` after creation, and re-verify all PRs at the start of every session. A PR that exists only in your tracking is a phantom PR — it wastes reviewer time and damages reputation when maintainers see stale references.
- **Circular imports when splitting modules** — When extracting shared helpers from a FastAPI app module (e.g. `gateway.py`) into a new module (`tab_or_exact.py`), the new module may import from the original, creating a circular dependency. Fix: extract the shared functions (config, helpers, models) into a third module (`helpers.py`) that has zero FastAPI dependencies. Both the original and the new module import from the helper, never from each other. Pattern: `gateway.py` and `tab_or_exact.py` both import from `helpers.py`; neither imports from the other.
- **C library compilation on import (liboqs-python pattern)** — Some Python packages (e.g. `liboqs-python`) trigger a full C library build from source on first `import`. This takes 5+ minutes on a VPS and will timeout any normal 10-30s terminal command. The build does eventually succeed, so the fix is to start the import in a background process (`terminal(background=True, notify_on_complete=True)`) first, then build the framework code while it compiles. After it finishes, the oqs module is available normally. Detection: if `import oqs` takes > 2 seconds or spawns a liboqs installation dialog, it's compiling — don't kill it, start it in the background and keep working.
- **Package directory names with hyphens are unimportable** — A package directory named `agentic-treasury` (with hyphen) cannot be imported by Python (`ModuleNotFoundError: No module named 'agentic_treasury'`). Python packages require underscores or camelCase. Fix: use `quantum_treasury` (underscore), never hyphens. If you already created the dir with a hyphen, `mv agentic-treasury quantum_treasury` and update all imports. Tests running via `pytest` from a parent directory will fail until this rename is done.
- **liboqs/oqs key lifecycle — in-memory only** — The `oqs.Signature` object stores signing keys internally in C memory and does NOT expose a `set_secret_key()` or `export_secret_key()` method. Once the context manager exits or the object is garbage collected, the key is gone. Pattern for signing: keep a live `oqs.Signature` instance on the signer object (`self._signer_ref`), call `generate_keypair()` once, then `sign(message)` on the same instance. For verification, create a fresh `oqs.Signature(alg)` and call `verify(message, sig, pub_key)` — verifiers don't need the secret. Persistent SPHINCS+ key storage requires wrapping oqs in a daemon that keeps a live reference.
