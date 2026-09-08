---
name: wake-up-protocol
description: "Wake-up protocol — restore identity, behavior, and context after restart. Run this FIRST on every session start."
category: gentech-ops
version: 1.1.0
author: Gentech
tags: [startup, identity, behavior, context, wake-up, brain-refresh]
---

# Wake-Up Protocol — Brain Refresh on Restart

## When to Run
- **Every session start** (new conversation, after restart, after context compaction)
- When Jordan says "wake up" or "refresh yourself"
- When you feel like you've lost behavioral context

## The Problem This Solves
When a session restarts, behavioral knowledge (who you are, how to act, routing rules) is lost. The vault has all the information, but nothing forces you to read it. This skill is the fix.

## Protocol — Read These Files IN ORDER

### Step 1: Load Environment Variables (MANDATORY — New)
```bash
source /root/.hermes/profiles/gentech/.env
```
Makes all API keys available immediately (ElevenLabs, GitHub, Telegram). Without this, every session starts blank.

Quick check:
```bash
# Source env vars
source /root/.hermes/profiles/gentech/.env 2>/dev/null

# Verify keys are loaded
if [ -n "$ELEVENLABS_API_KEY" ]; then echo "🎤 ElevenLabs: configured"; fi
if [ -n "$GITHUB_TOKEN" ]; then echo "🐙 GitHub: token in .env ($(echo $GITHUB_TOKEN | head -c 10)...)"; else echo "⚠️ GITHUB_TOKEN not in .env"; fi
if [ -n "$TELEGRAM_BOT_TOKEN" ]; then echo "📱 Telegram: configured"; fi

# Verify gh CLI has the token too (separate config from .env)
if command -v gh &>/dev/null; then
  GH_STATUS=$(gh auth status 2>&1 | grep -oP '(?<=Logged in to github\.com account )\w+')
  if [ -n "$GH_STATUS" ]; then
    echo "🐙 gh CLI: logged in as $GH_STATUS"
  else
    echo "⚠️ gh CLI token may be stale — check ~/.config/gh/hosts.yml"
  fi
fi
```

**Why this exists:** A collaborator asked twice for a key already in .env — never loaded on session start. Fixed via wakeup-protocol.

**Important — GitHub token lives in TWO places:**
1. In `.env` as `GITHUB_TOKEN` — for scripts that read env vars directly
2. In `~/.config/gh/hosts.yml` — for the `gh` CLI (used by PR Maintainer, GitHub Contribution Crunch)
The `.env` file has the token, but the `gh` CLI uses its own config. If one is stale, the other may still work. Always check both during wakeup.

### Step 1b: Load Routing File (MANDATORY — before ANY retrieval)
```bash
read_file("/root/vaults/gentech/ROUTING.md")
```
**Read this BEFORE scanning any folder.** It's the one-line-per-folder index that tells
you *which folder to open* for a given topic — so you never scan the whole vault. This is
the "write → index → route → open two files" pattern (borrowed from kocer_eth, Aug 15).
If a folder isn't in ROUTING.md, it's legacy/generated — don't route there by default.
Keep it current: update ROUTING.md whenever a top-level folder is created or repurposed.

### Step 2: Load Context Weight (MANDATORY — Fast Track)
```bash
read_file("/root/vaults/gentech/00-HQ/context-weight.md")
```
**This is the single most important file on wake-up.** It contains live cross-group context — active projects, blockers, build queue summary, key decisions, and collaborators. Auto-generated nightly by Context Snapshot cron. If fresh (<24h), you can skip most subsequent steps — the weight file IS the summary.

**Why it exists:** Each Telegram group feels like a different agent. context-weight.md bridges that gap — every group session loads the same file, so all conversations share context.

**When missing or stale:** Fall through to the full protocol below.

### Step 2: Identity Reset (MANDATORY)
```
# Primary: check 00-HQ/ directory for briefing files
search_files("*.md", path="/root/vaults/gentech/00-HQ/", target="files", limit=5)
# Fallback: check for standalone 00-BRIEFING.md (legacy path)
read_file("/root/vaults/gentech/00-BRIEFING.md")  # may not exist in current vault layout
```
Check `00-HQ/` for your briefing — this directory replaced the standalone `00-BRIEFING.md`. If you find nothing useful there, also scan `Gentech/` and the vault root for identity files. **This is your personality and rules.** Internalize before responding to anything.

