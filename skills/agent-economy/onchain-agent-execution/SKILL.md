---
name: onchain-agent-execution
description: "Wire an AI agent to an external onchain execution / reliability layer (KeeperHub and similar) so the agent performs REAL transactions, not mockups. Covers the hard 'link a real transaction' submission requirement, MCP-tool patterns (create_workflow / execute_contract_call / execute_check_and_execute), the kh_-style API-key blocker, and the read->check->execute agent shape. Use whenever an agent must execute onchain through a third-party execution layer (KeeperHub, execution-marketplace hackathons, pay-per-execution rails)."
tags: [onchain, execution, agent, keeperhub, mcp, x402, hackathon]
trigger: "When building an agent that must perform a REAL onchain transaction through an external execution layer (KeeperHub Agents Onchain hackathon, execution-marketplace bounties, or any 'agent executes onchain' requirement). Distinguish from api-monetization (selling OUR endpoints) — this is an agent CONSUMING a third-party execution rail to transact."
version: 1.0.0
author: Gentech
---

# Onchain Agent Execution via External Execution Layers

## Core rule: the real transaction is the deliverable

For execution-layer hackathons (e.g. KeeperHub Agents Onchain, $5K + $1K bounty), judges
weight **"does it execute onchain via KeeperHub?"** above everything. The submission MUST
link a real transaction the agent executed through the layer. "A working transaction beats
a polished demo that never touches a chain." **A simulation is not a submission.** Build the
code, but you are NOT done until you can paste a live tx link.

**First thing to check: do you have a platform API key?** These execution layers gate the
MCP/HTTP surface behind a `kh_`-style key. If there's no key in the profile `.env`, that's
the gating blocker — flag it immediately (not in a status report) and get the user to create
an account + key. You can build and unit-test everything except the actual on-chain call
without the key; the moment the key lands you execute for real and capture the tx link.

## Preferred integration: the official Hermes plugin (not a hand-rolled MCP client)

Before writing your own MCP HTTP client, check whether the execution layer ships an agent
plugin. KeeperHub has an official **Hermes plugin** — this is the canonical, lowest-effort path:

```bash
hermes plugins install KeeperHub/hermes-plugin --enable
```
- Registers **28 `kh_*` tools** (workflow mgmt, direct exec, marketplace, templates, status).
- **Read-only by default** (list/get/search/status). Write + exec tools are **withheld** until
  `KEEPERHUB_ENABLE_WRITES=true` — the gate is structural (withheld tools are never registered).
- Requires `KH_API_KEY` (org key, prefix `kh_`); install prompts for it — you can skip and
  set it later in the profile `.env`.
- After install: **restart the gateway** for tools to load — but you **cannot restart the
  Hermes gateway from inside the gateway process** (SIGTERM kills the session). Run
  `hermes gateway restart` from a separate external shell.

The plugin's MCP client does session init / 401 re-init / JSON-RPC framing for you — don't
reinvent that. Use the plugin when one exists; hand-roll a client only when it doesn't.

## Self-hosting as an alternative to the hosted key

KeeperHub is open-source and self-hostable (`github.com/KeeperHub/keeperhub`, Docker Compose),
so self-hosting is a theoretical path to execute without a hosted `kh_` key. **Practical
reality:** the full platform needs ~59 env vars (Turnkey secure-enclave keys, Stripe, OAuth
providers, Postgres, RPC URL) — a heavy lift that blocks the quick submission you're after.
A standalone MCP-server spec exists in the repo but is a bigger build. Verdict: for a
deadline-driven submission, get the hosted `kh_` key (2 min) rather than self-host. Only
self-host if you want the platform running long-term as infrastructure.

## The read → check → execute agent shape

The canonical "agent does real work onchain" flow:

1. **Read** — query the target contract's live state (e.g. `supplyRatePerSecond` on a yield pool).
2. **Check** — evaluate a condition against a threshold (APY < target → trigger).
3. **Execute** — perform the state-changing onchain action through the execution layer.

