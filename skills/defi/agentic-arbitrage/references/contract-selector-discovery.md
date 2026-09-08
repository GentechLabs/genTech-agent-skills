# Contract Function Selector Discovery

When the Across V3 SpokePool's `deposit()` function didn't work, this technique was used to find the correct function.

## The Proxy Layer

The contract at `0x09aea4b2242abC8bb4BB78D537A67a245A7bEC64` (Across SpokePool on Base) is an **EIP-1967 transparent proxy**. To find the implementation:

```python
implementation = eth_getStorageAt(
    proxy_address,
    "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc",  # EIP-1967 slot
    "latest"
)
```

Result: `0x77aa19d49484cc88c2ca1c8527226e891c5c72d8`

## Bytecode Function Selectors

The implementation bytecode's dispatcher lists every supported function selector. Extract them by looking for the `PUSH4 0xYYYYYYYY` pattern (`63 YYYYYYYY` in the raw hex):

```
6080604052600436101561001a575b3615610018575f80fd5b5f3560e01c8063079bd2c714...
```

Function selectors appear right after `5f3560e01c80` (the function dispatcher).

## Lookup Unknown Selectors

Use the [4byte.directory](https://www.4byte.directory) API to resolve unknown selectors:

```python
import json, urllib.request
url = f"https://www.4byte.directory/api/v1/signatures/?hex_signature={hex_sig}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read())
    for r in data.get('results', []):
        print(f'{hex_sig}: {r[\"text_signature\"]}')
```

## Getting the Full ABI

Three approaches:

1. **BaseScan (preferred):** `basescan.org/address/{impl_addr}#code` → Contract → Contract ABI. Cloudflare blocks this server; use a personal device.

2. **NPM package:** Extract from `@across-protocol/contracts` npm package:
   ```
   curl -sL "https://registry.npmjs.org/@across-protocol/contracts/-/contracts-5.0.24.tgz" \
   | tar -xzf - --to-stdout "package/dist/evm/artifacts/ISpokePool.sol/ISpokePool.json"
   ```

3. **Interface comparison:** Compare bytecode selectors against known interface selectors to identify extra functions the implementation supports beyond the interface.

## The Across V3 Refund Problem

The Across SpokePool implementation has **no `withdrawDeposit()` function** despite being a standard bridging pattern. The only refund-like function found in the bytecode is:

- `executeRelayerRefundLeaf(uint32,(uint256,uint256,uint256[],uint32,address,address[]),bytes32[])` — complex merkle-tree based refund process, not a simple public function
- `relayerRefund(address,address)` — permissioned, only callable by relayers/admins

This means if the Across relayer doesn't pick up the deposit for Hyperliquid (chain 999), the funds are **stuck in the spoke pool** with no straightforward public refund path.

To check if a deposit was filled:
```
fillStatuses(bytes32) → selector 0xc35c83fc
```
Pass the relay hash. Returns the fill status enum.

## Key Lessons

1. **Don't assume function names.** The Across V3 contract uses `depositV3` not `deposit`.
2. **Verify with bytecode.** If `estimate_gas` reverts silently, the function selector is wrong. Check the implementation bytecode directly.
3. **Proxy awareness.** Always check if a contract is a proxy before reading its bytecode. The storage slot method (`0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc`) works for EIP-1967 proxies.
4. **4byte.directory is invaluable.** When you have unknown selectors from bytecode, it's the fastest way to resolve them.
