# Internet Court — Vendoring a Skill Into the Package

**What it is:** Internet Court (internetcourt.org) is an open skill for agent-to-agent contracts. It vendors 69+ partner skills from 25+ founding partners into one master router SKILL.md. Each partner gets a directory under `vendored/<owner>/<skill>/` with a SKILL.md and LICENSE.

**Repo:** `github.com/internet-court/internet-court-skill`
**Install:** `git clone` into Hermes skills dir, or `openclaw skills install git:internet-court/internet-court-skill`

## When to Use This Pattern

When registering an agent API or tool as a vendored sub-skill inside an existing open-source skill package (not adding to a curated list, not submitting to a marketplace). The key difference from directory listing: you're contributing code/files to a repo that other agents load as a dependency.

## Pre-Submission Checklist (Mandatory)

Same as platform-registration general workflow, but with additional checks:

1. **Check README + NOTICE.md** — The package has attribution files. Find the right spot alphabetically.
2. **Check existing vendored structure** — `curl -sL https://api.github.com/repos/internet-court/internet-court-skill/contents/vendored` to see all partners.
3. **Check the master SKILL.md routing tables** — Does your skill fit an existing layer (1-6) or need a new row?
4. **Check NOTICE.md format** — Each partner gets a row: `| owner | Source | License (SPDX) | Copyright | Skills |`

## Directory Structure to Create

```
vendored/gentech/gentech-agent-kit/
├── SKILL.md      ← YAML frontmatter + markdown body
├── LICENSE       ← MIT (or your chosen license)
```

### SKILL.md Frontmatter

```yaml
---
name: gentech-agent-kit
description: "Trigger description — when should the agent route here. Use whenever [...]"
user-invocable: true
disable-model-invocation: true
allowed-tools: ["Bash(uvx *)", "Bash(npx *)", "Bash(curl *)", "Bash(git *)"]
---
```

**Rules:**
- `description` is the trigger field — agents match against it. Be thorough but concise.
- `user-invocable: true` lets humans explicitly request the skill.
- `disable-model-invocation: true` prevents the LLM from self-calling — tool execution only.
- `allowed-tools` restricts what shell commands the skill can run. Be specific.

### SKILL.md Body

Structure:
1. **Install** — one-line commands (uvx, npx, git clone)
2. **Configuration** — env vars needed
3. **Tools table** — organized by Internet Court layer
4. **Use Cases in Internet Court** — how agents would use your tools in the stack
5. **Reputation & Trust** — license, source, audit status

### NOTICE.md Entry

Add alphabetically by owner name:

```
| gentech | [ProtoJay4789/genTech-agent-kit](https://github.com/ProtoJay4789/genTech-agent-kit) | MIT | Copyright (c) 2026 GenTech Labs | gentech-agent-kit |
```

## Verification

1. The skill parses: `python3 -c "import yaml; yaml.safe_load(open('vendored/gentech/gentech-agent-kit/SKILL.md').read().split('---')[1])"`
2. The paths in the router's `vendored/` table match the directory structure
3. NOTICE.md entry is alphabetically correct

## Pitfalls

- **Fork first** — you don't have push access to the upstream repo
- **Existing PR from previous fork** — `gh pr list --head ProtoJay4789:main` may show a stale PR. Create a new branch with a different name
- **SKILL.md description is the trigger** — agents route by matching this text to user intent. Make it broad enough to catch relevant queries but not so broad it triggers falsely
- **Licenses** — The repo root is MIT, but each vendored skill carries its own license. Include a LICENSE file in your skill directory
- **Master SKILL.md routing** — The Internet Court master SKILL.md has routing tables per layer. Your tools may not need updates to those tables if they fit existing rows (e.g., "Execution" layer covers most tool categories without needing a new row)
- **OpenClaw plugin** — Internet Court also has `openclaw.plugin.json` for OpenClaw compatibility. Consider adding one if your skill targets OpenClaw users
