---
name: defi-onchain-position-reader
description: "Read on-chain DeFi LP positions from EVM chains using web3.py. Handles factory-based DEX protocols (LFJ, Uniswap V3, etc.) with dynamic pair addresses, ERC-1155/ERC-721 position tokens, and ABI mismatch recovery via raw RPC calls."
tags: [defi, web3, avalanche, on-chain, lp-position, smart-contract]
trigger: "When you need to read on-chain LP position data, query smart contract balances, or build a script to monitor DeFi positions directly from blockchain RPC. Use when off-chain APIs (DexScreener, CoinGecko) don't provide the granularity needed — e.g., per-bin position breakdowns, share-of-pool calculations, or real-time reserve data."
version: 1.1.0
author: Gentech
---

# DeFi On-Chain Position Reader

Build Python scripts that read LP position data directly from EVM-compatible blockchains using web3.py.

## When to Use vs. Off-Chain APIs

| Need | Use |
|------|-----|
| Price, volume, TVL | DexScreener / CoinGecko (see `market-macro-monitor`) |
| Per-bin share breakdown, exact reserve allocations, position NFT data | **This skill** — on-chain reads |

## Environment Setup

web3.py must be installed in an isolated venv (system Python is externally managed):

```bash
# Create venv
uv venv /root/.hermes/scripts/.venv --python 3.11

# Install web3 + requests
uv pip install --python /root/.hermes/scripts/.venv/bin/python web3 requests
```

Script shebang: `#!/root/.hermes/scripts/.venv/bin/python3`

## General Pattern

1. **Find contract addresses** — docs, SDK repos, or block explorer
2. **Get ABIs** — from verified source on block explorer, or SDK `constants/*.ts`
3. **Connect to RPC** — public endpoints work for reads
4. **Discover pair/pool addresses** — factory contract lookups
5. **Read position data** — balanceOf/balanceOfBatch on position tokens
6. **Calculate user share** — (user_shares / total_supply) × reserves

## Common Pitfalls

### ABI Return Order ≠ SDK Documentation
SDK docs often list struct fields in a different order than the actual ABI encoding. **Always verify with raw `eth_call` and manual decoding:**

```python
# Raw call + manual decode
result = w3.eth.call({'to': factory_addr, 'data': calldata})
field_0 = int.from_bytes(result[0:32], 'big')
field_1 = int.from_bytes(result[32:64], 'big')
# Map to known fields by value range (addresses are 20 bytes, bin steps are small ints)
```

### Function Selector Calculation
```python
from web3 import Web3
selector = Web3.keccak(text='functionName(type1,type2,type3)')[:4]
```

### Dynamic Pair/Pool Addresses
Many DEXes (LFJ, Uniswap V3) create pool contracts dynamically via factories. You must call the factory to find the pool address — it's not hardcoded.

### ERC-1155 vs ERC-721
Some DEXes (LFJ Liquidity Book) use ERC-1155 for positions (not ERC-721 like Uniswap V3). Token IDs often encode bin/tick information.

### RPC Batch Limits
`balanceOfBatch` may fail on large arrays. Batch in chunks of 50-100:
```python
batch_size = 100
for start in range(0, total, batch_size):
    chunk_ids = ids[start:start+batch_size]
    balances = pair.functions.balanceOfBatch(accounts, chunk_ids).call()
```

## LFJ (Avalanche) — Specific Reference

### ⚠️ CRITICAL: V2.1 vs V2.2 ABI Mismatch

The LFJ factory at `0xb43120c4745967fa9b93E79C149E66B0f2D6Fe0c` returns **V2.1 pair contracts** (minimal proxies), NOT V2.2. The SDK docs and GitHub repos document V2.2 function names, but the on-chain contracts use different names. **Always verify function names with raw `eth_call` before building a script.**

### Contracts (Avalanche C-Chain, Chain ID 43114)
| Contract | Address |
|----------|---------|
| LB Factory | `0xb43120c4745967fa9b93E79C149E66B0f2D6Fe0c` |
| WAVAX | `0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7` |
| USDC | `0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E` |

### Known Active AVAX/USDC Pool
| Pair | Pool Address | Notes |
|------|-------------|-------|
| WAVAX/USDC (binStep 10) | `0x864d4e5ee7318e97483db7eb0912e09f161516ea` | LFJ V2.2, actively tracked |

### ⚠️ Pool Address Verification
**Always verify a pool address has contract code before attempting reads.** A common source of errors is stale runbook addresses or typos. Check via `eth_getCode`:
```python
payload = json.dumps({"jsonrpc":"2.0","method":"eth_getCode","params":[address,"latest"],"id":1}).encode()
```
If the returned bytecode is `0x` (empty), the address has no contract — do not attempt further reads. Document the discrepancy in the runbook and use the verified address from your config file instead.

