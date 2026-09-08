---
name: dual-agent-coordination
description: Dual-agent operational coordination between Gentech (VPS) and Forge (Desktop) systems with vault-based synchronization and model routing strategies.
tags: [gentech, coordination, dual-agent, routing, synchronization]
---

# Dual-Agent Coordination

**Pattern:** Coordinated operation between Gentech (VPS, 24/7) and Forge (Desktop, home) with vault-based state sharing and optimized model routing.

---

## Architecture Overview

### System Roles
- **Gentech (VPS)**: 24/7 operations, strategic coordination, routing, cron, research, DeFi monitoring
- **Forge (Desktop)**: Build, content, coding, OSS contributions, PRs, local builds, email via Cloudflare

### Zero-RAM Stack (Forge Desktop)
Forge runs all models in the cloud — zero local RAM for AI. Full 32GB available for Unreal Engine, builds, and local development.
- **Models**: Cloud (Z.AI, Ollama Cloud, OpenCode Go)
- **Vision**: Cloud (qwen3-vl:235b-instruct via Ollama Cloud)
- **No local model management

**Forge's Expanded Capabilities:**
- ✅ Build & Development (APIs, Workers, smart contracts)
- ✅ Content Creation (social media, blog content, technical writing)
- ✅ Operations (system monitoring, maintenance, troubleshooting)
- ✅ Analysis (data analysis, market research, competitive intelligence)
- ✅ **Game Development** (Unreal Engine 5.8, Blender, 3D modeling, Chaos Clothing physics)
- ✅ **3D Character Pipeline** (Lychee Studio → Blender → AccuRig → Unreal Engine)
- ✅ **Rhythm Game Remake** (VISUAL KEi TAP → full 3D Unreal Engine game)

### Forge's Game Dev Pipeline (Jul 2026)
Forge is the designated game developer. Unreal Engine and Blender are desktop-only (GPU required) — never attempt to install or run them on the VPS.

**Lychee Studio → Blender → AccuRig → Unreal Engine 5.8 pipeline:**
1. **Lychee Studio** (lychee-studio.ai) — Generate 3D characters, clothing, props from text/images. Props Extraction breaks a character into separate game-ready pieces. Starter plan: 20€/seat/month, 20,000 credits (~40 3D models). 5,000 free credits to start.
2. **Blender** — Fit, align, adjust AI-generated meshes. Sculpt mode for quick shape fixes.
3. **AccuRig** — Auto-rig character, export to Unreal skeleton.
4. **Unreal Engine 5.8** — Import, retarget animations, Chaos Clothing physics, build the game.

