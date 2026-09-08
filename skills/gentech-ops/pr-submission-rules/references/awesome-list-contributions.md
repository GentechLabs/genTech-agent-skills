# Awesome-List Contribution Patterns

Awesome-list repos typically **don't have PR templates**, but they **do have CONTRIBUTING.md** with specific rules. Here's what to check for each one.

## Common Awesome-List Rules

| Rule | What to Check | How to Fix |
|------|---------------|------------|
| **Alphabetical order** | Entry must be in the correct position relative to neighbors | `grep -n -i "^- \[" README.md` to find the section, then verify your entry's position |
| **Description style** | Does it use `—` or `-`? Capitalized? Specific length? | Match the first 3-5 entries in that section's format exactly |
| **Link format** | `[Name](url)` or `[Name](url) — description` | Match existing entries |
| **Category/section** | Is your entry in the right section? | Check that the section heading matches your service type |
| **List item prefix** | `-` or `*`? Trailing colon? | Match existing convention |

## Awesome Lists We've Submitted To

| Repo | Has Template? | Key Rules |
|------|---------------|-----------|
| solana-foundation/awesome-solana-ai | No | Alphabetical within section, `- [name](url) - description` format |
| punkpeye/awesome-mcp-servers | No | Glama badge required for MCP servers |
| bitrefill/awesome-agentic-payments | No | Section-based, service provider format |
| xpaysh/awesome-x402 | No | Alphabetical in Ecosystem Projects |
| Merit-Systems/awesome-agentic-commerce | No | Service provider with description |
| jamesmurdza/awesome-ai-devtools | Yes | Has ## Description + ## Checklist template — MUST match exactly |

## The "No Template" Pattern

When a repo has no PR template:
1. **Do not invent sections** — Don't add `## Description` or `## Checklist` if they're not in the repo's template
2. **Do check CONTRIBUTING.md** — Many awesome lists have format rules there
3. **Match existing entries** — The safest format is to look at recently merged PRs
4. **Keep the PR body short** — Just describe what you added and why, no ceremony

## Post-Submit Verification

Even without a template bot, check after 60 seconds:
```bash
gh pr view <number> --repo <owner>/<repo> --json mergeable,comments
```

- `MERGEABLE` = good
- `CONFLICTING` = needs rebase (upstream added new entries in the same section)
- Any bot comments = review and fix immediately
