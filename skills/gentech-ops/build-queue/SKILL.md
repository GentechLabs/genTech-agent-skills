---
name: build-queue
description: "V4 autonomous build queue — agent works Easy→Hard, saves brain notes at stopping points, auto-switches tasks. Gentech 24/7 VPS, Forge desktop/GPU, Jordan decisions."
tags: [build, automation, pipeline, queue, agent-kit, autonomous, v4]
trigger: "When the user says 'start build list', 'run the queue', 'build queue', wants autonomous task processing, or the V4 Build Queue Tick cron fires (every 30m)."
version: 4.0.0
author: Gentech Labs
---

# Build Queue — Autonomous Pipeline

Turn any task list into an autonomous build pipeline. The agent reads a JSON queue, processes each item (build → test → commit), and delivers a structured report.

## V4 Autonomous Workflow (Jul 2026)

The build queue runs autonomously. **Gentech 24/7 on VPS. Forge desktop heavy lifting. Jordan decisions.**

### Silent Overnight Mode
At midnight ET, the **Nightly Build Session** takes over — develops, tests, verifies, and ships queue items **silently** with no notifications to Jordan. All output is logged to `11-Mess Hall/nightly-build-log.md`. The **Morning Digest** (8 AM ET) delivers the overnight report to Telegram HQ.

**Quiet hours philosophy:** Quiet hours blocks NOTIFICATIONS to Jordan (market alerts, social posts), not build work. The build pipeline runs through quiet hours.

### The Core Loop
```
Gentech picks next task (Easy→Hard) → works until stopping point →
  saves brain note (11-Mess Hall/agent-brain/) → marks task status →
  moves to next task → ...until queue empty → wake-up Jordan with summary
```

### Agent Routing
| Agent | Platform | Where | Handles |
|-------|----------|-------|---------|
| **Gentech** | cloud | VPS (24/7) | MCP tools, API calls, research, drafting, cron jobs, cloud deployments |
| **Forge** | desktop | Desktop/Cloud | GPU compute, local builds, UI testing, game builds, heavy compilation |
| **Jordan** | any | Anywhere | Decisions, auth, signups, submissions, wallet actions |

Each queue item carries a `platform` tag that determines which agent works it:
- **cloud** → Gentech (VPS, always-on, no Jordan needed)
- **desktop** → Forge (needs GPU or local build environment)
- **either** → first available agent
- **any** → Jordan action (needs human input)

### Platform Tagging
Every queue item has a `platform` field so the tick script auto-routes to the right agent.

| Platform | Agent | Can work independently? | Examples |
|----------|-------|------------------------|----------|
| cloud | Gentech | ✅ Fully autonomous | API deploys, contract deployment, content, research |
| desktop | Forge | ✅ No Jordan needed | GPU pipelines, local dev, game builds |
| either | First available | ✅ Autonomous | Coding tasks, documentation, integrations |
| any | Jordan | ❌ Needs Jordan | Signups, auth, wallet actions, submissions |

### Queue Sorting (Revenue First, then Easy→Hard)
**Revenue/income items always come first.** Subscription hubs, paid APIs, grant applications, and any item that generates or enables direct revenue takes priority over all difficulty tiers. Jordan (Jul 2026): "Income or revenue items come first."

Then within non-revenue or same-revenue-tier items, sort by difficulty:
- `difficulty: easy` — forms, signups, submissions (do first after revenue)
- `difficulty: medium` — coding, plugins, content (do second)
- `difficulty: hard` — complex builds, infrastructure (do last)

Rule: Revenue items first, regardless of difficulty. Then complete 1 easy before starting 1 medium. Complete 2 medium before starting 1 hard.

### Stopping Points
Work until one of these triggers:
- **Blocked** — Needs Jordan (auth, decision, wallet, submission)
- **Needs Forge** — Desktop-only work (GPU, local game build)
- **Needs Resource** — Missing API key, tool, credit
- **Complete** — Done, mark as shipped

At each stopping point, save a **brain note** to `11-Mess Hall/agent-brain/YYYY-MM-DD/NNN-taskID-name.md`.

### Idle Session Protocol (All Items Blocked)

When every Gentech-assigned item has `needs_jordan: true` or is otherwise blocked — the session enters idle mode. The agent should not stop working. Instead:

