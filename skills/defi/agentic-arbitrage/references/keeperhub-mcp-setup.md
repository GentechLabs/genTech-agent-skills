# KeeperHub MCP Server — Setup & Wiring (Aug 3, 2026)

Reference for connecting an agent to KeeperHub (DoraHacks Agents Onchain hackathon,
deadline Aug 13 2026). Build plan: `09-Green Room/specs/keeperhub-build-plan.md`.

## Endpoint (verified reachable from VPS)
- `https://app.keeperhub.com/mcp` → HTTP 200, ~0.16s
- OAuth discovery: `https://app.keeperhub.com/.well-known/oauth-authorization-server` → 200
- **Headless VPS CANNOT do browser OAuth.** Use an org API key (`kh_` prefix) as Bearer.
  Create at app.keeperhub.com → Settings → API Keys → Organisation tab. This is the ONE
  human step Gentech cannot do itself.

## Hermes HTTP MCP registration (same shape as ampersend/brickken/wurk)
```yaml
keeperhub:
  enabled: true
  url: https://app.keeperhub.com/mcp
  headers:
    Authorization: "Bearer kh_YOUR_KEY"
```
Verify a live key with `GET /user` via the token before wiring (like the GitHub token
health check pattern).

## Key tools (30+ registered; call `tools_documentation` at runtime for authoritative set)
- `execute_transfer`, `execute_contract_call`, `execute_check_and_execute`,
  `get_direct_execution_status`
- `search_protocol_actions`, `execute_protocol_action` (e.g. `aave-v3/supply`)
- `web3/transfer-funds`, `web3/transfer-token`, `web3/write-contract`
- Workflow mgmt: `create_workflow`, `execute_workflow`, `get_execution`

## Execution notes
- **`network` field accepts chain IDs as strings:** `"1"` Eth, `"11155111"` Sepolia,
  `"8453"` Base, `"42161"` Arbitrum, `"137"` Polygon.
- **Write actions need a wallet integration** (org-level). Confirm with
  `get_wallet_integration`; no per-action `walletId` field.
- **x402 payment (paid workflows):** settle Base USDC via EIP-3009
  `TransferWithAuthorization` — facilitator pays gas, wallet only debits USDC. This is
  our own stack — show it, don't just claim it (judging criterion).
- KeeperHub agentic wallet has server-side hard caps: 100 USDC/transfer, 200 USDC/day —
  fine for a small proof tx. `agentcash` alt stores the key in plaintext — NOT for real funds.

## The ONE hard judging requirement
Every hackathon submission must include a **live transaction link** the agent executed
through KeeperHub. Execution is weighted over demos. Lock a working execution path early —
don't leave it to day 8.

## Scoping pattern (from multi_mcp_agent_router)
Don't give the arb executor every tool — scope it to the execution tools it needs, and
gate which agent may call which KeeperHub tool behind the trust layer.
