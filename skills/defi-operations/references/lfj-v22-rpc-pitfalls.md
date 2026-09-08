# LFJ V2.2 On-Chain RPC Pitfalls

## The Problem

`getActiveId()` and `getBinStep()` function calls **revert** on LFJ V2.2 pools via public RPC (`https://api.avax.network/ext/bc/C/rpc`).

The selectors `0x80afabfa` (getActiveId) and `0xd327e941` (getBinStep) return `execution reverted` with no data.

## Root Cause

Unknown — likely one of:
- The pool contract uses a proxy pattern and these functions aren't exposed at the proxy level
- The V2.2 ABI differs from V2.1 in function naming or signature
- Public RPC nodes may not support certain view function calls on these contracts

## What Works

| Method | Selector | Status |
|--------|----------|--------|
| `getReserves()` | `0x0902f1ac` | ✅ Works — returns reserveX, reserveY |
| `balanceOf(address,uint24)` | `0xca282843` | ✅ Works — returns LP token balance per bin |
| `totalSupply(uint24)` | via multicall | ✅ Works — returns bin total supply |

## What Doesn't Work

| Method | Selector | Status |
|--------|----------|--------|
| `getActiveId()` | `0x80afabfa` | ❌ Reverts |
| `getBinStep()` | `0xd327e941` | ❌ Reverts |
| `factory()` | `0xc45a0158` | ❌ Reverts |
| `getFactory()` | `0x5aa6e675` | ❌ Reverts |

## Workarounds

1. **DexScreener** — returns current price directly (no bin math needed)
2. **LFJ Subgraph** — if available, provides bin-level data
3. **@traderjoe-xyz/sdk-v2** — handles ABI correctly but requires working viem installation
4. **Screenshots** — last resort, extract from LFJ web UI

## Bin Price Calculation (When getActiveId Works)

```python
bin_step = 10  # from pool config
scale = 10**12  # 18 - 6 decimals (AVAX - USDC)

def price_from_id(bin_id):
    return (1 + bin_step / 10000) ** bin_id * scale
```

## Pool Details

- **Pool:** `0x864d4e5ee7318e97483db7eb0912e09f161516ea`
- **Chain:** Avalanche C-Chain
- **Type:** LFJ V2.2 (Trader Joe Liquidity Book)
- **Fee Tier:** 5 bps
- **Bin Step:** 10
- **Token0 (AVAX):** `0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7` (18 decimals)
- **Token1 (USDC):** `0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E` (6 decimals)
- **Wallet:** `0x7ebff188f2Eba16518C02864589b1403a5d1296a`