1. **Run a full queue scan** — Read every item's status, `assigned_to`, `needs_jordan`, and `gate_type`. Confirm no actionable items were missed or misclassified.

2. **Identify the highest-leverage item** — Items with `gate_type: "decision"` (Jordan can answer from his phone) and a near `deadline` are top targets. Decision-gated items are faster to unblock than human-gated ones and have the tightest time windows.

3. **Research to remove information barriers** — For the target item, investigate: what infrastructure already exists? What would deployment require? Are there third-party docs, examples, or registration flows? The goal is to produce concrete answers that transform the decision from "what should we do?" to "yes or no with clear tradeoffs."

4. **Update the queue item** — Enrich `detail` and `note` fields with research findings so Jordan can read the updated item and make a fully-informed decision without follow-up questions.

5. **Save a build log** — Even when nothing ships, log what was researched, findings, and what Jordan still needs to decide. Include queue status at the top for next-session context.

6. **Deliver the status report** — Emphasize: (a) which items are closest to unblocked, (b) what decisions Jordan needs to make, (c) time-sensitive deadlines.

**Rationale:** This turns idle wait time into preparation time. When Jordan returns, decision surfaces are pre-shrunk — infrastructure is pre-researched, tradeoffs are documented, and he can batch-approve with one read-through.

### Brain Note Format
```markdown
# Brain Note — 2026-07-10 14:30 UTC
# Task: #38 Pika Subscription

## What was done
- Researched Pika pricing ($8/mo Standard)
- Built Pika plugin for Agent Kit

## Stopping point
Jordan Needed → Sign up at pika.art/pricing

## Next steps when resumed
1. Run Build-a-Brand with GenTech product brief
2. Generate App Sizzle from GitHub URL

## State
- Plugin built ✅
- Account needed ❌
```

### Build Queue Tick (Cron)
Runs every 30 min via `build_queue_tick.py` (no_agent, local delivery). This is the **automatic handoff engine**:

1. Loads `build_queue.json` from canonical path
2. Summarizes queue: total items, by agent, by platform, urgent deadlines
3. Finds next tasks for each agent (Forge next, Gentech next)
4. **Generates Forge task handoff** → `01-HANDOFFS/<date>-forge-tasks.md`\n5. **Generates Jordan action items** → `01-HANDOFFS/<date>-jordan-items.md`
6. Prints full summary to stdout (captured by cron, fed to Nightly Build Session via `context_from`)

**Error handling:** If `build_queue.json` doesn't exist or is corrupt, the script exits with a clear error message telling Gentech to rebuild the queue (rather than crashing silently).

**Context chaining:**
```
Tick (stdout) → context_from → Nightly Build Session (stdout) → context_from → Morning Digest
```

### Queue Cleanliness Rules (Jul 2026)

**Only builds belong in the queue.** Non-build items (signups, subscriptions, applications, submissions, account setups) must not be added to `build_queue.json`. These belong in a separate Jordan action-items list or a project-specific checklist.

### Overnight Maintenance Cron (Jul 2026)
A cron at **06:00 UTC** (`Build Queue — Overnight Maintenance`) auto-maintains the queue:
1. Reads `build_queue.json` and checks PR statuses for any open items with submitted PRs
2. Marks items as `shipped` if upstream PRs have been merged
3. Checks if blocked items have their blocker resolved
4. Updates summary counts if shipping counts changed
5. Commits and pushes changes to the vault

**Delivery is `local`** (silent — no Telegram notification). It's maintenance, not a report.
The Morning Digest (8 AM ET) picks up any queue changes in its overnight report.

**Only builds belong in the queue.** Non-build items (signups, subscriptions, applications, submissions, account setups) must not be added to `build_queue.json`. These belong in a separate Jordan action-items list or a project-specific checklist.

- **Build** = code to write, infrastructure to deploy, API to ship, pipeline to run
- **Not a build** = filling a form, signing up for a service, submitting an application, buying a subscription, setting up a phone number, authenticating with a platform

PR tracking is also **not** a build queue concern. Maintain a separate PR portfolio document (`00-HQ/pr-portfolio.md`) for the PR Scout and x402 Compliance Scout cron jobs to reference.