### V2.1 Function Names (correct for deployed contracts)
| Purpose | V2.1 (deployed) | V2.2 (SDK docs) |
|---------|-----------------|-----------------|
| Active bin | `getActiveId()` | `activeBin()` |
| Token X address | `getTokenX()` | `tokenX()` |
| Token Y address | `getTokenY()` | `tokenY()` |
| Bin reserves | **NOT AVAILABLE** | `getBin(uint256)` |
| User shares | `balanceOf(address,uint256)` | same |
| Total shares | `totalSupply(uint256)` | same |
| Pool reserves | `getReserves()` | same |

### V2.1 Contract Architecture
- Pair contracts are **EIP-1167 minimal proxies** (~96 bytes bytecode)
- Implementation contract: `0x7a5b4e301fc2b148cefe57257a236eb845082797`
- Immutable args embedded in proxy bytecode: tokenX, tokenY, binStep, factor
- `getBin(uint256)` does NOT exist on V2.1 — per-bin reserves are not accessible via contract calls
- Position calculation must use share percentages, not reserve amounts

### getLBPairInformation Return Format
**⚠️ SDK docs say:** `(LBPair, binStep, baseFactor, ...)`
**Actual on-chain return:** `(binStep, LBPair_address, baseFactor, ...)`

The first field is `binStep` (small int), second is `LBPair` address (20 bytes padded to 32). Verify by checking value range.

### Pair Discovery
Pairs are created per (tokenA, tokenB, binStep). Common bin steps for major pairs: 10, 25, 50. Check both token orderings (WAVAX/USDC and USDC/WAVAX).

### Position Data
- LFJ uses ERC-1155 (LBToken), not ERC-721
- Token ID = Bin ID (the concentrated liquidity bin)
- `balanceOf(wallet, binId)` returns user's shares in that bin
- `totalSupply(binId)` returns total shares in that bin
- User's share = (user_shares / total_supply) × 100%
- **CRITICAL: Scan outward from active bin, not linearly.** Linear scan (start_id → end_id) breaks early on consecutive zeros and misses positions that aren't adjacent to active bin. Use bidirectional scan: check bin 0, then -1/+1, -2/+2, etc.
- Early exit after 20+ consecutive empty offsets (not consecutive bins) to avoid missing spread-out positions

### Debugging Reverted Calls
When ALL contract calls revert (return empty/zero), the script silently returns 0 positions. **The AI agent will then hallucinate realistic-looking but fake data.** Always:
1. Test each function selector individually with raw `eth_call`
2. Check if the contract is a minimal proxy (code size < 200 bytes)
3. Extract implementation address from bytecode if needed
4. Verify selectors exist in the implementation bytecode

### RPC Endpoint
```
https://api.avax.network/ext/bc/C/rpc
```

## Light-Weight Wallet Monitoring (No web3.py)

For simpler needs — wallet balances, recent transactions, token holdings — use a block explorer API instead of web3.py. Much lighter, no venv setup required.

### Routescan API (Avalanche)
```python
import json, urllib.request

ROUTESCAN = "https://api.routescan.io/v2/network/mainnet/evm/43114/etherscan/api"
WALLET = "0x..."

# Native AVAX balance
url = f"{ROUTESCAN}?module=account&action=balance&address={WALLET}&tag=latest"
data = json.loads(urllib.request.urlopen(url).read())
avax_bal = int(data["result"]) / 1e18

# ERC-20 token balance (e.g., USDC)
usdc_contract = "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e"
url = f"{ROUTESCAN}?module=account&action=tokenbalance&contractaddress={usdc_contract}&address={WALLET}&tag=latest"
data = json.loads(urllib.request.urlopen(url).read())
usdc_bal = int(data["result"]) / 1e6

# Recent transactions
url = f"{ROUTESCAN}?module=account&action=txlist&address={WALLET}&sort=desc&page=1&offset=10"
data = json.loads(urllib.request.urlopen(url).read())
for tx in data["result"][:5]:
    print(f"{tx['functionName'][:40]} | {int(tx['value'])/1e18:.4f} AVAX")
```

