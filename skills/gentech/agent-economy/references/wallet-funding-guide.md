# Wallet Funding Guide

## Multi-Chain Wallet Strategy

GenTech operates across multiple chains. Same EVM address works on all EVM chains (just switch network in MetaMask). Solana uses a different address.

### Wallet Addresses

| Chain | Address | Current Balance |
|-------|---------|----------------|
| Base/BNB/Avax (EVM) | `0xebc8c71970EEb6973bd87F1FF146B3Ec4a5972f8` | Check with script |
| Solana | `z7ww986T74koL9Cvnc31LFpwCP8ue1UupJX3KCAbB5Q` | Check with script |

### Funding Requirements

| Chain | Min Amount | Why | Lasts |
|-------|-----------|-----|-------|
| Base (ETH) | $2-5 | ERC-8004, x402, Agent Kit | 6-12 months |
| Solana (SOL) | $5-10 | Boot camp, staking, x402 | Years |
| BNB (BNB) | $3-5 | 140K agents, largest ecosystem | Years |
| Avalanche (AVAX) | $5-10 | x402 Challenge ($100K) | Years |

### Common User Questions

**"Do I need to keep funding these wallets?"**
No. L2 gas is fractions of a penny per transaction. $5 of ETH on Base lasts 6-12 months of regular use. $5 of SOL lasts years.

**"How do I check my balances?"**
Run the wallet balance check script, or use the Agentscan API.

### Balance Check Script

Located at: `scripts/wallet-balance-check.py`

Checks ETH (Base) and SOL balances. Alerts if below threshold.

```bash
python3 scripts/wallet-balance-check.py
```

### RPC Providers for Base

- `https://mainnet.base.org` — official, rate-limits VPS requests
- `https://base.publicnode.com` — works from VPS ✅
- `https://base.meowrpc.com` — works from VPS ✅
- `https://base.llamarpc.com` — rate-limits (521 error)

**Pitfall:** The official Base RPC (`mainnet.base.org`) blocks direct requests from VPS environments. Always use a fallback RPC for scripts.
