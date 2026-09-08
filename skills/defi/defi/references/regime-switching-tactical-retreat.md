# Regime-Switching + Tactical Retreat — Quick Reference

## Two Regimes, Two Shapes

| Regime | Shape | When |
|--------|-------|------|
| Chop / No Direction | CURVE | Between macro events, F&G 25-40, consolidation |
| Macro Event (Fed/CPI/NFP) | Bid-Ask | 24h before → 24h after event |

## Tactical Retreat Loop

DEPLOY → EARNING → BREAKOUT → HOLD 2-5min → RETREAT to USDC → SENTINEL → RE-ENTER

### Sentinel Signals (3/4 = re-enter)
1. Fear & Greed > 35
2. 1h volume returning to 24h average
3. Price consolidating 2+ hours
4. Macro calendar clear 48+ hours

## Config-First Principle

**Never infer shape/entry/range from on-chain.** Always:
1. ASK user what they deployed
2. WRITE config from their answer
3. VERIFY reader matches config

## Key Numbers (Current as of Jul 19, 2026)

- Position: $24.42 (1.49 AVAX + $14.14 USDC)
- Range: $6.4039-$6.5463 (CURVE)
- Entry: $6.48 | Current: $6.48 | IL: 0%
- Est. daily fees: $0.055
- Next Fed: Jul 29-30 → switch to bid-ask Jul 28

## Files

- Full spec: `/root/repos/ProtoJay4789.github.io/DeFi/aae-tactical-retreat.md`
- Deploy UX: `/root/repos/ProtoJay4789.github.io/DeFi/aae-yield-farm-ux.md`
- Vault: `/root/vaults/gentech/03-Strategies/aae-regime-switching.md`
