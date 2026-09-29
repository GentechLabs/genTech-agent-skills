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
- **Answering a note is NOT closing it — the closure record must live in the INBOUND note.**
  If your reply goes into your own outbound lane, the inbound note still reads as open to
  every automated watcher, and the same message gets re-delivered. Observed: the same sync
  report arrived three times because the inbound note carried no resolved marker and the
  replies were filed separately. **Append a machine-readable closure record to the inbound
  note itself** (bottom of the file), using the vocabulary `handoff-watcher.py`
  `RESOLVED_MARKERS` actually matches: `status: answered`, `status: closed`, `status: [x]`,
  `answered`, `filed`, `nothing owed`, `no further action`.

  ```markdown
  ---

  ## STATUS: ANSWERED — closure record (machine-readable)

  **Answering seat:** <seat>   **Closed:** <UTC ts>   **State:** CLOSED — nothing owed
  <one short block per item: what was verified, with the evidence>
  **Outbound handoffs filed:** <paths>
  **One item left OPEN, not owed:** <if any>
  **Nothing owed. No further action required on this note.**
  ```

  **Prove it cleared; do not infer from silence.** Run `python3 scripts/handoff-watcher.py`
  and confirm it goes quiet for that lane — and check the PRE-closure text contained no
  marker, so you know the marker changed the verdict rather than an unrelated fix.
- **EDIT CORE, NEVER THE SEAT — a `skill_manage` patch lands on the SEAT copy and the next
  sync destroys it.** Learned by doing it: patched the seat copy, ran `fleet_skills_sync.py`,
  and the edit was rolled back while the sync printed *"replacing the seat copy destroys 1
  file(s) present only in the seat"* — which I read past. **That warning is the signal, not
  noise.** Either edit the CORE file directly
  (`10-Labs/skills-distribution/<cat>/<skill>/SKILL.md`) then sync CORE -> seats, or promote
  the seat copy into CORE first. A seat copy is a build artifact.
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
- **A message with shell metacharacters must go in via STDIN, not as an inline argument.** Passing
  prose with backticks, `|`, `()`, `<>`, `$` or `—` inline makes the SHELL die before `hermes peer dm`
  ever runs: `bash: syntax error near unexpected token ')'`. The failure looks like a delivery problem
  and is not — nothing was sent. Write the message to a file and pipe it:
  ```bash
  hermes peer dm --json <peer> < /tmp/msg.txt > /tmp/dm.json 2>&1
  ```
  Omit the positional argument and the message is read from **stdin**; no escaping needed. Confirm
  success by parsing the JSON reply, not by the exit code:
  `python3 -c "import json;print(json.load(open('/tmp/dm.json')).get('reply'))"`.
  **Also: `--json` must precede the target** (`peer dm --json gentech`, not `peer dm gentech --json`) —
  reversed, argparse reads the message as an unknown argument and refuses.
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
- **`hermes peer dm` BLOCKS until the remote agent replies — so a mid-turn target shows as exit
  `124` (timeout), not as exit 0.** This is a third failure signature: exit 124 means the message was
  very likely delivered and the target is simply busy generating a reply — NOT that the lane is
  dead. Do not retry it in a loop or conclude the peer is down. **For a heads-up you don't need a
  reply to, use `hermes peer run` from the start** — it returns a run id immediately and never
  blocks a tool call:
  ```bash
  hermes peer run <peer> "..."        # -> run_<hex>: started   (returns in ~1s)
  hermes peer status <peer> run_<hex> # -> running | completed
  ```
  ⚠️ **Also: `cmd | tail -5; echo "exit=$?"` reports TAIL's exit code, not the command's.** A piped
  `peer dm` threw away a real `124` this way and looked like `exit=0` — a false pass of exactly the
  kind this section exists to prevent. Capture with `out=$(cmd); rc=$?` or set `set -o pipefail`.
- **Check the peer's health first** (`curl -s -o /dev/null -w '%{http_code}' http://<tailnet-ip>:<port>/health`).
  200 means the lane is up; it does NOT mean your specific message was read.
- **A generated message that reports age/state must carry its own measurement time, or stale
  and live become indistinguishable.** The handoff watcher nudges with lines like
  `open 10h, no return` computed at the moment the sweep runs, but the message is delivered
  (or replayed) later. Without an `AS OF HH:MMZ` stamp and a stale-warning, the receiver has
  no way to know whether the nudge is current or an old sweep that simply arrived late — and
  will treat a stale nag as a fresh finding. Always timestamp measurement-derived claims in the
  message body itself; don't rely on channel metadata or assume the receiver will check the
  state file. See `references/measurement-time-in-generated-messages.md`.
