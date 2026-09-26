---
name: auto-fix-preflight
description: "Detect → Fix → Verify → Report pattern for preflight checks. Every issue detected gets auto-fixed, then verified, then reported."
tags: [preflight, auto-fix, verification, agent-kit, devops]
trigger: "When building preflight checks that should auto-fix issues, or when debugging why preflight keeps flagging the same issue."
related_skills:
  - ../cron-truth-layer/SKILL.md  # preflight verification pattern
  - ../preflight/SKILL.md  # the actual preflight script
version: 1.0.0
author: Gentech Labs
---

# Auto-Fix Preflight — Detect → Fix → Verify → Report

## The Problem

Preflight checks flag issues but don't fix them. The same warning appears every cron run. Users get annoyed. The issue never resolves.

## The Solution

Every preflight check should follow this cycle:

```
1. DETECT  — Find the issue
2. FIX     — Auto-fix it (if safe)
3. VERIFY  — Confirm the fix worked
4. REPORT  — Tell the user what happened
```

## Implementation Pattern

```python
def validate_something():
    """Detect → Fix → Verify → Report"""
    # 1. DETECT
    issue = detect_issue()
    if not issue:
        return ""  # silent = all good
    
    # 2. FIX (if safe)
    if is_safe_to_fix(issue):
        fix_result = attempt_fix(issue)
        
        # 3. VERIFY
        if verify_fixworked(fix_result):
            return f"✅ Fixed: {issue} → {fix_result}"
        else:
            return f"⚠️ Fix attempted but failed: {issue}"
    
    # 4. REPORT (can't auto-fix)
    return f"❌ Needs manual fix: {issue}"
```

## Example: Vault Sync

```python
def validate_vault_sync():
    """Auto-commit uncommitted vault changes."""
    # 1. DETECT
    result = subprocess.run(["git", "status", "--porcelain"], ...)
    if not result.stdout.strip():
        return ""  # nothing to fix
    
    changes = result.stdout.strip().split("\n")
    
    # 2. FIX
    subprocess.run(["git", "add", "-A"], ...)
    subprocess.run(["git", "commit", "-m", f"auto: {len(changes)} changes"], ...)
    push = subprocess.run(["git", "push"], ...)
    
    # 3. VERIFY
    if push.returncode == 0:
        return f"✅ Vault synced: {len(changes)} changes committed + pushed"
    else:
        return f"⚠️ Committed but push failed"
```

## Example: Stuck Git Rebase

```python
def validate_git_state():
    """Auto-abort stuck rebases."""
    # 1. DETECT
    if os.path.exists(".git/rebase-merge"):
        # 2. FIX
        subprocess.run(["git", "rebase", "--abort"], ...)
        # 3. VERIFY
        if not os.path.exists(".git/rebase-merge"):
            return "✅ Aborted stuck rebase"
        else:
            return "❌ Rebase abort failed — manual intervention needed"
    return ""
```

## Safe vs Unsafe Fixes

| Issue | Safe to Auto-Fix? | Why |
|-------|-------------------|-----|
| Uncommitted vault changes | ✅ Yes | Low risk, can be reverted |
| Stuck git rebase | ✅ Yes | Abort is safe, no data loss |
| Detached HEAD | ✅ Yes | Switch to main is safe |
| API key expired | ❌ No | Needs human decision |
| Config drift | ✅ Yes | On-chain is truth, auto-correct |
| Stale data | ⚠️ Maybe | Flag, but don't delete |
| Missing file | ❌ No | Needs investigation |

## Output Format

Always report in this format:

```
✅ [Fixed] What was wrong → What was done
⚠️ [Attempted] What was wrong → What was tried → Result
❌ [Manual] What was wrong → What needs to happen
```

## Critical Pitfall: Preflight Inside Debounce Gate

When a script has both preflight checks AND debounce/silence logic, the preflight MUST run AFTER the debounce check decides to send — not before.

**Wrong pattern (causes orphaned preflight messages):**
```python
def main():
    preflight()           # ← Always prints output
    if should_suppress():
        sys.exit(0)       # ← Silences report, but preflight already printed
    print(generate_report())
```

