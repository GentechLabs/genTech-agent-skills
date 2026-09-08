# Ampersend Agent Configuration — GenTech

## Agent Identity

- **Account (smart account):** `0x5ea265f44eFE09bEE2f9A56fc5C9b31f616b8C5B`
- **Key address (session key):** `0x71AB05CfE4C85592cF1d932c8AD047378E555289`
- **Network:** Base mainnet
- **Status:** Ready

## MCP Proxy

- **Source:** `/root/repos/ampersend-hermes/`
- **Binary:** `/root/repos/ampersend-hermes/dist/mcp/proxy-cli.js`
- **Registered in:** `~/.hermes/profiles/gentech/config.yaml` under `mcp_servers.ampersend`

## Spend Limits (from dashboard)

- **Daily:** $100 USD
- **Per-transaction:** Not set (consider adding)
- **Auto top-up:** Disabled
- **Auto-collect:** Disabled

## First Session Setup (May 8, 2026)

1. Installed `@ampersend_ai/ampersend-sdk@0.0.16` globally
2. Configured agent with `ampersend config set "0xkey:::0xaccount"`
3. Fixed network from base-sepolia sandbox to base mainnet
4. Cloned and built `ampersend-hermes` MCP proxy from source
5. Registered MCP proxy in Hermes config
6. Agent is ready for x402 payments — needs `/reload-mcp` in Hermes to activate MCP tools

## Key Commands

```bash
ampersend config status                    # Verify setup
ampersend fetch --inspect <url>            # Check payment cost
ampersend fetch <url>                      # Make payment
```
