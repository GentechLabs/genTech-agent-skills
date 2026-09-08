# LFJ/AAE Orchestration (Full)

> Absorbed from `defi-lfj-monitoring` skill. Script matrix, config locations, and SOP.

## Script Matrix

| Script | Purpose | Output | Frequency |
|--------|---------|--------|-----------|
| `defi-milestone-summary.py` | Daily executive snapshot | Markdown | Once daily |
| `defi-master-cron.py` | Consolidated watchlist + LP + DCA | Markdown + signals | 4× daily |
| `lp-aae-signal-monitor.py` | AAE signal generation | JSON + human | On-demand |
| `lp-unified-monitor.py` | Silent range + milestone monitor | SILENT or JSON | Every 5min |
| `lfj_monitor.py` | Price + wallet tracker | JSON | 4× daily |
| `lp-position-reader.py` | On-chain bin decoding | JSON | On-demand |
| `defi-lp-consolidated.py` | **Primary monitor** — alert-once | SILENT or Markdown | Every 10min |

## Config & State Files

**Config (milestone ladder, DCA rules):**
- Primary: `~/.hermes/scripts/.lfj-aae-config.json`
- Vault backup: `/root/vaults/gentech/03-Strategies/scripts/.lfj-aae-config.json`

**Position Tracker (primary source of truth for monitor):**
- `~/.hermes/scripts/.lfj-position-tracker.json` (main)
- `~/.hermes/profiles/gentech/scripts/.lfj-position-tracker.json` (cron context)

**⚠️ Config can drift from tracker.** Config is updated by rebalance handler; tracker may lag. Config wins for range/shape/balances.

**State (persistent across runs):**
- `~/.hermes/scripts/.lfj-position-state.json` — last price, alert flags, days in range
- `~/.hermes/scripts/.lfj-milestone-tracker.json` — cumulative fees, milestones hit
- `~/.hermes/scripts/.lfj-efficiency-trend.json` — efficiency history

## Standard Operating Procedure

### 1. Quick Health Check (<30s)
```bash
cd /root/vaults/gentech/03-Strategies/scripts
python3 defi-milestone-summary.py
```

### 2. Full Signal Analysis (<60s)
```bash
python3 lp-aae-signal-monitor.py
```
Extract: `current_tier_label`, `fee_efficiency`, `suggested_action`, `severity`

### 3. Consistency Verification
```bash
diff ~/.hermes/scripts/.lfj-aae-config.json      /root/vaults/gentech/03-Strategies/scripts/.lfj-aae-config.json
```

### 4. Deep Dive (if needed)
```bash
python3 lp-position-reader.py   # On-chain bin-level
python3 lfj_monitor.py          # DexScreener + wallet balances
```

## Critical Cross-Script Inconsistencies

1. **Milestone Ladder Divergence** — Different scripts use different tier thresholds ($3 vs $5 for Scout). Pick one and align.
2. **Fee Estimation Method** — Some hardcode fees, some estimate from volume, some use on-chain oracle. Standardize on TVL-weighted.
3. **Efficiency Calculation** — Different formulas across scripts. Agree on one.
4. **State File Location Fragmentation** — Multiple profiles write to different paths. Symlink or standardize.

## Cron Data Freshness Protocol

Cron jobs must run `lp-position-reader.py` FIRST, update config, THEN compose report. Without this, cron reports stale balance figures.

## Notification Policy (Jordan's Preference)

**Alert once per condition change. Stay silent otherwise.** Empty stdout = no Telegram delivery.

**Implementation:** Track `last_alerted_condition` in state. Fire alert only on:
1. New condition detected (5-min debounce)
2. Condition changes severity
3. Condition resolves then degrades
4. 1-hour cooldown elapsed

## Vault Entry Atomic Write Protocol

Use `scripts/atomic-vault-append.py` for destructive-safe append that:
1. Reads entire vault
2. Splits by `## YYYY-MM-DD Update` headers
3. Merges new entry with existing same-date block
4. Atomic `mv` to prevent partial writes

## LFJ-Specific RPC Call Sequence

1. Call `activeId()` → current active bin
2. Scan ±50 bins with `balanceOf(wallet, binId)`
3. For each bin with shares, `totalSupply(binId)` → share_pct
4. Price range from bin offsets using geometric formula

**Key selectors (hex, no 0x prefix):**
```
activeId:     0xdbe65edc
balanceOf:    0x00fdd58e
totalSupply:  0xbd85b039
```

## On-Chain Verification (Added Jun 22, 2026)

The primary monitor (`defi-lp-consolidated.py`) now verifies on-chain data before reporting:

1. **Reads defi-data.json** (on-chain reader output)
2. **Compares range/shape/amounts** against config files
3. **Auto-corrects** if drift >2¢ or shape mismatch
4. **Flags imbalanced positions** (>90% one token)
5. **Shows data age banner** if defi-data.json is >2h old

```
⚠️ RANGE MISMATCH: On-chain [6.1776–6.4039] vs Config [6.0400–6.1960]
  ✅ Auto-corrected: 6.0400–6.1960 → 6.1776–6.4039
```

**force_send flag:** Set `force_send: true` in `.lfj-defi-state.json` to override debounce and force a report.

## LP Shape Detector (GenTech Original)

Script: `/root/.hermes/profiles/gentech/scripts/lp-shape-detector.py`

Detects strategy shapes from on-chain bin distribution:
- **Curve:** Bell-curve, peak at center (range-bound markets)
- **Bid-Ask:** Liquidity at edges (volatile markets)
- **Spot:** Single bin (precision plays)
- **Asymmetric:** Skewed (directional bets)

Reads from `curveData.bins` in defi-data.json. Outputs shape classification with confidence %.

## Preflight Auto-Fix

The preflight script (`/root/.hermes/scripts/preflight.py`) now auto-fixes safe issues:
- **Vault sync:** Auto-commits uncommitted changes + pushes
- **Git state:** Auto-aborts stuck rebases, auto-switches detached HEAD to main
- **Position sync:** Auto-corrects config drift from position tracker

Pattern: Detect → Fix → Verify → Report

## Delegation & Routing

| Issue Type | Owner |
|------------|-------|
| Milestone ladder, efficiency formula | YoYo |
| State file persistence, profile paths | DMOB |
| Cron scheduling, alert routing | Gentech |
| Vault entry updates | Gentech |
