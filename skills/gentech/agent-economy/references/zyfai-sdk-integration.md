# Zyfai SDK Integration Reference

## Overview
Zyfai SDK (`@zyfai/sdk` v0.2.37) — TypeScript SDK for yield optimization, Smart Wallet deployment, and ERC-8004 identity registration. Installed Jun 2026 at `/root/node_modules/@zyfai/sdk/`.

## Key Capabilities

### 1. ERC-8004 Identity Registration
```typescript
sdk.registerAgentOnIdentityRegistry(smartWallet, chainId)
```
- Supported chains: Base (8453), Arbitrum (42161)
- Requires: API key from https://sdk.zyf.ai/, connected account
- Flow: connectAccount → deploySafe → registerAgentOnIdentityRegistry

### 2. Smart Wallet (Safe) Deployment
```typescript
sdk.deploySafe(userAddress, chainId, strategy)
// strategy: "conservative" (default) or "aggressive"
```
- Deterministic addresses via CREATE2
- Backend handles RPC calls (avoids rate limiting)

### 3. Session Keys (Delegated Execution)
```typescript
sdk.createSessionKey(userAddress, chainId)
```
- Auto-checks for existing session keys
- Uses SIWE authentication

### 4. Vault API (Shared Pool)
```typescript
sdk.vaultDeposit("100", "USDC")  // Deposit
sdk.vaultWithdraw()              // Withdraw
sdk.vaultClaim(withdrawKey)      // Claim
```
- Currently USDC on Base only

### 5. Yield Optimization
- Auto-rebalancing across protocols
- Conservative vs aggressive strategies
- Position tracking and earnings history

## Supported Chains
| Chain | Chain ID | ERC-8004 | Smart Wallet | Vault |
|-------|----------|----------|--------------|-------|
| Base | 8453 | ✅ | ✅ | ✅ |
| Arbitrum | 42161 | ✅ | ✅ | ❌ |
| Plasma | 9745 | ❌ | ✅ | ❌ |

## API Key
- Get from: https://sdk.zyf.ai/
- Format: `zyfai_...` (SDK API key) or regular API key
- SDK API keys enable `addWalletToSdk()` method
- **Configured:** Saved to `/root/.hermes/profiles/gentech/.env` as `ZYFAI_API_KEY`

## Test Results (Jun 22, 2026)

### Smart Wallet Address (Read-only)
```javascript
const walletInfo = await sdk.getSmartWalletAddress(
    '0x7ebff188f2Eba16518C02864589b1403a5d1296a', 8453
);
// → address: 0x0F03566A33d1fF24C16E7a8D96db610D8773C67A
// → isDeployed: false (needs deployment via wallet signature)
```

### Yield Opportunities (Base, USDC)
**Conservative (17 opportunities):**
- Morpho - Moonwell Flagship USDC: 5.49% APY
- Fluid - USD Coin: 5.24% APY
- Fluid - USDC: 5.00% APY

**Aggressive (27 opportunities):**
- Harvest - USDC - 40 Acres: **14.92% APY**
- Euler - AlphaGrowth: 8.46% APY
- Morpho - Moonwell Flagship USDC: 5.49% APY

### Protocols on Base (9 total)
Aave V3, Compound V3, Euler, Fluid, Harvest, Morpho, Moonwell, Origin, Spark

### TVL
$5.5M total across Base

### Integration into x402 API
Added `/v1/yield/opportunities` endpoint (price: $0.001/query). Returns top 4 yield opportunities with protocol, pool, APY, and risk level.

## Integration with Agent Kit
- **Identity:** Use Zyfai for Base/Arbitrum registration, keep Avalanche for our existing ERC-8004
- **Wallets:** Deploy Safe wallets for agents needing yield optimization
- **Session Keys:** Use for delegated execution in Compound vs Extract
- **Vault:** Could use for shared pool deposits in future

## Installation
```bash
npm install @zyfai/sdk viem
```
Peer dependency: `viem` ^2.0.0

## Pitfalls
- Requires SIWE authentication (automatic via connectAccount)
- Vault currently only supports USDC on Base
- Withdrawals are processed asynchronously (txHash may not be immediate)
- `@rhinestone/module-sdk` is deprecated in favor of `@rhinestone/sdk`
- **Safe deployment requires wallet signature** — cannot be done server-side without private key
- **Avalanche not supported** — Zyfai only supports Base, Arbitrum, Plasma
- **Deploy via dashboard** — user connects wallet at https://sdk.zyf.ai/ and deploys Safe from there

## Next Steps
1. User deploys Safe via Zyfai dashboard (connects MetaMask, deploys on Base)
2. Register ERC-8004 identity on Base via `registerAgentOnIdentityRegistry()`
3. Fund Safe with USDC for yield optimization
4. Configure auto-rebalancing strategy
