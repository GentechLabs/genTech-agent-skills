---
name: queue-truth-verification
description: Verify build-queue deploy claims against the live filesystem/URL BEFORE re-deploying or trusting a queue note. Prevents duplicate deploys and stale "needs Jordan" notes when work was actually shipped in a prior session.
---

# Queue Truth Verification

## Problem
Build-queue notes are snapshots of intent, not proof of current state. An item can say "needs Jordan to deploy production build" when the artifact is ALREADY live — deployed in a prior session, or sitting at the site root. Trusting the note leads to duplicate deploys, wasted work, and a false "blocked" status.

## The Rule
**Before deploying, marking blocked, or acting on a deploy claim, VERIFY the actual current state.** The filesystem and live URL are the source of truth, not the queue note.

## Verification Checklist
Run these BEFORE any deploy/undeploy/status change:

1. **Check the claimed live URL** — `curl -s -o /dev/null -w "%{http_code}" URL` and confirm it serves the right content (grep for a distinctive title/string, not just a 200 — nginx SPA fallback returns 200 even for missing paths).
2. **Inspect the deploy target filesystem** — `ls` the directory; confirm the expected files exist before you copy over them.
3. **Check alternate locations** — the artifact may live at a different path than the queue implies (e.g. a game that is the site root `/` rather than a `/cabinet/<name>/` subdir).
4. **Only then** update the queue note to reflect reality and do the minimal action (or none).

## Pattern (proven Aug 3, 2026)
Super Arcade Tennis queue item #4 said "needs Jordan to deploy production build." It was ALREADY live at arcade.gentechlabs.net root (it's the landing page). Result of not checking first:
- Deployed a redundant copy to `/cabinet/super-arcade-tennis/`
- Added a duplicate nav link
- Then had to revert both after discovering the root already served it.

**Fix:** curl the root URL first, read the title, `grep -c` a distinctive game string, check the cabinet dir. Then update #4 to "game is LIVE — only x402 crypto-payments wiring remains (Jordan-gated: needs wallet/funds)."

## What's Genuinely Jordan-Gated vs Not
When triaging a "needs Jordan" deploy note, separate:
- **Actually shippable by me** (static HTML/JS, no build step, no funds) → deploy it, don't defer.
- **Genuinely gated** (needs real wallet/funds for crypto-payments, MetaMask signature, private keys) → leave Jordan-gated and say why.

## Pitfalls
- **HTTP 200 ≠ deployed.** SPA fallback returns 200 for missing paths. Always grep for actual content.
- **The site root can BE the product.** Don't assume a `/cabinet/<name>/` subdir exists just because other cabs use that convention.
- **Stale notes are common** — a "deploy" done in a prior session leaves the note untouched. Verify, don't trust.
- **`shipped` status can be stale/mislabeled, not just notes (Aug 10, 2026).** After a merge-conflict resolution or overnight maintenance, items can carry `status: "shipped"` that doesn't match reality — the conflict resolution kept `[SHIPPED by labs]` annotations even for items that were NOT actually done. **Red flag: a `shipped` item with `needs_jordan: true` is almost always mislabeled** — a genuinely shipped item doesn't need Jordan. Before running the build list, audit every `shipped` item's `note` for "REMAINING", "needs Jordan to submit/register", or a pending deadline; correct to `pending`/`in_progress`/`cancelled` (missed deadlines → `cancelled`). Real example (Aug 10): 8 items wrongly `shipped` — KeeperHub (proof tx live but demo video + form pending → `in_progress`), DataHub + Arc (deadlines passed, unsubmitted → `cancelled`), BOT Chain/Telegraph/Gemini/Krexa (need Jordan registration → `pending`). A clean queue is honest: it won't skip live hackathons as "done" and won't waste time on missed ones.
