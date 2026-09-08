# Two-Phase Build Pattern

*Developed: June 27, 2026*

---

## The Pattern

```
Phase 1: BUILD (Local Qwen) → Fast, free, gets it working
Phase 2: AUDIT (GLM-5.2) → Quick review, polish, production quality
```

**Why:** Local builds fast and free. GLM-5.2 ensures production quality. Best of both worlds.

---

## Cost Comparison

| Approach | Cost per Task | Quality |
|----------|---------------|---------|
| GLM-5.2 only | $1.40 | High |
| Local only | $0.00 | Medium |
| **Two-Phase** | **$0.07** | **High** |

**Savings:** 95% cheaper than GLM-5.2 doing everything

---

## What Each Phase Does

### Phase 1: Build (Local Qwen)
- Write the code
- Make it functional
- Basic error handling
- Get it working

### Phase 2: Audit (GLM-5.2)
- Review for production quality
- Add missing error handling
- Check edge cases
- Security review
- Performance optimization
- Code style consistency
- Add type hints
- Add documentation

---

## What GLM-5.2 Audit Catches

- ⚠️ Missing error handling
- ⚠️ Edge cases not covered
- ⚠️ Security issues (eval/exec, hardcoded secrets, SQL injection)
- ⚠️ Performance problems
- ⚠️ Code style inconsistencies
- ⚠️ Missing type hints
- ⚠️ Documentation gaps

---

## Audit Queue System

**Problem:** GLM-5.2 rate limits prevent immediate audits.

**Solution:** Queue audits and run when limits clear.

```
Build Complete → Add to Audit Queue → Wait for Rate Limit Clear → Run Audit → Deploy
```

### Audit Queue File
Location: `10-Labs/audit-queue.md`

### Queue Management
1. **After local build** → Add task to `Pending Audits` table
2. **When rate limits clear** → Process queue in priority order
3. **After audit** → Move to `Completed Audits` table
4. **If audit fails** → Log issue, retry when available

### Integration with Deploy and Verify
- **Deploy and Verify** → Handles post-audit deployment
- **Vault Maintenance** → Logs build/audit status
- **Session Startup** → Reads audit queue on wake-up

---

## Implementation

### For Build Queue
1. Route simple/medium tasks to local Qwen
2. After build completes, route code to GLM-5.2 for audit
3. Apply audit fixes
4. Deploy with deploy-and-verify skill

### For Cron Jobs
- Maintenance tasks: Local only (no audit needed)
- Analysis tasks: GLM-5.2 only (no build phase)
- Code generation: Two-phase pattern

---

## Quick Reference

### Run Local Build
```bash
ollama run qwen2.5-coder:7b
# Ask it to write the code
```

### Audit with GLM-5.2
```python
# After local build completes
audit_prompt = f"""
Review this code for production quality:
{code}

Check for:
- Error handling
- Edge cases
- Security
- Performance
- Documentation

Provide fixed version.
"""
```

---

## Benefits

- ✅ **Speed** — Local handles the heavy lifting
- ✅ **Quality** — GLM-5.2 ensures production code
- ✅ **Cost** — 95% cheaper than GLM-5.2 doing everything
- ✅ **Rate limits** — Audits are quick, don't hit limits
- ✅ **Scalability** — Can run multiple builds in parallel locally

---

## User Preference

**Jordan (Jun 27, 2026):** "add that to the audit list for 5.2 for GLM. So that way, even if it's being coded by a smaller model, it still gets the love that it needs."

**Jordan (Jun 27, 2026):** "just a quick audit, just to make it look snappy, make it look good, you know, nothing crazy."

---

*"Two-phase build: Local builds fast, GLM-5.2 makes it production-ready."*
