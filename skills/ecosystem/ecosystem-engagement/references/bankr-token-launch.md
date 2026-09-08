# Bankr Token Launch on Robinhood Chain

## Overview
Bankr launches tokens on **Robinhood Chain by default** (pass `--chain base` for Base). This means a Bankr launch satisfies Victus Global's requirement for a tradable token on Robinhood Chain — two birds, one stone.

## Token Specs
| Parameter | Default | Notes |
|-----------|---------|-------|
| Supply | 100B | Fixed, not mintable after deployment |
| LP allocation | 85% | Seeded into Uniswap V4 pool |
| Creator vesting | 15% | Vested over 1 year, 30-day cliff |
| Swap fee | 0.7% | 95% to creator, 5% to protocol |
| Chain | Robinhood Chain | Pass `--chain base` for Base |

## Launch Methods

### CLI (if Bankr CLI is installed)
```bash
bankr launch --name "Agentic Treasury" --symbol TREASURY \
  --image "https://..." --chain robinhood --yes
```

### Web Interface
Go to [bankr.bot](https://bankr.bot), connect wallet, fill in name/symbol/image.

### Social
Tag @bankrbot on X: `@bankrbot deploy a token called Agentic Treasury`

## Key Details
- **Gas sponsored** for first 3 deploys/day (standard) or 10/day (Club)
- **Wallet age requirement** — may need 24h+ old wallet (anti-sybil)
- **1 token per minute** rate limit
- **95% of 0.7% swap fees** flow to creator — claimable anytime
- **No vesting option** — pass `--no-vesting` for 100% LP

## Use Case: Victus Global / Robinhood Ecosystem Fund
Victus Global manages the $10M Robinhood Ecosystem Fund. They require a tradable token on Robinhood Chain as proof of project legitimacy. Bankr launches on Robinhood Chain by default, making this a single-step process.
