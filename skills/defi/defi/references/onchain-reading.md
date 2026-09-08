# On-Chain Position Reading (Full)

> Absorbed from `defi` skill §3. Complete on-chain reading guide.

## When to Use

| Need | Use |
|------|-----|
| Price, volume, TVL | DexScreener / CoinGecko |
| Per-bin share breakdown, exact reserves | **On-chain reads** |

## LFJ V2.1 (Avalanche)

**⚠️ Pool at `0x864d...` is V2.1, NOT V2.2.**

| Function | V2.1 | V2.2 |
|----------|------|------|
| Pool state | `getReserves()` + `getActiveId()` (separate) | `getReservesAndId()` (combined) |
| Per-bin balance | `balanceOf(address, uint256)` ✅ | `balanceOf(address, uint256)` ✅ |

**⚠️ EIP-1167 proxy:** `balanceOf` reverts with raw `eth_call`. Use viem multicall with SDK ABI.

## Working Node.js/viem Approach (Production)

**Reader:** `/root/projects/lp-reader/reader.mjs`

```bash
cd /root/projects/lp-reader
npm install @traderjoe-xyz/sdk @traderjoe-xyz/sdk-v2 @traderjoe-xyz/sdk-core viem
node reader.mjs --wallet 0xYourAddress
```

**Architecture:**
- Uses `LBPairV21ABI` (not V2.2)
- Bin scanning: ±200 bins around active
- Position value: `(userLiquidity / totalSupply) × binReserves` per bin
- Price: DexScreener (bin formula doesn't work for V2.1)
- Output: `DeFi/defi-data.json` with curve data

**Output path:** MUST write to `DeFi/defi-data.json` — dashboard reads relative to itself.

## Pure JSON-RPC Alternative (No Dependencies)

```python
import json, urllib.request

def rpc(chain_url, method, params=None):
    payload = json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params or []}).encode()
    req = urllib.request.Request(chain_url, data=payload, headers={'Content-Type':'application/json'})
    resp = urllib.request.urlopen(req, timeout=15)
    return json.loads(resp.read()).get('result')

# ERC-20 balance
padded_wallet = wallet.lower().replace('0x','').zfill(64)
result = rpc(RPC_URL, 'eth_call', [{'to': token_addr, 'data': f'0x70a08231{padded_wallet}'}, 'latest'])
balance = int(result, 16) / 10**decimals
```

**Works everywhere** — cron, interactive, subagents. No pip install needed.

## Chain RPC Endpoints (Free)

| Chain | Endpoint |
|-------|----------|
| Avalanche | `https://api.avax.network/ext/bc/C/rpc` |
| Base | `https://mainnet.base.org` |
| Ethereum | `https://eth.llamarpc.com` |
| Arbitrum | `https://arb1.arbitrum.io/rpc` |
| Polygon | `https://polygon-rpc.com` |
| BSC | `https://bsc-dataseed.binance.org` |

## LFJ Pool Selectors

| Selector | Function | Returns |
|----------|----------|---------|
| `0xdbe65edc` | activeId() | Current bin ID |
| `0x0902f1ac` | getReserves() | reserve0 (AVAX), reserve1 (USDC) |
| `0xe77366f8` | getSwapOut(1e18) | USDC for 1 AVAX |
| `0x00fdd58e` | balanceOf(addr, binId) | User shares |
| `0xbd85b039` | totalSupply(binId) | Total shares |
| `0x05e8746d` | tokenX() | Token X address |
| `0xda10610c` | tokenY() | Token Y address |

## Position Scanning Pattern

1. Get `activeId()` → current bin
2. Scan ±200 bins with `balanceOf(wallet, binId)`
3. For each bin with shares: `totalSupply(binId)` → share_pct
4. Price from DexScreener (bin formula broken for V2.1)
5. Output to `DeFi/defi-data.json`

## Bin-to-Price Formula (Broken for V2.1)

Standard formula `price = (1 + binStep/10000)^(activeId - 2^23)` produces wrong values for V2.1 pools. Use DexScreener for live price.

**For visualization:** Linear mapping around DexScreener price:
```javascript
const spread = 0.12;
const lowPrice = dexPrice - spread;
const highPrice = dexPrice + spread;
```

## Event-Based Position Tracking

When `balanceOf` fails (EIP-1167 proxy), reconstruct from events:

| Event | Topic0 Hash |
|-------|-------------|
| DepositedToBins | `0x4a39dc06d4c0dbc64b70af90fd698a233a518aa5d07e595d983b8c0526c8f7fb` |
| WithdrawnFromBins | `0x87f1f9dcf5e8089a3e00811b6a008d8f30293a3da878cb1fe8c90ca376402f8a` |

Query via Routescan API (free, no key):
```python
url = f'https://api.routescan.io/v2/network/mainnet/evm/43114/etherscan/api?module=logs&action=getLogs&address={POOL}&topic0={DEPOSIT_HASH}&topic3={WALLET_TOPIC}'
```

## Silent Reverts → Agent Hallucination

When a contract function doesn't exist, `eth_call` reverts silently and returns empty bytes. The script reads this as zero positions and the AI agent then **hallucinates realistic-looking but fake data.** Always test each function selector individually.

## Pitfalls

- **LFJ SDK ABI version** — SDK exports `LBPairV21ABI`, NOT `LBPairV22ABI`
- **Dashboard data path mismatch** — Reader must write to `DeFi/defi-data.json`, not root
- **Shared state file corruption** — Filter non-numeric entries from history arrays
- **HOME directory expansion** — Use absolute paths, not `~`
