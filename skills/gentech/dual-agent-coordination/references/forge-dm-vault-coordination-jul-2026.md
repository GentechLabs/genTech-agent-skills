# Forge DM + Vault Coordination Pattern

**Created:** July 1, 2026  
**Updated:** July 13, 2026 — Added build queue dual-representation note
**Context:** User decided not to add Forge to Telegram groups; instead use DM + vault-based task assignment

---

## ⚠️ CRITICAL UPDATE (July 13, 2026): Build Queue Now Has Dual Representation

This reference document was written before the build queue was migrated to a dual-representation system. The following corrections apply:

- **`10-Labs/build-queue.md`** is now the **human-readable markdown reference only**. It is NOT read by any automation.
- **`scripts/build_queue.json`** is the **canonical source of truth** for all task automation.
- **`01-HANDOFFS/<date>-forge-tasks.md`** is the **auto-generated Forge task list** produced by `build_queue_tick.py` every 30 minutes.
- Forge should read `01-HANDOFFS/<date>-forge-tasks.md` (the latest dated file), NOT `10-Labs/build-queue.md`.
- Changes to the markdown queue alone will NOT reach Forge. Always update the JSON first, run the tick script, then sync git.

## ⚠️ Multi-Remote Vault Sync — Known Pitfall (Jul 2026)

The vault at `/root/vaults/gentech/` has **four remotes**:

| Remote | URL | Purpose |
|--------|-----|---------|
| `origin` | `ProtoJay4789/ProtoJay4789.github.io.git` | Portfolio site (default push target) |
| `hub` | `ProtoJay4789/ProtoJay4789.github.io.git` | Same as origin (legacy) |
| `vault` | `ProtoJay4789/gentech-vault.git` | **Forge's push target** |
| `desmonds` | `ProtoJay4789/desmonds-working-progress-...` | Desmonds project (unrelated) |

**The problem:** Forge pushes to `vault/main` (gentech-vault repo), but Gentech's default `origin` points to `ProtoJay4789.github.io`. When Forge's commit `83733b7c` landed only on `vault/main`, Gentech couldn't see it via `git pull origin main`. The files existed on GitHub but not in the local working tree.

**Recovery workflow:**
```bash
# 1. Fetch the vault remote
git fetch vault

# 2. Check if Forge's commit is there
git log --oneline vault/main -5

# 3. Merge it in (may hit conflicts if both agents edited the same files)
git merge vault/main

# 4. Resolve any conflicts, then push to BOTH remotes
git push origin main
git push vault main
```

**Prevention:**
- Gentech should run `git fetch --all` at session start to catch any remote-specific commits
- Forge should push to BOTH remotes, not just `vault`
- The `ob sync` command should push to all remotes, not just `origin`

**Detection:** If Forge reports files committed but Gentech can't find them, check `git remote -v` and `git branch -r` to see which remotes have new commits.

## Problem Statement

**User Preference (Jordan, July 1, 2026):**
> "I'm not going to have to add him to any groups. I'll just talk to him as like a normal DM, and I'll tell him like you could put the build list inside of one of the folders, right? So we could have it be in labs, and then put build list or build queue, and he can run it via that. Or we can have some type of communication layer via the vaults, since he'll see it."

**Challenge:**
- Multiple agents (Gentech VPS + Forge Desktop) need to coordinate
- Don't want group chaos (multiple agents in same Telegram channels)
- Need clear assignment, execution, and progress tracking
- Vault should serve as shared state layer

---

## Solution: DM + Vault Coordination

### Architecture

```
Jordan (User)
   ↓ DM
Forge (Desktop Agent)
   ↓ Reads/Writes
Vault Files (Shared State)
   ↑ Synced
Gentech VPS Agent
   ↓ Updates
Vault Files
```

**Key Insight:** Vault becomes the "shared brain" - single source of truth for state, assignments, and progress.

---

## Vault Structure

### Primary Coordination Files

```
10-Labs/
├── build-queue.md              # Strategic priorities
├── forge-assignments.md        # Current active assignments  
├── forge-quick-start.md        # Quick reference guide
└── active-projects/            # Project-specific work
    ├── cloudflare-gateway/
    │   ├── setup-notes.md
    │   └── deployment-steps.md
    ├── agent-registration-api/
    └── defi-intelligence-api/
```

---

## Communication Protocol

### Jordan → Forge (DM Commands)

```
Forge, read your assignments
Forge, work on the next urgent task
Forge, what's your current status?
Forge, mark [task name] as complete
Forge, skip to the next item
Forge, pause all work
Forge, resume work
```

### Forge → Jordan (DM Reports)

