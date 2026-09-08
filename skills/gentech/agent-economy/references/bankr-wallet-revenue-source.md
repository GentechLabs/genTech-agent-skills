# Bankr Wallet as a Revenue-Monitor Source (Aug 2026)

Extends §8c "Bankr Integration" with how to track Bankr income in the Revenue Monitor.

## Key fact: Bankr wallet ≠ x402 MetaMask wallet
Bankr (bankr.bot) **auto-provisions its own EVM + Solana wallets** the moment an API key is created. It does NOT reuse the user's MetaMask. So a Bankr key creates a SEPARATE balance channel from our x402 gateway wallet.

- **x402 gateway wallet** (Jordan's MetaMask): `0x7ebff188f2Eba16518C02864589b1403a5d1296a` — where gateway payments land; tracked via on-chain USDC RPC scan (Base/AVAX/BNB/Solana).
- **Bankr wallet** (auto-provisioned by the key): e.g. EVM `0x99ae...aebc` + Solana `6mcf...` — tracked via the Bankr REST API.

Track them **side-by-side as distinct channels**. Do NOT conflate them. The Bankr channel only matters as income if funds flow *through* Bankr.

## The Bankr API (wallet portfolio)
- Base URL: `https://api.bankr.bot`
- Auth: `Authorization: Bearer bk_usr_...` (keys start `bk_` / `bk_usr_`)
- Key stored in profile `.env` as `BANKR_API_KEY` (NOT hardcoded in scripts)
- Endpoint: `GET /wallet/portfolio`
  - Returns `{ success, evmAddress, solAddress, balances: { <chain>: { nativeBalance, nativeUsd, tokenBalances, total } } }`
  - Sum `total` per chain for a portfolio USD figure.

## Wiring pattern into revenue-monitor.py
1. `get_bankr_balances()` — reads `BANKR_API_KEY` from env, curls `/wallet/portfolio`, returns `{evm, sol, balances}` or `{"error": ...}`.
2. Called in `run()`, added to the result dict as `"bankr"`.
3. In `format_report`, a `🏦 Bankr Wallet` block shows EVM/SOL addresses + summed portfolio USD across chains; handles `None` (no key) and error cases.

## Pitfalls
- **Key may already exist** — before asking Jordan to mint a new one, grep for `bk_...` / `BANKR_API_KEY` across the whole profile: `.env`, `config.yaml`, `secrets/`, `.bashrc`, `.config`. Search the full profile, not one file.
- **Key creation provisions a wallet as a side effect** — the wallet appears (at $0) immediately. Expected, not an error.
- **Test before claiming done** — run `set -a && . <profile>/.env && set +a && python3 revenue-monitor.py` and confirm the Bankr block renders addresses + balance.

## Verification
```bash
cd /root/.hermes/profiles/gentech/scripts && set -a && . /root/.hermes/profiles/gentech/.env && set +a && timeout 90 python3 revenue-monitor.py | grep -A5 "Bankr Wallet"
```
