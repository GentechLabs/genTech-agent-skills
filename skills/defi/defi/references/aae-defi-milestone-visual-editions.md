# AAE DeFi Milestone Visual Editions — Reference

**Date:** 2026-06-01
**Vault:** `09-Green Room/aae-defi-milestone-visual-editions.md`
**Templates:** `03-Strategies/Defi-Monitor/`

---

## Vision

"Proof of Work" for Yield Farming Agents. Like Bitcoin mining dashboards show hashrate and rewards, our dashboards show agents farming yield and hitting milestones.

**Two user paths:**
- **Manual users** — yield farm themselves (Trader Joe style)
- **Autonomous users** — let the agent do it (subscription)

**The visual = trust layer.** Users can see the agents actually working, earning, compounding.

---

## Existing Templates

### 1. defi-milestone-tracker.html (Gold Theme)
- **Sections:** Header, Accumulation Banner, Current Position, DCA Schedule, Projection Table, Milestone Ladder (4 milestones)
- **Milestones:** Scout ($5/day), Raider ($20/day), Warlord ($55/day), Sovereign ($200/day)
- **Data:** Position value, token amounts, APR, fees, rewards, range status
- **Use case:** `/d5` daily check-in

### 2. yield-farm-tracker.html (Green Theme)
- **Sections:** Header, Stats Grid, Position Card, Fees Card, Range Card, Rewards Card, DCA Card, Pool Info
- **Data:** Token breakdown, composition bar, fees (24h/cumulative), range config, rewards, pool details
- **Use case:** `/farm` deep-dive

### 3. agent-performance.html (Cyberpunk Theme)
- **Sections:** Header, Stats Grid, Agent Actions, Performance Metrics, Position Health, Income Projection, Agent Config
- **Data:** Agent status, last 5 actions with timestamps/impact, ROI, compound efficiency, rebalance accuracy
- **Use case:** Autonomous users viewing agent performance

---

## Visual Editions

| # | Edition | Theme | Trigger | Key Elements |
|---|---------|-------|---------|--------------|
| 1 | Milestone Ladder | Gold | `/d5` | Progress bars, projection table |
| 2 | Yield Farm Detail | Green | `/farm` | Token breakdown, fees, range |
| 3 | Agent Performance | Cyberpunk | Agent view | Actions, ROI, config |
| 4 | Squad Dashboard | Multi | Social | Multiple positions, leaderboard |
| 5 | Celebration | Gold+Confetti | Milestone hit | Stats, share card |
| 6 | Alert | Red | Out of range | Warning, action needed |
| 7 | Weekly Summary | Blue | Sunday cron | 7-day chart, trend |

---

## Design Principles

1. **Context matches emotion** — Daily check-in is calm, celebration is exciting, alert is urgent
2. **Data is visual** — Progress bars, composition bars, color-coded stats
3. **Mobile-first** — Telegram screenshots, 1400x900 viewport
4. **Dark mode** — All templates use dark backgrounds for contrast
5. **Branding** — GenTech colors (gold/green/blue), consistent typography

---

## Template Variables

```html
<!-- Position -->
{{position.total_usd}}
{{position.avax_amount}}
{{position.usdc_amount}}
{{position.range_status}}

<!-- Fees & Rewards -->
{{fees.24h_usd}}
{{fees.cumulative}}
{{rewards.apr}}
{{rewards.claimable}}

<!-- Milestones -->
{{milestone.current}}        <!-- Scout/Raider/Warlord/Sovereign -->
{{milestone.progress}}       <!-- 0-100% -->
{{milestone.next_target}}    <!-- $20/day etc -->

<!-- Agent -->
{{agent.status}}             <!-- active/idle/rebalancing -->
{{agent.last_action}}        <!-- rebalance/compound/dca -->
{{agent.roi}}                <!-- +12.4% -->
{{agent.compound_efficiency}} <!-- 94% -->

<!-- Projections -->
{{projection.monthly}}
{{projection.to_next_milestone}}
{{projection.dca_impact}}
```

---

## Screenshot Pipeline

```python
def generate_dashboard(dashboard_type, wallet_address):
    # 1. Fetch live data from Data Layer
    position = fetch_lp_position(wallet_address)
    prices = fetch_prices(["AVAX", "USDC"])
    fees = fetch_fee_history(wallet_address)
    
    # 2. Populate HTML template
    html = render_template(dashboard_type, {
        "position": position,
        "prices": prices,
        "fees": fees,
        "milestones": calculate_milestones(position),
        "projections": generate_projections(position)
    })
    
    # 3. Screenshot with headless browser
    screenshot = browser.screenshot(html, width=1400, height=900)
    
    # 4. Return PNG path
    return screenshot
```

---

## Related

→ See `00-HQ/AAE-DeFi-Milestone-Spec.md` (Full spec)
→ See `03-Strategies/Defi-Monitor/` (Templates)
→ See `09-Green Room/lobby-ui-order-book.md` (Order book design)
