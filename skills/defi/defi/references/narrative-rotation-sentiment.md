# Narrative Rotation + Sentiment — Quick Reference

Script: `/root/.hermes/profiles/gentech/scripts/narrative-rotation.py`
Cron: `7ec71332b97c` — Sundays 7:30 PM UTC, delivers to Strategies group
JSON output: `/root/ProtoJay4789.github.io/DeFi/rainbow/rotation-data.json`

## What It Does

Scans 6 crypto narratives (AI, RWA, DeFi, L1/L2, Meme, Gaming) and classifies:
1. **Momentum zone** — Hot/Warm/Cooling/Cold (based on 7d + 30d changes)
2. **Sentiment** — Bullish/Mild Bullish/Mild Bearish/Bearish (based on 24h + 7d + volume)
3. **Rainbow hint** — Maps sentiment to yield rainbow bands

## Sentiment Classification

```python
score = change_24h * 0.3 + change_7d * 0.5
# Volume amplifier: high vol confirms, low vol weakens
if vol_ratio > 15: score *= 1.3
elif vol_ratio < 3: score *= 0.7

# Score → Sentiment → Rainbow mapping
> 5    → 🟢 Bullish    → Peak Yield / Euphoria (watch for tops)
> 0    → 🔵 Mild Bullish → Harvest Mode (hold and compound)
> -5   → 🟡 Mild Bearish → Accumulation zone (DCA opportunity)
else   → 🔴 Bearish    → Bleeding Edge / Panic Farm (generational entry)
```

## Feeds Into

- **Routing Layer** — sentiment per narrative determines mode (harvest/accumulate/dry powder)
- **Yield Rainbow** — sentiment confirms rainbow zone classification
- **Training Data** — narrative sentiment logged with LP observations
- **Dashboard** — rotation-data.json powers the narrative tab

## Narratives Tracked

| Narrative | Coins | Emoji |
|-----------|-------|-------|
| AI & Data | FET, RENDER, TAO, AKT | 🤖 |
| RWA | ONDO, PLU, CPOOL | 🏠 |
| DeFi Blue Chips | UNI, AAVE, LINK, MKR | 🏦 |
| L1/L2 | SOL, AVAX, NEAR, ARB | ⛓️ |
| Meme/Community | DOGE, PEPE, WIF, BONK | 🐸 |
| Gaming/Metaverse | IMX, GALA, PYTH | 🎮 |

## Pitfall

- CMC API key required — stored in `/root/.hermes/scripts/cmc_config.json`
- CMC rate limits: batch in groups of 10, sleep 1s between batches
- Sentiment is relative, not absolute — all narratives can be bearish simultaneously (as seen Jun 23, 2026)