- **A DM is never the record.** If it matters, it also goes to the vault lane. A silent DM
  plus no vault note means the handoff exists nowhere.
- **Do NOT report a handoff as undelivered because Obsidian Sync failed — on this box, git IS the
  delivery.** All four VPS seats read the SAME path on the SAME filesystem
  (`VAULT = "/root/vaults/gentech"`, verified by inode + device + md5, not by assumption), so a
  `git commit` is immediately legible to every seat with **no `ob sync` step involved**. Obsidian Sync
  is what carries the vault **OFF the box**: Forge (desktop) and Jordan's Obsidian clients.

  | receiver | delivered by | does `git push` alone reach them? |
  |---|---|---|
  | the four VPS seats | the shared filesystem | ✅ yes — immediately |
  | Forge (desktop, separate machine) | Obsidian Sync / its own clone | ❌ no |
  | humans (Jordan's Obsidian) | Obsidian Sync | ❌ no |

  **Never report a quota error as a fleet-wide communication stop.** The opposite belief makes agents
  re-send work the reader already has, or declare a handoff undelivered while its bytes are sitting on
  the reader's disk — and it turns an off-box transport problem into a false fleet-wide outage.
  Measured 2026-09-28 after `vault-handoff-lifecycle` and a seat copy of `agent-coordination` were both
  found teaching the false wording. State your transport consequence in terms of **which receiver**.
  Full detail: `00-System/vault-transport-protocol.md` (git-tracked, so every seat can read it).

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

**Read the RECORD before the MARKER — and never let prose outrank it.** The closure verdict is a
tri-state and the order you consult it in is load-bearing:

```
closed is True  -> resolved      (record exists, hash matches)
closed is False -> OPEN          (REOPENED: source changed since closure -- THIS WINS over any marker)
closed is None  -> fall through  (no record / unverifiable -> legacy prose parsing)
```

The watcher's `is_resolved()` did the opposite — `if _marker_hit(text): return True` returned
*before* the record was read — so on any note carrying a marker word the fail-closed reopen was
**inert**. Measured: close a note, reopen or edit it so the record goes stale; `is_closed()` returns
`(False, 'REOPENED…')` and `_closure_says_closed()` returns `False`, yet `is_resolved()` returned
`True` because the marker matched first. A reopened handoff read RESOLVED by the only thing that acts
on it. The `False` direction is the dangerous one and it was exactly the direction the ordering got
wrong — stale prose overriding a reopen. Fix: record first, marker second, with the tri-state `None`
fall-through preserved so no note with an unusable record changes behaviour (strict superset).

**To reverse a closure, `reopen` it — never delete the record.** `handoff_closure.py close|check|audit`
had no reopen, so the only way to reverse one was to **delete the record file**: evidence destroyed,
reason unrecorded, indistinguishable from tidying up — the exact unreceipted action the tool exists to
eliminate. Use `reopen <handoff> --by <agent> --reason "<why>"`; it rewrites the record **in place**
(`state: open`, `reopened_by`, `reopened_at`, `reopen_reason`), deletes nothing, and refuses without a
reason. It is deliberately **not** a bypass of the stale-hash path — `is_closed()` already reopens a
source-edited handoff automatically. It covers the other case: the **source is unchanged** and the
closure was simply wrong (a missed live ask, a premature close). There the hash still matches, nothing
detects it, and before `reopen` existed the only signal was a deletion.


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
minutes.

**NEVER wrap `hermes peer dm` in your own shell timeout** (`timeout 420 hermes peer dm ...`). The tool
already carries its own deadline — `DM_TIMEOUT_S = 600` in `hermes_cli/subcommands/peer.py` — and it
**prints the correct interpretation itself** when that deadline hits:

> `accepted the message but its turn is still running after 600s: the message is already in its Bot
> Chat (session …) and will be answered there. The reply cannot come back on this call. Do NOT resend.`

Wrap it anyway and you kill it before its own handling runs, then read **exit 124** and conclude the
transport hung. You measured **your** deadline and reported it as the peer's. This exact error was made
by two agents independently (both concluded "genuine hang, not a slow wait" from a self-imposed
`timeout 420` / `400s`) and circulated as fact in handoffs for a week — correcting a *one-sided
measurement* with a one-sided measurement. Before blaming the transport, check whether you set the limit.

**A timeout does NOT mean the message failed to send.** The message was delivered; the sender gave up
waiting. Do not re-send blindly — that double-delivers.

**The accurate model (four outcomes, not two):**

| observed | meaning |
|---|---|
| exit 0 **with** reply text | round-trip complete — done |
| exit 0, **no** text | queued / mid-turn / silenced — verify with `peer run` + `peer status`; never report "sent" on this alone |
| **exit 124** (or the 600s message) | **DELIVERED** and the peer is still working — do NOT resend |
| `peer run` run_id itself timing out | deep remote queue, not a dead lane |

- **Long handoff / wake → `hermes peer run <peer> "<msg>"`** — starts the turn asynchronously and returns a
  run ID. Read the result with `hermes peer status <id>`; stop it with `hermes peer stop <id>`.
- **Short question you need an answer to now → `peer dm`** is correct.
- **Always write the vault handoff too.** The vault is the source of truth and survives a machine being
  off; the DM only wakes. "DM to wake, vault to record."

**A hang is a diagnostic, not just a nuisance.** If `peer dm` hangs past a normal turn, suspect the remote
agent's own provider — a remote seat on a rate-limited or dead provider (e.g. ollama-cloud 429) will stall
exactly like this. Check the peer's provider before assuming the mesh is broken.

## ⚠️ A return note in the WRONG LANE NAME is invisible — check WHERE you wrote, not your diligence

**If a handoff keeps re-nudging after you answered it completely, test the watcher's matcher before
doubting your own work.** The return lane is resolved by literal interpolation —
`_reverse_lane(sender, receiver) -> "{receiver}-to-{sender}"`. When a seat has an **alias list**
(`SEAT_LANES`, e.g. `"gentech-treasury": ["treasury","strategies","gentech-treasury"]`) the watcher
KNOWS those are one seat's lanes, but `_reverse_lane()` picks a **single literal** with no alias
resolution — so every other name is invisible to return-detection.

Measured for the treasury seat; identical notes flip the verdict by location alone:

| Where the note is | `_has_return_note` |
|---|---|
| `01-HANDOFFS/treasury-to-gentech/` (group-name form) | **False** |
| `01-HANDOFFS/gentech-treasury-to-gentech/` (seat-name form) | **True** |

The inbound lane uses the **seat-name** form (`gentech-to-gentech-treasury`), so the reply must too.
Assert it with the matcher itself rather than assuming:

```python
spec = importlib.util.spec_from_file_location('hw', '<profile>/scripts/handoff-watcher.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m._has_return_note('01-HANDOFFS/gentech-to-gentech-treasury/<inbound>.md', '<sender>', '<receiver>')
```

**Two more blind spots in the same function:**
- It scans only the lane **top level** — the nightly archiver moves notes into `_archive/`, so an
  answered-but-archived return loses its evidence a second way.
- It matches the inbound **topic slug** in the filename or body — a note named only by date answers
  nothing. Keep the topic slug in the return filename.

**Consequence: a complete answer reads as "no return" forever and re-nudges every cooldown**,
manufacturing the exact impression the watcher exists to prevent ("this seat went silent"). Do not
read a repeated nudge as a peer ignoring you, and never file the same answer a third time — find
which of these three the watcher can see and satisfy it.

## ⚠️ Use the fleet's OWN comparator — a hand-rolled dir scan INVENTS drift

**Scanning skill dirs with your own hash of `md5sum` output that includes file PATHS produces false
DIFFERS**, because CORE and a profile live at different absolute paths by design. Measured: a
hand-rolled digest reported **4 spurious drift hits** on skills that were in fact identical;
content-only digests then agreed everywhere. The false alarm looks exactly like the real drift you
are hunting, so it costs a full round to disprove.

Use the fleet's own tool — `00-System/agent-profiles/fleet_skills_sync.py --check` — whose
`dir_digest()` is content-based and compares the **whole dir**, not just `SKILL.md`. It prints its
own denominator (**150 skills**); a depth-2 enumeration undercounts at 127 (d1=21, d2=127, d3=2).

**Two blind spots to hold together, both real, both seen on the same day:**
- **Depth:** a `SKILL.md`-level compare reads clean while a `references/` file differs (7964 B in
  CORE vs 10844 B on a seat). Zero drift at file level, real drift at dir level.
- **Lane coverage:** a return-lane scan that reads one lane NAME reads clean while returns sit in
  another. Zero drift at one scope, complete miss at another.

**Pin a hash to its commit** (`<md5> @ <sha>`). A bare hash is indistinguishable from a stale or
wrong one: a file that legitimately changed between your measurement and your reader's
(11:59 `ba46b55c9` → 12:08 `91e84fee4`) makes a correct report look like an error. **Never revert
on a hash mismatch before checking which commit moved it.**

**And update CORE, never the seat alone.** Editing a seat's own `SKILL.md` creates the exact drift
the sync exists to remove — one edit produced a 44-line seat-only divergence that the next
`--check` would have flagged as real. Write to `10-Labs/skills-distribution/`, then sync out.

## ⚠️ The `INBOX/<seat>/` layout is READABLE by the watcher but NOT closable by the closure tool

Found 2026-09-28 while answering a fleet notice. `handoff-watcher.py` **does** scan
`01-HANDOFFS/INBOX/<group>/` (`find_open()` walks `INBOX` by group), but
`handoff_closure.py close` **cannot close a note there**:

```
ValueError: cannot derive a return lane from
  '01-HANDOFFS/INBOX/gentech-treasury/2026-09-28-FLEET-ob-sync-github-dm.md'
  (expected <sender>-to-<receiver>/<file>.md)
```

`_lane_parts()` only understands `<sender>-to-<receiver>/<file>.md`. So a note in the new
inbox layout **nags forever and cannot be recorded closed** — the layout is half-wired.
36 INBOX notes existed fleet-wide when measured.

**What to do instead — use the INBOX's own convention** (`01-HANDOFFS/INBOX/README.md`,
step 4: *"tick the checkbox and move the file to `_archive/`"*):