**Character reference images** for KAGE and HIKARI (Vanito's Seedance characters) are in the vault at `music/vanito/` — these should be handed to Forge as the source of truth for 3D model generation. The goal is to preserve the Seedance character look while upgrading to full 3D with physics.

**Gentech's role:** Document the pipeline, gather character references, prepare the asset bible. Forge does the actual 3D work.

### Model Routing Strategy
| Environment | Primary | Complex Tasks | Vision | Cost Strategy |
|------------|---------|---------------|--------|---------------|
| VPS (Gentech) | GLM-4.7 (paid) | GLM-5.2 | GLM-4V | Use paid subscription first, DeepSeek fallback |
| Desktop (Forge) | GLM-4.7 (paid) | GLM-5.2 | GLM-4V | Same cost-optimized pattern |

### CRITICAL COST OPTIMIZATION RULE (July 5, 2026)

**Strategy: Use What You've Paid For**

| Situation | Decision |
|-----------|----------|
| GLM subscription active | ✅ Use GLM-4.7 (paid for, use it or waste it) |
| GLM quota exhausted | ✅ Switch to DeepSeek V4 Flash (free/cheap) |
| Audit needed | ✅ Use GLM-5.2 if GLM quota available |
| Critical quality needed | ✅ Use GLM-5.2 (even if quota low) |

**Build Queue Execution Protocol: Build First, Audit Last**

| Phase | Model | Purpose |
|-------|-------|---------|
| **BUILD** | GLM-4.7 (paid) or DeepSeek V4 Flash (free) | Execute task: code, docs, integration |
| **AUDIT** | GLM-5.2 (big boy) | Review quality, fix issues, final artifact |

**Why This Works:**
- ✅ You paid for GLM subscription, so use it until it's gone
- ✅ DeepSeek V4 Flash as fallback (5M free tokens, then cheap)
- ✅ GLM-5.2 for audits only (quality assurance)
- ✅ Optimal: Use paid first, then fall back to free

**Quota Awareness:**
```
When GLM weekly quota < 80%: Use GLM-4.7 for BUILD
When GLM weekly quota 80-95%: Use GLM-4.7, prepare DeepSeek fallback
When GLM weekly quota > 95%: Switch to DeepSeek V4 Flash
```

**This pattern:**
- Reduces waste (use what you've paid for)
- Maintains quality (GLM-5.2 for complex audits)
- Applies to both Gentech VPS and Forge Desktop
- Validated: Jordan's explicit directive on GLM subscription usage

### Peak Hour Optimization
- **Z.AI GLM-5.2**: Use only for complex/coding work (build layer)
- **Z.AI GLM-4.7**: Default for routine automation (run layer)
- **Cost Impact**: 80-90% reduction by using GLM-4.7 for execution
- **Vision**: GLM-4V on Z.AI (not Ollama)

---

## 🤝 Key Operational Pattern: GitHub-Only Vault Access

**Forge works from GitHub directly, not the local VPS path.** The vault at `/root/vaults/gentech/` lives on the VPS and is only accessible to Gentech.

**CRITICAL — Handoff directory path:** Forge's wake-up protocol reads from `01-HANDOFFS/gentech-to-forge/<date>-forge-tasks.md`. The `build_queue_tick.py` writes to `01-HANDOFFS/gentech-to-forge/` (configured via HANDOFF_DIR env var). If handoffs aren't appearing for Forge, check this path first — the tick script was previously writing to `01-HANDOFFS/` while Forge was looking in `01-HANDOFFS/gentech-to-forge/` (fixed Jul 13, 2026).

**⚠️ SPLIT-BRAIN PITFALL (Aug 24, 2026):** The vault has TWO handoff trees — root `01-HANDOFFS/` AND mirror `Gentech/01-HANDOFFS/`. Forge's wake-up + the queue tick read the ROOT `01-HANDOFFS/gentech-to-forge/`. When newer task files were written to the MIRROR path only, Forge couldn't see them ("can't see everything"). **The root `01-HANDOFFS/gentech-to-forge/` is canonical for Forge.** When adding a Forge task, write it there (or ensure the mirror copy also lands in root). Sync via `ob sync` pushes both to Obsidian (Forge's sink).

```
Forge workflow:
  1. git pull from github.com/ProtoJay4789/gentech-vault
  2. Read 01-HANDOFFS/gentech-to-forge/<date>-forge-tasks.md for assigned tasks (auto-generated by queue tick)
  3. Work on tasks (builds, PRs, marketplace listings)
  4. git add, git commit, git push
  5. Morning digest picks up Forge's handoff
```

**CRITICAL — Build queue has DUAL representation:**
- `scripts/build_queue.json` is the **source of truth** (machine-readable, drives tick script)
- `Gentech/00-HQ/build-queue.md` is the **human-readable reference** (tick script does NOT read this)
- Adding a task to the markdown only does NOT make it appear in Forge's handoff
- Always edit JSON first, run `python3 build_queue_tick.py` to regenerate handoff files, then optionally sync the markdown
- Proven Jul 13, 2026: Vanito MV task added to markdown only; Forge never received it until JSON was updated

**Morning Digest Integration:** Daily Digest cron (11 AM ET) includes a "Forge Night Handoff" section that checks vault commits and reports what Forge completed overnight.

**Motto:** *"Forge builds, Gentech operates."*

## Spawning Dedicated Worker Profiles per Group (memory inherited)

When the operator wants **distinct agent identities per Telegram group** (e.g. a
dedicated Treasury worker, a dedicated Labs worker — each its own bot they can
place/remove independently), the pattern is **one Hermes profile per worker**,
NOT reusing the single multi-channel agent.

Each profile at `~/.hermes/profiles/<name>/` is fully isolated: config, skills,
cron, sessions, AND memory (`memories/MEMORY.md` + `USER.md`). To stand up a new
worker that already knows what the parent agent knows:

```bash
hermes profile create <name> --clone-all --clone-from gentech
```

- `--clone-all` = full copy of the source profile's state, **including the
  memory files**.
- `--clone-from <src>` = seed from a specific source profile (default: active).
- Result: new worker starts with the parent's exact memories (Jordan's
  preferences, vault layout, stack) but is an independent bot identity.

**Key caveat — memory is copied AT CREATION TIME.** If the parent gains new
memories after the clone, the new workers do NOT auto-follow. Re-run
`--clone-all` from the parent or `cp` the `memories/` files over for ongoing
sync. For a clean one-time swap this is fine.

**"Replace the agent, keep the memories":** `--clone-all --clone-from <parent>`
is exactly the flow — create the new worker seeded from the parent's brain, then
remove the old bot from the group (or retire its profile). The memories persist
in the new profile; the parent profile is untouched unless `hermes profile
delete` is run.

**What the operator must supply per worker:** a distinct Telegram bot token (via
BotFather) and the target group chat ID. Each profile wires its own bot to its
group in that profile's gateway config.

**Cost note:** N workers = N context windows + token budgets (vs the single-agent
multi-channel pattern which is cheaper). Only choose per-group workers when
separate identities/placement actually matter — e.g. Jordan replacing the bot in
a group with a fresh identity while keeping the accumulated memory.

## Coordination Patterns

### 1. Task Classification & Routing
```python
# Task complexity classification
def classify_task(task):
    if "simple" in task or "cron" in task:
        return "gentech_vps"  # GLM-4.5 Flash
    elif "coding" in task or "complex" in task:
        return "forge_desktop"  # GLM-5.2
    elif "general" in task:
        return "forge_deepseek"  # DeepSeek Flash
    else:
        return "gentech_simple"  # GLM-4.5 Flash
```

### 2. Vault-Based State Sharing
### Shared Files:
- `01-HANDOFFS/gentech-to-forge/<date>-forge-tasks.md` - **Auto-generated** Forge task list (every 30 min via queue tick, generated by build_queue_tick.py from scripts/build_queue.json)
- `01-HANDOFFS/<date>-jordan-items.md` - **Auto-generated** Jordan action items
- `scripts/build_queue.json` - **Canonical** build queue (single source of truth)
- `Gentech/00-HQ/soul.md` - Agent identities and coordination rules
- `11-Mess Hall/considerations.md` - Decision tracking

### Build Queue System
- **Queue Phase**: Gentech queues tasks during work hours
- **Execute Phase**: Forge processes complex tasks at home
- **Audit Phase**: Both systems verify results via vault consensus

### Platform-Tagged Queue (Jul 2026)

Every queue item gets a `platform` field that routes work to the right agent:

| Tag | Who | When |
|-----|-----|------|
| `desktop` | Forge | Only when PC is on (GPU, local builds, testing) |
| `cloud` | Gentech | 24/7 — VPS handles overnight |
| `either` | First available | Any agent can pick it up |
| `gentech` | Gentech only | Never routed to Forge |

The `build_queue_tick.py` script handles VPS-side scanning; Forge uses `forge-build-queue-processor` skill to filter by platform.

### Stale Duplicate Queue — Known Pitfall

**This has happened before (Jul 2026):** A stale file `scripts/gentech-queue-remote.json` was a Jul 11 duplicate of the main queue, causing routing confusion. When both files differ, tick scripts read the wrong one and Forge gets stale assignments.

**Rule:** `scripts/build_queue.json` is the **only** queue file. Delete any other `*queue*.json` files immediately on discovery. The tick script, Forge's wake-up, and the nightly maintenance all reference this single path.

### Vanito Cron Guard — Known Pitfall (Jul 2026)

**Vanito is unfamiliar with Hermes cron mechanics.** He can accidentally create recurring cron jobs during his sessions that generate paid API calls every N minutes, burning wallet balance silently.

**Real incident (Jul 13-14, 2026):** Vanito created a "Seedance KAGE rooftop check" cron job running every 10 minutes, generating $0.26 xAI Grok videos each time. Over ~36 hours it consumed $35-40 of the wallet before being discovered.

**Rule:** Before creating any cron job during a Vanito session, ALWAYS double-check with him:
> "This will create a recurring job that runs every [X minutes/hours] and costs money each time — is that what you want?"

**Also check:** After Vanito's session, run `cronjob(action='list')` to inspect for any jobs he may have created accidentally. Look for video/image generation prompts, short intervals (< 30 min), and unfamiliar job names.

### Overnight Workflow (Jul 2026)

Jordan's weekly schedule defines when each agent runs:

| Time (ET) | Who | Activity |
|-----------|-----|----------|
| Evening ~6-10:30 PM | Jordan + Forge (desktop) | Active development, builds, testing |
| ~10:30-11 PM | Handoff | Forge writes handoff to `01-HANDOFFS/forge-to-gentech/`, syncs vault |
| Midnight - 8 AM | Gentech (VPS) only | Overnight queue processing, brain backups, maintenance |
| Morning ~8-9 AM | Morning Digest delivered | Jordan wakes up to overnight report |

**Key constraint:** Gentech's overnight work only picks `platform: "cloud"` items. Desktop/GPU items sit until Forge is back on the PC. The nightly maintenance runs at 4 AM UTC (midnight ET) and the build queue tick runs every 30 min.

### Desktop Heartbeat Detection

Forge writes a timestamp every 5 min via `scripts/heartbeat.py`:
```bash
date +%s > /root/vaults/gentech/scripts/.desktop-heartbeat
```
Gentech's cloud instance reads this at wake-up. If heartbeat < 10 min old → desktop is on → route `desktop` items. If > 30 min old → desktop is off → skip `desktop` items.

### 4. Handoff Protocol

**Handoff Folder Pattern:**
```
01-HANDOFFS/
  ├── gentech-to-forge/<date>-forge-tasks.md     # Auto-generated Forge task list
  ├── <date>-jordan-items.md                      # Auto-generated Jordan action items
  └── <date>-<task>.md                             # Manual handoffs
```

**How Handoffs Work:**
1. **Sender creates handoff file** in `/handoffs/` with timestamp
2. **Sender runs `ob sync`** to push to vault remote
3. **Receiver syncs** via `ob sync` or git pull
4. **Wake-up protocol** automatically checks `/handoffs/` folder on session start
5. **Receiver sees handoff** and takes action

**Critical Distinction:**
- **Writing to vault** = passive (file exists locally)
- **"Sending"** = requires sync + receiver runs wake-up protocol

**When to Use Handoffs:**
- Jordan is away/off andForge needs context
- Switching between agents mid-task
- Session start with incomplete work
- Git sync issues or blocked operations

**Sync Fallback Pattern (CRITICAL):**
When Obsidian sync times out or fails, use git as the primary delivery method:
```bash
# Step 1: Commit handoff
cd /root/vaults/gentech
git add handoffs/forge-handoff-YYYY-MM-DD.md
git commit -m "Add Forge handoff — YYYY-MM-DD"
git push origin main

# Step 2: Receiver pulls
cd ~/vault/gentech
git pull origin main

# Step 3: Receiver runs wake-up protocol
# Handoff file is now available in /handoffs/
```

**Why this works:** Git push is fast and reliable (seconds), while Obsidian sync can time out at 120s. The vault repo is the source of truth for handoff delivery.

**Handoff File Template:**
```markdown
# <Agent> Handoff — YYYY-MM-DD

## Context
[Why this handoff exists: Jordan away, session switch, etc.]

---

## What <Sender> Built/Did
| Item | Status | Notes |
|------|--------|-------|
| | | |

---

## What <Sender> Did
| Task | Status |
|------|--------|
| | |

---

## Git Status Summary
[Vault status, portfolio status, any unpushed commits]

---

## Recent Work
[What was just completed or in progress]

---

## Build Queue Snapshot
[Top items from 00-HQ/build-queue.md]

---

## Blockers / Needs
[Anything blocking progress or requiring user action]

---

## Next Steps for <Receiving Agent>
[Specific actions to take]
```

---

## Implementation Checklist

### Phase 1: Desktop Setup
- [ ] Install Ollama + llama3.1:8b (128K context requirement)
- [ ] Configure DeepSeek Flash integration
- [ ] Set GLM 5.2 explicit fallback for coding
- [ ] Install Hermes CLI on desktop
- [ ] Set up Discord gateway for home access

### Phase 2: Coordination Layer
- [ ] Daily cron sync for cross-system coherence
- [ ] Memory sharing via vault file synchronization
- [ ] Working state sync between desktop/VPS
- [ ] Decision tracking automation

### Phase 3: Optimization
- [ ] Add explicit model routing to cron jobs
- [ ] Weekly DeepSeek token usage monitoring
- [ ] Peak-hour task scheduling
- [ ] Performance benchmarking

---

## Model Configuration

### DeepSeek Integration (Desktop)
```bash
# Free tier: 5M tokens
# Model: deepseek-v4-flash
# Provider: DeepSeek
# Context: 128K+ (compatible with Hermes)

# Monitoring usage
curl -s "https://api.deepseek.com/v1/usage" \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY"
```

### GLM 5.2 Fallback (Desktop)
```bash
# For complex/coding tasks
# Provider: Z.AI
# Model: glm-5.2
# Cost: Premium (use off-peak when possible)
```

### VPS Configuration (Gentech)
```bash
# Simple tasks
# Provider: Z.AI  
# Model: glm-4.5-flash
# Use for: cron jobs, simple automation

# Complex tasks
# Provider: Z.AI
# Model: glm-5.2
# Use for: audits, analysis, multi-step reasoning
```

---

## Success Metrics

### Performance Targets
- **Token Cost Reduction**: 60-80% for general tasks via DeepSeek
- **Quality Maintenance**: GLM 5.2 for complex analysis
- **Zero Context Loss**: Seamless vault-based coordination
- **System Uptime**: 24/7 operations via Gentech VPS

### Monitoring
- Weekly DeepSeek token usage reports
- Daily sync completion verification  
- Cost optimization tracking
- Performance benchmarking between systems

---

## Troubleshooting

### Common Issues
1. **Context Window Mismatch**: Ensure 128K+ context for all models
2. **Token Exhaustion**: Monitor DeepSeek 5M free tier weekly
3. **Sync Failures**: Verify vault file permissions and Git status
4. **Provider Limits**: Peak-hour avoidance for Z.AI costs
5. **Forge GitHub Vault Access Denied**: When Forge reports "private repo" despite having a GitHub token:
   - **Root cause:** Forge's GitHub account needs to be added as a collaborator on the repo — a PAT alone doesn't grant access to private repos unless the token's user is a collaborator or the token was created by the repo owner
   - **Fix:** Go to repo Settings → Collaborators → add Forge's GitHub username
   - **Verify on Forge's machine:** `gh auth status` then `git pull`
   - **Recommended auth method:** HTTPS + PAT with `repo` scope (full access to private repos). SSH requires key setup on each machine.
   - **Edge case:** If the vault remote URL has embedded credentials (owner's PAT in the URL), switch to a PAT for the collaborator account or add the owner's PAT through GitHub CLI instead

### Recovery Patterns
- **DeepSeek Exhausted**: Switch to GLM-5.2 for critical tasks
- **Z.AI Quota Limit**: Route to DeepSeek or pause non-critical tasks
- **Vault Sync Issues**: Force sync with `git pull --rebase` before push
- **Handoff Not "Sent"**: Creating a handoff file in vault is passive — it won't reach the receiver until:
  1. Vault syncs (`ob sync` or git push/pull)
  2. Receiver starts a session with wake-up protocol running
  - **Fix:** Explicitly mention sync status + wake-up protocol dependency in handoff
  - **CRITICAL FIX (July 6, 2026)**: Use `agent-to-agent-communication-audit` skill to verify handoff completeness before syncing
    - Checks for all required sections (Context, What Sender Built/Did, What Sender Did, Git Status Summary, Recent Work, Build Queue Snapshot, Blockers/Needs, Next Steps for Receiver)
    - Detects duplicate tasks against handoff history and current queue
    - Generates audit reports for failed handoffs
    - Bidirectional support: Gentech → Forge AND Forge → Gentech

---

## File Templates

### Handoff Template
`templates/handoff-template.md` — Reusable handoff structure for agent-to-agent coordination

### Implementation Plan Template
```yaml
title: Dual-Agent Implementation Plan
phase_1:
  - Ollama installation
  - DeepSeek configuration
  - GLM 5.2 fallback setup
phase_2:
  - Daily sync setup
  - Vault integration
  - Discord gateway
phase_3:
  - Model routing optimization
  - Performance monitoring
  - Cost analysis
```

---

*Created: June 29, 2026*
*Last Updated: July 23, 2026*
*Version: 3.0*

## 📋 Current Handoff System (Jul 27, 2026)

> **NEW (Aug 12): Group-to-group INBOX handoffs.** Jordan's preferred model —
> any agent drops a note into `01-HANDOFFS/INBOX/<group>/` for any group.
> Resolve = checkbox → `_archive/` → nightly purge >7d. Desktop Forge connects
> via **Obsidian Sync** (not a live socket); SETUP.md carries his onboarding.
> Full protocol, note template, reinstall pitfall ("restore local changes = No"):
> `references/group-inbox-handoff-system.md`.


The handoff system uses five files in `01-HANDOFFS/`:

| File | Who Writes | Who Reads | What |
|------|-----------|-----------|------|
| `01-HANDOFFS/for-the-forge.md` | Gentech | Forge | Current tasks to build |
| `01-HANDOFFS/from-the-forge.md` | Forge | Gentech | What got done |
| `01-HANDOFFS/forge-completions.md` | Forge | Gentech | Per-item completion reports |
| `01-HANDOFFS/gentech-to-forge/<date>-forge-tasks.md` | Queue tick | Forge | Auto-generated task list |
| `01-HANDOFFS/<date>-jordan-items.md` | Queue tick | Jordan | Auto-generated action items |

**Protocol doc:** `01-HANDOFFS/sync-protocol.md` — templates + full loop description.

**Known issues (Jul 27, fixed Aug 5):**
- `from-the-forge.md` — last updated Jul 25. Forge hasn't reported back since.
- `for-the-forge.md` — last updated Jul 25. No new tasks sent to Forge since.
- `02-HANDOFFS/forge-to-gentech/` — **dead directory**, only a README template. Do not use.
- `gentech-vault-new` — referenced in old sync protocol but **does not exist** on this machine. The vault is at `/root/vaults/gentech/` and syncs to `github.com/ProtoJay4789/gentech-vault.git` via remote named `vault`.

## 🔁 Symmetric All-Group Return Loop (Aug 5, 2026) — supersedes the Forge-only gap

The handoff system was one-directional (Gentech → group) and Forge-only for returns. That is now **fixed**. Every group agent has a symmetric return path, consumed overnight:

```
OUTBOUND:  Gentech → 01-HANDOFFS/gentech-to-<group>/   (dated task files, per group)
RETURN:    Group   → 01-HANDOFFS/<group>-to-gentech/   (dated "here's what I did" files)
                     <group>-completions.md            (item IDs shipped, e.g. "- **#42** — built X")
CONSUME:   python3 scripts/group-returns-scanner.py    (reads EVERY group return, extracts shipped IDs + notes)
           Nightly Build Session + Morning Digest crons consume the scanner JSON.
```

Groups with return folders: **labs, entertainment, treasury, hq, forge**.
(Consolidated Aug 12: "Strategies"/"Finance" were stale names for the Treasury
group `-1002916759037`. INBOX folders, config channel_prompts, and the scanner
GROUPS list all now use `treasury`.)

**The scanner** (`scripts/group-returns-scanner.py`) is the machine-readable consumer:
- Reads every `<group>-to-gentech/` folder + `<group>-completions.md`.
- Extracts `#<id>` tokens → `groups[].shipped_ids` (items the group completed) + `groups[].notes`.
- Emits JSON; the Nightly Build Session applies returned IDs to `build_queue.json` (status → shipped, notes group+date).
- **Idempotent:** only applies IDs that exist in the live queue (renumbered/stale IDs are ignored, not forced).
- Run it from the profile scripts dir: `python3 group-returns-scanner.py`. It's attached as a cron `script`, so its output auto-injects into the Nightly + Digest jobs — the agent acts on it, doesn't re-derive it.

**The old `tick_build_queue.py` + `forge-completions.md` Forge-only path still works** (kept for legacy), but the generalized scanner now covers it and the other groups.

**Deterministic gate (build vs maintain):** The Nightly Build Session computes
`python3 -c "...sum(1 for i in items if i.get('status')=='pending' and not i.get('needs_jordan'))"`.
count >= 1 → BUILD mode (ship 1-2 verified items). count == 0 → MAINTENANCE mode (ob sync, vault push, flesh ideas, infra health) — **never sit idle**.

**Stale-notes scanner:** `stale-notes-scanner.py` surfaces unaddressed brain items from `considerations.md`, `agent-brain/`, and `ideas.md` (older than threshold, still open) so the Morning Digest flags them to Jordan. Runs every night regardless of build lane.

### Forge = the desktop lane (Jordan's routing codeword, Aug 5)
"Forge only" is shorthand for **desktop only**. Forge runs on Jordan's PC, so anything that's easier done on the desktop routes to Forge **regardless of group**:
- MetaMask / wallet signing
- Browser logins + account actions (uphive wallet link, OKX, etc.)
- Local files / desktop-only tools / GPU work
- Opening a website Jordan has to see

When writing a handoff, if the task needs Jordan at a desktop, direct it to `gentech-to-forge/` (or note "Forge (desktop)" in the per-group note). Forge returns via `forge-to-gentech/` + `forge-completions.md`.

**Build queue tick script** (`scripts/build_queue_tick.py`) is read-only — it never writes the queue. It generates handoff files and prints a summary. The Nightly Build Session or manual edits mutate the queue.

**Arcade pipeline routing (Jul 27):**
| Phase | Who | What |
|-------|-----|------|
| Design | Gentech | text-to-cad maps, archetype specs, game concepts |
| Build | Forge | GPU-heavy work (Modly meshes, game logic, AI behavior) |
| Ship | Gentech | Three.js integration, arcade deployment, x402 wiring |

## 🚚 Forge Completion Protocol (Jul 23, 2026)

**Rule: Ship → Report → Next item. Don't wait until everything's done.**

Forge writes completed item IDs to `01-HANDOFFS/forge-completions.md` as each item finishes, not in batches. The build queue tick script reads this file and auto-updates the queue.

**Completion report format:**
```markdown
# Forge Completions — 2026-07-23
## Just shipped
- #59 GenTech Receipts
## Still working
- #62 Multi-Wallet Treasury — 60% done
## Blocked
- #65 OpenClaw Skill — need Q402 docs
```

**Why this matters:** The queue only stays accurate if completions are reported immediately. Batched reports mean stale queue numbers and missing context.

## 🔄 Architecture Pivot (July 2026)

### From Dual-Agent to Single-Agent Distributed Compute

**User Directive (Jordan, July 1, 2026):**
> "We're no longer doing an agent-to-agent system... it might just be better just to give you more power. You're still 24/7 on the VPS, but now you can connect to the home desktop."

**Old Architecture:**
```
Gentech VPS (Telegram) ──┐
                         ├── Vault Coordination (async)
Forge Desktop (Discord) ─┘
```

**New Architecture:**
```
Gentech VPS (24/7)
       ↓ Remote Gateway
Forge Desktop (compute offload)
```

### Key Changes

| Aspect | Old | New |
|--------|-----|-----|
| **Agent Count** | 2 agents | 1 agent (Gentech VPS) |
| **Coordination** | Bot-to-bot + vault | Direct access via gateway |
| **Model Routing** | Fixed per location | Dynamic: GLM ↔ Ollama Cloud |
| **Primary Benefit** | Specialized roles | Cost optimization + compute scale |
| **Complexity** | High (coordination overhead) | Medium (gateway setup) |

### User Preference
- **More power to single agent** rather than reprogramming multiple agents
- **Cost optimization**: Use Ollama Cloud (desktop) when GLM quota is high (75%)
- **Build queue offload**: Heavy compute to desktop
- **One brain, one decision-maker**

### Technical Implementation
See `references/vps-remote-gateway-implementation-jul-2026.md` for:
- Remote gateway options (Hermes Relay, Cloudflare Tunnel, SSH)
- VPS Task API design
- Model routing logic for distributed compute

---

### Session Updates (June 30, 2026)
- **CRITICAL FIX**: Added wake-up protocol recovery for missing BRIEFING.md file
- **NEW**: Created Forge-specific wake-up protocol for desktop development
- **NEW**: Added dual-agent router script for automatic agent detection
- **NEW**: Implemented Windows desktop deployment guide
- **ENHANCED**: Added comprehensive error handling and troubleshooting
- **ENHANCED**: Extended model routing with DeepSeek integration

### Session Updates (July 1, 2026)
- **MAJOR PIVOT**: Changed from dual-agent to single-agent distributed compute architecture
- **NEW**: Remote gateway implementation pattern for VPS → Desktop access
- **NEW**: Cost optimization routing (GLM quota ↔ Ollama Cloud)
- **NEW**: Orchestrator list management pattern (Jordan's action items vs Forge's task queue)
- **NEW**: 10-Labs/ as dedicated handoff workspace for Forge
- **UPDATED**: Forge's capabilities expanded to include content creation and analysis
- **UPDATED**: DM + vault coordination pattern finalized (no Discord needed for Forge)
- **UPDATED**: Cost-optimized model routing documented (GLM-5.2 for build, GLM-4.7 for run)

**Support Files Created:**
- `references/desktop-connect-vault-as-brain-aug-2026.md` - Desktop/Forge connect model (Aug 12 2026): Vault-as-brain NOT live link; desktop app pairing fails on current version; SETUP.md onboarding; "restore local changes = No"; update prep
- `references/dual-agent-wake-up-implementations-jun-2026.md` - Session implementation guide
- `references/vps-remote-gateway-implementation-jul-2026.md` - VPS Task API patterns (replaced by dashboard approach)
- `references/hermes-dashboard-remote-access-jul-2026.md` - Hermes Dashboard remote access via Cloudflare Tunnel
- `references/forge-dm-vault-coordination-jul-2026.md` - DM + vault-based Forge coordination pattern
- `references/forge-quick-commands.md` - Quick command reference for Forge
- `references/orchestrator-list-pattern-jul-2026.md` - Jordan's action items vs Forge's task queue pattern
- `forge-implementation-guide.md` - Windows desktop setup guide
- `forge-wake-up-protocol` skill - Forge-specific initialization
- `dual-agent-router.py` script - Automatic agent detection
- `forge-auto-wakeup.py` script - Forge wake-up sequence