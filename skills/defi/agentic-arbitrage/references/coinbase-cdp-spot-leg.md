# Coinbase CDP Spot Leg — GTA Execution (verified Aug 3, 2026)

The verified, working path for executing the **"long spot" / "sell spot"** leg of a
basis trade via Coinbase Developer Platform (`cdp-sdk` v1.47). The other half of
contango (short perp on Hyperliquid) is detection-only for US residents — see SKILL.md.

## Env vars (profile .env, chmod 600, never commit)
- `CDP_API_KEY_ID` — the API key UUID
- `CDP_API_KEY_SECRET` — the private key (base64-ish)
Both go in `/root/.hermes/profiles/gentech/.env`. The SDK reads them via
`os.getenv("CDP_API_KEY_ID")` / `os.getenv("CDP_API_KEY_SECRET")`.

## The two quote paths (CRITICAL distinction)
| Method | Needs funding? | Use for |
|--------|---------------|---------|
| `client.evm.get_swap_price(...)` | **NO** — works on empty wallet | Read-only basis/price oracle. **The "what's the price on this platform" signal.** |
| `client.evm.create_swap_quote(...)` | **YES** — fails with `gasFee ... None` on unfunded account | Real execution quote |

On an empty CDP wallet, `create_swap_quote` raises
`1 validation error for CommonSwapResponseFees / gasFee / Input should be a valid
dictionary ... input_value=None`. That's a funding wall, not a bug — don't chase it;
use `get_swap_price` for anything read-only.

## Swap API contract requirements (real gotchas)
- **Contract ADDRESSES, not tickers.** Passing `"USDC"` / `"paxg"` fails validation
  (`must validate the regular expression /^0x[a-fA-F0-9]{40}$/`).
- **RAW integer amounts, not decimals.** `"0.5"` fails (`must validate /^\d+$/`).
  Convert human → raw: `str(int(round(human * 10**dec)))`.
- **Networks:** enum-validated strings — `'base'`, `'base-sepolia'`, `'ethereum'`.
  Not `base-mainnet`, not `ethereum-mainnet`.

## Verified Base addresses
- **USDC (native Base):** `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` (6 dec)
- **cbBTC:** `0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf` (8 dec) — **confirmed tradeable**
- **cbETH:** `0x2Ae3F1Ec37F1F233c8DF50054f9E5b7E7C2d3B1A` — resolves but currently
  "insufficient liquidity"; re-verify before enabling.

## ⚠️ NEVER fabricate contract addresses (hard rule)
Only list addresses you have VERIFIED against the live API. Do not invent a hex
address for SOL/AVAX/PAXG/etc. to make a token "work" — a fake address that resolves
nothing is worse than an honest "unsupported." If a token isn't verified, mark it
unsupported until you look up the real address and test `get_swap_price` against it.
This session caught a fabricated-address slip before it shipped; don't repeat it.

## Working executor
`scripts/gta_coinbase_leg.py` — `run_spot_leg(plan, dry_run, amount, network)`:
- plan = `{symbol, perp_side, spot_side, ...}`
- `spot_side == 'buy'`  → swap USDC → token (fund the long spot)
- `spot_side == 'sell'` → swap token → USDC (exit the spot)
- dry_run always quotes via `get_swap_price` first; returns `executed: False`
- real mode only on explicit request; refuses to fake a successful order
Test suite: `scripts/test_gta_coinbase_leg.py` (15/15 green incl. live BTC quote).

## Pattern: async SDK
The CDP SDK is `asyncio`-based — `await c.evm.list_accounts()`, `await c.close()`.
Calling a coroutine without awaiting yields `TypeError: object of type 'coroutine'
has no len()`. Always `asyncio.run(main())` with an async main.
