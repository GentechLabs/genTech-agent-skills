# Coinbase CDP Swap Execution — the `gasFee: null` SDK bug, FIXED + method-signature traps

**Date:** 2026-08-03. Live-tested against `cdp-sdk` v1.47.1 on Base mainnet with a
**funded** account (10.5 USDC + 0.0003 ETH on the account).

## Status: RESOLVED via 3 in-place SDK patches (Aug 3)
Real swap execution was blocked by an upstream `cdp-sdk` v1.47.1 bug: its Pydantic
models rejected fields the Coinbase API legitimately returns as `null`/boolean. **All
three bugs are fixed by monkey-patching the installed SDK files.** After the patches,
`account.quote_swap()` returns a real `QuoteSwapResult` (liquidity True, to_amount
returned) and execution proceeds to the signing step.

The patches are **in-place edits to the installed venv files**, NOT a wrapper/upgrade.
They'll be lost on SDK reinstall/upgrade — re-apply if `pip` reinstalls `cdp-sdk`.

## The 3 patches (each: `Optional`-ize or accept the real type)

### Patch 1 — `CommonSwapResponseFees.gas_fee / protocol_fee` null
File: `site-packages/cdp/openapi_client/models/common_swap_response_fees.py`
Bug: API returns `gasFee: null`; fields were non-optional `TokenFee` → ValidationError.
Fix: make both `Optional[TokenFee] = Field(default=None, ..., alias=...)`.
Error was:
```
ValidationError: 1 validation error for CommonSwapResponseFees
gasFee  Input should be a valid dictionary or instance of TokenFee [type=model_type, input_value=None]
```

### Patch 2 — `CommonSwapResponseIssues.allowance / balance` null
File: `site-packages/cdp/openapi_client/models/common_swap_response_issues.py`
Bug: same class — API returns `allowance`/`balance` as null when no issue present.
Fix: make both `Optional[...] = None`.

### Patch 3 — `CreateSwapQuoteResponse.liquidity_available` bool vs string
File: `site-packages/cdp/openapi_client/models/create_swap_quote_response.py`
Bug: `field_validator('liquidity_available')` only accepted the string `'true'`, but the
API returns a real Python `True`. Fix the validator to `if isinstance(value, bool) or value in {'true','false'}: return value`.

## After the patches
`acct.quote_swap(...)` works. The **next blocker is a credential, not code**: execution
then requires `CDP_WALLET_SECRET` (the signing secret for the CDP server account that
owns the funds). Set `CDP_WALLET_SECRET=<value>` in the profile `.env` (chmod 600, never
echo). This is a **trade-capable signing secret** — the highest-privilege piece of the
CDP setup, held only by the user. Don't fabricate or guess it.

## Method-signature gotchas (use these, they work)
- `get_account(address=...)` fetches a specific existing account.
- `get_or_create_account(address=...)` **does NOT take an address kwarg** — it is
  `get_or_create_account(name=None)` only. Passing `address=` raises
  `TypeError: ... unexpected keyword argument 'address'`.
- So to operate on a *funded* existing account: `acct = await client.evm.get_account(address=addr)`.
- Swap needs **contract addresses + raw integer amounts**, not tickers/decimals:
  - `from_amount` must be raw (e.g. `"2000000"` = 2 USDC at 6 dec), a string of digits.
  - Tokens as `0x` addresses (USDC Base = `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`,
    cbBTC = `0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf`).
- To move funds onto the CDP account: send from the GTA EOA with `chainId` explicitly set
  in the tx dict (omitting it causes `error getting sender from raw transaction`).
  Verify with the same web3 RPC: `eth_getBalance` for native gas + `balanceOf` for USDC.

## Verified tradeable tokens on Base (via live get_swap_price)
- **cbBTC** — tradeable (USDC→cbBTC returned a real price).
- **cbETH** — address resolves but `Swap unavailable: Insufficient liquidity` (not usable today).
- **SOL/AVAX/LINK/ONDO/PAXG** — NOT in the verified map. Do **NOT** fabricate
  addresses for them; leave them "unsupported" until a real address is looked up
  and tested against `get_swap_price`.

## If execution breaks again
Re-apply Patches 1-3 (they're in-place edits lost on reinstall). Then check for a
`CDP_WALLET_SECRET` env var — that's the credential gate after the parser. If a newer
`cdp-sdk` ships, prefer upgrading over patching.

## Honest-engineering note
Do NOT report "swap executed" when it did not. If execution is blocked, say so plainly,
confirm the funds are safely placed, and offer the unblock path — the read-only
price/basis layer is still genuinely live and useful.
