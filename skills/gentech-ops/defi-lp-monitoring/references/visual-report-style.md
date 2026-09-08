# Visual Report Style — Cron Job Formatting

## Style Standard

Cron reports use **box-drawing characters**, **visual bars**, and **tree-structured bullets** for scanable hierarchy.

## Template Structure

```
✅ **Report Name**
`Timestamp`

┌────────────────────────────────────────────┐
│ 📊 **Header Section**                      │
├────────────────────────────────────────────┤
│ **Status:** 🟢 In Range       │
│ **Price:**   $6.2960                        │
│ **Range:**   $6.1899 – $6.3783         │
│ **Eff:**     █████████░ 96.0%              │
│ **Shape:**   CURVE                           │
└────────────────────────────────────────────┘

**💎 Section**
├─ Metric A: `value`
├─ Metric B: `value`
└─ Total: **`$47.00`**

**💸 Another Section**
├─ Daily: `$0.203`
└─ Cumulative: `$1.034`

**📈 PnL**
├─ Entry: `$6.2300`
└─ IL: 🟡 `+1.06%`

**💡 DCA Strategy**
🟢 Center zone (70%+ efficiency) — full $6.3 DCA (~15% of position)

**📍 Key Levels**
`Proximity: 🟢 CENTER`
`🟢 AWAY FROM EDGES (0min)`
→ Price is centered in range. No consolidation to watch.
`Price near range center — optimal fee zone. No action needed.`

🟢 `$6.1899` — Range Floor `56.3%`
   → WATCH — if price holds, bid-ask earns. If breaks, rebalance down.
⚡ `$6.1616` — Rebalance Trigger (Below) `71.3%`
   → REBALANCE to $6.14–$6.18

**📊 vs Alternatives**
├─ LP Farming: **803.3% APR** (`$0.203/day`)
├─ AVAX Staking: `6.7% APR** (`$0.009/day`)
├─ HODL (50/50): `-0.53%` since entry
└─ vs Staking: 🟢 **Outperforming**

┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
`Source | Timestamp`
```

## Python Implementation

```python
def format_report(...) -> str:
    lines = []
    
    # Header
    emoji = "✅" if alert_level == "OK" else "⚠️" if alert_level == "LOW" else "🚨"
    lines.append(f"{emoji} **Report Name**")
    lines.append(f"`{now_et().strftime('%Y-%m-%d %H:%M EDT')}`")
    lines.append("")
    
    # Box-drawing header card
    lines.append("┌────────────────────────────────────────────┐")
    lines.append("│ 📊 **Section Name**                      │")
    lines.append("├────────────────────────────────────────────┤")
    lines.append(f"│ **Status:** {status_icon} {status_text:14s} │")
    lines.append(f"│ **Price:**   ${price:.4f}                        │")
    lines.append(f"│ **Range:**   ${range_low:.4f} – ${range_high:.4f}         │")
    
    # Efficiency bar
    eff_pct = min(100, max(0, efficiency))
    bars = int(eff_pct / 10)
    eff_bar = "█" * bars + "░" * (10 - bars)
    lines.append(f"│ **Eff:**     {eff_bar} {eff_pct:4.1f}%              │")
    
    lines.append(f"│ **Shape:**   {display_shape:20s}            │")
    lines.append("└────────────────────────────────────────────┘")
    lines.append("")
    
    # Tree-structured bullets
    lines.append("**💎 Section**")
    lines.append(f"├─ Metric A: `{value_a}`")
    lines.append(f"├─ Metric B: `{value_b}`")
    lines.append(f"└─ Total: **`${total:.2f}`**")
    lines.append("")
    
    # Footer
    lines.append("┄" * 44)
    lines.append(f"`Source | {now_et().strftime('%H:%M EDT')}`")
    
    return "\n".join(lines)
```

## Visual Elements

| Element | Usage | Example |
|---------|-------|---------|
| Box drawing `┌─┐ ├─┤ └─┘` | Section headers | Card-style layouts |
| Progress bar `█` `░` | Efficiency/metrics | `█████████░ 90%` |
| Tree bullets `├─` `└─` | Hierarchical lists | Position breakdown |
| Color emojis 🟢🟡🔴 | Status indicators | IL, alerts, performance |
| Monospace backticks | Values/metrics | `$6.2960`, `+1.06%` |
| Separator line `┄` | Footer divider | Bottom boundary |

## Jordan's Preference

"Can we get a visual upgrade for the cron Job 😎 we got some heat from the last update"

- Clean, scanable hierarchy over dense paragraphs
- Visual progress bars for efficiency
- Box-drawing cards for key metrics
- Color-coded status (green/yellow/red)
- Tree-structured bullets for nested data

## Applied To

- `defi-lp-consolidated.py` — DeFi Milestone + LP Report (Jun 28, 2026)

## Future Cron Jobs

All new cron output should follow this style standard for consistency.