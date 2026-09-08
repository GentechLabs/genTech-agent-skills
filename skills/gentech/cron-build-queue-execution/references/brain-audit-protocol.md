# Brain Audit Protocol

When the nightly build queue's Gentech items are all externally blocked (awaiting Jordan's keys, funding, or decisions), switch to Brain Audit mode instead of going idle.

## Trigger

Run this when **all** of the following are true:
- Gentech has pending/in_progress cloud items
- Every one of them has an external blocker (marked `needs_jordan: true`, or blocked on API keys/wallet keys/funding)
- None can be advanced autonomously in the current session

## Protocol

### 0. Recalibrate Queue Summary First

**The first thing to do — before any scanning or research — is check whether the queue's `summary` section is accurate.** The `summary.needs_jordan`, `summary.pending`, and `summary.blocked` counts drift when items are removed from `items[]` without being recalculated. Confirmed Jul 25, 2026: the summary said 31 needs_jordan and 22 pending when only 6 items needed Jordan and 5 were pending.

Recalculate from scratch with:
```python
from collections import Counter
c = Counter(i.get('status', 'unknown') for i in data['items'])
data['summary']['total'] = len(data['items'])
data['summary']['in_progress'] = c.get('in_progress', 0)
data['summary']['pending'] = c.get('pending', 0)
data['summary']['blocked'] = c.get('blocked', 0)
data['summary']['needs_jordan'] = sum(1 for i in data['items'] if i.get('needs_jordan'))
data['summary']['shipped'] = 0  # Shipped items are removed from items[]
```

