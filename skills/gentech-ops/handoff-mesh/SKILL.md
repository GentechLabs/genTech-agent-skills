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
- **A handoff written but never woken is a handoff nobody reads.** Writing the
  INBOX note and then running out of turns before the `peer dm` leaves the note
  sitting until the watcher's next cycle — and the watcher only *surfaces* it, it
  does not wake anyone. **Send the wake in the same call as the write**, or at the
  top of the next run before anything else. When you pick up a run and find a
  handoff you (or a prior run) wrote with no return note, check whether the wake
  actually went out — a missing wake is indistinguishable from a stalled agent.

## Pitfalls — delivery confirmation (learned the hard way)
- **`hermes peer dm <peer> "..."` prints the reply and exits 0 — silence is NOT proof of
  delivery.** A queued turn, a mid-turn target, or a run that produced no output all look
  identical to success: exit 0, no text. Never report "DM sent" on that alone.
- **Verify with the async path when output is empty** — it returns a run id and a terminal
  status you can read back:
  ```bash
  hermes peer run <peer> "reply with just ACK"   # -> run_<hex>
  hermes peer status <peer> run_<hex> --json     # -> {"status":"completed","output":"ACK"}
  ```
  `status: completed` + a non-empty `output` is a verified round-trip. A target that is
  `running` is mid-turn: your DM is queued behind its current work, which is fine — just
  don't claim it landed until you see it.
- **Check the peer's health first** (`curl -s -o /dev/null -w '%{http_code}' http://<tailnet-ip>:<port>/health`).
  200 means the lane is up; it does NOT mean your specific message was read.
- **A DM is never the record.** If it matters, it also goes to the vault lane. A silent DM
  plus no vault note means the handoff exists nowhere.

## Pitfalls — a hash-bound closure that your own tooling rewrites

**Never hash raw bytes of a file your own tooling appends to.** A watcher that writes a dedup
marker into the handoff it just read changes the bytes, so a `source_sha256` binding stops matching
and the closure **reopens on itself** — every pass. Reproduced live: close → CLOSED → append
`<!-- PEER_SEEN -->` → **REOPENED**.

**Why it hides:** the mechanism works exactly as designed. The design is what's wrong — it cannot
distinguish the author's edit from its own bookkeeping.

**Two separate halves, check both:**
1. **The writer** — does any watcher `open(path, "a")` on a handoff? Keep scaffolding OUT of the
text the sender authored, or move it to a sidecar (e.g. a `.seen` index). One file per receiver
avoids a multi-writer race.
2. **The checker** — even a seat that never appends is exposed, because a *peer's* watcher appends
into shared files. Any raw-byte hash is vulnerable.

**Fix — normalise before hashing, in this order:** strip `<!-- …SEEN…/…DEDUP… -->` scaffolding
comments, `CRLF → LF`, **then collapse trailing whitespace**. Marker-stripping alone is NOT
sufficient: each append also adds blank lines, which accumulate. And **keep a legacy-digest
fallback** (`(md, legacy-hash)`) so records written before the fix don't mass-reopen.

**Test battery — the third test is the one that matters:**
```
3 consecutive appends  -> stays CLOSED        (stability)
a second marker type   -> stays CLOSED        (type-agnostic)
REAL sender edit       -> REOPENS             (detection still works!)
legacy record          -> CLOSED (legacy-hash) (back-compat)
```
A binding that ignores *all* change is worse than one that over-fires: it would silently accept a
genuinely edited handoff. Always verify the mechanism still detects what it exists to detect.

## Pitfalls — a closure trigger that reads only prose

**A marker-based trigger cannot close a handoff that has no marker to read.** If the trigger parses
`Status:` lines and `RESOLVED_WORDS` from the note text, then every handoff written *without* a
Status line re-alerts forever — even when a valid closure record exists. Measured: **22 of 46**
outbound handoffs were written with no Status line, and two of them re-alerted repeatedly while the
receiver's own lane showed `0 open`.

**Fix — consult the closure RECORD first, prose second:**
```
closed is True   -> resolved      (record exists, hash matches)
closed is False  -> OPEN          (REOPENED: source changed since closure -- this WINS)
closed is None   -> fall through  (no record/unverifiable -> legacy prose parsing)
```

**The `False` direction is the dangerous one.** Treating a REOPENED record as "fall through to
prose" lets stale prose override a fail-closed reopening: a note that still says "ANSWERED" but
whose source was edited afterwards is genuinely open again. This was caught live — one file was
being reported resolved while its record said REOPENED.

**Corollary:** adding a `Status:` line to a handoff binds it to a *new* revision, which correctly
REOPENS any existing closure for it — re-close after editing. Editing a file you authored to make a
peer's trigger happy is a workaround; making the trigger read records is the fix.