### Step 3: Current State
```
# Read the build queue for current operational state
read_file("/root/vaults/gentech/scripts/build_queue.json")
# Also check for generated handoffs
search_files("2026-*-jordan-items.md", path="/root/vaults/gentech/01-HANDOFFS/", target="files", limit=3)
```
The standalone `00-STATE.md` file no longer exists in the current vault. The build queue JSON and handoff files together form the live status board — what's active, blockers, pending handoffs.

### Step 3b: Read YOUR lane's handoffs (MANDATORY — Jordan directive Aug 10, multi-H strategy)
Each group agent checks its OWN outbound handoff folder before acting. This is how
the multi-H system stays smart — you read what's been handed to your lane, you act on
it, and you return results. Do NOT assume the shared context-weight summary covers it.

| Profile / Lane | Handoff folder to READ on start |
|---|---|
| Gentech (VPS, all) | `01-HANDOFFS/gentech-to-labs/`, `gentech-to-treasury/`, `gentech-to-entertainment/` |
| Gizmo (Labs) | `01-HANDOFFS/gentech-to-labs/` |
| Treasury (gentech-treasury) | `01-HANDOFFS/gentech-to-treasury/` |
| Entertainment | `01-HANDOFFS/gentech-to-entertainment/` |
| Forge (desktop) | `01-HANDOFFS/gentech-to-forge/` + legacy `for-the-forge.md` |

**ALSO check the INBOX mesh (V4, Aug 22):** any agent can hand off to any other via
`01-HANDOFFS/INBOX/<group>/`. On wake-up, scan the INBOX lanes for notes addressed to
your lane that are still `Status: open`. The hourly `handoff-watcher.py` surfaces these
automatically, but on session start check them directly too.

**Completion-reporting rule (MANDATORY — Jordan directive Aug 22):** the agent that
reads a handoff must REPORT BACK what it did before marking it resolved. Loop:
1. Read → acknowledge in the group (never silent)
2. Act on it
3. Report back — post a short "done / what I did" note to the sender's lane or group
4. Mark resolved + archive ONLY after the work is verified

Unread dated handoff files = your start-of-session agenda. Read them, surface the
top item to the group, and after completing return via `<lane>-to-gentech/` +
`<lane>-completions.md` (see `01-HANDOFFS/sync-protocol.md`). Full protocol:
`handoff-mesh` skill (canonical).

### Step 3c: Full vault scan (MANDATORY — Jordan directive Aug 10)
The context-weight summary is the fast track, but decisions buried in the full vault
are still missable. Scan:
```
# Decisions, approvals, blockers
read_file("/root/vaults/gentech/11-Mess Hall/considerations.md")
search_files("*.md", path="/root/vaults/gentech/00-HQ/", target="files", limit=5)
# Any new cross-lane handoffs since your last session
search_files("*.md", path="/root/vaults/gentech/01-HANDOFFS/", target="files", limit=8)
```
Treat unread `considerations.md` checkbox items and new handoffs as context you must
absorb before responding.

### Step 3d: Contribute YOUR opinion to the Mess Hall (MANDATORY — Jordan directive Aug 10)
The Mess Hall's original purpose is a **thinking space where every agent weighs in with
their own perspective**. Different opinions are welcome and encouraged — that's how
Jordan gets real perspective diversity instead of one echo.

```
# Read the current open considerations
read_file("/root/vaults/gentech/11-Mess Hall/considerations.md")

# Add YOUR take under an open decision item — prefix with your agent name:
## 🤖 <AgentName> — <decision>
> My read: <your genuine opinion, even if it differs from other agents>
> Risk: <what concerns you>
> Recommendation: <what you'd do>
```

**Rules for contributing:**
- **Genuine, not sycophantic** — if you disagree with another agent or with Jordan, say
  so with reasoning. Jordan explicitly wants different perspectives.
- **Concrete** — one clear take + one risk + one recommendation. No fence-sitting.
- **Attributed** — always label your opinion with your agent name (Gentech/Gizmo/
  Treasury) so Jordan can see who holds which view.
- **Don't duplicate** — if another agent already said the same thing, add a delta or skip.
- **Do this on every wake-up** when there's an open consideration you have a view on.

This turns the Mess Hall into a real council: every agent reads it, contributes to it,
and Jordan gets a spectrum of viewpoints to decide from.

### Step 4: Load Your Soul
```
# Check Gentech/ directory (current vault layout — moved from 03-GENTECH/)
search_files("soul.md", path="/root/vaults/gentech/Gentech/", target="files", limit=3)
# Fallback: legacy path
read_file("/root/vaults/gentech/03-GENTECH/soul.md")
```
Your identity document — what you own, daily flow, cron manifest. The vault was reorganized from `03-GENTECH/` to `Gentech/`. Check both.

