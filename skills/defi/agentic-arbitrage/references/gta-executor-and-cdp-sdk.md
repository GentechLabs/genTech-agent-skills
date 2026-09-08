# GTA Execution Engine + Coinbase CDP SDK

Session-proven setup (Aug 3, 2026). Turns GTA from detection-only into execution-capable.

## GTA Executor Pattern (`scripts/gta_executor.py`)

Build a **dry-run-first execution engine** — the decision/order-plan brain ships and is fully testable WITHOUT a live key; real execution activates only when the key exists.

- **Dry-run mode (default):** reads `.gta-arb-state.json` (from `gta-arb-monitor.py`), applies rules, emits an order plan, moves NO funds.
- **Real mode:** executes ONLY if `GTA_HL_KEY` env var is set; otherwise raises `NoExecutionKeyError` and **refuses to fake a successful order** (never stub real execution as success — that hides a missing integration).
- **Rule set (from agentic-arbitrage):** Execute ≥ 10 bps, Report ≥ 5 bps, Close < 3 bps, stop-loss = spread widened > 50 bps from entry, max hold 7 days.
- **Open position exits dominate entry:** if holding, evaluate CLOSE (stop-loss / normalized / max-hold) before scanning for new ENTER.
- **Contango** (perp > spot) → short perp + long spot. **Backwardation** → reverse.
- Idempotent position tracking via JSON state file. Quiet-hours gate at top (same 3:00–10:30 UTC as other GTA crons).
- Wire as a cron that runs the executor (dry-run) and reports the DECISION, never claiming execution.

Test suite (`test_gta_executor.py`) runs with `GTA_HL_KEY` popped — 9 tests covering threshold, stop-loss, normalize, max-hold, dry-run, real-mode-fails, persistence roundtrip.

## Current GTA blocker state (Aug 3, 2026)

- ✅ **Detection** — live (GTA Arb Monitor, 3h cadence).
- ✅ **Coinbase spot leg** — CDP SDK key wired + verified (below).
- ❌ **Hyperliquid perp leg** — needs `GTA_HL_KEY` (trade-only key: can place/cancel orders but CANNOT withdraw; user retains custody). This is the #1 blocker. `gta_executor.py` real mode stays stubbed until it exists.
- ⚠️ **Bridge Base→HL** — historically broken (Across relayers stuck funds Jul 26). Not rebuilt.

## Coinbase CDP SDK wiring (v1.47.1, `pip install cdp-sdk`)

The CDP SDK reads these env vars (NOT a single key):
```bash
CDP_API_KEY_ID=<uuid>
CDP_API_KEY_SECRET=<base64 secret>
# optional: CDP_WALLET_SECRET
```
Source of truth in `cdp/cdp_client.py`:
```python
api_key_id = api_key_id or os.getenv("CDP_API_KEY_ID") or os.getenv("CDP_API_KEY_NAME")
api_key_secret = api_key_secret or os.getenv("CDP_API_KEY_SECRET")
```

**Key facts:**
- **Async API.** Methods like `evm.list_accounts()` return coroutines — must `await`:
  ```python
  import asyncio
  from cdp import CdpClient
  async def main():
      c = CdpClient()
      accts = list(await c.evm.list_accounts())
      await c.close()
  asyncio.run(main())
  ```
  Calling without await raises `TypeError: object of type 'coroutine' has no len()` — that's the "it worked, just await it" tell, not an auth failure.
- **Auth verification (read-only, no funds move):** `await c.evm.list_accounts()` — a 401 means the key is wrong; a successful call with zero exceptions proves auth. Store in profile `.env` (chmod 600), never git.
- Client top-level surface: `.evm`, `.solana`, `.policies`, `.end_user`, `.webhooks`.
- Useful read-only methods: `evm.list_accounts()`, `evm.list_token_balances()`, `evm.get_account()`.
- **Credential-in-chat hygiene:** if the user pastes a CDP/API secret in chat, store it, verify it in the SAME turn, then tell the user they can delete the chat copy. Never echo the value back.

## Funding routing: the funded account ≠ the CDP server account (critical)
There are **multiple distinct wallets** in the GTA system — do not assume funding lands where
execution looks:
- **GTA EOA wallet** (`gentech-arb-wallet.json` in `secure/`) — where the user funds USDC
  (the onboarding checklist targets this address).
- **Coinbase CDP server accounts** — where `gta_coinbase_leg.py` executes swaps. These start
  EMPTY; funds must be **moved** from the EOA to the CDP account before a real swap.
- **x402 / main wallet** — unrelated, don't confuse.

**To move USDC EOA → CDP account (web3, Base):**
```python
w3 = Web3(Web3.HTTPProvider('https://base.drpc.org'))
# MUST include chainId=8453 in the tx dict — omitting it raises
# "error getting sender from raw transaction".
tx = usdc.functions.transfer(to_addr, AMOUNT).build_transaction({
    'from': from_addr, 'nonce': nonce,
    'gas': 100000, 'gasPrice': w3.eth.gas_price, 'chainId': 8453})
signed = w3.eth.account.sign_transaction(tx, key)
w3.eth.send_raw_transaction(signed.raw_transaction)
```
- **Gas gotcha:** a too-low hardcoded `gas` (e.g. 60000) reverts with "FAILED" even though
  `eth_call` simulation passes. Use a generous `gas: 100000` (or `estimate_gas` + 20% buffer)
  and verify the receipt `status == 0x1`.
- **CDP swap needs native gas on the account too** — the account must hold both the USDC AND
  native ETH (for gas) or `create_swap_quote` fails with a `gasFee` fee-estimation error.
  Send ~0.0003 ETH alongside the USDC.
- **Verify after transfer:** `eth_getBalance` (native) + `balanceOf(USDC)` on the CDP account,
  and confirm the receipt on-chain (`status: SUCCESS`).
- **`get_swap_price` works unfunded** (read-only basis oracle) — that's the "what's the price
  on this platform" signal. Only *execution* needs funded accounts + gas.
