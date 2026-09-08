---
case_study: DeFi Milestone Cron Enhancement
date: 2026-05-02
author: Gentech (CEO)
skill_applied: stateful-alert-monitoring
related_script: 03-Strategies/scripts/defi-master-cron.py
vault_doc: 03-Strategies/Defi-Monitor/defi-milestone-enhancements-2026-05.md
---

## Context

Jordan voice-approved (May 2, 12:42 PM) enhancements to the DeFi Milestone monitoring cron job. The original script ran 4× daily and fired alerts immediately on condition changes (out-of-range, low efficiency). This caused noise when price ping-pongged across boundaries.

## Problem → Pattern Mapping

| Problem | Pattern Applied |
|---------|-----------------|
| Price crosses lower bound at 14:05, recrosses at 14:07 → false alert | **Debounce**: Wait 5min to confirm breakout |
| Efficiency <30% needs immediate attention (continuous decay) | **Tiered alerts**: Immediate path bypasses debounce |
| Need to suggest DCA boost when price near lower edge | **Conditional logic** in alert body (not part of debounce) |
| Multiple conditions could fire simultaneously | **Single escalation state** prevents spam |

## Implementation Decisions

### 1. State File Choice
**File:** `~/.hermes/scripts/.lfj-aae-state.json` (extend existing)
- **Why extend?** Existing state already tracks cumulative fees, days in range. Adding `pending_breakout` keeps all DeFi state together.
- **Schema addition:**
  ```json
  {
    "pending_breakout": {
      "condition": "out_of_range",
      "first_seen": "2026-05-02T14:05:00-04:00",
      "confirmed": false
    }
  }
  ```

### 2. Alert Tier Design
Three tiers implemented:
- **IMMEDIATE** (`eff ≤ 30%`) → 🚨 ACTION REQUIRED (no wait)
- **WATCH** (`out_of_range` OR `30% < eff < 50%`) → ⚠️ pending → 🚨 confirmed after 5min
- **INFO** (daily snapshot, Monday DCA) → vault only, no Telegram

### 3. Timing Parameters
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `CONFIRMATION_DELAY_MIN` | 5 | Matches Jordan's spec; short enough to be responsive, long enough to filter wicks |
| Cron frequency | 4× daily (8:15, 12:15, 4:15, 8:15 EDT) | 3–4 hour spacing means 5min is negligible overhead |
| `MIN_ALERT_INTERVAL_MIN` | 60 (implicit) | Prevent duplicate confirmed alerts if condition persists across many runs |

### 4. Bid-Ask Edge Strategy
Not a debounce pattern, but a **conditional recommendation**:
```python
if price <= range_low * 1.02 and 30 <= eff < 50:
    dca_note += " | 📈 Bid-ask edge — consider DCA boost"
```
- Buffer set at **2%** (YoYo to confirm)
- Trigger zone: efficiency 30–50% (low but not critical)
- Suggests temporary DCA multiplier (`BID_ASK_BOOST_MULTIPLIER`, default 1.5×)

## Code Structure (DMOB To Implement)

**File:** `03-Strategies/scripts/defi-master-cron.py`

1. **Add state helpers** (from `references/state-helpers-template.py`)
2. **Refactor `should_alert()`** → returns `(should_send, tier)` instead of boolean
3. **Add `check_debounce(state, condition_met)`**:
   - If `pending.confirmed == false` AND `elapsed ≥ 5min` AND `condition_met` → return `CONFIRMED`
   - If `pending.confirmed == false` AND `elapsed < 5min` → return `PENDING`
   - If `pending.confirmed == true` → return `CONFIRMED` (until cleared)
4. **Add `send_alert(message, tier)`**: formats differently (⚠️ vs 🚨), respects `last_alert_sent` rate limit
5. **Update main loop**:
   ```python
   state = load_state(STATE_PATH)
   metrics = compute_metrics()
   send, tier = should_alert(state, metrics)
   if send:
       msg = format_alert(metrics, tier)
       telegram.send(msg)
       state['last_alert_sent'] = now_iso()
   save_state(STATE_PATH, state)
   ```

## Acceptance Criteria (from handoff)

- [x] Vault doc created with full spec
- [x] Handoffs issued to DMOB (code) and YoYo (strategy/config)
- [ ] DMOB implements state machine (pending → confirmed)
- [ ] Efficiency ≤30% bypasses debounce (immediate)
- [ ] Bid-ask edge note appears in Telegram when triggered
- [ ] Vault logging enabled in `03-Strategies/Defi-Monitor/`
- [ ] No duplicate alerts within 5min window

## Lessons Learned (For Future Sessions)

1. **Named patterns beat ad-hoc solutions** — saying "add debounce logic" is vague; "stateful alert monitoring with tiered alerts" is a transferable skill.
2. **State file location matters** — keep alongside other script state, not in vault (vault sync could race).
3. **Always provide a state template** — copy-paste boilerplate reduces errors.
4. **Separate concerns:** debounce logic ↔ alert formatting ↔ vault logging. Each can be unit-tested.
5. **Document the "why" in case studies** — future agents need to know *why* 5min was chosen, not just that it is.

## Forward Hook

This pattern will next be applied to:
- **LFJ range monitor** (currently `lp-range-monitor-v2.py`) — same debounce for range breaches
- **Wallet health checker** — low-balance alerts with 10min confirmation
- **Milestone cross-checker** — DeFi tier transitions need confirmation too

**This is just the beginning** of a coordinated, stateful monitoring fabric across the AAE stack.
