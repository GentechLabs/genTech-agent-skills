# Forge Compliance Checklist — Build Queue Execution Protocol

**Purpose**: Verify Forge (desktop app) is following token-efficient BUILD → AUDIT workflow when executing build queue tasks.

---

## 🔍 Compliance Checklist

### Build Queue Tasks
- [ ] Do you BUILD with DeepSeek V4 Flash (or GLM-4.7 if DeepSeek unavailable)?
- [ ] Do you AUDIT with GLM-5.2 after building?
- [ ] Do you check Forge Threshold before starting tasks (NO = Jordan-only, YES = Forge/Gentech)?
- [ ] Do you estimate token costs per task following complexity guide?

### Protocol Adherence
- [ ] Are you following `00-HQ/workflow-local-first.md` (Build First, Audit Last)?
- [ ] Are you using `00-HQ/build-queue.md` cost estimates?
- [ ] Are you reading `10-Labs/forge-assignments.md` for priorities?
- [ ] Are you syncing vault after task completion?

### Desktop App Specifics
- [ ] Are you using PowerShell instead of bash?
- [ ] Are you using Windows paths (`C:\Users\jhitm\`) instead of `/root/`?
- [ ] Are you handling model routing via desktop app config?
- [ ] Are you avoiding VPS-only skills (cron, watchers)?

---

## 📋 Expected Response Format

```markdown
## Compliance Status
- Build Queue Execution Protocol: YES/NO
- Token Efficiency Routing: YES/NO
- Desktop App Specifics: YES/NO

## Current Setup
- BUILD model: [model name]
- AUDIT model: [model name]
- Vault location on Windows: [path]
- Model routing enabled: YES/NO

## Blockers or Issues
- [Any blockers or protocol violations]
```

---

## ⚙️ Build Queue Execution Protocol

**Rule: Build First, Audit Last**

| Phase | Model | Purpose |
|-------|-------|---------|
| **BUILD** | DeepSeek V4 Flash (or GLM-4.7) | Execute task: code, docs, integration |
| **AUDIT** | GLM-5.2 | Review quality, fix issues, final artifact |

**Workflow**:
```
1. BUILD TASK (cheapest capable model)
   → Execute task
   → Output: draft artifact

2. AUDIT TASK (GLM-5.2)
   → Review draft
   → Fix issues
   → Output: final artifact
```

**Why This Works:**
- ✅ 70% cost savings (cheap default + targeted audit)
- ✅ Quality assurance (GLM-5.2 big boy review)
- ✅ No blind escalation (audit only when needed)

---

## 💰 Token Efficiency Tracking

**Every build queue task includes:**
- **Cost Estimate**: $X.XX (GLM-5.2, ~XXX,XXX tokens)
- **Forge Threshold**: YES/NO (Complexity: Simple/Medium/Complex)

**Forge Threshold Rules:**
- **NO** = Jordan-only (strategic, outreach, hackathon submissions)
- **YES** = Forge/Gentech (technical builds, infrastructure, documentation)
- Jordan decides; Forge works on YES items when home (unless quick/inexpensive)

**Complexity Guide:**

| Complexity | Cost | Token Range | Model Route |
|------------|------|-------------|-------------|
| **Simple** | < $0.10 | < 50K tokens | DeepSeek V4 Flash only |
| **Medium** | $0.10-0.30 | 50K-200K tokens | DeepSeek V4 Flash → GLM-5.2 audit |
| **Complex** | $0.30-1.00 | 200K-800K tokens | DeepSeek V4 Flash → GLM-5.2 audit |

---

## 🖥️ Desktop vs VPS Differences

| VPS (Linux) | Desktop (Windows) |
|-------------|-------------------|
| Bash/sh commands | PowerShell commands |
| `/root/` paths | `C:\Users\jhitm\` paths |
| Cron jobs | Desktop app scheduler |
| Background processes | App lifecycle |

**Model Routing**: Platform-agnostic — same BUILD → AUDIT pattern works on both.

**Skills That Work on Both**:
- ✅ `hermes-model-routing/` (Configuration only)
- ✅ `identity/` (Pure behavioral rules)
- ✅ `memory/` (File operations platform-agnostic)
- ✅ `research/*` (Web-based)

---

## 📂 Reference Documents

- `00-HQ/build-queue.md` — Token efficiency tracking + execution protocol
- `00-HQ/workflow-local-first.md` — Build first, audit last pattern
- `00-HQ/desktop-compatibility-guide.md` — VPS vs desktop differences
- `00-HQ/forge-compliance-check-2026-07-05.md` — Full compliance check document
- `10-Labs/forge-assignments.md` — Current assignments + reading routine

---

**Created**: July 5, 2026
**Purpose**: Session-specific verification pattern for Forge protocol compliance