**Completed items are removed, not kept.** When an item ships, remove it from `items[]` in `build_queue.json`. Do not leave completed items with `status: "completed"` — the queue should show only active builds. This keeps the queue short, scannable, and honest.

**Violation pattern to avoid:** "The build list should only be things that need to be built" — Jordan's exact words after finding signups, subscription forms, and application submissions mixed into the queue. If you catch yourself adding a non-build item, stop and ask where it really belongs.

### Wake-Up Protocol for Jordan
When Jordan reconnects, Gentech auto-delivers:
```
📋 Build Queue Update
  ✅ Completed since last: 3
  👑 Awaiting Jordan: 4 (Pika signup, Circle app, GoPlausible, Sourcegraph submit)

🎯 Recommended Order (Easy→Hard):
  1. Pika signup (2 min)
  2. Circle form (5 min)
  3. GoPlausible Discord auth (5 min)
```

### Queue Format v2 (Current — Jul 2026)
```json
{
  "version": 2,
  "updated": "2026-07-12",
  "items": [
    {
      "id": 28,
      "name": "PixelRAG — Visual Search Demo",
      "difficulty": "medium",
      "priority": "high",
      "status": "pending",
      "assigned_to": "forge",
      "platform": "desktop",
      "needs_jordan": false,
      "detail": "Install on lab laptop (RTX 3070). Test pixelshot CDP. Run demo."
    },
    {
      "id": 34,
      "name": "Sell APIs to AI Agents",
      "difficulty": "medium",
      "priority": "high",
      "status": "pending",
      "assigned_to": "gentech",
      "platform": "cloud",
      "needs_jordan": false,
      "detail": "Deploy Rugcheck v2 API. Add Q402 payment middleware. List in pay-skills."
    },
    {
      "id": 32,
      "name": "Vast.ai GPU Instance",
      "difficulty": "easy",
      "priority": "medium",
      "status": "pending",
      "assigned_to": "jordan",
      "platform": "any",
      "needs_jordan": true,
      "detail": "Sign up at vast.ai. Email + $5 deposit."
    }
  ],
  "agents": {
    "gentech": { "platform": "cloud", "always_on": true },
    "forge": { "platform": "desktop", "always_on": true },
    "jordan": { "platform": "any", "decision_maker": true }
  }
}
```

**Fields:**
- `id` — Unique numeric ID
- `name` — Task name
- `difficulty` — easy | medium | hard (Easy→Hard sorting)
- `priority` — urgent | high | medium | low
- `status` — pending | in_progress | blocked | completed | shipped | cancelled
- `assigned_to` — gentech | forge | jordan | auto
- `owner` — gentech | forge | jordan (consolidated ownership field, added Jul 18 2026)
- `platform` — cloud | desktop | either | any (routes to the right agent)
- `needs_jordan` — true if task requires Jordan input
- `human_gated` — true | false (added Jul 24 2026). When true, `gate_type` specifies the kind of gate.
- `gate_type` — "human" | "decision" | omitted (added Jul 24 2026). "human" = needs Jordan in a browser (fork, signup, KYC, web UI submission). "decision" = needs a yes/no or config value from Jordan.
- `blocked_on` — Optional item ID this task is blocked by
- `deadline` — Optional ISO date
- `repo` — Optional GitHub repo link
- `detail` — Free-text task description

### Gate Type Classification (Jul 24 2026)

The `human_gated` + `gate_type` fields help Jordan batch-process items efficiently:

| Gate Type | Meaning | Example Items | Jordan's Action |
|-----------|---------|---------------|-----------------|
| `human` | Needs Jordan physically in a browser | Fork repos, account signups, KYC, web UI PR submissions | Batch these together in one sitting |
| `decision` | Needs a value or yes/no from Jordan | RECIPIENT_ADDRESS, funded deployer key, go-ahead for new work | Quick answers, can reply from phone |

**Review pattern:** When presenting blocked items to Jordan, group them by gate type — show all human-gated items first (requires his focused time), then decision-gated (quick replies he can do anytime).

**Expected distribution:** In a typical queue of 32 items, ~18 are human-gated, ~8 are decision-gated, ~6 are fully autonomous.

### Status Lifecycle
```
pending → in_progress → shipped
pending → blocked → pending (when unblocked)
pending → cancelled
```

