---
name: hermes-update-assessment
description: "When Hermes updates, translate changelogs into user-relevant insights. Focus on what matters to THIS user's stack, not everything Nous ships."
category: gentech-ops
version: 2.0.0
tags: [hermes, updates, agent-kit, user-centric, maintenance]
---

# Hermes Update Assessment — User-First

## Core Principle
Nous Research has unlimited tokens and 10+ agents building Hermes. There will be MANY updates. Most won't matter to the user. Our job is to filter the noise and surface only what's relevant to THEIR stack.

**Don't report what changed. Report what it means for them.**

## Trigger
- After every Hermes update (`hermes update`)
- When Nous Research announces a new release on X
- Weekly cron check for new versions
- **The Personal Assistant Suite runs this loop weekly (MONDAY 08:00) + after updates** — see the EVOLUTION section in the PA prompt and `personal-assistant-suite` skill. The PA writes dated entries to `/root/vaults/gentech/10-Labs/hermes-evolution-log.md`.

## Workflow

### Step 1: Get the Changelog
```bash
# Check current version
hermes --version

# Get latest release notes (with version tag)
curl -s https://api.github.com/repos/NousResearch/hermes-agent/releases/latest | python3 -c "import sys,json; r=json.load(sys.stdin); print(f\"Latest: {r['tag_name']}\n{r['body'][:1500]}\")"
```

**Pitfall: Large changelogs truncate** — Recent Hermes releases have 15,000+ character changelogs that get truncated. Pull in chunks and scan for relevant patterns:
```bash
# Pull changelog in chunks
curl -s https://api.github.com/repos/NousResearch/hermes-agent/releases/latest | python3 -c "import sys,json; r=json.load(sys.stdin); body = r.get('body', ''); print(body[2000:4000] if body else '')"

# Or search for specific patterns (security, background, cron, mcp, delegate)
curl -s https://api.github.com/repos/NousResearch/hermes-agent/releases/latest | python3 -c "import sys,json; r=json.load(sys.stdin); body = r.get('body', ''); import re; matches = re.findall(r'.{0,300}(?:delegate|background|parallel|fan.?out|security|mcp|cron).{0,300}', body, re.IGNORECASE); print('\n---\n'.join(matches[:5]) if matches else 'No matches')"
```

### Step 2: Filter by User's Stack
Read the user's profile to know what they use:
- What providers? (custom, opencode-go, anthropic, etc.)
- What channels? (telegram, discord, etc.)
- What tools? (terminal, browser, file, etc.)
- What cron jobs? (portfolio, scanner, monitor, etc.)
- What MCP servers? (blockrun, wurk, pay, etc.)
- What skills? (defi, crypto, github, etc.)

**Then filter the changelog:**
- Does this affect their provider? → Report
- Does this affect their channels? → Report
- Does this affect their tools? → Report
- Does this affect their cron jobs? → Report
- Does this affect their MCP? → Report
- Does this affect their skills? → Report
- None of the above? → Skip it

### Step 3: Translate to User Language
Don't say: "Background subagents now dispatch via delegate_task(background=true)"
Say: "I can now run long tasks in the background while we keep talking — no more sitting blocked waiting"

Don't say: "Memory tool gained atomic batch operations"
Say: "Memory updates are now faster and never fail mid-edit — I can clean up and add new info in one shot"

Don't say: "Curator consolidation pass disabled by default"
Say: "This update saves you money — routine skill checks no longer burn API tokens"

### Step 4: Update Agent Kit If Needed
Only update when:
- Distribution format changed (rare)
- Skill format changed (affects how we write skills)
- New features we should be using (background subagents, memory ops)
- Security fixes (must update)

### Step 5: Report
Produce a USER-FOCUSED report:

```
🔄 Hermes v[NEW] — What It Means for You

## TL;DR
[1-2 sentences: should you care or not?]

## What Changed (That Matters)
1. [Feature] — [what it means for YOUR stack]
2. [Feature] — [what it means for YOUR stack]

## What You Can Do Now
- [New capability they couldn't do before]

## Agent Kit Updated?
- Yes → [what changed]
- No → [why not needed]

## Skip This Update If...
- [Conditions where update doesn't matter]
```

## What NOT to Report
- UI/theme changes (unless user customizes skins)
- Internal refactors (no user impact)
- New features the user doesn't use (e.g., if they don't use Discord, skip Discord changes)
- Developer-facing changes (PRs, tests, CI)
- Bug fixes for features the user doesn't use

## Pitfalls
- Don't overwhelm with details — users don't care about 1,475 commits
- Don't report "nothing changed" — silence is fine
- Don't update Agent Kit just because something changed — only when it affects users
- Some updates are for other users (enterprise, teams) — skip those
- Large configs truncate: config.yaml files can be 800+ lines. Use search_files with patterns or grep instead of read_file to find specific settings:
  ```bash
  # Search for provider/model/channel patterns
  search_files file_glob=config.yaml output_mode=content path=~/.hermes/profiles/gentech pattern="provider|model|channel"
  
  # Or use grep directly
  grep -E "(provider|model|channel)" ~/.hermes/profiles/gentech/config.yaml
  ```

## Production Safety
- Don't update Hermes in production without testing first
- Some changes are cosmetic (UI/themes) — skip those
- Provider changes may affect cron job model pinning
- Distribution format changes need careful testing before pushing

## Tags
#hermes #updates #agent-kit #maintenance #assessment
