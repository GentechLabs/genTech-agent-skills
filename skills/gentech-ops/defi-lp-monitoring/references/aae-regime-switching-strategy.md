# AAE Regime-Switching Strategy — CURVE vs Bid-Ask

**Established:** 2026-07-19
**Author:** Jordan + Gentech

## Core Thesis

The market has two distinct regimes. Each demands a different liquidity shape. The Agentic Treasury should detect which regime we're in and switch automatically.

## Regimes

### Regime 1: Chop / No Direction (Default → CURVE)

- **When**: Between macro events, consolidation, priced-in anxiety, low volatility
- **Shape**: CURVE (wide distribution across range)
- **Behavior**: Set and forget. All bins earn as price oscillates within range.
- **Why**: No clear directional bias. Bid-ask would sit in the dead zone between edges and earn 0%.
- **Jordan**: "Markets are not dropping dropping fast right now, just chop. Cooling from the recent pump of the inflation numbers last week."
- **Status (Jul 19)**: ✅ Defines current chop environment

### Regime 2: Macro Event (Fed / CPI / NFP → Bid-Ask)

- **When**: 24h before Fed meetings, CPI/NFP releases, major economic data
- **Shape**: Bid-Ask (concentrated at two edges)
- **Behavior**: Price moves hard one direction → one edge catches it → peak efficiency
- **Why**: You know the direction of risk (usually risk-off for macro surprises). No point spreading liquidity across a range when 90% of the action is at one edge.
- **Jordan**: "Bid ask is perfect for fed meetings and macro data coming out 🧠 these will be Strategies for Agentic Treasury AAE yield fam"
- **Next event**: FOMC Jul 29-30 — switch to bid-ask by Jul 28 EOD

### Future: Trending Market

- Directional trend with momentum could use skewed CURVE or 100% spot
- Not yet implemented — waiting for a clear trend

## Automation Plan

1. Cron job checks macro calendar daily (fed-event-tracker.py already exists)
2. 24h before FOMC/CPI/NFP → auto-switch config to bid-ask at current macro-relevant range
3. 24h after event settles → auto-switch back to CURVE
4. Manual override always available (Jordan sets shape directly on LFJ)

## Vault Strategy Doc

Full spec: `/root/vaults/gentech/03-Strategies/aae-regime-switching.md`
