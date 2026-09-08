# SAP MCP Agent Metadata Template

Use this when registering a new agent on SAP MCP. Covers the agent-metadata.json structure and the SAP MCP config.

## agent-metadata.json

```json
{
  "name": "Your Agent Name",
  "description": "What the agent does",
  "version": "1.0.0",
  "x402Version": 2,
  "owner": "SOLANA_WALLET_ADDRESS",
  "agentAddress": "SAP_MCP_KEYPAIR_PUBKEY",
  "website": "https://yoursite.com",
  "x402Endpoint": "https://api.yoursite.com/.well-known/x402-bazaar",
  "capabilities": [
    {
      "name": "Service Name",
      "description": "What this endpoint does",
      "endpoint": "https://api.yoursite.com/v1/service/{param}",
      "price": "$0.01"
    }
  ],
  "protocols": ["sap", "x402", "mcp"],
  "networks": ["eip155:8453", "solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp"],
  "tags": ["x402", "your-category"],
  "revenue": {
    "model": "x402-pay-per-call",
    "settlement": "base-usdc",
    "minPrice": "$0.005",
    "maxPrice": "$0.01"
  }
}
```

## SAP MCP config.gentech.json

```json
{
  "mode": "auto",
  "rpcUrl": "https://api.mainnet-beta.solana.com",
  "rpcUrlDevnet": "https://api.devnet.solana.com",
  "programId": "SAPpUhsWLJG1FfkGRcXagEDMrMsWGjbky7AyhGpFETZ",
  "commitment": "confirmed",
  "maxRetries": 3,
  "walletPath": "~/.config/mcp-sap/keypairs/gentech-keypair.json",
  "maxTxValueSol": 10,
  "requireApprovalAboveSol": 1,
  "dailyLimitSol": 100,
  "allowedTools": "all",
  "logLevel": "info",
  "enableCache": true,
  "cacheTtlSeconds": 300
}
```

## Registration Flow

1. Install Solana CLI: `sh -c "$(curl -sSfL https://release.anza.xyz/v2.1.0/install)"`
2. Create keypair: `solana-keygen new --no-bip39-passphrase --outfile ~/.config/mcp-sap/keypairs/agent-keypair.json`
3. Fund with ~0.01 SOL from owner wallet
4. Clone: `git clone https://github.com/OOBE-PROTOCOL/sap-mcp.git`
5. Register via local `sap_payments_register_agent` (hosted MCP returns `hosted_local_signer_required`)

## External x402 Wiring

Once registered, `sap_payments_call_external_x402` can call non-SAP x402 endpoints:
- Fetches the 402 challenge from the external URL
- Signs locally with the SAP MCP profile signer
- Retries with PAYMENT-SIGNATURE header
- Returns the response + settlement receipt
