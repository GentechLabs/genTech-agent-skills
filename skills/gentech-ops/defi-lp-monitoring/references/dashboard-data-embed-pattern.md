# Dashboard Data Embed Pattern

## The Problem
The on-chain reader (`run-reader.py`) writes a clean `defi-data.json` every 10 minutes. It only writes the keys it knows about (hero, lpPosition, fees, etc.). Any extra keys added by the consolidated monitor (regime, strategyComparison, yieldSpectrum, narrativeRotation) are wiped.

## The Solution
The consolidated monitor (`defi-lp-consolidated.py`) runs 3 minutes after the reader. The `embed_dashboard_extras()` function:
1. Reads the freshly-written `defi-data.json`
2. Adds regime, strategy comparison, yield spectrum, and narrative rotation data
3. Writes it back

## Data Flow
```
:00 — run-reader.py writes clean defi-data.json
:03 — defi-lp-consolidated.py reads it → adds extras → writes back
:10 — run-reader.py overwrites again
:13 — defi-lp-consolidated.py re-embeds
... (every 10 minutes)
```

## Keys Added by embed_dashboard_extras()

### regime
```json
{
    "current": "volatile" | "sideways" | "bull_trend" | "bear_trend",
    "previous": "sideways",
    "changedAt": "2026-06-25T17:00:00Z",
    "signals": {
        "price": 6.19,
        "ma20": 6.07,
        "volume24h": 1200000,
        "volatility": "high" | "low"
    },
    "strategy": {
        "shape": "bid-ask" | "curve",
        "dcaAggressiveness": "aggressive" | "moderate" | "conservative",
        "rationale": "Price at 40% of range"
    },
    "recommended": "Stay BID-ASK — volatile regime"
}
```

### strategyComparison
```json
{
    "lpApr": 372.4,
    "lpDailyFees": 0.485,
    "stakingApr": 6.7,
    "stakingDaily": 0.009,
    "hodlReturn": -0.49,
    "entryPrice": 6.13,
    "currentPrice": 6.19,
    "outperforming": true,
    "verdict": "LP 372.4% APR vs Staking 6.7% — outperforming"
}
```

**⚠️ PITFALL:** The renderer destructures `lpApr`, `hodlReturn`, etc. It does NOT accept `bidAsk`/`curve`/`spot` keys. Writing those will cause `Cannot read properties of undefined (reading 'toFixed')`.

### yieldSpectrum
```json
{
    "currentBand": {"id": "accumulation", "name": "Accumulation", "emoji": "🟢", "color": "#22c55e", ...},
    "bands": [...],
    "position": {"currentPrice": 6.19, "rangeLow": 6.01, "rangeHigh": 6.25, ...},
    "metrics": {"efficiency": 47.9, "dailyFees": 0.485, "annualizedApr": 372.4, ...},
    "history": [45.2, 52.1, ...]
}
```

### narrativeRotation
```json
{
    "lastUpdated": "2026-06-23T19:42:53Z",
    "btc": {"price": 62258, "change_7d": -5.0},
    "narratives": [
        {"rank": 1, "name": "DeFi Blue Chips", "emoji": "🏦", "score": -10.4, "zone": "🔴 Cold", ...},
        ...
    ],
    "topNarratives": ["DeFi Blue Chips", "Gaming / Metaverse", ...]
}
```

## Verification

After any change to the embed function, run:
```python
python3 -c "
import json
with open('/root/ProtoJay4789.github.io/DeFi/defi-data.json') as f:
    d = json.load(f)
for k in ['regime', 'strategyComparison', 'yieldSpectrum', 'narrativeRotation']:
    print(f'{k}: {\"✅\" if k in d else \"❌\"} {list(d.get(k, {}).keys())[:3] if k in d else \"MISSING\"}')"
```

## Related Pitfalls
- Cron timing: reader must run BEFORE monitor (3-min offset)
- Renderer data shapes: always check `defi-dashboard.html` for expected keys
- Quiet hours: must not kill the embed (use `quiet_mode` flag, not `sys.exit`)
