# Key Levels Engine — Consolidation Tracking

## What It Solves
Before: Out-of-range alerts just said "RECONFIGURE NEEDED" — no guidance on levels or timing.
After: Every report shows distance to floor/ceiling, consolidation duration, and specific rebalance ranges.

## Consolidation Time Thresholds

| Phase | Duration | Signal | Action |
|-------|----------|--------|--------|
| ⏱️ EARLY | <15 min | Just arrived at edge, too early to act | Watch, don't rebalance |
| 🟡 WATCHING | 15-30 min | Consolidation forming | Monitor for direction |
| 🟡 MATURE | 30m-1h | Breakout likely soon | Be ready to rebalance |
| 🔴 CRITICAL | 1h+ | Extended consolidation, market has decided | Next move = rebalance NOW |

## How It Works
State tracks `edge_start` (timestamp) and `edge_direction` (low/high). Timer resets when:
- Price moves back to range center (>15% from both edges)
- Price switches to opposite edge (low→high or high→low)

## Knife vs Consolidation
- **Knife**: Sharp 5-10% drop in a single candle — may bounce back quickly, wait before rebalancing
- **Consolidation**: Gradual drift over hours with tight candles ($6.43→$6.38 over 6h in $0.08 band) — market is deciding direction, rebalance on breakout

## Edge Proximity Zones
- 🟢 CENTER: Price within 15% of range midpoint
- 🟡 IN RANGE: In range but off-center
- ⚠️ NEAR EDGE: <15% from floor or ceiling
- 🔴 OUT OF RANGE: Price broke through edge
