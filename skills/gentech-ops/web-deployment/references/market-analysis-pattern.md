# Market Analysis Section Pattern for Data Dashboards

## Purpose
Every data dashboard (Yield Rainbow, Narrative Rotation, etc.) should include a dynamic analysis section that interprets the current data for the user. This turns a chart into a decision tool.

## Pattern: renderMarketAnalysis(data)

### Three States
The analysis function reads the current data and produces one of three states:

| State | Condition | Message |
|-------|-----------|---------|
| **Oversold** | `currentBand.position >= 5` | 🔴 Market is in panic/oversold territory. Contrarian accumulation zone. |
| **Neutral** | `currentBand.position >= 3 && currentBand.position <= 4` | 🟢 Balanced conditions. Hold and compound. |
| **Overbought** | `currentBand.position <= 2` | 🟡 Market is overheated. Take profits. |

### Three Outputs Per State

1. **marketStatus** — What's happening right now. Current price, current band name, historical context (e.g., "generational entries are made here").
2. **recoverySignal** — Concrete, measurable signals that indicate the trend is turning. For oversold: efficiency rising above threshold, band moving up, 24h change turning positive. For neutral: efficiency trend direction, macro factors. For overbought: efficiency dropping, band moving down.
3. **userAdvice** — Actionable portfolio guidance. For oversold: DCA in, widen LP range. For neutral: hold and compound, monitor trend. For overbought: take profits, move to stablecoins.

### Bear Market Timing Context
When in oversold territory, include the 4-year halving cycle context:
- Most analysts predict the bear market could bottom within 2-3 months
- The 4-year cycle may be on schedule or delayed by macro headwinds (rates, regulation)
- The rainbow bands help track where we are in the cycle regardless of timing
- Each band the marker climbs is a signal the cycle is turning

### Educational Footer
Include a "How the Rainbow Works" box that explains:
- The tool maps any coin's market position across 6 bands
- From Euphoria (overbought, top) to Panic Farm (oversold, bottom)
- Each band represents a different risk/reward regime
- The same tool works for any coin on any chain
- Use it to check if your favorite tokens are overvalued or undervalued

## Implementation

```javascript
function renderMarketAnalysis(data) {
    const { currentBand, position, metrics, bands } = data;
    
    const sortedBands = [...bands].sort((a, b) => a.rainbow_position - b.rainbow_position);
    const currentIdx = sortedBands.findIndex(b => b.id === currentBand.id);
    const bandAbove = currentIdx > 0 ? sortedBands[currentIdx - 1] : null;
    
    const isOversold = currentBand.position >= 5;
    const isOverbought = currentBand.position <= 2;
    
    let marketStatus, recoverySignal, userAdvice;
    
    if (isOversold) {
        marketStatus = `🔴 <strong>Oversold Territory</strong> — ...`;
        recoverySignal = `Most analysts predict the bear market could bottom within <strong>2-3 months</strong>...`;
        userAdvice = `For your portfolio: This is a <strong>contrarian accumulation zone</strong>...`;
    } else if (isOverbought) {
        marketStatus = `🟡 <strong>Overbought Territory</strong> — ...`;
        recoverySignal = `N/A — the market is already overheated...`;
        userAdvice = `For your portfolio: <strong>Take profits</strong>...`;
    } else {
        marketStatus = `🟢 <strong>Neutral Zone</strong> — ...`;
        recoverySignal = `The current trend could shift based on...`;
        userAdvice = `For your portfolio: <strong>Hold and compound</strong>...`;
    }
    
    return `<div class="treasury-card">...${marketStatus}...${recoverySignal}...${userAdvice}...</div>`;
}
```

## HTML Structure
The analysis section is a separate `<div id="market-analysis">` placed after the main chart container. It's populated by `analysis.innerHTML = renderMarketAnalysis(data)` in the `init()` function.

## Dry Powder Analysis (Narrative Rotation)
For pages that track market-wide conditions, add a dry powder section showing USDC + USDT market caps:

```javascript
async function fetchStablecoinData() {
    const res = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=usd-coin,tether&vs_currencies=usd&include_market_cap=true');
    const data = await res.json();
    const usdcCap = data['usd-coin'].usd_market_cap;
    const usdtCap = data['tether'].usd_market_cap;
    const combined = (usdcCap + usdtCap) / 1e9;
    // Interpret: >$180B = high dry powder, >$150B = moderate, >$120B = low
}
```

Interpretation:
- **> $180B combined** — High dry powder, capital waiting on sidelines, potential deployment incoming
- **$150-180B** — Moderate, normal market conditions
- **$120-150B** — Low, capital actively deployed in risk assets
- **< $120B** — Very low, capital fully deployed, market is risk-on
