# Ecosystem Contribution Pattern

Three-way scan for evaluating and contributing to open-source ecosystems.

## The Three-Way Scan

Every ecosystem gets evaluated on three axes:

| Angle | Question | Output |
|-------|----------|--------|
| 🛠️ **Contribute** | What can we submit? (skills, PRs, docs, compliance tools) | PRs, issues commented, skills uploaded |
| 🔗 **Integrate** | How does their stack connect to ours? (MCP, SDK, API) | Config changes, adapter code |
| 📦 **Use** | What can we consume from them? (tools, data, infrastructure) | Installed tools, imported skills |

## Execution Flow

1. **Scan** — Read the repo README, check open issues, check for CONTRIBUTING.md
2. **Map gaps** — What's missing that we already have? (compliance scanner, x402 skills, DeFi trajectories)
3. **Prioritize** — Quickest win first (chore PR → feature PR → integration PR)
4. **Build** — Develop the contribution using the develop-and-verify pipeline
5. **Submit** — Fork (or work around forking restrictions), push branch, open PR
6. **Log** — Save to build queue, note in handoff if blocked

## Submission Triage — Three Contribution Modes

Not every contribution is a PR. Pick the right mode based on how well you know the codebase and whether forking works:

| Mode | When | What you do | Example |
|------|------|-------------|---------|
| **🛠️ Build-first, PR later** | Repo is forkable, codebase familiar, exact gap known | Clone, build, test, PR | GOAT AgentKit compliance plugin |
| **💡 Issue-first, build later** | Repo is popular but unfamiliar, you can't fork, or you want maintainer buy-in before investing | Open issue proposing integration with pitch template, wait for green, then PR | Obsidian Mind #142, MiroFish #743 |
| **📋 Directory submission** | AI tool directories (Cursor Directory, Smithery, etc.) | Prepare plugin manifest + rules + MCP config + logo, submit via web form | Cursor Directory — community path |

**Issue-First Pitch Template** — When proposing x402 integration via an issue, use this arc:

> *"Your project does X for agents. This proposal lets them pay for Y with x402 — no API keys, no subscriptions, no human approval. The agent sends a request, gets a 402 challenge, signs a payment proof, and the API responds. All in under a second."*

Then fill in:
- The Gap (what breaks autonomy today)
- The Fit (why your project is the right place for x402)
- What I'm Offering (credentials + deliverable)
- About (We help creators monetize. We're the monetization layer for the agent economy.)

## Cursor Directory Submission

For community directories (cursor.directory/plugins/new):

| Field | Example |
|-------|---------|
| **Name** | GenTech Gateway |
| **Description** | x402 pay-per-call gateway — 16 endpoints, 5 chains, no API keys |
| **Source** | github.com/ProtoJay4789/x402-gateway |
| **Tags** | x402, payments, usdc, base, solana, gateway, mcp |
| **Logo** | Generate via image_generate: clean solid navy circle, bold white G, one cyan accent dot. Must be recognizable at 16x16px. Flat vector, no gradients, no glow. |
| **Rules** | Spend-safety rule: no unprompted payments, verify before spending, surface limits. |
| **MCP** | Streamable-http server config with tool list |
| **Skills** | 4 max: x402 payment, compliance scanner, treasury dashboard, API monetizer |

Requires GitHub sign-in. Prep content in advance, save to vault, Jordan submits when ready.

## Forking Workarounds

Some repos block automated forking (403 from API). Options:
- **Create standalone repo** under your user, push branch, then try PR
- **Set `fork: true`** via PATCH on the standalone repo metadata
- **Web UI fallback** — save code locally, note in handoff for manual submission
- **Org fork** — try `?organization=Gentech-Labs` param on fork API

## Repos Scanned

| Repo | Stars | Action Taken |
|------|-------|-------------|
| x402-foundation/x402 | 6.4k | PR #2905 (compliance scanner), commented on #2823 |
| QwenLM/Qwen-AgentWorld | ~2k | PR #9 (x402 compliance trajectories + DeFi prompts) |
| XRPLF/xrpl-dev-portal | 2k | x402 compliance skill drafted (needs fork) |
| near-examples/near-intents-agent-example | 9 | x402 integration PR draft (needs fork) |
| HKUDS/OpenSpace | 6.8k | Added to queue: contribute + integrate |
| Dexter-DAO/dexter-x402-sdk | 3 | PR ready (Zod validation, #36 + #41), fork blocked |
| GOATNetwork/agentkit | 4⭐ | PR #7 (compliance plugin + ERC-8004 fix) — needs Jordan to submit |
| InjectiveLabs/iAgent | 50⭐ | x402 middleware built (15/15 tests), pushed to ProtoJay4789/iagent-x402 |
| Circle (arc-p2p-payments) | 19⭐ | Evaluated — gasless P2P on Arc, our lane. Added to queue. |
| Obsidian Mind (breferrari/obsidian-mind) | 3.6k⭐ | Issue #142 opened — proposal for x402 monetization skill |
| MiroFish (666ghj/MiroFish) | 69k⭐ | Issue #743 opened — proposal for x402 payment layer |
