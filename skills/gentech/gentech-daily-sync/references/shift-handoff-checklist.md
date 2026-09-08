# Shift Handoff Systematic Audit Checklist

Use this checklist when performing a comprehensive shift handoff or mid-shift coordination update.

## 📋 Pre-Handoff Setup
- [ ] Confirm current date, time, and shift context
- [ ] Identify handoff type (end-of-shift, mid-shift, daily sync)
- [ ] Determine delivery mode (silent run vs. active delivery)

## 🔍 Phase 1: Session History Review
```python
# Search for recent coordination sessions
sessions = await session_search("active projects hackathon deadlines ongoing work", limit=5)
```
- [ ] Review session summaries for project status updates
- [ ] Note any previously identified blockers or risks
- [ ] Check for handoff acknowledgments and deadline changes

## 📁 Phase 2: Vault File Scan
```bash
# Scan recent files (last 24h)
recent_files = scan_recent_vault_files(days=1, exclude_dirs=['.git','tmp','__pycache__'])
```
**Key files to read:**
- [ ] `11-Mess Hall/YYYY/W##/YYYY-MM-DD/today-context.md` (Active Discussions table)
- [ ] `11-Mess Hall/considerations.md` (checkbox items — primary blocker source)
- [ ] `09-Green Room/build-logs/2026-05-*.md` (recent build progress)
- [ ] `00-HQ/hackathon-tracker.md` (active hackathon deadlines)
- [ ] `11-Mess Hall/task-board.md` (sprint status, active priorities)
- [ ] `09-Green Room/ideas.md` (new ideas logged today)
- [ ] `11-Mess Hall/vault-audits/vault-sweep-YYYY-MM-DD.md` (latest sweep findings)

## ⚙️ Phase 3: System Health Verification
Always check operational status:
```bash
# Gateway service
systemctl --user status hermes-gateway.service

# Disk usage
df -h /

# Auth errors
journalctl --user -u hermes-gateway.service --no-pager -n 30
```
- [ ] Gateway running
- [ ] Disk usage < 85%
- [ ] No auth errors (Nous, OpenRouter)
- [ ] Cron jobs scheduled and running

## 🎯 Phase 4: Critical Blocker Identification
Categorize by severity:

**🔴 CRITICAL** (Require immediate action)
- Auth expired → all LLM ops blocked
- Hackathon deadlines < 3 days with incomplete work
- Toolchain failures preventing builds
- Portfolio sync broken (data drift, git auth issues)

**🟡 HIGH PRIORITY** (24-48 hours)
- IL breaches or LP position risks
- Missing API keys/credentials
- Stale vault data causing bad decisions (Working Memory > 5 days old)
- xurl auth not configured — blocks content distribution

**🟢 MONITOR** (Track, no immediate action)
- Stale configuration files
- Content drafts awaiting Jordan's review
- Build artifacts accumulating (vault bloat)

## 📊 Phase 5: Cross-Verification
Check multiple sources for consistency:
- [ ] Session history vs. current vault files
- [ ] Documented status vs. system state (file existence, git status)
- [ ] `task-board.md` vs. actual file modifications
- [ ] `considerations.md` checkbox status vs. actual progress

## 📝 Phase 6: Handoff Structure
Organize handoff with clear sections (as Jordan prefers):
1. **What Got Done** (shipped artifacts, completed builds)
2. **Still In Progress** (active builds, % complete, what's remaining)
3. **Blockers & Decisions Needed** (categorized by severity, direct action asks)
4. **Tomorrow's Priorities** (deadline-driven, sorted by urgency)
5. **Forward-Looking Hook** (warm, brief, "This is just the beginning...")

## ✅ Quality Assurance
- [ ] All critical blockers identified and flagged
- [ ] Clear ownership for each action item
- [ ] Deadline risks accurately assessed
- [ ] Report is skimmable (bullets, short sentences)
- [ ] Ends with forward-looking hook
- [ ] Silent run mode respected (if applicable)

## ⏱️ Time Efficiency
- **Initial scan complete:** < 60 seconds
- **Full handoff report:** < 3 minutes
- **Action items identified:** > 3 per audit

## 🚨 Escalation Protocol
Escalate to Jordan immediately if:
- [ ] Any critical blocker remains unaddressed after 2 hours
- [ ] Hackathon deadline < 3 days with major blockers
- [ ] Gateway FAILED or auth expired (blocks all operations)
- [ ] System health critical (disk >90%)

## 📚 Reference Materials
- `gentech-project-coordination` skill — systematic audit methodology
- `references/shift-handoff-format.md` — output template
- `references/vault-topology-2026-05.md` — vault structure

---
*Last updated: May 20, 2026 — solo operation restructuring (removed multi-agent references, updated vault paths to current structure, aligned section order with Jordan's preferred format).*