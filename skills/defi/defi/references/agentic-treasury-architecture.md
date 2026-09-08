# Agentic Treasury — Yield Farm Command Center

## Vision
A unified dashboard + alert system that tracks every DeFi position across protocols and chains in one place. Same pattern as the LP monitor, but scaled.

**Core thesis:** ARC as home base. Everything in USDC — gas, LP deposits, fees, rebalances. One currency, one pool of capital, the AI agent handles all the chain math.

## ARC Home Base — Single-Currency Operations

The fundamental insight: **gas tokens are friction**. Every chain has its own native token for fees (AVAX, SOL, ETH, BNB). Every time you want to move capital, you need to swap into the right gas token first. That's mental overhead and failed transactions.

**ARC fixes this:**
- Deposit USDC once → that's your gas budget, LP capital, and fee pool
- ARC bridges to Avalanche, Solana, Base, wherever the yield is
- No token swapping for fees — the single biggest UX friction in DeFi, eliminated
- The AI agent calculates everything: "To deploy $X into this pool, we need $Y for the position and $Z for gas, all in USDC"

**The agent's job:**
1. Know your total USDC pool across all chains
2. Before any deployment, calculate exact amounts: position size + gas + buffer
3. Simulate the transaction on-chain before you sign
4. Execute with the corrected parameters
5. Report: "Deployed $X into LFJ AVAX/USDC. Gas cost: $0.02. Remaining USDC: $W."

## Architecture

### 1. Unified Config (`agentic-treasury.json`)
Single source of truth for all positions. Each entry has:
- Protocol, chain, pool/contract address
- Shape (for LP), strategy label
- Entry price / APY target
- Alert thresholds

### 2. On-Chain Readers (one per protocol)
| Protocol | Status | What it reads |
|----------|--------|---------------|
| LFJ V2.2 | ✅ Done | Range, bins, active price, balances |
| Uniswap V3 | 📝 Template | NFT manager → tick range, liquidity |
| Aave / Morpho | 📝 Planned | supply balance, APY, borrow rate |
| Balancer | 📝 Planned | pool ID, weights, LP value |
| Meteora DLMM | 📝 Planned | bin range, active bin, balances (Solana) |
| Raydium CLMM | 📝 Planned | tick range, position NFT (Solana) |

### 3. LP Monitor (existing, proven)
- Reads config → fetches live data → calculates efficiency, IL, fees
- Debounce rules: 2x/hour normal, immediate on out-of-range or low efficiency
- Quiet hours: 11 PM – 6 AM ET

### 4. Command Center Dashboard
- GitHub Pages frontend (same pattern as existing hub)
- One card per position: range, efficiency, APY, IL, next action
- Cron updates data every cycle

### 5. Alerts (same debounce pattern)
- Out of range → immediate
- APY drops below target → alert
- Compound ready → notification
- DCA day → notification

## Chain Landscape

| Chain | TVL | Top Protocols | USDC Native? | Notes |
|-------|-----|---------------|-------------|-------|
| **Base** | $4.68B | Aerodrome ($327M TVL), Morpho ($3.1B), Aave, Uniswap | ✅ Yes | Aerodrome is the LFJ equivalent — concentrated liquidity, 65%+ of Base DEX volume |
| **Avalanche** | $436M | LFJ, Aave, Benqi, GMX | ✅ CCTP | Where we are now. Smaller but stable |
| **Solana** | ~$7B | Meteora, Raydium, Orca, Jupiter | ✅ CCTP | Meteora DLMM is the LFJ equivalent |
| **ARC** | Testnet | None yet | ✅ Native | Future home base. Circle's L1, USDC as gas token. Goldman Sachs, Mastercard, Visa building on it. |

## The Multi-Chain Flow with ARC

