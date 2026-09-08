# Dashboard Integration Pattern

How data flows from cron scripts to the main DeFi dashboard on GitHub Pages.

## Architecture

```
defi-lp-consolidated.py (cron, every 10 min)
  → writes defi-data.json (position + fees + efficiency)
  → writes yield-rainbow-data.json (rainbow zone data)
  → embeds yieldSpectrum into defi-data.json (for main dashboard)
  → writes to BOTH paths (scripts dir + GitHub Pages)

defi-dashboard.html (GitHub Pages)
  → loads defi-template.json (section config)
  → loads defi-data.json (all data)
  → renders sections via customRender functions
  → auto-refreshes every 60 seconds
```

## Adding a New Dashboard Section

1. Add renderer in defi-dashboard.html
2. Register in customRender switch (around line 820)
3. Add section to defi-template.json
4. Write data to defi-data.json from cron
5. Push to GitHub Pages

## Current Sections (Jun 25, 2026)

1. Hero Efficiency (heroEfficiency → hero)
2. Autonomous Regime (regimeDetector → regimeDetector)
3. Performance vs Alternatives (strategyComparison → shapeComparison)
4. Yield Rainbow Spectrum (yieldSpectrum → yieldSpectrum)
5. AVAX Market Intel (marketIntel → marketIntel)
6. Support and Resistance (supportResistance → supportResistance)
7. Strategy Advisor (strategyAdvisor → strategyAdvisor)
8. Liquidity Distribution (lpCurve → curveData)
9. Fee Milestones (feeMilestones → feeMilestones)
10. Trajectory (trajectory → feeMilestones)
11. Spot Positions (spotPositions → spotPositions)
12. Activity Log (activityLog → activityLog)
13. Position Details (default → lpPosition)
14. Rebalance Suggestions (rebalanceSuggestions → rebalanceSuggestions)
15. Recent Activity (default → transactions)
16. Market Scenarios (marketScenarios → marketScenarios)
17. IL Calculator (ilCalculator → ilCalculator)

## Data Embedding Pattern

The consolidated monitor embeds rainbow data into defi-data.json via embed_rainbow_in_dashboard(). This function reads defi-data.json, adds the yieldSpectrum key with currentBand/bands/position/metrics/history, and writes it back.

## Pitfalls

- Template must be committed alongside HTML renderer changes
- dataSource in template must match the key in defi-data.json
- GitHub Pages caching: add ?v=timestamp to raw URLs
- DexScreener overlay: dashboard fetches live price and overlays on stored data
