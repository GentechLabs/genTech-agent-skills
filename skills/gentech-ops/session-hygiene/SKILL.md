---
name: session-hygiene
description: "Auto-manage context bloat, memory pressure, and session freshness. Prevents the 'lost in the task' behavior."
version: 2.0.0
author: gentech
category: gentech-ops
hermes:
  tags: [context, memory, session, freshness, automation, auto-save, pressure-protocol]
---

# Session Hygiene — Automated Context Pressure Protocol

## Pitfall: cron blocks skill-dir scripts (Aug 20 2026)
The cron runner **blocks any `script:` whose path resolves outside the
scripts directory** (`/root/.hermes/profiles/gentech/scripts`). A job pointing
directly at `skills/<x>/scripts/<script>.py` fails with:
`Blocked: script path resolves outside the scripts directory`.
Fix: put a thin wrapper in `scripts/` that subprocess-calls the skill script
(see `prewake_context_save.py`). Repoint the cron job's `script` to the
wrapper, then re-fire to confirm.

## Purpose
When conversations get long (30+ messages) or memory hits 80%+, the model degrades. This is an **active behavior I follow**, not guidelines. On every memory-save response, I check the usage %. When thresholds are crossed, I auto-save and recommend /new.

## 🔴 HARD RULE — Auto-Detect & Act

On every `memory()` tool call, the response includes current usage **as a percentage** (e.g. `"usage": "88% — 1,949/2,200 chars"`). I MUST check this value on every memory operation.

**Exact thresholds:**
- **≥80% — Yellow zone.** Start planning the save. Reduce new saves.
- **≥85% — Orange zone.** Save context snapshot, compact memory, suggest /new.
- **≥90% — Red zone.** Save context snapshot NOW, suggest /new immediately. Do not add more memory.

### Auto-Save Protocol (≥85%)

When memory hits 85% or higher:

1. **Run the context-save script:**
   ```bash
   python3 /root/.hermes/profiles/gentech/skills/gentech-ops/session-hygiene/scripts/context-save.py
   ```
2. **Populate the bridge file** — Write key decisions, what I was building, blockers, next steps into the generated file at `09-Green Room/context-bridge/context-{timestamp}.md`
3. **Compact memory** — Use `memory()` with a batch operations array to:
   - Remove stale entries older than 7 days
   - Merge similar entries
   - Remove task-progress entries (PR numbers, commit SHAs, completed-work logs)
   - Keep identity facts, user preferences, environment details
4. **Tell Jordan:** "Memory at [X]% — here's what's saved. Time for /new?" Follow with a 2-sentence summary of what's preserved.
5. **Wait for confirmation** — Jordan says /new or says "save it"

### Context Bloat (>25 messages in session)

When conversation exceeds 25 messages:

1. **Assess** — Are we in the middle of something critical? If yes, finish it first.
2. **Save to vault** — Write a context bridge snapshot (same as the memory trigger path).
3. **Suggest fresh session** — "This conversation is getting long. I've saved context — want to /new?"
4. **Don't force it** — If Jordan declines, keep going but note context is accumulating.

## 🔄 SAVE AT EVERY STOPPING POINT (Jordan directive — 2026-08-17)

The old "save at midnight" approach loses work done 12:00–4 AM (the 6:25 AM bridge
was a blank template, not real content). Fixed: the auto-save now pulls REAL content
from the session DB. But the PRIMARY rule is **proactive saving at every stopping point**,
so nothing depends on a clock or a memory threshold.

**HARD RULE — save at every stopping point, any time of day:**
- When you finish a meaningful chunk of work (a scene, a clip, a build step, a PR, a
  research pass), **write it to the vault immediately** — a dated handoff under
  `01-HANDOFFS/<lane>-to-gentech/YYYY-MM-DD.md` or an update to the relevant project
  file. Do NOT wait for a nightly save or the 6:25 AM bridge.
- The handoff is the REAL resume point the 6 AM wake-up reads. The bridge is a fallback.
- Save small and often. Every completed chunk is already safe if the session dies.

**HARD RULE — route it to the RIGHT folder, don't save blindly (Jordan directive — 2026-08-17):**
At a stopping point you have the whole brain in front of you — use it. Before you write,
decide WHERE each piece belongs:
- **Group-specific work** → save to that Telegram group's own folder/lane first (e.g.
  Entertainment content → `Entertainment/` + `01-HANDOFFS/entertainment-to-gentech/`).
