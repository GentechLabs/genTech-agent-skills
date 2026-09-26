---
name: model-optimized-cron-config
description: "Two-tier model routing: DeepSeek V4 Flash (OpenCode Go) for routine runs, GLM-5.2 (OpenCode Go) for audits/builds. Nous Research fallback. Jordan sets provider — don't change without his say-so."
tags: [cron, model-optimization, cost-efficiency, agent-kit, devops]
trigger: "When creating or updating cron jobs, or when concerned about AI token usage in automated workflows."
related_skills:
  - ../auto-fix-preflight/SKILL.md  # verification layer for cron jobs
  - ../cron-truth-layer/SKILL.md    # data verification layer
  - ../code-audit-protocol/SKILL.md # develop-and-verify pattern
version: 1.2.0
author: Gentech Labs
---

# Model-Optimized Cron Configuration

## The Problem

Using the same powerful model for both building AND running cron jobs wastes tokens. Complex models (GLM-5.2) are expensive, while routine automated tasks don't need that power.

## Dual-Agent Gateway Setup

Gentech (VPS) and Forge (Desktop) use the same model stack through different gateways:

| Agent | Gateway | Models | Hardware |
|-------|---------|--------|----------|
| 🖥️ **Gentech** (VPS) | OpenCode Go | DS V4 Flash + GLM-5.2 | Cloud |
| 🛠️ **Forge** (Desktop) | Ollama Cloud | DS V4 Flash + GLM-5.2 | RTX 3070 + Cloud |
| 🔄 Both | Nous Research (fallback) | — | Only if primary gateways down |

**Do NOT mix gateways** — Gentech uses OpenCode Go, Forge uses Ollama Cloud. Each agent has one primary gateway for both models.

## The Solution

**Two-tier model strategy (current as of Jul 2026):**
- **Build/Audit Layer**: Use GLM-5.2 via OpenCode Go (Gentech) or Ollama Cloud (Forge) for creating cron jobs and auditing results (high-value, occasional)
- **Run Layer**: Use DeepSeek V4 Flash via OpenCode Go (Gentech) or Ollama Cloud (Forge) for routine cron execution (cost-efficient)

**⚠️ Provider/model routing is set by Jordan. Do NOT change routing without his explicit say-so. Jordan announces changes — don't switch without confirmation.**

**Fallback chain:** If OpenCode Go is down, fail over to Nous Research. No other fallbacks configured.

## When to Use Each Model

### GLM-5.2 (The "Coding Beast") - Build Layer Only

**Use for:**
- Creating new cron jobs
- Writing complex cron prompts
- Debugging cron job failures
- Refining cron job logic
- Analyzing cron job performance

**Why:** Coding requires complex reasoning, error handling, and architectural thinking. GLM-5.2 excels here and the one-time cost is worth it.

### DeepSeek V4 Flash (Run Layer — Default)

**Use for:**
- Daily automated tasks (digests, reminders)
- Routine monitoring (health checks, alerts)
- Content generation (social drafts, summaries)
- Data processing (scans, syncs, reports)
- Standard automation workflows

**Why:** These tasks run frequently and don't need complex reasoning. DeepSeek V4 Flash handles them well at low cost (~$0.06/M in).

### GLM-5.2 (via OpenCode Go) — Build/Audit Layer

**Use for building/auditing, NOT routine runs (cost optimization).**

**Trigger conditions for audit:**
- Cron job returns unexpected data or errors
- A task needs complex reasoning, error handling, or architectural thinking
- User says "audit this" — follows develop-and-verify pattern
- Pre-publish security/code review

**Fix pattern:**
```python
# Audit a failing cron with GLM-5.2 via OpenCode Go
result = mcp__blockrun__blockrun_chat(
    message="Analyze this cron error...",
    model="zai/glm-5"
)
```

**Cost note:** GLM-5.2 is premium ($1.40/M in) — use only for high-value one-off tasks. DeepSeek V4 Flash handles routine runs at ~$0.06/M in.

**Why it works:** DeepSeek Flash offers 128K context, costs ~$0.06/M in and ~$0.40/M out, and has proven reliable for all cron job classes (routine monitoring, content generation, complex scanning, data processing). No rate limit issues observed with 38 concurrent cron jobs.

