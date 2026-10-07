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
- **A check that records while it checks burns evidence a later step still needs** — even if the earlier step refuses, its write has already consumed a token the downstream step needs. If every guard must agree before acceptance, **record only after all guards have agreed**. Measured: a replay guard inserted the `jti` while checking it; a token then refused by a later step (stale roster) had already burned its `jti`, so re-presenting the same valid token after the roster refreshed failed as a replay for a call that never happened. Fix: separate `is_seen` (read-only check) from `claim` (accept-once write), and call `claim` last.
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

## The AUDIT INTENT — what to look for

**An audit without a stated intent is not an audit, it is a look around.** Before any audit, write down the
**ONE question** it answers and **the number that answers it**. **No number, no audit.**

### The ten failure classes, each with the question that finds it

1. **The EXEMPTION / bypass audit — do this FIRST.** Every bypass is a hole. Ask what feeds it, and whether the
   action it permits can **CREATE the condition that justifies the next one**. *A leak lives in an exemption.*
2. **The TRIGGER audit** — which condition actually fired, not which rule the docs describe. **A category
   present in 100% of runs is a HEADER, not a cause.**
3. **The NECESSITY test** — for any "it does X too much", reconstruct **per event** whether the stated condition
   was met.
4. **The COST decomposition** — mechanism cost vs external change vs income, and **report the RATIO**.
5. **The READER audit** — a sample taken mid-rewrite is a **frame, not a state**; a write is verified by its
   **receipt**, not by a number read afterwards.
6. **The RESERVE / limit audit** — a limit must cover the operation's **full step count**; ask whether the
   guarantee comes from the **ORDER** (provision-then-spend) rather than the **SIZE** of the reserve.
7. **The CONSTANT-vs-MECHANISM test** — did we move a number, or change a mechanism? *A fix that has to be
   re-applied is evidence, not progress.*
8. **The RECORD audit** — does the record carry the values **at the moment of decision**? Is there a writer for
   every reader? Is the published number the number the system acts on?
9. **The BANNER-OVER-A-NO-OP class** — a confident success line over an action that did nothing. **Read the
   POST-STATE, never the banner.**
10. **The FALSE-VALUE family** — a failed or unreadable read printed as a real value, **especially as ZERO**.
    "Unknown" is valid; "zero" is not unless measured.

### The two rules that make it an audit rather than a walk

- **Prove the direction it should REFUSE.** A guard never tested in the direction it blocks is decoration.
- **Re-audit after the fix — round 2 finds the regression round 1 introduced.**

### The order

measure first → **exemption audit** → trigger audit → necessity + cost ratio → readers/record → fix in the
**canonical copy** (never a side copy a sync reverts) → syntax check → sync → **verify the deployed copy by
hash** → **watch one full cycle.**

### The case that produced this (Treasury, 2026-10-04)

A book lost ~$7/day; the question was *"is it the rebalances or the market?"* The answer came from the checklist,
not from opinion:

- **42 re-actions in 24h against a cap of 2 — and 0 of 41 justified by price** (median move **0.19%** against a
  **1.20%** band). The book was in range and earning the whole day.
- **Cause: an exemption.** An idle-capital trigger written `(>25%) OR (>= $10)` fired on **change the loop's own
  last rebuild left in the wallet** — and that trigger **bypassed the churn cap**. Rebuild → change → "idle" →
  rebuild, forever. **The cap was never broken; it was bypassed, so the budget was never consulted.**
- **The fix that did NOT work:** raising the gas floor $1.00 → $1.50 — *a number, not a mechanism* — and the
  same failure returned the same day (class 7, in action).
- **The rule broken while writing the tool meant to enforce it:** the new watcher read a state file from the
  wrong path, failed silently, and printed **`0 re-centers`** on books that ran **31** and **42** (class 10,
  exactly).

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
- `references/pitfalls.md` — **INDEX** for 143 accumulated failure-mode lessons, the ledger behind this skill's silent-wrongness rule. The items live in `references/pitfalls-1.md`, `-2.md` and `-3.md` (**part 3 is the LIVE one — append new lessons there**); the index carries the part list, their counts and digests, and the stated census rule for checking an extraction. **Read on demand.**
- `references/audit-findings-catalog.md` — Real bugs caught by Kimi K2.7 / Claude Opus 4.8 review sessions. CWE-338, CWE-1333, CWE-117, and exception isolation patterns with fixes and provenance.

## Pitfalls

> **The ledger lives in `references/pitfalls.md` — an INDEX since 2026-09-28** — 143 accumulated silent-wrongness lessons, in three part files (`references/pitfalls-1.md`, `-2.md`, `-3.md`; **part 3 is LIVE and takes new lessons**). Read the part you need with `skill_view(name='develop-and-verify', file_path='references/pitfalls-1.md')`, or grep the three. The index carries each part's count, digest and the stated census rule.
> Extracted from this file 2026-09-28 to restore headroom (SKILL.md had reached 103,752 chars against the 100,000-char platform cap, which makes every write refuse), then SPLIT into parts the same evening when the single ledger reached 93,842 chars against the same per-file cap. **The cap is enforced PER FILE, not per directory** — so the parts, not the directory, are what must stay under it.
> **Nothing was deleted — the section moved.**
## The CANDIDATE-vs-FINDING rule — time it before you name it

**A list of what a thing COULD be is not a finding. If you cannot say which one it IS, the answer is `UNKNOWN`.**

Measured over one investigation (peer-mesh, 2026-10-05/06), where the same finding needed **three** corrections:
a rate that was a snapshot, a trigger hypothesised then falsified, and a cause hypothesised then falsified. **Every
correction came from measuring again; none came from thinking harder.**

The rules that would have prevented all three:

1. **A count is not a rate.** Before writing `%`, check the events' TIMESTAMPS. Five calls that all land inside one
   minute are one event, not 3% — and the count staying flat while the denominator grows is what a fixed cluster
   looks like. *The number was one command away the whole time.*
2. **A correlation is not a cause, and SHARED PATH is not SHARED MECHANISM.** Two anomalies on the same code path
   looked like one bug. Timing the path showed **0.15 s against a 30 s ceiling** — two hundred times under the
   limit the theory blamed. **A limit cannot cause a timeout on a call that finishes in a fraction of it: check the
   LATENCY before blaming the CEILING.**
3. **Falsify your own hypothesis before handing it over.** Adding a deliberately mis-configured input and watching
   it reproduce the exact symptom (including the same record id) is what turned a guess into a finding — and the
   same method is what killed the two guesses that were wrong.

**Corollary for handoffs: report the DISTINCTION, not the tidier story.** *"This is a real correctness bug AND it is
not the explanation for the failure you saw"* is worth more to the next person than a single confident cause that
happens to fit both.
