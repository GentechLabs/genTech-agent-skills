# Arc Testnet Deploy Notes (chain 5042002) — MAINNET ADDENDUM 2026-09-16

## ✅ Arc MAINNET is live (verified on-chain 2026-09-16, launch day)
- Chain ID **5042** (`0x13b2`) — NOT 5042002 (that is testnet: `0x4cef52`)
- RPC `https://rpc.mainnet.arc.io` (verified: block 21,154,228, gasPrice ~58 Gwei)
- Explorer `https://explorer.arc.io` · docs `https://docs.arc.io/llms.txt`
- **USDC = native gas token**: 18-decimal native accounting, **6-decimal ERC-20
  interface at `0x3600000000000000000000000000000000000000`** (same address as testnet;
  `decimals()` re-verified = 6 on mainnet). One shared balance, no wrapper.
  → `ArcAgentWallet.sol`'s 6-decimal units are correct for mainnet unchanged.
- **`maxFeePerGas` floor 20 Gwei** — below it a tx hangs or fails outright
- EIP-7708: a system emitter `0xffff…fffe` logs EVERY USDC transfer → any log
  reader must de-duplicate against the token's own events
- `address(0)` sends REVERT (unlike standard EVM); blocklisted reverts burn gas
  with no receipt. Arc baseline is **Osaka** → `evm_version = "cancun"` still fine
- Local sim: vanilla `anvil` cannot reproduce Arc semantics — use Arc Foundry's
  `arc-anvil --network arc`
- CCTP V2 on Arc mainnet: **domain 26**, TokenMessengerV2
  `0x28b5a0e9C621a5BadaA536219b3a228C8168cf5d` (bytecode verified),
  MessageTransmitterV2 `0x81D40F21F12A8F0E3252Bccb954D722d4c464B64`,
  TokenMinterV2 `0xfd78EE919681417d192449715b2594ab58f5D002`
- Gateway (unified balance / nanopayments): GatewayWallet
  `0x77777777Dcc4d5A8B6E418Fd04D8997ef11000eE`, GatewayMinter
  `0x2222222d7164433c4C09b0b0D809a9b52C04C205`
- ⚠️ **Yield check before any deployment** (2026-09-16 council): Aave V4 + Morpho
  both printed **0.00%** USDC supply APY on Arc; Aerodrome Slipstream USDC depth
  $27.7K. Deploy triggers live in `steward-buylist-overrides.json` → `_arc_rail`.
  Minutes: `Treasury/Strategy-Journal/2026-09-16-council-arc.md`
- ⚠️ Circle's own `llms.txt` still says "Arc is currently available on Testnet
  only" — stale on launch day. Trust the chain (`eth_chainId`), not the page.

---

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