This maps directly to KeeperHub's `execute_check_and_execute` primitive (read a value,
evaluate a condition, execute if met) and to a KeeperHub workflow of nodes
(contract_call → condition → contract_call). Build your agent around this shape and it
demonstrates reliability, observability, and real execution — all scoring criteria.

## Key design pattern: plan mode must not hit the network

Separate the workflow/plan generation from the actual execution call:
- `create_workflow()` returns the workflow **dict** locally (pure function, no network) —
  this is your demo/verify path that runs with no credentials.
- `create_workflow_remote()` / `execute_*()` call the MCP server and require the API key.

This lets you verify the whole build and produce a demo even before the key arrives, and
keeps the "no key" state honest instead of failing with connection errors.

## Working with KeeperHub MCP (docs.keeperhub.com/ai-tools/mcp-server)

Connect: `claude mcp add --transport http keeperhub https://app.keeperhub.com/mcp --header "Authorization: Bearer kh_..."`
Per-workflow: `/mcp/w/<slug>` exposes exactly one tool named after the workflow.

**Verify any key BEFORE wiring** — a `wfb_` key returns HTTP 200 but cannot open an MCP
session. Test with the plugin's own `KeeperHubClient._ensure_session_unlocked()` first; full
sequence + REST scope-probe table: `references/keeperhub-key-testing.md`.

