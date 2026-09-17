# shape-semantics
> *Use when the user talks about an agent understanding what a trading shape is and does — CURVE vs BID_ASK, knowing the shape not just the trigger. Shape selector that reasons about semantics, not just regime mapping.*

## 1. What this skill encodes

The Agentic Treasury's shape selector doesn't just "map regime → shape" — it *knows* what each shape is, what it does, and when it fits the scenario. That's the difference between a rule-follower and a reasoning operator.

### Shapes the treasury knows

- **CURVE** — earns from chop within a range. Best when price oscillates inside the bins. Worst when price trends *through* the range (price breaks out, curve gets left behind, fee capture drops to zero).
- **BID_ASK** — concentrates liquidity at the front/back of the range. Captures directional movement. Best when there's a trend to catch (either direction). Worst in whipsaw (rapid back-and-forth with no net direction — gets clipped both ways).
- **SPOT** — flat. No yield. No shape. Best deployed into a trade, leverage, or a different earn strategy when the LP shapes aren't the right fit.

### What "knowing a shape" means

A rule-follower knows: RANGE_BOUND → CURVE, BULL_TRENDING → BID_ASK.

A shape-aware operator knows: **CURVE earns when price stays inside the bins and trades cross them. BID_ASK captures when price moves from one side of the range to the other. If the price is trending up and out of the top of the range, a CURVE re-center at the current price just puts us out of range again on the next tick up — a BID_ASK that extends the range upward catches the trend instead.**

That's the semantic layer. The shape selection becomes a *reasoning step*, not a lookup table.

## 2. Assessment criteria

When the user is evaluating whether an agent truly knows shapes, they ask themselves:

1. **Can it explain what a CURVE does vs a BID_ASK in plain language?** Not just "CURVE for range, BID_ASK for trend" — but *what happens to fee capture* when price trends through a CURVE, and *what BID_ASK does instead*. If it can't explain the mechanics, it doesn't know the shape.

2. **Can it reason about *when* to use each shape based on the scenario, not just the regime label?** If the regime says RANGE_BOUND but the price is trending up and out of the top, does it see the mismatch? Does it adjust the shape *before* or *after* the range breaks? A rule-follower waits for the regime to flip. A shape-aware operator sees the price action and adjusts.

3. **Does it know what happens to the position when it picks wrong?** A CURVE that re-centers at a price that then trends up: position goes out of range on the upside, fee capture stops. A BID_ASK that deploys into whipsaw: gets clipped both ways, earns less than a CURVE would have. Knowing the cost of being wrong is part of knowing the shape.

4. **Can it talk about shape *selection* as a reasoning step, not a policy lookup?** "The regime is RANGE_BOUND so I deploy CURVE" is a policy. "Price is trending up and breaking the top of the range — a CURVE re-center here would just be out of range again in a few ticks, so I'd rather extend the range upward with a BID_ASK or hold spot until the trend settles" is reasoning.

## 3. How the agent uses this

### Shape selection becomes a reasoning chain

The current architecture maps regime → shape via a dictionary (`REGIME_SHAPE` in `steward_rebalance.py`). That's the rule-follower baseline.

The shape-aware version adds a reasoning step *on top* of the regime read:

1. Read regime (RANGE_BOUND, BULL_TRENDING, etc.) — the honest market label
2. Read price action relative to the position (is price inside the range, at an edge, breaking out?)
3. For each candidate shape, run the semantic check: "what happens to this position if I deploy {shape} at {price} and the price does {scenario}?"
4. Pick the shape whose outcome matches the goal (stay earning, capture trend, minimize IL)
5. Explain the choice in plain language so the user can follow the reasoning

### The shape map becomes a starting point, not the answer

```python
# Baseline (rule-follower): regime maps to shape
REGIME_SHAPE = {
    "RANGE_BOUND": "CURVE",
    "BULL_TRENDING": "BID_ASK",
    ...
}

# Shape-aware: regime gives a default, reasoning adjusts
shape = REGIME_SHAPE.get(regime_name, "CURVE")
shape = reason_about_shape(shape, position, price_action, regime)
```

### Two concrete cases from this session

**Case 1 — RANGE_BOUND with price trending up and out:**
- Regime: RANGE_BOUND (honest — daily chop, 7d momentum only 2.3%)
- Price: $7.58, above range $7.4248–$7.4620, trending up
- Rule-follower: deploy CURVE at current price → trend breaks it again on the next tick up → out of range, fee capture stops
- Shape-aware: "price is leaving the range upward. A CURVE re-center at $7.58 just puts us out of range again. Better to either BID_ASK that extends the range upward to catch the trend, or hold spot until the trend settles and re-deploy a CURVE lower. The regime label doesn't change, but the *shape* should."

**Case 2 — BULL_TRENDING with a clean trend:**
- Regime: BULL_TRENDING
- Price: trending cleanly, volume supporting
- Rule-follower: deploy BID_ASK because the map says so
- Shape-aware: "BULL_TRENDING + clean trend = BID_ASK is right. The range should be wide enough to catch the move, not so tight it gets left behind. Shape is right, but check the *width* — too narrow and we miss the trend, too wide and we earn less per bin."

## 4. Response protocol

When the user asks about shape selection or the agent explaining its shape choice:

1. **Name the shape and what it earns** — "CURVE earns from bin crossings inside the range. BID_ASK earns from the price moving through the concentrated bins at the edges."

2. **Explain the scenario it fits** — "CURVE fits chop inside a range. BID_ASK fits a trend that moves the price from one side to the other."

3. **Explain what happens if the price doesn't cooperate** — "If price trends through a CURVE, the curve gets left behind and fee capture drops to zero. If BID_ASK deploys into whipsaw, it gets clipped both ways."

4. **Say why this shape for this scenario** — connect the shape choice to the actual price action and regime, not just the regime label.

5. **Acknowledge the cost of being wrong** — "The risk with BID_ASK here is whipsaw — if the trend reverses sharply, we get clipped. The risk with CURVE is the trend leaves us behind."

## 5. What triggers building this skill

- User asks "does the agent know what a bid-ask is?" or "does it know when to use which shape?"
- User proposes shape selection should be reasoning-based, not rule-based
- User wants the agent to explain its shape choice in plain language
- User references "shape semantics" or "the agent knowing the shape"

## 6. Notes

- The shape semantics layer is additive — it sits on top of the regime classifier, doesn't replace it. The regime is still the honest market label. The shape reasoning is what interprets the regime *in context of the position*.
- The Assessment criteria (4 questions) are for the *user* to evaluate the agent, not for the agent to self-assess. The agent shows its shape awareness through its reasoning, not by ticking boxes.
- Shape semantics and the shape override (FARM-mode shape adjustment) are related but separate. The override is "when FARM is committed, adjust shape by price trend." The semantics layer is "understand what each shape is and does, then reason about which fits." The override can use the semantics layer as its reasoning engine.
- Shape semantics is a capability, not a module. It's demonstrated by how the agent talks about and selects shapes, not by a specific file or function.