## Quick Start

### For Users (Say This)
```
start build list
run the build queue
build queue --report
```

### For Agents (Do This)
```bash
cd /path/to/your/vault && python3 scripts/run_build_queue.py
```

## Queue Format (`build_queue.json`)

The canonical queue lives at `/root/vaults/gentech/scripts/build_queue.json`.
See **Queue Format v2** above for the current format and fields.

### Cost Field
For internal tools, use `"$0 (uses existing infrastructure)"` or `"Internal — <benefit>"`. For external APIs, list per-call or monthly cost. Jordan's first question is always "how much does this cost?" — the queue should answer that at a glance.
## Handoff Generation

Every 30 minutes, the queue tick generates two auto-updating documents in `01-HANDOFFS/`:

**`<date>-forge-tasks.md`** — Forge's actionable task list:
- All items assigned to Forge (`platform: desktop`), sorted by priority
- Includes difficulty, status, and full description
- Footer shows how Forge should use the list

**`<date>-jordan-items.md`** — Jordan's action items:
- All items needing Jordan (`assigned_to: jordan` or `needs_jordan: true`)
- Clean bullet list with item IDs and descriptions

The Nightly Build Session (midnight ET) receives the tick's stdout via `context_from`, then works cloud items and generates the Morning Digest source.

### Pipeline Wiring
```
V4 Build Queue Tick (every 30m, no_agent)
  → stdout injected via context_from into ↓
Nightly Build Session (midnight ET, LLM agent)
  → reads handoff files, works cloud items
  → stdout injected via context_from into ↓
Morning Digest (8 AM ET, LLM agent)
  → reads nightly output + handoff files
  → delivers overnight report to HQ
```

## Runner Script (`run_build_queue.py`)

```bash
# Run all pending items
python3 run_build_queue.py

# Run specific item
python3 run_build_queue.py --item my-project

# Generate report only
python3 run_build_queue.py --report

# Show queue status
python3 run_build_queue.py --status
```

## Integration with Hermes Features

### Background Subagents (Parallel Builds)
When items are independent, spawn parallel subagents:

```python
# In your agent's main loop:
delegate_task(tasks=[
    {"goal": "Build and test module A", "toolsets": ["terminal", "file"]},
    {"goal": "Build and test module B", "toolsets": ["terminal", "file"]},
])
```

### Cron Jobs (Scheduled Builds)
Set up a cron to run the queue on a schedule:

```yaml
# Daily build at 9 AM
schedule: "0 9 * * *"
prompt: "Run the build queue: cd /path && python3 scripts/run_build_queue.py"
```

### Multi-Group Support (Proven Pattern)
Each Hermes group can run its own queue independently:
- **Labs** → code projects (pytest, forge test, npm test)
- **HQ** → coordination tasks (status checks, reviews)
- **Strategy** → DeFi/finance (backtests, yield calculations)
- **Entertainment** → content (TTS, video, social)

Jordan's vision: "No matter what group they're in — coding, social media, whatever — they have an automated way to have their agent work on something." The build queue is the universal autonomous pipeline.

## Hermes Async Integration
Leverage Hermes background subagents for parallel builds:
- `delegate_task` with `toolsets=["terminal", "file"]` for independent modules
- `terminal(background=True, notify_on_complete=True)` for long builds
- Reports auto-deliver to originating channel when done
- Queue runner is the sequential fallback when parallel isn't needed

## Customization

### Per-Group Queues
Each Hermes group can have its own queue:
- `Labs/build_queue.json` — code projects
- `Strategy/build_queue.json` — DeFi/finance
- `Entertainment/build_queue.json` — content

### Custom Test Commands
Any shell command that returns exit code 0 = pass:
```json
{
  "test_cmd": "pytest tests/ -v",
  "test_cmd": "npm test",
  "test_cmd": "forge test",
  "test_cmd": "go test ./..."
}
```

### Revenue Tracking
Include revenue info per item for pipeline reporting:
```json
{
  "revenue": "$0.001/call x402",
  "effort": "1 week"
}
```

## Report Format

