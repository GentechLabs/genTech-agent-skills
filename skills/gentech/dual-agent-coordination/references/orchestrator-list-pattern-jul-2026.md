# Orchestrator List Pattern — Jordan vs Forge Coordination

**Created:** July 1, 2026
**Purpose:** Clear separation between Jordan's action items and Forge's task queue

---

## Pattern Overview

### Two Lists, Two Owners

| List | Location | Owner | Purpose |
|------|----------|-------|---------|
| **Orchestrator List** | `10-Labs/jordan-orchestrator-list.md` | Jordan | Jordan's personal action items |
| **Build Queue** | `10-Labs/build-queue.md` | Forge | Forge's strategic task queue |

### Jordan's Orchestrator List Structure

```
## ⚡ Quick Wins (5-10 min)
1. [ ] Cloudflare Security Headers — Configure on gentechlabs.net (5 min)
2. [ ] Agenstry.com — Submit URL (2 min)
3. [ ] x402-list.com — Submit form (3 min)

## 🔧 Medium Tasks (15-30 min)
4. [ ] a2alist.ai — Submit + $0.99 (10 min)
5. [ ] a16z Speedrun — Sign up (10 min)

## 🎯 Priority Projects (1-2 hrs)
6. [ ] Bankr $100K — Apply (30 min)
7. [ ] Virtuals ACP — Create agent (1 hr)

## 🚀 Big Builds (2+ hrs)
8. [ ] Cloudflare x402 Monetization Gateway Setup (3-5 hrs) — IN PROGRESS
```

### Forge's Build Queue Structure

```
## 🔥 URGENT (This Week)
### 1. Cloudflare x402 Monetization Gateway Setup
**Status**: Ready to start
**Action Items**:
- [x] Sign up for Cloudflare Monetization Gateway waitlist
- [ ] Audit existing API candidates
- [ ] Design pricing structure

## 🟡 HIGH PRIORITY (Next 2 Weeks)
### 2. Agent Registration API
### 3. DeFi Intelligence API
### 4. Agent Search API
```

---

## Why This Separation Matters

### Jordan's Orchestrator List:
- **Human-executable tasks** (form submissions, reviews, approvals)
- **Quick wins** (5-10 min) → build momentum
- **Time-ordered** (easy → hard)
- **Personal productivity** (what Jordan should do)

### Forge's Build Queue:
- **Agent-executable tasks** (coding, building, deploying)
- **Revenue-focused** (APIs, infrastructure)
- **Priority-ordered** (URGENT → HIGH → MEDIUM)
- **Strategic execution** (what builds business value)

---

## Coordination Pattern

### When Jordan Asks "What should I do?":

1. **Agent pulls orchestrator list** → `cat 10-Labs/jordan-orchestrator-list.md`
2. **Filters by available time** → "You have 30 min? Here are 3 quick wins"
3. **Suggests order** → "Start with Security Headers, then Agenstry"
4. **Marks complete** → Jordan updates checkboxes

### When Jordan Assigns to Forge:

1. **DM command** → "Forge, work on the next urgent task"
2. **Forge reads build queue** → `cat 10-Labs/build-queue.md`
3. **Forge executes** → Builds, codes, deploys
4. **Forge updates** → Marks checkboxes, adds progress notes
5. **Forge syncs** → `ob sync`
6. **Forge reports** → DM: "Working on Cloudflare setup ✓"

---

## Handoff Workspace: 10-Labs/

All coordination files live in `10-Labs/`:

```
10-Labs/
├── build-queue.md              # Forge's strategic task queue
├── forge-assignments.md        # Current assignments + protocol
├── forge-quick-start.md        # Quick command reference
├── jordan-orchestrator-list.md # Jordan's action items
├── local-hermes-discord-setup.md  # Discord setup (for Gentech, not Forge)
└── active-projects/            # Project-specific work
```

---

## Success Indicators

### Work is Flowing When:
- ✅ Jordan's orchestrator list checkboxes getting marked
- ✅ Forge's build queue checkboxes getting marked
- ✅ Vault syncs happening regularly
- ✅ Clear progress notes in files
- ✅ Blockers communicated immediately

### Work is Stalled When:
- ❌ No checkbox updates in 24 hours
- ❌ No vault syncs in 12 hours
- ❌ Unclear blockers
- ❌ No progress notes
- ❌ Agent not responding to DMs

---

## DM Communication Pattern

### Jordan → Forge Commands:
```
Forge, read your assignments
Forge, work on the next urgent task
Forge, what's your current status?
Forge, mark [task name] as complete
```

### Forge → Jordan Reports:
```
Working on Cloudflare gateway setup
Completed: Signed up for waitlist ✓
Next: Audit existing API candidates
Blocked on: Need API documentation
Estimated: 3-5 hours total
```

---

## Best Practices

### For Jordan:
- ✅ Keep strategic decisions in HQ files
- ✅ Let Forge focus on execution (Labs)
- ✅ Check progress via vault sync, not constant DMs
- ✅ Approve pivots quickly when Forge is blocked
- ✅ Sync vault before reviewing progress

### For Forge:
- ✅ Always read assignment file first
- ✅ Never skip items without approval
- ✅ Mark blockers immediately
- ✅ Sync vault after significant changes
- ✅ Report major milestones in DM

---

## Benefits Over Group-Based Coordination

### Problem with Groups:
- ❌ Multiple agents in same channel → confusion
- ❌ Chat history gets long → hard to track
- ❌ No persistent state → progress gets lost
- ❌ Requires group membership → permission management

### Benefits of DM + Vault:
- ✅ Clear responsibility → DM is 1:1
- ✅ Persistent state → Vault files always available
- ✅ Progress tracking → Checkboxes and notes
- ✅ No group chaos → Each agent in own DM
- ✅ Vault as truth → Single source of state
- ✅ Can sync later → No immediate pressure

---

**Key Insight:** Vault becomes the "shared brain" - single source of truth for state, assignments, and progress.