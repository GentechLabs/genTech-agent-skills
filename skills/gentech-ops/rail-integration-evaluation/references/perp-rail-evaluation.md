# Perp / CLOB derivative rail evaluation recipe

Use this when Jordan shares a perps/DEX front end (Pangolin, Hyperliquid UI, dYdX, etc.) and
asks whether it is a usable treasury rail and what markets are available.

## 1. Front end vs engine

Most crypto perp interfaces are skins over a clearing engine. The evaluation target is the
engine, not the front end.

- Read the front end's docs / about page for "powered by" language.
- Search the engine name in the vault before researching.
- Verify the engine's own positioning: Orderly says *"no official front end; builders create
  DEXes on top."*

## 2. Collateral and chain fit

The single biggest convenience factor is whether the rail uses an asset and chain we already
hold.

| Question | How to check |
|----------|--------------|
| Deposit token | Read the vault contract; call `token0()` / `asset()` / `collateralToken()` |
| Is it native USDC we hold? | Compare token address to our known USDC on that chain |
| Chain reachable without bridge? | Same chain as our wallet / dry-powder reserve |
| Gas model | Gasless order signing vs on-chain gas per order |

Orderly Avalanche vault: `0x816f722424b49cf1275cc86da9840fbd5a6167e9`, native USDC
`0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E`.

## 3. Contract verification

A multi-chain engine may claim a deployment that is not actually live. Verify with on-chain
bytecode, not docs prose.

```bash
# compare bytecode across chains
for chain in avalanche base optimism; do
  python3 - <<PY
from web3 import Web3
url={"avalanche":"https://api.avax.network/ext/bc/C/rpc","base":"...","optimism":"..."}[$chain]
w3=Web3(Web3.HTTPProvider(url, request_kwargs={"headers":{"User-Agent":"GenTech-Steward/1.0"}}))
addr="0x816f722424b49cf1275cc86da9840fbd5a6167e9"
print(f"{$chain}: {len(w3.eth.get_code(addr))} bytes")
PY
done
```

If the engine exposes an MCP, also check `chainId` in the MCP response against the on-chain
`eth_chainId`.

## 4. Market coverage

Fetch the active market list from the engine's public API. For Orderly:

```bash
curl -s "https://api.orderly.org/v1/public/markets" | python3 -c "
import sys,json
d=json.load(sys.stdin)['data']['markets']
for m in d:
    if m.get('status')=='TRADING':
        print(m['symbol'], m.get('max_leverage'))
"
```

Cross-reference with our buy list and produce:
- Which buy-list assets have perps
- Which do not (and why — e.g. COQ has no perp on Orderly)
- RWA / macro coverage if relevant

## 5. Funding rate — sustained average, not snapshot

A single funding reading is noise. Report the distribution over a window.

```bash
curl -s "https://api.orderly.org/v1/public/funding_rate/history?symbol=PERP_AVAX_USDC&page_size=100" | python3 -c "
import sys,json
rows=json.load(sys.stdin)['data']['rows']
vals=[float(r['funding_rate'])*24*365*100 for r in rows]
print(f'n={len(vals)} avg={sum(vals)/len(vals):.2f}%/yr positive={sum(1 for v in vals if v>0)}/{len(vals)} max={max(vals):.2f}%')
"
```

Report:
- Window length and count of periods
- Sustained annualised average
- Positive/negative ratio
- Instantaneous high (with warning that it is a snapshot)

## 6. Depth and fees at real size

Probe the orderbook at the amount we would actually deploy, not a fantasy size.

```bash
curl -s -X POST -H "Content-Type: application/json" "https://api.orderly.org/v1/public/query" \
 -d '{"type":"orderbook","symbol":"PERP_AVAX_USDC"}' | python3 -c "
import sys,json
d=json.load(sys.stdin)['data']
mid=float(d['mid_price'])
for side in ('asks','bids'):
    rows=d.get(side,[])
    if not rows: continue
    best=float(rows[0]['price'])
    for need in (146,500,1000):
        eaten=0.0; px=best
        for r in rows:
            p=float(r['price']); q=float(r['quantity'])
            if eaten+q*p>=need: px=p; break
            eaten+=q*p
        slip=(px/best-1)*100 if side=='asks' else (1-px/best)*100
        print(f'{side} ${need} -> {px}  {slip:.3f}% from best')
"
```

Also fetch the fee schedule and compute round-trip taker cost for the planned leverage.

## 7. Risk surface

Check before calling a perp rail deployable:

- **Open interest** — total and for the specific market
- **Liquidation** — isolated vs cross, maintenance margin, stop availability
- **KYC / gating** — whether an account or API key is required
- **Withdrawal path** — how collateral returns to our wallet

## 8. Cash-and-carry sizing

When funding is persistently positive, the delta-neutral play is short perp + long spot.

```
gross_annual = position_size * leverage * avg_funding_rate
round_trip_cost = position_size * taker_fee_rate * 2
net_first_order = gross_annual - round_trip_cost - estimated_liquidation_risk_premium
```

At very small sizes the gross can be smaller than the operational attention cost. State that
honestly rather than annualising to a large-sounding percent.

## 9. Verdict shape

- **🟢 Deploy candidate** — same-chain collateral, real depth, fee < 10% of expected annual
  funding, OI can absorb size, no KYC blocker.
- **🟡 Watch / wrong size** — rail is real but the book is too small for the mechanism to
  matter today; set a re-review trigger (e.g. when weekly cadence reaches $X deployed).
- **🔴 Not a rail** — wrong chain, no programmatic surface, requires wrapped asset we do not
  hold, or engine docs omit the chain that the contract surface must prove.
