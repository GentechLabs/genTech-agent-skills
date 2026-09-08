# Ecosystem Research Workflow

**Pattern:** Structured research before any PR or integration work. Used for Injective iAgent (Jul 23) and Circle Skills (Jul 23).

## Research Pipeline

When a queue item says "Research X" or you encounter an unfamiliar ecosystem project:

### Phase 1: Repo Surface Scan
```bash
# 1. Read the repo page — stars, forks, language, last commit, contributors
web_extract(urls=["https://github.com/owner/repo"])

# 2. Read the raw README
web_extract(urls=["https://raw.githubusercontent.com/owner/repo/main/README.md"])

# 3. Read key source files (agent_server.py, SKILL.md, main.py, etc.)
web_extract(urls=["https://raw.githubusercontent.com/owner/repo/main/agent_server.py"])
```

### Phase 2: Ecosystem Context
```bash
# 4. Search for ecosystem news (blog posts, announcements, partnerships)
web_search(query="project x402 integration 2026")
web_search(query="project AI agent payments")

# 5. Check related repos (SDKs, plugins, examples)
web_search(query="github owner related-repo")
```

### Phase 3: Integration Analysis
- **Architecture fit:** Does the project's architecture support our contribution pattern?
- **x402 alignment:** Is the project x402-native, x402-adjacent, or unrelated?
- **Contribution readiness:** Open issues? Active maintainers? Forking allowed?
- **Strategic value:** Does this reach our target audience (agent builders, x402 devs)?

### Phase 4: Document
Write a structured research doc to `10-Labs/<project>-research.md`:

```markdown
# <Project> — Research

**Date:** YYYY-MM-DD
**Queue Item:** #N — Name
**Priority:** High/Medium/Low
**Difficulty:** Easy/Medium/Hard

## Key Findings
- Stars, forks, language, last commit
- Key architecture details
- x402 alignment
- Strategic value

## Integration Opportunity
- What we can contribute
- Pattern (same as GOAT AgentKit, etc.)
- Specific files to modify

## Recommended Approach
1. Fork repo
2. Add X
3. Submit PR

## Blockers
- None / Jordan dependency / etc.
```

### Phase 5: Update Queue
- Update the item's `note` field with "RESEARCHED YYYY-MM-DD: [summary]"
- Update `detail` with current findings
- Set `status: "pending"` (ready to build) or `status: "blocked"` (needs Jordan)

## Pitfalls
- **README may be on a different branch** — try `main`, `master`, `develop`
- **Repo may be 404** — check if it was renamed or made private
- **Raw file URLs differ** — some repos use `master` instead of `main`
- **Blog posts are more current than repos** — always search for recent ecosystem news
- **Don't over-research** — 3-5 web_extract calls + 2-3 web_search calls is enough. If you can't find the answer in 10 calls, document what you know and move on.