```
Working on Cloudflare gateway setup
Completed: Signed up for waitlist ✓
Next: Audit existing API candidates
Blocked on: Need API documentation
Estimated: 3-5 hours total
```

### Vault Sync (Both Agents)

```bash
# After major changes
cd /root/vaults/gentech
ob sync
```

---

## Assignment Lifecycle

### Step 1: Create/Update Task
```markdown
### 1. Cloudflare x402 Monetization Gateway Setup
**Status**: Ready to start
**Priority**: URGENT

**Action Items**:
- [ ] Sign up for waitlist
- [ ] Audit existing APIs
- [ ] Design pricing structure
```

### Step 2: Assign to Forge
```
Jordan: "Forge, read your assignments"
Forge: Reads `10-Labs/forge-assignments.md`
Forge: Reads `10-Labs/build-queue.md`
```

### Step 3: Forge Executes
```
Forge: Sees URGENT task #1
Forge: Starts working on it
Forge: Updates progress in build queue
Forge: Syncs vault: ob sync
```

### Step 4: Progress Tracking
```bash
# Jordan checks progress
cd /root/vaults/gentech && ob sync
cat 10-Labs/build-queue.md

# Sees updated checkboxes and notes
- [x] Sign up for waitlist ✓
- [ ] Audit existing APIs (in progress)
```

### Step 5: Completion
```
Forge: Marks task as complete
Forge: Updates file: - [x] Design pricing structure
Forge: Syncs vault
Forge: Reports in DM: "Completed Cloudflare setup ✓"
```

---

## File Templates

### forge-assignments.md
```markdown
# Forge Agent Assignments

## 🎯 Current Assignment

### 📋 Build Queue Execution
**File**: 10-Labs/build-queue.md
**Status**: Active
**Priority**: URGENT (Cloudflare x402 Gateway Setup)

**Instructions**:
1. Read the build queue from `10-Labs/build-queue.md`
2. Work on items in priority order: URGENT → HIGH → MEDIUM
3. Mark items as complete with `- [x]` checkboxes
4. Add progress notes under each task
5. Sync vault after changes: `ob sync`

## 💬 Communication Protocol

**Trigger commands for Forge:**
- "Forge, read the build queue"
- "Forge, work on the next urgent task"
- "Forge, what's the build queue status?"
- "Forge, mark Cloudflare setup as complete"

**Communication style:** Vault-first, DM-second. Forge reads queue, executes, updates file, you sync vault to see progress.
```

### build-queue.md
```markdown
# Build Queue — Priority Execution

## 🔥 URGENT (This Week)

### 1. Cloudflare x402 Monetization Gateway Setup
**Status**: Ready to start
**Estimated Time**: 3-5 hours

**Action Items**:
- [x] Sign up for Cloudflare Monetization Gateway waitlist
- [ ] Audit existing API candidates:
  - Agent Registration API (ERC-8004)
  - DeFi Intelligence API (BlockRun data)
  - Agent Search API (unified search)
- [ ] Design pricing structure
- [ ] Configure Cloudflare access policies

**Success Criteria**:
- 3 APIs available via Cloudflare Gateway
- x402 payments working in sandbox
- Documentation for agent buyers

## 🤖 Forge Integration

How Forge should process this queue:

1. **Read this file** from `10-Labs/build-queue.md`
2. **Prioritize by status**: URGENT → HIGH → MEDIUM
3. **Work top-down**: Complete all items in a section before moving down
4. **Update checkboxes**: Mark `- [x]` when done
5. **Report progress**: Update the file with brief notes under each task
6. **Sync vault**: Run `ob sync` after changes
```

---

## Best Practices

### For Jordan (User)
- ✅ Keep strategic decisions in HQ files
- ✅ Let Forge focus on execution (Labs)
- ✅ Check progress via vault sync, not constant DMs
- ✅ Approve pivots quickly when Forge is blocked
- ✅ Sync vault before reviewing progress