1. Append a resolution block to the note itself, headed with a word the watcher reads
   (`Status: answered`, `answered`, `filed`, `nothing owed`, `no further action`) and naming
   your return file by its full path.
2. `mv` it into that inbox's `_archive/`.
3. Commit — **including the move**, and check whether the note was ever tracked at all.
   A note whose sender could not push is untracked, so `git mv` fails with
   *"not under version control"*; use plain `mv` + `git add -A` on the inbox dir.

**Do not point a closure record at your own reply.** Closing your outbound reply with
`handoff_closure.py` writes a record into `<sender>-to-gentech-treasury/_closed/`, i.e. it
treats your reply as a handoff *received by you*. That is a false record — delete it.
**A closure record is for an inbound note; a reply is recorded by the note it answers.**

### A name is a claim — validate the value satisfies it
A field called `seconds` that was produced by `timestamp[:23]` on a `YYYY-MM-DD HH:MM:SS,mmm` log line **retains the
milliseconds**, so every "second" was a distinct-millisecond value. It read LOWER than the line count, which made it
look like the tighter estimator, while being structurally looser. **Before trusting a derived field, check that the
value can actually satisfy its name** (here: 19 characters, not 23). A truncation that keeps a decimal separator
looks exactly like a precise measurement.
## Closing an INBOX note needs the HEADER MARKER, not a closure record

