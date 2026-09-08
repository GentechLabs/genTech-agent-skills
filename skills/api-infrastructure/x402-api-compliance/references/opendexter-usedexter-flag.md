# OpenDexter listing — the `X402_USE_DEXTER=1` gateway flag (Aug 16 2026)

## The core rule (why a "successful" settlement didn't list us)

**A settlement only lists you on the platform whose facilitator it went through.**
Separate facilitators = separate catalogs. OpenDexter (open.dexter.cash) auto-catalogs
APIs that settle through **Dexter's** facilitator (`x402.dexter.cash`) — NOT CDP, NOT
GoPlausible, NOT PayAI. Settling through CDP (the default for Base) lands the payment
on-chain but never catalogs you on OpenDexter.

## The gateway flag

The GenTech gateway's verify dispatch (`server.py`) routes Base (`eip155:8453`) proofs
to Dexter **only when `X402_USE_DEXTER=1`** is set in the gateway env:

```python
use_dexter = os.getenv("X402_USE_DEXTER", "0") == "1"
...
elif is_base and use_dexter:
    valid, reason = verify_proof_via_dexter(proof, price)   # → OpenDexter rail
else:
    # auto: CDP when a key exists, else simulation
    valid, reason = verify_proof_via_cdp(proof, price)
```

## How to enable it (safe — only affects Base)

```bash
# 1. Add the flag to the gateway env file
echo "X402_USE_DEXTER=1" >> /root/.hermes/profiles/gentech/.env

# 2. Restart so the running process re-reads .env
systemctl restart x402-api.service

# 3. Verify the RUNNING process picked it up (ground truth, not the .env file)
PID=$(systemctl show -p MainPID --value x402-api.service)
cat /proc/$PID/environ | tr '\0' '\n' | grep -E "^X402_USE_DEXTER=|^PAYMENT_VERIFY_MODE="
```

**Why it's safe:** the dispatch is per-proof-network. `X402_USE_DEXTER=1` only changes
the **Base** branch. Algorand proofs still → GoPlausible, Avalanche/XLayer still → PayAI.
So flipping it does NOT break the other rails. Verify after restart: 402 challenge still
returns `payment-required`, and `/.well-known/x402`, `/.well-known/x402.json`,
`/.well-known/x402-bazaar` all still return 200.

## The wallet funding gap (the actual blocker after the flag)

Even with the flag on, you need a **signable wallet holding USDC on Base** to settle
through Dexter. These frequently split across two wallets:

| Wallet | Address | Has key? | USDC on Base | Purpose |
|---|---|---|---|---|
| Owner (Jordan) | `0x7ebff...96a` | ❌ no key in env | **2.94 USDC** ✅ | revenue/settlement owner |
| Arb (GTA) | `0x3d117...eCb` | ✅ key in `secure/gentech-arb-wallet.json` | **0 USDC** ❌ | signable, needs funding |

**Unlock:** either (a) send ~$2 USDC on Base to the arb wallet `0x3d117` (key we hold),
or (b) provide the private key for the owner wallet `0x7ebff` (has 2.94 USDC). Then run
`self-settle.mjs` against our own endpoint → settles through Dexter → auto-cataloged →
verify via `capabilitySearch` after ~24h (indexing lags, do NOT re-settle to force it).

## Verify listing (read-only, free)

```js
import { capabilitySearch } from "@dexterai/x402-core";
const r = await capabilitySearch({ query: "gentechlabs" });  // OBJECT, not string
// listed if any strongResults/relatedResults url contains "gentechlabs.net"
```

`strongResults: []` for `gentechlabs` / `api.gentechlabs.net` / `gentech` = NOT cataloged.

## The facilitator → platform → rail → wallet map (keep current)

| Facilitator | Catalogs | Gateway verify path | Status |
|---|---|---|---|
| Dexter (`x402.dexter.cash`) | OpenDexter | `verify_proof_via_dexter` (needs `X402_USE_DEXTER=1`) | ✅ enabled Aug 16 |
| CDP (Coinbase) | Agentic.Market, CDP Bazaar | `verify_proof_via_cdp` | ⚠️ CDP indexing gap (#2112/#3045) — settled but NOT indexed |
| GoPlausible | GoPlausible Bazaar, Algorand x402 Challenge | `verify_proof_via_goplausible` (AVM) | ✅ live |
| PayAI | PayAI Bazaar, OrbitX402, xPay | `verify_proof_via_payai` | ✅ wired |

**Do NOT burn settlements on CDP Bazaar** — it's a documented platform indexing gap, not
a config issue. Pivot to x402scan (non-CDP discovery via `/.well-known/x402` + OpenAPI)
and OpenDexter (Dexter rail) as the reliable listing paths.
