---
name: defi-lp-strategy-designer
description: "Design systematic DeFi strategy rules — LP exit/entry signals, multi-strategy portfolio rotation (LP ↔ Staking ↔ HODL ↔ Farming), regime detection, resistance ladders, shape selection, position sizing, and trainable learning layers. For concentrated liquidity on DEXes like LFJ, Uniswap V3, Camelot, and hybrid portfolio management."
version: 1.1.0
author: Gentech
tags: [defi, lp, strategy, portfolio, rotation, avalanche, lfj, market-making, staking, yield]
trigger: "When the user wants to design, document, or refine DeFi strategy rules — LP exit/entry signals, multi-strategy rotation between LP/Staking/HODL/Farming based on market regime, resistance ladders, shape selection, position sizing, hybrid portfolio allocation, or trainable learning layers where agents learn user trading patterns."
---

# DeFi LP Strategy Designer

Design systematic, documented strategy rules for concentrated liquidity positions. Covers the full lifecycle: when to LP, when to exit, when to re-enter, and how to size positions during transitions.

## When to Use

- Designing bull/bear market LP exit or entry strategies
- Creating resistance ladder rules for scaling out of LP
- Deciding which LFJ shape (curve/bid-ask/spot) fits a market regime
- Building systematic signals for when to transition between LP and spot
- Documenting strategy rules in vault files (LP-Monitor-Rules.md, etc.)
- Refining existing strategy rules based on new market thesis
- **Designing multi-strategy rotation** between LP, Staking, HODL, and Yield Farming
- **Building hybrid portfolio allocation** models with weighted strategy buckets
- **Creating trainable learning layers** where agents observe user trading patterns and learn to trade like them
- **Defining market regime classifiers** that detect volatility, trend, and volume states

## Core Concepts

### LP Shape Selection by Market Regime

| Regime | Best Shape | Why |
|--------|-----------|-----|
| **Choppy / ranging** | Curve | Balanced, earns fees in both directions |
| **High volatility, no direction** | Bid-Ask | Heavy at edges, harvests bounces |
| **Strong bullish breakout** | Exit LP → hold spot | IL destroys LP returns in trending markets |
| **Crash / panic dump** | Skewed curve (70% stablecoin) | Buys the dip, minimizes IL |
| **Consolidation after rally** | Curve at new range | Price stable, LP earns cleanly |
| **Parabolic move** | Exit entirely, re-enter on pullback | Don't chase, wait for setup |

### Exit Signal Framework

When designing exit signals, categorize by confidence level:

**High Confidence (act immediately):**
- Volume breakout: price breaks resistance with >1.5x average 24h volume
- Momentum surge: RSI > 70 + price above range high + volume spike
- Macro catalyst: major event (rate cut, peace deal, ETF approval)

**Medium Confidence (scale out):**
- Trend confirmation: 4h close above resistance with rising volume
- Partial exit (50%), rest on confirmation

**Low Confidence (wait):**
- Parabolic move: >15% in 24h with no pullback — too late to exit optimally
- Better to wait for consolidation than chase

### Resistance Ladder Pattern

When price is trending up, define key levels and what to do at each:

```
Level | Action
$X    | Exit 25%, keep LP running
$Y    | Exit 25% more, rebalance LP to new range
$Z    | Exit 25%, rebalance LP again
$W    | Exit final 25%, go full spot
```

Key principles:
- Scale out, don't dump everything at once
- Each exit level should correspond to a historical support/resistance flip
- Keep some LP running at each level to earn fees from traders fighting that zone
- Set bid-ask at resistance levels to sell into strength and buy pullbacks

### Re-Entry Rules

When designing re-entry signals, look for:

| Signal | Condition | Action |
|--------|-----------|--------|
| Consolidation | Price in $0.50 range for 48+ hours | Re-enter LP at consolidation range (curve) |
| Pullback to support | 15-20% retracement, holds a level | Re-enter at support zone (curve) |
| Volume decline | Volume < 0.8x average after rally | Re-enter — less directional pressure |
| RSI reset | RSI drops from >70 to 40-50 | Momentum cooled, range likely |

### Position Sizing Templates

**Bull breakout transition:**
```
├── 75% → Spot (hold for upside)
├── 15% → Bid-Ask LP at resistance (earn fees on pullback)
└── 10% → USDC reserve (dry powder for DCA)
```

