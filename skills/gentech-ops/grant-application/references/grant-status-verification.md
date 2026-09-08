# Grant Status Verification — Verify Against Official Pages, Not Aggregators

## The lesson (proven Aug 15, 2026)
Twice in one session a grant was flagged **OPEN** from third-party aggregator listings, but the **official program page** showed it **CLOSED**:

| Grant | Aggregator said | Official page showed |
|-------|----------------|----------------------|
| **AI Grant (aigrant.org)** | "Open, rolling" | "Batch 4 closed" (recurring — wait for Batch 5) |
| **The Graph Grants** | "Open, rolling" | "No open RFPs at this time" |
| **Circle Developer Grants** | "Open" | First 2026 cohort awarded Mar; "stay tuned for reopening" |
| **CDP AI Builder Grants** | "Current, $15K" | Page dated **Aug 2024** (deadline Sep 2024) — 2 years stale |

## Hard rules
1. **Extract the OFFICIAL program domain before recommending.** Never trust a third-party listing's "Open"/"Active" label. Official sources:
   - `aigrant.org` / `aigrant.com`
   - `thegraph.com/grants`
   - `esp.ethereum.foundation/applicants`
   - `circle.com/grant`
2. **Check the DATE on program pages and blog posts.** A viral/sourced article may be from a prior year. "CDP AI Builder" looked current in search but the Coinbase page was dated Aug 16, 2024.
3. **"Recurring" ≠ "open."** Batch/cycle programs (AI Grant Batch 4, Circle "reopening") are closed between windows even though the program "exists."
4. **"Rolling" ≠ "infinite."** Annual budgets exhaust; rolling portals close.
5. **When a grant matters, extract the official page** (`web_extract` its URL). If that's ambiguous, browser-verify. Only then classify OPEN / WATCH / CLOSED.

## Classify into three tiers before drafting
- ✅ **Still Open** — official portal accepting, rolling deadline confirmed on the OFFICIAL page
- ⚠️ **Watch** — recurring/batch program between windows (draft is ready, fire when it reopens)
- ❌ **Closed** — deadline passed, page dated to a prior year, program wound down

## Action pattern
When the official page shows closed/recurring, **save the draft anyway** to a reference/queue note flagged "watch — fire when <next batch> opens," then move on. Drafts are reusable across cycles; don't discard them. Keep the drafts in `09-Green Room/grant-application-drafts.md` and the queue in `03-Strategies/Grant-Applications-Queue.md` with accurate statuses.

## Why this matters for GenTech
Spending time drafting against a closed grant wastes effort and erodes trust ("I flagged it open and it wasn't"). A 60-second official-page extraction prevents recommending an unavailable program. When Jordan challenges a status, the fix is always: go to the source page, read the actual current state, correct the record immediately.