```
🔧 BUILD QUEUE REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 SUMMARY
   ✅ Shipped: 5
   ❌ Failed: 0
   🧪 Total tests: 71
   ⏱️  Total time: 18s

✅ SHIPPED
   • Deal Tracker — 12/12 tests (17.7s)
   • Agent Arena — 16/16 tests (0.1s)

📋 FULL QUEUE STATUS
   ✅ Deal Tracker — shipped (12/12)
   ⏳ New Project — pending (0/0)

💰 Revenue pipeline: 5 products ready
```

## Session Record (Jun 22, 2026)

9 products shipped in one session, 124 tests, 0 failures. Full pipeline run took 18s.
Products: Deal Tracker, Agent Arena, DeFi Intelligence API, Agent Registration API,
Agent Search API, Fleet Monitor, Starter Kit, Human Feedback API, Routing API.

## Session Record (Jun 24, 2026)

3 products shipped via parallel subagents, 44 tests, 0 failures. Agent Payment Stack complete.
Products: Receipt Generator (13 tests), Rugcheck Payment Classifier (13 tests), Agent-to-Agent Invoicing (18 tests).

## Build Pattern (Proven Across 9 Products)

1. **JSON queue** → `build_queue.json` is source of truth
2. **Runner** → `run_build_queue.py` processes items, runs tests, commits
3. **Report** → structured output: pass/fail, timing, test counts
4. **Status** → `--status` for quick check, `--report` for full scan
5. **Item** → `--item <id>` to run one specific product

### Per-Product Pattern
```
mkdir -p 10-Labs/<name>/{api,tests}
# Write engine module (simulation mode first)
# Write tests (live API or simulation)
# Run tests, fix until green
# Commit, update queue status
```

### Simulation-First Pattern
All 9 products started with simulation mode (no API keys needed).
This lets tests pass immediately and demos work without credentials.
Wire real APIs after the MVP is proven. Example:
```python
class SomeClient:
    def __init__(self, simulation=True):
        self.simulation = simulation
    def get_data(self, query):
        if self.simulation:
            return self._sim_data(query)
        # Real API call here
```

## Three-Tier Build Pattern (V3 — Jul 2026)

**Default to DeepSeek V4 Flash.** Escalate only when the task justifies the cost.

```
T1 — DeepSeek V4 Flash (default, 80%+ of work)
  → Cron jobs, code gen, summaries, routine builds
  → ~$0.15/M in · ~$0.60/M out

T2 — Kimi K2.7 (when Flash isn't reliable enough)
  → Complex debugging, code review, retry on Flash failure
  → ~$2/M (13x Flash)

T3 — Kimi K3 (when the answer matters)
  → Architecture, security audits, design reviews, full-codebase
  → ~$15/M out (100x Flash)
```

**Why this works:**
- Flash builds fast and cheap (80% of work)
- K2.7 catches what Flash missed (15% of work)
- K3 for the big stuff (5% of work — architecture, security, design)
- 95% cheaper than using a premium model for everything

**Cost Comparison:**
| Approach | Cost per Task | Quality |
|----------|---------------|---------|
| Premium model only (K3) | ~$0.15 | High |
| Flash only | ~$0.001 | Medium |
| **Three-Tier** | **~$0.01** | **High** |

**Rule of thumb:** Start with Flash. If it fails or output is wrong, retry on K2.7. Only reach for K3 when the answer is worth $15.

**Queue Integration:**
Each queue item now carries a `recommended_tier` field (set by `build_queue_tick.py`):
- `flash` → T1, default for most items
- `k2.7` → T2, for complex integrations, hard difficulty
- `k3` → T3, for audits, architecture, security, strategy

The tick script auto-classifies items based on name, detail, and difficulty keywords.

## Queue Consolidation & Maintenance

**Jordan's frustrations (July 12, 2026):** Duplicate build queue files across the vault cause confusion. Forge doesn't see everything. Hard to know what's current.

### The Rule
**One canonical source of truth:** `scripts/build_queue.json`. All markdown copies are deprecated.

### Full Audit Command
When suspecting fragmentation, sweep the entire filesystem:
```bash
find /root -name "build-queue*" -o -name "build_queue*" 2>/dev/null | sort
```

### Deprecation Stamp Pattern
Stamp stale markdown copies with a redirect header so no agent or human reads them as current:

