# KeeperHub — Agents Onchain Hackathon (DoraHacks), worked build Aug 2026

**Deadline:** Aug 13, 2026 12:00 UTC+2 · **Prize:** $5,000 (1st $2K / 2nd $1.2K / 3rd $800) + **$1,000 bounty** ("Best Onboarding UX Improvement", split 2 ways)
**Link:** https://dorahacks.io/hackathon/agents-onchain/detail
**Status (Aug 3 2026):** rebalancer code done at `/root/keeperhub-rebalancer/yield_rebalancer.py`; plan mode verified. **`kh_` org key now wired** (Aug 3): `KH_API_KEY` + `KEEPERHUB_ENABLE_WRITES=true` in `/root/.hermes/profiles/gentech/.env`; MCP session confirmed with `mcp:read mcp:write mcp:admin` scope. Org has 3 workflows (Aave Health Factor Monitor, Large Withdrawal Alert, Aave Governance Alert) + a web3 wallet integration `0x53A8DFA431D03A36499f9DB70AAFbb00C28308EA` (Jordan Jones, owner). Execution rail verified: `execute_protocol_action` with `aave-v3/get-user-account-data` on Base mainnet returned live data (healthFactor). **NEXT: fire a real onchain tx (testnet recommended — Base Sepolia — or mainnet micro-tx with user sign-off), capture tx hash/explorer link, then build the GitHub repo + demo video + DoraHacks submission.** Hermes plugin installed + enabled (28 `kh_*` tools, needs gateway restart from external shell to activate).
**KEY-TYPE LESSON:** a `wfb_`-prefixed key (webhook) authenticates HTTP-200 but CANNOT open an MCP session (plugin raises `KeeperHub did not return mcp-session-id`) and is read-only — only the `kh_` org key works. Verify with the plugin's own client before wiring.

## The hard requirement
Submission needs: GitHub link + short demo video + **a link to a transaction the agent executed via KeeperHub**. "A working transaction beats a polished demo that never touches a chain." Real tx is non-negotiable.

## Chosen build: Autonomous Yield Rebalancer
Monitors a yield pool's `supplyRatePerSecond`, annualizes to APY bps, and when APY < `TARGET_APY_BPS` executes an onchain rebalance (`redeem`) through KeeperHub. Exercises `execute_check_and_execute` + workflow nodes (contract_call → condition → contract_call), reliability/observability, audit trail.

Usage:
- `python yield_rebalancer.py plan --pool <addr> --wallet <addr>` — prints workflow JSON locally, **no key needed** (verified working).
- `python yield_rebalancer.py run --pool <addr> --wallet <addr> --once` — requires `KEEPERHUB_API_KEY`; reads APY, decides, executes.

Env: `POOL_ADDRESS`, `WALLET_ADDRESS`, `CHAIN_ID` (8453 Base), `TARGET_APY_BPS` (500 = 5%), `CHECK_INTERVAL_S`.

## MCP server (from docs.keeperhub.com/ai-tools/mcp-server)
Add: `claude mcp add --transport http keeperhub https://app.keeperhub.com/mcp --header "Authorization: Bearer kh_..."`
Per-workflow: `claude mcp add --transport http my-workflow https://app.keeperhub.com/mcp/w/<slug> ...`

Tools: `list_workflows`, `get_workflow`, `create_workflow` (disabled by default, `enabled=true` to arm), `update_workflow`, `delete_workflow`, `validate_workflow`; `execute_workflow` (→ execution ID), `execute_contract_call` (view→result / state-changing→execution ID), `execute_check_and_execute` (read→check→execute); `search_workflows`, `call_workflow` (read→result, write→unsigned calldata, paid→x402 challenge, does NOT auto-pay), marketplace listing tools, `ai_generate_workflow`.

## KeeperHub stack (reference in submission)
MCP/CLI · x402/MPP pay-per-execution (settled onchain, x402scan.com; Tempo + Stripe for MPP) · smart gas estimation (exponential backoff) · private routing (MEV protection) · audit trail (trigger, simulation, submitted tx, gas, outcome, timestamp) · gas sponsorship on Ethereum · agentic wallet (Turnkey sub-org custody, no private key on disk, `~/.keeperhub/safety.json` auto/ask/block; server-side hard limits: Base USDC + Tempo USDC.e only, no approve/transfer > 100 USDC).

## Judging criteria
Execution via KeeperHub (weighted heaviest) · use of KeeperHub surfaces (MCP/CLI/x402/MPP/audit trail) · reliability + observability (retries, gas, audit log) · originality + real-world usefulness · integration quality + DX.

## Bounty hedge
"Best Onboarding UX Improvement" ($1K) — a starter template / first-tx-in-5-min tutorial / teardown of where you got stuck + proposed fixes. KeeperHub is open source; fresh-eyes contributions win.

## Pitfalls
- Real tx is the deliverable; no simulation passes. Key is the gating blocker.
- Plan vs execute split (plan is pure-local, no network).
- DoraHacks blocks VPS terminal/curl (Human Verification) — Jordan uses local browser for registration/forms.
- Submit early, leave time to wrap the demo video + tx link.
