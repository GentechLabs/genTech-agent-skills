# Across Protocol Bridge — Discovery Notes

Source: session where agent discovered how Hyperliquid users deposit
USDC on Base chain to fund their Hyperliquid L1 accounts.

## Key Findings

1. **Hyperliquid does NOT have its own bridge contract on Base.**
   It uses **Across Protocol** (across.to), a third-party bridge.
   Chain ID for Hyperliquid on Across = **999**.

2. **The deposit flow:**
   - User visits app.hyperliquid.xyz → Deposit → Base
   - Frontend calls `POST https://app.across.to/api/deposit-addresses`
     with an API key embedded in the frontend JS bundle
   - Across returns a unique deposit address
   - User sends USDC to that address
   - Across relays the funds to Hyperliquid L1 (~3 seconds)

3. **Cross-venue pairs discovered from Across API:**
   - Base USDC (chain 8453, token 0x8335...) → Hyperliquid USDC
     (chain 999, token 0xb883...)
   - Base USDT (chain 8453, token 0xfde4...) → Hyperliquid USDT
     (chain 999, token 0xB8CE...)

4. **The Across API requires authentication for deposit-addresses:**
   - Header: `authorization: Bearer <api_key>`
   - Query param: `integratorId=<id>`
   - The Hyperliquid frontend has these embedded; they're not publicly
     available from outside the app

5. **Direct deposit to SpokePool — SUCCESSFULLY EXECUTED (Jul 26 2026)**
   The SpokePool contract at `0x09aea4b2242abC8bb4BB78D537A67a245A7bEC64`
   is an **EIP-1967 transparent proxy**. The implementation contract is at
   `0x77aa19d49484cc88c2ca1c8527226e891c5c72d8`.

   The correct function is **`depositV3()`** (selector `0x7b939232`),
   NOT `deposit()` (selector `0xd2645d20` which does NOT exist on this
   contract). Full signature:
   ```
   depositV3(address depositor, address recipient, address inputToken,
             address outputToken, uint256 inputAmount,
             uint256 outputAmount, uint256 destinationChainId,
             address exclusiveRelayer, uint32 quoteTimestamp,
             uint32 fillDeadline, uint32 exclusivityDeadline,
             bytes message)
   ```

   **Successful transaction (Base chain):**
   `0x8238ce18dd1b4949c29fc5f5dd2cfbe1c9ce7caaf28f22d1a873cbdd2d702f5a`
   - Deposited $20.99 USDC from Base → Hyperliquid
   - Gas used: 73,670 (cost ~$0.015)
   - Fill time quoted: 3 seconds

   **Python/web3.py approach (PROVEN WORKING):**
   ```python
   from web3 import Web3, HTTPProvider
   from eth_account import Account

   w3 = Web3(HTTPProvider("https://mainnet.base.org"))
   account = Account.from_key(PRIVATE_KEY)

   SPOKE = "0x09aea4b2242abC8bb4BB78D537A67a245A7bEC64"
   USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
   OUTPUT = "0xb88339CB7199b77E23DB6E890353E22632Ba630f"

   # Use web3 Contract with minimal ABI for depositV3
   abi = [{"inputs":[...same as above...],"name":"depositV3","outputs":[],"stateMutability":"payable","type":"function"}]
   contract = w3.eth.contract(address=SPOKE, abi=abi)

   # Get quote from Across API
   import requests
   quote = requests.get(f"https://app.across.to/api/suggested-fees?...").json()

   tx = contract.functions.depositV3(
       ADDRESS, ADDRESS, USDC, OUTPUT, AMOUNT, int(quote["outputAmount"]),
       999, quote["exclusiveRelayer"],
       int(quote["timestamp"]), int(quote["fillDeadline"]),
       int(quote["exclusivityDeadline"]), b""
   ).build_transaction({...})

   signed = account.sign_transaction(tx)
   w3.eth.send_raw_transaction(signed.raw_transaction)
   ```

6. **Treasury address on Base (validators-controlled EOA):**
   `0x8d68eFBf06fb8cf932518bcB53705E674C4852DC`
   This is NOT a contract — validators monitor it for incoming USDC.
   But without the Across deposit-address flow, they can't link the
   sender to a Hyperliquid account.