**Cost comparison (current routing):**
| Model | Provider (Gateway) | ~Cost/M in | Role |
|-------|-------------------|-----------|------|
| DeepSeek V4 Flash | OpenCode Go (Gentech) / Ollama Cloud (Forge) | ~$0.06 | Routine runs (default) |
| GLM-5.2 | OpenCode Go (Gentech) / Ollama Cloud (Forge) | ~$1.40 | Builds, audits, high-value tasks |
| (fallback) | Nous Research | — | Only if primary gateways down |

**Migration rule:** When a cron fails with a connection error on Z.AI, try DeepSeek Flash first (not GLM-5.2). It's cheaper than GLM-5, doesn't burn Z.AI quota, and doesn't require a separate API key. Only escalate to GLM-5.2 when the prompt itself needs complex rewriting.

**Pitfall — Z.AI fallback chain:** Do NOT set Z.AI as fallback provider for DeepSeek Flash crons. If DeepSeek is the primary and Z.AI is the fallback, the cron will silently swap to Z.AI on any transient error and burn quota. Set `fallback=null` or use a provider without quota limits as the fallback.

## Model Selection Matrix

| Task Type | Frequency | Complexity | Recommended Model | Cost Impact |
|-----------|-----------|------------|-------------------|-------------|
| **Job Creation/Config** | One-time | High | GLM-5.2 (OpenCode Go) | Low (one-time) |
| **Job Updates/Fixes** | Occasional | High | GLM-5.2 (OpenCode Go) | Low (occasional) |
| **Daily Digest** | Daily | Medium | DeepSeek V4 Flash (OpenCode Go) | Medium |
| **Health Monitoring** | Every 6h | Low-Medium | DeepSeek V4 Flash (OpenCode Go) | Medium |
| **Content Generation** | Weekly | Medium | DeepSeek V4 Flash (OpenCode Go) | Low |
| **Complex Analysis** | Weekly | High | GLM-5.2 (OpenCode Go) | Low (justified) |
| **Simple Alerts** | Variable | Low | DeepSeek V4 Flash (OpenCode Go) | Low |
| **Data Sync/Scrape** | Variable | Low | None (script-only) | None |
| **Audit/Verify** | After tasks | Medium | GLM-5.2 (OpenCode Go) | Low (per-task) |

## Implementation Pattern

### When Creating Cron Jobs

**Step 1: Build with GLM-5.2**
```python
# Use GLM-5.2 for complex prompt engineering
prompt = """
You are Gentech running the weekly API Marketplace Scout.
Your job is to scan our entire vault and categorize APIs by:
1. Integration complexity
2. Business value
3. Priority for implementation

Requirements:
- Use routing skill for context
- Check obsidian vault for existing APIs
- Generate prioritized action list
- Deliver to HQ group
"""

cronjob(action='create', 
        name='API Marketplace Scout',
        schedule='0 14 * * 3',
        prompt=prompt,
        model='glm-5.2',  # Complex task, worth the premium
        provider='zai')
```
#### Cost Optimization — Pin to Run-Layer Model

```python
# After job is created, pin to run-layer model
cronjob(action='update',
        job_id='f854e4283771',
        model={'provider': 'nous', 'model': 'deepseek/deepseek-v4-flash'})
```

### When Upgrading Existing Jobs

**Example: Fixing Failing Cron Jobs**

```python
# 1. Identify failing jobs
failing_jobs = cronjob(action='list')
failing = [job for job in failing_jobs if job['last_status'] == 'error']

# 2. Use GLM-5.2 to analyze and fix (build layer)
for job in failing_jobs:
    print(f"Analyzing {job['name']} with GLM-5.2...")
    
    # Complex debugging uses GLM-5.2
    fixed_prompt = refine_prompt_with_glm52(job['prompt_preview'])
    
    # Update job with improved prompt
    cronjob(action='update',
            job_id=job['job_id'],
            prompt=fixed_prompt)
    
    # 3. Downgrade to GLM-4.7 for runs (cost optimization)
    cronjob(action='update',
            job_id=job['job_id'],
            model='glm-4.7',
            provider='zai')
```

## GLM-5.2 Premium Justification Criteria

Only use GLM-5.2 for running cron jobs when:

1. **Complex Analysis Required**
   - Multi-source data synthesis
   - Strategic recommendation generation
   - Complex decision trees

2. **High Business Value**
   - Opportunity scanning (hackathons, jobs, grants)
   - Revenue-generating activities
   - Competitive intelligence