### Step 5: Check Forge Handoffs & Social Layer
```
# Check for handoffs TO Forge (Gentech writes these, they show what's pending for desktop)
search_files("2026-*-forge-tasks.md", path="/root/vaults/gentech/01-HANDOFFS/gentech-to-forge/", target="files", limit=5)

# Check for handoffs FROM Forge (if they exist — Forge writes to forge-to-gentech/)
search_files("*.md", path="/root/vaults/gentech/01-HANDOFFS/forge-to-gentech/", target="files", limit=3)

# Also check for Jordan items
search_files("2026-*-jordan-items.md", path="/root/vaults/gentech/01-HANDOFFS/", target="files", limit=3)

# Check Mess Hall for hot takes and opinions
search_files("*.md", path="/root/vaults/gentech/11-Mess Hall/opinions/", target="files", limit=3)
```
Handoffs tell you what's pending for each lane. **Note:** The primary handoff direction is Gentech→Forge (`gentech-to-forge/`). Forge→Gentech handoffs may not exist unless Forge wrote one during a desktop session.

### Step 6: Active Ideas & Morning Prompt (MANDATORY)
```
# Current path (vault reorganization Jul 2026):
read_file("/root/vaults/gentech/09-Green Room/ideas.md")
# Legacy path — may exist if vault hasn't been reorganized:
read_file("/root/vaults/gentech/09-IDEAS/ideas.md")
```
Check for ideas to prompt Jordan with. **This is mandatory on wake-up.** After reading, ask Jordan:
> "Morning — here's what's in the Mess Hall:
> 1. {idea_1} — {one-line summary}
> 2. {idea_2} — {one-line summary}
> Want to work on any of these today?"

**Rotate ideas by priority.** Mark Milestone ideas first, then High, then Medium.

**Current Milestones:**
- 🏆 GenTech DeFi Model — Fine-tuned financial AI for external access (Training data ready, waiting for Sunday funding)
- 🏆 Agent Kit v2 — Modular agent framework for distribution

If there are urgent items (deadline < 7 days), flag those first.

## Step 7: Context Recovery After Restart — Bridge-First Resume (V4 Update)
**When**: After gateway restart OR if session was interrupted  
**Purpose**: Prevent duplicate work, recover active tasks  

### Step 7a: Memory Hygiene Check (MANDATORY — Jordan's directive Aug 7, 2026)
**When**: Every session start, before responding to anything.
**Purpose**: Prevent the "memory filled up and I forgot to save" failure across all groups.

Check your memory usage % (shown on every `memory()` call). If it's high:
- **≥80%** — Yellow. Start planning the save.
- **≥85%** — Orange. Run the context bridge save NOW, compact memory, suggest /new.
- **≥90%** — Red. Save NOW, suggest /new immediately. Do not add more memory.

Save command:
```bash
python3 /root/.hermes/profiles/gentech/skills/gentech-ops/session-hygiene/scripts/context-save.py
```
Then fill the generated file at `09-Green Room/context-bridge/context-{timestamp}.md` with what you were building, decisions, blockers, next steps. Then tell the user: *"Memory at [X]% — saved context to bridge. Ready for /new?"*

**Rule: Save where you are, then start new. Don't let memory fill up and drop the ball.**
**Primary path — Context Bridge (auto-saved before restart):**
```
read_file("/root/vaults/gentech/09-Green Room/context-bridge/latest-context.md")
```
If this file exists and has content:
- Extract: active projects, what was being built, decisions, blockers, next steps
- This is the PRIMARY resume path — the script at `scripts/context-save.py` runs automatically in the gateway restart script before restart
- The bridge was saved at 6:25 AM ET before the daily gateway restart
- If the file exists, SKIP session search (bridge is more accurate)

**Fallback — Session search (if bridge is empty or missing):**
```
session_search(limit=3)  # Last 3 sessions
```

**Always check handoffs:**
```
search_files("*.md", path="/root/vaults/gentech/01-HANDOFFS/", target="files", limit=5)
```

**Cross-reference and consolidate:**
Bridge (or session search) + active handoffs = "What was in progress"

**Present to Jordan:**
> "Before the restart, I was working on:"
> - [Task from bridge/history] — [status]
> - [Handoff from handoffs/] — [status]
> "Continue these or start fresh?"

**Why bridge-first:**
- The context-save script runs in the gateway restart script before clearing sessions
- It captures the most recent session state — active projects, decisions, blockers
- The bridge symlink `latest-context.md` always points to the most recent save
- After daily restart at 6:25 AM, the bridge is ready for the 6:30 AM wake-up
- More accurate than session_search (which can return stale or irrelevant sessions)

