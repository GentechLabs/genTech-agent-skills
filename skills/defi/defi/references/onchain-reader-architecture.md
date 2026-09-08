# On-Chain Position Reader — Agent Kit Template Architecture

**Date:** 2026-06-16 (updated)
**Status:** Working on Jordan's wallet (Avalanche LFJ V2.1)
**Purpose:** Universal template for reading LP positions from any EVM chain/DEX

## Architecture (3 Layers)

```
Layer 1: Chain-Agnostic (works everywhere)
  ├── RPC balance queries (native + ERC-20)
  ├── DexScreener / Pyth price feeds
  └── Routescan event logs (free, no API key)

Layer 2: DEX-Specific Adapters
  ├── LFJ (Trader Joe V2.1): balanceOf per bin via SDK ABIs ✅
  ├── Uniswap V3: NonfungiblePositionManager.positions(tokenId) 📋
  ├── Pangolin V2: Similar to LFJ (fork) 📋
  └── Aerodrome/Velodrome: veNFT position reads

Layer 3: Unified Output
  └── defi-data.json format (compatible with all dashboards)
```

## Working Implementation (Node.js + viem)

**Location:** `/root/projects/lp-reader/reader.mjs`
**Cron wrapper:** `/root/vaults/gentech/scripts/run-reader.sh`
**Schedule:** Every 3 hours via Hermes cron
**Agent Kit doc:** `/root/projects/genTech-agent-kit/docs/ONCHAIN-LP-READER.md`

### Dependencies
```bash
npm install @traderjoe-xyz/sdk @traderjoe-xyz/sdk-v2 @traderjoe-xyz/sdk-core viem
```

### Key Pattern: balanceOf per bin
```javascript
import sdkV2 from '@traderjoe-xyz/sdk-v2';
const { LBPairV21ABI } = sdkV2;  // MUST use V2.1 ABI for Avalanche pools

// Scan ±200 bins around active to find wallet's position
for (let binId = activeId - 200; binId <= activeId + 200; binId++) {
  const bal = await client.readContract({
    address: POOL, abi: LBPairV21ABI,
    functionName: 'balanceOf', args: [wallet, BigInt(binId)],
  });
  if (bal > 0n) found.push({ binId, liquidity: bal });
}

// Calculate actual token amounts per bin
const share = Number(userLiquidity) / Number(totalSupply);
const userX = share * binReserveX / 1e18;  // WAVAX
const userY = share * binReserveY / 1e6;   // USDC
```

### Multicall for Performance
```javascript
// Batch totalSupply + getBin for all found bins in one multicall
const calls = found.flatMap(b => [
  { address: POOL, abi: LBPairV21ABI, functionName: 'totalSupply', args: [BigInt(b.binId)] },
  { address: POOL, abi: LBPairV21ABI, functionName: 'getBin', args: [BigInt(b.binId)] },
]);
const results = await client.multicall({ contracts: calls });
```

## Critical: V2.1 vs V2.2 ABI

The pool at `0x864d...` on Avalanche is **V2.1**, not V2.2.

| Function | V2.1 | V2.2 |
|----------|------|------|
| Pool reserves + active ID | `getReserves()` + `getActiveId()` (separate) | `getReservesAndId()` (combined) |
| Bin liquidity | `balanceOf(address, uint256)` ✅ | `balanceOf(address, uint256)` ✅ |
| Bin reserves | `getBin(uint256)` | `getBin(uint256)` |
| Total supply per bin | `totalSupply(uint256)` | `totalSupply(uint256)` |

**Always verify which ABI version the pool uses before building.**

```javascript
try {
  await client.readContract({ address: POOL, abi: LBPairV21ABI, functionName: 'getReserves' });
  console.log('Pool is V2.1');
} catch { /* try V2.2 with LBPairABI */ }
```

## Free Data Sources (Verified)