3. **Low Frequency**
   - Weekly or less frequent runs
   - One-off analysis tasks
   - Special reports

**GLM-5.2 Jobs Examples:**
- 5-Star Opportunity Scanner (Mon/Thu - high value)
- Social Media Engine (Wed/Sat - complex content creation)
- Sunday Review (weekly - comprehensive analysis)

**DeepSeek V4 Flash Jobs (Routine):**
- Daily Digest (daily - routine)
- Health Monitoring (every 6h - routine)
- Game Patch Notes (daily - routine)
- Simple alerts (variable - routine)
- Hub Nightly Sync (daily - routine)
- Morning To-Do (daily - routine)

## Cost Impact Analysis

### Example: 38 Cron Jobs

**All GLM-5.2:**
- Daily jobs: ~10 jobs × GLM-5.2 cost = High daily cost
- Weekly jobs: ~15 jobs × GLM-5.2 cost = Medium weekly cost
- **Total:** Very expensive monthly usage

**GLM-5.2 for build/audit, DeepSeek V4 Flash for run:**
- Build layer: Jobs configured/audited with GLM-5.2 = One-time cost
- Run layer: Most jobs running with DeepSeek V4 Flash = Low daily cost
- GLM-5.2 premium: Only used for complex one-off audits = Minimal cost
- **Total:** 80-90% cost reduction

## Verification Pattern

**Verify after every task.** After any cron job creation, update, or maintenance:
1. Verify the job runs (`last_status: ok` or trigger a test run)
2. If it fails → audit with GLM-5.2 via OpenCode Go → diagnose → fix → re-verify
3. Confirm model routing is correct for the task tier

Always verify model configuration after cron job creation:

```python
def verify_model_config(job_id, expected_model):
    """Ensure cron job uses cost-effective model."""
    job = cronjob(action='list', job_id=job_id)
    
    if job['model'] == expected_model:
        return f"✅ {job['name']}: {expected_model} (optimized)"
    else:
        return f"⚠️ {job['name']}: {job['model']} → downgrading to {expected_model}"
        cronjob(action='update', job_id=job_id, model=expected_model)

# Then verify it runs
result = cronjob(action='run', job_id=job_id)
if result['last_status'] == 'ok':
    print(f"✅ {job_id} verified — runs clean")
else:
    print(f"🔍 {job_id} failed — audit with GLM-5.2")
```

## Common Pitfalls

### 0. Unpinned Jobs Failing Due to Global Config Drift

**Problem:** A cron job running fine for weeks suddenly fails with: `global inference config drifted since this job was created (model 'X' -> 'Y'), and this job is unpinned.`

**Root cause:** The job was created without an explicit `model` pinned to it, so it inherits the global default. When the global default changes (new provider, model rollout, config migration), the inherited model changes too. The scheduler detects the drift and blocks execution to prevent unintended spend.

**Detection — two types of `model: null` jobs:**

| Job shape | Type | Vulnerability |
|-----------|------|--------------|
| `model: null, provider: zai` | LLM job, unpinned | ⚠️ Drift-vulnerable — will fail when global defaults change |
| `model: null, provider: null` | Script-only (`no_agent: true`) | ✅ Immune — no LLM involved |

**Fix — pin model + provider in one call:**
```python
cronjob(action='update',
        job_id='...',
        model='glm-5',    # Pick capability level the job needs
        provider='zai')   # Must be set together with model
```

**Prevention:** Always pass an explicit `model` when creating jobs:
```python
cronjob(action='create', ...,
        model='glm-4.7',  # Never leave this null
        provider='zai')
```

**Real-world example (Jul 2, 2026):**
- **Before:** `model: null, provider: zai, last_status: error`
- **Error:** `skipped to prevent unintended spend: global inference config drifted (glm-4.7 -> stepfun/step-3.7-flash:free)`
- **Fix:** Pinned to `model='glm-5', provider='zai'`
- **Lesson:** Build for the right capability tier AND pin it. Unpinned jobs break silently on config change.

### 1. Over-Upgrading to GLM-5.2

**Wrong:** "Let's make everything GLM-5.2 for quality"
**Right:** "Use GLM-5.2 only for high-value, low-frequency tasks"

### 2. Forgetting Cost Optimization