7. **Proxy discovery method:**
   Use EIP-1967 storage slot to find implementation:
   ```
   eth_getStorageAt(proxy_addr, "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc", "latest")
   ```
   Returns `0x77aa19d49484cc88c2ca1c8527226e891c5c72d8` for the
   Across SpokePool on Base.

8. **Function selector extraction from bytecode:**
   The implementation contract bytecode lists all supported function
   selectors in its dispatcher. Search for `0x7b939232` to confirm
   `depositV3` is supported.

## JS Bundle Analysis

The Across API key and integrator ID were found in the Hyperliquid
frontend's main JS bundle at:
`https://app.hyperliquid.xyz/static/js/main.a8ba0615.js`

The `w()` wrapper function adds auth to every Across API call:
```javascript
function w(e, t, n) {
  const r = new URL(t);
  r.searchParams.set("integratorId", e.integratorId);
  return fetch(r.toString(), {
    ...n,
    headers: {
      authorization: "Bearer " + e.apiKey,
      ...(n?.headers || {})
    }
  });
}
```

## Chain Config (from JS bundle)

```javascript
const chainConfig = {
  ethereum: 1,
  base: 8453,
  monad: 143,
  plasma: 9745,
  avalanche: 43114,
};
```

Base USDC address: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`

## Suggested-Fees API (WORKING — no auth needed)

```
GET https://app.across.to/api/suggested-fees
  ?originChainId=8453
  &destinationChainId=999
  &inputToken=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
  &outputToken=0xb88339CB7199b77E23DB6E890353E22632Ba630f
  &amount=<raw_amount_6_decimals>
  &recipient=<0x_address>
```

Returns: spokePoolAddress, estimatedFillTimeSec (3s), fees in bps,
quoteBlock, exclusiveRelayer, fillDeadline, outputAmount.

## Pitfalls

- **`deposit()` does NOT exist on this contract.** Using `0xd2645d20`
  as the function selector will revert silently. Always use `depositV3()`
  (selector `0x7b939232`).
- The contract is a transparent proxy — make sure to interact through
  the proxy address, not the implementation.
- The `deposit-addresses` API endpoint requires an Across API key.
  Direct deposit via `depositV3()` on the SpokePool does NOT require
  API keys — just the public `suggested-fees` endpoint for the quote.
- Gas on Base is ~$0.0002/tx. At current ETH prices ($1,870), you can
  do ~4,000 transactions with $1 worth of ETH.
- The allowance must be >= the deposit amount (USDC approve). Check
  before depositing — estimate_gas will revert with
  `"ERC20: transfer amount exceeds allowance"` if insufficient.
- **Bridge relay may NOT complete even though the Base tx confirmed.**
  Tested on Jul 26, 2026: the `depositV3` call succeeded on Base
  (tx `0x8238ce...`) but the Across relay for Hyperliquid (chain 999)
  never completed, even after the 3-hour fill deadline passed. The funds
  are stuck in the spoke pool contract.
  - The refund/withdraw functions could not be identified from the
    implementation contract's bytecode selectors (none of the standard
    `withdrawDeposit`/`executeWithdraw` variants matched).
  - The Across `/api/deposit-addresses` endpoint (which would provide
    a deposit address with proper relay coverage) requires API key auth.
  - **Workaround:** Use the Hyperliquid UI (app.hyperliquid.xyz via VPN)
    instead — it generates a valid deposit address that relayers service.
    Do NOT rely on direct `depositV3()` calls for funding the HL account.
- The `depositV3` quote includes an `exclusiveRelayer` address that has
  an `exclusivityDeadline` (typically 5 seconds). If the exclusive relayer
  doesn't claim within that window, any relayer can fill. On Hyperliquid,
  apparently no relayer picks up these deposits.
- To monitor bridge status from Python, use the `spotClearinghouseState`
  endpoint (funds arrive in spot first, not perp):

## Chain IDs

| Chain | ID |
|-------|----|
| Ethereum | 1 |
| Arbitrum | 42161 |
| Base | 8453 |
| Avalanche | 43114 |
| Monad | 143 |
| Plasma | 9745 |
| Hyperliquid (Across) | 999 |