### When to Use Which
| Need | Approach |
|------|----------|
| Wallet balances, recent txs, token holdings | Routescen API (lightweight, no deps) |
| Per-bin position breakdown, share-of-pool | web3.py (this skill's main pattern) |
| Real-time LP position NFT data | web3.py + ERC-1155 reads |
| Quick portfolio snapshot | Routescen + CoinGecko price lookup |

### Avalanche Token Contracts (Quick Reference)
| Token | Contract |
|-------|----------|
| USDC | `0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e` |
| WAVAX | `0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7` |
| USDT | `0x9702230a8ea53601f5cd2dc00fdbc13d4df4a8c7` |
| LINK | `0x5947bb275c521040051d82396192181b413227a3` |
| JOE | `0x6e84a6216eA6dACC71eE8E6b0a5B7322EEbC0fDd` |

### Pitfalls
- **Routescan rate limits** — no explicit limits documented, but batch requests sparingly
- **`~` expansion** — same issue as web3.py scripts. Use absolute paths in config reads
- **Snowtrace** — `api.snowtrace.io` is often blocked by bot detection. Use Routescan as primary

## Combined LP Monitor + Wallet Tracker

For ongoing monitoring, combine LP position data with wallet balances in a single script. This avoids duplicate cron jobs and gives the agent a complete picture.

### Pattern: Single Script, Both Data Sources

```python
#!/usr/bin/env python3
"""Combined LP + Wallet monitor — outputs JSON for cron agent."""

import json, os, urllib.request
from datetime import datetime, timezone

WALLET = "0x..."
ROUTESCAN = "https://api.routescan.io/v2/network/mainnet/evm/43114/etherscan/api"
POOL_ADDRESS = "0x..."

def fetch_wallet_data():
    """Fetch native balance + ERC-20 balances + recent txs."""
    # Native AVAX
    url = f"{ROUTESCAN}?module=account&action=balance&address={WALLET}&tag=latest"
    data = json.loads(urllib.request.urlopen(url).read())
    avax_bal = int(data["result"]) / 1e18

    # ERC-20 (USDC)
    usdc_contract = "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e"
    url = f"{ROUTESCAN}?module=account&action=tokenbalance&contractaddress={usdc_contract}&address={WALLET}&tag=latest"
    data = json.loads(urllib.request.urlopen(url).read())
    usdc_bal = int(data["result"]) / 1e6

    # Recent LP activity
    url = f"{ROUTESCAN}?module=account&action=txlist&address={WALLET}&sort=desc&page=1&offset=5"
    data = json.loads(urllib.request.urlopen(url).read())
    recent = []
    for tx in data.get("result", [])[:3]:
        fn = tx.get("functionName", "transfer")
        if "addLiquidity" in fn: action = "➕ Added"
        elif "removeLiquidity" in fn: action = "➖ Removed"
        elif "swap" in fn.lower(): action = "🔄 Swapped"
        else: action = fn[:30]
        ts = datetime.fromtimestamp(int(tx["timeStamp"]), tz=timezone.utc).strftime("%m/%d %H:%M")
        recent.append({"time": ts, "action": action})

    return {"avax_balance": round(avax_bal, 4), "usdc_balance": round(usdc_bal, 2), "recent_activity": recent}

# Combine with LP price data from DexScreener, then print JSON
```

### Why Combined?
- One cron job instead of two (fewer API calls, simpler mental model)
- Agent sees wallet context alongside price data (can spot: "wallet empty, all in LP")
- Recent activity shows if position was recently rebalanced

## Wiring Into Hermes Cron Jobs

On-chain scripts can be attached to cron jobs as `script:` pre-hooks. The script runs first, outputs JSON to stdout, and the agent prompt receives the output as context.

```python
# In the script, print JSON:
print(json.dumps({
    "wallet": wallet,
    "avax_price": avax_price,
    "total_avax": total_avax,
    "total_usdc": total_usdc,
    "total_value_usd": total_value_usd,
    "position_details": results
}))
```

Config file pattern: `/root/.hermes/scripts/{protocol}_config.json`

## Post-Rebalance Config Update

After every rebalance, update these files to keep monitors accurate:

1. **Position config** (`/root/.hermes/scripts/.lfj-aae-config.json`):
   - `position.token0_amount` / `position.token1_amount`
   - `position.range_low` / `position.range_high`
   - `position.shape` (curve / bid-ask / spot)
   - `position.rebalanced_at` (ISO timestamp)

2. **LP monitor script** bounds:
   - Update `LOW_BOUND` and `HIGH_BOUND` constants in `lfj_monitor.py`

3. **lfj_config.json** notes field:
   - Update with new range, shape, date

4. **Verify** by running the monitor script and checking `in_range` reflects new bounds.

### Silent Reverts → Agent Hallucination (CRITICAL)
When a contract function doesn't exist, `eth_call` reverts silently and returns empty bytes. The script reads this as 0/empty and produces zero-position output. **The AI agent consuming this output will then hallucinate realistic-looking but completely fake data** (e.g., "8.72 AVAX + $92.69 USDC" when the real position was never read).

**Prevention:**
1. Always test each function selector with a raw `eth_call` before building the script
2. If the script returns 0 positions, log a warning — don't let the agent assume data
3. Add a `note` field in JSON output when data couldn't be fully read

## Testing Checklist

1. ✅ Script syntax valid: `python3 -c "import ast; ast.parse(open('script.py').read())"`
2. ✅ RPC connection works: `w3.is_connected()`
3. ✅ Factory returns non-zero pair addresses
4. ✅ **Each function selector verified with raw `eth_call` (not just ABI-based calls)**
5. ✅ User has non-zero balanceOf in at least one bin
6. ✅ Reserve calculation yields reasonable USD values
7. ✅ **Script outputs a warning/error when data is incomplete, not silent zeros**
