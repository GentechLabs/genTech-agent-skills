# Wallet Security Rules

## Core Rule
NEVER assume the agent controls a wallet. Always ask the user for their wallet addresses.

## What Happened (Jun 22, 2026)
Agent generated wallets during setup. User funded them from Coinbase thinking he owned them. Turns out the agent controlled the private keys — user had no access.

## Prevention
1. **Ask first** — always get wallet addresses from the user
2. **Verify ownership** — ask if they have the private keys
3. **Never generate wallets for the user** — unless explicitly requested and keys are saved securely
4. **Log addresses only** — never store private keys in session history or vault

## Jordan's Verified Wallets
| Chain | Address |
|-------|---------|
| EVM (Base + BNB + Avalanche) | `0x7ebff188f2Eba16518C02864589b1403a5d1296a` |
| Solana | `71Y3H36eb2WRGseYM9GwinjNawfMfAUbcof5eeWGoGSA` |

## Agent-Generated Wallets (ABANDONED)
| Chain | Address | Status |
|-------|---------|--------|
| Base/BNB | `0xebc8c71970EEb6973bd87F1FF146B3Ec4a5972f8` | BlockRun custodial — use balance, don't fund |
| Solana | `z7ww986T74koL9Cvnc31LFpwCP8ue1UupJX3KCAbB5Q` | Abandoned |
