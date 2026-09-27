# OpenClaw Master Skills — Evaluation Notes

**Source:** `github.com/LeoYeAI/openclaw-master-skills`
**Date:** 2026-06-01
**Total Skills:** 1609+

## Category Breakdown (from README)

- AI & LLM Tools (50)
- Search & Web (21)
- Productivity & Office (43)
- Development & DevOps (87)
- Marketing & Growth (40+)
- Media & Creative (30+)
- Finance & Trading (20+)
- Communication (25+)
- Smart Home & IoT (15+)
- Memory & Agent (20+)
- Security (10+)
- Data & Analytics (15+)
- Social & Content (20+)

## Skills Evaluated

### Installed (4)

| Skill | Category | Why Installed |
|-------|----------|---------------|
| `agent-team-orchestration` | DevOps | Multi-agent task routing, handoff protocols |
| `agent-security-hardening` | DevOps | 7 rules of prompt injection defense |
| `stock-analysis` | Finance | Yahoo Finance, 8-dimension scoring, rumor scanner |
| `bitmart-wallet` | Blockchain | 12 endpoints, no API key, 5 chains |

### Evaluated but Skipped

| Skill | Why Skipped |
|-------|-------------|
| `binance-derivatives-trading-portfolio-margin` | Binance-specific, not our focus |
| `agent-memory` | Basic, we already have better (vault + memory tool) |
| `vincent-trading-engine` | Polymarket + HyperLiquid specific |
| `chainbase-openapi-skill` | Requires API key, we have bitmart-wallet (no key) |
| `elite-longterm-memory` | Requires LanceDB plugin, we have vault memory |

## Adaptation Notes

OpenClaw skills use:
- `{baseDir}` variable → replace with actual path
- `uv run` commands → replace with `python3` or `terminal()`
- `~/.clawdbot/skills/...` → replace with `~/.hermes/profiles/<profile>/skills/...`
- `clawhub install` → use `skill_manage(action='create')`

## Key Insight

The value is in the SKILL.md content (knowledge, workflows, patterns), not the wrapper tooling. Adapt the paths and commands, keep the knowledge.
