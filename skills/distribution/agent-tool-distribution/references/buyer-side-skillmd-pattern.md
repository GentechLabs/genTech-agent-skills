# Buyer-Side skill.md — the missing distribution piece for our paid APIs

## The lesson (Jordan, Aug 20 2026)
We ship paid x402 endpoints but no buyer-side skill.md. Syra proves the pattern:
`GET https://api.syraa.fun/skill.md` lets any agent run `set up https://api.syraa.fun/skill.md`
and instantly know how to discover, pay, and call Syra's APIs. That is where agents
find tools — a self-serve skill.md at a discoverable URL, not a listing in an empty
supply-side directory.

## Syra's skill.md anatomy (the template to mirror)
`GET /skill.md` returns a frontmatter + markdown file covering:
- **Name/version/description** — trigger phrase for when the agent should use it
  (e.g. "crypto news, sentiment, signals, TVL, smart money").
- **One-liner install** — `set up https://api.syraa.fun/skill.md`.
- **Human setup** — fund ≥ $1 USDC, install MCP with `SYRA_PAYER_KEYPAIR`.
- **Free consult first, paid on execute** — a `*_consult` tool that returns which
  paid tool to call, without billing. Billing only hits on the real call (HTTP 402 quote).
- **Setup** per agent type (Claude Code / Cursor `mcp.json` / Codex) and SDK usage.
- **Payment rails** — accepted networks, facilitator failover chain (Dexter→GoPlausible→PayAI),
  and which auto-pay signers exist today.
- **Discovery endpoints** — `/.well-known/x402`, `/x402/capabilities`, `/openapi.json`,
  `/llms-full.txt`, `/skill.md`, `/llms.txt`.

## To apply to GenTech
Draft a `skill.md` for `api.gentechlabs.net` mirroring Syra's structure:
- `name: gentech-x402-gateway`, description listing our paid services
  (agent_research, token_security, market_intel, defi_lp_analytics, wallet_analysis,
  nft_search, treasury_defender, lineage_guard, agent_discovery).
- One-line `set up https://api.gentechlabs.net/skill.md`.
- Free `consult`-style route → returns which paid endpoint to call + price + params.
- Funding: USDC on Base (PayAI/CDP facilitator — our settlement rail).
- Serve it at a discoverable URL agents/developers find, and place it in the kit
  (`genTech-agent-kit/skills/`) so `npx skills` surfaces it.

## General rule
A buyer-side skill.md that lives at a discoverable URL and teaches agents how to
pay-and-call us is a first-class distribution artifact — equal to an Apify Actor.
Reach the buyer where they buy, don't just list in seller directories.