## Pitfalls — normalisation must be a shared, versioned contract

**Two seats normalising "the same" content differently cannot validate each other's hashes.**
Measured: a peer's closure record claimed a `source_sha256` that **neither** my normalised hash
**nor** my raw-bytes hash reproduced — and the peer's own checker did not reproduce its own record
either. Each seat could validate only its own closures, which defeats the point of cross-seat
verification.

**Rules:**
- Write the normalisation down as a **spec with a version**, not as whatever each implementation
  happens to do.
- **Pin every choice, not just the steps.** A spec saying "strip markers, CRLF→LF, rstrip" was
  implemented twice and the two versions disagreed — three rules, each with a plausible alternate
  reading: marker → one `\n` vs deleted entirely; rstrip document-END vs EVERY LINE; append exactly
  one `\n` vs none. Measured divergence on one real file: **31 bytes**. A seat coding from that prose
  has ~1-in-8 odds of matching (2³ variants). Enumerate the choices in a table with the canonical
  answer and the tempting wrong reading.
**Verify by BYTE-COMPARISON, never by reading the rules.** Ship a **conformance harness with golden
vectors** and run it against any checker before trusting its digests:

```bash
python verify-hash-normalisation.py path/to/handoff_closure.py
# expect: CONFORMANT — all 9 vectors match byte-for-byte.
```

**Prove the suite can FAIL before trusting it to pass.** A suite that has never failed might not run.
Build each divergent variant and confirm it is caught, with the failing case named:
```
delete-marker-instead-of-newline  -> 1/9 divergent (marker_midfile)
rstrip-every-line                 -> 1/9 divergent (trailing_spaces)
omit-final-newline                -> 9/9 divergent
```

**Know which choices are actually observable** — it tells you which bugs survive review. Measured
over 61 real files: final-newline **61/61**, marker-substitution **55/61**, trailing-whitespace scope
**1/61**. The last one passes almost every real file, so it is the one that ships broken.

**The digest detects SEMANTIC edits, not byte-exactness.** Nine vectors produce only four distinct
digests — six different inputs collapse to one (plain / no-final-newline / CRLF / one-marker /
three-markers / other-marker-type). That insensitivity is intended for closure-binding, but it means
`source_sha256` must **never** be repurposed as a byte-integrity or tamper check; it cannot be one.

**Re-verify by byte-comparison, never by reading the rules.** Two functions can satisfy the same
English description and produce different bytes.
- **Record which normalisation produced a hash** in the closure record, so a mismatch is diagnosable
  instead of mysterious.
- **Never report a norm mismatch as REOPENED.** The digests are incomparable; call it UNVERIFIABLE.
  Reporting it as an edit **accuses a peer of changing a file they never touched** — which happened
  in both directions in practice.
- **Publish to the SYNCED copy as part of the change, not after a peer reports a mismatch.** A fix
  made only in a seat's local scripts dir (which does not sync) leaves the peer running old rules
  while the writer believes it's solved. *A fix the consumer cannot see is not a fix.*
- When a peer's hash doesn't reproduce, try in this order: their checker's output, your normalised
  hash, your raw hash, then earlier revisions — then report it as an incompatibility rather than
  silently re-verifying with your own method.

## Verification
- [ ] Every agent/group has an `INBOX/<group>/` folder + `_archive/`.
- [ ] Watcher surfaces open handoffs hourly (silent when clear).
- [ ] Agent that reads a handoff reports back what it did.
- [ ] Resolved notes archived; `_archive/` purged weekly.
- [ ] No handoff left unread or unreported at a stopping point.

## PITFALL: `hermes peer dm` is SYNCHRONOUS — it waits for the remote agent's whole turn

`hermes peer dm <peer> "<msg>"` delivers the message **and prints the reply**, which means the command
does not return until the remote agent has finished its entire turn. On a long handoff this blocks for
minutes and can hit any shell timeout (observed: a 400s timeout on a Forge handoff).

**A timeout does NOT mean the message failed to send.** The message was delivered; the sender gave up
waiting. Do not re-send blindly — that double-delivers.

- **Long handoff / wake → `hermes peer run <peer> "<msg>"`** — starts the turn asynchronously and returns a
  run ID. Read the result with `hermes peer status <id>`; stop it with `hermes peer stop <id>`.
- **Short question you need an answer to now → `peer dm`** is correct.
- **Always write the vault handoff too.** The vault is the source of truth and survives a machine being
  off; the DM only wakes. "DM to wake, vault to record."

**A hang is a diagnostic, not just a nuisance.** If `peer dm` hangs past a normal turn, suspect the remote
agent's own provider — a remote seat on a rate-limited or dead provider (e.g. ollama-cloud 429) will stall
exactly like this. Check the peer's provider before assuming the mesh is broken.
