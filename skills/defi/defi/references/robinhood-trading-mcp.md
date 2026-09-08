# Robinhood Trading MCP Setup

## Status
Configured in `config.yaml` as `robinhood-trading`. Awaiting authentication on next gateway restart.

## Configuration
```yaml
mcp_servers:
  robinhood-trading:
    url: https://agent.robinhood.com/mcp/trading
    timeout: 180
    connect_timeout: 60
```

## Purpose
- Read portfolio value, buying power, positions, balances
- Place orders (market, limit, etc.)
- Build portfolios, automate DCA, rebalance, analyze risk
- Read order history and watchlists

## Limitations
- Only trades in a dedicated **Agentic account** (separate from main Robinhood)
- User reviews before it acts (unless auto-execution authorized)
- Stocks only — no crypto mentioned in the docs

## Next Steps
1. Restart gateway: `hermes gateway restart --profile gentech` (from separate shell)
2. Authenticate — Robinhood prompts to open an Agentic account and link it
3. Then the agent can read portfolio, check buying power, and eventually execute Tradesta signals directly

## Connection
MCP link: `https://agent.robinhood.com/mcp/trading`
Works with Claude, ChatGPT, Codex, Cursor, Grok — any MCP-compatible agent.
