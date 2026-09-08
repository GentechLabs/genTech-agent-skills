# Across V3 Contract Investigation (Jul 26, 2026)

## Background

Attempted to bridge $20.99 USDC from Base to Hyperliquid via Across Protocol
for GTA arb trading. The depositV3 call succeeded on Base (tx confirmed,
FundsDeposited event emitted) but the relay to Hyperliquid never completed.
Fill deadline passed without the funds arriving.

## Finding the Implementation

The SpokePool at `0x09aea4b2242abC8bb4BB78D537A67a245A7bEC64` is an **EIP-1967
transparent proxy** — all calls go through a proxy that delegates to an
implementation.

**Implementation address:** `0x77aa19d49484cc88c2ca1c8527226e891c5c72d8`

Found via EIP-1967 storage slot:

```
eth_getStorageAt(proxy, "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc")
```

The implementation() call (0x5c60da1b) also works but may revert on some
proxy patterns.

## Function Selector Discovery

The implementation bytecode was fetched via `eth_getCode`. The function
dispatcher in the preamble lists ~70 function selectors. These were compared
against the ISpokePool interface (25 functions from the npm package
`@across-protocol/contracts` artifact) — 51 extra selectors exist.

Unknown selectors were looked up on 4byte.directory:

### Confirmed Across V3 Functions

| Selector | Function | Notes |
|----------|----------|-------|
| 0x7b939232 | depositV3(address,address,address,address,uint256,uint256,uint256,address,uint32,uint32,uint32,bytes) | ✅ Used successfully |
| 0xc35c83fc | fillStatuses(bytes32) | ✅ Returns 0/1/2 |
| 0xd7e1583a | getV3RelayHash((bytes32,bytes32,bytes32,bytes32,bytes32,uint256,uint256,uint256,uint256,uint32,uint32,bytes)) | ✅ Computes relay hash |
| 0xac9650d8 | multicall(bytes[]) | ✅ Batch execution |
| 0xf79f29ed | relayerRefund(address,address) | View function, returns uint256 |
| 0x1b3d5559 | executeRelayerRefundLeaf(uint32,(...),bytes32[]) | Relayer-only, merkle proof |
| 0x97943aa9 | fillRelayWithUpdatedDeposit(...) | Relayer function |
| 0x541f4f14 | depositFor(...) | Old deprecated variant |
| 0x1fab657c | executeSlowRelayLeaf(...) | Relayer function |
| 0x979f2bc2 | ... | Not identified |
| 0x2e63e59a | proxiableUUID() | UUPS pattern |

### Functions NOT Found (not in bytecode)

- `deposit(address,...)` — does NOT exist (selector 0xd2645d20 not found)
- `withdrawDeposit(bytes32,address,uint256)` — NOT found
- `withdrawDeposit(address,address,uint256)` — NOT found
- `refundDeposit(address,address,uint256)` — NOT found
- `executeRefund(bytes32,uint256,address)` — NOT found
- `withdrawExpiredDeposit(...)` — NOT found

**Conclusion: Across V3 has no depositor-initiated refund function.**

## Checking Fill Status

```python
# 1. Get relay hash
relay_struct = (depositor_bytes32, recipient_bytes32, ..., message_bytes)
hash_sel = Web3.keccak(text="getV3RelayHash((bytes32,bytes32,bytes32,bytes32,bytes32,uint256,uint256,uint256,uint256,uint32,uint32,bytes))")[:4].hex()
hash_calldata = "0x" + hash_sel + abi_encode(['(bytes32,bytes32,bytes32,bytes32,bytes32,uint256,uint256,uint256,uint256,uint32,uint32,bytes)'], [relay_struct]).hex()
relay_hash = w3.eth.call({'to': PROXY, 'data': hash_calldata})

# 2. Check fillStatuses
fill_sel = Web3.keccak(text="fillStatuses(bytes32)")[:4].hex()
status_data = fill_sel + relay_hash[2:]
status = int(w3.eth.call({'to': PROXY, 'data': status_data}).hex(), 16)
# 0 = UNFILLED, 1 = FILLED, 2 = REQUESTED_SLOW_FILL
```

## Deposit Address API (Blocked)

The Across API at `app.across.to/api/deposit-addresses` generates a unique
deposit address for Base→Hyperliquid deposits. This endpoint requires:
- `integratorId` query param
- `Authorization: Bearer <api_key>` header
- The API key is embedded in the Hyperliquid frontend JS bundle

Without these, returns 403. This is what the Hyperliquid frontend uses when
users deposit from the app.

## Getting the ABI

1. **From a personal device:** `basescan.org/address/0x77aa19d49484cc88c2ca1c8527226e891c5c72d8#code`
   (Cloudflare blocks automated requests but personal browsers work fine)

2. **From the npm package:**
   ```
   npm view @across-protocol/contracts dist-tags  → latest: 5.0.24
   npm pack @across-protocol/contracts
   tar xzf across-protocol-contracts-5.0.24.tgz
   # ABI at: package/dist/evm/artifacts/ISpokePool.sol/ISpokePool.json
   ```

3. **From the SDK:**
   ```
   npm view @across-protocol/sdk-v2 dist-tags  → latest version
   # Interfaces in package/src/interfaces/SpokePool.ts
   ```

## Key Learnings

- Always use `depositV3()` NOT `deposit()` — the old function doesn't exist
- The Across relay for Hyperliquid (chain 999) may not be reliable —
  deposits can confirm on Base but never relay
- No way to manually trigger a refund from the contract
- For reliable deposits, use the Hyperliquid app UI (which generates a
  deposit address via the Across API with proper relayer coverage)
- Blockrun RPC (api.blockrun.ai) + 4byte.directory is a viable fallback
  when BaseScan/Etherscan is blocked