### For Forge (Agent)
- ✅ Always read assignment file first before starting work
- ✅ Never skip items without explicit approval
- ✅ Mark blockers immediately in notes with clear description
- ✅ Sync vault after every significant change
- ✅ Report major milestones in DM (don't wait for sync check)

### For Both Agents
- ✅ Always sync vault after changes: `ob sync`
- ✅ Use checkboxes for progress tracking: `- [ ]` vs `- [x]`
- ✅ Add clear notes under tasks: "Started X, completed Y, blocked by Z"
- ✅ Maintain single source of truth: vault files, not chat history

---

## Blocker Protocol

### When Forge Hits a Blocker

**Forge should:**
1. Mark in build queue: `"BLOCKED: Need X"`
2. Add specific note: `"Waiting for Jordan approval for Y"`
3. Sync vault: `ob sync`
4. Report in DM: `"Blocked on X - added to build queue"`

**Example:**
```markdown
### 1. Cloudflare Setup
**Status**: BLOCKED - Waiting for API documentation

**Action Items**:
- [x] Sign up for waitlist ✓
- [x] Audit existing APIs ✓
- [ ] Design pricing structure
**Note:** BLOCKED: Need API documentation for DeFi Intelligence API - waiting for Jordan to provide docs
```

### When Jordan Sees a Blocker

**Jordan should:**
1. Review the blocker in vault file
2. Provide solution or approval in DM: `"Forge, continue with workaround: use mock data for pricing"`
3. Forge resumes work
4. Forge updates file to remove blocker

---

## Example Workflow

### Full Cycle Example

**Step 1: Jordan Assigns Work**
```
Jordan: "Forge, work on the next urgent task"
```

**Step 2: Forge Reads Assignments**
```bash
Forge reads: 10-Labs/forge-assignments.md
Forge reads: 10-Labs/build-queue.md
Forge sees: Cloudflare setup is #1 URGENT
```

**Step 3: Forge Starts Work**
```bash
Forge starts: Cloudflare x402 Gateway Setup
Forge completes: Sign up for waitlist
Forge updates: - [x] Sign up for waitlist ✓
Forge adds note: "Completed waitlist signup via https://t.co/pvICtEIixj"
```

**Step 4: Forge Syncs and Reports**
```bash
Forge syncs: ob sync
Forge reports: "Started Cloudflare setup, waitlist signed up ✓"
```

**Step 5: Jordan Reviews Progress**
```bash
Jordan syncs: cd /root/vaults/gentech && ob sync
Jordan reads: cat 10-Labs/build-queue.md
Jordan sees: - [x] Sign up for waitlist ✓
```

**Step 6: Jordan Approves Next Step**
```
Jordan: "Good progress! Continue with the API audit"
```

**Step 7: Forge Continues**
```bash
Forge continues: Audit existing API candidates
Forge updates progress notes
Forge syncs vault
```

---

## Benefits Over Group-Based Coordination

### Problem with Group-Based:
- ❌ Multiple agents in same channel → confusion over who responds
- ❌ Chat history gets long → hard to track progress
- ❌ No persistent state → progress gets lost
- ❌ Requires group membership → permission management

### Benefits of DM + Vault:
- ✅ Clear responsibility → DM is 1:1
- ✅ Persistent state → Vault files are always available
- ✅ Progress tracking → Checkboxes and notes are clear
- ✅ No group chaos → Each agent works in own DM
- ✅ Vault as truth → Single source of state
- ✅ Can sync later → No immediate pressure to check

---

## Status Checks

### Check Forge's Status
```bash
# What is Forge working on?
cat 10-Labs/forge-assignments.md

# What's in the build queue?
cat 10-Labs/build-queue.md

# What's the priority order?
grep -A 2 "URGENT\|HIGH\|MEDIUM" 10-Labs/build-queue.md
```

### Check Specific Project
```bash
# How's Cloudflare setup going?
cat 10-Labs/active-projects/cloudflare-gateway/setup-notes.md
```

### Check Progress Over Time
```bash
# See recent changes
cd /root/vaults/gentech
git log --oneline --since="1 day ago" 10-Labs/

# Show differences
git diff HEAD~1 10-Labs/build-queue.md
```

---

## Success Indicators

### Work is Flowing When:
- ✅ Build queue checkboxes getting marked regularly
- ✅ Vault syncs happening regularly (every few hours)
- ✅ Clear progress notes in files
- ✅ Blockers communicated immediately in both DM and vault
- ✅ Jordan reviews progress via vault sync, not constant DMs

### Work is Stalled When:
- ❌ No checkbox updates in 24 hours
- ❌ No vault syncs in 12 hours
- ❌ Unclear blockers (vague notes)
- ❌ No progress notes under tasks
- ❌ Forge not responding to DMs for 2+ hours
- ❌ Build queue hasn't been synced recently

---

## Related Files

- `dual-agent-coordination` skill — Overall architecture
- `gentech-ops` skill — Operational workflows
- `10-Labs/build-queue.md` — Strategic priorities
- `10-Labs/forge-assignments.md` — Current assignments
- `10-Labs/forge-quick-start.md` — Quick reference

---

**Next Steps:**
1. Create `10-Labs/` structure if it doesn't exist
2. Set up `build-queue.md` with current priorities
3. Create `forge-assignments.md` with communication protocol
4. Create `forge-quick-start.md` for quick reference
5. Test with one task to validate workflow
6. Adjust patterns based on actual usage