> ⚠️ **DEPRECATED — Build Queue moved to JSON**
> The canonical build queue is now at `scripts/build_queue.json`.
> All `N` markdown copies are stale — do not edit or reference this file.
> Run `python3 /root/.hermes/profiles/gentech/scripts/build_queue_tick.py` to regenerate the Forge handoff.

Scripted application:
```python
redirect = "> ⚠️ **DEPRECATED — Build Queue moved to JSON**..."
for path in stale_files:
    if os.path.exists(path) and "DEPRECATED" not in open(path).read():
        with open(path, "w") as f:
            f.write(redirect + content)
```

### What Gets Stale
- Old markdown queue files in vault subfolders (`00-HQ/`, `10-Labs/`)
- **Stale JSON queue files** in `scripts/` — `gentech-queue-remote.json` was a stale duplicate from Jul 11 that survived the first consolidation (`find` filter only caught `build-queue*` / `build_queue*`, not `gentech-queue-*`). **Deleted Jul 15, 2026.**
  - The `find` command should now be: `find /root -name "*queue*" -not -path "*/node_modules/*" 2>/dev/null | sort` to catch all queue-related files regardless of naming convention.
- Their copies in GitHub Pages repos (`ProtoJay4789.github.io/`)
- Their copies in git clones (`repos/ProtoJay4789.github.io/`)
- Portfolio copies (`portfolio/10-Labs/`)

The JSON queue at `scripts/build_queue.json` is the ONLY file that should be edited. All other copies get deprecation-stamped.

## Pitfalls

