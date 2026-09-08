# Buy Zone Framework

**Last updated:** 2026-06-08

## Concept

Tiered buy zones for each asset, displayed alongside price data in the CMC watchlist report. Each coin gets 4 zones:

| Zone | Meaning | Action |
|------|---------|--------|
| 🔥 Deep Value | Below all major support | Heavy accumulation — historic opportunity |
| 🟢 Accumulate | At or near strong support | Good entry, DCA territory |
| 🔵 Watch | Current trading range | Monitor, wait for dip |
| ⚪ Extended | Above recent resistance | Too expensive, wait for pullback |

## Zone Definitions (18 coins)

```python
BUY_ZONES = {
    "BTC":   [("", 0, 50000), ("", 50000, 60000), ("", 60000, 70000), ("", 70000, 999999)],
    "SOL":   [("", 0, 40),    ("", 40, 60),       ("", 60, 80),       ("", 80, 999999)],
    "LINK":  [("", 0, 5),     ("", 5, 8),         ("", 8, 12),        ("", 12, 999999)],
    "AVAX":  [("", 0, 5),     ("", 5, 7),         ("", 7, 10),        ("", 10, 999999)],
    "TAO":   [("", 0, 150),   ("", 150, 250),     ("", 250, 400),     ("", 400, 999999)],
    "ONDO":  [("", 0, 0.50),  ("", 0.50, 0.80),   ("", 0.80, 1.20),   ("", 1.20, 999999)],
    "XAUt":  [("", 0, 2000),  ("", 2000, 2500),   ("", 2500, 3000),   ("", 3000, 999999)],
    "XAG":   [("", 0, 25),    ("", 25, 30),       ("", 30, 35),       ("", 35, 999999)],
    "BEAM":  [("", 0, 0.005), ("", 0.005, 0.01),  ("", 0.01, 0.02),   ("", 0.02, 999999)],
    "COQ":   [("", 0, 0.0000005), ("", 0.0000005, 0.000001), ("", 0.000001, 0.000002), ("", 0.000002, 999999)],
    "ARENA": [("", 0, 0.05),  ("", 0.05, 0.10),   ("", 0.10, 0.20),   ("", 0.20, 999999)],
    "PEPE":  [("", 0, 0.000005), ("", 0.000005, 0.00001), ("", 0.00001, 0.00002), ("", 0.00002, 999999)],
    "RENDER":[("", 0, 3),     ("", 3, 6),         ("", 6, 10),        ("", 10, 999999)],
    "DOGE":  [("", 0, 0.08),  ("", 0.08, 0.12),   ("", 0.12, 0.20),   ("", 0.20, 999999)],
    "ILV":   [("", 0, 5),     ("", 5, 10),        ("", 10, 20),       ("", 20, 999999)],
    "AERO":  [("", 0, 0.30),  ("", 0.30, 0.60),   ("", 0.60, 1.00),   ("", 1.00, 999999)],
    "TRUMP": [("", 0, 5),     ("", 5, 10),        ("", 10, 20),       ("", 20, 999999)],
}
```

## Narrative Rotation Engine

Dynamically tracks capital flow between 8 narrative categories. Uses BTC as benchmark:

- **Momentum** = (narrative 7d avg - BTC 7d avg) - (narrative 30d avg - BTC 30d avg)
- **🔥 HEATING** (momentum > +3): Recovering faster than BTC, capital flowing in
- **🟢 Warming** (0 to +3): Tracking with BTC
- **🟡 Stable** (-3 to 0): Slightly lagging
- **🔴 Cooling** (< -3): Capital flowing out

Output sorted hottest → coldest with leading/dragging coins identified.

## Pitfalls

- **Zone definitions need manual updates** after major market structure changes
- **XAG (silver) data unreliable** — CMC returns rank #7800+ with $0 volume
- **RENDER/AERO** may not return data from CMC free tier — verify symbols
- **Rotation is relative to BTC** — in recovery phases, all narratives may show "HEATING" but ranking reveals relative strength
