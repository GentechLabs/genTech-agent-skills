# Leg Orientation Semantics — how to read a two-sided book

Reading a bid-ask back out of its bins is the single most mis-written check in this system. Three
successive versions of it produced a confident FALSE "INVERTED" on a correct book, so the rules
below are the corrected shape. The logic lives in a module-level pure function
(`_leg_orientation(shp, act_id, shape_kind)`) with a regression test, so it is exercisable without
the live hub.

## What a leg IS

**A leg is a CONTIGUOUS RUN of held bins.** The gap at spot separates the two legs: the lower run is
BID (holds USDC — buys as price falls), the higher run is ASK (holds WAVAX — sells as price rises).

Split the bins into runs first, then keep at most two. Do **not** group by "below spot" / "above
spot": that is a proxy for "which leg" and it only holds while price sits INSIDE its own band.

## The expectation depends on the SHAPE (shape-aware, never one rule for all)

| shape | geometry | heaviest where |
|---|---|---|
| `bid-ask` | **U** — pays at the edges | FAR edges (each leg is smallest nearest spot) |
| `curve` | **bell** | NEAREST spot |

A bid-ask's two legs together form the U the chart draws with spot at the trough: bid grows leftward,
ask grows rightward. Our build is 15 bid + 30 ask = 45 bins, junction `n0 = 33.3%`.

**A check that asserts one geometry for every shape reports the design as a fault.** The original
bug: `nearest_usd > furthest_usd` (a bell) asserted for ALL books, so every correct bid-ask read
INVERTED on both legs and the page instructed a rebuild of a healthy position.

## A crossed leg is NOT an inverted one — refuse the verdict

When price rises through a bid leg, that leg's bins are ABOVE the active bin and, being contiguous
with the ask leg, they **merge into a single run spanning spot**. The geometry is then genuinely
unreadable from the bins — two different ramps are now one.

Return:

```python
{"shape": shape_kind, "bid": None, "ask": None, "inverted": [],
 "judgeable": False, "verdict": None,
 "note": "cannot judge: a leg has been crossed by price, ..."}
```

and render it as an **INFO note**, never the alarm. Judgeable requires, for a two-run book:
- no run straddles the active bin (`min(ids) < act_id < max(ids)`),
- the bid run's max bin is strictly BELOW spot,
- the ask run's min bin is strictly ABOVE spot.

With ONE run and no gap, judge what you can but never invent a second leg.

## Honesty rules for this field

- An **all-zero leg is not a pass** (`None`, not `toward_spot=True`).
- An **empty book** is `None`, not `OK`.
- "Cannot judge" must never render as healthy AND never as an alarm. A crossed book is a normal
  market outcome.

## The regression test (`test_leg_orientation.py`)

Assert the historical false alarms as hard as the true positive — that is the whole point of the file:

| case | expected |
|---|---|
| bid leg heaviest nearest spot | `INVERTED: bid` (true positive still caught) |
| ask leg heaviest nearest spot | `INVERTED: ask` |
| correct bid-ask (both legs U) | `OK` — this was false alarm #1 |
| crossed book, runs merged | `verdict=None`, `judgeable=False` — this was false alarm #2 |
| all-zero leg | never `OK` |
| empty book | `None` |
| single run | never invents a second leg |
| bell-curve geometry (curve) | `OK` — the same geometry judges differently by design |

The test must be **enrolled in the same sync manifest as the code** — a guard that is not deployed
does not exist on the machine that runs it.

## Pitfall: your fixtures will be wrong before the detector is

The first run of this test failed 4/10 **because the fixture book had the geometry backwards**, not
because the detector was wrong. Build fixtures from real measured numbers pulled off the chain, and
state the direction explicitly in a comment (`bid must be heaviest FARTHEST from spot; heaviest
NEAREST spot is the defect`).
