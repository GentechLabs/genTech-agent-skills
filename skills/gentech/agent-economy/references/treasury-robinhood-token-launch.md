# $TREASURY — Agentic Treasury Token Launch (Jul 22, 2026)

## Overview
Launched $TREASURY (Agentic Treasury) on Robinhood Chain via Bankr. Contract: `0x56D03C0f4167cC2c26B781dE47E608d660F13ba3`. 100B supply, 85% LP, 15% creator vesting.

## Strategic Context
This launch served two purposes simultaneously:
1. **Victus Global / Robinhood Ecosystem Fund** — They require a tradable token on Robinhood Chain as proof of project legitimacy before discussing the fund. $TREASURY unlocked that conversation.
2. **Product-token alignment** — Instead of launching a generic brand token ($GENTECH), we tied the token to the Agentic Treasury product. This makes the token's purpose clear: it's the native asset for autonomous agent treasury infrastructure.

## Launch Flow
1. Go to bankr.bot → connect wallet
2. Launch a Token → follow the wizard
3. **Name:** Agentic Treasury
4. **Symbol:** TREASURY
5. **Image:** AI-generated gold vault door with G logo (see brand-assets skill for generation workflow)
6. **Chain:** Robinhood Chain (Bankr default)
7. **Website:** gentechlabs.net
8. **Fees:** Skip (keep for yourself — 95% of 0.7% swap fees)
9. **Vesting:** Keep default (15% over 1 year, 30-day cliff)
10. Confirm and deploy

## Key Lessons
- **Bankr deploys to Robinhood Chain by default** — no special config needed. Pass `--chain base` to deploy on Base instead.
- **Product tokens > brand tokens** — Tying the token to a specific product (Agentic Treasury) gives it a clear narrative and use case. Better for ecosystem fund conversations than a generic brand token.
- **Image matters** — We iterated through 5+ image generations before landing on the final design. The process: concept → feedback → refine → simplify → final. Kimi K3 provided useful critique (too busy, G logo needs context, text at top is illegible at small sizes).
- **Two birds, one stone** — The same launch satisfied both the Victus Global requirement AND put our product token live.
- **Token image iteration pattern:** Start with a concept (vault + G logo), get feedback from a strong model (Kimi K3), simplify based on critique (remove text, reduce clutter, one focal point), test at small sizes (wallet icon, DEX screener thumbnail). The final design was the simplest — just the gold vault door with G logo on dark navy, no text, no building.
- **Bankr CLI deployment flow:** `bun add -g @bankr/cli` → `bankr login` (paste API key) → `bankr x402 init` → `bankr x402 add <name>` (interactive wizard for method/path/price) → edit handler at `x402/<name>/index.ts` → `bankr x402 deploy`. The CLI creates a scaffolded TypeScript handler that you customize before deploying.
- **Bankr x402 CLI pitfalls:** The `x402/` directory must be in the current working directory. The `bankr x402 add` command is interactive (prompts for method, path, price, npm packages). The `--ni` (not-interactive) flag does NOT suppress the interactive wizard for this subcommand — to bypass, write the config file directly at `x402/bankr.x402.json` with the service definition, then run `bankr x402 deploy`. The `bankr.x402.json` config file at the root level (`/root/bankr.x402.json`) is NOT the same as the one in the `x402/` directory — the CLI only reads from `x402/bankr.x402.json`. `bankr x402 deploy` with `BANKR_NOT_INTERACTIVE=1` works for non-interactive deployment.
- **Victus Global outcome:** They replied "Perfect. The fund is specifically focused on projects that are already available for trading, that's minimum requirement to prove project is legit." — confirming the token requirement was real. We launched $TREASURY and notified them. Awaiting next response.

## Follow-up
- [ ] Animate the token image (shining gold vault) — queued as build queue #58
- [ ] Tell Victus Global: "Token's live on Robinhood Chain. $TREASURY — 100B supply, trading on Uniswap V4. Contract: 0x56D03C0f4167cC2c26B781dE47E608d660F13ba3. Ready to pick up the ecosystem fund conversation whenever you are."
- [ ] Monitor trading volume and fee accumulation
