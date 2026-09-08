# Strategy Design (Full)

> Absorbed from `defi` skill §2 and `defi-operations` §2. Complete strategy framework.

## Regime-Based Strategy

### 4 Regime Types

| Regime | Action | LP Allocation |
|--------|--------|---------------|
| Range-bound | 100% LP | Full position |
| Bull confirmed | 25% LP + 75% spot | Capture trend upside |
| Bear confirmed | 100% LP or stable | Earn fees in decline |
| Uncertain | Wide-range LP | Maximize range |

### Shape by Regime

| Regime | Best Shape | Range |
|--------|-----------|-------|
| Choppy/ranging | Curve | Tight (3%) |
| High volatility, no direction | Bid-Ask | Wide (6%) |
| Strong bullish breakout | Exit → spot | — |
| Crash/panic dump | Skewed curve | 70% stablecoin |
| Consolidation after rally | Curve | New range |

## "Go Spot" Signal Framework

5 signals — 3+ fire → exit 75% LP to spot:
1. Price holds above level for 48h+
2. BTC trend confirmation
3. Macro pivot signal
4. Volume 2x average
5. Higher lows pattern

### LP Re-Entry at Resistance

Consolidation at level for 12-24h → re-LP. Blast through → stay spot.

### Exit Everything Signal

RSI >85, BTC distribution, macro shock, 3x from recent levels.

## Position Sizing Templates

**Bull breakout:** Scale in 50% at breakout, 25% on retest, 25% on confirmation.
**Post-consolidation:** 40% at range midpoint, 30% at support, 30% reserve.
**Crash protection:** 20% immediate (dip buy), 30% at -20%, 50% reserve.

## LP + Limit Bid Combo (Bottom-Fishing)

When accumulating near support:
1. **LP position** — earn yield while waiting
2. **Limit bid below** — trap at lower support (8-10% below)
3. **Two ways to win:** limit fills on drop, LP earns on flat, LP captures upside on bounce

**Monitor total exposure** — both increase concentration in same asset.

## Exit Signal Framework

| Confidence | Signal | Action |
|-----------|--------|--------|
| High | Volume breakout, momentum surge, macro catalyst | Act immediately |
| Medium | Trend confirmation | Scale out 50%, rest on confirmation |
| Low | Parabolic moves | Wait for consolidation |

## Multi-Strategy Rotation (v1.1)

Baseline: 30% yield farming, 20% staking, 50% active bucket (LP/HODL/rotate).
Active bucket shifts based on regime detection.

## Trainable Learning Layer

AAE observes user trading decisions → learns patterns → mimics style → executes autonomously → compares and improves.

Modes: Shadow → Supervised → Autonomous

## Jordan's Investment Philosophy

- **Small/mid cap focus** for asymmetric returns (10x+ moves)
- **"Rich Rich" thesis:** BTC/ETH can't deliver life-changing returns at current caps
- **Boomer token filter:** Institutional backing + real on-chain activity + active dev
- **Accumulation mindset:** Low prices = opportunity
- **Zone-based DCA:** Buy at PRICE LEVELS, not on schedule
- **LP + Limit Bid combo:** Two ways to win
- **Approval model:** Code/docs = do, spending = flag, mainnet = wait

## Macro Context for LP Decisions

| Signal | What It Tells You | Source |
|--------|-------------------|--------|
| Fed meeting schedule | Rate decisions move everything | federalreserve.gov |
| Gold/silver correlation | If falling with stocks = liquidity crisis | Barchart |
| Stablecoin inflows | Rising = dry powder accumulating | DefiLlama |
| BTC dominance | Rising = flight to quality; falling = alt rotation | CMC |
| DXY | Strong $ = risk-off; weak $ = risk-on | TradingView |

## Liquidity Crisis Pattern

When gold, silver, stocks, AND crypto ALL fall together:
- It's mechanical liquidation, not fundamental repricing
- Safe havens fail (sold to cover margin elsewhere)
- Smart money moves to stablecoins
- Creates opportunity for patient accumulators

## RWA Token Evaluation

**Hard rule: Liquidity Before APY**

| DEX Volume | APY | Action |
|------------|-----|--------|
| >$10K/day | Any | Evaluate normally |
| $1K-10K/day | >20% | Small position only (<$200) |
| $1K-10K/day | <20% | Watch, wait for volume growth |
| <$1K/day | Any | **PASS** — can't exit |