- **`build_queue.json` top-level format can be dict OR bare list — the tick reader must handle both** — The queue file has historically been either a dict (`{"version": ..., "items": [...]}`) or a bare list of items. `build_queue_tick.py`'s `load_queue()` indexes `q["items"]`, so a bare-list file crashes every run with `TypeError: list indices must be integers or slices, not str`, silently stalling Forge/Jordan handoff generation. **Fix (shipped evolve-68):** `load_queue()` normalizes — dict returned as-is, bare list wrapped as `{"version": "list", "items": <list>}`. If you ever touch the queue format, keep this normalization. Symptom of a broken tick: stale `01-HANDOFFS/*-forge-tasks.md` / `*-jordan-items.md` (no file for today). Verify with `python3 scripts/build_queue_tick.py` → must print "✅ Queue tick complete." and exit 0.
- **Concurrent write protection** — The build queue (`scripts/build_queue.json`) can be silently overwritten by concurrent cron jobs. This happened Jul 2026: a poker session cron's `execute_code` full-write overwrote the queue, losing 8 newly-added Arc/Bankr items. **Prevention:** (1) The build-queue-tick cron (`no_agent=True`) is READ-ONLY — it never writes the queue. (2) Nightly Build Session uses targeted `patch` on specific item fields, never a full file write. (3) When adding items, append to the array — don't rewrite the whole file. (4) Run `scripts/build_queue_tick.py` (not `execute_code with full write`) for any queue mutation.
- **Handoffs go to BOTH brains** — `01-HANDOFFS/` files must be pushed to both vault (Obsidian sync via `ob sync`) AND vault's GitHub remote. The vault's `origin` remote is the **portfolio site** — never push handoffs there. Use `git push vault main` (remote named `vault`) to push to `gentech-vault.git`. Verified Jul 14, 2026: `origin` = ProtoJay4789.github.io, `vault` = gentech-vault.git. Check with `git remote -v` before pushing.
- **"Skip and Focus" — Strategic Cancellation:** Not every opportunity is worth pursuing, even with time remaining. If a project doesn't excite or align with the next 3 moves, cancel it and redirect energy — don't let sunk cost (deadlines passed, effort already spent) keep it in the queue. Cancelled items must have `status: "cancelled"` and a clear `detail` or `notes` field documenting why, so they never re-appear in "pending" counts. Real example (Jul 2026): cancelled #0 OKX AI Genesis Hackathon ($100K prize, deadline 2 days away) and #40 Sui Overflow 2026 to focus entirely on Algorand x402 challenge.
- **Test command must be self-contained** — script runs from the project directory, not vault root
- **Timeout: 120s per item** — long test suites need `timeout` param increased
- **Git commits are automatic** — only commits if tests pass (exit code 0)
- **Queue file is the source of truth** — manual markdown lists get out of sync
- **Parallel builds need independent modules** — shared state causes race conditions
- **Floating point in assertions** — use `abs(a - b) < 0.01` instead of `==` for cost comparisons
- **Enum serialization** — dataclass `to_dict()` doesn't auto-convert enums; add `d["field"] = self.field.value`
- **Floating point comparisons in tests** — `0.1 + 0.2 != 0.3` in Python. When asserting costs/totals, use `assert abs(result - expected) < 0.01` instead of `==`. Proven on Human Feedback API: `5*0.04 + 10*0.04 = 0.6000000000000001`, not `0.60`.
- **`__pycache__` stale imports** — When tests fail but code is correct, stale `.pyc` files load wrong modules. Fix: `find . -name "__pycache__" -exec rm -rf {} +` before re-running. Common with `sys.path.insert` relative paths.
- **Parallel subagent builds** — When shipping multiple independent products (e.g., Receipt Generator + Invoicing + Classifier), delegate each to a separate subagent. They run concurrently and complete in ~60-90s each. After all complete, run each test suite manually to verify. Pattern: `delegate_task(tasks=[{goal, toolsets}, ...])` with 3 parallel tasks max.
- **gh auth not active in session** — After cloning/forking repos, `gh` CLI may not be authenticated. Fix: `unset GITHUB_TOKEN && cat /root/.git-credentials | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|' | gh auth login --with-token`. Verify with `gh auth status`.
- **Nginx .well-known access** — Default nginx denies dotfile access. To serve agent-card.json: add explicit `location /.well-known/` block in server config, fix file permissions (`chmod 644`, `chown www-data:www-data`), reload nginx. Proven on gentechlabs.net.
- **`__init__.py` relative import breaks pytest** — When `__init__.py` uses `from .module import X`, pytest collection fails with `ImportError: attempted relative import with no known parent package`. Fix: wrap in try/except: `try: from .module import X; except ImportError: from module import X`. Proven on Agent-to-Agent Invoicing (Jun 2026): 18 tests errored until __init__.py was patched.
- **Split long reports into multiple messages** — Telegram truncates messages over ~1500 chars. When reporting build queue status, split into separate messages: one for completed items, one for in-progress, one for blocked. Jordan (Jun 2026): "message got cut off and this one is short."
- **`summary.shipped` is cumulative, not derivable from items[]** — Shipped items are REMOVED from the `items[]` array. `summary.shipped` is the only record. A count like `sum(1 for i in items if i.get('status') == 'shipped')` will always return 0. When verifying summary accuracy, use `summary.shipped` directly — do not derive it from the items array.
- **Cancelled items stay in items[]** — Unlike shipped items, cancelled items remain in the `items[]` array with `status: "cancelled"`. They are NOT removed. This means `len(items)` includes cancelled items. When computing `total` for the summary, use `len(items)` (includes cancelled). When computing `pending`, exclude cancelled. The tick script's `summary()` function counts `pending` correctly but `total` should match `len(items)`. Verify with `sum(1 for i in items if i['status'] != 'cancelled')` for active count.
- **Summary counts drift with manual edits** — When adding/removing items via `patch` or `write_file`, the summary counts can fall out of sync. After any queue mutation, run the audit check: load the JSON, count items by status, and verify against `summary`. The tick script (`build_queue_tick.py`) is read-only and never writes the queue — it only reads it. Only the Nightly Build Session or manual edits should mutate the queue.
- **`updated` timestamp format varies between cron jobs** — The Nightly Build Session (04:00 UTC) writes ISO format (`2026-07-23T04:03:07Z`). The Overnight Maintenance cron (06:00 UTC) writes human-readable (`2026-07-23 06:00 UTC`). Both are valid. When doing time-window checks, parse both formats.

## Parallel Subagent Build Pattern (Proven Jun 24, 2026)

When the build queue has **3+ independent products**, spawn parallel subagents — one per product. Each subagent gets:
1. Exact file paths to create
2. Existing code to reference (import paths, dataclass shapes)
3. Branding/design specs (colors, fonts, footer text)
4. Test count target
5. "Run pytest and fix until all pass"

