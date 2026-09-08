---
date: 2026-05-03
type: incident-protocol
severity: P0
domain: monitoring / state-management
status: published
---

# Multi-Script Monitoring Discrepancy Resolution Protocol

**Discovered:** 2026-05-03 during DeFi Milestone daily monitoring  
**Detected by:** YoYo (Strategies) — 4× daily monitoring run  
**Severity:** P0 — Systematic reporting divergence across scripts ($55 variance)  
**Status:** Resolved — protocol defined, tasks assigned, skills-capture published

---

## Symptom

Three monitoring scripts reporting **substantially different position values** for the same pool at identical timestamp:

| Script | Reported Position | Efficiency | Status |
|--------|------------------|------------|--------|
| `defi-milestone-summary.py` | $83.92 | 38.2% | ❌ Under-reporting |
| `defi-master-cron.py` | $138.92 | 66.3% | ⚠️ Over-reporting |
| `lp-position-reader.py` | $134.94 LP + $0.88 wallet = **$135.82** | 38.2% | ✅ Ground truth |

**Variance:** ~$55 (~40%) between extremes.

---

## Root Cause

### 1. State File Fragmentation Across HERMES Profiles
Scripts maintain independent state caches in different filesystem locations:
- `~/.hermes/scripts/` — Default global state
- `~/.hermes/profiles/<profile>/home/.hermes/scripts/` — Per-profile state (YoYo-specific, etc.)

**Result:** No single source of truth; scripts reading different `.lfj-*.json` files observe divergent snapshots.

### 2. Independent Implementation Logic
- `defi-master-cron.py` — Consolidated report; may include **pending DCA injection** or stale snapshot not yet on-chain
- `defi-milestone-summary.py` — Human-narrative snapshot; uses **different config range source** and **simplified efficiency calculation**
- `lp-position-reader.py` — On-chain position decoder; queries blockchain directly → verified balances

---

## Resolution Protocol (Executed 2026-05-03)

### Step 1 — Establish Ground Truth Hierarchy

```bash
# ALWAYS run in this order:
python3 lp-position-reader.py   # → USE THESE NUMBERS for vault Balance field
python3 defi-master-cron.py       # → USE for watchlist prices + volume metrics only
# defi-milestone-summary.py → Use ONLY for narrative boilerplate/template
```

**Priority:** On-chain decoded values > consolidated watchlist > narrative template.

### Step 2 — Vault Entry Number Authority
Balance field in vault entries **MUST match** `lp-position-reader.py` output exactly. Any deviation requires inline `Note:` explaining variance.

### Step 3 — Discrepancy Thresholds
If any two sources disagree by:
- **>$0.50** in position value, OR
- **>5 percentage points** in efficiency

→ Log incident in Green Room and **defer vault update** until resolved.

### Step 4 — IL Spike Protocol
If `lp-position-reader.py` shows IL > threshold:
- Auto-flag vault entry with `🚨 Review` action
- Add rationale: "IL spiked to X% (>2% threshold); on-chain verification required"
- Strategy owner (YoYo) verifies oracle/settlement integrity before rebalance decision

---

## Follow-Up Tasks (Assigned 2026-05-03)

| Owner | Task | Status |
|-------|------|--------|
| DMOB | Symlink state files: `~/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-*.json` → `~/.hermes/scripts/` | 🚀 Pending |
| YoYo | Reconcile milestone ladder: `defi-master-cron.py` hardcodes `$5/$20/$55/$200` vs AAE config `$3/$5/$8/$10/...` | 🚀 Open |
| Desmond | Verify `defi-milestone-summary.py` reads config range from same source as `defi-master-cron.py` | 🚀 Open |

---

## Prevention Checklist (Daily Sync Integration)

During daily sync, BEFORE updating vault balance fields:

```bash
# 1. Ground truth check
python3 lp-position-reader.py > /tmp/ground-truth.json

# 2. Watchlist sanity check
python3 defi-master-cron.py > /tmp/watchlist.json

# 3. Compare numbers (implement in daily sync pre-flight)
# If variance > $0.50 OR efficiency diff > 5pp → flag incident

# 4. Only after validation, write vault entry with ground truth numbers
```

**Rule:** Never trust a single monitoring script in isolation. Always triangulate.

---

## Related Incidents

- **2026-05-03** — DeFi Milestone Tracker IL spike coincident with script divergence; both traced to state fragmentation + pending DCA injection in master cron.
- **Skills-capture published:** `09-Green Room/skills-captures/defi-monitoring-script-discrepancy-resolution.md`

---

**This is just the beginning of systematic monitoring hygiene.**  
— Gentech, 2026-05-03
