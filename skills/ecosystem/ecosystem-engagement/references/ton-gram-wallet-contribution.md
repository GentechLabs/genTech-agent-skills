# TON Blockchain (Gram Wallet) — Contribution Pattern

**TON (The Open Network)** — 110 repos, 4.1k⭐ main monorepo, 70 contributors. Fully open source.
**Gram:** Toncoin token rebranded to Gram. Telegram rolling out native non-custodial Gram wallet to all 1B users this summer.

## Key Repos

| Repo | Stars | Language | Role |
|------|-------|----------|------|
| `ton-blockchain/ton` | 4.1k⭐ | C++ (93%) | Main monorepo — heavy, 2,423 commits |
| `ton-blockchain/wallet-contract` | 739⭐ | FunC/Shell | Wallet V4 smart contracts — **best target** |
| `ton-blockchain/ton-wallet` | 26⭐ | TypeScript | Web wallet (forked from MyTonWallet) |
| `ton-blockchain/docs` | 50⭐ | MDX | Developer docs — **easiest entry** (386 open issues) |

## Contribution Angle

### x402 Payment Plugin for Wallet Contract

The wallet contract already has a **subscription plugin** (periodic payments). We could add an x402 payment plugin that lets TON wallets receive x402 payments. This would make every Telegram wallet compatible with our gateway.

### Docs Contribution

386 open issues on the docs repo. Improve TON developer docs, especially around wallet integration and smart contract deployment.

## Ecosystem Significance

- 1B Telegram users getting a wallet this summer
- Zero-fee transactions
- Non-custodial (self-custody)
- Potential distribution channel for x402 — every Telegram user could pay for agent services
- We operate from Telegram — we'd be first to know when it ships