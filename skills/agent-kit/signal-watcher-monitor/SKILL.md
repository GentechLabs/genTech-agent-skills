---
name: signal-watcher-monitor
description: "Pattern for two independent cron jobs that communicate through a JSON state file bridge: a Signal cron generates entries/exits, a Watcher cron monitors conditions, scans external data, and alerts on threshold breaches. Used for autonomous position monitoring, event-driven alerts, and condition-based execution."
category: agent-kit
version: 2.0.0
author: Gentech
tags: [cron, monitoring, signals, automation, agentic-trading, pair-pattern]
---

# Signal + Watcher Monitoring Pair

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────────┐
│   SIGNAL CRON    │     │   WATCHER CRON       │
│   (e.g. 7AM/7PM) │     │   (e.g. every 30min)  │
│                   │     │                       │
│ • Generate entry  │────▶│ • Read current state  │
│ • Read market     │     │ • Check conditions    │
│ • Determine dir   │     │ • Scan external data  │
│ • Write position  │     │ • Alert on breaches   │
│   to JSON bridge  │     │ • Update position     │
└─────────────────┘     └───────────────────────┘
         │                         │
         └─────────┬───────────────┘
                   ▼
        ┌─────────────────────┐
        │   STATE BRIDGE       │
        │   (JSON file)        │
        │                      │
        │  symbol, direction,  │
        │  entry_price,        │
        │  stop_loss_pct,      │
        │  take_profit_pct,    │
        │  last_price,         │
        │  last_checked        │
        └─────────────────────┘
```

## When to Use

- You have a cron that generates periodic signals (entries/exits) and need continuous monitoring between them
- You want a news-aware "watchdog" that flags thesis-breaking events without human polling
- You need to separate concerns: one cron for data analysis + signal generation, another for real-time monitoring
- The two jobs have different cadences (signal: twice daily, watcher: every 30 min)

## Key Design Decisions

### 1. JSON File Bridge (Not a Database)

The signal and watcher communicate through a simple JSON file. No database, no message queue, no API call between them.

**Why this works:**
- Both cron jobs run as `no_agent=True` scripts — zero LLM token overhead
- JSON is human-readable for debugging
- The file is the source of truth for "what position is open?"
- No network dependency between the two jobs

**The bridge schema:**
```json
{
  "symbol": "BTC",
  "direction": "LONG",
  "entry_price": 63925.08,
  "stop_loss_pct": 5,
  "take_profit_pct": 8,
  "leverage": "3x",
  "entered_at": "2026-07-25T07:00:00Z",
  "signal_source": "Tradesta 7AM ET",
  "reason": "Relief bounce in fear regime",
  "last_price": 64006.00,
  "last_checked": "2026-07-25T12:04:00Z"
}
```

### 2. Watcher is Stateless (Except the Bridge)

The watcher reads the bridge file at every tick. It does not maintain in-memory state. This means:
- If the watcher crashes mid-tick, it re-reads the bridge file on restart
- If the signal updates the bridge mid-tick, the watcher picks up the new state next tick
- No race conditions — the bridge file is write-atomic (small JSON)

### 3. News Awareness is Built Into the Watcher

The watcher's key differentiator from a simple price-checking bot is that it scans external news sources for thesis-breaking headlines.

**Sources to scan:**
- CryptoPanic (free tier, no API key needed)
- Google News RSS (crypto/macro keywords)
- Yahoo Finance RSS (macro/economic news)
- Future: Exa neural search (paid, deeper)

**Keyword-based thesis break detection:**
- Long position: flag on "hack, crash, ban, sanction, regulation, investigation, fraud"
- Short position: flag on "approval, ETF, partnership, adoption, institution, ATH"

## Implementation Template

### Signal Cron (generates entries)

```python
#!/usr/bin/env python3
"""Signal generator — runs on schedule, writes position file if entry signal fires."""

import json, os
from datetime import datetime, timezone

BRIDGE_PATH = "/path/to/position_bridge.json"
SIGNAL_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_signal() -> dict:
    """Your signal logic here — returns {direction, leverage, reason, entry_price} or None for SKIP."""
    # ... market analysis, fear/greed, price action ...
    pass

