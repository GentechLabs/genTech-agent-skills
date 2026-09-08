---
name: handoff-mesh
description: "Use when agents hand work to each other. Full-mesh inboxes."
version: 1.0.0
author: Gentech
tags: [handoff, coordination, multi-agent, mesh, inbox, communication, vault]
license: MIT
---

# Handoff Mesh — Communication Layer for Multi-Agent Setups

## When to Use
- You run **more than one agent** (multi-agent strategy) and they need to hand work to each other.
- An agent finishes something and another agent (or a human) needs to pick it up.
- You want a **durable, searchable** coordination layer — not just real-time chat.
- You want to know, at a glance, what handoffs are open and whether they got done.

## What This Is
A **full-mesh handoff system** built on the vault (Obsidian) — the durable brain.
Any agent can drop a handoff into any other agent's inbox. A watcher surfaces
open handoffs hourly. Nightly maintenance archives old ones. And a
completion-reporting loop closes the deal: the agent that reads a handoff
reports back what it did before it's marked resolved.

This is the **storage + verification** half of agent communication. Real-time
channels (Buzz, Telegram) are the *talking* half; this is the *remembering and
proving* half. They complement each other — the vault stays the source of truth.

## The Layout
```
01-HANDOFFS/
    INBOX/
        <group>/                    ← one receive folder per agent/group
            <YYYY-MM-DD>-<topic>.md ← a handoff note for that agent
            _archive/               ← resolved notes (auto-moved, purged weekly)
    <from>-to-<to>/                 ← optional explicit sender→receiver folders
```

## The Protocol (4 steps — the loop)

### Step 1 — SEND: drop a handoff into the target's inbox
Write `<date>-<topic>.md` into the target group's `INBOX/<group>/` folder.
**Any agent can initiate a handoff to any peer** (Forge, Labs, Treasury,
Entertainment, HQ) — not just respond to one. The wake trigger now teaches the
send side: write the dated note into `INBOX/<target>/` with `**From:** <you>`,
`**To:** <target>`, `**Status:** open`, and a `## What's needed` section, then
commit + push. Never hand off to a peer without writing the note to their INBOX
folder — the watcher and the target's wake trigger surface it from there.
Format:
```markdown
# <topic>
**From:** <agent/group>
**To:** <group>
**Date:** <YYYY-MM-DD>
**Status:** open

## What's needed
<what the receiving agent should do>

## Context / files
<any links or paths>
```
Commit + push (or `ob sync`).

### Step 2 — WATCH: surface open handoffs automatically
Run the watcher hourly (or on each agent's wake-up). It scans every inbox lane
and reports any note still `Status: open` (not resolved, not archived).
```bash
python3 handoff-watcher.py [vault_path]
```
- **Silent when clear** — only pings when there's actually something to do.
- **Quiet overnight** — schedule it for waking hours only (e.g. 7 AM–11 PM ET).
- Wire it as a `no_agent` cron (pure script, zero tokens) so it's cheap.

### Step 3 — ACT + REPORT: the agent that reads it reports back
This is the half that makes handoffs *verified*, not just *seen*:
1. **Read** the handoff → acknowledge it in the group (never silent).
2. **Act** on it.
3. **Report back — the default return format.** When you finish, write a dated
   note to the **original sender's** return lane (`<sender>-to-<group>/`) with
   THREE sections, always:
   - **`## ✅ What was done`** — the concrete deliverable/results
   - **`## 📌 What you should know`** — blockers, wallet-control checks, caveats,
     anything that changes the picture for the receiver
   - **`## ⏭️ What's next`** — the next step, even if it's on the other agent/human
   A return note with these three sections is the default. If any is empty,
   write "None" — the structure stays. This is what lets Jordan (and any
   original sender) see the full hand-back at a glance.
4. **Mark resolved + archive** only AFTER the work is verified.

### Step 4 — CLEAN: archive weekly so it never gets too big
Nightly/weekly maintenance:
- Move resolved notes to `_archive/`.
- **Purge `_archive/` entries older than 7 days.**
- Auto-archive stale OPEN notes older than 7 days (still unresolved).

## The Watcher Script
`handoff-watcher.py` (stdlib-only, stable output — safe as a `monitor_script`):
- Lists every `<group>/` subfolder under `INBOX/`.
- Finds `*.md` notes NOT in `_archive/` and NOT marked resolved.
- Emits a short, stable report of OPEN handoffs (or nothing if all clear).

## Lifecycle states (so Jordan sees work in progress)
A handoff can carry three statuses the watcher surfaces:
- `Status: open` — just dropped, not picked up yet → watcher lists under NEW.
- `Status: in progress` (or `in route`, `picked up`, `working`, `active`,
  `awaiting review`) — an agent has ACKed and started it → watcher lists it
  under 🚧 IN PROGRESS grouped by routing direction (e.g. `gentech → labs`).
  Set this as soon as you pick up a handoff so the routing context is visible.
- `Status: resolved` / `[x]` — done + verified → watcher lists it under CLEARED.
ACK + START + REPORT is mandatory: when you pick up a handoff, (1) mark it
`Status: in progress` in a dated `<you>-to-gentech/` return note and push,
(2) start immediately, (3) report the first progress chunk or first blocker in
the same return lane. Silence after pickup is a defect — Jordan must SEE work
in progress, not wonder if an agent started.

## STALLED watchdog (closes the "is anyone working?" blind spot)
`handoff-watcher.py` also flags **STALLED** handoffs: any outbound handoff
(`gentech-to-<agent>` or `<agent>-to-<other>`) that is open, older than 6h
(by its date prefix — NOT mtime, which git re-touches), and has **no return
note** in the reverse lane. It reports each stalled handoff ONCE, then stays
silent until the agent returns or it's resolved.
- If you see a 🆘 STALLED alert: **wake the agent** (the wake-trigger re-arms
  on their next cycle) or reassign. If the stall is actually waiting on
  Jordan (funding, credentials, login), say so — the watchdog can't tell a
  stalled agent from a waiting-on-human handoff.

## Decision Table
| Situation | Action |
|-----------|--------|
| Agent A finishes work for Agent B | A writes handoff to B's inbox |
| Handoff sits open >1 hour | Watcher surfaces it; B picks it up |
| B reads the handoff | B ACKs (marks `in progress`), acts, reports back |
| B completes the work | B marks resolved + archives, reports what it did |
| Handoff unresolved >7 days | Nightly maintenance auto-archives it |

## Pitfalls
- **Reading without reporting** — a handoff archived as "resolved" with no
  completion note is a silent failure. Always report what you did.
- **No archive cleanup** — inboxes grow unbounded. Purge `_archive/` weekly.
- **Watcher pinging overnight** — schedule it for waking hours only.
- **Only watching your own inbox** — in a mesh, check ALL lanes; any agent can
  hand off to any other.
- **Real-time chat ≠ durable record** — keep the handoff in the vault; chat is
  for talking, the vault is for remembering.

## Verification
- [ ] Every agent/group has an `INBOX/<group>/` folder + `_archive/`.
- [ ] Watcher surfaces open handoffs hourly (silent when clear).
- [ ] Agent that reads a handoff reports back what it did.
- [ ] Resolved notes archived; `_archive/` purged weekly.
- [ ] No handoff left unread or unreported at a stopping point.
