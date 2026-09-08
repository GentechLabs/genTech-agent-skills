# Robinhood Agentic Trading — Integration Reference

**Announced:** 2026-07-20
**MCP URL:** `https://agent.robinhood.com/mcp/trading`
**Status:** Configured in Hermes ✅

## What It Is
Robinhood opened agentic trading — connect any AI agent to a real brokerage account via MCP. Equities + options live now, crypto coming.

## Tools Available (30+)

| Category | Tools |
|----------|-------|
| **Account** | get_accounts, get_portfolio, get_realized_pnl, get_pnl_trade_history, search |
| **Watchlists** | get_watchlists, create/update/follow/unfollow, add/remove symbols |
| **Market Data** | get_equity_historicals (OHLCV), fundamentals, technical indicators (RSI, MACD, Bollinger), earnings calendar, indexes |
| **Equities** | get_positions, get_quotes, get_orders, review_order, place_order, cancel_order |
| **Options** | get_chains, get_instruments, get_quotes, get_positions, review/place/cancel orders |
| **Scanners** | get_scans, create_scan, run_scan, update filters |

## How It Fits GenTech Labs

| Our Asset | Robinhood Play |
|-----------|---------------|
| Agentic Treasury spec | Real execution layer — spec meets real brokerage |
| DeFi strategies | Extend to equities + options |
| x402 compliance patterns | Safety-first order review before placement |
| Content pipeline | First video: "We connected an AI agent to Robinhood" |
| Q402 wallet | Fund the Agentic account from treasury |

## Robinhood vs Base DeFi — Complementary, Not Competing

| Dimension | Robinhood | Base |
|-----------|-----------|------|
| **Assets** | Equities, options, ETFs | Tokens, DeFi positions, LP shares |
| **Regulation** | SIPC insured, regulated, audited | Permissionless, self-custody |
| **Hours** | Market hours (9:30-4 ET) | 24/7 |
| **Access** | KYC required, US only | Global, no approval |
| **Custody** | Brokerage holds assets | You hold the keys |
| **Agent capabilities** | Buy/sell stocks, options strategies | Arbitrage, yield farming, LP, lending |

**The thesis:** Agentic Treasury uses both. Robinhood for traditional assets (equities, options, ETFs). Base for on-chain yield (DeFi, lending, LP). The agent routes capital to whichever market offers the best risk-adjusted return.

## Setup
1. `claude mcp add robinhood-trading --transport http https://agent.robinhood.com/mcp/trading`
2. Authenticate via browser
3. Open an Agentic account
4. Fund it
5. Start trading

## Safety
- Dedicated account with budget
- Push notifications on every trade
- Disconnect anytime from the app
- review_equity_order / review_option_order before placement