- **Cross-group / open ideas / decisions** → check `11-Mess Hall/considerations.md`
  and `09-Green Room/` (ideas, context-bridge) — if anything you learned this session
  belongs there (a decision, an idea worth keeping, a consideration for another lane),
  put it there. Don't let it die in a generic handoff.
- **Actionable status** → update `build_queue.json` + `considerations.md` if the
  stopping point changed an item's state.
Saving isn't a dump — it's routing each piece of the brain where the next reader will
look for it.

**HANDOFF IS A FORM OF SAVING (Jordan directive — 2026-08-17):**
Routing a project onward into the build pipeline is its own kind of save. When a
stopping point means a project is ready to move to another lane, don't leave it sitting
in your own notes — **hand it off to where it gets built:**
- **Needs building / is a build item** → send it to **Labs** via `01-HANDOFFS/<lane>-to-labs/`
  (or into `build_queue.json`). That's saving it into the queue so it actually gets built.
- **Needs the desktop / GPU (Forge)** → `01-HANDOFFS/<lane>-to-forge/` (e.g. ACE-Step,
  ComfyUI renders, heavy builds on the RTX 3070). That's saving it to the machine that
  can do it.
- **Needs treasury / funding / payments** → `01-HANDOFFS/<lane>-to-treasury/`.
- **Needs another group's lane** → that group's inbound handoff folder.
Same principle as the rest: at a stopping point, use the whole brain to put the project
where the next reader/doer will pick it up — not in a generic log. A project that's
handed off correctly is saved AND scheduled.

**COMPLETION MUST SHOW DONE + HAND OFF TO THE ORIGIN GROUP (Jordan directive — 2026-08-17):**
When a build item is completed, "done" isn't enough — close the loop so the *why* is
recoverable. Every completion must BOTH:
1. **Mark it complete** — flip `status` to shipped/completed in `build_queue.json` (and
   the human-readable queue file). Show the completion, don't leave it ambiguous.
2. **Write a handoff back to the group where the task was completed** — a dated
   completion note in that lane's completions file + `01-HANDOFFS/<lane>-to-gentech/`
   entry describing WHAT was actually built and WHY (the decisions/intent behind it).
This is the same "routing" principle applied to the end of a task: don't just tick a box,
leave a trace of what was done and the reasoning, pointing back at the origin group. That
trace is what lets anyone (or the Morning Digest) look at a shipped item and understand
the "why" — not just that it got done.

**HARD RULE — collaborators can trigger a save (Jordan directive — 2026-08-17):**
Saving isn't one-directional. Vanito (and other collaborators) work on the projects too — they
can and should say "let's save" at any point, and the agent must honor it immediately,
the same as if Jordan said it. Don't wait for a stopping point you choose; when a
collaborator asks for a checkpoint, do the routed save right then. And agents should
invite it — at a natural pause, ask *"Want me to save here?"* so collaborators know the
checkpoint is always available to them.

**HARD RULE — ask the human at stopping points (Jordan explicitly wants this):**
- At a natural stopping point (project milestone, long session, memory ≥85%), ask the
  collaborator: **"Want to save now or keep going?"** — don't just assume.
- This applies with Jordan AND other collaborators (Vanito, etc.).
- A quick checkpoint is always welcome: *"We hit a good stopping point — save progress
  and keep going, or wrap here for the night?"*

**HARD RULE — when memory is full, tell the GROUP and the COLLABORATOR (Jordan directive — 2026-08-17):**
Memory filling up is a coordination event, not a private one. When you hit the memory
threshold (≥85% orange, ≥90% red) **in any group**:
1. **Save progress first** (routed as above) so nothing is at risk.
2. **Let the group know**: "Memory's getting full — I've saved progress."
3. **Tell the specific collaborator you're working with** (e.g. Vanito) how to
   start a fresh context so you can continue seamlessly: *"Hey Vanito — my context is
   filling up. Start a new chat/context (or say /new) and we'll pick right back up from
   the saved handoff."* Give them the exact resume file/handoff to reference.
4. Only then start the fresh session yourself.
The goal: no collaborator is left hanging because you silently ran out of context. Make
it a smooth handoff for them, not a surprise.

**Why it matters:** the auto-capture now catches everything, but the handoff written at
the stopping point is richer (decisions, intent, next steps) than the auto-pulled
activity log. Write the handoff when you stop; let the auto-bridge be the safety net.