**Wrong:** Create with GLM-5.2, forget to downgrade
**Right:** Build with GLM-5.2, run with GLM-4.7 (unless justified)

### 3. Script-Only Jobs Using LLMs

**Wrong:** LP Monitor with GLM-5.2 (script-only, no LLM needed)
**Right:** LP Monitor with `no_agent: true` (script execution only)

### 4. Assuming Z.AI Is Always Available

**Wrong:** Model selection only considers Z.AI provider (GLM-5.2 → GLM-4.7)
**Right:** Include DeepSeek Flash on opencode-go as a lateral failover for when Z.AI has connection errors or quota exhaustion

**Detection pattern:**
- Cron `last_status: "error"` with no delivery error message
- User reports "it was erroring out"
- The error surface is a bare `Connection error` — no auth failure, no 4xx, just network-level timeout

**Fix:** Swap model + provider together in one `cronjob(action='update')` call. Do NOT chain through Z.AI at all once connection errors appear — the issue is provider-side, not model-specific.

### 5. Fixing Failing Crons — Start with DeepSeek Flash, Not GLM-5.2

**Wrong:** When a cron fails, immediately upgrade to GLM-5.2 for analysis (expensive + burns Z.AI quota)
**Right:** Try DeepSeek Flash first — if the issue was Z.AI connectivity, DeepSeek Flash resolves it at lower cost. Only escalate to GLM-5.2 if the prompt itself needs rewriting.

**Real-World Example (Jul 2, 2026):**
- **Problem**: API Marketplace Scout (GLM-5, Z.AI) → `Connection error`
- **Attempted fix**: Upgrade to GLM-5.2 (same Z.AI provider) → would have failed the same way
- **Actual fix**: Swapped to `deepseek-v4-flash` on `opencode-go` → ran successfully on first attempt
- **Lesson**: The error wasn't model quality — it was provider connectivity. Changing models within the same broken provider doesn't help.

## Integration with Agent Kit

This skill works with the truth architecture:

1. **Truth Layer** (cron-truth-layer) — verify data freshness
2. **Fix Layer** (auto-fix-preflight) — auto-fix safe issues
3. **Build Layer** (model-optimized-cron-config) — optimize model selection
4. **Run Layer** — cost-effective execution

Every cron job should pass through all layers: verify → fix → optimize → run.

**Quick Reference**

**GLM-5.2 (via OpenCode Go) for:**
- ✅ Creating new cron jobs
- ✅ Debugging cron failures (complex prompt analysis)
- ✅ Complex audits and verification
- ✅ High-value weekly analysis

**DeepSeek V4 Flash (OpenCode Go) for:**
- ✅ Daily automated tasks
- ✅ Routine monitoring
- ✅ Standard content generation
- ✅ Most data processing

**No LLM for:**
- ✅ Script-only jobs (no_agent: true)
- ✅ Simple data sync/scrape
- ✅ Routine health checks (script-based)

## Cost Formula

```
Monthly Cost = (Daily_Run_Jobs × DEEPSEEK_Cost × 30) + 
               (Weekly_Run_Jobs × DEEPSEEK_Cost × 4) +
               (Premium_Audit_Tasks × GLM52_Cost × Frequency)
```

**Optimization Goal:** Minimize the third term by using GLM-5.2 only for audits and builds.

## Systematic Cron Job TLC Workflow

When user reports "a lot of cron jobs failing right now" or mentions performance issues, follow this systematic pattern:

**Phase 1: Diagnosis**\n```python\n# List all cron jobs\njobs = cronjob(action='list')\n\n# Identify problems\nfailing = [job for job in jobs if job['last_status'] == 'error']\nold_models = [job for job in jobs if job['model'] in ['mimo-v2.5', 'glm-4.5-flash', 'glm-4.7-flash']]\n\n# TWO kinds of null-model jobs — handle differently:\ndrift_vulnerable = [job for job in jobs if not job['model'] and job['provider']]  # LLM jobs, unpinned\nscript_only = [job for job in jobs if not job['model'] and not job['provider']]  # no_agent=true, immune\n```\n\n**Phase 2: Targeted Fix (not blanket upgrade)**\n```python\n# Fix drift-vulnerable jobs: pin to appropriate tier, don't auto-upgrade\n# These are already working on the inherited default — just pin it\nfor job in drift_vulnerable:\n    # Check what the job's prompt does to determine appropriate tier\n    # Scanning/research jobs → glm-5, routine jobs → glm-4.7\n    cronjob(action='update',\n            job_id=job['job_id'],\n            model='glm-4.7',  # Pin to appropriate tier, not premium\n            provider='zai')\n\n# Upgrade truly failing jobs to GLM-5.2 for analysis (old approach still valid)\nfor job in failing + old_models:
    cronjob(action='update', 
            job_id=job['job_id'],
            model='glm-5.2',  # Use coding beast for complex fixes
            provider='zai')
```

