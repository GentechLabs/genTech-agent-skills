---
name: cron-truth-layer
description: "Universal data verification pattern for cron jobs — every job verifies truth before acting. Catches stale data, config drift, and API failures before they cause wrong decisions."
tags: [cron, preflight, verification, truth, data-freshness, agent-kit]
trigger: "When creating or updating any cron job that reads data files, API responses, or config. Also when debugging stale data issues in existing cron jobs."
related_skills:
  - ../stateful-alert-monitoring/SKILL.md  # uses preflight for alert gating
  - ../dca-rebalance-handler/SKILL.md  # needs fresh price data
version: 1.2.0
author: Gentech
---

# Cron Truth Layer — Universal Data Verification

## Core Principle

**Every cron job must verify data freshness before acting on it.** Stale data causes wrong decisions. The truth layer catches this before it happens.

## How It Works

### The Preflight Script (`/root/.hermes/scripts/preflight.py`)

Every cron job should call this before doing real work:

```python
import subprocess
subprocess.run(["python3", "/root/.hermes/scripts/preflight.py"], 
               capture_output=True, timeout=15)
```

Or for job-specific filtering:
```python
subprocess.run(["python3", "/root/.hermes/scripts/preflight.py", "--job", "data-freshness"], 
               capture_output=True, timeout=15)
```

### Built-in Validators

| Validator | What It Checks | Threshold |
|-----------|---------------|-----------|
| `data-freshness` | Key data files aren't stale | defi-data.json: 2h, position tracker: 24h |
| `position-sync` | Config files match position tracker | Auto-corrects drift |
| `git-state` | No stuck rebases or detached HEAD | Auto-fixes |
| `vault-sync` | Vault has no uncommitted changes | Warns only |
| `api-health` | Critical APIs are responding | DexScreener, AgentScan |

### Output Format

- ✅ Silent = all checks passed
- 🔍 Header = issues found (printed to stdout)
- `[validator-name] message` = specific issue

## Reference: Handoff Truth Check (LIVE — built Aug 29, 2026)

**Where:** embedded in `/root/.hermes/profiles/gentech/scripts/handoff-watcher.py` (`verify_truth()` + helpers).

**What it does:** every watcher run cross-checks OPEN handoff claims against the vault brain and reports drift as a stateful `🔍 TRUTH CHECK` block. Two validator classes:

1. **Memory-posture claims** — a `*memory-posture*` handoff naming a lane is re-measured against that lane's actual profile MEMORY.md (lane→profile map: labs→gizmo, treasury→gentech-treasury, pixel→pixel, gentech/hq→gentech). Below 85% = "claim stale, safe to resolve."
2. **Queue-reference claims** — `#N` refs in handoff text are checked against `scripts/build_queue.json`:
   - *Stale claim* (any age): handoff says waiting/blocked/needs-Jordan on #N while brain shows shipped/done/cancelled/dropped. This direction is HIGH-VALUE and low-FP — it caught DataHub #30 + Keeperhub #1 listed open in the Aug 26 nightly-build report after both had shipped.
   - *Hallucination claim* (≤2-day-old files, ≤2 refs per line only): handoff claims #N shipped/completed while brain says pending.

**False-positive guards (paid for with real FPs — do not remove):**
- Multi-ref digest lines (`#50, #8, #9, #73 shipped`) are ambiguous — hallucination-direction skipped when >2 refs on a line, because "shipped" may grammatically attach to only some refs.
- The queue RENUMBERS as items ship. Historical handoffs cite dead numbers (Aug 13 `#71` was FrameForge; `#71` today is Sovereign Model Router) — hallucination-direction restricted to ≤2-day-old files.
- First sweep found 19 findings; 1 was a real FP pair from exactly these two traps.

