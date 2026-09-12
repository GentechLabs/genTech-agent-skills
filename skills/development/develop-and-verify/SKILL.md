---
name: develop-and-verify
description: "Consolidated develop-and-verify pipeline: DeepSeek V4 Flash (DEV) → GLM-5.3-flash / Kimi K2.7 (AUDIT) on Ollama Cloud, Hermes portal fallback. Two-phase build pattern with pre-publish audit checklist."
version: 2.1.0
author: gentech
tags: [build, audit, workflow, karpathy, tdd]
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
| **DEV** | DeepSeek V4 Flash (`deepseek-v4-flash:0731`) | Ollama Cloud | ~$0/M out | Draft code, make it functional, pass tests |
| **AUDIT** | GLM-5.3-flash OR Kimi K2.7-code | Ollama Cloud | ~$0-2/M out | Code tracing, bug hunting, security, architecture review |

> **⚠️ AUDIT model status (Sep 12, 2026):** GLM-5.3-flash via **Z.AI is DEAD** (`1113
> Insufficient balance`) and **Ollama Cloud is at its weekly cap** (429, resets weekly). The
> working AUDIT second-opinion is now **Kimi K2.7-code via Nous** (`moonshotai/kimi-k2.7-code`,
> live on the Nous inference API). Do not route audits to glm-5.3-flash until Z.AI is re-funded;
> treat any doc that still names it as the primary AUDIT model as stale (see E-17).
| **BIG BOY** | Kimi K3 | Ollama Cloud / Hermes portal | ~$15/M out | Architecture decisions, security audits, design reviews, full-codebase analysis |

**Provider routing (Sep 7, 2026 — Jordan directive):** Ollama Cloud is the ONLY primary provider. Hermes portal (Nous) is the fallback. OpenCode Go is retired — do NOT route to it. Primary `deepseek-v4-flash:0731` on ollama-cloud; fallback `deepseek/deepseek-v4-flash` on nous. The AUDIT pair is GLM-5.3-flash or Kimi K2.7-code, both on Ollama Cloud.

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
| **Current** | DeepSeek V4 Flash (free) | GLM-5.3-flash / K2.7 (free) | Already free — both on Ollama Cloud |
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

### Phase 3: REVIEW (AUDIT — GLM-5.3-flash or Kimi K2.7-code on Ollama Cloud)
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

Run through GLM-5.3-flash or Kimi K2.7-code (Ollama Cloud) before pushing to public repos:

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
5. **No skipping audit** — Every task gets GLM-5.3-flash / Kimi K2.7 review before moving on
6. **No "just one more feature"** — Scope creep kills submissions
7. **No silent assumptions** — State what you're assuming or ask
8. **No drive-by improvements** — Touch only what you must
9. **No declaring done without proof** — Verify persistence before stopping

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
