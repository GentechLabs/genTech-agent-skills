# Solana Network Data Dashboard — Treasury Reference Source

**Source:** https://solana.com/data (Solana Foundation official dashboard, launched June 2026)
**Status:** ✅ Approved as reference source for treasury reads (Jordan, 2026-07-31). Saved to vault: `Treasury/solana-network-data.md`.

## What it is
Foundation-run dashboard aggregating **9 data providers** (Allium, Artemis, Birdeye, Blockworks, DeFiLlama, DexPaprika, Dune, Token Terminal, Top Ledger, Uniblock) under one shared schema. Values are the **median across providers for the latest available day** — no API key needed, web_extract works.

## Key metrics tracked
- **Transaction Count (Total)** — includes vote + non-vote
- **Non-Vote Tx (Success / Failed)** — real usage vs. spam/junk
- **SOL Price** — cross-provider median
- **Compute Units** — blockspace demand
- **Fees** — base + priority fees only (SOL)
- **Slots** — block production
- **Fee Payers** — unique wallets paying fees (proxy for new-wallet activity)

## Reading the signals (treasury playbook)
| Signal | Read |
|--------|------|
| Tx up + fees up | Strong real demand, fee competition healthy |
| Tx up + fees flat/down | Activity up but priority-fee pressure easing — healthier blockspace, less spam competition |
| Fee payers spiking | New wallets entering — growth signal |
| Failed non-vote tx climbing | Possible spam/botting/congestion — check |

## Reference snapshot (2026-07-31)
- Tx total: 299.4M (+1.1%)
- SOL: $74.3 median (CoinGecko live ~$73.6, -0.2% 24h)
- Compute units: 32.5M (+3.5%)
- Fees: 7.5K SOL (−3.1%)
- Fee payers: up to ~8M/day

Interpretation at snapshot: price flat while activity up; fees down 3.1% while tx up 1.1% → priority-fee pressure easing, not demand collapse.

## Related resources (from the same page)
- SDA (open source repo powering dashboard): github.com/solana-foundation/solana-data-aggregator
- RPC Latency Monitor: github.com/solana-foundation/rpc-latency-monitor
- Tx Sender Metrics (Grafana): rpclatency.grafana.net public dashboards
- Allium institutional data, Lightspeed dashboards, Dune, tokens.xyz
- CoinGecko live price check used alongside: `api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd&include_24hr_change=true`
