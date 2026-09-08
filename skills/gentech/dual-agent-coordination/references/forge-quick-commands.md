# Forge Quick Commands (Cheat Sheet)

**For Jordan (User) — DM Commands for Forge**

---

## Common Commands

### Assign Work
```
Forge, read your assignments
Forge, work on the next urgent task
Forge, start on the Cloudflare gateway setup
```

### Check Status
```
Forge, what's your current status?
Forge, what are you working on?
Forge, what's the build queue status?
```

### Update Progress
```
Forge, mark [task name] as complete
Forge, update progress on [task name]
Forge, skip to the next item
Forge, pause all work
Forge, resume work
```

### Redirect Work
```
Forge, focus on DeFi Intelligence API instead
Forge, switch to Agent Registration API
Forge, go back to Cloudflare setup
```

---

## Forge's Response Patterns

### Starting Work
```
Forge: "Reading assignments from 10-Labs/forge-assignments.md"
Forge: "Started Cloudflare gateway setup"
Forge: "Next: Audit existing API candidates"
```

### Progress Update
```
Forge: "Completed: Signed up for waitlist ✓"
Forge: "Working on: Audit existing APIs"
Forge: "Estimated: 3-5 hours total"
```

### Blocked
```
Forge: "BLOCKED: Need API documentation"
Forge: "Added blocker note to build queue"
Forge: "Waiting for your input"
```

### Completed
```
Forge: "Completed Cloudflare setup ✓"
Forge: "Updated build queue with checkboxes"
Forge: "Synced vault"
```

---

## File Locations

### Forge Reads
- `10-Labs/forge-assignments.md` — Current assignments
- `10-Labs/build-queue.md` — Strategic priorities

### Forge Updates
- `10-Labs/build-queue.md` — Updates checkboxes and notes

### Jordan Checks
```bash
cd /root/vaults/gentech && ob sync
cat 10-Labs/build-queue.md
```

---

## Sync Pattern

### After Major Changes
```bash
# Both agents sync after changes
cd /root/vaults/gentech
ob sync
```

### Jordan Checks Progress
```bash
# Sync first, then check
cd /root/vaults/gentech && ob sync
cat 10-Labs/build-queue.md
```

### Forge Syncs After Work
```bash
# After completing tasks or major progress
cd /root/vaults/gentech
ob sync
```

---

## Priority Order

### URGENT (This Week)
1. Cloudflare x402 Monetization Gateway Setup
2. Any time-sensitive revenue opportunities

### HIGH PRIORITY (Next 2 Weeks)
3. Agent Registration API
4. DeFi Intelligence API
5. Agent Search API

### MEDIUM PRIORITY (This Month)
6. Agent Fleet Monitor
7. Agent Starter Kit
8. Human Feedback API

---

## Checkbox Format

### Task Not Started
```markdown
- [ ] Sign up for waitlist
```

### Task In Progress
```markdown
- [x] Sign up for waitlist ✓
**Note:** Completed, moving to next step
```

### Task Complete
```markdown
- [x] Sign up for waitlist ✓
- [x] Audit existing APIs ✓
- [x] Design pricing structure ✓
```

---

## Common DM Patterns

### Simple Assignment
```
You:   "Forge, work on the next urgent task"
Forge: "Started Cloudflare setup, waitlist signed up ✓"
```

### Check Progress
```
You:   "Forge, what's your status?"
Forge: "Working on Cloudflare setup, completed: waitlist signup ✓"
Forge: "Next: Audit existing APIs"
```

### Redirect
```
You:   "Forge, switch to Agent Registration API instead"
Forge: "Switched to Agent Registration API, starting work"
```

### Blocker
```
Forge: "BLOCKED: Need API documentation"
Forge: "Added to build queue, waiting for your input"
You:   "Use mock data for now"
Forge: "Continuing with mock data approach"
```

---

## Troubleshooting

### Forge Not Responding
```
Check: Is Forge's Telegram running?
Fix:   Restart Forge's gateway

Check: Is vault accessible?
Fix:   Sync vault: ob sync

Check: Are there errors in assignments?
Fix:   Review 10-Labs/forge-assignments.md
```

### Progress Not Updating
```
Check: Did Forge sync vault?
Fix:   Tell Forge: "Forge, sync vault"

Check: Are you syncing your side?
Fix:   Run: cd /root/vaults/gentech && ob sync

Check: Git conflicts?
Fix:   Resolve merge conflicts manually
```

### Unclear Blockers
```
Check: Build queue notes
Fix:   Read: cat 10-Labs/build-queue.md

Ask Forge: "Forge, what's blocking you?"
Forge: "Blocked on: Need X approval"
```

---

## Quick Reference URLs

### Cloudflare Resources
- Waitlist: https://t.co/pvICtEIixj
- Dashboard: https://dash.cloudflare.com
- API Docs: https://developers.cloudflare.com

### x402 Resources
- Protocol: https://x402.org
- Foundation: https://x402.foundation

### Gentech Resources
- Vault: `/root/vaults/gentech/`
- Build Queue: `10-Labs/build-queue.md`
- Assignments: `10-Labs/forge-assignments.md`

---

## Success Indicators

### ✅ Work Flowing Well
- Checkboxes getting marked regularly
- Vault syncs happening every few hours
- Clear progress notes in files
- Forge responding to DMs within minutes
- No unclear blockers

### ❌ Work Stalled
- No checkbox updates in 24 hours
- No vault syncs in 12 hours
- Forge not responding to DMs for 2+ hours
- Vague blocker notes
- Build queue hasn't been synced

---

**Last Updated:** July 1, 2026  
**Related Files:**
- `references/forge-dm-vault-coordination-jul-2026.md` — Full pattern guide
- `dual-agent-coordination/SKILL.md` — Overall architecture
- `10-Labs/build-queue.md` — Current priorities
- `10-Labs/forge-assignments.md` — Current assignments