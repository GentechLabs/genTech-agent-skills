# API Health Audit + Placeholder Fix (worked recipe, Aug 3 2026)

Goal: find every GenTech API that looks "live" but returns placeholder/dead data,
then wire real data in. A healthy systemd service + green health endpoint + correct
402 challenge can ALL pass while the paid data is hardcoded zeros.

## Why it matters

Placeholder endpoints sit on the x402 Bazaar/registry looking online, accept
payments, but return garbage → cannot convert, occupy dead surface area on the
fee-earning rail. This is a top reason for "$0 traction despite 10K visitors."

## Audit method (run this, don't trust systemd)

1. Enumerate every running API service:
   ```bash
   systemctl list-units --type=service --state=running | grep -iE "api|backend|gateway"
   ```

2. Find each service's working dir + source:
   ```bash
   systemctl cat <svc>.service | grep -E "ExecStart|WorkingDirectory"
   ```

3. Grep the source for the smoking gun (hardcoded stub):
   ```bash
   grep -rn "placeholder\|source.*placeholder\|return {}\|return \[\]" <api-dir>
   ```
   - `{"price": 0.0, "source": "placeholder"}` → dead
   - `{"ethereum": 0, "base": 0, "polygon": 0}` → dead
   - `{"score": 0, "level": "unknown"}` → dead
   - `{"deals": [], "count": 0}` → dead (stub returning empty list)

4. Probe the ACTUAL data endpoints, not just health:
   ```bash
   curl -s "http://localhost:<port>/v1/<data-endpoint>"
   # eyeball body: price:0.0 / deals:[] / score:0 = red flag
   ```

5. For x402 gateways (FastAPI with redirects), follow the redirect + inspect the
   backend source for a REAL external call:
   ```bash
   curl -sL "http://localhost:<port>/v1/<service>"   # 307 → 402 challenge = correct
   # then check the backend .py calls a real source:
   grep -iE "https://|dexscreener|rpc|8004scan|magiceden" /root/gentechlabs/services/<svc>.py
   ```

## Findings (Aug 3, 2026)

| Service | Port | Data endpoint | Verdict | Root cause |
|---|---|---|---|---|
| deal-tracker-api | 8080 | `/v1/deals?title=` | ❌→✅ FIXED | Stub returned `[]`; engine existed but not wired |
| crypto-price-api | 8082 | `/v1/price/{symbol}` | ❌ | Hardcoded `price:0.0` |
| gas-price-api | 8084 | `/v1/gas` | ❌ | Hardcoded all-zero gas prices |
| token-security-api | 8086 | `/v1/score/{mint}` | ❌ | Hardcoded `score:0`; duplicated Rugcheck engine |
| rugcheck-api | 8088 | `/v1/score/{mint}` | ✅ | Real Solana scoring, proper 402 |
| x402 backends (agent_discovery, defi_lp_analytics, wallet_analysis, nft_search, treasury_defender, lineage_guard) | 8092-8096 | via gateway | ✅ | All call real sources (8004scan, DexScreener, Solana RPC, Magic Eden, Base RPC) |

## Fix paths

- **crypto-price** → use `crypto-price-fetch` skill / CoinGecko fallback chain
- **gas-price** → Etherscan gas oracle or live RPC gas estimation
- **token-security** → REUSE the already-working Rugcheck engine (port 8088) instead of duplicating
- **deal-tracker** → wire the existing `deal_tracker.py` CheapShark engine (done Aug 3)

## Reuse-not-rewrite rule

Before building a new data endpoint, check for an existing working engine/service
that already does the job. token-security duplicated Rugcheck; deal-tracker had a
working CheapShark engine sitting one directory over, unwired.

## Adding a new endpoint to deal-tracker (worked example)

The engine lived in `10-Labs/deal-tracker/deal_tracker.py` (sibling of the API dir
`10-Labs/deal-tracker-api/`). Wire it in with a `sys.path` insert in the new module:

```python
import sys
_ENGINE_DIR = "/root/vaults/gentech/10-Labs/deal-tracker"
if _ENGINE_DIR not in sys.path:
    sys.path.insert(0, _ENGINE_DIR)
from deal_tracker import CheapSharkClient
```

Then expose endpoints in `api/server.py` via `from . import games`. Restart the
service, verify with a real curl, write pytest cases that point the price-watch
store at a temp file (`games.WATCH_FILE = tempfile.mktemp()`) so tests don't
pollute prod data.

## Verification after restart

```bash
systemctl restart <svc>.service && sleep 3
curl -s "http://localhost:<port>/v1/<data-endpoint>"   # must return REAL data
pytest <test-file> -q                                    # all pass
```

## Registry discipline

Any service change (new endpoint, fixed endpoint, price) → update
`marketplace-listings-registry.md` row AND prompt Jordan to confirm. New service →
append a row.
