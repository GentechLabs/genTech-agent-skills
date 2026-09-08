# Build Queue Token Efficiency Template

**Purpose**: Standard format for build queue tasks with token cost tracking and Forge threshold rules.

---

## Task Template

```markdown
### XX. Task Name
**Status**: Just added — DEADLINE/NO DEADLINE
**Cost Estimate**: ~$X.XX (GLM-5.2, ~XXX,XXX tokens)
**Forge Threshold**: YES/NO (Complexity: Simple/Medium/Complex)
**Impact**: Brief impact statement
**Estimated Time**: X weeks
**Difficulty**: ⚠️ LEVEL (brief description)
**Why Now**: Brief justification

**Action Items**:

**Week 1: Phase** [BUILD: DeepSeek V4 Flash → AUDIT: GLM-5.2]
- [ ] Task 1
- [ ] Task 2

**Week 2: Phase** [BUILD: DeepSeek V4 Flash → AUDIT: GLM-5.2]
- [ ] Task 3
- [ ] Task 4

**Success Metrics**:
- Metric 1
- Metric 2
```

---

## Complexity Guide

| Complexity | Cost | Token Range | Model Route |
|------------|------|-------------|-------------|
| **Simple** | < $0.10 | < 50K tokens | DeepSeek V4 Flash only |
| **Medium** | $0.10-0.30 | 50K-200K tokens | DeepSeek V4 Flash → GLM-5.2 audit |
| **Complex** | $0.30-1.00 | 200K-800K tokens | DeepSeek V4 Flash → GLM-5.2 audit |

---

## Forge Threshold Rules

- **NO** = Jordan-only (strategic, outreach, hackathon submissions)
- **YES** = Forge/Gentech (technical builds, infrastructure, documentation)
- Jordan decides; Forge works on YES items when home (unless quick/inexpensive)

---

## Cost Estimation Examples

| Task | Complexity | Cost Estimate | Token Range |
|------|------------|---------------|-------------|
| Mission Control setup | Simple | $0.02-0.05 | 10K-40K |
| Travala MCP integration | Medium | $0.05-0.15 | 30K-120K |
| BNPL MVP | Complex | $0.30-0.80 | 200K-650K |
| 3D Visual Explorer | Complex | $0.25-0.60 | 150K-500K |

---

## Build First, Audit Last Protocol

| Phase | Model | Purpose |
|-------|-------|---------|
| **BUILD** | DeepSeek V4 Flash (or GLM-4.7) | Execute task: code, docs, integration |
| **AUDIT** | GLM-5.2 | Review quality, fix issues, final artifact |

**Why This Works:**
- ✅ 70% cost savings (cheap default + targeted audit)
- ✅ Quality assurance (GLM-5.2 big boy review)
- ✅ No blind escalation (audit only when needed)

---

**Created**: July 5, 2026
**Purpose**: Standard template for token-efficient build queue tasks