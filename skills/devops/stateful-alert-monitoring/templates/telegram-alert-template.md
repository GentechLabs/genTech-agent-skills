# Telegram Alert Templates — Stateful Monitoring

## Mini-Warning (Pending Confirmation)

**Tier:** WATCH — condition detected, awaiting confirmation  
**Emoji:** ⚠️  
**Frequency:** Once per condition per confirmation window  
**Purpose:** Soft heads-up, not urgent action yet

```
⚠️ **DeFi Monitor — Watching Condition**
Time: {time_str}
Condition: {condition_name}
Current: {current_value}
Threshold: {threshold_value}
Status: Monitoring for {CONFIRMATION_DELAY_MIN} minutes to confirm...
```

**Example:**
```
⚠️ **DeFi Monitor — Watching Condition**
Time: 2:15 PM EDT
Condition: Price out of range
Current: $8.92 (range: $8.95–$9.36)
Status: Monitoring for 5 minutes to confirm...
```

---

## Confirmed Alert (Action Required)

**Tier:** WATCH → CONFIRMED OR IMMEDIATE  
**Emoji:** 🚨  
**Frequency:** Once per condition lifetime (until condition clears)  
**Purpose:** Clear call-to-action, urgent

```
🚨 **{SCRIPT_NAME} — ACTION REQUIRED**
Time: {time_str} | {date_str}
Condition: {condition_name} [CONFIRMED]

Current: {current_value}
Threshold: {threshold_value}
Context:
• Price: {price_str} ({price_change:+.2f}%)
• Efficiency: {efficiency}%
• Fees (24h): ${fees}

🎯 Action: {action_recommendation}

---
📊 Data: {data_sources}
🔔 Status: Escalated after {CONFIRMATION_DELAY_MIN}min confirmation
```

**Example:**
```
🚨 **DeFi Milestone — ACTION REQUIRED**
Time: 2:20 PM EDT | Saturday, May 02
Condition: Out of Range [CONFIRMED]

Current: $8.92 (below $8.95 lower bound)
Context:
• Price: $8.92 (-1.2% vs 24h ago)
• Efficiency: 42.1%
• Fees (24h): $0.19

🎯 Action: Rebalance suggested — shift LP range downward to capture current volatility

---
📊 Data: CMC + DexScreener + DeBank
🔔 Status: Escalated after 5min confirmation
```

---

## Immediate Alert (No Debounce)

**Tier:** IMMEDIATE  
**Emoji:** 🚨  
**Frequency:** Every run while condition holds (rate-limited by `MIN_ALERT_INTERVAL_MIN`)  
**Purpose:** Critical condition requiring instant attention

```
🚨 **{SCRIPT_NAME} — CRITICAL**
Time: {time_str}
Condition: {condition_name} (IMMEDIATE)

Metric: {metric_name} = {current_value}
Threshold: ≤ {threshold_value}

🎯 Action: {action_recommendation}

⚠️ This condition does not wait for confirmation — address immediately.
```

**Example:**
```
🚨 **DeFi Milestone — CRITICAL**
Time: 12:15 PM EDT
Condition: Efficiency Critical (IMMEDIATE)

Metric: Fee efficiency = 28%
Threshold: ≤ 30%

🎯 Action: Rebalance NOW — efficiency in edge zone (<30%), capital poorly deployed

⚠️ This condition does not wait for confirmation — address immediately.
```

---

## Recovery Notice (Condition Cleared)

**Tier:** INFO (optional)  
**Emoji:** ✅  
**Frequency:** Once when condition clears after being confirmed  
**Purpose:** Close the loop, signal return to normal

```
✅ **{SCRIPT_NAME} — Condition Resolved**
Time: {time_str}
Previously: {condition_name}
New status: {new_status}

Current: {current_value}
Back within: {threshold_description}

➡️ Monitoring continues.
```

**Example:**
```
✅ **DeFi Milestone — Condition Resolved**
Time: 3:45 PM EDT
Previously: Out of Range [CONFIRMED]
New status: Price back in range $9.02

Current: $9.02 (range: $8.95–$9.36)
➡️ Monitoring continues.
```

---

## Formatting Rules

1. **Time:** Always include Eastern time (`%I:%M %p EDT`) and date if crossing midnight
2. **Condition name:** Short, scannable (`"Out of Range"`, `"Efficiency Low"`, `"Gas Critical"`)
3. **Values:** Use `fmt_price()` for tokens, `round(x, 1)` for percentages, `f"${x:.2f}"` for USD
4. **Action:** Start with verb: `Rebalance suggested`, `DCA now`, `Add gas`, `Check wallet`
5. **Sources:** Always list data sources at bottom (`CMC + DexScreener`, `On-chain reader`, etc.)
6. **No markdown heavy** — Telegram only supports bold/italic; use sparingly

---

## Rate-Limiting Logic

```python
MIN_ALERT_INTERVAL_MIN = 60

def can_send_alert(state):
    if not state['last_alert_sent']:
        return True
    elapsed = minutes_elapsed(state['last_alert_sent'])
    return elapsed >= MIN_ALERT_INTERVAL_MIN
```

Even if condition stays confirmed, suppress repeats within interval. Log to vault instead.

---

## Vault Entry Companion

Every confirmed alert should trigger a vault log entry (even if Telegram suppressed by rate-limit):

```markdown
## YYYY-MM-DD HH:MM Update

**Condition:** Out of Range — CONFIRMED after 5min  
**Price:** $8.92 | **Efficiency:** 42.1%  
**Action:** Rebalance needed (range shift)  
**Telegram:** Sent 2:20 PM EDT (tier: CONFIRMED)
```

---

## Copy-Paste Template Bundle

Save as `templates/telegram-alert-template.md` in skill dir. Copy relevant block into script and fill `{placeholders}`.