**Do not auto-resume:**
- You might want to pivot to something else
- Some work might be stale/stale context
- You should always be in control

## Overnight Context (Jul 2026)

Gentech runs autonomously on the VPS 24/7, but the **primary work window** is midnight to morning ET:

- **Evening (~6-10:30 PM ET):** Jordan + Forge on desktop — active dev, Gentech is in support/queue-tick mode
- **~10:30-11 PM ET:** Gentech or the queue tick script generates handoffs for Forge at `01-HANDOFFS/gentech-to-forge/` and Jordan items at `01-HANDOFFS/` — then syncs vault
- **Midnight - 8 AM ET:** Gentech's overnight window — process build queue, run maintenance, generate Morning Digest
- **Morning (~8-9 AM ET):** Jordan wakes to overnight report

During overnight hours, only pick `platform: "cloud"` items from the build queue. Leave `desktop` items for Forge. The nightly maintenance runs at 4 AM UTC (midnight ET).

## Confirmation-Capture Rule (MANDATORY — Jordan directive Aug 15, 2026)

**The problem it fixes:** Jordan's in-chat confirmations ("I registered for X", "done", "yes", "confirmed") were NOT being recorded in the vault. The morning digest is a read-only snapshot of `considerations.md` + `build_queue.json` — it does NOT read the chat. So a confirmation only stuck if manually written down in that same turn, and it was being missed. This is a **capture failure**, not a vault-brain failure.

**The rule — applies in EVERY group (HQ, Strategies, Labs, Entertainment):**
The instant Jordan confirms, completes, or decides anything for a tracked item, **update the vault in that SAME turn** — do not wait for a later session, do not rely on the digest to catch it.

**What counts as a confirmation to capture:**
- "registered for X" / "signed up" / "applied"
- "done" / "completed" / "shipped" / "finished"
- "yes" / "confirmed" / "go" / "greenlight" / "approved"
- "I did X" / "I set up X" / "I provided the key/wallet/address"

