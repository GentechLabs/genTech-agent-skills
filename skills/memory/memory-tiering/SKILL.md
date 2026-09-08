---
name: memory-tiering
description: "When saving/pruning memory, tier facts by relevance."
version: 1.0.0
author: Gentech
tags: [memory, context, tiering, agentic-behavior, fleet]
---

# Memory Tiering — Intelligence for Intelligence

Jordan's model (Aug 20, 2026): an agent's always-loaded memory (MEMORY.md / USER.md)
should NOT be a dump. It should be a **curated index** of the facts we touch every
session, with everything else parked in the vault brain where it's one search away.

Two tiers:
- **Always-loaded** (MEMORY.md / USER.md) — facts referenced EVERY session. Identity,
  rails, wallet, rules, standing strategy. Lean, high-signal.
- **Vault brain** (retrievable) — facts referenced less often, or RESOLVED. Not lost,
  just parked. Pull back via session_search / search_files when the topic resurfaces.

## Why (the intelligence part)
- Every session reads the memory file. Bloat = slower, more tokens, worse focus.
- **More memory = worse performance** (proven Jul 28, 2026: elaborate memory stack
  deleted → agent worked dramatically better).
- Trimming from the BACK (oldest-first) is dumb — an old high-frequency fact gets
  archived while a recent resolved worry stays loaded. Tier by **relevance**, not age.

## Tiering rules — what stays ALWAYS-LOADED vs ARCHIVES

### ALWAYS-LOADED (keep in MEMORY.md/USER.md)
- **Identity**: who the agent is, personality, speech, the boss (never call Jordan
  terms of endearment — only Vanito).
- **Core rails/keys**: payment rails, wallets, canonical repos, the strategy that
  shapes every decision.
- **Standing rules/red lines**: "never fake receipts," "spend less," "blockers flag
  immediately," "build first talk later."
- **Recurring topics** (per Jordan Aug 20): agentic treasury, x402, AWS, APIs — these
  come up every session, keep them.
- **Active commitments with near deadlines.**

### ARCHIVES TO VAULT BRAIN (low-frequency / resolved)
- **Resolved worries**: "termination risk cleared", "sweep was intentional", "bug
  fixed". Once resolved, compress to a one-liner or archive entirely.
- **One-off events**: a single hackathon that's done, a single hire, a single date.
- **Task progress / session logs**: these go to the brain (09-Green Room / 11-Mess
  Hall / handoffs), NOT persistent memory.
- **Any fact not touched in many sessions** and not needed for the standing model.

## How to apply (standing agentic behavior — do this EVERY save)
1. Before adding a NEW memory entry, ask: "will this be needed EVERY session, or
   only when this topic comes up?" If only-on-topic → save to the Vault instead.
2. When a fact is RESOLVED (problem solved, deadline passed, task done): compress it
   to a one-liner or archive it — don't keep the full narrative loaded.
3. When at the 85% threshold: consolidate in ONE atomic batch (remove stale + add
   new) instead of cramming.
4. The fleet dietician (memory-dietician.py) uses the same relevance tiering, not
   back-of-file trimming, so low-frequency facts archive and high-frequency stay.
5. When a topic resurfaces, pull the archived entry back from the vault
   (search_files / session_search) and re-load it if it's now a standing fact.

## Verification
- MEMORY.md / USER.md stay well under cap with only high-signal facts.
- Resolved worries are compressed or archived, not carried forward.
- No durable fact is ever lost — it's in the vault brain, retrievable.

## Pitfalls
- Don't archive on a whim — if it's referenced across sessions, keep it.
- Don't keep resolved worries loaded "just in case" — archive them; the vault has room.
- The brain (vault) has room — that's its purpose. Overflow belongs there, not in the
  always-loaded memory file.
- This is a STANDING behavior, not a one-time cleanup. Apply it on every save.