1. **Deposit USDC on ARC** — one pool of capital
2. **CCTP bridge to Avalanche** → deploy on LFJ (what we're doing now)
3. **CCTP bridge to Base** → deploy on Aerodrome
4. **CCTP bridge to Solana** → deploy on Meteora DLMM
5. **Agent calculates everything** — "Bridging $100 USDC to Base costs $0.02 in gas. Deploying into AERO/USDC pool needs $X. Remaining: $Y."
6. **All in USDC** — no gas token swaps, no failed transactions from wrong gas

## The Shape Decision Framework

| Shape | When | Why |
|-------|------|-----|
| **Curve** | **Default — always** | Starts at peak efficiency, degrades gracefully. Best for chop, ranging, and mild trends. |
| **Spot** | Rare — only in confirmed directional moves | Peak efficiency but narrow. Falls off a cliff if price moves wrong. |
| **Bid-Ask** | Macro events (Fed, CPI, NFP) | Captures volatility on both sides. |

**Curve is the default. Always.** Spot is overrated — people recommend it for bull runs, but bull runs are rare. 90% of the time we're in chop or mild trends, and Curve is simply better for that.

## The Regime Switch — From Command Center to War Room

Two modes:

1. **Accumulation Mode (default)** — Curve, farm fees, compound, DCA. The command center tracks everything, alerts on issues, but we're not betting directionally.

2. **Bull Mode (triggered)** — Buy and hold the asset. Stop farming fees and start accumulating the token itself. The command center becomes a war room — tracking entries, exits, position sizing.

**The trigger question** — when do we switch? Signals to watch:
- CLARITY Act passes → structural green light
- Tariff pivot → macro headwind removed
- BTC breaks and holds above a key level
- Global regulatory race accelerates (Russia Sep 1, Japan expanding, etc.)

When enough of those line up, flip the switch. Until then, Curve is the right call.

## Command Center Dashboard Pattern

The Yield Farm Command Center (`command-center.html`) is the reference implementation for the Agentic Treasury UI. It follows a specific architecture:

### Layout Architecture
- **Stack Status Bar** — 8-layer AAE bar at top, active layers highlighted (L1 Identity, L4 Commerce, L7 Intelligence)
- **2-Column Command Grid** — Agent Fleet + Treasury Overview side by side
- **Full-Width Metrics** — 8 metric cards in 4-column grid (efficiency, APR, daily/weekly fees, volume, TVL, 24h change, price)
- **LP Curve + Rainbow Panel** — Side-by-side visualization linking Layer 4 (Commerce) and Layer 7 (Intelligence)
- **Agent Identity** — ERC-8004 protocol info
- **Activity Log** — Timestamped agent actions with scroll
- **Human-Agent Collaboration** — Three-mode UX section at bottom

### LP Curve Canvas Visualization
The LP curve is drawn on an HTML5 Canvas element showing concentrated liquidity shape:
- **Curve shape:** High plateau inside the LP range, exponential drop-off outside
- **Range markers:** Dashed vertical lines at rangeLow and rangeHigh with price labels
- **Current price marker:** Red vertical line with dot, "OUT OF RANGE" / "IN RANGE" badge
- **Gradient fill:** Cyan-to-blue gradient under the curve
- **Responsive:** Redraws on window resize via event listener

```javascript
// Core curve math — concentrated liquidity shape
function drawLpCurve(data) {
    const { position } = data;
    const rangeLow = position.rangeLow;
    const rangeHigh = position.rangeHigh;
    const currentPrice = position.currentPrice;
    
    // For each point along the x-axis:
    for (let i = 0; i <= steps; i++) {
        const price = minX + t * (maxX - minX);
        
        // Inside range: full liquidity (yRatio = 1.0)
        // Outside range: exponential drop (yRatio = exp(-dist * 6))
        if (price >= rangeLow && price <= rangeHigh) {
            yRatio = 1.0;
        } else if (price < rangeLow) {
            yRatio = Math.exp(-(rangeLow - price) / rangeWidth * 6);
        } else {
            yRatio = Math.exp(-(price - rangeHigh) / rangeWidth * 6);
        }
    }
}
```

### Canvas Rendering — Critical Fixes

The LP curve canvas had persistent rendering issues. Here are the fixes that worked:

**1. Explicit canvas dimensions + inline styles:**
```html
<canvas id="lp-curve" width="400" height="200" style="width:100%;height:100%;display:block;"></canvas>
```

**2. Use `clientWidth`/`clientHeight` instead of `getBoundingClientRect()`:**
```javascript
const parent = canvas.parentElement;
let w = parent.clientWidth || 400;
let h = parent.clientHeight || 200;
if (w < 10) w = 400;  // fallback if layout not settled
if (h < 10) h = 200;
```

**3. Wrap draw call in `setTimeout(100ms)` after data fetch:**
```javascript
setTimeout(() => drawLpCurve(data), 100);
```
`requestAnimationFrame` double-nesting did NOT reliably work. `setTimeout(100)` was the only consistent fix.

**4. Fallback data when live fetch fails:**
The `catch` block should draw a sample curve with hardcoded data rather than showing an error state. Include all 6 rainbow bands, position data, and pool metadata in the fallback object so the entire page renders even offline.

**5. Debug element for troubleshooting:**
```html
<div id="lp-debug" style="font-size:0.65em;color:var(--dim);margin-top:6px;text-align:center;">LP curve loading...</div>
```
Update on render: `debug.textContent = '✅ LP curve rendered at $' + price;`

### Fee Scaling for Demo Positions
When showing a demo position (e.g., $1,000 instead of real $24.32), scale fees proportionally:
```javascript
const scaleFactor = 1000 / Math.max(realPositionUsd, 0.01);
const scaledDaily = realDailyFees * scaleFactor;
const scaledWeekly = realWeeklyFees * scaleFactor;
```

### Demo Site Card Pattern
Each subdomain dashboard gets a card on the demo site (`demo.html`) with:
- Icon, status badge (● LIVE), title, description, and "→ Live Dashboard" link
- Cards are grouped under section titles (e.g., "📊 DeFi Intelligence", "🤖 Agent Infrastructure")
- The GenTech Trading Agent (GTA) card explicitly spells out the name with abbreviation: "GenTech Trading Agent (GTA)" to avoid confusion with Grand Theft Auto

### Human-Agent Collaboration Modes
The Command Center supports three interaction modes, displayed as a 3-column card grid at the bottom:

| Mode | Badge | Behavior | Tags |
|------|-------|----------|------|
| **Autonomous** | 🤖 Set & Forget | Agent manages everything — monitoring, compounding, rebalancing, strategy. User gets weekly summary. | Full automation, Weekly reports, Hands-off |
| **Assisted** | 🧑‍💻 You & The Agent | Agent suggests actions ("Efficiency dropped below 30%, recommend widening range"), user approves or adjusts. | Agent suggests, You approve, Learn as you go |
| **Manual** | 🎮 Full Control | Agent monitors and alerts — user makes every move. Agent is analyst, not manager. | You decide, Agent alerts, Full transparency |

**UX copy pattern:** "Different personalities, different strategies — same Command Center. You choose how deep the agent goes."

### Key CSS Patterns
- Panel hover: `border-color` transition to blue accent
- Metric card hover: `translateY(-1px)` lift + border highlight
- Agent dot pulse animation for active agents
- Custom scrollbar styling for activity log
- Responsive breakpoints: 900px (collapse LP+Rainbow), 768px (single column), 1024px (expanded)

## Next Steps
1. Build the unified config file
2. Add Aave/Morpho reader
3. Wire into the existing LP monitor cron
4. Build the dashboard frontend
5. Research Aerodrome pool contracts for Base deployment
6. Research Meteora DLMM for Solana deployment