**Verification after parallel build:**
```bash
# Check all products have files
find 10-Labs/<product1> 10-Labs/<product2> 10-Labs/<product3> -type f -name "*.py" | sort

# Run each product's tests independently
cd 10-Labs/<product1> && python3 -m pytest -v
cd 10-Labs/<product2> && python3 -m pytest -v
cd 10-Labs/<product3> && python3 -m pytest -v
```

**Session record:** Jun 24, 2026 — 3 products (Receipt Generator, Rugcheck Payment Classifier, Agent-to-Agent Invoicing), 44 tests total, 0 failures, all shipped in ~2 minutes via parallel delegation.

## Running the Workflow

When Jordan says "run the build list", "go down the queue", or similar — this is a **mandatory trigger** that takes priority over whatever else is in conversation. Stop what you're doing and execute.

### Trigger Phrases (Exact Match)
| Phrase | Action |
|--------|--------|
| "run the build list" | Load queue, process pending items |
| "run the build queue" | Same as above |
| "go down the list" | Same as above |
| "start building" | Same as above |
| "knock out the queue" | Same as above |
| "go down the queue" | Same as above |

These override any other conversation context. Do not interpret them as part of a different topic.

### Develop & Verify Protocol (Mandatory)
Every item follows **develop and verify** — draft cheap, audit expensive:

```
PHASE 1: DEVELOP (cheap model — DeepSeek Flash / GLM-4.7)
  → Read item details from build_queue.json
  → Check existing code at item path
  → Build module + write tests
  → Run tests, iterate until green
  → Update queue status to "built"

PHASE 2: VERIFY (expensive model — GLM-5.2 / audit model)
  → Switch to audit model for verification pass
  → Review for: error handling, edge cases, security, performance, style
  → Fix any issues found
  → Re-run tests
  → Update queue status to "shipped"

PHASE 3: REPORT
  → Summary to wherever Jordan is
  → Include: what shipped, test count, cost, blockers
```

**Cost rule:** If the item's `assigned_to` is `jordan` or `needs_jordan` is `true`, flag it as Jordan action and skip — don't build without sign-off.

### Execution Steps
1. **CHECK COMPLETIONS FIRST (MANDATORY GATE — Jordan directive Aug 10)** — Before picking
   ANY pending item, check what other lanes already completed and handed back. Never redo
   work a group already marked done. This is the "we're cooking with V4" loop.
   ```
   # 1a. Read every group's completion returns
   search_files("*.md", path="/root/vaults/gentech/01-HANDOFFS/*-to-gentech/", target="files")
   read_file("/root/vaults/gentech/01-HANDOFFS/labs-completions.md")
   read_file("/root/vaults/gentech/01-HANDOFFS/treasury-completions.md")
   read_file("/root/vaults/gentech/01-HANDOFFS/forge-completions.md")
   read_file("/root/vaults/gentech/01-HANDOFFS/entertainment-completions.md")
   read_file("/root/vaults/gentech/01-HANDOFFS/hq-completions.md")
   # 1b. Extract the #<id> shipped tokens and mark those queue items shipped/skip them
   ```
   Any item ID found in a `*-completions.md` file (or `<lane>-to-gentech/` return notes) is
   DONE — set its queue status to `shipped`, note the lane + date, and skip it. Run the
   `group-returns-scanner.py` first to get this as structured JSON:
   ```
   python3 /root/.hermes/profiles/gentech/scripts/group-returns-scanner.py
   ```
2. **Load queue** — Read `/root/vaults/gentech/scripts/build_queue.json`
3. **Find first pending** — Items with `"status": "pending"`, sorted by `priority` ascending
4. **Check item** — If `assigned_to` is not you (and not `auto`), skip. If `needs_jordan` is `true`, flag as Jordan action.
5. **Develop** — Phase 1 on cheap model
6. **Verify** — Phase 2 on expensive model
7. **Report** — Phase 3

**Batch auth:** "green light" / "go down the list" = process sequentially without pausing between items.

-----

## Related

- `build-queue-processor` — Per-item develop → verify → ship pipeline (used by Nightly Build Session)
- `gentech-build-workflow` — 7-phase build pipeline (for complex projects)
- `deploy-and-verify` — Post-build deployment verification
- `agent-coordination` — Multi-agent task routing
- `references/v4-overnight-pipeline.md` — **Nightly Build Session + Morning Digest**. Silent overnight builds. Active configuration.