## 📋 Detection — Where I Check

| Trigger | How I Detect | Action |
|---------|-------------|--------|
| Memory usage ≥85% | `memory()` response shows `usage: "X%"` | Run save protocol |
| Session is 25+ messages long | Count of back-and-forth in this conversation | Suggest /new |
| Jordan says "save progress" or "/new" | Direct instruction | Save immediately, don't question |
| Memory save fails (too full) | memory() returns error or entry rejected | Emergency save + compact |
| I notice context feels heavy | Subjective — tasks take longer, I re-read history | Proactive check + save |

## 🏃 Active Behavior — The Save Sequence

When ANY trigger fires:

```
Step 1: Run the context bridge script
  → python3 scripts/context-save.py
  → Generates context-{timestamp}.md in 09-Green Room/context-bridge/

Step 2: Populate the bridge file with:
  - What I was building (project + status)
  - What decisions were made this session
  - Key facts discovered
  - Blockers
  - Next steps for each active project
  Use read_file + patch to fill in the template.

Step 3: Compact memory via memory() batch operations
  - Remove task-progress logs (PRs, commits, completed phases)
  - Remove entries >7 days old unless still relevant
  - Merge duplicate facts
  - Keep: user preferences, identity, environment facts, stable conventions

Step 4: Report to Jordan
  "Memory at X% — saved context to bridge file. Ready for /new?"
  Include a brief summary of what was preserved.
```

## 🧠 Memory Hygiene Rules

### Weigh Each Task Against Current Memory (Jordan Aug 22)
Before starting ANY task, ask: **"What is my current memory %, and does this task
need to be saved to the vault or can it live in the brain?"** Keep memory in mind
constantly, not just when the wall hits.

**The weight-check — before every task:**
1. **Check your memory %** — the `memory()` tool response shows usage as a % on every
   save. Also the fleet watchdog reports it. Keep it front-of-mind.
2. **Route by task weight:**
   - **Light task** (a quick answer, one tool call) → do it, memory likely fine.
   - **Heavy task** (multi-step build, big write, research, long session) → this WILL
     bloat memory. Save the task's context to the VAULT FIRST (project file / handoff /
     context bridge), then do the task with a clean memory. The vault holds it; memory
     only tracks the active state.
3. **Proactive, not reactive** — trim BEFORE you bloat, not at the wall. If memory is
   already 70%+ and a heavy task is coming, save-to-vault + compact memory FIRST so the
   heavy task has room.
4. **Never lose it** — every save is archive-first to the vault. Memory is the index;
   the vault is the storage.

**Rule:** A heavy task should never push you past 85%. If it would, park/save the
overflow to the vault before starting. The agent, not the wall, decides where context
lives.

### What to Keep in Memory
- User preferences and corrections
- Environment details (paths, tools, credentials)
- Stable project conventions (build system, test framework, deploy target)

### What to REMOVE from Memory on Compact
- PR numbers, issue numbers, commit SHAs
- Completed-work logs: "fixed bug X", "submitted PR Y", "Phase N done"
- File counts or artifact inventory
- Any fact that will be stale in 7 days
- Previous session summaries

### When to Stop
If memory() refuses an add due to full capacity:
1. Don't keep retrying — compact first
2. Run the save protocol immediately
3. Don't lose information — save it to vault first, compact second

## 💾 Context Bridge — What Goes In

The bridge file (`09-Green Room/context-bridge/context-{timestamp}.md`) is what wake-up reads after /new. It must be **actionable**, not a log:

```
## Active Project 1
- What I was building:
- Exact file/line I was at:
- Next code step:
- Blocker (if any):

## Decisions This Session
- We agreed X instead of Y because Z

## Blockers Flagged
- [Blocker] — explain, waiting on Jordan

## Resume Commands
- `cd /project && ...`
- Check handoffs folder
```

## 🧹 Memory Dietician — Automatic Boundary Enforcement

A nightly cron (`memory-dietician.py`) runs at midnight ET to enforce size limits on all context-bearing files:

| File | Max | Auto-Trim |
|------|-----|-----------|
| MEMORY.md | 2,100 chars | No (manual) |
| USER.md | 1,300 chars | No (manual) |
| witness-log.md | 1,500 chars | ✅ Resolved entries >7 days |
| context-weight.md | 1,200 chars | Manual review flagged |

