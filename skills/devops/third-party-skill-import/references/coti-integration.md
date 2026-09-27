# COTI Privacy Blockchain Integration

## Overview
COTI provides 8 Hermes-compatible skills + 48+ MCP tools for privacy-preserving blockchain operations. Uses garbled circuits for encrypted balances, on-chain encrypted messaging, and private ERC20/ERC721 tokens.

## Repos
| Repo | Purpose | Status |
|------|---------|--------|
| `coti-io/coti-skills` | 8 SKILL.md files (framework-agnostic) | ✅ Cloned |
| `coti-io/coti-mcp` | MCP server (30+ tools: accounts, ERC20, ERC721, contracts, tx debugging) | ⚠️ Needs build |
| `coti-io/coti-agent-messaging` | MCP server (18 tools: encrypted messaging, rewards, starter grants) | ⚠️ Needs build |

## Skills Catalog
| Skill | Tools | Purpose |
|-------|-------|---------|
| coti-account-setup | 6 | Wallet creation, AES key generation, network config (MUST run first) |
| coti-starter-grant | 4 | One-time gas funding via challenge-response |
| coti-private-messaging | 6 | E2E encrypted on-chain messaging (24-byte chunks) |
| coti-rewards-management | 7 | Pull-based rewards, 14-day epochs |
| coti-private-erc20 | 8 | Garbled-circuit encrypted fungible tokens (max 6 decimals) |
| coti-private-nft | 11 | Privacy-preserving ERC721 |
| coti-smart-contracts | 5 | Custom Solidity with MpcCore primitives |
| coti-transaction-tools | 7 | Debugging, event decoding, sign/verify |

## Architecture
```
Account Setup → Starter Grant → Messaging/Tokens/Contracts → Transaction Debugging
     ↓                ↓                    ↓                        ↓
  Wallet + AES    Funded wallet      Private operations        Debug/verify
```

## Dependencies
- `@coti-io/coti-ethers` (ethers.js fork with COTI extensions)
- `@modelcontextprotocol/sdk` (MCP protocol)
- Node.js LTS + TypeScript

## Environment Variables
```env
PRIVATE_KEY=0x_your_private_key_here
AES_KEY=your_aes_key_here
CONTRACT_ADDRESS=0xc94189E22144500a66669E5bA1B42387DCc5Cd6a
COTI_NETWORK=testnet
```

## Build Status (Jun 14, 2026)
- `coti-agent-messaging`: npm install ✅, npm run build ✅ (monorepo, 4 workspaces)
- `coti-mcp`: npm install ✅, TypeScript build ❌ (interrupted, needs `npx tsc`)
- Skills: 8 SKILL.md files ready, not yet installed in Hermes

## Strategic Fit
- **Privacy layer** for GenTech stack (encrypted balances/transactions)
- **Agent-to-agent encrypted comms** (alternative to plain Telegram)
- **Hackathon angle** — private cookbook payments, encrypted recipe access
- **Pattern:** COTI solved privacy, we integrate and orchestrate