Only after the summary is correct should you proceed with scanning. A bad summary pollutes every downstream consumer (handoffs, Morning Digest, Jordan's review).

### 0.5. Check From-the-Forge Handoff Freshness

Before reconciling Forge completions from `01-HANDOFFS/from-the-forge.md`, read line 1 (the date header). If the date is >2 days old, the completions were already processed — skip reconciliation entirely. Rely on `consolidation_notes[]` in the queue for recent shipped items instead.

### 1. Scan the Vault Infrastructure

Check these files for stale data, gaps, or broken links. Also check:

| Location | What to check |
|----------|---------------|
| `07-Ideas/` | Legacy directory — may contain spec files worth promoting (e.g. `metaray-3d-reconstruction.md` → copy to `09-Green Room/specs/`). Pattern: copy the file, add a link in `09-Green Room/ideas.md` under "Promoted from Legacy", then clean empty legacy dirs after confirmation. Do NOT delete non-empty legacy dirs — flag for Jordan. |
| `02-HANDOFFS/` | Typically only a 0-byte README.md — safe to delete. |
| `11-Mess Hall/` | Check for stale `build_queue.json` duplicates (already DEPRECATED-stamped files can be safely deleted). |
| `09-Green Room/ideas.md` | Check for dead links to spec files that no longer exist (common in the "Other Mess Hall Ideas" section after vault consolidation). Replace dead links with concept descriptions or remove them.

### 2. Update ideas.md — Stale Links & Status

- Update the date/timestamp at the top
- Move shipped items from checkbox lists to the **Completed** section (`[x]`)
- **Fix stale links** — The "Other Mess Hall Ideas" section may reference spec files under `11-Mess Hall/ideas/` that were lost during vault consolidation. If the referenced files no longer exist on disk, replace the dead links with plain concept descriptions or remove the entries entirely.
- Add checkbox items for **newly discovered opportunities** (ecosystem integrations, hackathons, partnerships)
- Add a section for **items that entered the build queue** via Jordan brainstorm but aren't yet reflected in ideas
- If Ready-to-Test items are blocked, add a note about the blocker
- **Correct queue statuses** — Items marked `in_progress` may have only a design doc with zero implementation. If nobody is actively writing code, correct to `pending`. This prevents the queue from misleading others about what's being built.

### 3. Create/Update considerations.md

If `11-Mess Hall/considerations.md` doesn't exist, create it. Surface every pending decision that's blocking progress:

- Each decision gets a section with: Ask, Status, Trade-off, Stack
- Group by priority (🔴 urgent, 🟡 important, 🟢 nice-to-have)
- Add a "Previously Decided" section for closed items
- Link to related queue items by ID

### 3.5. Run a PR Status Sweep

Before researching new items, verify the status of all open PRs in the portfolio. This is a standard Brain Audit step, not an optional extra.

See `references/pr-status-sweep.md` for the full protocol. Key pattern:

```bash
# Discover all PRs from any fork name in one call:
gh api repos/<owner>/<repo>/pulls --jq '.[] | select(.head.label | startswith("ProtoJay4789")) | {number, state, title: .title[0:60]}'

# Confirm a PR exists without knowing the fork name:
gh api repos/<owner>/<repo>/pulls --method POST \
  -f head='ProtoJay4789:<branch>' \
  -f base='main' \
  -f title='test'
# Returns 422 "already exists" = PR is real. Returns 201 = just created (don't do this).
```

**Why this matters:** PRs in the portfolio may have been submitted from forks with unpredictable names (e.g. `pay-skills-fork` instead of `pay-skills`). Querying the upstream repo's PR list by `head.label` catches all of them regardless of fork name. A 422 response from the create endpoint is the most reliable way to confirm a PR exists without needing to know the fork name.

**Update the PR portfolio** with verified PR numbers and statuses after the sweep. Propagate any status changes to the build queue (e.g. a PR that was blocking an item is now merged → unblock the item).

### 4. Infrastructure Health Check

Verify every service claim in the queue notes against actual running processes. Do NOT trust "deployed" or "running" claims from queue notes alone:

```bash
# x402 Gateway
curl -s http://localhost:8088/v1/health          # Should return {"status":"ok",...}

# Nginx / gentechlabs.net
curl -sI https://gentechlabs.net | head -5        # HTTP 200?

# All listening services
ss -tlnp | grep -E '808[0-9]|80|443'             # Ports expected vs actual

# Arcade or other special apps
curl -sI https://arcade.gentechlabs.net | head -3 # HTTP 200?
```

Log results in the brain note. If a service that the queue claims is running is actually down, note it in the Morning Digest.

### 4.5. Hackathon Scan

Use `blockrun_search` to find active hackathons with deadlines <30 days, especially those aligned with the x402/compliance/revenue stack:

```
Sources: ["web"]  (3-5 results to cap spend at ~$0.08)
Queries: "x402 hackathon 2026", "AI agent payments hackathon", "AI agent hackathon deadline soon prize"
```

Cross-reference findings against existing queue items by name. For each hackathon NOT already in the queue:
- Sort by deadline (ASC)
- Flag any with ≤7 days remaining as `priority: urgent`
- Add to queue immediately with `needs_jordan: true` and a clear `detail` noting what Jordan needs to do
- Add a `consolidation_note` documenting the discovery

Confirmed Jul 25, 2026: AI Factory Hackathon (lablab.ai, Aug 3-10, $60K+ prize pool) was discovered this way and queued as #79.

### 6. Research Unblockable Items

Even when most items are blocked, at least one or two may have research/design work that doesn't need Jordan:

- **External integrations** (Coinbase AgentKit, r0x, pay-skills): Read READMEs, docs, issue trackers. Understand the integration path. Document prerequisites.
- **Spec/design work** (AAE Rank Engine, DeFi Dashboard): Can advance the spec without execution
- **Documentation gaps**: Find things that should be documented but aren't

For each item researched:
- Update the queue item's `detail` field with findings
- Note the next actionable step

### 7. Write Brain Notes

Save findings to `11-Mess Hall/agent-brain/YYYY-MM-DD-nightly-build.md` covering:
- What was researched and what was found
- What's blocked and why
- What should happen next (which items Jordan needs to unblock)
- Any alerts for the day (deadlines, urgent items for Forge)

### 8. Generate Fresh Handoffs

After all updates, run:
```bash
python3 /root/.hermes/profiles/gentech/scripts/build_queue_tick.py
```

This regenerates the Forge task list and Jordan items in `01-HANDOFFS/` with the latest queue state.

## Common Blockers Found

| Blocker | Typical Root Cause | What's Needed |
|---------|-------------------|---------------|
| No X/Twitter API keys | #39 Agent Credit Score posting | Jordan creates dev keys |
| No Solana USDC | #61 WURK microtask testing | Jordan sends ~$2-5 USDC |
| No Q402 API key | Subscription links, Q402 middleware | Jordan visits q402.quackai.ai |
| No deployer key | #38 AgentBridge deployment | Jordan provides key + testnet ETH |
| No GPU funding | #58 DeFi Model fine-tune | Jordan decides + funds $30-60 |

## Output

After a Brain Audit session, the user should see:
- Updated ideas.md with fresh checkbox state
- Considerations.md (created or updated) with surfaced decisions
- Build queue items updated with research findings
- Fresh handoffs in 01-HANDOFFS/
- Brain notes summarizing the night's work
