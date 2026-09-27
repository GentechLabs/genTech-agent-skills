# Agensi — Paid SKILL.md Marketplace (Aug 22, 2026)

Agensi (agensi.io) is a curated marketplace for SKILL.md skills. Creators keep
**70%** of revenue (70/30 split). Crossed 2,000 skills, 3,000 users, 50K
monthly visitors within 3 months of launch (Jul 2026). This is a **paid**
distribution channel — unlike npx skills / EduHub / ClawHub which are free
directories.

## What Actually Sells (per Agensi's own guide)

Best-sellers save developers time on **repetitive, high-stakes** tasks:
- **Code review** — opinionated review standards ("review this React component
  against our hooks/error-boundary/accessibility patterns")
- **Testing** — pytest fixtures/parametrized tests, Jest async patterns
- **DevOps** — Dockerfile best practices, CI/CD, Kubernetes manifests
- **Framework starters** — Next.js/Django/FastAPI scaffolding with opinionated
  defaults

## Pricing

- **$3–10** — sweet spot for individual skills (low enough no purchase approval,
  high enough to add up with volume)
- **$15–25** — comprehensive bundles ("complete React dev kit")
- **Free skills** — list 2-3 free to build reputation, then premium versions

## Economics (70/30 split)

| Price | 100 sales | 500 sales | 1,000 sales |
|-------|-----------|-----------|-------------|
| $5    | $350      | $1,750    | $3,500      |

## Listing Workflow

1. Pick a domain you know well (daily workflow has skills worth packaging)
2. Create a SKILL.md file
3. **Test it across at least 2 agents** (Claude Code + one other) — this is the
   key pre-listing requirement
4. List on Agensi with clear description + tags
5. Promote on Reddit (r/AI_Agents, r/devops), dev.to, Discord communities

## Our Picks (drafted Aug 22, saved to vault
`09-Green Room/agensi-skill-listings-draft-2026-08-22.md`)

| Skill | Price | Category | Why |
|-------|-------|----------|-----|
| safe-update-restart | $6 | DevOps | "Never blind-restart a production VPS" — #1 selling category |
| x402-payments | $8 | Web3/Payments | Flagship + hottest standard in agent economy |
| handoff-mesh | $7 | Agent Orchestration | Multi-agent comms = fastest-growing need |
| output-enforcer | $5 | Testing/Reliability | Saves hours on malformed LLM outputs |

## Pitfall — 2-Agent Test Requirement

Agensi requires testing each skill on **Claude Code + one other agent** before
listing. Our skills are Hermes-tested but not Claude Code-tested. Claude Code
CLI (`npm install -g @anthropic-ai/claude-code`) needs an `ANTHROPIC_API_KEY`
or `claude auth login` (browser OAuth) — neither was configured on the VPS as
of Aug 22. **Fallback:** test on opencode (free models, `opencode auth list`
shows 0 creds but free models available) as the "second agent" to get 90% of
the way, and flag the Claude Code pass as a to-do until a key exists. Do NOT
list without at least one non-Hermes agent test.
