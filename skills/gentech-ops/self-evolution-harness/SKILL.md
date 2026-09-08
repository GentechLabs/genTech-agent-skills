---
name: self-evolution-harness
description: "Self-Evolution Harness — cron-driven agent that makes the agent measurably better over time. Constitution-governed, witness-fed, fix-first. Single-agent design: the cron job IS the Evolution agent."
category: gentech-ops
version: 2.0.0
author: Gentech
tags: [self-evolution, harness, constitutional-ai, witness-log, fix-dont-just-report, bootstrap]
---

# Self-Evolution Harness

## Overview

A cron-driven self-improvement loop. The harness cron job (this session) acts as the **Evolution** agent: it reads the constitution, checks the witness log for real friction, proposes a grounded improvement, and **executes it immediately** (fix, don't just report).

**Multi-agent design (current).** The harness runs four separate cron jobs:

| Role | Schedule | Job ID | Purpose |
|------|----------|--------|---------|
| Evolution | `0 */4 * * *` | 22d8ad319fd4 | Read constitution, check witness log, propose + execute improvements |
| Critic | `2 */4 * * *` | 8f71e23cbfd6 | Audit Evolution's output for stagnation, data corruption, action-type monoculture |
| Verifier | `0 */6 * * *` | 6e771a4bf8a3 | Check past-due predictions, record outcomes, produce critique entries |
| Gardener | `0 4 1,8,15,22 * *` | c1fc1e48409a | Skill-pruning and credential-health maintenance (monthly) |

The Critic and Verifier roles have converged: the Verifier now also produces critique entries (checking prediction outcomes + data integrity) in the same run. This is a deliberate simplification — the Verifier's 6-hour cadence catches stale state faster than the Critic's 4-hour offset, and the Critic focuses on deeper stagnation analysis.

All jobs use `opencode-go → ollama-cloud` as the model provider (switched from the original `deepseek-v4-flash` via a batch job).

## Location

**Canonical harness home: `/root/.hermes/profiles/gentech/harness/`** — this is the tree
all four crons use as Workdir. The `/root/.hermes/harness/` path that earlier versions of
this skill documented was a **split-brain duplicate** with its own git history and its own
`facts/`; it was archived to `/root/.hermes/harness.orphan-20260731` in evolve-21 after
confirming zero crons referenced it. Do not recreate it.

- Constitution: `harness/constitution.md`
- Facts directory: `harness/facts/` (witness-log, predictions, prediction-outcomes,
  execution-log, recommendation, critique-log, harness-state, cleanup-log)
- Execution loop: `harness/scripts/execution-loop.sh` (note the `scripts/` prefix)

## The Execution Loop

`execution-loop.sh` supports four modes:

| Mode | Purpose |
|------|---------|
| `evolve` | Read constitution, check witness log, run the evolution cycle |
| `critique` | Review the last recommendation for evidence and action-bearing quality |
| `verify` | Check all 7 harness files exist and are non-empty |
| `garden` | Placeholder for future skill-pruning/credential-health tasks |

## Core Principle: Fix, Don't Just Report

Evolution's job is to **fix** problems, not file them. If it identifies:
- A stale build queue item → remove it
- An expired credential → check the source and update
- A broken config → fix the config
- A dormant skill → archive it

Only escalate to Jordan if the fix requires his input, credentials, or a decision.

## The Constitution (Articles I-V)

Five articles, all binding:

- **Article I: Evidence Gate** — Every recommendation must cite specific, inspectable evidence (tool output, file content, error logs, conversation transcript). Hunches and extrapolations are not evidence.
- **Article II: Allowlist** — Evolution may only recommend: (a) adding new skills, (b) patching outdated skills, (c) improving the constitution, (d) improving the critique process. It may NOT recommend disabling safety gating, modifying production data without confirmation, or bypassing user consent.
- **Article III: Falsifiability** — Every prediction must be measurable. "This will reduce errors" is not falsifiable. "This will reduce X error from 5/wk to <2/wk" is.
- **Article IV: Action Bearing** — Evolution must produce a concrete, executable action. Observations without actionable next steps are noise, not recommendations.
- All evidence, recommendations, and critiques survive in `/root/.hermes/profiles/gentech/harness/facts/`. No ephemeral knowledge.

## Cycle Protocol (8 Steps)

Each cycle follows this exact sequence:

1. **Read constitution** — load `/root/.hermes/harness/constitution.md`
2. **Read critique log** — if last 3 entries are unaddressed, address them; new hypothesis disallowed
3. **Generate goal** — ask "What concrete user-facing capability is currently weak?"; write to recommendation.md BEFORE reading existing files
4. **Ground in evidence** — read witness-log.md, harness-state.md, execution-log.md, skills inventory; cite one witness by timestamp
5. **Write recommendation.md** — with RECOMMENDED_ACTION, CONFIDENCE, REASONING fields
6. **Append prediction** — write falsifiable prediction to predictions.md BEFORE executing
7. **Execute** — `cd /root/.hermes/profiles/gentech/harness && bash execution-loop.sh evolve 2>&1 | tail -15`
8. **Record outcomes** — after execution, verify ALL past-due predictions (not just the current one) and record verdicts in `facts/prediction-outcomes.md`. Cross-reference predictions.md (entries past DUE) against prediction-outcomes.md and fill in any gaps. This prevents the Verifier or Critic from finding stale outcomes. If the Verifier cron is too slow to check 1-cycle predictions (e.g., every 2 days), the Evolution agent must backfill outcomes itself — do not wait for the Verifier.

## Pitfalls

- **Empty witness log** — if no friction is recorded, Evolution has nothing to act on. Seed the witness log with current-state evidence on first cycle.
- **No execution loop** — the harness is a static directory without `execution-loop.sh`. Always create the loop before running cycles.
- **Phantom paths** — the original skill documented `/root/.hermes/profiles/gentech/harness/` but the actual harness lives at `/root/.hermes/harness/`. Always verify the actual path with `ls /root/.hermes/harness/` before referencing. **Fixed Jul 29, 2026** — all paths in this skill now correct.
- **Silent fallback to phantom path** — all 5 harness scripts originally used `HERMES_HOME="${HERMES_HOME:-$HOME/hermes-harness}"` as a fallback when auto-detect failed. The path `$HOME/hermes-harness` does not exist on this system. When auto-detect failed (e.g., script copied outside the harness tree), the script silently created phantom directories and wrote data to a location no one ever checks. **Fixed evolve-8 (Jul 28, 2026)** — replaced with a hard error: `echo "FATAL: cannot determine HERMES_HOME" >&2; exit 1`. See `references/auto-detect-hard-fail.md` for the full pattern and verification steps.
- **No cron trigger (RESOLVED Jul 29, 2026)** — the harness had no cron entry and only ran when manually invoked. Cycle 2 added `0 8 * * * cd /root/.hermes/harness && bash execution-loop.sh evolve >> /root/.hermes/harness/facts/cron-output.log 2>&1`. The cron sits between the gateway restart (06:25) and the opportunity scanner (09:00).
- **Proposal-only amendments** — Evolution cannot modify constitution.md directly. It writes proposals to `facts/amendment-proposal.md` for human review.
- **Awk field-index bug in `read-external-feedback()`** — When parsing `- Verdict: HEALTHY` lines with `awk '{print $2}'`, the result is `Verdict:` (the label), not `HEALTHY` (the value). The value is at `$3`. This affects any bash function that parses `key: value` format lines with awk. **Fix (evolve-14, Jul 29 2026):** Use `$3` for the value field. The `read-external-feedback()` function in `execution-loop.sh` had all three field extractions (verdict, severity, action) using `$2` instead of `$3`, meaning the abort-on-high-severity guard never worked. Verify with: `grep -c 'awk.*print $3' scripts/execution-loop.sh` — must return 3.
- **`skill-automation.sh` was a stub for `facts-cleanup` (FIXED evolve-17, Jul 29 2026)** — The `facts-cleanup` action type dispatched to `skill-automation.sh` which had no real handler — it printed "no specific skill wired for facts-cleanup" and returned success. Every `facts-cleanup` cycle required the Evolution agent to execute the actual work manually. **Fixed evolve-17:** `skill-automation.sh` now has a real `facts-cleanup` handler that updates `harness-state.md` header, adds the latest critique entry to the Critique Status section, and updates the Last Action section. The handler is verified working — it updated the header from evolve-16 to evolve-17, added the evolve-16 critique to status, and committed to git. Other action types (`update_script`, `create_skill`) still need handlers wired in, but `facts-cleanup` covers 9 of the last 10 recommendations.

- **`skill-automation.sh` facts-cleanup handler does NOT update Last Action Change/Result text (evolve-18, Jul 29 2026)** — The handler updates the `## Last Action — Cycle evolve-N` heading but leaves the `- Change:` and `- Result:` lines showing the PREVIOUS cycle's detail text. After the dispatcher runs, you must manually fix these two lines with a `patch` call. Example:
  ```
  patch path=facts/harness-state.md old_string="Change: <old text>" new_string="Change: <new text>"
  ```
  Then `git add -A && git commit -m "evolve-N: fix Last Action section text"`. This is a known gap in the handler — it only updates the heading, not the content.

- **`skill-automation.sh` `local` keyword in case arms (FIXED evolve-17, Jul 29 2026)** — Bash's `case` is NOT a function. The `local` keyword can only be used inside functions. Using `local` inside a case arm produces `can only be used in a function` error. Fix: remove all `local` keywords from case arms, use plain variable assignment instead. This was discovered during the evolve-17 fix when the first attempt at the `facts-cleanup` handler failed with this error.

- **`_get_cycle()` uses `grep -oP` (GNU grep only)** — The `_get_cycle()` helper function uses `grep -oP '#\\d+'` which requires Perl-compatible regex (`-P` flag). This is available in GNU grep (Linux) but NOT in macOS grep. This script runs on Linux (VPS), so it works. If porting to macOS, use `grep -o '#[0-9]\\+'` instead. Documented here so future porting doesn't rediscover this.

- **`execution-loop.sh` lives at `scripts/execution-loop.sh`, not at harness root** — The skill's Cycle Protocol step 7 says `bash execution-loop.sh evolve` but the actual file is at `scripts/execution-loop.sh`. Running from the harness root without the `scripts/` prefix produces `No such file or directory`. Always use `bash scripts/execution-loop.sh evolve` from the harness directory. This was discovered in evolve-17 (Jul 29, 2026) when the documented command failed.

  **Impact:** The harness is configured to run autonomously but the evolve action is incapable of producing change. Every 4-hour cycle is wasted. The Critic's counter-recommendations accumulate unaddressed because the script has no implementation loop.

  **Fix required:** Replace the evolve case with a real implementation loop that:
  1. Reads `recommendation.md` and extracts `RECOMMENDED_ACTION`
  2. Dispatches to the appropriate handler (git init, create prediction-outcomes.md, add witnesses)
  3. Updates `harness-state.md` cycle count
  4. Appends to `execution-log.md`

  **Verification:** After the fix, `bash execution-loop.sh evolve` should produce changes in at least one tracked file (recommendation.md, harness-state.md, execution-log.md, or predictions.md). Run `md5sum facts/*.md` before and after to confirm.

**Implementation details of the fix:**
- The original stub had `case "$ACTION" in ... facts-cleanup) log "no specific skill wired for '$ACTION'" ... exit 0` — it logged and returned success without doing anything.
- The fix replaces the `facts-cleanup` case arm with actual operations: reads the current cycle from `recommendation.md`, updates `harness-state.md` header via `sed`, adds the latest critique entry to the Critique Status section, and updates the Last Action section.
- **Pitfall avoided:** `local` keyword in bash case arms. Bash's `case` is NOT a function — `local` can only be used inside functions. The first attempt used `local` variables inside the case arm and failed with "can only be used in a function". Fix: remove all `local` keywords from case arms, use plain variable assignment instead.
- **Pitfall avoided:** `_get_cycle()` function uses `grep -oP '#\d+'` which requires Perl-compatible regex. The `-P` flag is available in GNU grep (Linux) but NOT in macOS grep. This script runs on Linux (VPS), so it works. If porting to macOS, use `grep -o '#[0-9]\+'` instead.
- **Verification:** Run `bash harness/scripts/skill-automation.sh facts-cleanup` from the harness directory. Expected output: `[timestamp] facts-cleanup: updating state files`, `[timestamp] updated header to Cycle evolve-N`, `[timestamp] updated Last Action section`, `[timestamp] facts-cleanup complete`, exit code 0.
- **Execution loop lives at `scripts/execution-loop.sh`, not at harness root** — The skill's Cycle Protocol step 7 says `bash execution-loop.sh evolve` but the actual file is at `scripts/execution-loop.sh`. Running from the harness root without the `scripts/` prefix produces `No such file or directory`. Always use `bash scripts/execution-loop.sh evolve` from the harness directory. This was discovered in evolve-17 (Jul 29, 2026) when the documented command failed.

## Guard: `ABORTED: <verdict> <severity> unaddressed`

`evolve` refuses to dispatch while the last `- Action:` line in `facts/critique-log.md`
is not `ADDRESSED` and severity is `critical|high`. Fixing the problem on disk is NOT
enough — you must append a **Resolution Entry** carrying `- Verdict: RESOLVED`,
`- Severity: low`, `- Action: ADDRESSED`, then re-run. Also: re-verify every
counter-recommendation bullet against live state before executing it — the Critic's
view can be hours stale and "NOT APPLICABLE, already self-resolved" is a valid,
recordable outcome. Full recipe + the orphan-tree archive check:
`references/unaddressed-critique-abort.md`.

## Pitfall: dispatch without an audit trail

Through evolve-20, `execute_action()` in `scripts/execution-loop.sh` dispatched actions
and **never wrote `$EXECUTION_LOG`** — evolve-18 and evolve-20 committed code to git yet
appeared nowhere in `facts/execution-log.md`, which is the user-facing answer to "what
has the harness changed lately?". Fixed evolve-21 by adding `_append_execution_log()`
and calling it unconditionally on BOTH the normal dispatch path and the unknown-action
skip path. General rule for this harness: any code path that can mutate state must write
its own log line — never rely on the agent remembering to append by hand.
Verify: `grep -c '_append_execution_log' scripts/execution-loop.sh` >= 3.

## Pitfall: half-computed state files, truncated logs, empty DETAIL

Three related defects fixed in evolve-22 — full recipe in
`references/computed-fields-and-audit-integrity.md`:

1. **Partial automation is not a fix.** `refresh-next-events.sh` computed only the
   `## Next Events` block; the header and `## Last Action — Cycle N` label stayed
   hand-edited, so harness-state staleness recurred **5×** while being declared
   "structurally fixed" each time. Added `scripts/refresh-harness-state.sh` (derives both
   from `facts/recommendation.md`) and wired it beside `refresh-next-events.sh`. Rule: if
   a critique names the same file stale twice, enumerate *every* hand-edited field in it.
2. **Never truncate the audit trail.** `_append_execution_log()` used `${a_detail:0:200}`
   and severed its own first entry mid-token. Slice removed. Verify:
   `grep -c 'a_detail:0:200' scripts/execution-loop.sh` → 0.
3. **`_parse_field()` now reads multi-line blocks.** A `DETAIL:` field whose value is on
   the following lines used to parse as empty and log `- detail:` with nothing after it.

## Pitfall: leaked raw DETAIL + duplicate log entries (evolve-24)

Three cycles in a row shipped a "computed field" fix that broke the adjacent line.
Full recipe: `references/idempotent-audit-trail-and-sanitised-fields.md`.

1. **Sanitise at the boundary.** `refresh-harness-state.sh` pasted the raw
   `- detail:` string into the user-facing `- Change:` line, leaking internal batch-job
   IDs and code spans. Strip code spans, collapse whitespace, cap at 180 chars *before*
   substitution. Fix the pipe, not the leaked string.
2. **Make `_append_execution_log()` idempotent.** It fired on every dispatch, so
   re-running `evolve` inside one cycle left phantom stubs (`^## evolve-23` × 3).
   Fingerprint `(cycle, action, detail)` into an `<!-- fp:xxx -->` marker and skip on
   match. Do NOT key on `facts/.dispatch-state` field 3 — that's a per-arm counter, not
   a global sequence. Verify by running `evolve` twice: the second must print
   `already present, skipping`.
3. **A missing `DETAIL:` field logs silently empty** and propagates a blank `- Change:`
   into harness-state.md. Always write a plain `DETAIL:` line into recommendation.md
   before dispatching.

## Pitfall: compound shell commands get rejected by the command layer

Long one-liners that chain `&&` with `$(...)` substitution and several `grep -c`
calls are refused. Split them: one `bash -n` per call, verification as bare
`grep -c` invocations rather than `echo "x=$(grep -c ...)"`, heredocs on their own
line. This is a command-shape constraint — restructure and it runs.

## Pitfall: re-probe before executing a stale counter-recommendation

The Critic's view can be hours old. In evolve-22 it prescribed a gnome-keyring fix for
`pay=NO_ACCOUNT`; a live probe showed the state had changed to
`pay_cli_not_installed` (`which pay` empty). Always re-verify external state before
acting, and rewrite any user-facing decision block to match reality — a stale options
list is worse than none, because the user acts on it.

## Recommendation Format Requirement

The `execution-loop.sh` parser (`_parse_field` function) uses `awk` to match lines starting with the field name followed by `:`. It does NOT handle markdown headings (`## RECOMMENDED_ACTION:`). The recommendation file MUST use plain field names:

```
RECOMMENDED_ACTION: update_script
DETAIL: One-line description of the change
CONFIDENCE: high
REASONING: Multi-line explanation of why this change is needed
EXPECTED_OUTCOME: What the user will observe after the fix
```

**Do NOT use markdown headings** for the field names. The parser will return empty and the cycle will report "could not parse RECOMMENDED_ACTION from recommendation".

Since evolve-22 the parser DOES accept a multi-line value: `DETAIL:` alone on its line
followed by indented/numbered continuation lines is joined into one string, terminated by
the next ALLCAPS field, a blank line, or a markdown heading.

## Prediction Metric Pattern

When writing a prediction metric that checks a specific provider's status in a multi-provider log file, use `grep` to isolate the provider's lines before `tail`:

```python
# ❌ WRONG — tail -1 may hit a different provider's line
METRIC: tail -1 /path/to/log | grep -q 'provider_x=200'

# ✅ CORRECT — grep isolates the provider, then tail gets the latest
METRIC: grep 'provider_x=' /path/to/log | tail -1 | grep -q 'provider_x=200'
```

This is especially important for `credential-health.log` which interleaves 6 providers (github, telegram, elevenlabs, blockrun, pay, q402) in the same file. A bare `tail -1` will hit whichever provider wrote last, not the one being predicted.

## Stale Env Var Pattern

When a cron job or probe script reports a false failure because a stale env var overrides a valid credential:

1. **Check the env var** — `env | grep <VAR>` to see if it's still exported in the current session
2. **Check the config file** — the valid credential may live in a config file (e.g. `~/.config/gh/hosts.yml`) while the env var is stale
3. **Fix the source** — remove the stale var from `.env` so new sessions don't inherit it
4. **Fix the probe** — add `unset <VAR>` before the probe call so the current session's stale export doesn't interfere
5. **Verify** — run the probe and check the log shows the correct status

**Real-world example (evolve-6):** The `GITHUB_TOKEN` env var was an expired `ghp_` token. The valid token lived in `~/.config/gh/hosts.yml`. `gh auth status` checks `GITHUB_TOKEN` first, so it always failed. Fix: `unset GITHUB_TOKEN` in `credential-health.sh` before `gh auth status`.

## Delivery: silent by default (Jordan Aug 12)

Jordan explicitly asked the Harness jobs to **stop spamming the chat**. All four
crons (Evolution, Critic, Verifier, Gardener) are set to `deliver: local` — they
save output to files and only surface in the chat when something genuinely needs
Jordan's attention. Do NOT change these back to `origin`/`telegram` delivery.
The daily digest (7 AM) and EOD digest (11 PM) are the only jobs that deliver to
Jordan's chat, and they summarize harness state there.

## Overgrown Cron Prompt Pattern

When a harness cron job (Critic, Verifier, Gardener) starts failing with ollama HTTP 402 ("extra usage only, balance empty"):

1. **Check the prompt size** — `wc -c prompts/<job>.md`. If >2KB, the prompt may be inflating input tokens.
2. **Check the skill file** — if the prompt's detailed workflow is already documented in a skill file (e.g. `harness-critic.md`), the prompt is redundant.
3. **Trim the prompt** — move detailed workflow to the skill file. Keep the cron prompt to essential instructions + a reference to the skill.
4. **Recreate the job** — `hermes cron remove <id>` then `hermes cron create --name "..." --deliver "origin" --workdir "..." "schedule" "$(cat prompts/job.md)"`
5. **Verify** — check the next run's input token count via `state.db` session_model_usage table.

**Real-world example (evolve-9, Jul 28 2026):** The Harness Critic prompt was 6,580 bytes of detailed workflow instructions that were already in `harness-critic.md`. This caused 960K input tokens per run on ollama-cloud, exhausting the free tier. Trimmed to 1,309 bytes. The Critic now runs successfully on the same model as Evolution.

**Note:** `hermes cron create` and `hermes cron edit` do NOT accept `--model` or `--provider` flags. The model is inherited from the default provider in `config.yaml`. If you need a different model for a harness job, you must edit `jobs.json` directly after creation.

## Verifier Cron Too Slow for 1-Cycle Predictions

The Verifier cron job checks past-due predictions and records outcomes. If its schedule is too infrequent (e.g., every 2 days), predictions with `DUE: 1 cycle` will never be checked in time, and the missing-outcomes gap compounds every cycle.

**Symptoms:**
- `prediction-outcomes.md` has entries for recent predictions but older ones (#1-#5, etc.) are missing
- The Verifier's "Last run" timestamp is 40+ hours ago
- The Critic flags "prediction outcomes going unrecorded" in multiple consecutive cycles

**Fix:**
1. Check the Verifier schedule: `hermes cron list | grep -A 10 'Verifier'`
2. If schedule is `0 4 */2 * *` or similar (every 2+ days), increase to every 6 hours: `hermes cron edit <job_id> --schedule "0 */6 * * *"`
3. Backfill the missing outcomes immediately — do not wait for the Verifier. Each past-due prediction can be verified against execution-log.md evidence.
4. Verify: `hermes cron list | grep -A 3 'Verifier' | grep '0 \\*/6'`

**Real-world example (evolve-12, Jul 28 2026):** The Verifier ran every 2 days. Predictions #1-#5 were past-due for 2+ days with no outcome recorded. The evolve-10 and evolve-11 Critic runs both flagged this but it was never addressed until evolve-12. Fix: changed schedule to `0 */6 * * *` and backfilled all 5 outcomes from execution-log evidence.

## No-Op Cycle Pattern (evolve-13+)

When the harness reaches a healthy steady state — all predictions have outcomes, Verifier runs on schedule, action diversity sustained, no unaddressed critiques — the Evolution agent should:

1. **Commit the Verifier's changes** to git (the Verifier produces outcomes and critique entries that are uncommitted)
2. **Update harness-state.md** to reflect the current cycle as last action
3. **Fix the Last Action Change/Result text** — the `skill-automation.sh` facts-cleanup handler only updates the heading, not the content. Use `patch` to replace the stale `- Change:` and `- Result:` lines with the current cycle's detail.
4. **Update execution-log.md** with the dispatch entry
5. **Produce a no-op report** — the cycle did not change any user-facing capability because none needed changing

This is NOT stagnation. The constitution (Article III) explicitly grants the right to remain silent. Three consecutive no-ops trigger a review of cycle frequency, not a panic to justify existence.

**Real-world example (evolve-13, Jul 28 2026):** The Verifier ran at 18:04Z on the new 6-hour schedule, produced outcomes for #11 and #12, added the evolve-12 critique entry, and cleaned up old resolved entries from witness-log.md. Evolution committed these changes to git (5fa098f, c2e4b0f), updated state files, and reported no-op. The only unresolved witness entry (Pay wallet NO_ACCOUNT) requires Jordan's decision — no tool-available fix exists.

**Real-world example (evolve-14, Jul 29 2026):** No-op cycle with a bonus bugfix. While committing the Critic's evolve-13 critique entry, discovered that `read-external-feedback()` in `execution-loop.sh` was silently broken — `awk '{print $2}'` on `- Verdict: HEALTHY` returns `Verdict:` (the label), not `HEALTHY` (the value at `$3`). Fixed all three field extractions (verdict, severity, action) from `$2` → `$3`. Verified: log now shows `verdict=HEALTHY severity=low` instead of broken `verdict=Verdict: severity=Severity:`.

## Critic Restoration Pattern

When the Harness Critic cron job fails with `ollama HTTP 402` or similar token/balance errors, see `references/critic-restoration-verification.md` for the trim-prompt, recreate-job, and self-confirming-prediction recipe.

Every cycle produces one report:
- **ACTION REPORT** — what was fixed and the result
- **NO-OP REPORT** — when no friction found
- `[SILENT]` — only when ALL conditions met: no actionable friction, no outstanding amendments/predictions/critic counter-recommendations

## Prediction System

Every action cycle pre-registers a falsifiable prediction before executing. Predictions go in `facts/predictions.md` with:
- Statement (what will happen)
- Falsification (what would prove it false)
- Confidence (0-100%)
- Deadline (when it must be checked)

## Bootstrap History

- Jul 26: Harness directory created with constitution.md, facts/ directory, critique-log.md, harness-state.md, recommendation.md placeholder
- Jul 27 (Cycle 1): Full bootstrap — created execution-loop.sh, witness-log.md (3 entries), predictions.md (2 predictions), execution-log.md, updated recommendation.md with real RECOMMENDED_ACTION, ran first evolve cycle, updated harness-state.md to "Active — Cycle 1 completed"

## Gardener Role (skill-pruning + credential-health + log compaction)

The Gardener cron (`0 4 1,8,15,22 * *`) runs three maintenance passes:

1. **Dormant skills** — scan `harness/skills/`; any skill file untouched > 30 days and
   unreferenced by prompts/scripts/cron is a candidate for archive. The
   `harness-gardener.sh` script prints the dormant/active split (mtime-based proxy).
2. **Credential health** — run `bash scripts/credential-health.sh`; it probes
   github/telegram/elevenlabs/blockrun/q402 and appends to `facts/credential-health.log`.
   Exit 0 = all OK. A `401`/`KEY_EXPIRED` means re-auth is needed — flag it, don't
   silently pass.
3. **Log compaction** — any `facts/` or `logs/` file over 200 lines gets compacted.
   Full recipe + the header-preservation pitfall: `references/log-compaction.md`.

Report `[SILENT]` only when: no dormant skills, no credential expiry, and the cleanup
log is empty. Otherwise report what was pruned/archived/expired and why.

## Support Files

- `references/critic-restoration-verification.md` — How to restore the Harness Critic cron job when it fails with ollama HTTP 402, including reliable verification commands and the self-confirming prediction pattern
- `references/cycle-1-bootstrap.md` — Bootstrap history and first-cycle evidence
- `references/auto-detect-hard-fail.md` — The auto-detect + hard-fail pattern used by all 5 harness scripts, with verification steps and the phantom-path bug history
- `references/facts-cleanup-pattern.md` — How to fix stale state files, record missing prediction outcomes, and initialize git in one pass. Use action type `facts-cleanup` to break `update_script` monoculture streaks.
- `references/backfill-missing-prediction-outcomes.md` — How to verify and record outcomes for past-due predictions when the Verifier cron is too slow. Includes common verification commands and the outcome format.
- `references/unaddressed-critique-abort.md` — Unblocking `ABORTED: <verdict> <severity> unaddressed`: the Resolution Entry format the guard requires, re-verifying stale counter-recommendations, and the pre-archive cron Workdir check.
- `references/computed-fields-and-audit-integrity.md` — Killing recurring state-file staleness by computing every hand-edited field, un-truncating the execution log, the multi-line `_parse_field()` awk, and re-probing ground truth before acting on a stale counter-recommendation.
- `references/idempotent-audit-trail-and-sanitised-fields.md` — Sanitising internal DETAIL before it reaches a user-facing file, fingerprint-based idempotency for `_append_execution_log()`, the silently-empty `DETAIL:` trap, and the compound-shell-command shape constraint.
- `references/log-compaction.md` — The Gardener's log-compaction workflow: archive head to `facts/.tmp/`, keep last 100 lines, preserve doc headers, record in cleanup-log. Includes the header-preservation dedup pitfall (blank-line sentinel silently drops a title) and the don't-grade-predictions-during-compaction rule.
