---
name: routing
description: "Unified routing — detect topic → route to group, detect complexity → route to model. One system, two dimensions."
category: core
priority: critical
version: 3.1.0
author: GenTech Labs
tags: [routing, smart-routing, model-selection, topic-detection, cost-optimization]
---

# Unified Routing

One routing system, two dimensions:
1. **Topic** → which group (Labs, Strategies, Entertainment, HQ)
2. **Complexity + Domain** → which model (MiMo, OpenCode Go, BlockRun)

## Dimension 1: Topic Routing (Which Group)

| Topic | Group | Chat ID |
|-------|-------|---------|
| Code, SDKs, smart contracts, technical dev | Labs | `-1003872552815` |
| Finance, DeFi, portfolio, yield, market analysis | Treasury | `-1002916759037` |
| Content, social media, hackathon submissions | Entertainment | `-1003893562036` |
| Coordination, decisions, blockers, status | HQ | `-1003863540828` |
| **Forge-domain tasks** (code builds, PRs, local git, email) | **→ Handoff via** `01-HANDOFFS/` | **Forge (Desktop) handles** |
| **Gentech-domain tasks** (infra, cron, DeFi, research) | **→ Build on VPS** | **Gentech (VPS) handles** |

## Dimension 2: Model Routing (Which Model)

### Z.AI / GLM Provider Stack (June 26, 2026 — migrated from Xiaomi/OpenCode Go)

| Provider | Models | Strategy |
|----------|--------|----------|
| **Z.AI (zai)** | GLM-5.2, GLM-5, GLM-5-Turbo, GLM-5.1, GLM-4.7, GLM-4.6, GLM-4.7-Flash, GLM-4.5-Flash | **ALL** — single provider with full ladder |

### Routing Rules (GLM-optimized)

| Complexity | Primary | Overflow | Why |
|-----------|---------|----------|-----|
| **Trivial** | GLM-4.7-Flash, GLM-4.5-Flash | GLM-4.7 | Free for quick facts |
| **Simple** | GLM-4.7-Flash, GLM-4.7 | GLM-4.6 | Flash for speed, 4.7 for quality |
| **Medium** | GLM-4.7, GLM-4.6 | GLM-5 | Budget models first |
| **Complex** | GLM-5, GLM-5-Turbo | GLM-5.2, GLM-5.1 | Premium for complex work |

### Domain Affinities (GLM-optimized)

| Domain | Best Models | Why |
|--------|------------|-----|
| **Code** | GLM-5.2 → GLM-5.1 → GLM-4.7 | **GLM-5.2 always** — #1 open-source coder, 1M context |
| **Finance** | GLM-5 → GLM-5-Turbo → GLM-5.2 | GLM-5 strong reasoning |
| **Analysis** | GLM-5 → GLM-4.7 → GLM-4.6 | GLM-5 analysis, 4.7 good value |
| **Content** | GLM-4.7 → GLM-4.6 → GLM-4.7-Flash | 4.7 good writing, Flash for simple |
| **Research** | GLM-5 → GLM-5.1 → GLM-5.2 | Premium models for deep research |
| **Quick QA** | GLM-4.7-Flash → GLM-4.5-Flash | Free, fast |
| **Creative** | GLM-4.7 → GLM-4.6 → GLM-5 | 4.7/4.6 creative, 5 for complex |
| **Technical** | GLM-5.2 → GLM-5.1 → GLM-5 | GLM-5.2 1M context for technical |

### Cost Savings (GLM vs always GLM-5.2)

| Model | Tasks (1000) | Cost |
|-------|--------------|------|
| GLM-4.7-Flash (free) | 200 | $0.00 |
| GLM-4.7 | 600 | $1.68 |
| GLM-5 | 150 | $0.63 |
| GLM-5.2 | 50 | $0.29 |
| **Total** | **1,000** | **$2.60** |

**vs always GLM-5.2:** $5.80/month → **55% savings**  
**vs always Claude Sonnet 4:** $18.00/month → **85.6% savings**

### Task-Aware Scheduler (TAS) Implementation

**Location:** `/root/vaults/gentech/10-Labs/model-router/`  
**Tests:** 27/27 passing  
**Agent Kit:** `/root/projects/genTech-agent-kit/core/intelligence/model-router/`