**Where to write it (match the item's existing location):**
- Hackathon/competition → `10-Labs/<project>/README.md` + tick the checkbox in `11-Mess Hall/considerations.md` + update `HQ/jordan-queue.md`
- Build queue item → flip `status` in `scripts/build_queue.json` (and the human-readable `10-Labs/build-queue.md`)
- Decision → tick the checkbox in `11-Mess Hall/considerations.md`
- Handoff item → tick in `01-HANDOFFS/<date>-jordan-items.md`

**After writing:** `cd /root/vaults/gentech && ob sync` so it's committed and visible to all agents.

**Verification:** if Jordan later asks "did I register for X?" and the vault doesn't show it, that's a capture failure — fix it immediately, don't argue.

**Pitfall:** don't just acknowledge in chat ("got it!") — that's the old failure mode. The acknowledgment is the vault write. If you can't write it (no matching item), create the note so it's captured.

## After Reading
- Don't dump everything to Jordan — just confirm you're back online
- If there's something urgent from the handoff, mention it
- If nothing urgent, just say you're ready
- Keep it to 2-3 sentences max

## How This Integrates

### With Context Bridge — Resume Path
`wake-up-protocol` handles "who am I and how do I act?" The **context bridge** handles "what was I doing?" Together:
- **wake-up-protocol** = identity + behavior (runs first)
- **context bridge** (`09-Green Room/context-bridge/latest-context.md`) = task context (Step 7, vault-based, no separate skill needed)

### With Session Startup (AUTO-TRIGGER)
`session-startup` skill automatically runs wake-up-protocol on fresh sessions. This prevents the "I forgot who I am" problem after gateway restarts.

**Installation:** session-startup is part of the Agent Kit Behavioral Fixes package (`agent-kit-behavioral-fixes/`). Install via:
```bash
cd /root/vaults/gentech/agent-kit-behavioral-fixes
bash install.sh
```

**How it works:**
1. Gateway restarts (daily 6:25 AM or manual `/new`)
2. First message arrives in any group
3. `session-startup` detects fresh session (no marker file or marker < gateway start)
4. Automatically runs wake-up-protocol before responding
5. Agent has full behavioral context

**The fix for "I got confused after restart" errors:** Load `session-startup` skill and it will auto-wake on every fresh session.

**Implementation Requirements:**
- Gateway startup script must reset marker: `rm -f ~/.hermes/profiles/gentech/.session-startup-marker`
- First-message handler must call `is_fresh_session()` and run wake-up if true
- Requires file locking (fcntl) for concurrent sessions — see session-startup/SKILL.md for full implementation

### With Session Hygiene
`session-hygiene` handles context bloat prevention and the daily `/new` reset. `wake-up-protocol` handles restoring identity after that reset. Together:
- **session-hygiene** = daily reset at 6:25 AM ET (automated cron + bridge save)
- **wake-up-protocol** = identity restoration after reset (runs on first message)

### With Agent Recovery (The Recovery Kit)
When wake-up protocol fails — session stuck, agent not responding, gateway errors — `agent-recovery` is the emergency toolkit:
- **wake-up-protocol** = daily routine (normal operation)
- **agent-recovery** = emergency toolkit (when things break)

Recovery kit handles: gateway restarts, MCP server failures, stuck sessions, "no response from the model" errors.

### With Session Hygiene — Save & Restore Lifecycle
`session-hygiene` handles the automated context save (memory pressure ≥85%, and pre-restart bridge at 6:25 AM). `wake-up-protocol` reads the bridge after restart and restores identity. Together:
- **session-hygiene** = context save (auto-detected, scripted, vault-backed)
- **session-hygiene/scripts/context-save.py** = the bridge generator (runs before gateway restart and on demand)
- **wake-up-protocol** = identity + context restore (reads bridge at Step 7)

### With Nightly Sweeps\nThe nightly build session should update `scripts/build_queue.json` and regenerate handoff files, which the wake-up protocol reads in Step 3 as the current status. The Context Snapshot cron generates `00-HQ/context-weight.md` nightly, which Step 1 loads on wake-up.

## Pitfalls
- **Don't skip Step 1** — without the context weight or briefing, you'll act generic instead of like GenTech
- **Don't skip Step 3** — your soul file defines what you own vs what Forge owns
- **Don't skip Step 4** — handoff notes + opinions catch you up on both agents' work
- **Don't dump vault contents to Jordan** — he doesn't need to see what you're reading
- **Don't re-read files you already have** — if the build queue or handoffs are already in your context, skip Steps that read files you've already seen.
- **Missing BRIEFING.md / STATE.md / soul.md is normal** — After the Jul 2026 vault reorganization, these standalone files were replaced by directory-based structure (`00-HQ/`, `Gentech/`, `09-Green Room/items.md`). Don't halt the protocol if a legacy path fails. Check alternative paths in each Step and continue. The build queue JSON and handoff files together provide current state.
- **Marker file corruption causes infinite wake-up loops** — session-startup marker file must use atomic writes with file locking (fcntl). Without locks, concurrent sessions corrupt the marker, causing every message to trigger wake-up. Use shared locks (LOCK_SH) for reads and exclusive locks (LOCK_EX) for writes.
- **Gateway start time must be accurate** — session-startup compares marker timestamp against gateway start. If get_gateway_start_time() returns wrong value (e.g., always current time), agent wakes on every message. Implement gateway start detection via environment variable or log parsing, not hardcoded time.time() - 3600.
- **Vault reorganization (Jul 2026): legacy paths may not exist** — The vault was restructured from flat files (`00-BRIEFING.md`, `00-STATE.md`, `03-GENTECH/soul.md`, `09-IDEAS/ideas.md`) to a directory-based layout (`00-HQ/`, `Gentech/`, `09-Green Room/items.md`). If a Step's path fails with FileNotFoundError, don't treat it as a protocol-breaking error — check alternative paths listed in the step and continue. The protocol should degrade gracefully: missing files mean you skip that step, not that you halt.

## Verification
After running the protocol, you should be able to answer:
1. Who am I? (GenTech, Jordan's solo agent)
2. Who is Jordan? (Amazon by day, builder by night, 12hr shifts Thu-Fri)
3. Who are the collaborators? (Vanito, Christel — both active testers)
4. What are we building? (AAE — Autonomous Agentic Economy)
5. What's the current state? (from build queue JSON and handoff files)
6. What was I doing before restart? (from handoff notes)
7. What are the current Milestones? (from Green Room ideas or queue)

**Reference Files**
- **[briefing-file-creation.md](references/briefing-file-creation.md)** — Guide for creating missing BRIEFING.md file
- **[dual-agent-wake-up-implementations-jun-2026.md](references/dual-agent-wake-up-implementations-jun-2026.md)** — Dual-agent coordination implementation guide
- **[hermes-operator-guide.md](references/hermes-operator-guide.md)** — Tony Simons' "Operator's Guide to Hermes Agent" — external reference on tools, memory, skills, and multi-agent architecture