def write_bridge(signal: dict, price: float):
    """Write position file when signal fires."""
    if signal["direction"] in ("LONG", "SHORT") and signal["leverage"] > 0:
        bridge = {
            "symbol": signal["symbol"],
            "direction": signal["direction"],
            "entry_price": price,
            "stop_loss_pct": 5,
            "take_profit_pct": 8,
            "leverage": f"{signal['leverage']}x",
            "entered_at": datetime.now(timezone.utc).isoformat(),
            "signal_source": "MySignal",
            "reason": signal.get("reason", ""),
            "last_price": price,
            "last_checked": datetime.now(timezone.utc).isoformat(),
        }
        with open(BRIDGE_PATH, "w") as f:
            json.dump(bridge, f, indent=2)
        print(f"Position opened: {bridge['direction']} {bridge['symbol']} @ ${price:,.2f}")
    else:
        # SKIP — clear any existing position
        if os.path.exists(BRIDGE_PATH):
            os.remove(BRIDGE_PATH)
        print("Signal: SKIP — no position opened.")

def main():
    signal = generate_signal()
    write_bridge(signal, signal.get("entry_price", 0))
```

### Watcher Cron (monitors position)

```python
#!/usr/bin/env python3
"""Position watcher — runs frequently, alerts on threshold breaches or thesis-breaking news."""

import json, os, subprocess, re, urllib.request
from datetime import datetime, timezone

BRIDGE_PATH = "/path/to/position_bridge.json"

def load_position() -> dict:
    if os.path.exists(BRIDGE_PATH):
        try:
            with open(BRIDGE_PATH) as f:
                return json.load(f)
        except:
            pass
    return {}

def get_current_price(symbol: str) -> dict:
    """Fetch from CoinGecko, BlockRun, or your price source."""
    pass

def get_fear_greed() -> dict:
    """Fetch Fear & Greed Index."""
    pass

def fetch_breaking_news() -> list:
    """Scan multiple RSS/API sources for recent headlines."""
    pass

def check_thesis_breakers(headlines: list, direction: str) -> list:
    """Flag headlines matching bearish/bullish keywords based on position direction."""
    pass

def check_stop_loss(pos: dict, current_price: float) -> dict:
    """Compare current price to entry + stop/take-profit thresholds."""
    pass

def main():
    position = load_position()
    if not position:
        print("No open position. Idle.")
        return
    
    # Fetch data
    price = get_current_price(position["symbol"])
    fear = get_fear_greed()
    news = fetch_breaking_news()
    flagged = check_thesis_breakers(news, position["direction"])
    stop_check = check_stop_loss(position, price)
    
    # Update bridge with latest price
    position["last_price"] = price
    position["last_checked"] = datetime.now(timezone.utc).isoformat()
    with open(BRIDGE_PATH, "w") as f:
        json.dump(position, f, indent=2)
    
    # Generate alert if needed
    if stop_check["triggered"] or flagged:
        print(generate_alert(position, price, fear, stop_check, flagged))
    else:
        # Quiet — nothing to report
        pass

if __name__ == "__main__":
    main()
```

### Cron Job Setup (Hermes)

```bash
# Signal — runs 7 AM and 7 PM
cronjob(action='create',
        name='My Signal',
        script='mysignal.py',          # relative to ~/.hermes/scripts/
        schedule='0 7,19 * * *',
        no_agent=True,                  # script-only, no LLM
        deliver='telegram:-1000000000')

# Watcher — runs every 30 min
cronjob(action='create',
        name='My Watcher',
        script='mywatcher.py',
        schedule='*/30 * * * *',
        no_agent=True,
        deliver='telegram:-1000000000')
