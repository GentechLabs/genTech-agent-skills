# Vault Routing File — "write → index → route → open two files"

**Borrowed from:** kocer_eth (Aug 15, 2026) — "STOP TREATING YOUR OBSIDIAN VAULT AS AI MEMORY."
**Mechanism:** a one-line-per-folder routing index, kept current, loaded BEFORE any retrieval
call — so the agent knows *which folder to open* without scanning the whole vault.

## The problem it solves
A folder full of markdown does not make the agent smart. What makes it smart is what the
agent can find WITHOUT rereading the whole vault. Without a routing file, the agent scans
everything, hallucinates half of it, and forgets by the next session.

- **Storage (bad):** write → tag → graph → agent scans everything
- **Memory (good):** write → index → route → agent opens two files

## What we shipped (Aug 15, 2026)
- **`${VAULT_DIR}/ROUTING.md`** — one line per top-level folder, grouped
  (Core Ops / Finance / Gaming / People / Generated), plus a quick-routing table.
- **`${PROFILE_DIR}/scripts/routing-watcher.py`** — scans top-level
  folders, flags any not yet in ROUTING.md. Silent (exit 0, no output) when all routed.
- **Cron `routing-watcher`** (daily 6:00 UTC) — runs in **monitor mode** so it burns zero
  tokens on no-change days; only fires an agent run when a new folder appears.

## The "kept current" half (critical)
A routing file that rots is worse than none. The watcher closes the loop:
new folder → watcher flags it → agent adds one line → ROUTING.md stays current.

## Wiring into wake-up
`wake-up-protocol` Step 1b loads ROUTING.md BEFORE any retrieval. Route before you scan.

## Pitfalls (learned building the watcher)
- **Regex over table rows false-matches.** Matching `` `folder/` `` with a loose regex
  matched across table rows and paths. Fix: iterate the actual top-level dirs and check
  `f"`{d}/`" in routing_text` (exact backtick-wrapped token).
- **Define `top_dirs` before the `mentioned` loop** — referencing it before definition
  is a NameError.
- **Monitor-mode cron** is the right pattern for a "flag when something changes" job:
  stable output (no timestamps) → hash-suppressed → silent on no-change ticks.

## Related
- `vault-first-research` — vault retrieval efficiency umbrella.
- `gentech-context-management` — vault organization umbrella.