**Key principles (Jordan's architecture, his words):** handoffs are quick work messages; the vault is the source of truth — the brain holds the extended context (Mess Hall considerations, Green Room ideas/specs, per-group folders). The watcher reports drift only; the receiving agent resolves against the brain. Read-only flagging, no auto-edits from the checker.

**Silent-failure lesson from the build itself:** the truth pass was initially wrapped in a bare `try/except: []` that swallowed a tuple-unpacking crash (find_open yields 3-tuples, not 2) — the layer silently did nothing while appearing green. Rule: verification layers must print their own failures to stderr. A verifier that fails silently is worse than no verifier.

## Reference: Operational Monitor Pattern

A health-check-first, multichain-aware operational monitor is documented in `references/multichain-operational-monitor-pattern.md` with the live example at `/root/.hermes/profiles/gentech/scripts/revenue-monitor.py`.

This extends the preflight principle: verify ALL deployed services are up before trusting wallet or payment data, scan across multiple chains, then report infrastructure readiness alongside financial metrics.

## Pattern for New Cron Jobs

When creating a new cron job that reads data:

1. **Call preflight first** — catch stale data before it matters
2. **Check data age** — if file > threshold, flag it
3. **Compare sources** — if config ≠ on-chain, auto-correct
4. **Banner stale data** — make it impossible to miss in output

### Example: Stale Data Banner

```python
import os, time

DASHBOARD_PATH = "/root/ProtoJay4789.github.io/DeFi/defi-data.json"

def check_data_age():
    """Returns age in hours, or 999 if missing."""
    try:
        mtime = os.path.getmtime(DASHBOARD_PATH)
        return (time.time() - mtime) / 3600
    except Exception:
        return 999

# In your report:
age = check_data_age()
if age > 2:
    print("🚨 **STALE DATA** — report may be inaccurate")
elif age > 1:
    print(f"⚠️ Data age: {age:.1f}h")
```

### Example: Config vs On-Chain Verification

```python
def verify_range(on_chain_range, config_range, tolerance=0.02):
    """Auto-correct if drift exceeds tolerance."""
    drift = abs(on_chain_range[0] - config_range[0]) + abs(on_chain_range[1] - config_range[1])
    if drift > tolerance:
        print(f"⚠️ RANGE MISMATCH: on-chain [{on_chain_range}] vs config [{config_range}]")
        # Auto-correct config
        return on_chain_range  # use on-chain as truth
    return config_range
```

## Data Source Hierarchy

When multiple sources disagree, use this order:

1. **On-chain data** (blockchain is always truth)
2. **Position tracker** (Jordan updates on rebalance)
3. **AAE config** (fallback)
4. **Dashboard JSON** (reader output)

## Adding Custom Validators

Create a Python file in `/root/.hermes/scripts/validators/`:

```python
# /root/.hermes/scripts/validators/my_check_validator.py
def validate():
    """Return issue string if problem found, empty string if OK."""
    # Your check logic here
    return ""  # empty = all good
```

The preflight auto-discovers all `*_validator.py` files in that directory.

## Auto-Fix Layer

The preflight now auto-fixes safe issues (see `auto-fix-preflight` skill):

| Issue | Auto-Fix? | How |
|-------|-----------|-----|
| Uncommitted vault changes | ✅ | `git add -A && git commit && git push` |
| Stuck git rebase | ✅ | `git rebase --abort` |
| Detached HEAD | ✅ | `git checkout main` |
| Config drift | ✅ | Auto-correct from on-chain data |
| Stale data | ⚠️ | Flag with banner, don't delete |
| API key expired | ❌ | Needs human decision |

**Pattern:** Detect → Fix → Verify → Report

## Common Anti-Patterns in Cron Scripts

These bugs recur across script fleets. Check for them in every audit.

### Anti-Pattern 1: `[SILENT]` Leak to User

**Bug:** Scripts with `no_agent: true` print `[SILENT]` to stdout when suppressing output. Since stdout goes directly to Telegram, the user sees `[SILENT]` as a message.

**Fix:** Empty stdout — just `return` or `sys.exit(0)` without printing anything.

```python
# ❌ WRONG — leaks "[SILENT]" to Telegram
if nothing_changed:
    print("[SILENT]")
    return

# ✅ CORRECT — empty stdout = nothing delivered
if nothing_changed:
    return  # or sys.exit(0)
```

**Where to look:** Any script using `no_agent: true` that has debounce/suppression logic. Search for `print.*SILENT` or `print.*suppress`.

### Anti-Pattern 2: Hardcoded Config Drift

**Bug:** Scripts embed position data (range, shape, position_usd, milestones) as hardcoded dicts. When the position tracker config gets updated (rebalance, shape change), these scripts keep using stale values.

**Fix:** Load from the config file at runtime with fallback defaults.

```python
# ❌ WRONG — stale after first rebalance
POOL = {
    "range_low": 6.30,
    "range_high": 6.55,
    "shape": "bidirectional",
    "position_usd": 44.74,
}

# ✅ CORRECT — reads live config, falls back to defaults
CONFIG_FILE = "/root/.hermes/scripts/.lfj-aae-config.json"

def load_pool_config():
    defaults = {"range_low": 6.04, "range_high": 6.196, "shape": "curve", ...}
    try:
        with open(CONFIG_FILE) as f:
            cfg = json.load(f)
        pos = cfg.get("position", {})
        return {
            "range_low": pos.get("range", {}).get("low", defaults["range_low"]),
            "range_high": pos.get("range", {}).get("high", defaults["range_high"]),
            "shape": pos.get("shape", defaults["shape"]),
            "position_usd": pos.get("total_usd", defaults["position_usd"]),
        }
    except Exception:
        return defaults

POOL = load_pool_config()
```

**Where to look:** Any script with a `POOL = {...}` or `POSITION = {...}` hardcoded dict. Also check milestone tiers — they evolve (Scout → Raider → Warlord → Fisher → Sovereign).

### Anti-Pattern 3: Path Resolution Under Non-Standard HOME

**Bug:** `os.path.expanduser("~")` uses the `HOME` environment variable. Under Hermes profiles, HOME is set to the profile's `home/` subdirectory (`/root/.hermes/profiles/gentech/home`), NOT `/root` and NOT the profile root directory. This causes `~/.hermes/scripts/` to resolve to `/root/.hermes/profiles/gentech/home/.hermes/scripts/` — a three-level-deep nested path that doesn't exist.

Two common patterns that fail:

| Pattern | Resolves To (bogus) | Actual Path |
|---------|---------------------|-------------|
| `expanduser("~/.hermes/scripts/config.json")` | `/root/.hermes/profiles/gentech/home/.hermes/scripts/config.json` | `/root/.hermes/scripts/config.json` |
| `expanduser("~/.hermes/profiles/gentech/secrets/token")` | `/root/.hermes/profiles/gentech/home/.hermes/profiles/gentech/secrets/token` | `/root/.hermes/profiles/gentech/secrets/token` |

The second pattern is especially insidious — the path already contains `.hermes/profiles/gentech/` which makes the expanded path doubly nested and the error message harder to correlate with the source.

**Fix:** Use absolute paths for scripts that run under Hermes profiles. Never use `os.path.expanduser()` in a script that runs as a cron job under a profile.

```python
# ❌ WRONG — resolves to wrong path when HOME=/root/.hermes/profiles/gentech/home
CONFIG = os.path.expanduser("~/.hermes/scripts/config.json")
TOKEN = os.path.expanduser("~/.hermes/profiles/gentech/secrets/github-token")  # doubly nested!

# ✅ CORRECT — absolute path works regardless of HOME
CONFIG = "/root/.hermes/scripts/config.json"
TOKEN = "/root/.hermes/profiles/gentech/secrets/github-token"
```

**Where to look:** Any script using `os.path.expanduser()` that references `.hermes/`. Also check for `~` in shell commands (`cd ~/.hermes/...`) within `subprocess.run()` or `run_cmd()` — those use `HOME` too. Test by running the script under the profile environment (`echo $HOME` first).

### Anti-Pattern 4: State Flag Exists But Never Checked

**Bug:** A script writes a flag to state (e.g. `force_send`, `force_report`, `alert_override`) but the main logic never reads it. The flag accumulates in state, giving the illusion of control, but has zero effect. Jordan sets `force_send = true` expecting a report — the script ignores it.

**Fix:** After adding any state flag, grep the main logic path to verify it's actually consumed.

```python
# ❌ WRONG — flag is set but never read
def save_state(state):
    state["force_send"] = True
    # ... later, in main():
    # (no code ever checks state["force_send"])

# ✅ CORRECT — flag is consumed in the decision path
def should_send_report(state, ...):
    if state.get("force_send"):
        state["force_send"] = False
        return True, "force_send triggered"
    # ... normal debounce logic
```

**Where to look:** Any script with debounce/suppression logic. Check all `state.set()` or `state[key] =` writes against the reads in the main decision function. The `defi-lp-consolidated.py` had exactly this bug — `force_send` was written by the cron run command but `should_send_report()` never checked it.

### Anti-Pattern 5: Inference Config Drift

**Bug:** Cron jobs fail when the global inference config changes. Two scenarios:

**Scenario A: Pinned Job Drift**
- Job has explicit model/provider (pinned)
- Global config changes to different model/provider
- Hermes blocks execution to prevent running on unintended model

**Scenario B: Unpinned Job Drift**
- Job was created with a specific model (e.g., `glm-4.7`)
- Job has NO explicit model/provider saved (unpinned)
- Global config changes (e.g., new default: `stepfun/step-3.7-flash:free`)
- Hermes detects drift between "created with" and "current global" and blocks execution

**Error message:** "Skipped to prevent unintended spend: global inference config drifted since this job was created (model 'X' -> 'Y'), and this job is unpinned. To run on the new config, pin it explicitly..."

**Fix Pattern:**

```python
# 1. Check the job
cronjob(action='list')  # Look for the failing job_id

# 2. Identify current state
# - If model is null: job is unpinned
# - If model is set: job is pinned (Scenario A)

# 3. Fix Scenario A (pinned job drifted):
cronjob(action='update', job_id='xxx', 
        model={'provider': 'zai', 'model': 'glm-4.7'})

# 4. Fix Scenario B (unpinned job drifted):
cronjob(action='update', job_id='xxx', 
        model={'provider': 'zai', 'model': 'glm-5.2'})

# 5. Verify the fix
cronjob(action='run', job_id='xxx')
```

**Verification:** After fixing, check that:
```python
# Should show:
# model: glm-5.2  (or your chosen model)
# provider: zai
# base_url: null  # null means pinned, not inheriting global config
```

**Where to look:** Any cron job that failed with "config drifted" error. Check the current global config in `~/.hermes/profiles/gentech/config.yaml` under `inference:` section.

**Prevention:**
- Always pin models explicitly when creating cron jobs
- When updating global inference config, immediately list and update all active cron jobs
- For complex jobs (GLM-5.2), pinning is mandatory to ensure consistent quality
- For cost-sensitive jobs, pinning prevents accidental upgrades

**Real-world example (Jul 5, 2026):**
- Job: `5-Star Opportunity Scanner` (job_id: `71d5c3e3b245`)
- Created with: `glm-4.7` (but unpinned — not saved)
- Global config changed to: `stepfun/step-3.7-flash:free`
- Error: "Skipped to prevent unintended spend: global inference config drifted since this job was created (model 'glm-4.7' -> 'stepfun/step-3.7-flash:free'), and this job is unpinned"
- Fix: Pinned to `provider: zai, model: glm-5.2`
- Result: Job runs successfully

### Anti-Pattern 6: Partial Audit ("fix the one that's broken")

**Bug:** When one cron job has a bug, only that job gets fixed. The same bug class exists in 2–5 other scripts.

**Fix:** When you find a bug in one script, immediately grep ALL scripts for the same pattern. The audit from this session found:
- `force_send` flag set but never checked → 1 script (fixed)
- `[SILENT]` leak → 2 scripts (fixed)
- Hardcoded config → 1 script (fixed)

**Workflow:** `search_files` for the anti-pattern across the entire scripts directory. Patch all instances in one pass.

### Anti-Pattern 7: Skipping Proper Develop → Test → Verify → Troubleshoot Workflow

**Bug:** Agent makes multiple changes to scripts/configs/data sources in rapid succession without testing each change individually. When the cron job runs, it's unclear which specific change caused the issue (or if all changes together caused it).

**Fix:** Follow Jordan's explicit workflow for cron job changes:

```
1. DEVELOP → Make one specific change
2. TEST → Run the cron job manually and capture output
3. VERIFY → Check if output is correct
4. TROUBLESHOOT → If wrong, diagnose and fix
5. RUN AGAIN → Re-test after each fix
6. AUDIT → Use stronger model if needed (GLM-5.2)
7. FIX → Apply the fix
8. PRESENT → Show working solution with real output
```

**Jordan's requirement:** "You do all these changes and the cron job, you do a test run of the cron job, right? And you check to see if everything's right. All the things we talked about, if it's not you wanna troubleshoot, you know, run it again, audit fix, present. See what happens."

**Pitfalls to avoid:**
- ❌ Making 3+ changes before testing
- ❌ Assuming fixes will work without verification
- ❌ Skipping manual test runs when quiet hours prevent output
- ❌ Moving to next solution when current one wasn't verified
- ❌ Presenting plans instead of working artifacts

**Practical application (session example):**
- Bug: Dashboard showed wrong shape (curve vs bid-ask), wrong entry price, wrong position amounts
- Problem: Multiple scripts writing to same dashboard file (race condition)
- Wrong approach: Made file read-only + updated multiple scripts + changed data sources all at once
- Correct approach: Test each change, verify output, fix only what breaks

**Test technique when quiet hours block output:**
Temporarily disable quiet hours in the script, force a test run, verify output, re-enable quiet hours:

```python
# In the script:
QUIET_START = 25  # Disabled for testing
QUIET_END = 25

# Run test:
python3 /root/.hermes/profiles/gentech/scripts/defi-lp-consolidated.py

# Revert after test:
QUIET_START = 23
QUIET_END = 6
```

**Verification checklist for cron changes:**
- [ ] Manual test run completed
- [ ] Output shows correct data (shape, entry price, position amounts)
- [ ] Exit code is 0 (no errors)
- [ ] Any errors in stderr were addressed
- [ ] Test reproduced the issue before fix
- [ ] Test confirmed fix after change
- [ ] Next scheduled cron run will be monitored for confirmation

### Anti-Pattern 9: Corrupted JSON from Git Merge Conflicts

**Bug:** JSON data files (`defi-data.json`, config files, state files) accumulate merge conflict artifacts (`<<<<<<< Updated upstream`, `=======`, `>>>>>>> Stashed changes`) when multiple agents or humans push/pull from the same repo. The `git pull --rebase` encounters conflicts, and `git add -u` stages the conflicted file. Next cron run tries `json.load()` → fails with `JSONDecodeError`.

**Real-world example (Jul 8, 2026):**
- `defi-data.json` on GitHub had `<<<<<<< Updated upstream` repeated 7+ times
- Hub Nightly Sync cron failed: "Invalid JSON in defi-data.json"
- Root cause: prior process committed a file with unresolved conflict artifacts

**Crucial pitfall (Jul 13, 2026):** `=======` with trailing characters (e.g. `=======,`) bypasses `stripped == '======='` checks. The `=======,` pattern occurs when a conflict ends right before a JSON structural character like `,` or `}`. Use regex (`re.match(r'^={7}', stripped)`) instead of strict equality for detection.

**Fix: Three-layer defense in every JSON-reading script:**

```
Layer 1: sanitize_json_text()  — strip markers before parse
Layer 2: load_json_safe()      — auto-repair + write clean copy
Layer 3: pre-commit scan       — catch before push
```

**Layer 1 — Sanitize function:**

```python
def sanitize_json_text(text):
    """Strip merge conflict markers and common JSON corruption from raw text."""
    import re
    # First pass: regex strip any line starting with conflict markers
    lines_raw = text.splitlines(keepends=True)
    pre_cleaned = []
    for line in lines_raw:
        stripped = line.strip()
        if re.match(r'^<{7}', stripped):
            continue
        if re.match(r'^={7}', stripped):
            continue
        if re.match(r'^>{7}', stripped):
            continue
        pre_cleaned.append(line)

    # Second pass: handle well-formed conflict blocks
    lines = pre_cleaned
    clean = []
    in_conflict = False
    keep_side = False  # True when past ======= (keeps "theirs")
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('<<<<<<< '):
            in_conflict = True
            keep_side = False
            continue
        if stripped == '=======' and in_conflict:
            keep_side = True
            continue
        if stripped.startswith('>>>>>>> ') and in_conflict:
            in_conflict = False
            keep_side = False
            continue
        if not in_conflict:
            clean.append(line)
        elif keep_side:
            clean.append(line)
    cleaned = ''.join(clean)
    # Strip BOM
    cleaned = cleaned.lstrip('\ufeff')
    # Fix trailing commas before closing braces/brackets
    cleaned = re.sub(r',\s*}', '}', cleaned)
    cleaned = re.sub(r',\s*]', ']', cleaned)
    # Fix missing commas after conflict removal
    cleaned = re.sub(r'("\s*:\s*[^,{}\[\]]+)\s*\n(\s*")', r'\1,\n\2', cleaned)
    cleaned = re.sub(r']\s*\n\s*"', '],\n"', cleaned)
    return cleaned
```

**Layer 2 — Safe loader (auto-repairs file):**

```python
def load_json_safe(path):
    """Load JSON, sanitizing merge conflict artifacts first. Writes clean copy back."""
    if not os.path.exists(path):
        return None, f"{path} not found"
    try:
        with open(path, 'r') as f:
            raw = f.read()
        cleaned = sanitize_json_text(raw)
        data = json.loads(cleaned)
        if cleaned != raw:
            with open(path, 'w') as f:
                f.write(cleaned)  # Prevent recurrence
        return data, None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON in {path}: {e}"
    except Exception as e:
        return None, f"Error reading {path}: {e}"
```

**Layer 3 — Pre-commit conflict scan:**

```python
def push_to_github():
    # ... copy file to repo ...
    # Pre-commit check:
    with open(staged_file) as f:
        raw = f.read()
    if '<<<<<<<' in raw or '=======' in raw or '>>>>>>>' in raw:
        clean = sanitize_json_text(raw)
        with open(staged_file, 'w') as f:
            f.write(clean)
        errors.append("⚠️ Stripped merge conflict markers before commit")
    # ... commit and push ...
```

**Where to apply:** Any script that reads/writes JSON files shared via git. Search for `json.load` across the scripts directory.

**Verification:** Test with corrupted file containing conflict markers:
```python
corrupted = '{"test": 1,\n<<<<<<< HEAD\n"val": "old"\n=======\n"val": "new"\n>>>>>>> branch\n}'
data = json.loads(sanitize_json_text(corrupted))
assert data == {"test": 1, "val": "new"}
```

### 🔴 The Sequence Vulnerability (Layer 3 Timing)

**Bug pattern:** The pre-commit scan checks for conflict markers BEFORE `git pull --rebase`, but the rebase can introduce NEW conflict markers that the scan never sees. Then `git add -u` stages those markers.

**Vulnerable flow (hub-sync-nightly.py, Jul 10, 2026):**
```
1. cp vault/file.json → repo        ← clean copy from vault
2. Pre-commit scan (Layer 3)        ← clean (file is fresh from vault) ✅
3. git commit
4. git pull --rebase origin main     ← ⚠️ REBASE can introduce conflict markers!
5. git add -u                        ← ⚠️ STAGES conflict markers!
6. git push with retry               ← 🚨 pushes corrupted file
```

The pre-commit scan at step 2 found nothing because the file was freshly copied from the vault. The rebase at step 4 conflicted with a concurrent push (POE2 build sync at 18:00 UTC). Step 5 staged everything including markers. Step 6 pushed corrupted JSON. The vault copy was correct all along — the copy-to-repo → rebase → push pipeline was the broken link.

**Detection:**
```bash
# After a failed nightly sync, check the repo file for markers:
grep -c '<<<<<<< \|=======\|>>>>>>> ' /path/to/repo/data.json
# Non-zero = conflict markers in staged file
```

**Fix: check rebase exit code, scan post-rebase, continue rebase, then push:**

```python
def push_to_github():
    # ... copy file, commit ...

    # Pull rebase first to handle remote divergence
    rebase_out, rebase_rc = run_cmd(f"cd {REPO_PATH} && git pull --rebase origin main", timeout=60)
    if rebase_rc != 0:
        # Rebase conflicted — auto-resolve with theirs (remote is fresher)
        run_cmd(f"cd {REPO_PATH} && git add -u", timeout=15)

        # ⚠️ SECOND scan: check for rebase-introduced conflict markers
        staged_file = f"{REPO_PATH}/path/to/data.json"
        with open(staged_file) as f:
            raw = f.read()
        if '<<<<<<<' in raw or '=======' in raw or '>>>>>>>' in raw:
            clean = sanitize_json_text(raw)
            with open(staged_file, 'w') as f:
                f.write(clean)
            subprocess.run(["git", "add", staged_file], check=False)
            print("⚠️ Stripped rebase-introduced conflict markers")

        # Continue the rebase (required after conflict resolution)
        run_cmd(f"cd {REPO_PATH} && GIT_EDITOR=true git rebase --continue", timeout=30)
    else:
        # No conflict — rebase autostaged changes
        pass

    # Now push with retry
    for attempt in range(push_retries):
        # ... push with retry ...
```

**Key addition over the earlier fix:** The rebase exit code is checked. On conflict, we add, scan, and **continue the rebase** with `git rebase --continue`. Without this step, the repo stays in a rebase-apply state and subsequent pushes fail. On clean exit, no extra work is needed — the rebase autostages resolved changes.

**Real-world correction (Jul 12, 2026):** The earlier fix at hub-sync-nightly.py ran `git add -u` unconditionally after `git pull --rebase` without checking the rebase exit code. When the rebase conflicted, `git add -u` staged the conflicted file, and `git push` failed because the rebase was still in progress. Added: (1) check rebase rc, (2) `git rebase --continue` after conflict resolution, (3) skip git add -u on clean rebase.

**Key insight:** The first scan (pre-commit, Layer 3) is still valuable — it catches pre-existing corruption before commit. The SECOND scan (post-add, pre-push) catches rebase-introduced corruption. Both are needed. Without the second scan, a concurrent push during the rebase window leads to silently corrupted data on the remote.

### Anti-Pattern 10: Empty Dict Silently Filters All Data

**Bug pattern:** A script has a filter dict (`KNOWN_SERVICES`, `ALLOWED_SOURCES`, `TRACKED_WALLETS`) populated at declaration time but never updated. The main processing loop only handles items that match the dict — but since the dict is empty (or stale), **all data is silently discarded**.

This is different from a hardcoded stale value (Anti-Pattern 2). An empty dict filter causes *complete data loss*, not just stale data.

**Real-world example (Jul 16, 2026 — revenue-monitor.py):**
```python
# ❌ WRONG — KNOWN_SERVICES = {} means nothing ever matches
KNOWN_SERVICES = {}  # ← never populated

for tx in external:
    if tx["service"] != "unknown":  # ← NEVER TRUE
        data["revenue_by_service"][svc]["total_usdc"] += tx["amount_usdc"]
        # All revenue silently counted as $0
```

The script scanned 3 EVM chains for USDC transfers, found them, classified every one as "unknown" (since KNOWN_SERVICES was empty), then discarded them all. Total revenue was perpetually $0, not because nobody paid — but because the counting gate was locked.

**Fix: Label-based, not filter-based.** Count ALL legitimate data. Use the dict for labeling/enrichment only:

```python
# ✅ CORRECT — labels enrich, never filter
KNOWN_SENDERS = {
    # customer_address: "customer_name" (optional labels)
}

for tx in external:
    svc_name = KNOWN_SENDERS.get(tx["sender"].lower(), tx["chain"])
    data["total_revenue_usd"] += tx["amount_usdc"]  # always count
```

**Detection pattern:**
```bash
# Search for the pattern: filter dict followed by conditional that skips unknown
grep -n -A5 'KNOWN.*= {\|ALLOWED.*= {\|_.*SERVICES.*= {' revenue-monitor.py
grep -n '!= "unknown"\|not in ALLOWED\|not in TRACKED' *.py
```

**Key insight:** An empty dict that gates data processing is a time bomb. It works during initial development (no data matches because there IS no data), then silently fails forever when real data arrives. The fix is to make the dict optional/enrichment-only: the processing path must work correctly with or without it.

**Where to look:** Any script that has:
1. A dict initialized to `{}` as a filter/allowlist
2. A loop that only processes items that have a matching key in that dict
3. No fallback that handles unmatched items

Also check: `ALLOWED_SOURCES`, `TRACKED_WALLETS`, `MONITORED_CHAINS`, and any `_registry` or `_catalog` dict that gates processing.

### 🛡️ Layer 4: Vault-Fallback Recovery (NEW — Jul 15, 2026)

**Bug pattern:** Even when conflict markers are successfully stripped, `sanitize_json_text()` can leave JSON structurally incomplete. Removing markers can delete structural characters (closing `}`, `]`, or commas at the boundary of a conflict block). After "theirs" side is kept, the surrounding JSON structure may be broken — e.g., a conflict ending right before the final `}` means the surviving side ends truncated.

**Real-world example (Jul 15, 2026):** Hub Nightly Sync hit a rebase conflict on `DeFi/defi-data.json`. `sanitize_json_text()` stripped markers, but the file lost its closing `}` — 19 of 28 keys survived. Pre-push validation caught the corruption, but the script only reported the error without auto-recovering.

**Fix:** When cleaned JSON is still invalid, re-copy from the authoritative vault source (which was written before the push step), re-stage, and continue.

**Copy-paste recovery block for any push-to-github script:**

```python
# === POST-REBASE CORRUPTION RECOVERY ===
# If sanitize_json_text() stripped markers but left structurally
# incomplete JSON, re-copy from vault and re-stage.
VAULT_SOURCE = "/path/to/vault/source.json"   # adjust
STAGED_FILE  = "/path/to/repo/target.json"    # adjust

with open(STAGED_FILE) as f:
    try:
        json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"🔴 JSON invalid after post-rebase clean: {e}")
        subprocess.run(f"cp {VAULT_SOURCE} {STAGED_FILE}", shell=True, check=True)
        subprocess.run(f"cd {REPO_PATH} && git add {STAGED_FILE}", shell=True, capture_output=True)
        with open(STAGED_FILE) as f2:
            try:
                json.load(f2)
                errors.append("🔄 Re-copied from vault — valid, continuing")
            except json.JSONDecodeError as e2:
                errors.append(f"🔴 Vault copy also invalid: {e2}")
# === END RECOVERY BLOCK ===
```

**When to add:** Any script that (a) pushes JSON to a git repo AND (b) does `git pull --rebase` after commit. Insert after the post-rebase conflict scan and before `git rebase --continue`.

**Why vault is safe to fall back to:** In hub-sync-nightly.py, the update function writes to the vault BEFORE the push function runs. So the vault always has a valid, more-recent copy than the repo working copy.

**Verification that the fix works:**
```python
# After applying the fix, check the remote file is valid JSON
import json, urllib.request
sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
url = f"https://raw.githubusercontent.com/owner/repo/{sha}/path/to/data.json"
raw = urllib.request.urlopen(url).read().decode()
json.loads(raw)  # should not raise
print("VALID JSON on remote — fix verified")
```

**Full reference implementation:** See `references/json-conflict-sanitizer.md` for the complete `sanitize_json_text()` + `load_json_safe()` + `post_rebase_conflict_check()` code ready to copy into any script.

### Anti-Pattern 11: Rebase Cascade — Multi-Commit Divergence (NEW — Jul 19, 2026)

**Bug pattern:** `git pull --rebase` re-applies EVERY commit between local and remote, one at a time. When there are N divergent commits, EACH ONE can conflict. A script that handles ONE conflict with `git add -u + git rebase --continue` only survives the first — the next `rebase --continue` hits commit 2's conflict, and so on for all N. The script has no loop to handle this, so it falls through to pre-push validation with a corrupted file, then reports a push failure.

**Real-world example (Jul 19, 2026):** Hub Nightly Sync ran `git pull --rebase` finding 15 commits behind remote. Commit 1 conflicted → resolved. `rebase --continue` hit commit 2's conflict → resolver didn't run again (one-shot logic). After 13 more conflicts, the file was corrupted (only 1 of 28 keys survived). Pre-push validation caught it, blocked the push, but the repo was left in a stuck rebase state that needed manual `git rebase --abort` + `git merge --strategy-option theirs` to recover.

**Detection:**
```bash
# After a failed sync, check if rebase is still in progress:
git status | grep -q "rebase in progress" && echo "⚠️ Stuck rebase — needs abort"

# Count how many commits diverged:
git rev-list --count HEAD..origin/main
# If > 1, any ONE rebase conflict will cascade through all of them
```

**Fix for automated data sync scripts — prefer merge over rebase:**

For scripts where the data file is **fully regenerated** from an authoritative source (vault, API, on-chain), use merge with `--strategy-option theirs` instead of rebase. This avoids the cascade entirely because merge resolves all conflicts in one pass:

```python
def push_to_github():
    """Copy file to repo and push. Merge (not rebase) for automated data."""
    # ... copy file, commit ...

    # Fetch remote changes first
    run_cmd(f"cd {REPO_PATH} && git fetch origin main", timeout=30)

    # Merge with theirs — remote wins conflicts because our file
    # is fully regenerated from vault, not a user-edited document
    merge_out, merge_rc = run_cmd(
        f"cd {REPO_PATH} && git merge origin main --no-edit --strategy-option theirs",
        timeout=30
    )
    if merge_rc != 0:
        run_cmd(f"cd {REPO_PATH} && git merge --abort", timeout=15)
        errors.append("⚠️ Merge failed, falling back to rebase")
        # ... rebase logic with cascade loop ...

    # Pre-push validation
    with open(json_check_path) as f:
        try:
            json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"🔴 Pre-push JSON validation failed: {e} — data not pushed")
            return "corrupted", errors

    # Push with retry
    for attempt in range(3):
        out, rc = run_cmd(f"cd {REPO_PATH} && git push", timeout=30)
        if rc == 0:
            break
        time.sleep(30 * (2 ** attempt))
    return "pushed", errors
```

**⚠️ When NOT to use merge with theirs:** If the data file is manually curated (user edits, hand-tuned configs, editorial content), rebase preserves the user's work correctly. Only use merge with theirs when the script fully regenerates the file from an authoritative source and your version is authoritative.

**Recovery from stuck rebase cascade:**

```bash
# Check state
cd /path/to/repo
git status | head -5
# → "interactive rebase in progress; onto <sha>"
# → "both modified: path/to/file.json"

# Option A: Abort and restart (preferred — preserves nothing lost from rebase)
git rebase --abort

# Verify vault copy is valid
python3 -c "import json; json.load(open('/path/to/vault/file.json')); print('VAULT VALID')"

# Copy vault → repo, commit, merge, push
cp /path/to/vault/file.json path/to/repo/file.json
cd /path/to/repo
git add path/to/repo/file.json
git commit -m "data: sync from vault"
git fetch origin main
git merge origin main --no-edit --strategy-option theirs
git push

# Option B: Continue through remaining rebase steps (tedious, only if Option A risky)
while git status | grep -q "rebase in progress"; do
    git add -u
    GIT_EDITOR=true git rebase --continue 2>/dev/null || break
done
# If loop exited with failure: git rebase --abort and fall back to Option A
```

**The key insight:** For automated data syncs on a single fully-regenerated file, rebase is the wrong tool. Merge-with-theirs is safer (one-shot conflict resolution) and avoids cascading failures. Save rebase for user-interactive sessions with multiple manual edits.

**Where to apply:** Any cron script that:
1. Generates a data file from an authoritative source (vault, API, on-chain)
2. Pushes to a shared repo that other scripts also push to
3. Uses `git pull --rebase` before push

**Reference:** `references/rebase-cascade-prevention.md` — full pattern with recovery commands, comparison table, and merge-vs-rebase decision tree.

### Anti-Pattern 12: Stale Env Var Overrides Valid Credential

**Bug pattern:** A probe script reports a false failure because a stale environment variable (exported in the shell session) overrides a valid credential stored in a config file. The probe checks the env var first, finds the stale value, and reports failure — even though the real credential is valid.

**Real-world example (evolve-6, Jul 28, 2026):**
- `credential-health.sh` reported `github=401` every cycle
- Root cause: `GITHUB_TOKEN` env var was an expired `ghp_` token
- The valid token lived in `~/.config/gh/hosts.yml`
- `gh auth status` checks `GITHUB_TOKEN` first, so it always hit the stale one
- The evolve-5 fix removed the stale var from `.env`, but the cron session's shell still had it exported

**Fix pattern (four steps):**

1. **Check the env var** — `env | grep <VAR>` to see if it's still exported
2. **Check the config file** — the valid credential may live in a config file while the env var is stale
3. **Fix the source** — remove the stale var from `.env` so new sessions don't inherit it
4. **Fix the probe** — add `unset <VAR>` before the probe call so the current session's stale export doesn't interfere
5. **Verify** — run the probe and check the log shows the correct status

```bash
# In the probe script, before the credential check:
unset GITHUB_TOKEN  # Stale env var — valid token is in ~/.config/gh/hosts.yml
```

**Detection pattern:**
```bash
# Check if env var differs from config file
env | grep GITHUB_TOKEN
grep 'oauth_token' ~/.config/gh/hosts.yml
# If they differ, the env var is stale
```

**Where to look:** Any probe script that checks an env var before falling back to a config file. The `gh auth status` command is especially vulnerable because it checks `GITHUB_TOKEN` before reading `hosts.yml`.

### Anti-Pattern 13: Pages Deploy Verification Gap

**Bug pattern:** A cron job pushes data to a GitHub repo that serves a GitHub Pages site, but only verifies the data landed on GitHub (via raw.githubusercontent.com or the API) — it never checks that the Pages deploy actually ran. The data can be on GitHub but the Pages site serves stale content because the deploy workflow didn't trigger.

**Real-world example (Jul 20, 2026):** Hub Nightly Sync pushed `defi-data.json` to `ProtoJay4789.github.io` successfully (commit `96ac9886`, valid JSON, 15/15 sections). But the Pages deploy workflow never ran — no workflow run was created for that commit. The Pages build was stuck on a 12-hour-old commit (`831fd0642253`). The script's `verify_live()` checked raw.githubusercontent.com (404 — raw CDN issue) and gentechlabs.net (HTML — wrong deployment target), but never checked the actual Pages URL or the Pages API.

**Root cause:** The workflow is configured to trigger on `push: branches: [main]`, but the push didn't create a workflow run. Possible causes:
- GitHub Actions rate limiting (free tier has limits)
- Workflow file mismatch between local and remote
- `concurrency: cancel-in-progress: false` blocking new runs while a previous one is still "in progress" in GitHub's state
- The `pages-build-deployment` dynamic workflow (not the user's workflow) is the one that actually builds Pages — it may not have been triggered

**Fix: Add Pages deploy verification to the push function:**

```python
def verify_pages_deploy(repo_owner, repo_name, token, expected_sha, timeout=120):
    """Poll GitHub Pages API until the deploy matches expected SHA or timeout."""
    import time, urllib.request, json
    
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pages/builds"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    deadline = time.time() + timeout
    while time.time() < deadline:
        req = urllib.request.Request(api_url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=10)
        builds = json.loads(resp.read().decode())
        if builds:
            latest = builds[0]
            if latest.get("status") == "built" and latest.get("commit", "")[:12] == expected_sha[:12]:
                return True, None
            if latest.get("status") == "built" and latest.get("commit", "")[:12] != expected_sha[:12]:
                # Deploy ran but for a different commit — ours hasn't been picked up yet
                pass
        time.sleep(10)
    
    return False, f"Pages deploy did not complete for {expected_sha[:12]} within {timeout}s"
```

**Integration into push_to_github():**

```python
def push_to_github():
    # ... copy, commit, merge/pull, push ...
    
    # After successful push, verify Pages deploy
    if push_rc == 0:
        time.sleep(5)
        deploy_ok, deploy_err = verify_pages_deploy(
            "ProtoJay4789", "ProtoJay4789.github.io", 
            token, expected_sha, timeout=120
        )
        if not deploy_ok:
            errors.append(f"⚠️ Pages deploy not confirmed: {deploy_err}")
            errors.append("  Data is on GitHub but Pages may serve stale content")
            errors.append("  Manual fix: push an empty commit or trigger workflow_dispatch")
    # ...
```

**Detection pattern:**

```bash
# After a push, check if the Pages build matches your commit
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/ProtoJay4789/ProtoJay4789.github.io/pages/builds?per_page=1" \
  | python3 -c "import json,sys; b=json.load(sys.stdin)[0]; print('Built:', b['commit'][:12], 'Status:', b['status'])"

# Compare with latest local commit
git rev-parse HEAD | cut -c1-12
# If they don't match, the deploy didn't run for your commit
```

**Where to apply:** Any cron script that pushes to a GitHub Pages repo and relies on the Pages site being up-to-date. Add after the push step, before live verification.

**Key insight:** `raw.githubusercontent.com` and the Pages CDN (`*.github.io`) are different services with different caches. A 404 from raw.githubusercontent.com does NOT mean the data isn't on GitHub — it means the raw CDN hasn't picked it up. The Pages deploy is a separate workflow that must be verified independently. The script should check BOTH: (1) the data exists on GitHub (via API), and (2) the Pages deploy ran for the expected commit.

**⚠️ raw.githubusercontent.com 404 for main branch (Jul 21, 2026):** Even the `main` branch URL can return 404 when the file is confirmed on GitHub via the API. This is a raw CDN propagation issue, not a data problem. The three-layer verification chain is:

1. **GitHub API blob content** (definitive, no cache) — `curl -s -H "Authorization: token $GH_TOKEN" "https://api.github.com/repos/owner/repo/contents/path/file.json?ref=main"` — if this returns valid data, the file IS on GitHub
2. **GitHub Actions build status** — confirm deploy ran for the expected commit
3. **raw.githubusercontent.com** — best-effort, treat 404 as "CDN not propagated" not "data missing"

**Fix in verify_live():** Add a GitHub API verification step as the primary check before falling back to raw CDN. Never report "data missing" based on raw CDN 404 alone.

## Health Tracking + Workflow Enforcement Layer (NEW — Jul 2026)

**Problem:** Jordan caught that cron jobs were running without verification, and workflow gaps existed (no "develop → verify → troubleshoot" enforcement, no health tracking).

**Solution:** Two new scripts enforce workflows and track health.

### Cron Health Tracker (`cron-health.py`)

**Location:** `/root/.hermes/profiles/gentech/scripts/cron-health.py`

**What it does:**
- Tracks last run time for each cron job
- Checks if jobs are overdue vs schedule
- Records exit codes from each run
- Generates health reports with alerts
- Detects drift-vulnerable jobs (model: null, provider: zai)

**Usage:**
```bash
# Check all jobs and generate report
python3 /root/.hermes/profiles/gentech/scripts/cron-health.py --report

# Check specific job
python3 /root/.hermes/profiles/gentech/scripts/cron-health.py --job <job_id>

# Manual health check (runs from a cron job)
python3 /root/.hermes/profiles/gentech/scripts/cron-health.py
```

**Health states:**
- ✅ `healthy` — Running on schedule, exit code 0
- 🔴 `overdue` — Haven't run in schedule + threshold time
- ❌ `failed` — Last run had non-zero exit code
- ⚠️ `never_run` — No health data recorded yet
- ❓ `unknown` — Job not in schedule registry

**Schedule registry:** Track expected run intervals in `JOB_SCHEDULES` dict:
```python
JOB_SCHEDULES = {
    "defi-lp-consolidated": 4,      # Every 4 hours
    "daily-sync": 24,               # Daily
    "morning-briefing": 24,         # Daily
    "opportunity-scanner": 6,       # Every 6 hours
    "agent-health-audit": 24,       # Daily
}
```

**Health data storage:** `/root/.hermes/profiles/gentech/cron/state/health-tracking.json`

### Cron Wrapper (`cron-wrapper.py`)

**Location:** `/root/.hermes/profiles/gentech/scripts/cron-wrapper.py`

**What it does:**
- **Enforces preflight before execution** — verifies data freshness
- **Runs the actual job with timeout** — 10 minute limit
- **Records health after completion** — calls cron-health.py with exit code
- **Alerts on failure** — flags issues immediately

**Usage (update cron jobs to use wrapper):**
```python
# Before:
cronjob(action='create',
        name='DeFi LP Monitor',
        script='/root/.hermes/profiles/gentech/scripts/defi-lp-consolidated.py',
        schedule='0 */6 * * *')

# After:
cronjob(action='create',
        name='DeFi LP Monitor',
        script='/root/.hermes/profiles/gentech/scripts/cron-wrapper.py',
        args='--job defi-lp-consolidated --script /root/.hermes/profiles/gentech/scripts/defi-lp-consolidated.py',
        schedule='0 */6 * * *')
```

**Workflow enforced by wrapper:**
```
1. 🚀 Start job → log timestamp
2. 🔍 Run preflight → check data freshness, API health
3. ▶️ Execute job → with 10-minute timeout
4. 📊 Record health → cron-health.py --record <job_id> <exit_code>
5. ✅ Report status → success or failure
```

**Wrapper arguments:**
- `--job <job_id>` — Job ID for health tracking
- `--script <path>` — Script to run
- `--command "<cmd>"` — Shell command to run (alternative to script)
- `--skip-preflight` — Bypass preflight (rare, for emergencies)

**Audit results (Jul 4, 2026):**
- 39 jobs total
- Model routing: 90% compliant (good)
- Drift-vulnerable jobs: 2 found and fixed
- **Wrapper integration: 0/39 jobs** — **WORKFLOW GAP**
- **Health tracking: 0/39 jobs** — **WORKFLOW GAP**

**Next actions:**
1. Update top 5 high-value jobs to use wrapper
2. Create daily health check cron job
3. Verify workflow compliance via manual test runs

### Anti-Pattern 8: Wrapper Exists But Never Deployed

**Bug:** Agent created `cron-health.py` + `cron-wrapper.py` but zero cron jobs were updated to use them. The infrastructure exists but isn't integrated.

**Fix:** When creating wrapper/verification infrastructure, immediately update existing jobs to use it.

**Pattern:**
1. Create wrapper/health tracking scripts
2. Update existing jobs in batches (5-10 at a time)
3. Test each batch manually
4. Deploy to production
5. Verify health data appears in tracking

**Where to look:** After creating wrapper/health scripts, check if any jobs reference them. Search cron job list for wrapper path.

**Detection pattern:**
```bash
# List all jobs
cronjob(action='list')

# Check how many use wrapper
wrapper_jobs = [j for j in jobs if 'cron-wrapper.py' in str(j.get('script', ''))]
print(f"Jobs using wrapper: {len(wrapper_jobs)}/{len(jobs)}")
```

**Real-world example (Jul 4, 2026):**
- Created cron-health.py + cron-wrapper.py
- Audit revealed 0/39 jobs using wrapper
- User asked: "we have to find a way to check to see if the cron jobs run after they're initiated"
- Fix needed: Update jobs to use wrapper + health tracking

## For Agent Kit Users

This pattern is part of the Agent Kit trust layer. When deploying agents that make decisions based on data:

1. **Always verify before acting** — never assume data is fresh
2. **Auto-correct when possible** — don't just flag, fix
3. **Banner when you can't fix** — make stale data impossible to miss
4. **Log the verification** — prove the agent checked truth
5. **Track health** — use cron-health.py for all jobs
6. **Enforce workflows** — use cron-wrapper.py for all jobs

The preflight script is the reference implementation. Copy it or adapt it for your own agent infrastructure.
