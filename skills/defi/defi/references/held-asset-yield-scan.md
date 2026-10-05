# Held-Asset Yield Scan

Scan for yield venues for assets the treasury **already holds or is built around**, not for the whole market. A general yield leaderboard surfaces 400% APYs on tokens we will never own; this narrows the search to the small set of assets the operator has chosen, and asks whether a new venue has appeared for one of them.

**When to use:**
- A held asset (e.g. TAO) is added to a new ecosystem or DEX.
- The operator wants to know if there is a better place to *put* what they already own.
- Adding yield discovery as a sibling to a rail/buy-list watch, not a replacement.

**Source:** DefiLlama yields API — `https://yields.llama.fi/pools` — free, no key, updated hourly.

---

## Standing filters

A pool is only an opportunity for this treasury if ALL of these are true:

1. **Every token in the pair is an asset we hold or are building around.**
   - A `WAVAX-USDC` pool qualifies because both legs are in the treasury set.
   - A `RANDOM-USDC` pool does NOT qualify, even at 4,000% APY, because `RANDOM` is not a held asset.
   - This is the most common false-positive path: matching on *any* shared symbol part produces hundreds of junk results.

2. **The chain is a rail we can actually reach.**
   - Avalanche, Solana, Ethereum, Base are the current rails.
   - A venue on a chain we cannot reach is a fact about someone else, not an opportunity.

3. **TVL is high enough to be real.**
   - Default floor: $250k. Below this, an APY is usually an artefact of thin liquidity or short-lived reward farming.

4. **APY is in a plausible band.**
   - Minimum: 3% — below this, gas and attention eat it.
   - Maximum sanity: 300% — above this, it is almost always emissions-priced-at-fantasy or a brand-new pool, not durable yield.

5. **Stablecoin pools carry a sanity warning.**
   - A stablecoin pool paying more than ~60% is a warning, not a yield. It usually means the peg is under stress or the reward token is inflating.

---

## Fee yield vs reward yield

DefiLlama splits `apy` into `apyBase` (real fees the pool earns) and `apyReward` (emissions someone is paying to attract liquidity).

| What you see | What it means | How to treat it |
|--------------|---------------|-----------------|
| High `apyBase`, low `apyReward` | The venue is actually earning fees. | Prefer. |
| High `apy`, high `apyReward` | Most of the return is a temporary subsidy. | Flag it; the yield will drop when the subsidy ends. |
| High `apy`, zero `apyBase` | Pure reward farming. | Usually ignore unless there is a specific strategy reason. |

**Sort by durability:** primary sort on `apyBase`, secondary on total `apy`. A list led by subsidy pools is a list of adverts.

---

## Silence doctrine

A yield scan that repeats itself every run is a scan nobody reads. Alert **only** when:

- A qualifying venue appears for the first time.
- A previously seen venue disappears.

Seed the watch state on first deployment so the cron starts quiet. Empty stdout means no message.

---

## Reference implementation sketch

```python
import json, urllib.request

HELD = {"AVAX", "WAVAX", "USDC", "USDT", "SOL", "BTC", "WBTC", "LINK", "TAO", "COQ", "ETH", "WETH"}
CHAINS = {"Avalanche", "Solana", "Ethereum", "Base"}
TVL_MIN = 250_000
APY_MIN = 3.0
APY_MAX_SANITY = 300.0
STABLE_SANITY = 60.0

req = urllib.request.Request("https://yields.llama.fi/pools", headers={"User-Agent": "Treasury/1.0"})
data = json.load(urllib.request.urlopen(req))

out = []
for r in data.get("data", []):
    sym = (r.get("symbol") or "").upper()
    chain = r.get("chain")
    apy = r.get("apy") or 0
    tvl = r.get("tvlUsd") or 0
    base = r.get("apyBase") or 0
    reward = r.get("apyReward") or 0
    stable = bool(r.get("stablecoin"))

    if chain not in CHAINS or tvl < TVL_MIN or apy < APY_MIN or apy > APY_MAX_SANITY:
        continue

    parts = {p.strip() for p in sym.replace("/", "-").split("-") if p.strip()}
    if not parts or not parts.issubset(HELD):
        continue

    flag = ""
    if stable and apy > STABLE_SANITY:
        flag = "stablecoin paying >60% is a warning, not a yield"
    if reward and base and reward > base:
        flag = f"{reward:.1f}% of this is reward emissions vs {base:.1f}% fee yield"

    out.append({
        "symbol": sym, "chain": chain, "project": r.get("project"),
        "apy": round(apy, 2), "apy_base": round(base, 2), "apy_reward": round(reward, 2),
        "tvl_usd": round(tvl), "flag": flag,
    })

out.sort(key=lambda x: (x["apy_base"], x["apy"]), reverse=True)
```

---

## Verification

After adding or changing the scan:

1. Run it dry and inspect the top result. If the top line is a 4,000% APY on a token you do not hold, the symbol filter is wrong.
2. Check that the number of "new" results is small (tens, not hundreds) for a narrow held-asset set.
3. Confirm the cron delivers nothing on the second run (state seeded, silence doctrine working).