**Usage:**
```python
from model_router import route_task

# Coding always gets GLM-5.2
result = route_task("run the build list", context="coding")
# → {'model': 'glm-5.2', 'provider': 'zai', 'reasoning': 'Code task → GLM-5.2 (best coding model)'}

# Finance gets GLM-5
result = route_task("analyze LP position ROI")
# → {'model': 'glm-5', 'provider': 'zai', 'reasoning': 'finance / simple → glm-5'}

# Quick QA gets free Flash
result = route_task("what is GLM?")
# → {'model': 'glm-4.7-flash', 'tier': 'free', 'reasoning': 'quick_qa / trivial → glm-4.7-flash'}
```

**Cron Job Routing Pattern (current - manual):**
Use `cronjob action=update` with `model` and `provider` parameters:

```python
cronjob(action="update", job_id="5fb8a3cf8160", model={"model": "glm-4.7", "provider": "zai"})
```

**Cron Job Routing Pattern (future - automated TAS):**
Build Hermes middleware that:
1. Intercepts every request
2. Calls `route_task(prompt)`
3. Updates model/provider dynamically
4. Routes to optimal model automatically

**Provider name:** `zai` (exact match to config)

## Dimension 3: Auto-Hub Detection

When someone talks about a topic, auto-detect and log to their hub. No cron — the agent does this in real-time.

### Topic → Hub Mapping

| Topic Signal | Hub | Action |
|-------------|-----|--------|
| Food, cooking, recipes, restaurants | Cookbook | Log dish, suggest next meal |
| Travel, flights, hotels, trips | Travel | Log destination, track plans |
| Fitness, workout, gym, diet | Fitness | Log routine, track progress |
| Goals, targets, bucket list | Goals | Log goal, offer support |
| Hobbies, side projects, learning | Hobby | Create hub if new, log activity |

### Detection Keywords

**Food:** cook, cooking, recipe, dish, meal, food, eat, fried, sautéed, simmered, ingredients, restaurant, grocery. Filipino: adobo, sinigang, tinola, caldereta, pancit, giniling, kare-kare

**Travel:** flight, hotel, trip, vacation, booking, airport, destination, resort, island

**Fitness:** gym, workout, exercise, run, protein, diet, calorie, muscle

**Goals:** goal, target, want to, hoping to, dream, plan, by next year

**Hobbies:** hobby, interested in, learning, practicing, side project

### What To Do

1. Detect topic in message
2. Read hub registry at `/root/vaults/gentech/hubs/registry.json`
3. Find or create the person's hub
4. Log the entry (dish, trip, goal, etc.)
5. Respond naturally — don't mention logging
6. Suggest related items

### Hub Registry

```
/root/vaults/gentech/hubs/registry.json
/root/vaults/gentech/Cookbook/christel-journal.json
/root/vaults/gentech/Travels/christel-travel.json
```

### Important Rules

- **Don't be creepy** — respond like a friend, not a database
- **Don't force it** — "I'm hungry" ≠ recipe. Only log real shares
- **Suggest, don't lecture** — offer ideas, not instructions
- **Filipino vibe** — for Christel, use Filipino dish names and references

## How Routing Works

```
Message → Topic Detection → Group Selection
       → Complexity Detection → Model Selection
       → Auto-Hub Detection → Log to Hub
       → Execute in right group with right model
```

### Example

User: "Debug this Python race condition"

1. **Topic:** Code → Labs group
2. **Domain:** Code
3. **Complexity:** Complex
4. **Model:** GLM-5.2 (best coding) or MiMo (subscribed)
5. **Execute:** Build in Labs, report to HQ

User: "What's the AVAX price?"

1. **Topic:** Finance → Strategies group
2. **Domain:** Finance (quick check)
3. **Complexity:** Trivial
4. **Model:** Step 3.5 Flash (free) or DeepSeek Flash
5. **Execute:** Quick answer, no MiMo credit burn

## Delegation Layer v2 (Aug 29, 2026 — Jordan directive: route work, don't hoard it)

When a message in HQ clearly belongs to a specialist group, HQ does NOT absorb the work. Route it through the handoff mesh:

