# Price Feed & State Patterns

Common patterns for building agents that monitor market data during cron sessions. Derived from the Dry Powder Mode crash detection engine (Jul 2026).

## Price Feed Fallback Chain

When fetching cryptocurrency prices, never depend on a single source. Use a fallback chain:

```
Primary:   BlockRun Price API (free, crypto/fx/commodity)
Fallback:  DexScreener via BlockRun DEX (free, any chain)
Fallback:  CoinGecko (free, no key needed, rate-limited)
```

**Implementation pattern:**
```python
def fetch_price(symbol: str, coingecko_id: str) -> dict:
    """Try each source in order. Raise only if all fail."""
    # Primary: BlockRun
    try:
        url = f"https://api.blockrun.ai/v1/price?category=crypto&symbol={symbol}-USD"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if isinstance(data, dict) and "price" in data:
                return {"symbol": symbol, "price": float(data["price"]),
                        "change_24h": float(data.get("change_24h_pct", 0)),
                        "source": "blockrun"}
    except Exception:
        pass

    # Fallback: DexScreener (free, no key)
    try:
        url = f"https://api.blockrun.ai/v1/dex/search?query={symbol}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            pairs = data.get("pairs", [])
            if pairs:
                p = pairs[0]
                return {"symbol": symbol, "price": float(p.get("priceUsd", 0)),
                        "change_24h": float(p.get("priceChange", {}).get("h24", 0)),
                        "source": "dexscreener"}
    except Exception:
        pass

    # Fallback: CoinGecko (free, rate-limited)
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=usd&include_24hr_change=true"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            coin = data.get(coingecko_id, {})
            if "usd" in coin:
                return {"symbol": symbol, "price": float(coin["usd"]),
                        "change_24h": float(coin.get("usd_24h_change", 0)),
                        "source": "coingecko"}
    except Exception:
        pass

    raise RuntimeError(f"Could not fetch price for {symbol}")
```

### When to Use Each Source

| Source | Best For | Limit | Free? |
|--------|----------|-------|-------|
| BlockRun Price | Realtime quote, any asset class (crypto/fx/stock) | 200 calls/day free | Yes |
| BlockRun DEX | DEX pair discovery, on-chain liquidity | Unlimited | Yes |
| CoinGecko | Broad coverage, historical, no API key | 10-30 calls/min | Yes |

## Disk-Backed State with Atomic Writes

For agents that persist state across VPS reboots:

```python
import json
from pathlib import Path

STATE_DIR = Path(os.path.expanduser("~/.hermes/state"))
STATE_PATH = STATE_DIR / "agent-state.json"

def load_state(defaults: dict) -> dict:
    """Load state from disk, returning defaults on missing/corrupt file."""
    if STATE_PATH.exists():
        try:
            with open(STATE_PATH) as f:
                data = json.load(f)
                merged = dict(defaults)
                merged.update(data)
                return merged
        except (json.JSONDecodeError, OSError):
            pass
    return dict(defaults)

def save_state(state: dict) -> None:
    """Atomic write via temp file + rename. Survives partial writes."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    tmp.replace(STATE_PATH)  # atomic on POSIX
```

**Key design choices:**
- `load_state` never raises — returns defaults on any error (corrupt file, disk full, etc.)
- `save_state` uses temp + replace — prevents half-written files
- Merge pattern (`dict(defaults).update(data)`) — new fields get defaults on schema migration
- State dir under `~/.hermes/state/` — standard location, survives profile restarts

## Circuit Breaker Pattern

For agents that could oscillate (detect → act → detect → act again):

```python
# In the agent's poll loop:
state["circuit_breaker_count"] += 1
state["circuit_breaker_date"] = today_str

if state["circuit_breaker_count"] >= 5:
    print("⛔ Circuit breaker engaged! Max 5 triggers/day.")
    state["status"] = "circuit_breaker"
    save_state(state)
    return state  # no action taken

# Reset daily
if state.get("last_trigger_date") != today_str:
    state["triggers_today"] = 0
    state["last_trigger_date"] = today_str
```

**When to use:** Any agent that (a) polls on a schedule, (b) can trigger actions autonomously, and (c) has a risk of false positive oscillation (crash detection, rebalancing, etc.).

## Config Auto-Creation with Default Merge

```python
DEFAULT_CONFIG = {
    "mode": "advisory",
    "threshold": 50,
    "poll_interval_seconds": 300,
}

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
            merged = dict(DEFAULT_CONFIG)
            merged.update(cfg)
            return merged
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)
    return dict(DEFAULT_CONFIG)
```

This ensures:
- Config is always present (auto-created with defaults)
- New fields added to defaults merge into existing configs without breaking them
- The agent never crashes on first run due to missing config

## Watch Mode with Dynamic Polling

```python
def watch(config, state):
    interval = config["poll_interval_seconds"]
    while True:
        state = poll(config, state)
        # Poll faster when watching
        if state.get("status") == "watching":
            interval = config["watch_poll_interval_seconds"]
        else:
            interval = config["poll_interval_seconds"]
        time.sleep(interval)
```

Use this pattern when an agent needs to:
- Poll slowly during normal conditions (saves API credits, CPU)
- Speed up when something interesting is happening
- Never block indefinitely -- always returns to the event loop

## Status Report Format

```python
def show_status(config, state):
    print("=" * 50)
    print("  AGENT NAME — Status Report")
    print("=" * 50)
    print(f"  Mode:        {config['mode']}")
    print(f"  Status:      {state['status']}")
    print(f"  Last Signal: {state.get('last_signal', 'N/A')}")
    print(f"  Last Check:  {state.get('last_checked', 'never')}")
    print(f"  Triggers Today: {state.get('triggers_today', 0)}")
    print(f"  Pool:        {config['pool_address'][:20]}...")
    print(f"  Chain:       {config['chain']}")
    print(f"  Threshold:   {config.get('crash_threshold', 'N/A')}")
    print("=" * 50)
```

Aim for: fits in one screen, key operational fields only, no debug noise. The user/operator needs to know mode, status, and last action — nothing else.
