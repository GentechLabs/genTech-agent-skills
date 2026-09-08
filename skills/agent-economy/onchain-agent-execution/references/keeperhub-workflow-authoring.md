# Authoring KeeperHub workflows by hand (verified Aug 4, 2026)

`kh_ai_generate_workflow` may be disabled server-side:
`503 {"error":"AI Prompt is disabled"}`. When that happens, author nodes/edges by hand.

## Fastest way to learn the exact node shape
Call `kh_get_workflow` on any existing workflow in the org and copy its JSON structure.
That is far more reliable than `kh_get_plugin` / `kh_list_action_schemas`, which returned
`"actions": {}` / 0 schemas — the plugin payload is mostly chain list + template syntax docs.

## Config field gotchas (each produced a 422 INVALID_ACTION_CONFIG)
- `web3/*` actions take **`network`** (stringified chain id, e.g. `"8453"`), NOT `chainId`.
- `web3/approve-token`: no `tokenAddress`. Requires
  `tokenConfig` as a **JSON string**:
  `"{\"mode\":\"custom\",\"customToken\":{\"address\":\"0x...\",\"symbol\":\"USDC\"}}"`
  plus `spenderAddress`, `amount`, `integrationId`, `network`.
- `web3/write-contract`: requires an inline **`abi`** (JSON string of the function fragment),
  plus `contractAddress`, `functionName`, `functionArgs` (JSON string array), `integrationId`, `network`.
- Protocol reads: `actionType: "aave-v3/get-user-account-data"`, `network`, `user`, and a
  `_protocolMeta` JSON string `{"protocolSlug","contractKey","functionName","actionType":"read"}`.
- Condition node: `actionType: "Condition"`, `group.rules[]` with unique `id`,
  `leftOperand`/`rightOperand` (not field/value), operators as exact symbols (`<`, `===`).
  Edges out of it need `sourceHandle: "true" | "false"`.
- Trigger: `{"triggerType":"Schedule","scheduleCron":"*/15 * * * *","scheduleTimezone":"UTC"}`.

The 422 response lists every invalid field with path + expected name — read it and re-submit;
two iterations is normal.

## Known-good 4-step rebalancer skeleton
Schedule → `aave-v3/get-user-account-data` → Condition `healthFactor < 1500000000000000000`
→ `web3/approve-token` → `web3/write-contract` `Pool.supply(asset, amount, onBehalfOf, 0)`.
Base Aave v3 Pool `0xA238Dd80C259a72e81d7e4664a9801593F98d1c5`, USDC `0x8335...2913`.
Created as `GTA Yield Guard` (`r0nfoic9vk12ik1h3af67`).

## Execution observability
`kh_execute_workflow` returns an execution ID, but `kh_get_execution_status` /
`kh_get_execution_logs` may return `MCP error -32602: Tool ... not found` — the server
doesn't always expose them. Fall back to the KeeperHub UI for run detail; don't treat the
returned execution ID as proof of success.

## Before promising a live tx: check the wallet has funds
The org wallet from `kh_list_integrations` may be empty. Verify with a plain RPC call
before claiming a tx is imminent:

```bash
curl -s -X POST https://mainnet.base.org -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"eth_getBalance","params":["0xWALLET","latest"]}'
# ERC20: eth_call to token with 0x70a08231 + 32-byte padded address
```
Zero balance on both mainnet and testnet = hard blocker; escalate for funding immediately
rather than building further submission assets.
