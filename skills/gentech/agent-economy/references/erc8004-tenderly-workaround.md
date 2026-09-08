# ERC-8004 Contract Updates via Tenderly

## Problem

ERC-8004 Identity Registry contracts are often deployed as **UUPS proxies**. Block explorer UI (Etherscan, Snowtrace, BscScan) shows "no public Write functions" because the proxy hides the implementation's Write interface.

## Solution: Use Tenderly

Tenderly correctly handles proxy contracts and exposes Write functions.

### Steps

1. **Navigate to contract on Tenderly:**
   ```
   https://tenderly.co/contract/{network}/{contract_address}
   ```
   Example for Avalanche:
   ```
   https://tenderly.co/contract/avalanche/0x8004A169FB4a3325136EB29fA0ceB6D2e539a432
   ```

2. **Connect wallet**
   - Click "Connect Wallet" → MetaMask/other
   - Confirm network switch to the correct chain

3. **Find `setTokenURI` function**
   - Expand "Write Contract" section
   - Scroll to `setTokenURI(uint256 tokenId, string tokenURI)`
   - Click to expand

4. **Fill parameters:**
   ```
   tokenId: 1770
   tokenURI: https://raw.githubusercontent.com/{owner}/{repo}/main/{metadata-file}.json
   ```

5. **Sign transaction**
   - Click "Write"
   - Review gas (L2s are pennies, mainnet ETH is more)
   - Confirm in wallet

## Alternative: Direct Contract Call (Python)

If Tenderly is unavailable, use a transaction library that supports proxies:

```python
from web3 import Web3
from eth_account import Account

# Setup
w3 = Web3(Web3.HTTPProvider("https://api.avax.network/ext/bc/C/rpc"))
private_key = os.environ.get("PRIVATE_KEY")
account = Account.from_key(private_key)

# Contract ABI (only the function we need)
abi = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "tokenId", "type": "uint256"},
            {"internalType": "string", "name": "tokenURI", "type": "string"}
        ],
        "name": "setTokenURI",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# Contract instance
contract = w3.eth.contract(
    address="0x8004A169FB4a3325136EB29fA0ceB6D2e539a432",
    abi=abi
)

# Build transaction
txn = contract.functions.setTokenURI(
    1770,
    "https://raw.githubusercontent.com/ProtoJay4789/ProtoJay4789.github.io/main/gentech-avax-metadata.json"
).build_transaction({
    "from": account.address,
    "nonce": w3.eth.get_transaction_count(account.address),
    "gas": 100000,
    "gasPrice": w3.eth.gas_price
})

# Sign and send
signed = w3.eth.account.sign_transaction(txn, private_key)
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
print(f"Transaction sent: {tx_hash.hex()}")
```

## Verify Update

**After confirmation (30-60 seconds):**

```bash
# Check via AgentScan API
curl -s "https://agentscan.info/api/agents?search=GenTech" | python3 -m json.tool
```

Look for `updated_at` timestamp to change and `skills`/`domains` fields to populate.

## Networks

| Network | Tenderly URL | RPC |
|---------|--------------|-----|
| Avalanche | `tenderly.co/contract/avalanche/{address}` | `https://api.avax.network/ext/bc/C/rpc` |
| Base | `tenderly.co/contract/base/{address}` | `https://mainnet.base.org` |
| BNB Chain | `tenderly.co/contract/binance/{address}` | `https://bsc-dataseed.binance.org` |
| Ethereum | `tenderly.co/contract/ethereum/{address}` | `https://eth.llamarpc.com` |

## Contract Address

ERC-8004 Identity Registry (CREATE2, same on all 22 chains):
```
0x8004A169FB4a3325136EB29fA0ceB6D2e539a432
```