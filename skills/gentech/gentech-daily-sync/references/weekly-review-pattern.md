# Weekly Sunday Review — Pattern Reference

## Purpose
Three-section review delivered every Sunday. Independent sections — if one fails, continue with the others.

## Sections

### 1. Brain Sync (local only)
- Review vault activity from the past week (7 days)
- **Primary signal:** `git log --since='7 days ago' --oneline --all` — commit-driven insight is the most reliable source in solo operation (no daily notes directory exists)
- **Vault scans (in order of usefulness):**
  1. `09-Green Room/` — build logs, design docs, active work
  2. `11-Mess Hall/YYYY/W##/` — weekly context folders with daily notes
  3. `11-Mess Hall/ideas.md` — checkbox list of ideas to consider
  4. `00-HQ/` and `02-Labs/` — operational decisions and builds
  5. `03-Strategies/` and `Gentech/handoffs/` — research and agent handoffs
- **NOTE — These vault paths are STALE and don't exist:**
  - `08-Daily/` — legacy, removed. Use `git log` instead.
  - `Daily/` at vault root — doesn't exist. No daily notes directory.
  - `11-Mess Hall/daily/` — never created in current structure. Use `11-Mess Hall/YYYY/W##/`.
  - `00-Working-Memory.md` — multi-agent era artifact. Sprint state in `today-context.md`.
  - `11-Mess Hall/considerations.md` — doesn't exist. Use `11-Mess Hall/ideas.md`.
- Output: Write consolidated review to `11-Mess Hall/YYYY/W##/YYYY-MM-DD-weekly-review.md` (all 3 sections in one file)
- Include: TL;DR, key decisions table, hackathon status, completed items, blockers, system health, lessons learned, forward hook

### 2. Skills Update (deliver to HQ)
- Check upstream: `cd /usr/local/lib/hermes-agent && git fetch origin && git rev-list --left-right --count HEAD...origin/main`
- Categorize commits: `git log HEAD..origin/main --oneline | grep -ci "security|harden|inject|bypass"` for security count
- Compare skills: `diff <(find skills/ -name SKILL.md | sed ...) <(find ~/.hermes/profiles/gentech/skills/ -name SKILL.md | sed ...)`
- Check optional-skills for new additions
- Output: Write to `11-Mess Hall/YYYY/W##/YYYY-MM-DD-weekly-review.md` (consolidated)
- Deliver summary to HQ (-1003863540828)

### 3. x402 Ecosystem Scan (deliver to Labs)
- Research x402 protocol developments, new integrations, ecosystem growth
- **Primary:** Use `mcp__blockrun__blockrun_search` (the correct MCP tool name — NOT `mcp_blockrun_blockrun_search` or `blockrun_search`). 2-3 targeted queries. Check wallet balance FIRST via `mcp__blockrun__blockrun_wallet action:"status"` — paid tool sessions need funded wallets or they return `Payment was rejected`.
- **Belt:** `web_search` (Firecrawl) and `web_extract` — work when the Nous Portal has credits.
- **Suspenders:** `mcp__blockrun__blockrun_exa(path="search")` — neural web search via Exa, different payment pool.
- **Last resort (all tools fail):** The vault snapshot (`references/x402-ecosystem-snapshot-2026-07.md` in `gentech-daily-sync` skill) contains the last known-good baseline. Rely on it for the scan and explicitly note in the report that live research was unavailable. This is preferable to fabricating data.
- **Alternative:** `delegate_task` with 3 parallel research subagents for deeper dives:
  1. **Protocol developments** — new integrations, partnerships, Foundation updates
  2. **On-chain metrics** — transaction volume, active agents, implementation quality
  3. **Grants & SDKs** — funding opportunities, new SDK releases, GitHub repo activity
- Compile into report with sections: Executive Summary, Integrations, Metrics, Competitors, Tooling, Strategic Takeaways, Recommended Actions
- Include implications table mapping ecosystem signals to GenTech's position and actions
- Save to consolidated weekly review file
- Deliver summary to Labs (-1003872552815)

## Pitfalls
- **Stale vault paths:** Earlier docs reference `08-Daily/`, `00-Working-Memory.md`, `Daily/`, `11-Mess Hall/daily/`, and `considerations.md` — none of these exist in the current vault structure. The git log is the primary signal source. Daily notes are in `11-Mess Hall/YYYY/W##/` per-week folders. Ideas are in `11-Mess Hall/ideas.md`.
- **CRON DELIVERY — DO NOT USE `hermes send`**: In a cron job context, the system delivers the final response automatically to the configured destination. Do NOT attempt `hermes send --chat-id "..." --message "..."` — the shell will expand special characters (backticks, emoji, markdown) as commands, causing failures. Just produce the report as your final response and let the cron system handle delivery.
- **delegate_task optional for x402 scan**: The pattern recommends 3 parallel subagents via `delegate_task`, but sequential web research (`web_search` + `web_extract`) also works well. Use parallel delegation when the agent model supports it well; sequential research is a valid fallback.
- **Git fetch required:** The skills update must `git fetch origin` before checking behind count — stale local refs give wrong numbers.
- **No ob sync:** Obsidian CLI sync is not configured. Skip that step.
- **Telegram truncation:** Long Sunday Review messages (~80+ lines) may be cut by Telegram's message length limits. The full review is always saved to the vault file. If delivered as a cron response, the vault file is the authoritative version.
- **ALL research tools unavailable:** If BlockRun MCP is unreachable AND Firecrawl/Web tools are not configured, ALL three x402 research paths fail simultaneously. Do NOT fabricate data or repeat stale baseline numbers as if they're fresh. Instead: (1) note clearly in the report that live research was unavailable, (2) use the vault snapshot (`references/x402-ecosystem-snapshot-2026-07.md`) as the baseline, (3) inject any ecosystem signals discovered through local vault activity (build queue items, grant applications, new hackathons) as the week-over-week delta. The snapshot path is in the `gentech-daily-sync` skill's linked files — extract and reference it by name so future scans know the baseline timestamp.
- **BlockRun wallet funds affect x402 scan:** The blockrun_search tool charges $0.025 × max_results (~$0.26 for default max_results=10). If the BlockRun wallet has low balance, searches fail with `Payment was rejected`. Run `mcp__blockrun__blockrun_wallet(action="status")` first to check. If under $1, scale down max_results or fall back to vault snapshot. Do NOT retry a failing paid search 3+ times — that burns the wallet to $0.