| Topic surfaces in HQ | Delegate to | Mechanism |
|----------------------|-------------|-----------|
| Code/SDK/contract/build tasks | **Labs** (gizmo) | Handoff note → `01-HANDOFFS/gentech-to-labs/` |
| Finance/DeFi/yield/portfolio analysis | **Treasury** (Steward) | Handoff note → `01-HANDOFFS/gentech-to-treasury/` |
| Content/social/video/hackathon submissions | **Entertainment** (pixel) | Handoff note → `01-HANDOFFS/gentech-to-entertainment/` |
| Local builds/PRs/desktop work | **Forge** (desktop, human-gated) | Handoff note → `01-HANDOFFS/gentech-to-forge/` |

**Why it works now (Aug 29 rollout):** every agent's wake trigger sweeps its lanes every 10 min (silent when clear), and the PA Suite enforces ACK→act→report with 6h-stall escalation to Jordan. Early delegation attempts failed from unseen handoffs — that failure mode is closed.

**Protocol:** write the handoff note (From/To/Date/Status: open + What's needed + Context) → announce the routing decision in the origin chat → specialist ACKs in a return lane note → work happens → return note with What was done / What you should know / What's next. HQ keeps the thread: summary in, task out, result back, all visible in git.

**Do NOT delegate:** coordination, decisions, blockers, cross-group work, anything Jordan explicitly wants in HQ.

## When to Route

**Route automatically when:**
- Message clearly fits a specialist topic
- User says "continue in Labs" / "go to Strategies"
- Build task completed → Labs
- Financial decision needed → Strategies
- Content creation discussed → Entertainment

**Stay in HQ when:**
- Topic is coordination/meta
- Asking about routing itself
- Topic spans multiple groups
- User explicitly wants HQ

## Build Queue Auto-Detection

When a buildable idea surfaces in ANY group, add to build queue — don't build immediately.

**Detection signals:** "We should build...", "This could be a...", "What if we made...", "Let's build..."

**Response:** Acknowledge → Add to `scripts/build_queue.json` → Tell user

**Exception:** "Build it now" / "green light" / "ship it" → skip queue, build immediately.

## Run the Build List Trigger (Mandatory)

When Jordan says any of the following, this **overrides all other context**:

| Trigger Phrase | Action |
|----------------|--------|
| "run the build list" | Execute build-queue skill immediately |
| "run the build queue" | Same |
| "go down the list" | Same |
| "knock out the queue" | Same |

This is not a suggestion — it's a mandatory skill trigger. Stop current topic, load the build-queue skill, execute.

## Two-List System (Orchestrator + Build Queue)

Jordan established a clean separation — June 24, 2026:

| List | Location | Who Adds | What Goes Here |
|------|----------|----------|----------------|
| **Orchestrator List** | `HQ/jordan-queue.md` | Agent or Jordan | Jordan's personal action items only |
| **Build Queue** | `scripts/build_queue.json` (canonical JSON) | Agent only | Technical build tasks, start to finish |
| **Build Queue (human-readable)** | `10-Labs/build-queue.md` | Agent only | Summary of JSON queue for quick reference |

**Pitfall:** The canonical build queue is `scripts/build_queue.json` (v50+, 28 items). The `10-Labs/build-queue.md` file is a human-readable summary that may not exist until a cron job creates it. Always read `scripts/build_queue.json` for the authoritative list. If `10-Labs/build-queue.md` doesn't exist, create it as a summary after adding items.

### Routing Rules for Cron Jobs
When a cron job finds issues, route them:

| Issue Type | Where It Goes | Who Handles |
|------------|---------------|-------------|
| Small fix (config, doc, stale data) | Auto-fix in cron | Cron job does it |
| Big task (new platform, API listing) | Build Queue | Labs agent |
| Human-only (wallet, DNS, account) | Orchestrator List | Jordan |

**Never put Jordan action items in the Build Queue. Never put build tasks in the Orchestrator List.**

### Cron Job Prompt Pattern
When updating cron jobs to be action-oriented, use this structure:

```
## ROUTING RULES

### Small fixes (do automatically)
- Code/config fixes → Make the change, commit it
- Missing documentation → Create the file
- Stale data in vault → Update the file

### Big tasks (add to Labs build queue)
- New platform registration → Add to build queue
- API listing scaffolding → Create files, add to build queue
- Competitor counter-strategy → Add analysis to build queue

### Human-only tasks (add to orchestrator list)
- Profile updates requiring wallet connection → Add to orchestrator list
- DNS changes → Add to orchestrator list
- API keys or account setup → Add to orchestrator list
```

### Pitfall: Don't Mix Lists
- Jordan's to-do items in the Build Queue get lost — he doesn't read it
- Build tasks in the Orchestrator List confuse the agent — it tries to do them itself
- Always verify which list an item belongs to before adding

## Cron Job Creation Rules

**BEFORE creating any cron job, ALWAYS:**

1. **List existing jobs** — `cronjob(action='list')`
2. **Check for duplicates** — same name, same schedule, same purpose
3. **Check for conflicts** — jobs running at the same time that could crash
4. **Check for redundancy** — jobs doing similar things that should be consolidated
5. **Report to user** — "Found X similar jobs. Creating new one anyway? Consolidate?"

**COLLABORATOR GUARD (CRITICAL):** When Vanito or any non-technical collaborator asks you to create a timed/recurring task, you MUST:
- Pause and explain: **"This will create a recurring job that runs every [X minutes/hours] and costs money each call — is that what you want?"**
- Get explicit verbal confirmation before creating it
- Do NOT assume they understand cron mechanics or billing implications
- Why: Vanito accidentally created a `every 10m` cron that ran `blockrun_video` at $0.26/clip, burning ~$35 in under 2 days without anyone knowing

**Provider name check (CRITICAL):**
When setting model on a cron job, the provider MUST match the exact `name` field in `custom_providers:` config. Check config first:
```bash
grep -A3 "custom_providers" ~/.hermes/profiles/gentech/config.yaml
```
Wrong: `custom:XiaomiMega` ❌
Right: `custom:Token-plan-sgp.xiaomimimo.com` ✅

**Delivery target selection for cron jobs (established Jul 17, 2026):**
| Cron Type | Delivery Group | Rationale |
|-----------|---------------|-----------|
| PR monitoring (PR Scout) | HQ | Inbox duty + decisions — needs Jordan's attention |
| Compliance/listing (x402 Compliance) | Labs | Technical work, auto-queue to build list |
| Build status (Build Queue Snapshot) | Labs | Team visibility on active builds |
| Finance (Portfolio, Market, LP) | Strategies | Financial analysis |
| Revenue (Revenue Monitor) | HQ | Bottom-line status for founder |
| Content (Shop, Social) | Entertainment | Content creation and distribution |
| Research (Ecosystem, Opportunity) | HQ or Origin | Depends — scanning for Jordan vs technical audit |

**Conflict detection:**
- Same time slot (within 5 min) = potential crash
- Same purpose = duplicate
- Same script = redundant
- Same delivery target + similar schedule = consolidation candidate

**Auto-consolidation rule:** If a new job overlaps with an existing one, consolidate instead of creating a duplicate. Update the surviving job's prompt to absorb the new job's responsibility.

## Rules\n## Cross-Channel Message Forwarding

When you need to send a message to a different channel (e.g., from Entertainment to HQ), use `hermes send`:

```bash
# Forward to Jordan in HQ
hermes send --to telegram:-1003863540828 "Message here"

# Pipe content from a file
cat /tmp/message.txt | hermes send --to telegram:-1003863540828

# Send to any channel by chat ID
echo "Status update" | hermes send --to telegram:<chat_id>
```

**Key points:**
- Works without the agent running — reuses gateway credentials directly
- Format: `hermes send --to telegram:<chat_id> <message>`
- Can pipe from file: `cat file.txt | hermes send --to telegram:<chat_id>`
- Available targets: `hermes send --list` shows all configured channels

## Pitfalls
**Channel IDs with cron routing (established Jul 17, 2026):**\n| Channel | Chat ID | Cron Deliveries |\n|---------|---------|----------------|\n| HQ | `-1003863540828` | PR Scout (8/14/20 ET), Revenue Monitor (8 AM/PM), Morning Digest, Context Snapshot, Marketplace Scout, Opportunity Scanner |\n| Labs | `-1003872552815` | x402 Compliance Scout (8:10/14:10/20:10 ET), Build Queue Snapshot (8:30/12:30/18:30 ET) |\n| Treasury | `-1002916759037` | Portfolio Health Check, CMC Watchlist, Tradesta Signal, Narrative Rotation, Fed/FOMC, LP Monitor v2 |\n| Entertainment | `-1003893562036` | GenTech Shop Sales/Releases, Social Media Engine, Game Intelligence |

## Rules
1. Always announce routing decision — don't silently route
2. If ambiguous, stay in HQ and ask
3. HQ is fallback for everything
4. User can override with "stay here"
5. After routing, summarize what was sent where
6. Check vault for context before replying
7. Relaxed build exception: small in-group builds OK
8. **Telegram links must be tappable** — bare URLs on own line, not in tables
9. **Split long messages** — under 1500 chars each (Telegram hard limit is 4096, but 1500 is safe for formatting)
10. **Cron job creation** — ALWAYS check existing jobs first for duplicates/conflicts

## Pitfalls

### Provider Names Are Case-Sensitive and Specific
The custom provider name in cron jobs MUST match the `name` field in `custom_providers:` config exactly. Example: `custom:Token-plan-sgp.xiaomimimo.com` NOT `custom:XiaomiMega`. Wrong name = "Unknown provider" error. Always check config first:
```bash
grep -A5 "custom_providers" ~/.hermes/profiles/gentech/config.yaml
```

### OpenCode Go Model Availability
Not all models are available on OpenCode Go. Verified working: `qwen3.6-plus`, `mimo-v2.5`, `kimi-k2.6`. NOT working: `step-3.5-flash`. Always test a model before assigning it to cron jobs:
```bash
API_KEY=$(grep OPENCODE_GO_API_KEY ~/.hermes/profiles/gentech/.env | cut -d= -f2-)
curl -s -X POST "https://opencode.ai/zen/go/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"model":"MODEL_NAME","messages":[{"role":"user","content":"Say hi"}],"max_tokens":10}'
```

### Wallet Ownership Rule
NEVER assume the agent controls a wallet. Always ask the user for their wallet addresses. Agent-generated wallets are unowned unless the user confirms they have the private keys. Fund only wallets the user explicitly provides.

### Model routing for cron jobs
- **Simple tasks** (script-only, summarization): use free/cheap models (qwen3.6-plus via OpenCode Go)
- **Medium/Complex tasks** (analysis, research): use subscribed models (mimo-v2.5 via Xiaomi Custom)
- **Code-heavy tasks** (audits, security, smart contracts): GLM-5.2 via BlockRun (pay-per-use, #1 coding benchmarks) — only if quality matters more than cost
- **Script-only jobs** (no_agent=True): no model needed

### Known routing gap (Jun 2026)
Code-heavy cron jobs (Project Audit, code reviews) currently use MiMo-V2.5 instead of GLM-5.2. MiMo is solid at code but GLM-5.2 is top-rated for coding benchmarks. Consider upgrading code-domain jobs to GLM-5.2 via BlockRun when quality matters — it's pay-per-use so only costs when it runs.

### Fix routing gaps on discovery
When a routing mismatch is found (wrong model for domain, suboptimal provider for task type), fix it immediately — don't just flag it in a report. Jordan's directive: "Less troubleshooting, fix all issues." Update the cron job model/provider on the spot, verify it works, then report what was fixed.

## References
- Code: `/root/vaults/gentech/10-Labs/model-router/` — Model router module (27 tests, 84.6% savings)
- GLM Model Router Guide: `references/glm-model-router.md` — Quick reference, cron update patterns, coding rule
- x402 Bazaar: `references/x402-bazaar.md` — How to get listed, API pricing, revenue monitor
- Wallet Security: `references/wallet-security.md` — Jordan's verified wallets, agent-generated wallet rules
- Cron Model Routing: `references/cron-model-routing.md` — Provider names, model availability, job distribution
- Cloudflare Setup: `references/cloudflare-setup.md` — DNS, SSL, security headers for gentechlabs.net
