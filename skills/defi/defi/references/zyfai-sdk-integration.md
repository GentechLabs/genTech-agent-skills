# Zyfai SDK Integration

## What is Zyfai?

Zyfai is a yield optimization platform with an SDK for deploying Safe smart wallets, managing DeFi positions, and optimizing yield across multiple protocols. Supports Base (8453), Arbitrum (42161), and Plasma (9745).

## Installation

```bash
npm install @zyfai/sdk viem
```

## API Key

Get from https://sdk.zyfai/ — free tier available.

```typescript
import { ZyfaiSDK } from "@zyfai/sdk";
const sdk = new ZyfaiSDK("zyfai_your_key_here");
```

## Key Features

### Smart Wallet Deployment
```typescript
const walletInfo = await sdk.getSmartWalletAddress(userAddress, 8453);
// → { address: "0x...", isDeployed: false }

const result = await sdk.deploySafe(userAddress, 8453, "conservative");
// → { success: true, safeAddress: "0x...", txHash: "0x..." }
```

### Yield Opportunities
```typescript
const opps = await sdk.getConservativeOpportunities(8453, "USDC");
// → [{ protocolName: "Morpho", poolName: "Moonwell", apy: 5.49, ... }]

const aggressive = await sdk.getAggressiveOpportunities(8453, "USDC");
// → [{ protocolName: "Harvest", poolName: "40 Acres", apy: 14.92, ... }]
```

### ERC-8004 Registration
```typescript
await sdk.connectAccount(privateKey, 8453);
const result = await sdk.registerAgentOnIdentityRegistry(smartWalletAddress, 8453);
// → { txHash: "0x...", ... }
```

### Session Keys
```typescript
const session = await sdk.createSessionKey(userAddress, 8453);
// → { alreadyActive: false, sessionKeyAddress: "0x...", ... }
```

### TVL & Volume
```typescript
const tvl = await sdk.getTVL();          // → { totalTvl: 5507293.02 }
const volume = await sdk.getVolume();    // → { volumeInUSD: ... }
```

## Supported Chains

| Chain | ID | Status |
|-------|-----|--------|
| Base | 8453 | ✅ |
| Arbitrum | 42161 | ✅ |
| Plasma | 9745 | ✅ |
| Avalanche | 43114 | ❌ Not supported |
| Solana | — | ❌ Not supported |

## Integration with GenTech Stack

Zyfai fills the **yield optimization** layer that our Agent Kit lacks:

- **Smart Wallets** → agents get their own Safe wallets on Base/Arbitrum
- **Yield Optimization** → automated rebalancing across protocols
- **Session Keys** → delegated execution without exposing private keys
- **ERC-8004** → native agent identity on Base/Arbitrum

### API Server Integration

We added a yield endpoint to our x402 API server:

```
GET /v1/yield/opportunities?chain=8453&asset=USDC&strategy=aggressive
→ Returns top yield opportunities via Zyfai SDK
→ Price: $0.001 USDC via x402
```

## Pitfalls

- **No Avalanche support:** Zyfai only supports Base, Arbitrum, Plasma. Our ERC-8004 is on Avalanche — can't use Zyfai for that chain.
- **Private key required for deployment:** Safe wallet deployment and ERC-8004 registration require signing with a private key. Can't be done from a server without the key.
- **API key format:** Keys start with `zyfai_` — different from regular API keys.

## Verified

- SDK installed and tested (v0.2.37)
- API key configured
- Smart wallet address pre-computed: `0x0F03566A33d1fF24C16E7a8D96db610D8773C67A`
- Yield data flowing through our API (10 endpoints)
