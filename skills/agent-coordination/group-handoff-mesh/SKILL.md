---
name: group-handoff-mesh
description: "Use when moving work between GenTech groups — V4 mesh."
version: 1.0.0
author: Gentech
license: MIT
category: agent-coordination
tags: [handoff, coordination, vault, multi-channel, mesh]
related_skills:
  - agent-coordination
  - routing
  - single-agent-multi-channel
---

# Group Handoff Mesh (V4)

## When to use
Any time work needs to move between GenTech groups (HQ, Labs, Entertainment,
Treasury, Forge, gizmo) — for approval, context, or handoff. This replaced the
old hub-and-spoke model where every group returned only to Gentech.

## The core idea
V4 is a **full mesh**: ANY group can hand off to ANY other group. The mesh adds
peer handoffs on top of Gentech's consolidation role — it does not remove it.
Gentech still consumes ALL returns overnight, so nothing is lost regardless of
who sent it to whom.

## Routing rules
- **Approval/decision** → hand off to `hq` (Jordan's lane) or the group that owns the decision.
- **Context** → hand off to the group that holds it (e.g. a finance decision needing Labs' technical read → `labs-to-treasury/`).
- **Build** → `labs` (or `forge` for desktop-only work).
- **Content/social** → `entertainment`.
- **Finance/portfolio/yield** → `treasury`.

## Folder naming & file contract
- Folder: `01-HANDOFFS/<from>-to-<to>/` with dated `.md` files (e.g. `labs-to-treasury/2026-08-15.md`).
- Shipped item IDs also go in `<from>-completions.md` (e.g. `labs-completions.md`).
- Return note format:
  ```
  ## From <Group> — <date>
  ### ✅ Completed this session
  - #<id> — what was built
  ### ⏸ Blocked / waiting on
  - #<id> — what's blocking
  ### 📝 Notes
  ```

## The overnight scanner
`/root/vaults/gentech/scripts/group-returns-scanner.py` reads EVERY
`<from>-to-<to>/` folder (not just `-to-gentech/`) plus every
`<group>-completions.md`, extracts shipped `#<id>` tokens + notes, and emits
JSON for the Nightly Build Session + Morning Digest. It also auto-creates
missing return folders. Groups list includes `gizmo` (Labs bot).

## Vault source of truth
- `01-HANDOFFS/sync-protocol.md` — the full protocol (read before writing handoffs).
- `01-HANDOFFS/INBOX/README.md` — the delegation board + mesh rules.

## Pitfalls
- **A handoff is closed by its STATUS LINE — never by prose that merely mentions a marker word.**
  Marker scans over the whole file produce false NEGATIVES (a genuinely open note reads resolved — the
  direction that HIDES work). Measured defects, all fixed 2026-09-18: `"unanswered"` contains `answered`;
  `"this was NOT answered"` matched; **markers inside backticks** counted, so a note DOCUMENTING the
  vocabulary or showing a command example closed itself; and prose about a DIFFERENT handoff
  (`"you answered it on Sep 16"`) closed the note doing the describing.
  **Cleanest real case:** auto-generated `forge-tasks.md` files contain the instruction
  ``"update the queue via: `assigned_to: gentech, status: shipped`"`` — backticked, instructional — and
  the substring scan read `status: shipped`, so **the Forge task lists silently resolved themselves and
  were invisible to the watcher.** If you write or review a scanner: scope markers to status lines,
  ignore code spans, use word boundaries, and reject negation.
- **⚠️ `✅` in a Status line means DONE — even next to an open word.** `✅` tokenises to `[done]`, so
  ``**Status:** ✅ ACTION — install X`` reads as **resolved**. Use `🔴`/`🟠`/`⏸`/`⏳` (they tokenise to
  `[open]`) for anything still needing action.
- **⛔ NEVER stamp the `Status:` line on a handoff that already has a CLOSURE RECORD — it REOPENS it.**
  The record (`<receiver>-to-<sender>/_closed/<slug>.md`) is **sha-bound** to the exact source revision it
  closed. Editing the source changes the hash, the resolver stops matching, and the handoff goes back to
  OPEN. Verified 2026-09-18: adding a marker line flipped `CLOSED — answered by forge` →
  `OPEN — REOPENED: source changed since closure`, and reverting restored CLOSED. **Order of operations:**
  no record → stamp the source (the rule below). Record present → **edit nothing**; the record is the
  authority. The two mechanisms conflict, so the marker rule below is *conditional*, not absolute.
- **A watcher that only scans for marker words cannot see closure records — fix it, don't trust it.**
  `handoff-watcher.py` had zero closure-record awareness (`grep -c closure` = 0), so every handoff closed
  *properly* with a record still read as OPEN and got re-reported as stuck. Real impact: an audit reported
  a closed handoff as "unanswered at 22h". Fix = have `is_resolved()` defer to the record and fail open.
  When a stuck-list disagrees with `handoff_closure.py check`, **the record wins** — verify with the tool
  before believing a watcher.
- **After delivering the report, mark the SOURCE handoff's `Status:` line DONE.** Completing the work and writing the return note to `labs-to-gentech/` is not enough — the watcher/re-flag trigger keys off the source file in `01-HANDOFFS/<sender>-to-<you>/<name>.md` still reading `**Status:** open`. Leaving it open makes the same done item keep surfacing as "new handoff, ACK now". Patch the source's Status line to `✅ DONE — <what> (see <return-lane file>)`, commit, push, and Obsidian-sync. Do this in the same push as the report. (Hit twice in one day on arb-loop-phase0 + lighter-ts-read.)
- **When a peer flags your return as un-ACKed, file the ACK in the lane THEIR watcher scans — not only your own sender-lane convention.** The mesh has two lane conventions (`<sender>-to-<target>/` and `<agent>-to-<group>/`); a watcher that scans one keeps flagging the handoff open/stalled while your full substantive return sits in the other. Substantive return in your own lane, a short ACK or status stamp in the scanned lane, cross-linked — and stamp the source file's Status line in the same push.
- **Close the handoff in EVERY lane it was delivered to, not just the one you were nudged about.** The same note reaches an agent through two lane conventions (e.g. the canonical `01-HANDOFFS/INBOX/<agent>/` delivery lane AND the legacy sibling like `labs-to-labs/`); the copies are independent, so flipping Status on the copy the nudge pointed at leaves the other reading its older status forever — the watcher keeps re-flagging, with the age quoted from whichever copy is stale. Grep the vault for the filename across all `01-HANDOFFS/` subfolders, flip the Status on EACH copy, keep exactly one unambiguous status per file (a legacy copy can carry a second, stale status line), and cross-link the return note into both.
- **Never `write_file` an append-only completion/return log.** `<from>-completions.md` (and return notes) are append-only shared files that every session contributes to. `write_file` overwrites the ENTIRE file, silently destroying all prior sessions' entries — recovered only by `git checkout HEAD -- <file>` then re-appending. Always append with `>>` (or `patch` to add a line), never rewrite the whole file.
- **Peer DMs block until the reply — deliver async instead.** `hermes peer dm <agent>` waits on the
  recipient's response and can hang a session mid-turn (it timed out waiting on a peer that was mid-turn).
  For fire-and-forget delivery use `hermes peer run <agent> --idempotency-key <stable-key> <<'EOF' ... EOF`:
  it returns `run_<id>: started` immediately and the stable idempotency key makes a retry a no-op instead
  of a duplicate. Keep the vault return note as the durable record either way.
- **The peer-DM path can be DARK, not just slow — measure it before you rely on it, and know the local
  twin.** After a multiplex convergence the four per-profile gateways are gone and the default
  multiplexer may have **no `api_server` adapter at all**: `hermes peer dm <peer>` then fails instantly
  with `[Errno 111] Connection refused` and `ss -ltnp` shows nothing on the old ports (measured
  `:8642`–`:8645`). **Nothing is listening — do not read that as the peer refusing.** The mesh's own
  design is that the default's `api_server`/`webhook` adapters are served as `/p/<profile>/` mirrors, so
  the repair is one bind on the default profile plus per-seat peer URLs
  (`http://<host>:<port>/p/<seat>`), which is **gateway-affecting and needs checkpoint ACKs** — never
  taken alone. **Until then: deliver with the local twin, and log the failure.**
  `hermes -p <profile> chat --query-file <file> --oneshot` runs a real turn as that seat's agent (use
  `--query-file`, not `-q`, so quotes and `$(…)` survive the shell); the vault handoff stays the durable
  record; the note says the DM failed and why. **A wake that never landed must never be reported as a
  wake** — and once the peer answers, verify its claim yourself rather than relaying it.
- Don't assume a handoff must go back to Gentech — route peer-to-peer when the target group owns the decision/context.
- The scanner regex `^([a-z]+)-to-([a-z]+)$` matches peer folders; `-to-gentech` is handled separately in `scan_group`, so don't double-count.
- Group agents sometimes push only to GitHub — always `git push vault main` before reading handoffs.
- **Strengthen tool-scout handoffs with vault-backed scope.** When handing off a scouted tool to a group (e.g. a GPU/desktop tool → Forge), search the vault for existing planned usage of that tool BEFORE writing the handoff, and include it. A tool that looks like a one-off may actually be a planned accelerant across several projects (e.g. BlendCap mocap → Blender is already Forge's lane per SETUP.md, #74 Agent Arcade 3D Lobby, and the `blender_mcp` skill). Including that context lets the receiving group see the full picture and prioritize correctly, instead of treating it as a lone tool. Proven Aug 21, 2026: BlendCap handoff to Forge was strengthened this way.
- **A collaborator's note missing at the canonical path is not proof it was never filed.** Fleet members push from side branches and sometimes under a divergent path prefix on top of the canonical one; Obsidian sync can also lag a git push. Before concluding 'never arrived', find their commit (`git log --all --grep=<topic>` or the sha they quoted) and read the note straight out of it with `git show <sha>:<path-as-committed>`. Then flag the path divergence to the sender so their tooling gets fixed — do not silently re-file a duplicate.
- **Trace an attributed claim to its author before accepting or retracting it.** Vault notes get edited by third parties (status headers, digests quoting a number back). Before a peer correction makes you retract something 'you' claimed, `git log`/`git blame` the note: if the figure was quoted into your note's header by someone else, correct the misleading source (the header), not just your copy, and state precisely who measured what. Fix the affected eval/verdict doc entry IN PLACE (restate the corrected trigger/mechanism/workaround) rather than appending an 'UPDATE:' line — a doc that keeps its old wrong claim beside the correction is still wrong to every future reader who skims.
- Close handoff notes with a status line in the fleet resolver's marker vocabulary. Check the resolver's resolved-words list (e.g. `RESOLVED_MARKERS` in the closure tooling) and end the note with a matching status (answered / acked / confirmed / resolved / done) — prose closers like 'accepted + acted' match no machine marker, and fleet-resonant words that FEEL like markers but aren't in the list (superseded, decided, implemented) don't either, so the item stays 'open' and re-alerts loop on it forever. Before trusting any 'resolved via note' claim, sweep open handoffs for closing words the resolver does NOT know.
- **A peer's report back on work you originated is a continuation, not a new ask.** When the async executor (e.g. Forge self-hosting the tool your eval recommended) files results on work you originated, you do not wait for an explicit greenlight to keep acting: read it immediately and act within your lane (correct your own eval/verdict doc, verify their findings independently, route spend/public-write calls onward). Never leave your own eval sitting in 'awaiting greenlight' limbo while the work has already moved past it — the standing greenlight that opened the eval covers its continuation. When two seats end up reporting on the same line in parallel, flag the duplicate lane in your next reply so the fleet stops double-staffing it.


> 🚫 **NEVER `git pull` the vault** — Obsidian Sync writes this same working tree, so a pull reads its changes as local edits and DIVERGES the clone (Forge: 842 phantom deletions / 886 changed files). **Receive by `ob sync`, deliver by `git push vault main` + `ob sync`.** See `00-System/vault-transport-protocol.md`.