| Source | What | Cost | Reliability |
|--------|------|------|-------------|
| Chain RPC (public) | Wallet balances, eth_call, multicall | Free | High |
| DexScreener API | Price, volume, TVL, 24h change | Free | High |
| Routescan API | Event logs, tx history, token transfers | Free | High |
| LFJ SDK (npm) | Contract ABIs for V2.1/V2.2 pools | Free | High |

## DEX Adapter Patterns

### LFJ (Trader Joe V2.1) — Direct Contract Reads ✅
- Pool IS the LBToken (ERC-1155-like): each bin = tokenId
- `balanceOf(wallet, binId)` returns liquidity shares per bin
- `totalSupply(binId)` + `getBin(binId)` → user's share of bin reserves
- **Scan range:** ±200 bins from active covers most positions (30-60 bins typical)
- Pool is EIP-1167 proxy, but SDK ABIs handle delegation correctly

### Uniswap V3 — NFT Position Manager (Template)
- Each position is an NFT (ERC-721)
- `NonfungiblePositionManager.positions(tokenId)` returns:
  - token0, token1, fee, tickLower, tickUpper, liquidity
- Read `balanceOf(wallet)` → count → `tokenOfOwnerByIndex` → tokenId
- NFT Manager: `0xC36442b4a4522E871399CD717aBDD847Ab11FE88` (Ethereum)

### Pangolin V2 — Similar to LFJ (Fork)
- Same `balanceOf` per-bin pattern, different contract addresses

## Routescan Event Query Format

```
https://api.routescan.io/v2/network/mainnet/evm/{CHAIN_ID}/etherscan/api?
  module=logs&action=getLogs&address={POOL}&topic0={EVENT}&topic3={WALLET_PADDED}
```

**Chain IDs:** Avalanche=43114, Base=8453, Ethereum=1, Polygon=137, Arbitrum=42161, BSC=56

## Known Pitfalls

1. **V2.1 vs V2.2 ABI mismatch** — Test `getReserves()` vs `getReservesAndId()` first.
2. **Min proxy reverts** — Raw `eth_call` to EIP-1167 proxy can revert without proper ABI. Use SDK ABIs.
3. **Scan range too narrow** — If position spans >200 bins, increase range. Most LFJ positions are 30-60 bins.
4. **Price from bin formula** — The exponential formula `price = (1+binStep/10000)^(activeId-2^23)` produces wrong values for V2.1 pools. Use DexScreener for reliable USD price. For visualization, use linear bin-to-price mapping.
5. **Multicall batch size** — viem defaults work. For 400+ calls, split into batches of 50-100.
6. **Python vs Node.js** — Python stdlib works for simple reads but lacks multicall. Node.js + viem is significantly faster for bin scanning (30 bins in ~2s vs ~30s sequential).
7. **Dashboard data path** — The reader MUST write to the same directory the HTML fetches from. Mismatch between root vault (`/root/vaults/gentech/defi-data.json`) and `DeFi/` folder caused stale dashboard data on GitHub Pages.

## Dashboard Visualization (Bar Chart Style)

The dashboard uses a canvas-based bar chart renderer (like LFJ's app) instead of a bell curve:

- **Green bars** = USDC side of position (lower price bins)
- **Purple bars** = AVAX side (higher price bins)
- **Pink bar** = Active/rewarded bin (closest to current price)
- **Red dashed line** = Current price marker
- **Legend** at bottom: USDC / AVAX / Active

The renderer expects `curveData` with format:
```json
{
  "currentPrice": 6.93,
  "rangeMin": 6.78,
  "rangeMax": 7.02,
  "bins": [
    {"price": 6.78, "depth": 0.047},
    {"price": 6.79, "depth": 0.069}
  ]
}
```

Where `depth` is normalized 0-1 (liquidity amount / max liquidity across all bins).

The `LPCurveRenderer` class in `defi-dashboard.html` handles rendering with ease-out cubic animation.
