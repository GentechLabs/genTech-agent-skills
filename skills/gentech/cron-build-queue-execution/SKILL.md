---
name: cron-build-queue-execution
description: "Recurring nightly build session protocol — process the build queue autonomously, ship cloud items, generate handoffs, and produce the morning digest. Triggered by midnight ET cron job. Covers the full loop from reading queue state through delivering the Morning Digest."
version: 1.8.0
author: Gentech
tags: [gentech, cron, build-queue, nightly-session, handoff, brain-audit]
related_skills: [gentech-ops, gentech-build-workflow, dual-agent-coordination, cron-session-fresh-start]
---

# Cron Build Queue Execution — Nightly Session Protocol

Recurring autononomous cron workflow for processing the build queue during night hours (midnight ET) when Jordan is asleep. The cron job delivers the queue tick output as context, and Gentech executes the operational loop.

This is **not** about how to build a single product (see `gentech-build-workflow` for the 7-phase pipeline). This is about **which products to build, when, and how to pass them to the next agent**.

## Entry Point

The midnight ET cron job fires and delivers. The pipeline is fed by the **Forge evening handoff** (~10:30-11 PM ET):

```
Evening: Jordan + Forge on desktop (creative/dev/media)
  # Forge writes completions (01-HANDOFFS/forge-completions.md) + handoff (01-HANDOFFS/forge-to-gentech/)
  → Jordan syncs vault / goes to sleep
  → Midnight ET (4:00 UTC): Nightly Maintenance + Nightly Build Session fire
  → Gentech picks up Forge's handoff, works cloud/overnight items
  → Queue tick runs, brain notes saved
  → Morning digest delivered by 8 AM
```

**This is the confirmed operating rhythm.** Jordan works with Forge until ~10:30-11 PM. The handoff at the end of that session is the single source of truth for what Gentech should pick up overnight. If no handoff exists, Gentech works autonomously from the build queue, respecting platform tags.

The cron provides:
- **context_from** injection: the queue tick's stdout (`build_queue_tick.py` output)
- The tick reports: total items, status breakdown, agent assignments, urgent items, next-for-Forge, next-for-Gentech

## Execution Protocol (7 Steps)

### Step 0: Check if Queue Was Already Maintained

**The overnight maintenance cron (06:00 UTC) may run after a prior nightly session (04:00 UTC) already updated the queue.** Before doing any work, check the `updated` timestamp in `build_queue.json`:

```python
import json
q = json.load(open('/root/vaults/gentech/scripts/build_queue.json'))
updated = q.get('updated', '')
# If updated within the last 6 hours, the queue was already maintained
# by the Nightly Build Session — skip redundant work
```

If the queue was updated within the last 6 hours, skip Steps 1-5 and go directly to Step 6 (regenerate handoffs) and Step 7 (Morning Digest). The prior session already handled queue reconciliation, PR status checks, and item status updates.

**Exception:** If the cron job's purpose is specifically to check PR merge statuses (overnight maintenance), still run the PR status sweep — a PR could have been merged in the hours between the nightly session and the maintenance cron. But skip the full queue reconciliation (Step 1.5) if the queue was already reconciled.

### Step 1: Read Queue State

Process the tick output:
- How many items? What's their status breakdown (done / in-progress / pending / blocked)?
- Which items are urgent? What are their deadlines?
- What's assigned to Gentech (cloud items) vs Forge (desktop/GPU items) vs Jordan?

Also read the actual `build_queue.json` and the generated handoff files:
```bash
# Read generated handoffs
/root/vaults/gentech/01-HANDOFFS/<date>-forge-tasks.md
/root/vaults/gentech/01-HANDOFFS/<date>-jordan-items.md
```

### Step 1.5: Reconcile Queue Against Forge's Handoff

**The queue file can fall out of sync with reality.** Forge may add items during the evening desktop session that never make it into `build_queue.json`. The session handoff (`01-HANDOFFS/from-the-forge.md`) is the most recent snapshot of work in flight.

Read **the Forge handoff** (`01-HANDOFFS/from-the-forge.md`) and **the Forge completions** (`01-HANDOFFS/forge-completions.md`) and cross-reference every item listed there against the queue:

