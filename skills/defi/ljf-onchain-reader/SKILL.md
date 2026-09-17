---
name: lfj-onchain-reader
description: Read LFJ V2.2 LP positions from on-chain data using correct keccak256 selectors
---

# LFJ On-Chain LP Reader

Reads live wallet + LP position from Avalanche blockchain for LFJ V2.2 pools.

## CRITICAL: Keccak256 vs SHA3-256

Python's `hashlib.sha3_256()` is **NOT** Ethereum's keccak256. They are different hash functions. NIST standardized SHA-3 differs from the original Keccak that Ethereum uses.

**Wrong (will revert every call):**
```python
import hashlib
selector = hashlib.sha3_256(b'getActiveId()').hexdigest()[:8]  # 0x80afabfa ❌
```

**Correct:**
```python
from Crypto.Hash import keccak
selector = keccak.new(digest_bits=256, data=b'getActiveId()').hexdigest()[:8]  # 0xdbe65edc ✅
```

## Correct Selectors for LFJ V2.2

| Function | Selector |
|----------|----------|
| `getActiveId()` | `0xdbe65edc` |
| `getBinStep()` | `0x17f11ecc` |
| `getReserves()` | `0x0902f1ac` |
| `getTokenX()` | `0x05e8746d` |
| `getTokenY()` | `0xda10610c` |
| `balanceOf(address,uint256)` | `0x00fdd58e` |
| `getBin(uint24)` | `0x0abe9688` |

## Price Formula

```python
SHIFT = 2**23  # 8,388,608
price = (1 + bin_step / 10000) ** (bin_id - SHIFT) * 10**12
```

## Usage

```bash
# Read LFJ V2.2 position (Avalanche) — CORRECT invocation
python3 ${VAULT_DIR}/scripts/onchain-reader.py --wallet 0x7ebff188f2Eba16518C02864589b1403a5d1296a --dex lfj --chain avalanche --json
```

## On-Chain Range Verification Protocol (Jul 22, 2026)

**Jordan's rule:** "No wrong range. Check on chain data." The on-chain reader is the authoritative source.

**Steps:**
1. Run reader with `--dex lfj --chain avalanche --json`
2. Extract `activeBin` from the response
3. Compute range from bin IDs:
   ```python
   SHIFT = 2**23  # 8388608
   bin_step = 10  # 0.1%
   for bin_id in bin_ids:
       price = (1 + bin_step / 10000) ** (bin_id - SHIFT) * 10**12
   ```
4. The lowest bin_id → range_low, highest bin_id → range_high
5. Update config files with verified range

**Pitfall:** The LFJ UI shows 149 bins in the slider by default, but the actual deployed position may have far fewer (e.g. 21 bins). The UI shows the available range, not what's actually active. Always verify with on-chain data.

## Verified Working State (Jul 22, 2026)

The reader now works correctly. Tested against the live LFJ V2.2 pool:
- Active bin: 8362850
- Bins with liquidity: 21
- Computed range: $6.48 – $6.61
- Active price: $6.59

**All selectors confirmed working.**

## Pool Details

- **Pool:** LFJ V2.2 AVAX/USDC (binStep 10)
- **Address:** `0x864d4e5ee7318e97483db7eb0912e09f161516ea`
- **Wallet:** `0x7ebff188f2Eba16518C02864589b1403a5d1296a`
- **RPC:** `https://api.avax.network/ext/bc/C/rpc`
