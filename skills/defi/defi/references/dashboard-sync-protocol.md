# Dashboard Sync Protocol (Full)

> Absorbed from `dashboard-sync` + `defi-dashboard-sync` skills. Complete sync workflow.

## One-Command Sync

```bash
python3 /root/.hermes/scripts/defi-dashboard-sync.py   --range 6.20-6.37   --balance 43.2   --avax 3.444   --usdc 21.51   --shape curve
```

**Status check:** `python3 defi-dashboard-sync.py --status`

## Files Updated (7 + 1 deployment config)

| # | File | Purpose |
|---|------|---------|
| 1 | `DeFi/defi-data.json` | Dashboard data source |
| 2 | `DeFi/defi-dashboard.html` | Dashboard renderer |
| 3 | `hub.html` | Hub embedded tab |
| 4 | `Strategies/scripts/.lfj-aae-config.json` | LFJ config |
| 5 | `Strategies/scripts/defi-master-cron.py` | Cron script |
| 6 | `HQ/config/defi-lp-config.env` | Env config |
| 7 | `DeFi/journal.md` | Trading journal |
| 8 | `.github/workflows/deploy-portfolio.yml` | Deployment config (CHECK ONLY) |

## Two-Repo Sync (Critical)

Dashboard reads from `ProtoJay4789/ProtoJay4789.github.io`, NOT `gentech-vault`.

```bash
cp /root/vaults/gentech/defi-data.json /root/ProtoJay4789.github.io/DeFi/defi-data.json
cd /root/ProtoJay4789.github.io && git add DeFi/defi-data.json && git commit -m "..." && git push
```

**Verify via GitHub API (bypasses CDN cache):**
```bash
curl -s "https://api.github.com/repos/ProtoJay4789/ProtoJay4789.github.io/contents/DeFi/defi-data.json" | python3 -c "
import sys, json, base64
d = json.load(sys.stdin)
content = base64.b64decode(d['content']).decode()
data = json.loads(content)
print('Keys:', sorted(data.keys()))
"
```

## defi-data.json Required Keys (ALL must exist)

| Key | Section |
|-----|---------|
| `hero` | Position overview |
| `marketIntel` | Price, volume, TVL, news |
| `strategyAdvisor` | Efficiency, DCA, risk |
| `lpPosition` | Protocol, pair, deposit, fees |
| `curveData` | Range, bins for chart |
| `feeMilestones` | Tier ladder + progress |
| `regime` | Market regime classification |
| `strategyComparison` | LP vs staking vs HODL |
| `rebalanceSuggestions` | Context-aware suggestions |
| `transactions` | Activity history |
| `spotPositions` | Watchlist + compound ops |
| `activityLog` | Verification history |
| `marketScenarios` | What-if scenario cards |
| `ilCalculator` | IL vs fee offset table |

## Renderer Field Contracts (MUST match exactly)

| Section | Correct Fields | Common Mistake |
|---------|---------------|----------------|
| `feeMilestones.tiers[]` | `{tier, label, icon, unlocks, target}` | Using `name` instead of `label` |
| `lpPosition.deposit` | `{avax, avaxValue, usdc, usdcValue}` | Using `avaxAmount` |
| `strategyAdvisor` | `{recommendedAction, dcaType, dcaDetails, riskLevel, riskNote}` | Using `recommendation` |
| `hero.efficiency` | number `64.4` | String `"64.4"` — crashes `.toFixed()` |
| `regime` (key name) | `regime` | `regimeData` — template mismatch |

## Curve Bin Generation

### Curve (Convergent)
```python
mid = (rangeLow + rangeHigh) / 2
for i in range(35):
    price = rangeLow + (rangeHigh - rangeLow) * (i / 34)
    depth = max(0.05, 1.0 - abs(price - mid) / ((rangeHigh - rangeLow) / 2) * 0.95)
```

### Bid-Ask (Bidirectional)
```python
for i in range(51):
    price = rangeLow + (rangeHigh - rangeLow) * (i / 50)
    distFromEdge = min(price - rangeLow, rangeHigh - price)
    depth = max(0.05, 1.0 - (distFromEdge / ((rangeHigh - rangeLow) / 2)) * 0.95)
```

### Spot
Single peak at current price, all other bins at minimum depth.

## Efficiency Calculation (Shape-Aware)

```python
def calc_efficiency(price, range_low, range_high, shape):
    if price < range_low or price > range_high:
        return 0.0
    pos = (price - range_low) / (range_high - range_low)
    if shape == "spot": return 100.0
    elif shape in ("bidirectional", "bid-ask"):
        return round(abs(pos - 0.5) * 2 * 100, 1)  # Edge-high
    else:  # curve
        return round((1 - abs(pos - 0.5) * 2) * 100, 1)  # Center-high
```

## AAE Brand Theme

| Element | Color | Hex |
|---------|-------|-----|
| USDC / Token A | Blue | `#3b82f6` |
| AVAX / Token B | Red | `#ef4444` |
| Active/Rewarded bin | Silver | `#c0c0c0` |
| Price line | White | `#ffffff` |
| Background | Dark | `#0f172a` |
| Text | Light gray | `#9ca3af` |

## Verification Protocol

1. Run `--status` to confirm values
2. Spot-check at least 2 different files
3. Confirm git push succeeded
4. Confirm GitHub Actions completed

## Live Data Fetching Pattern

**CRITICAL:** Load FULL static data first, then overlay live API data. Never "try live first, fall back to cached."

```javascript
// 1. Load full defi-data.json
const data = await fetch('defi-data.json?' + Date.now()).then(r => r.json());

// 2. Overlay live prices from DexScreener
const live = await fetchLiveData();
if (live) {
    if (live.hero) Object.assign(data.hero || {}, live.hero);
    if (live.marketIntel) Object.assign(data.marketIntel || {}, live.marketIntel);
}
```

## Pitfalls

1. **Dashboard HTML hardcoded values cause flicker** — Update fetchLiveData() after EVERY rebalance
2. **Hub vs Dashboard use different data sources** — Both have hardcoded ranges
3. **GitHub Pages CDN caching** — 5+ min delay after push
4. **Git push failure = stale dashboard** — Check for detached HEAD
5. **Template dataSource key vs JSON key** — Must match character-for-character
6. **On-chain reader writes to wrong path** — Must write to `DeFi/defi-data.json`, not root
7. **Pair name must be "AVAX/USDC"** — Not "AVAX/USD"
8. **DexScreener must only overlay price/volume/tvl** — Never range or position data