`handoff_closure.py` has ZERO INBOX awareness: `closure_path()` returns `None` for
`01-HANDOFFS/INBOX/<seat>/...` because the lane regex `^(.+)-to-(.+)$` finds no sender/receiver in a
folder named just `treasury` — so the tool reports "no return lane derivable from path" and writes
nothing. That is a real limitation, NOT a dead end.

**Measured:** appending a prose closure block to an INBOX note left the watcher's `is_resolved()`
returning **False** — the note kept nagging while reading, to a human, as closed. Changing the header
from `**Status:** open` to **`**Status:** resolved`** flipped it to **True**.

So: to close an INBOX note, change its header to a marker the resolver reads
(`status: resolved` / `status: done` / `status: closed` / `## resolved` / `- [x]`). Verify with the
resolver itself rather than by eye:

```python
import importlib.util, sys
spec = importlib.util.spec_from_file_location("hw", "<...>/handoff-watcher.py")
hw = importlib.util.module_from_spec(spec); sys.argv=["hw"]
try: spec.loader.exec_module(hw)
except SystemExit: pass
print(hw.is_resolved("<note path>"))     # True = the nag is cleared
```

And a file COUNT of the INBOX folder is not a count of unresolved notes — resolved notes stay on
disk. Count with the resolver, or you will report an open item that is already closed.