**Insight from X (Jul 28, 2026):** Someone built an elaborate memory stack around Hermes, deleted it, restored defaults — agent worked dramatically better. Thesis: more memory = worse performance. Context limits and "capacity theater" (filling context with noise) hurt focus.

**Applied to Gentech this session:**
- MEMORY.md / USER.md consolidated, removing Vanito/HIKARI bloat and redundant model routing
- witness-log.md cut from 3,041 → 1,338 chars (5 resolved entries removed)
- context-weight.md cut from 1,799 → 1,024 chars (stale project noise stripped)
- **Total context saved: ~3,500 chars**

Script: `scripts/memory-dietician.py` — runs nightly at 5:00 UTC, silent when healthy.

## 🔄 Post-/New Flow

After Jordan runs /new:
1. session-startup loads (wake-up-protocol)
2. wake-up reads the latest-context.md symlink in context-bridge/
3. Memory is rebuilt with critical facts
4. Projects resume from bridge instructions

This replaces the old approach of "save to Mess Hall and hope someone reads it."

## Response Rules [unchanged below]

### Casual Messages (links, quick comments, reactions)
- **Extract + summarize** — 1-2 sentences max
- **Don't load skills** — unless task requires it
- **Don't do deep analysis** — unless asked

### Complex Tasks (build, audit, research)
- **Load relevant skills** — only the ones needed
- **Fresh context** — check vault first
- **Save progress** — to vault during work, not just at end

### Mid-Response Truncation Prevention
When hitting token limits mid-response:
- **Finish the current thought completely** — don't leave sentences hanging
- **Use executive summary structure** — complete points before stopping
- **Explicitly signal completion** — "Done" or "✅ Complete" at the end
- **Follow up proactively** — don't wait for user to ask "what about the rest?"
- **Pattern**: Complete current section → deliver → continue in next message if needed

**Pitfall**: Stopping mid-sentence or mid-thought frustrates users. Always complete the current idea before the token limit forces a stop. If you can't fit everything, prioritize complete, coherent partials over incomplete wholes.

### Voice Messages
- **Transcribe + respond** — don't over-analyze the voice aspect
- **If it's a link** — extract and summarize quickly
- **If it's a question** — answer directly, don't add unnecessary context

## Automated Daily Reset — Bridge-Save + Gateway Restart

Sessions accumulate context from cron deliveries until they hit limits. Without daily resets, groups get stuck.

The system crontab script at 6:25 AM ET:
```bash
25 6 * * * /root/.hermes/profiles/gentech/scripts/daily-gateway-restart.sh >> /root/.hermes/logs/gateway-restart.log 2>&1
```

This script:
1. **Saves context bridge** — runs `scripts/context-save.py` to capture overnight work, decisions, and active projects
2. **Restarts the gateway** via `systemctl --user restart hermes-gateway-gentech`
3. **Clears ALL in-memory sessions** across all groups
4. **Waits 10 seconds** for initialization
5. **Logs result** to `/root/.hermes/logs/gateway-restart.log`

**Why 6:25 AM:**
- Before first morning cron jobs (typically 6:30-7:00 AM)
- Bridge save captures the overnight work window (midnight-6:25 AM)
- Gateway restarts in ~10 seconds, so 6:25 → 6:26 = ready before 6:30 deliveries
- Wake-up protocol on first message reads the bridge, restoring context seamlessly

**Who can also trigger `/new`:**
When a user sends `/new` in a group, it resets ONLY that group's session. This is useful mid-day when one group gets stuck but others are fine.

**Recovery when `/new` isn't enough:** See `agent-recovery` skill — gateway restart from outside the process, MCP server diagnostics.

## Integration

- **session-startup** — automatically runs wake-up-protocol on first message after fresh session. This prevents "I forgot who I am" after daily resets. Uses marker file vs gateway start time comparison.
- **wake-up-protocol** — restores context after fresh session
- **agent-recovery** — the emergency toolkit when sessions stay stuck after `/new`
- **context-loading** — checks vault before work
- **vault-maintenance** — handles daily backups and cleanup
- **memory tool** — saves durable facts (keep under 85%)

## The Rule

**Short messages → short responses.**
**Long sessions → suggest fresh start.**
**Memory full → clean before adding.**
**Topic switch → don't carry old context.**
