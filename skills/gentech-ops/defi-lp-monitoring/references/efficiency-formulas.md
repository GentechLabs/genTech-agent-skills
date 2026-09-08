# LP Shape Efficiency Formulas

## Curve Shape
Max efficiency at CENTER (50% of range). Earns most when price is stable in the middle.

```python
pos = (price - rangeLow) / (rangeHigh - rangeLow)
efficiency = (1 - abs(pos - 0.5) * 2) * 100
```

Example: Range $6.00–$6.40, price $6.20
- pos = (6.20 - 6.00) / (6.40 - 6.00) = 0.50
- efficiency = (1 - 0) * 100 = **100%** (perfect center)

Example: Range $6.00–$6.40, price $6.35
- pos = (6.35 - 6.00) / (6.40 - 6.00) = 0.875
- efficiency = (1 - 0.75) * 100 = **25%** (near edge)

## Bid-Ask Shape
Max efficiency at EDGES. Earns most when price swings to boundaries.

```python
pos = (price - rangeLow) / (rangeHigh - rangeLow)
efficiency = abs(pos - 0.5) * 2 * 100
```

Example: Range $6.00–$6.40, price $6.20
- pos = 0.50
- efficiency = 0 * 100 = **0%** (center — worst for bid-ask)

Example: Range $6.00–$6.40, price $6.35
- pos = 0.875
- efficiency = 0.75 * 100 = **75%** (near edge — best for bid-ask)

## Spot Shape
Max efficiency everywhere within range. Single-price concentration.

```python
efficiency = 100  # always 100% if in range
```

## Key Insight

Same price, opposite results:
| Price Position | Curve Efficiency | Bid-Ask Efficiency |
|---------------|-----------------|-------------------|
| Center (50%) | 100% | 0% |
| 75% into range | 50% | 50% |
| Edge (90%) | 20% | 80% |
| Outside range | 0% | 0% |
