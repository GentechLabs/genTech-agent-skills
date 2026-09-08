# Robinhood Trading MCP

**URL:** `https://agent.robinhood.com/mcp/trading`
**Auth:** OAuth via Robinhood Agentic account
**Status:** Configured in Gentech profile (Jul 20, 2026)

## What It Does

Robinhood's Agentic Trading MCP lets AI agents:
- Read portfolio value, buying power, positions, balances
- Place orders (market, limit, etc.)
- Build portfolios, automate DCA, rebalance, analyze risk
- Read order history and watchlists

## Setup

```yaml
# In ~/.hermes/profiles/gentech/config.yaml
mcp_servers:
  robinhood-trading:
    url: https://agent.robinhood.com/mcp/trading
    timeout: 180
    connect_timeout: 60
```

After adding to config, restart the gateway from a separate shell:
```bash
hermes gateway restart --profile gentech
```

## Auth Flow

1. Connect the MCP server (config above)
2. Robinhood prompts to open an **Agentic account** (separate from main Robinhood)
3. Follow on-screen steps to authenticate
4. Agent gets read access to: accounts, positions, balances, transactions, watchlists
5. Agent can place trades in the Agentic account only

## Integration with Tradesta Signals

The Tradesta Leverage Trading Signal cron (`tradesta-signal.py`) generates LONG/SHORT/SKIP signals daily at 7 AM and 7 PM ET. With Robinhood MCP connected, the next step is to execute those signals automatically:

1. Signal says "BTC LONG 3x"
2. Agent checks Robinhood buying power
3. Agent places market/limit order in Agentic account
4. Confirmation delivered to user

## Limitations

- Stocks only (no crypto mentioned in Robinhood's docs)
- Dedicated Agentic account only (not main brokerage)
- User reviews before execution (unless auto-execution authorized)
- Desktop-only for initial auth flow
