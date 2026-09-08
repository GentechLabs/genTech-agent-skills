# a2a Borrows — LoopX + Multi-Agent Trust Layer (worked examples, Aug 3 2026)

Two framework evaluations the same session, both using the "eat the meat, spit out the bones" borrow pattern. Both wired into the a2a design (Jordan's #1 priority: agent-to-agent comms).

## 1. LoopX (huangruiteng/loopx) — borrow 3 primitives, don't adopt

- **Repo:** 680★, 55 forks, MIT, Python 3.11+ stdlib-only, v0.4.x. Agent-agnostic "state kernel / control plane" for long-running agent work — "agent-native Kanban."
- **Why NOT adopt:** our Hermes cron + queue + kanban already cover orchestration better (decomposition playbook, parent-link dependency graph, reclaim/reassign recovery). 953-branch churn = heavy. Bytedance-adjacent author — don't build a2a core on a corporate-owned control plane.
- **Borrowed 3 primitives** (wired into `agent-handoff-enforcement`):
  1. **Explicit user gates** — every human-gated item = stated question + owner + deadline + no-response fallback. Never vague "waiting on Jordan."
  2. **Quota-aware `should-run`** — before a scheduled run, ask "is there a useful transition left?" If no → stay quiet, spend no tokens. Formalizes the `no_agent` silent-on-empty-stdout watchdog pattern.
  3. **Evidence lineage** — every handoff carries a 3-line stub: `changed:` / `validated:` / `next-todo:`.
- **Vault note:** `09-Green Room/specs/loopx-a2a-handoff-borrow.md`

## 2. awesome-llm-apps Multi-Agent Trust Layer — build on (Apache-2.0)

- **Repo:** 130K★, Apache-2.0, cloned at `/root/repos/awesome-llm-apps/` (depth-1). Trust layer is a single self-contained Python file — **verified it runs clean** (demo passed: trust scoring + scope narrowing + policy + audit).
- **The 5 mechanisms:**
  1. **Agent identity + human sponsor** — every agent anchored to an accountable human.
  2. **Trust scoring (0–1000)** — TRUSTED 900+/STANDARD 700+/PROBATION 500+/RESTRICTED 300+/SUSPENDED <300. Deltas: `task_completed`+10, `stayed_in_scope`+5, `delegation_success`+15; `scope_violation_attempt`−50, `inaccurate_output`−30, `security_violation`−100, `delegation_failure`−25.
  3. **Delegation scope narrowing** (THE standout) — `DelegationScope.narrow()` computes intersection for sub-delegation: allowed_actions ∩, denied ∪, min(max_tokens, time_limit, max_sub_delegations). Least-privilege for agent-to-agent.
  4. **Role-based policy engine** — role base_trust_required + allowed/denied actions + delegation check; RESTRICTED requires human approval.
  5. **Full audit trail** — queryable `(timestamp, event, agent_id, action, delegation_id, result, details)`.
- **Security bug they fixed** (capture for OUR a2a): an empty `allowed_actions` set previously read as "all allowed" (wildcard) — a least-privilege hole. Fix: `None` sentinel = all, empty set = nothing. **Lesson: empty allow-list must mean DENY, never ALLOW.**
- **What we take:** delegation-scope narrowing + trust scoring as the a2a governance substrate. Map: Gentech=orchestrator(900), Forge=specialist, GTA executor=restricted. Wire delegation narrowing into `agent-handoff-enforcement`.
- **Vault note:** `09-Green Room/specs/a2a-trust-layer-deep-dive.md`

## Also relevant
- **KeeperHub MCP wiring** — the `multi_mcp_agent_router` pattern (specialist agents each connected to ONLY the MCP servers they need, routed by intent) is the right shape for wiring GTA → KeeperHub MCP. Don't give the arb executor every tool; scope it.
- **KeeperHub build** (GO Aug 3): deadline Aug 13, must include a **live transaction link** executed through KeeperHub (non-negotiable judging requirement). Auth needs a `kh_` org API key from app.keeperhub.com → Settings → API Keys (headless VPS can't do browser OAuth). Endpoint `https://app.keeperhub.com/mcp` reachable, OAuth discovery at `/.well-known/oauth-authorization-server`. Plan: `09-Green Room/specs/keeperhub-build-plan.md`.
