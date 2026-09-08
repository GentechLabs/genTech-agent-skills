# Bankr Skills-Marketplace Listing (verified Aug 2, 2026)

Bankr (bankr.bot) is the agent-economy financial platform on Base ($5.03B
volume). Its x402-native agents can pay our gateway — verified: our 402
envelope has `accepts[0]` with USDC/Base/payTo/EIP-712 `{name:"USD Coin",
version:"2"}` exactly where Bankr clients expect it.

## Two listing routes — use skills, NOT x402 Cloud

| Route | Fee | Hosting | Discovery |
|-------|-----|---------|-----------|
| **Skills marketplace** (CHOSEN) | 0% | Ours (self-hosted gateway) | Agents install the skill, then call/pay our endpoints |
| x402 Cloud mirror | 5% + free tier 1K/mo | Bankr hosting | Auto-indexed in their agent discovery layer |

Bankr's agent discovery auto-indexes **their** Cloud endpoints; for a
self-hosted gateway the skills marketplace is the free entry point.

## Publish a skill (verified flow)

1. Write `SKILL.md` with frontmatter `name`, `description` (agent-trigger
   keywords!), `version`, `author`, `tags`. Bankr parses frontmatter.
2. Commit to a **public GitHub repo the org owns** and push.
3. Verify the raw URL returns 200:
   `curl -s -o /dev/null -w "%{http_code}" <raw.githubusercontent.com URL>`
4. Give Jordan (or any agent) the install command:
   `install the <skill-name> skill from https://github.com/Gentech-Labs/<repo>/tree/master/skills/<name>`

## PITFALLS (hit Aug 2, 2026)

- **`ProtoJay4789/` repos 404 on the web** (flagged account) — pushes
  succeed, raw URLs 404. Always use `Gentech-Labs/<repo>` for public links.
- **Org kit repo default branch is `master`, not `main`.** Pushing `main`
  fails with "src refspec main does not match any" even when local clone
  uses `main`. Fix: `git push origin HEAD:master` or clone fresh and push
  its default branch.
- **Local repo and org repo can genuinely diverge** (different layouts,
  different content under the same name). Don't force-push local over org —
  clone the org repo separately, add just the new file, commit, push.
- **Never inline long content (HTML/SKILL.md) in a Telegram message** —
  4096-char cap truncates mid-message. Build to server, send only the
  short link. (Jordan: "every time you're working on giving me the link,
  the message gets cut off short.")

## Skill content that makes agents actually use it

- Describe each endpoint: path, service, price, example URL.
- Explain the flow: call → 402 envelope → sign EIP-3009 (gasless USDC on
  Base) → retry with `Authorization: x402 <proof>` → 200 with data.
- Include the discovery URLs (`/.well-known/x402`, `/.well-known/x402-bazaar`).
- State the EIP-712 domain explicitly — standard clients need it.