**Post-consolidation re-entry:**
```
├── 50% → Spot AVAX (still bullish)
├── 30% → LP at new range (curve)
└── 20% → USDC reserve
```

**Crash protection:**
```
├── Exit LP (out of range)
├── Hold spot (already holding from exit)
└── Wait for support confirmation, then re-enter LP
```

## Design Workflow

1. **Assess current regime** — choppy, trending, crashing, consolidating?
2. **Identify current position** — shape, range, in/out of range, fee efficiency
3. **Define exit triggers** — what conditions would make LP underperform holding?
4. **Set resistance ladder** — key levels where price might sell off
5. **Define re-entry rules** — when to go back into LP after exiting
6. **Document in vault** — add to LP-Monitor-Rules.md or strategy file
7. **Wire into monitor** — add signal fields to cron job output JSON
8. **Set alert format** — define how the agent communicates the signal

## Documentation Pattern

When adding strategy rules to vault files, use this structure:

```markdown
## [Strategy Name] (DeFi Addendum — [date])

> *"[User quote that inspired the strategy]"* — [Name]

### Core Principle
[1-2 sentence summary of the strategy thesis]

### Exit Signal Triggers
[Table of signals with conditions, confidence, and actions]

### Resistance Ladder
[Table of levels with significance and LP strategy]

### Re-Entry Rules
[Table of signals with conditions and actions]

### Position Sizing
[Code block with allocation breakdown]

### Monitor Integration
[JSON schema for cron job output]

### Alert Format
[Example alert the agent would send]
```

## Common Pitfalls

1. **Over-engineering triggers** — keep it to 3-5 signals max, or the system becomes paralyzing
2. **Ignoring IL math** — always calculate what LP returns vs spot would be at the target price
3. **No re-entry plan** — designing exit rules without re-entry rules leaves capital idle
4. **Forgetting fees** — LP earns fees even when out of range on some bins; factor this into exit decisions
5. **Static ranges** — resistance levels shift over time; review ladder monthly
6. **All-or-nothing exits** — always scale out in tranches, never exit 100% at once

## Jordan's Zone-Based DCA Preference (Jun 2026)

**Core principle:** Jordan prefers zone-based DCA (price-level triggers) over calendar DCA (fixed schedule regardless of price). "Buy the dip on the average of the dip."

### How It Works

Instead of investing a fixed amount every week regardless of price, split the capital into tranches and deploy at specific price levels:

```
AVAX DCA Zones (Jun 2026):
├── $6.50-$6.78 — Accumulate zone → deploy tranche 1
├── $5.50-$6.00 — Approaching Deep Value → deploy tranche 2 (limit bid)
├── $4.50-$5.00 — Deep Value → deploy tranche 3 (aggressive)
└── Below $4.50 — Capitulation → deploy tranche 4 (size up if fundamentals hold)
```

### Why This Works Better Than Calendar DCA

- **Buys the dip on the dip** — capital deploys at progressively better averages
- **No timing pressure** — you don't need to catch the exact bottom
- **Two ways to win** — if price drops, limit bids fill at great entries; if price stays flat, LP earns yield; if price recovers, LP captures upside
- **Reduces regret** — you're always "in the game" at some level

### Implementation Pattern

1. Define zones based on buy zone system (Deep Value → Accumulate → Watch → Extended)
2. Allocate fixed dollar amount per tranche (e.g., $15 per tranche)
3. Set limit bids at lower zones
4. Enter LP at current zone with first tranche
5. Let lower tranches fill automatically

### Key Rule

Jordan still likes weekly DCA for discipline, but zone-based triggers are the primary entry strategy. Calendar DCA is the backup for weeks when no zone triggers hit.

## Integration with Existing Skills

- **`defi-onchain-position-reader`** — read current position data before designing strategy
- **`market-macro-monitor`** — check current prices and macro context for regime assessment
- **LP Monitor cron jobs** — wire exit/entry signals into JSON output for automated alerts

---

## Multi-Strategy Portfolio Rotation (v1.1)

Beyond single-strategy LP design, the AAE Hybrid Strategy Brain rotates between multiple DeFi strategies based on market regime. This section covers portfolio-level allocation.

### Strategy Regime Map

