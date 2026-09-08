# Smart Routing Layer — Quick Reference

Full spec: `Strategies/smart-routing-layer-spec.md`

## Four Modes

| Mode | Trigger | Action |
|------|---------|--------|
| 🟢 HARVEST | Rainbow 60-90%, sentiment bullish/neutral | Farm fees, compound |
| 🟡 ACCUMULATE | Rainbow 20-60%, sentiment bearish | Deploy dry powder, aggressive DCA |
| 🔴 DRY POWDER | Crash >10% in 5min, all narratives 🔴 | Pull to USDC, preserve capital |
| 🔵 SPOT | Bull confirmed (3+ signals) | Exit LP, hold spot |

## Decision Matrix (Rainbow × Sentiment)

```
                Bullish    Neutral    Bearish
Euphoria    → DRY_POWDER  DRY_POWDER  DRY_POWDER
Peak Yield  → HARVEST     HARVEST     HARVEST
Harvest     → HARVEST     HARVEST     ACCUMULATE
Accumulate  → HARVEST     ACCUMULATE  ACCUMULATE
Bleeding    → ACCUMULATE  ACCUMULATE  DRY_POWDER
Panic       → ACCUMULATE  DRY_POWDER  DRY_POWDER
```

## Override Rules (Always Fire)

- Price >10% in 5min → DRY POWDER
- Price >20% in 1hr → DRY POWDER + alert
- All narratives 🔴 → DRY POWDER
- Sentiment stabilizes + rainbow > Accumulation → ACCUMULATE
- 3+ bull signals → SPOT

## Integration Points

**Inputs:** Yield Rainbow, Narrative Sentiment, Shape Detection, Price Velocity, Volatility, Volume/MCap
**Outputs:** LP Monitor mode, Dashboard status, Telegram alerts, Training data

## User Modes

- **Autonomous:** Agent decides, executes, alerts after
- **Hybrid (default):** Agent recommends + executes with 60s override
- **Advisory:** Agent recommends, user executes

## Connection to Training Data

Every mode decision gets logged to `defi-training-data.json` with inputs and outcomes. This feeds the DeFi model that will eventually predict optimal mode switches.
