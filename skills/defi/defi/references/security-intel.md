# Security Intelligence (Full)

> Absorbed from `defi` skill §4. Post-incident recon workflow.

## Workflow

1. **Define scope** — which protocol, what incident, timeframe
2. **Gather official sources** — blog archive, GitHub releases, governance portals
3. **Search protocol changes** — GitHub commits post-incident, Snapshot/Tally proposals
4. **Check on-chain/analytics** — Dune dashboards, on-chain flows
5. **Competitor intelligence** — rival protocols capitalizing on incident
6. **Compile report** — structured intelligence with risk assessment
7. **Save to vault** — date header, risk level, action items

## Risk Level Rubric

| Level | Definition |
|-------|-----------|
| IMPROVED | Protocol enacted on-chain upgrade reducing recurrence risk |
| UNCHANGED | No protocol-level change; only operator-level responses |
| WORSENED | New attack vectors, protocol silent, or contagion risk increased |

## Known Obstacles & Workarounds

| Obstacle | Workaround |
|----------|------------|
| Google search bot detection | Navigate direct URLs; skip search |
| Dune Cloudflare block | Try advanced stealth; document gap |
| X/Twitter login wall | browser_navigate may expose posts |
| JS-heavy docs | browser_console execute JS selectors |

## Report Template

```markdown
# [Protocol] Incident Report — [Date]

## Summary
[What happened, when, impact]

## Protocol Response
[Official statements, blog posts, governance]

## On-Chain Evidence
[Transactions, flows, contract changes]

## Competitor Response
[How rivals are capitalizing]

## Risk Assessment
- **Risk Level:** [IMPROVED/UNCHANGED/WORSENED]
- **Recurrence Risk:** [Low/Medium/High]
- **Contagion Risk:** [None/Limited/Significant]

## Action Items
- [ ] [Specific action]
```