| Market State | Best Strategy | Signal |
|-------------|--------------|--------|
| **High volatility + breakout** | HODL (spot) | Volume spike, RSI >60, above range |
| **High volume + range-bound** | LP (concentrated liquidity) | Tight spread, high pair volume |
| **Low volatility + sideways** | Staking (stable yield) | Range-bound, no clear trend |
| **Any market** | Yield Farming (passive baseline) | Always-on, compounding |

### Hybrid Allocation Model

Instead of all-or-nothing, run a **weighted portfolio** that shifts:

```
BASELINE (always active):
├── 30% — Yield Farming (passive, compounding)
├── 20% — Staking (stable yield, low risk)
└── 50% — Active bucket (LP / HODL / rotate)

ACTIVE BUCKET (dynamic):
├── LP when: volume high, range-bound
├── HODL when: breakout / momentum surge
├── Rotate when: signals shift
└── Defensive when: macro uncertainty
```

### Market Regime Classifier

Define signals that detect each market state:

```
HIGH VOLATILITY + BREAKOUT
├── Price breaks resistance with >1.5x normal volume
├── RSI crossing 70 with momentum
└── Action: Shift 50% to HODL, exit LP

HIGH VOLUME + RANGE-BOUND
├── Price in tight range, high trading volume
├── RSI 40-60, no directional bias
└── Action: Increase LP allocation to 40%

LOW VOLATILITY + SIDEWAYS
├── Price in narrow range for 48+ hours
├── Volume below average, RSI neutral
└── Action: Max staking allocation (30%)

MACRO UNCERTAINTY
├── Bearish signals, negative sentiment
├── Volume declining, RSI dropping
└── Action: Max staking + farming (60%), exit LP
```

### Strategy Switching Notifications

Agents proactively notify users on regime shifts:

> *"Market regime shift detected. RSI crossing 70 with volume surge — transitioning 40% from LP to HODL position. Yield farming continues at 30% baseline. Approve?"*

Or in passive mode:

> *"AAE re-allocated: LP ↓30%, HODL ↑20%, Staking ↑10%. Net yield impact: +2.3% projected APR."*

### Competitive Advantage

| Single-Strategy Approach | Multi-Strategy Rotation |
|------------------------|------------------------|
| Locked into one yield type | Adapts to market conditions |
| Manual prompt required | Proactive regime detection |
| Reactive only | Predictive + reactive |
| One-dimensional returns | Hybrid compounding |

---

## Trainable Learning Layer (v1.1)

The AAE doesn't just execute — it **learns from the user** and trades like them over time.

### How It Works

1. **Observe** — AAE watches user trading decisions (buys, sells, holds, timing)
2. **Learn** — Pattern recognition: risk tolerance, preferred strategies, market conditions
3. **Mimic** — AAE starts making decisions *like the user*, with their style baked in
4. **Execute** — Autonomously runs strategies when user is not watching
5. **Improve** — Compares its decisions to user's, learns from corrections

### Feedback Loop

```
USER ACTION → AAE OBSERVES → PATTERN CAPTURED
     ↑                                    ↓
     ← CORRECTION ← AAE PROPOSES ←
```

- User corrects AAE: "No, exit now" → AAE learns the signal
- User approves AAE: "Yes, good call" → AAE reinforces the pattern
- Over time: AAE = personalized trading agent that thinks like the user

### Learning Modes

| Mode | Description | When to Use |
|------|------------|-------------|
| **Shadow Mode** | AAE observes, suggests, but doesn't execute. User confirms every move. | Initial learning phase, new strategies |
| **Supervised Mode** | AAE executes with approval. User can override anytime. | Building trust, validating patterns |
| **Autonomous Mode** | AAE runs independently. Only notifies on major shifts. | Proven patterns, user confidence |

### Key Differentiator

> *"Everyone is building AI that trades better than you. We're building AI that trades **like** you — and learns to be even better."*

The user doesn't lose control. They **train** the system. Their edge becomes the AI's edge.

---

## Example: Bull Market Exit Strategy (Completed)

See `/root/vaults/gentech/03-Strategies/LP-Monitor-Rules.md` — "🐂 Bull Market Exit Strategy (DeFi Addendum — Apr 29, 2026)" for a fully documented example covering exit signals, resistance ladder ($10/$12/$15/$18/$20+), re-entry rules, position sizing, and monitor integration.