**Correct pattern:**
```python
def main():
    if should_suppress():
        sys.exit(0)       # ← Silent exit, zero output
    preflight()           # ← Only runs when report will be sent
    print(generate_report())
```

**Why this matters:** With `no_agent: true` cron jobs, stdout goes directly to the user. If preflight prints before the debounce gate, the user sees orphaned preflight messages with no report attached — exactly the noise pattern this skill is meant to prevent.

**Found:** `defi-lp-consolidated.py` (Jun 22, 2026) — preflight was printing vault-sync status even when debounce suppressed the report. Jordan explicitly flagged: "I'm still getting a lot of these preflight cron jobs instead of the cron job itself."

## ⚠️ Critical Pitfall: Auto-Fixing Drift When the Direction Is Unknown

"Two copies differ" does **not** tell you which one is right. Before auto-fixing any
copy-drift finding, establish the direction, or you will destroy work.

**Real case (2026-09-18, api-health-check fix layer):** `revenue-monitor.py` was
**39,184 B deployed vs 31,171 B in the vault** — the *live* file was newer and held
~8 KB that had never been committed. Auto-copying the canonical over it would have
deleted live code, silently, on a schedule.

**The rule — split targets into two classes:**

| Class | Know the authority? | Action |
|---|---|---|
| **Curated / reviewed** (hand-maintained table) | ✅ Yes — the canonical is the reviewed source | Auto-FIX |
| **Auto-discovered** (found by scanning) | ❌ No | **DETECT + REPORT only** |

For discovered drift, report the **direction** (compare mtimes) and let a human decide:
- *deployed is NEWER* → the vault copy is stale → **commit the live file**
- *canonical is NEWER* → the deployed copy is stale → safe to redeploy

Collapse N discovered items into **one summary line** plus a detail command; 30 paths
in a cron message buries the signal it exists to carry.

## Safety Gates Every Auto-Fix Needs

1. **Validate before deploying.** Compile the source text in memory
   (`compile(src, path, 'exec')`) before copying it over a working entry point.
   Deploying a broken canonical turns a quiet drift into a dead job.
2. **Verify after fixing.** Re-hash (or re-run the check) and confirm the fix landed.
   A fix that reports success without verification is indistinguishable from a no-op.
3. **Refresh the reported state.** Re-derive the finding after repairing, so the report
   never shows drift that was just healed.
4. **Report fixes — never hide them.** Silent self-healing lets the underlying habit
   (edit the source, never re-deploy) go unnoticed for months. The goal is a robust
   system, not an invisible symptom.
5. **Keep one read-only mode.** (`json`) so machine consumers and debugging can never
   trigger a write; add a `--no-fix` escape hatch.
6. **Never auto-delete.** Duplicate files, dead vhosts, anything where "remove it" is a
   plausible fix — those are **human decisions**. Diagnose instead (state latent vs live,
   give exact remedy commands) and mark them manual.

## ⚠️ Critical Pitfall: Matching a Word Shared by Both Branches

When summarising two opposite outcomes, never count by a substring they **both** contain.
Building this, a tally of "how many are deployed-newer" matched `"NEWER"` — but both
direction strings ended in "NEWER" (`deployed is NEWER` / `canonical is NEWER`), so it
reported **5** when the truth was **3**.

**Rule:** match the **full distinguishing phrase** (`"deployed is NEWER"`), and **check the
computed number against the underlying detail list** before shipping. A wrong count in a
health report is worse than no count — it is a plausible number nobody re-derives.

## For Agent Kit

This pattern is the "fix layer" of the truth architecture:

1. **Truth Layer** — verify data is fresh (cron-truth-layer)
2. **Fix Layer** — auto-fix what's safe (auto-fix-preflight)
3. **Report Layer** — tell the user what happened

Every cron job should have all three. Detect without fixing is noise. Fix without
verifying is guesswork. Verify without reporting is invisible. **Fix without knowing the
direction is data loss.**
