# Algebra / Blackhole CL pool — chain reads (concrete patterns)

Raw word-decode over `eth_call`/`eth_getLogs` is the robust path; web3.py ABI
objects break on field-order mismatches (NonEmptyPaddingBytes) — decode 32-byte
words by hand instead. Probe every selector once at `latest` before bulk use;
keep only selectors that return data (a reverted call returns 0x, which a naive
parser reads as 0).

## Selectors (Algebra CL pool)

| What | Selector | Decode |
|---|---|---|
| globalState | `0xe76c01e4` | words: price uint160, tick int24 (sign-fix: `v-2**24 if v>=2**23`), fee uint16 (÷10000 = %) |
| active liquidity | `0x1a686502` | uint128; ÷1e18 for e18 display |
| totalFeeGrowth0Token | `0x6378ae44` | uint256 (Q128 fixed point) |
| totalFeeGrowth1Token | `0xecdecf42` | uint256 |
| ERC20 balanceOf(pool) | `0x70a08231` + pool address padded to 64 | ÷10^decimals |

## Pool price (USD) — derive from globalState, NOT the reserve ratio

The reserve ratio of a concentrated pool is position composition, not price.
Deriving spot from reserves understated AVAX ~4.5x, inflated TVL ~3x, and fired
a bogus collapse alert. Use the pool's own state:

```python
words = decode(eth_call(POOL, '0xe76c01e4'))      # globalState()
price_q, tick, fee = words[0], signfix(words[1]), words[2]
raw = (price_q / 2**96) ** 2                      # token1 raw per token0 raw
t0, t1 = token0(POOL), token1(POOL)               # 0x0dfe1681 / 0xd21220a7
p_t0_in_t1 = raw * 10**(dec0 - dec1)              # then x token1/USD price
```

For pools where reserves ARE the price basis (volatile/solidly-style constant-
product pools), still resolve `token0()`/`token1()` first — assuming the order
produced a $24k token price and an 11-digit emissions APR. Whatever the method,
bounds-check the derived USD value in the script and REFUSE an implausible one
instead of reporting it.

## Swap events → volume

- topic0 (UniV3-style; Algebra emits the same signature):
  `0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67`
- data words 0/1 are amount0, amount1 as SIGNED int256:
  `a = raw - 2**256 if raw >= 2**255 else raw`
- per-swap USD volume = `(|a0|/10^dec0 × price + |a1|/10^dec1) / 2`
- LP fee revenue = volume × feeTier (e.g. 0.0005 for the 0.05% tier)

## Pagination (public RPCs silently cap eth_getLogs ranges)

A wide-range query returns an EMPTY result that looks like "0 swaps". Paginate:

```python
CHUNK = 2000
for lo in range(head - blocks, head, CHUNK):
    hi = min(lo + CHUNK - 1, head)
    logs = rpc('eth_getLogs', [{'address': POOL, 'topics': [SWAP],
                                'fromBlock': hex(lo), 'toBlock': hex(hi)}])
```

Control test first: 2000-block window on the pool must return logs; if even a
small window is empty while an unrelated busy contract returns logs, the pool
genuinely has no swaps. Historical block offsets on a 2s chain:
24h=43200, 3d=129600, 7d=302400, 14d=604800, 30d=1296000.

## DefiLlama endpoints

- TVL trend: `https://api.llama.fi/protocol/<slug>` → `chainTvls.<Chain>.tvl`
  list of `{date, totalLiquidityUSD}`; sample now / −7d / −30d entries.
- Venue fees: `https://api.llama.fi/summary/fees/<slug>?dataType=dailyFees` →
  `total24h`, `total7d`, `total30d`, `change_1d`.
- Sanity: venue fees/TVL annualized gives the whole-venue yield ballpark;
  a single pool's share of venue TVL bounds its expected share of venue fees.