```

The bridge file path should resolve to a shared directory both scripts can access. Use `os.path.dirname(os.path.abspath(__file__))` scoped to one of the script directories, or a fixed absolute path like `/root/.hermes/profiles/gentech/scripts/position_bridge.json`.

If using symlinks (repo code linked into hermes scripts dir), the `__file__` path resolves to the symlink location, not the target — this ensures the bridge file stays in the hermes scripts directory where both cron jobs can find it.

## Pirate Pitfalls

**1. Bridge file path mismatch.** Signal writes to path A, watcher reads from path B. Debug: add a log line printing the resolved path.

**2. Watcher runs even when no position is open.** Check for empty bridge file before doing work. Early return saves API calls and compute.

**3. News API rate limits.** Three RSS sources in one watcher tick can trigger rate limiting. Spread them across ticks or catch exceptions gracefully.

**4. Over-alerting.** If every watcher tick reports "no material change," the user ignores the alerts. Only speak when there's something to say — threshold breach, thesis-breaking news, or position-status change. Idle ticks should produce zero output (empty stdout = silent delivery with `no_agent=True`).

**5. News keyword false positives.** "hack" in "hackathon" or "crash" in "crash course" triggers false thesis-break alarms. Use word-boundary regex: `r'\bhack\b'` not keyword substring.

**6. Position file stale when watcher misses a tick.** If the watcher cron fails for 30 min, the position file is still valid on next tick — the watcher is stateless by design. No special recovery needed.

## Reference Implementation

The full working implementation of this pattern is at `ProtoJay4789/gentech-treasury-trader` on GitHub:

- `src/tradesta_signal.py` — Signal generator (Fear & Greed + price action → direction + leverage)
- `src/tradesta_watcher.py` — Position watcher with news awareness and stop-loss monitoring
- `tradesta_position.json` — Auto-generated bridge file

Key metrics from production (Jul 25, 2026):
- Signal runs: 2x daily (7 AM / 7 PM ET)
- Watcher runs: every 30 min
- Price source: CoinGecko (free, fast)
- News sources: CryptoPanic + Google News + Yahoo Finance RSS
- Alert triggers: stop-loss (5%), take-profit (8%), thesis-breaking news headlines
- Bridge file: self-clearing (deleted on SKIP signal)

## Extended Pattern — Three-Cron System (Signal + Watcher + Data Scanner)

The original two-cron pattern can be extended with a **third cron** that generates independent data as its own product:

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ GTA Signal   │    │ GTA Watcher  │    │ GTA Arb      │
│ (7AM/7PM)    │    │ (every 30m)  │    │ Monitor (1h) │
│              │    │              │    │              │
│ Direction    │───▶│ Position     │    │ Perp/Spot    │
│ + Leverage   │    │ + News/Macro │    │ Basis Scan   │
│ + Fear/Greed │    │ + Stop-Loss  │    │              │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌──────────────────────────────────────────────────────┐
│              DATA PRODUCTS LAYER                       │
│  • GTA Arb API (x402 pay-per-call, $0.02/req)         │
│  • Position Tracker (P&L every 60 min)                │
│  • Telegram reports (hourly/daily digest)              │
└──────────────────────────────────────────────────────┘
```

### When to Add a Third Cron

- You have a data source that generates independent value (not position-specific)
- The data is latency-sensitive enough to warrant its own cadence
- The third cron's output can be monetized independently (API, feed, alert)

### Data API Monetization Pattern

The third cron's data can be exposed as an HTTP API with x402 payment gate. The monitor writes a state file on each tick; a persistent Python HTTP server reads it on each request; nginx proxies with TLS.

**Confirmed** (Jul 25, 2026): `api.gentechlabs.net/arb` serves Hyperliquid vs Coinbase basis data via nginx → port 8081 Python server.

### VPS Geo-Bypass Pattern

When the data source is geo-restricted from the user's location:

1. **Run the cron on a VPS with non-US IP** — bypasses frontend geo-blocks.
2. **Access the protocol at the chain/API level**, not the website.
3. **Use agent wallet keys** (trade-only, cannot withdraw).
4. **Use direct curl with `--max-time 8`** — SDKs often lack timeouts and hang.

**Hyperliquid pitfall**: Python SDK uses `requests.post()` with no default timeout. Replace with curl + Content-Type header. Without `Content-Type: application/json` the API returns empty response — no error, no data.

### Wallet Onboarding Flow (Client-Facing Arb Service)

1. Generate wallet (secrets.token_bytes → eth_account), save key at `~/.hermes/profiles/gentech/secure/<name>.json` chmod 600.
2. Share deposit address on Base. $0.50 ETH needed for gas.
3. Bridge USDC to perp exchange, place both legs when spread exceeds threshold.
4. Monitor P&L via cron (60 min cadence). Stop-loss: close if spread widens 50%+ against entry.

## References

- `cron-truth-layer` — Data freshness verification for cron jobs
- `message-length-discipline` — Telegram output limits for cron deliveries