**Substep 0 — Check handoff freshness before trusting its completions:** Two file sources, two ages to verify:

   - **`from-the-forge.md`** — Read the date header on line 1. If >2 days old, its "completions" were already processed in an earlier session — re-processing them double-counts shipped items.
   - **`forge-completions.md`** — Check the "Last updated" line in the footer. This file is the Forge agent's canonical completions log and is often more current than from-the-forge.md (e.g. `forge-completions.md` dated Jul 24 while `from-the-forge.md` shows Jul 22).

   **When the handoffs disagree in age:** Prefer `forge-completions.md` as the primary completions source — it is the dedicated completions file and is updated independently of the nightly session handoff. Only cross-reference its shipped items if they overlap with items already recorded in `consolidation_notes[]`. Confirmed Jul 25, 2026: from-the-forge.md was dated Jul 22 (3 days stale) with 0 completions, while forge-completions.md was dated Jul 24 with 6 shipped items (#61, #59, #60, #66, #62, #65). All were already reconciled.

   When both are stale or the queue's consolidation_notes already cover the shipped items, skip the full reconciliation, note the staleness in the brain note, and fall through to Step 2 (cloud items). Use `consolidation_notes[]` as the ground truth for recently-shipped items.

1. **Extract completed items** — Forge's handoff has a "Completions" section listing items it shipped. For each completed item still present in `items[]`:
   - Remove it from the `items[]` array entirely
   - Increment `summary.shipped`
   - Add a consolidation note: `"Removed shipped item from Forge: #N — Name"`
   - This prevents ghost items from accumulating in the queue
2. **Extract all item IDs and names** from the handoff's queue table
3. For each item NOT found in `build_queue.json`, add it as a new queue entry
4. For each item FOUND in both but with a different `status`, update the queue to match the handoff

**Pitfall — items may share IDs across sources.** The handoff table often uses different ID numbers than the queue file (e.g. the queue has #28 as "Monad Agent Hub" while the handoff has #28 as "PixelRAG Demo"). Match by `name` (fuzzy), not by `id` alone. When IDs conflict, prefer the queue file's assignment for existing items and add handoff-only items at the end with free IDs.

**Pitfall — handoff date vs queue date.** The tick script generates handoff files with yesterday's date stamp (e.g. `2026-07-22-forge-tasks.md` even when running at 2026-07-23 04:00 UTC). The `from-the-forge.md` and `forge-completions.md` files are the canonical sources regardless of their dates. Always read both for the latest Forge completions, not the dated handoff file.

### Step 2: Pick Cloud Items to Work On

Gentech works **cloud** items only (desktop/GPU items go to Forge).

**Priority rules:**
1. **URGENT** items first — anything with a deadline today or sooner
2. **EASY** difficulty — complete quickly, build momentum
3. **MEDIUM** difficulty — only after all easy items are done
4. **NEVER start HARD items** during night session — they need focused daylight work

**Allowed items class:** items with `assigned_to: gentech` and `platform: cloud`.

**Platform tag dispatch system:**

| Tag | Who | When |
|-----|-----|------|
| `desktop` | Forge | Only when PC is on (GPU/local dev/media) |
| `cloud` | Gentech VPS or Forge-cloud | 24/7 — no special hardware needed |
| `either` | First available | Any agent picks it up |
| `gentech` | Gentech only | Infrastructure/strategy — always |

**Items to skip:**
- `desktop` items (Forge's lane — GPU, local builds, media)
- Jordan's personal items (wallet auth, signups, approvals — need his input)
- Blocked items (until dependency is resolved)
- Cancelled items (marked `cancelled` — don't re-open)

### Step 2.5: Queue Empty Fallback — Brain Audit Mode

**If Step 2 finds zero Gentech cloud items that are actually actionable** (no pending items assigned to gentech, OR all gentech-assigned items are blocked/Jordan-dependent), don't go silent. Switch to **Brain Audit Mode** instead. The distinction matters: the queue may show 7 gentech items, but if all 7 are blocked on Jordan, the actionable count is zero — you should check this before deciding there's nothing to do.

1. **Scan the vault** at `/root/vaults/gentech/` for:
   - Stale data in existing projects (outdated docs, dead links, incomplete specs)
   - **Stale nightly-report-*.md files in vault root** — These accumulate from interrupted `ob sync` or failed git push attempts. They are noise — record failed operations, not actual build work. Move them to `11-Mess Hall/agent-brain/` (if content has value) or delete them. Confirmed Jul 25, 2026: 3 stale reports found and moved in one pass. See `references/brain-audit-protocol.md` for the cleanup pattern.
   - Gaps in our documentation (missing READMEs, un-indexed folders)
   - Unresolved decisions in `11-Mess Hall/considerations.md`
   - Opportunities we're not tracking (new platforms, competitors, integrations)
   - **Legacy directories** — `07-Ideas/` may contain spec files worth promoting. Pattern: copy the file to `09-Green Room/specs/`, add a link in `09-Green Room/ideas.md` under a "Promoted from Legacy" section, then clean empty directories after confirmation. Do NOT delete non-empty legacy dirs — flag for Jordan. `02-HANDOFFS/` typically has only a README.md — safe to delete if 0 bytes. The `Gentech/` full vault copy has already been purged.
   - **ideas.md stale-link cleanup** — The `Other Mess Hall Ideas` section in `09-Green Room/ideas.md` may reference spec files under `11-Mess Hall/ideas/` or `11-Mess Hall/ideas.md` that vanished during vault consolidation. When these files no longer exist on disk, replace dead links with concept descriptions or remove them entirely. Proven Jul 23: 5 dead links cleaned in one pass.

2. **Audit existing ideas** in `09-Green Room/ideas.md`:
   - Check each checkbox item — is it still relevant? Ready to promote to the build queue?
   - Move shipped items to the Completed section
   - Mark stale/abandoned items clearly
   - **Correct queue item statuses** — Items marked `in_progress` may have zero code (design doc only, no implementation started). If nobody is actively building the code, correct to `pending` so the queue accurately reflects what's actually being worked on.

3. **Check BOTH ideas files** — there are two locations with different purposes:
   - `09-Green Room/ideas.md` — Action-ready, curated list (what to build next)
   - `11-Mess Hall/ideas.md` — Raw idea dump from conversations (15+ items, with detailed specs in `11-Mess Hall/ideas/`)
   - Cross-reference both. Promote ready items from Mess Hall to Green Room when they have clear next steps.
   - If an idea has a full spec document (check `11-Mess Hall/ideas/` for matching filenames), link it from the Green Room.

4. **Find new ideas** — scan recent cron outputs, session transcripts, and ecosystem activity:
   - What did the Opportunity Scanner find that we haven't acted on?
   - What new platforms went live recently (marketplaces, registries, hackathons)?
   - What gaps exist in our current tooling or infrastructure?
   - **Concrete: Run a hackathon scan** — Two-pass strategy for maximum coverage:

     **Pass 1 — Narrow/domain-specific:** Use `blockrun_search` with queries like
     `"x402" "hackathon" 2026`, `"AI agent payments" hackathon`, or `"most x402 payments" prize`.
     These catch prizes and tracks specifically aligned with our x402/compliance stack.

     **Pass 2 — Broad/discovery:** Use `blockrun_search` with queries like
     `"AI agent" "hackathon" July August 2026`. This cast a wider net and catches adjacent
     opportunities that the domain-specific queries miss. On Jul 25, 2026 this returned 6+
     distinct events including the Keeperhub Onchain Hackathon ($5K+, Jul 27 start) and
     HackerRank Orchestrate (Aug 1-7, 24hr virtual) — both missed by the narrow queries.

     Cross-reference findings against existing queue items by name to avoid duplicates.
     Sort results by deadline (ASC) and flag any with ≤7 days remaining for `priority: urgent`
     regardless of prize size. Add to queue immediately if not present. Confirmed Jul 25, 2026:
     AI Factory Hackathon (Aug 3-10, $60K+ prize pool) and Keeperhub Agents Onchain Hackathon
     (Jul 27, $5K+) were discovered this way.

5. **Run an infrastructure health check** — Before assuming services work, verify:
   - x402 Gateway: `curl -s http://localhost:8088/v1/health` — returns JSON with `"status":"ok"`?
   - Nginx: `curl -sI https://gentechlabs.net | head -5` — HTTP 200?
   - Listening ports: `ss -tlnp | grep -E '808[0-9]|80|443'` — all expected services running?
   - Arcade or other special services: `curl -sI https://arcade.gentechlabs.net` — HTTP 200?
   - Log results in brain note. Do NOT rely on queue notes' "deployed" claims alone — every service
     claim gets a curl check before you trust it in a handoff.

6. **Run a PR status sweep** — Check all open PRs in the PR portfolio (`10-Labs/pr-portfolio.md`) via `gh api`. See `references/pr-status-sweep.md` for the full protocol. Update the portfolio and queue items with any status changes.
   - **Maintenance check vs discovery sweep**: If the PR portfolio is already populated with verified PRs, run a targeted **maintenance check** — verify each known PR is still open with `gh api repos/<owner>/<repo>/pulls/<number> --jq '{state, merged_at}'`. This is faster and cheaper than a full sweep (1 API call per PR vs scanning the entire repo). Only run a full **discovery sweep** when you're looking for new PRs or the portfolio is stale/empty.
   - **REST API for direct PR verification**: `gh api repos/<owner>/<repo>/pulls/<number> --jq '{state, merged_at}'` uses the REST API (60 req/hr, separate from GraphQL's 0/hr limit). When GraphQL is exhausted (0 remaining), REST still works. Use this for targeted checks of known PR numbers.
   - **Phantom PR detection:** The portfolio may contain entries claiming PRs were submitted when the fork or PR never actually existed (known pattern from GitHub API rate limit failures). Verify a sample of claimed PRs by checking that the fork repo exists (`gh api repos/ProtoJay4789/<fork-name>`) and that the PR number exists in the upstream repo (`gh pr view <number> -R <owner/repo>`). See `off-hours-autonomous-work/references/pr-portfolio-audit.md` for the full detection protocol.
   - **⚠️ CRITICAL: GraphQL vs REST rate limits.** `gh pr list` uses GraphQL which has a SEPARATE rate limit bucket from REST API. A GraphQL rate limit hit returns empty results silently — you will see zero PRs even when PRs exist. This caused a false "phantom PR" conclusion in Jul 2026: `gh pr list` returned empty, but `gh api repos/<owner>/<repo>/pulls --method POST` (REST) returned 422 "already exists" for the same PRs. **Verification protocol:** When `gh pr list` returns empty but you expect PRs to exist, verify via REST by attempting to create the PR. A 422 "already exists" response confirms the PR is real. A 201 response means the PR was just created. A 403 means rate limited — stop and report partial results.
   - **Rate limit guard:** Check `gh api rate_limit` before starting. If remaining < 10, skip the sweep and report partial results. Stop immediately on 403 — do not retry. Note that GraphQL and REST have separate rate limit counters — you may have REST capacity even when GraphQL is exhausted.

7. **Add promising findings** to `09-Green Room/ideas.md` using checkbox format (`- [ ]` for new, `- [x]` for shipped)
   - High-confidence ideas can be promoted directly to the build queue with `status: "idea"`
   - Save a brain note to `11-Mess Hall/agent-brain/` documenting what was found

**Why this exists:** Jordan explicitly requested this (Jul 16, 2026): "If there's nothing on the build list, audit the brain, add to existing ideas or find others. This way we don't have to have a separate cron for auditing the brains." The brain audit replaces what would have been a standalone cron job, keeping our cron count lean.

**DEFAULT BEHAVIOR (Jordan directive, Aug 3, 2026):** When the build lane is gated shut (queue mostly `needs_jordan: true` / `human_gated: true`, zero autonomously-shippable Gentech cloud items), this is the **default fallback, not an exception**. Do BOTH, in order:
1. **Push everything that needs Jordan to his action list** — every decision-gated and action-gated item goes to `01-HANDOFFS/<date>-jordan-items.md` so nothing stalls unseen. Regenerate handoffs so his list is complete.
2. **Then run Vault Maintenance / Brain Audit Mode** — do NOT sit idle. Spend the gated time productively: scan `11-Mess Hall/notes.md` / agent-brain for unfinished notes, flesh out or improve ideas in `09-Green Room/ideas.md`, promote raw ideas from `11-Mess Hall/ideas.md`, clean stale references/dead links, and run the infra health check + PR sweep (Steps 5-6 above).

The rule: **a gated queue never means "nothing to do"** — it means "Jordan's list gets complete, and I use the time to maintain the vault." Never report `[SILENT]` in this state; always report what was moved to Jordan's list and what vault work was done.

**Relationship to building:** The Brain Audit happens WHEN there are no items to build. If queue items appear later (e.g. Jordan adds them during the audit), step back to building with the new items. Brain Audit is not a separate cron — it is the empty-queue fallback for the existing nightly session.

**What NOT to do in Brain Audit Mode:**
- Do not report [SILENT] — always report what was found, even if nothing new
- Do not attempt to build anything unless a queue item explicitly appears
- Do not change production scripts, configs, or deployed services

**What TO do with findings:** If Brain Audit discovers actionable data (PR status changes, stale queue notes, new items to add), DO update the queue and regenerate handoffs. The "do not modify handoff files" rule only applies when nothing changed. Findings that affect the queue (e.g. a PR was closed without merge, a blocker was resolved) should propagate to handoffs so Forge and Jordan see the latest state. The tick script is cheap to re-run — run it after any queue mutation.

**Signal for switching OUT of Brain Audit Mode:** If during vault scanning you discover something that SHOULD be a queue item (a clear build opportunity), add it to `09-Green Room/ideas.md` first, NOT the build queue. Only promote to build queue if urgent and immediately actionable. The default path: ideas.md → future queue tick → Jordan reviews → build queue.

### Step 3: Build and Verify

For each selected item:
1. Check vault for existing design docs / context
2. Follow `gentech-build-workflow` (fast-track is OK when scope is clear)
3. Build the minimum viable deliverable
4. **Always verify** — run the code, check tests, confirm output
5. For static HTML/asset updates: verify BOTH local origin AND public URL. Cloudflare/CDN caches (`Cache-Control: max-age`) may serve stale content even after file updates on disk. Use `curl -s http://localhost/<path>` (origin) vs `curl -s https://domain/<path>` (CDN) to distinguish deployment success from cache staleness.
6. Write a brain note at `11-Mess Hall/agent-brain/<date>-<session-name>.md`

**Night session deliverables can be:**
- Design docs (`09-Green Room/designs/`)
- Engine/script files (`03-Strategies/scripts/`)
- Configuration files
- Updated dashboard HTML
- Content drafts

### Step 4: Update Build Queue

Update `/root/vaults/gentech/scripts/build_queue.json`:

| Action | `status` value |
|--------|---------------|
| Completed item | `"shipped"` |
| Started but not finished | `"in_progress"` |
| New item discovered | Add new entry with `"in_progress"` |
| Blocked item | `"blocked"` + add `blocked_on` field |

Also update the `"updated"` timestamp at the top of the file.

Add new items to the `items` array (after the last existing entry) with:
- Sequential `id` (check existing highest ID first)
- Clear `name`, `status`, `assigned_to`, `priority`, `difficulty`, `platform`
- Detailed `notes` field with file paths and what was done

When adding items that need Jordan (wallet auth, signups, approvals), set:
- `assigned_to: "jordan"`
- `needs_jordan: true`
- `platform: "any"`

These will appear in Jordan's action items handoff after the next queue tick.

### Step 5: Write Agent Brain Note

Save a session record to `11-Mess Hall/agent-brain/<date>-<session-name>.md`:

```markdown
# Agent Brain — <Session Name> <Date>

## What I Did
- <Item A> — <summary>
- <Item B> — <summary>

## What Forge Should Do Tomorrow
- <Item X> — <reason>
- <Item Y> — <reason>

## What's Waiting on Jordan
- <Item Z> — <reason>
```

This is a stopping-point record, not a status report. Write it when you finish a session phase.

### Step 6: Regenerate Handoffs

After updating the queue, regenerate the Forge task list and Jordan items:

```bash
python3 /root/.hermes/profiles/gentech/scripts/build_queue_tick.py
```

This produces:
- `01-HANDOFFS/gentech-to-forge/<date>-forge-tasks.md` — Forge's morning queue
- `01-HANDOFFS/<date>-jordan-items.md` — Jordan's pending items

**Do not skip this step.** The handoff files are how Forge knows what to work on in the morning.

Verify the handoff files were created (non-empty):
```bash
wc -l /root/vaults/gentech/01-HANDOFFS/gentech-to-forge/<date>-forge-tasks.md
```

**Augment if needed:** After verification, read the generated handoff and check whether any items listed as "Ready" actually have `needs_jordan: true` in the queue. The tick script does not check this field. If Jordan-dependent items appear actionable, add a warning section at the top of the handoff listing which items need Jordan first. Proven Jul 25: #63, #68, #7 were shown as "Ready" in the auto-generated handoff but all need Jordan.

**Also verify the Jordan items file** after regeneration. The tick script categorizes items by `status` only, not by `gate_type`. Items with an imminent deadline (`≤7 days`) need to be in "Needs Your Action" not "Needs Your Decision". Items with `gate_type: "human"` belong under "Needs Your Action" (requires browser/physical action) while `gate_type: "decision"` items belong under "Needs Your Decision". If the auto-generated file misclassifies items, augment it by moving urgent-deadline items up and marking them clearly. Confirmed Jul 25, 2026: #72 OKX Hackathon (T-2 day deadline) was auto-listed under "Needs Your Decision" — it needed "Needs Your Action" with an 🚨 marker.

### Step 7: Produce Morning Digest

The final output is the Morning Digest — a structured report covering:

1. **Night Session Recap** — what Gentech worked on, what was shipped
2. **Forge's Morning Queue** — priority-sorted items for Forge (URGENT flagged, deadline shown)
3. **Jordan's Action Items** — pending items needing Jordan attention, with clear due markers
4. **Blockers** — items that can't proceed, with reason and dependency
5. **Quick Stats** — queue totals, this session's output

This digest IS the cron job's final output — it auto-delivers to the configured destination.

## Pitfalls

- **Two ideas files exist** — `09-Green Room/ideas.md` (curated) and `11-Mess Hall/ideas.md` (raw dump). Always check both during brain audit. The raw dump often has 10x more content but with no priority labels. Promote items from Mess Hall to Green Room, never the reverse.
- **`11-Mess Hall/ideas.md` may not exist** — The raw idea dump file can be empty or missing entirely. When it's absent, check `11-Mess Hall/ideas/` directory for individual spec files instead. These are the actual raw ideas with full specs. Cross-reference them against `09-Green Room/ideas.md` for items that should be promoted.
- **Handoff paths are single source of truth** — All handoffs go to `01-HANDOFFS/`. The old `Gentech/handoffs/` path is dead code from the vault consolidation. If you find scripts still referencing the old path, fix them immediately to prevent the dual-build-list problem.
- **Git in cron scripts needs explicit remote+branch** — `git pull --rebase` fails silently in `nightly-maintenance.py` because the vault has multiple remotes (`origin` = portfolio, `vault` = gentech-vault.git). Every git command in a cron script MUST use the explicit form: `git pull --rebase vault main`, `git push vault main`. Also stash before pull — unstaged cron output blocks the rebase.
- **PREFER soft-reset over rebase for single-file queue updates** — When you only changed `build_queue.json` and the remote has new commits, skip `git pull --rebase` entirely. Use `git fetch origin && git reset --soft origin/main && git commit -m "queue: ..." && git push` directly. Rebase replays every remote commit against your change, risking cascading conflicts from old commits that also touched the queue file. Soft-reset keeps your changes staged, moves HEAD to remote, and commits cleanly on top. Confirmed Jul 27, 2026: 16-commit rebase failed on commit 3 with an old queue-file conflict; soft-reset completed in 3 commands.
- **Git rebase hits 5+ conflicts on auto-generated files** — `git pull --rebase vault main` often fails on nightly hub sync commits that touch `DeFi/defi-data.json` or `Gaming/vanito-music.json`. These are auto-generated data files with no semantic value — resolving 36 rebase steps one by one wastes the session. Two recovery options depending on the situation:

  **Option A — Soft-reset (local work to preserve):** Abort the rebase (`git rebase --abort`), fetch the remote (`git fetch vault main`), then soft-reset your work on top: `git reset --soft vault/main && git commit -m "nightly: <description>" && git push vault main`. This squashes all local changes into one commit on top of remote HEAD and avoids the multi-conflict rebase hell entirely. Use this when `git pull --rebase` fails on commit 3+ of a long chain. Exception: do NOT use soft-reset when the local branch has independent commits you need to preserve (e.g. handoff files, queue updates from a previous session that haven't been pushed yet) — in that case, cherry-pick those commits onto the remote HEAD instead of one squashed commit.

  **Option B — Hard-reset (remote is the authority):** When the remote has advanced past your local state, OR when your local changes can be reconstructed from scratch (queue updates from the current session, not historical commits), accept the remote as base and rewrite your changes on top. Steps: `git rebase --abort`, `git fetch origin`, `git reset --hard origin/main`, then rewrite the changed files from scratch, then `git add`, `git commit`, `git push`. This is faster than soft-reset when the remote IS the canonical source (e.g. another agent pushed changes you don't have) and your local work was all derived from the same input data (the queue file). Only use Option B when you can reconstruct your changes from session context — do NOT reset if your local has commits with work that can't be re-derived (e.g. handoff content that wasn't saved anywhere else). Confirmed Jul 26, 2026: remote had diverged with old queue data (v16) while local had un-pushed v28 — hard-reset to remote, then rewrote the queue file from session context.
- **Handoff file may not exist on first run** — The tick script creates it. If the file is empty (0 bytes), the tick hasn't run yet. Run it, then read.
- **Queue item IDs may skip or be non-sequential** — Some items have been cancelled or deleted. Check `id` values to find the next available ID.
- **Design docs may already exist** — Search the vault before creating new ones. `09-Green Room/designs/` is the canonical location.
- **`patch` fails on JSON queue with escaped Unicode** — `build_queue.json` uses escaped Unicode sequences (e.g. `\\u2014`, `\\u2026`) in its `detail` fields. The `patch` tool's fuzzy matching can fail against these sequences (finding 17+ matches or missing the match entirely). Fix: use Python's `json.load`/`json.dump` via `terminal` (`python3 << 'PYEOF'`) for reliable queue updates instead of `patch`. Keep the patch approach for other files — this is specific to the JSON queue file with its escaped characters.
- **`patch` also fails on JSON files with merge conflict markers** — When `git pull` produces a merge conflict in `build_queue.json`, the file contains `<<<<<<< HEAD`, `=======`, `>>>>>>>` markers that make it invalid JSON. The `patch` tool refuses to write because the candidate content fails JSON syntax validation. Fix: (1) use `sed -i '3,7d'` to remove the conflict marker lines, (2) verify with `python3 -c "import json; json.load(open('scripts/build_queue.json'))"`, (3) use Python `json.dump` for the actual content update. Do NOT use `patch` on a conflicted JSON file — it will always fail.
- **Stale-notes scan is now UNCONDITIONAL (SUPERSEDED Aug 5, 2026)** — The old limitation ("stale-notes/Brain-Audit scan only runs when the build lane is gated") was FIXED with a dedicated `stale-notes-scanner.py` that runs EVERY night regardless of lane state and feeds a `## 🗂 Stale / unaddressed notes` Morning Digest section. See the "V4 Nightly Loop" section above. The old symptom to remember: shipping a build overnight used to silently skip notes maintenance, so a productive night never surfaced stale notes — that gap is closed. If a future session sees the old conditional behavior, the fix is to make the stale-notes scan unconditional, not to re-embed the gated-lane dependency.
- **Blocker notes go stale — cross-check against the most recent handoff (proven Aug 6, 2026)**: An item's `note`/`detail` describing a blocker can be wrong by the next session. The classic drift: a note says "needs Jordan to fund wallet" when the handoff confirms the wallet is now funded and the blocker has *shifted* (e.g. to a platform outage). Before committing an overnight maintenance pass, read the newest handoff file(s) and diff the queue's blocker/status claims against them:
  ```bash
  ls -t 01-HANDOFFS/*.md | head -3   # newest handoffs
  grep -rn -i "<wallet-addr>|<item-name>" 01-HANDOFFS/ | head
  ```
  **Rule:** a note must describe the *current* blocker, not the historical one. If a blocker was resolved, say so and name the new blocker (or "none"). This prevents re-asking Jordan for something already done. Real case: KeeperHub item #1 still claimed wallet `0x53A8…8EA` had 0 ETH/0 USDC and "needs Jordan to fund ~$15 ETH + ~$10 USDC", but the Aug 5/6 handoff showed 10 USDC + 0.0079 ETH on Base and a platform-outage blocker with a retry cron armed. Updating that note was the highest-value edit of the whole maintenance pass — the queue would otherwise have re-asked Jordan for funding he already provided.
- **SILENT mode** — If genuinely nothing was done (all items blocked, nothing changed), respond with exactly `[SILENT]` to suppress delivery. Never combine `[SILENT]` with content. But in Brain Audit Mode, always report findings — never use [SILENT].
- **\"All blocked on Jordan\" is a valid stopping point** — When every Gentech item is blocked on Jordan (wallet addresses, fork permissions, API keys), do not spin wheels trying to invent work. Run queue triage (stale file cleanup, deprecation stamping, ideas.md audit), regenerate handoffs, and produce the Morning Digest with a clear \"zero actionable items\" section. The bottleneck is Jordan's attention — flag it prominently in the digest rather than fabricating work.
- **Legacy directories — promote content, then clean empties** — `Gentech/` full vault copy has been purged (Jul 23). `07-Ideas/` may contain spec files worth promoting: copy to `09-Green Room/specs/`, link in ideas.md, then clean empty dirs. `02-HANDOFFS/` typically has only a 0-byte README.md — safe to delete. Do NOT delete non-empty legacy dirs — flag for Jordan.\n- **Gentech/ legacy directory promotion — files already git-tracked in main vault** — When promoting files from `Gentech/` to the main vault, the files are already tracked by git in their main vault paths (e.g. `09-Green Room/circle-developer-grant-application.md` is already in git's index). Use `cp` (not `mv`) to copy the content over, then `git add` to stage the updated content. The `Gentech/` copy can remain as a stale reference — it's the main vault path that matters. Confirmed Jul 28, 2026: 10 unique files promoted this way, all already git-tracked.
- **`summary.shipped` is cumulative across all queue versions** — Shipped items are REMOVED from the `items[]` array, not kept with `status: "shipped"`. The `summary.shipped` counter is the only record of how many items ever shipped. This means a count check like `sum(1 for i in items if i.get('status') == 'shipped')` will always return 0, even though `summary.shipped` may be 27. When verifying summary counts, use `summary.shipped` directly — do not derive it from the items array.
- **`updated` timestamp format varies** — The queue file may use ISO format (`2026-07-23T04:03:07Z`) or human-readable (`2026-07-23 06:00 UTC`). When comparing timestamps, parse both formats. The Nightly Build Session (04:00 UTC) uses ISO; the Overnight Maintenance cron (06:00 UTC) uses human-readable. Both are valid — just be aware when doing time-window checks.
- **`git checkout --ours` vs `--theirs` — CORRECT SEMANTICS in merge conflicts** — In a merge conflict during `git pull vault main`, `--ours` = LOCAL (what HEAD already has), `--theirs` = REMOTE (what `vault/main` is merging in). **To accept the remote/upstream version** (the vault's changes, which are usually more recent), use `git checkout --theirs <file> && git add <file>`. **To keep your local version**, use `git checkout --ours <file> && git add <file>`. The old version of this pitfall had these swapped — double-check before running. After resolving, run `git diff --cached -- <file>` to verify content. Do NOT attempt `patch` on a conflicted JSON file — conflict markers make it invalid JSON so `patch` always fails; use Python `json.dump` instead.\n- **DU (deleted/modified) merge conflicts** — When `git pull vault main` produces status `DU <file>` ("deleted in working tree, updated in index"), it means git's staged version (from the remote) modified a file that HEAD deleted locally. This happens when one agent deletes a handoff file that another agent continued updating. Fix: restore the remote version with `git checkout --theirs <file> && git add <file> && git commit -m "merge: accept upstream <file>"`. Verify with `git status` and `git log --oneline -1` after.

## V4 Nightly Loop (Aug 5, 2026) — Deterministic Gate + All-Group Return Loop

The nightly pipeline was redesigned from "gated → brain audit only" to a **deterministic
build-or-maintain loop** that runs EVERY night, plus a symmetric return path for EVERY
group agent. This overrides the Forge-centric assumptions elsewhere in this skill.

### 1. Deterministic gate — build vs maintain is a NUMBER, not a judgment call
Compute the autonomous-work count instead of deciding "is the lane gated?":
```python
python3 -c "import json; q=json.load(open('/root/vaults/gentech/scripts/build_queue.json')); items=[i for i in q if isinstance(i,dict)]; print(sum(1 for i in items if i.get('status')=='pending' and not i.get('needs_jordan')))"
```
- `count >= 1` → BUILD MODE. Ship 1-2 verified items (tests pass, code runs). Never fabricate.
- `count == 0` → MAINTENANCE MODE. Do NOT idle. Run ALL: stale-notes scan → flesh/promote an
  idea → `ob sync` → git push → infra health check. A gated queue never means "nothing to do."

### 2. Stale-notes scan runs EVERY night, not just when gated
This FIXES the pitfall elsewhere on this page ("Brain Audit only fires when gated — a
productive build night silently skips notes maintenance"). Run `stale-notes-scanner.py`
nightly regardless of lane state; feed its output to the Morning Digest as a
`## 🗂 Stale / unaddressed notes` section. Shipping and vault maintenance are no longer
mutually exclusive.
- Scanner: `/root/.hermes/profiles/gentech/scripts/stale-notes-scanner.py`
- Reads `11-Mess Hall/considerations.md` (open checkboxes + frontmatter date), `agent-brain/`
  (dated notes with "Jordan:" asks), `09-Green Room/ideas.md` (unchecked ideas).
- Outputs JSON `{stale[], all_open[], counts}`. `[SILENT]` only if nothing changed AND nothing stale.

### 3. All-group return loop (not just Forge)
Every group agent gets a symmetric return path so work flows BACK overnight:
- Return folders: `01-HANDOFFS/<group>-to-gentech/` (dated notes)
- Completion files: `01-HANDOFFS/<group>-completions.md` (item IDs shipped, `- **#<id>** ...`)
- Groups: labs, entertainment, finance (Treasury), hq, forge.
- Scanner: `/root/.hermes/profiles/gentech/scripts/group-returns-scanner.py` reads EVERY
  group's return, extracts shipped IDs + notes, emits JSON.
- Nightly Build applies returned IDs to the queue (status → shipped, note group+date).
- Morning Digest surfaces `## 🔁 Group returns received` + `## 🗂 Stale / unaddressed notes`.
- Both scanners attach to the cron jobs as `script` (their JSON auto-injects into context).
- **Cron script paths MUST be relative to the profile scripts dir** (`/root/.hermes/profiles/gentech/scripts/`), not absolute vault paths — the cron scheduler rejects absolute paths. Keep a copy of each scanner in the profile scripts dir and reference it by filename.
- **The return-loop plumbing is NOT enough — each group agent needs the instruction in its SOUL.md (Aug 6, 2026).** The folders + scanner existed, but only Forge was writing real completions; labs/entertainment/finance/hq all sat at `*None this session.*` placeholders. The fix was adding an **"End-of-Day Report (REQUIRED)"** section to each group agent's `SOUL.md` (gizmo, gentech-treasury, desmond, dmob, yoyo) telling it to write a dated note to `01-HANDOFFS/<group>-to-gentech/YYYY-MM-DD.md` + append shipped IDs to `<group>-completions.md` + `git add -A && git commit` at end of session. **Diagnostic:** if the Morning Digest's `## 🔁 Group returns received` is always empty, check the group agents' SOUL.md files for the instruction — the folders existing doesn't mean the agents know to write to them. Note: SOUL.md files live in each profile dir (NOT the vault), so they're not git-tracked and take effect on the agent's next session; the `<your-group>` placeholder should be confirmed per-agent.

### 4. Forge = desktop lane (routing rule, Jordan Aug 5)
"Forge only" is shorthand for **desktop only**. Forge runs on Jordan's PC. Route anything
needing desktop access to Forge REGARDLESS of group: MetaMask/wallet signing, browser
logins + account actions (uphive wallet link, OKX), local files/desktop-only tools, opening
a website Jordan has to see. Direct these to `gentech-to-forge/` (or note "Forge (desktop)").
Forge returns via `forge-to-gentech/` + `forge-completions.md`. This generalizes the old
"desktop/GPU items go to Forge" platform-tag rule to a cross-cutting routing criterion.

## Reference: Item Selection Priority Matrix

```
              | URGENT deadline  | HIGH priority  | MEDIUM priority  | LOW priority
--------------+-----------------+---------------+-----------------+-------------
EASY difficulty| DO FIRST         | DO SECOND      | DO IF TIME       | SKIP
MEDIUM diff.  | DO IF EASY DONE  | DO IF EASY DONE| DO IF EASY DONE  | SKIP
HARD diff.    | NOTE FOR MORNING | NOTE FOR MORN. | NOTE FOR MORN.   | NEVER START
```

## Common Items by Lane

| Lane | Platform | Who | Examples |
|------|----------|-----|----------|
| Gentech | Cloud | Gentech | API builds, Python scripts, configs, content, research, design docs |
| Forge | Desktop | Forge | RomM, PixelRAG, Local TTS, Character API, GPU work |
| Forge | Either | Forge | Hackathon submissions (OKX), platform registrations |
| Jordan | Desktop | Jordan | Wallet auth, signups, approvals, account setup |
| Jordan | Cloud | Jordan | Seller applications, Pika signup, business phone |

## Related Skills

| Skill | How it relates |
|-------|---------------|
| `gentech-build-workflow` | The 7-phase build pipeline — invoked during Step 3 for each item |
| `gentech-ops` | Broader operational workflows — this skill is a specific instance |
| `dual-agent-coordination` | Gentech/Forge coordination — this skill produces the handoffs |
| `cron-session-fresh-start` | Morning session pruning — this skill runs just before it |

## References

- [`references/nightly-maintenance-pattern.md`](references/nightly-maintenance-pattern.md) — The `nightly-maintenance.py` script design, git sync pattern, cron wiring, and update procedure. Used by the V4 Nightly Maintenance cron job at midnight ET.
- [`references/pr-status-sweep.md`](references/pr-status-sweep.md) — Repeatable PR status sweep protocol for Brain Audit Mode. Covers REST vs GraphQL rate limits, portfolio updates, and queue propagation.
