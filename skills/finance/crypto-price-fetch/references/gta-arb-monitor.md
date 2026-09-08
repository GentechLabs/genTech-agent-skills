# GTA Arb Monitor Reference

## Detection Formula

\`\`\`
basis_bps = ((perp_price - spot_price) / spot_price) * 10000
\`\`\`

- **Positive** = CONTANGO (perp above spot — short perp, long spot)
- **Negative** = BACKWARDATION (perp below spot — long perp, short spot)

## API Connection — Hyperliquid

Hyperliquid uses a **POST-based JSON API** (not REST). All calls go to `https://api.hyperliquid.xyz/info`:

\`\`\`bash
curl -s "https://api.hyperliquid.xyz/info" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"type":"allMids"}' \
  --max-time 8
\`\`\`

**CRITICAL — Content-Type header:** Hyperliquid requires `Content-Type: application/json`. Without it, the API returns an empty response with no error message. This was discovered when migrating from the SDK (which auto-adds the header) to direct curl calls for timeout control.

**SDK timeout pitfall:** The Python SDK (`hyperliquid-python-sdk`) uses `requests.post()` with no default timeout — it can hang indefinitely. Always use direct `curl` with `--max-time 8` for cron jobs.

## Threshold Tuning

| Threshold | Use Case |
|-----------|----------|
| 5 bps | Default — catches meaningful arb without noise |
| 10 bps | High-conviction only — fewer alerts, larger spreads |
| 2 bps | Aggressive — catches tiny gaps, frequent alerts |

## Watchlist

Core 7: BTC, ETH, SOL, AVAX, LINK, ONDO, PAXG

- **PAXG added Jul 25, 2026** — gold-backed token from Paxos. Added in response to Iran/US geopolitical escalation. PAXG tracks the same gold price as XAUt (Tether Gold) but is the only gold token listed on Hyperliquid. Confirmed on Hyperliquid at $4,053.25.
- **ONDO** — confirmed as a tradable perp pair on Hyperliquid with good liquidity. $0.36-0.40 range during Jul 2026. RWA narrative (Ondo Finance + SBI Japan partnership broke Jul 24, 2026).

## Geo-Bypass

Hyperliquid's geo-block is at the **frontend** (app.hyperliquid.xyz), not the protocol. A VPS with non-US IP has full read-write access via API.

**Confirmed Jul 25, 2026:** VPS IP 2.24.195.196 — 232 assets, 939 mids, all unrestricted.

## USD Value Threshold

The arb is only profitable when the absolute spread (in USD) exceeds execution costs:

| Asset | Price | 5 bps | 10 bps | 15 bps |
|-------|-------|-------|--------|--------|
| BTC | $64K | $32.05 | $64.10 | $96.15 |
| ETH | $1.86K | $0.93 | $1.86 | $2.79 |
| SOL | $74 | $0.04 | $0.07 | $0.11 |
| AVAX | $6.35 | $0.003 | $0.006 | $0.095 |
| LINK | $8.37 | $0.004 | $0.008 | $0.013 |
| ONDO | $0.38 | $0.0002 | $0.0004 | $0.0006 |

## Proof of Value — Real-Time Market Catch

**Jul 25, 2026:** The arb monitor showed ONDO at +10.6 bps contango when Ondo Finance announced its SBI Group Japan partnership. The basis data was available *before* the news hit mainstream Twitter. This validates the product thesis: real-time spread data from a geo-blocked venue is valuable to traders who can't access it.

## Cron

```yaml
schedule: "0 * * * *"  # hourly (changed from */5 to 0 * on Jul 25)
no_agent: true
script: gta-arb-monitor.py
deliver: telegram:-1002916759037
```

- **Original cadence:** Every 5 min during proof-of-concept
- **Changed to hourly** once proven. Arb spreads move in single-digit bps over hours — sub-15min scans are unnecessary and generate noise.
- Silent when spreads < 5bps for all assets.

## Business Model

**Two-tier product** (conceived Jul 25, 2026):

1. **GTA Arb API** — raw data feed. Pay-per-call via x402 ($0.02/request). Returns perp, spot, basis_bps per asset. Target: US traders who can't access Hyperliquid directly. Similar model to Trump API (sold simple sentiment data; we sell executable spread data).

2. **Agentic Arbitrage** — managed execution. User deposits USDC → agent trades both legs (perp + spot) → auto-closes → sweeps profit. Non-custodial: user holds the private key, agent has trade-only access (can't withdraw).

**Flow:**
- User sends USDC (+ tiny ETH for gas) to a generated wallet
- Agent bridges into Hyperliquid
- Agent watches for 5+ bps arb opportunities
- Agent enters both legs (long perp / short spot or vice versa)
- Agent monitors every hour
- Agent closes when spread normalizes (<3bps)
- Agent auto-refuels gas (swaps USDC → ETH when low)
- Agent sends profit back to user's wallet

**Economic model:**
- User risk: spread widens against position (stop-loss at -50% of position)
- Agent cut: percentage of profit OR flat fee per trade
- Unit economics: $20 USDC + $0.50 ETH → gas costs <$0.01 per cycle
- Scalable: same agent handles N users with N independent wallets

**Competitive moat:**
- VPS is non-US — bypasses Hyperliquid geo-block naturally
- Agent monitors 24/7 — user can't watch markets continuously
- No VPN/subscription fees — VPS does it for free
- Multi-venue: if Hyperliquid goes down, plug into dYdX or another DEX