**Public REST surface exists without a session.** `GET https://app.keeperhub.com/openapi.json`
is unauthenticated and enumerates every callable workflow + input schema (handy for capability
mapping even pre-key). Read-only `wfb_` keys can hit `GET /api/mcp/workflows` (list) and try
`POST /api/mcp/workflows/{slug}/call` — but public listings are often disabled (503 "owner
disabled this workflow"), and only a `kh_` org key can create/execute your OWN workflow.

Tools:
- **Workflow mgmt:** `list_workflows`, `get_workflow`, `create_workflow` (disabled by default; `enabled=true` to arm), `update_workflow`, `delete_workflow`, `validate_workflow`.
- **Execution:** `execute_workflow` (manual trigger → execution ID), `execute_contract_call` (view → result, state-changing → execution ID), `execute_check_and_execute` (read→check→execute — the key primitive).
- **Meta:** `search_workflows`, `call_workflow` (read → result, write → unsigned calldata, paid → x402 challenge, does NOT auto-pay), marketplace listing tools, `ai_generate_workflow` (NL → workflow).

KeeperHub stack to reference in a submission: MCP/CLI, x402/MPP pay-per-execution, smart gas estimation (exponential backoff), private routing (MEV protection), audit trail (every action logged), gas sponsorship on Ethereum. Agentic wallet = Turnkey sub-org custody, no private key on disk, `~/.keeperhub/safety.json` three-tier (auto/ask/block) policy; server-side hard limits (only Base USDC + Tempo USDC.e signing, no approve/transfer > 100 USDC).

## Pitfalls

- **Not every key that authenticates works.** KeeperHub ships multiple key types: **`kh_`** = organization key (full read/write/admin MCP scope) and **`wfb_`** = webhook/user key. A `wfb_` key will pass the HTTP layer (init returns **200**) but fails the MCP session handshake with *"KeeperHub did not return mcp-session-id"*, and is read-only on REST (POST /api/workflows → 405, /api/keys → 401). **If a key authenticates but the plugin client errors with no session-id, check the prefix — you need a `kh_` org key, not a `wfb_` one.** Get it from Settings → API Keys → Organisation. Verify BEFORE wiring: the plugin's own `KeeperHubClient._ensure_session_unlocked()` raising `RuntimeError: KeeperHub did not return mcp-session-id` is the definitive tell.
- **Prove the rail before any real tx.** A working key means you can verify the full pipeline with zero risk: `execute_protocol_action` with a **read-only** action (e.g. `aave-v3/get-user-account-data` with the wallet's own address) returns live chain data — that proves key → session → exec-tool → onchain connectivity. Use `simulate: true` on `execute_transfer`/`execute_contract_call` to dry-run a state-changing tx with no funds moved. Only after a successful read/simulate is it safe to fire a real (funds-moving) transaction — and still get explicit user sign-off first.
- **`list_action_schemas` / `/openapi.json` are the capability map.** Don't guess tool names. `list_action_schemas` (MCP) and `GET https://app.keeperhub.com/openapi.json` (REST, unauthenticated) enumerate every action/endpoint with input schemas. Flag write actions by the presence of `transactionHash` in `outputFields`. Use this to pick the exact action + required params instead of trial-and-error.
- **Simulation is not a submission.** If the requirement is a linked real transaction, don't claim done until you have the tx link. Report the key blocker honestly.
- **Key gates everything.** 401 on `tools/list` without `kh_` key. No key = no execution. This is an environment/credential blocker the user fixes — capture the fix (create account → key → set in `.env`), don't harden "KeeperHub doesn't work."
- **Plan vs execute must be split** so the build is verifiable pre-key.
- **Bounty hedge:** for "Best Onboarding UX" style stackable bounties, a starter template / first-tx tutorial / teardown-of-where-you-got-stuck is a low-risk parallel submission.
- **Submit early** — platform forms may block VPS terminal/curl (DoraHacks Human Verification); user uses their local browser for registration/forms.
- **Fund check before promising a tx.** The org wallet returned by `kh_list_integrations` may hold zero balance. Verify with a raw `eth_getBalance` / ERC20 `balanceOf` RPC call on mainnet AND the testnet you'd fall back to, *before* building submission assets. Empty wallet = escalate for funding immediately; the workflow can still be built and test-executed on a read-only path meanwhile.
- **`ai_generate_workflow` may be disabled** (`503 "AI Prompt is disabled"`) — author nodes by hand. The fastest way to get the exact node/config shape is `get_workflow` on an existing org workflow and copy its JSON; `list_action_schemas` / `get_plugin` returned empty `actions` maps. Field gotchas (`network` not `chainId`, `tokenConfig` JSON string, inline `abi` on write-contract) and a known-good 4-node rebalancer skeleton: `references/keeperhub-workflow-authoring.md`.
- **Execution status tools may not be exposed.** `execute_workflow` returns an execution ID, but `get_execution_status` / `get_execution_logs` can 404 with `MCP error -32602`. An execution ID is NOT proof of success — check the UI before claiming a run passed.
- **`kh_execute_transfer` wrapper param names DON'T match the MCP server schema.** The Hermes `kh_execute_transfer` tool accepts `network`/`recipient_address`/`token_address`, but the underlying MCP `execute_transfer` tool validates against `chain_id`/`to_address` — so it fails with `Invalid arguments for tool execute_transfer: expected string, received undefined` for `chain_id`/`to_address` no matter which wrapper names you pass. **Don't fight the wrapper.** Use the canonical action instead: `kh_execute_protocol_action` with `actionType: "web3/transfer-token"` and params `{network, tokenConfig (JSON string), amount, recipientAddress}`. But note:
- **Direct execution of `web3/transfer-token` returns 501.** `kh_execute_protocol_action` with a write action returns `501 Not Implemented - Direct execution not supported for "web3/transfer-token". Use workflow execution instead.` So for a real funds-moving transfer you MUST: (1) `kh_create_workflow` with a `web3/transfer-token` node (network, tokenConfig JSON string, amount, recipientAddress, integrationId), (2) **`kh_update_workflow` with `enabled=true`** — a workflow created disabled will execute as a silent no-op (balance never moves), (3) `kh_execute_workflow` → execution ID, (4) verify the balance actually debited on-chain (raw RPC `balanceOf`) since the status tools may be absent. **Confirmed Aug 5, 2026:** created the "GTA Proof Transfer" workflow disabled, executed (no-op, balance unchanged), enabled it, re-executed — still couldn't confirm via status tools; the honest blocker is that the MCP session lacks status tools and the balance check is the only ground truth.
- **Full worked reference:** `references/keeperhub-agents-onchain-2026.md` in this skill (the Aug 13 build: rebalancer at `/root/keeperhub-rebalancer/yield_rebalancer.py`, tool reference, judging criteria).
- **Public repo + demo video pattern for the submission (Aug 12, 2026):** `references/keeperhub-submission-repo-pattern.md` — how to publish the submission to a public GitHub repo (use the Gentech-Labs org via REST, not Jordan's flagged personal account; LICENSE at root is the #1 judge check; verify raw files serve 200), plus the 4-part demo-video script built around the live workflow + real tx ID.
- **Agent payment rails — chain coverage (verified Aug 2026):** `references/payment-rails-chain-coverage.md` — Beep (justbeep.it) is **Sui-only** (USDC-on-SUI a402) and does NOT reach Monad/EVM; Monad is covered via **Q402 (chain 143, gasless USDC/USDT) + Trader Joe pools**; our x402 gateway settles Base/Polygon/Arbitrum. Verify a rail's settlement chain before proposing it for a target chain — don't map a Sui-native protocol onto an EVM L1.
- **Revenue tracking after settlements:** `references/revenue-monitor-wallet-contract-pitfall.md` — when the Revenue Monitor shows $0 despite real settlements, it's usually scanning the wrong wallet (old `0x7ebf...` instead of the CDP account `0x77C6...` + arb wallet `0x3d117...`) or a stale Base USDC contract (`0x83358933...b43` → `0x833589fC...2913`). Scan both wallets, add all own-wallets to the self-transfer filter, and add the 3-rail (x402/Q402/Solana) breakdown.
- **`web3/transfer-token` can corrupt the token address — bypass with a direct `web3/write-contract` call (Aug 6, 2026).** When a transfer workflow errors instantly (2-3ms, no gas, no network) with `Invalid token address: 0x...`, compare the address in the error against the real contract address. KeeperHub's `web3/transfer-token` token resolution mangled Base USDC: the error showed `0x833589FC06e0b6E08f4c7C32D4F71b54bD0A02913` (wrong) while the real address is `0x833589fCD6eDb6E08f4c7C32D4f71b54bDA02913` — it was NOT using the exact `tokenConfig` address I passed. **Fix:** bypass token resolution entirely. Create a workflow with a `web3/write-contract` node that calls the token's `transfer(address,uint256)` directly, passing the exact contract address + a minimal ABI + `functionArgs: ["<recipient>","<raw-amount>"]` (raw units, e.g. 10000 = 0.01 USDC at 6 decimals). This sidesteps KeeperHub's token lookup. Also confirm the workflow is typed `write` (a `read`-typed workflow never executes a state-changing action — check `workflowType` in `kh_get_workflow`). Even with both fixed, if the balance still doesn't move and the node stays `idle`, it's the platform outage (see next pitfall), not your config.
- **All direct-exec wrappers share the broken param map (Aug 10, 2026).** It's not just `kh_execute_transfer` — `kh_execute_contract_call` fails identically with `MCP error -32602` complaining the string field `chain_id` is `undefined`. The Hermes plugin's write/exec wrappers pass `network`/`recipient_address`/`contract_address`, but the live MCP server validates `chain_id`/`to_address`. **No direct-exec tool works through the wrapper.** Don't burn time re-passing args; go straight to workflow execution (create_workflow with a node) or escalate.
- **CHECK THE EIP-55 CHECKSUM FIRST (Aug 10, 2026 — the actual root cause).** When an EVM execution layer rejects a contract address as `Invalid token address` / `Invalid contract address`, do NOT assume platform defect. The #1 cause is a **wrong EIP-55 checksum** in YOUR address string — one case-difference in one char makes every EVM validation reject it. The canonical Base USDC `0x833589fCD6eDb6E08f4c7C32D4f71b54bDA02913` was being typed with a bad checksum; the correct checksummed form is `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` (note `bdA` not `bDA`). Fix: run ANY contract address through `eth_utils.to_checksum_address(addr)` before sending it to an execution layer; compare against what you were passing. **Do this before concluding platform defect or burning time re-creating workflows.** Once checksum-corrected, the direct `execute_contract_call` (below) succeeded and the real 0.01 USDC tx landed on-chain and confirmed `success` — the exact same call KeeperHub had been rejecting. **Ready-made probe:** `scripts/keeperhub-direct-call.py` in this skill checksum-corrects + simulates/executes USDC.transfer directly, bypassing the broken plugin wrappers.
- **Interrupted execution may have LANDED — verify chain state before retrying.** If a side-effecting MCP/exec call is interrupted (tool marked "interrupted; effect UNKNOWN"), do NOT blindly re-fire — you could double-send. Check ground truth on-chain first: raw RPC `balanceOf` (e.g. the Base wallet dropped 10.0 → 9.98 USDC proving a real transfer occurred) and pull the tx hash from a blockscout-style API. If the balance already moved, the tx landed; capture the hash and DON'T resend. Retry only if balance is unchanged. Interrupted ≠ failed.
- **The write-contract bypass can ALSO be rejected (Aug 10, 2026) — usually a checksum bug, NOT a platform defect.** A workflow whose node calls USDC.transfer() with a canonical Base USDC address + minimal ABI errored instantly with `Invalid contract address` for that address. Earlier this looked like platform-side validation breaking; the real cause was the EIP-55 checksum error above. **Diagnostic order when an address is rejected: (1) run the address through `eth_utils.to_checksum_address()` and retry — fixes the vast majority; (2) call `execute_contract_call` directly with the correct server param names (`chain_id`, `contract_address`, `function_name`, `function_args`, `abi`) which bypasses the broken plugin wrapper param map; (3) simulate (`simulate:true`) → expect `wouldRevert:false`; (4) only if a checksum-correct address + direct call still errors, then suspect a genuine platform defect and escalate. **Capture the exact error + corrected address when escalating.**
- **Platform outage masquerades as config error (Aug 6, 2026).** When a workflow page 404s ("Workflow Not Found") but the API (`kh_get_workflow`) confirms the workflow exists and is enabled, and executions return execution IDs but the balance never moves — check the platform's **status page** before assuming your config is wrong. KeeperHub had an active "KeeperHub app degraded" incident (status.keeperhub.com) that made the app 404 on workflows the API still served, and silently no-op'd executions. **Diagnostic order:** (1) `kh_get_workflow` — does the API still see it? (2) fetch the platform status page — active incident? (3) only then suspect your workflow config. If it's a platform outage, **set a retry cron** (check status → re-execute → verify balance debited) rather than babysitting or re-creating the workflow. The on-chain balance check (`balanceOf` via raw RPC) is the only ground truth that survives a degraded app — an execution ID is not proof.
- **"Needs Jordan's MetaMask + gas" may be a dissolvable blocker — use a CDP server wallet as signer (Aug 29, 2026).** Before flagging a gas/signature human gate, triage the THREE wallet roles: signer (can be ours via CDP), fee/earnings recipient (can be Jordan's — it's just a parameter in the call), owner (whoever holds the signer key). If the signer role is unassigned, a GenTech CDP server wallet (`get_or_create_account(name=...)` — we hold keys, wallet rule honored) + CDP faucet + `cast`-recomputed calldata registers on-chain for $0 on testnet. Telegraph #49 was "blocked on human gas" for 5 days; dissolved in one session (tx status 0x1, receipt event verified). Full recipe + gotchas: `references/cdp-server-wallet-signing.md`. Only the PLATFORM FORM submission stays human.