**Phase 3: Cost Optimization (Run Layer)**
```python
# Roll back routine jobs to GLM-4.7
routine_jobs = [
    # Daily monitoring
    'Daily Digest', 'Morning To-Do', 'Hub Nightly Sync',
    # Game patches
    'Game Release Intelligence', 'Voice Patch Notes',
    # Content generation
    'Desmond Content Engine', 'Weekly Sales Sweep'
]

for job in routine_jobs:
    cronjob(action='update',
            job_id=job['job_id'],
            model='glm-4.7',
            provider='zai')
```

**Phase 4: Verification**
```python
# Verify model distribution
final_jobs = cronjob(action='list')
glm_52_count = len([j for j in final_jobs if j['model'] == 'glm-5.2'])
glm_47_count = len([j for j in final_jobs if j['model'] == 'glm-4.7'])

print(f"GLM-5.2 jobs: {glm_52_count} (high-value only)")
print(f"GLM-4.7 jobs: {glm_47_count} (cost-optimized)")
```

**Critical Pitfall: Forgetting Rollback**
- **Wrong**: Upgrade everything to GLM-5.2, consider it "fixed"
- **Right**: Upgrade to GLM-5.2 for analysis, roll back to GLM-4.7 for runs
- **User Signal**: "we can run it using a different model. I just wanted to create the actual cron job using 5.2"

**Workflow Recovery Pattern**
When user says "we have a lot of cron jobs failing right now":
1. First acknowledge: concern about cost impact of using GLM-5.2 everywhere
2. Explain two-tier strategy: GLM-5.2 for build, GLM-4.7 for run
3. Execute systematic upgrade → rollback workflow
4. Verify cost savings achieved

**Real-World Example** (Jul 1, 2026):
- **Problem**: 5 failing cron jobs + traces of mimo-v2.5 + glm-4.5-flash
- **Solution**: Upgraded 16 jobs to GLM-5.2 → rolled back 12 to GLM-4.7
- **Result**: Only 2 high-value jobs on GLM-5.2, 80-90% cost reduction
- **User Feedback**: "I just wanted to create the actual cron job using 5.2"

## MODEL-HEALTH PROBE FALSE FLAGS — REASONING BUDGET FLOOR (Sep 8 2026)

**Symptom:** A model-health cron flags ALL reasoning models (glm-5.2/5.3/kimi) as DEGRADED for days — but they were never down. Same symptom as the fleet-wide Sep 7 "ollama-cloud degradation."

**Root cause:** The probe used `max_tokens=10` (trivial) and `250` (substantive) — under the reasoning-model floor. glm/kimi burn the budget on `reasoning_content` before ANY content, returning `content:"" / finish:"length"` at low budgets. The probe classified a healthy model returning empty-on-tight-budget as DEGRADED.

**Fix the PROBE first, not the models:**
1. **Substantive probe budget ≥ 4000** (we verified glm-5.3-flash/kimi-k2.7/kimi-k3/deepseek all return real content at 4000; 500 passes trivial but cuts off on audit load).
2. **Trivial probe budget ≥ 500** (reasoning models return empty below this).
3. **Retry on empty-body / EmptyStreamError**: an upstream SSE hiccup returns HTTP 200 + empty body (via Google Frontend). Retry (up to 3x) clears it. Don't classify a one-off hiccup as "degraded." Also retry on 429/500/502/503/504.

**Rule:** If a probe flags an entire fleet degraded, suspect the PROBE BUDGET + empty-body handling FIRST (raise to 4000, add retry) before declaring the backend down. A probe that uses a tight budget is the more likely bug than the whole provider vanishing.

**Verified (Sep 8):** all 7 ollama-cloud models return substantive DeFi-audit content at max_tokens=4000. glm-5.3-flash gave a real 1,418-char audit finding. The AUDIT lever (develop-and-verify second phase) is usable.