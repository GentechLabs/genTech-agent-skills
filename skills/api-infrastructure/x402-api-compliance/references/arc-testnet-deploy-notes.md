# Arc Testnet Deploy Notes (chain 5042002)

Deploying contracts to Arc (Circle's stablecoin-native L1) — from the
Programmable Money hackathon prep (Aug 2026).

## Chain facts
- RPC: `https://rpc.testnet.arc.network` (chainId `0x4cef52` = 5042002)
- Explorer: `https://testnet.arcscan.app` (API: `https://api.testnet.arcscan.app/api`)
- **USDC is the NATIVE GAS token** — `eth_getBalance` returns USDC, and USDC
  also exists as an ERC-20 at `0x3600000000000000000000000000000000000000`
  (18 decimals for gas balance; 6 decimals for the ERC-20 transfer amount)
- Faucet: `faucet.circle.com` (claims testnet USDC to a wallet address)
- Contract deploy gas limit check: 7,908-byte contract fine; 24,576 limit

## Foundry config
```toml
[profile.default]
src = "contracts"
out = "out"
libs = ["lib"]
optimizer = true
optimizer_runs = 200
evm_version = "cancun"   # REQUIRED — see below

[rpc_endpoints]
arc_testnet = "https://rpc.testnet.arc.network"
```

**`evm_version = "cancun"` is mandatory** if the contract imports
OpenZeppelin `ReentrancyGuardTransient` (or anything using `tstore`/`tload`).
Default `paris` fails with: `Error (6243): The "tstore" instruction is only
available for Cancun-compatible VMs`.

## Deploy flow that needs no server-side key
The deployer is the user's MetaMask wallet — the server never holds the key:
1. Build bytecode: `forge build` → `out/ArcAgentWallet.sol/ArcAgentWallet.json`
   → `bytecode.object` (~15.8K chars for a 7.9K-byte contract)
2. Host a static deploy page (`/var/www/gentechlabs/arc-deploy.html`) that:
   - connects MetaMask (`eth_requestAccounts`)
   - adds/switches to Arc testnet (`wallet_addEthereumChain` with
     `nativeCurrency: {name: "USDC", symbol: "USDC", decimals: 18}`)
   - `eth_estimateGas` + `eth_sendTransaction` with `{from, data: BYTECODE}`
   - polls `eth_getTransactionReceipt` → shows `contractAddress`
3. Verify deployer wallet first: nonce 0 (`eth_getTransactionCount` = `0x0`)
   and gas balance ≥ 20 USDC — a fresh wallet + USDC funding is a clean deploy

## Deployer-wallet hygiene
Use a DEDICATED test wallet for hackathon/testnet deploys, never the treasury
wallet (BlockRun, Q402 recipient, gateway payTo). Testnet-only value makes a
server-side key acceptable; keep mainnet keys out of the deploy path.
