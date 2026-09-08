# OpenDexter NOT Cataloged — Root Cause: X402_USE_DEXTER gating (Aug 16, 2026)

## The finding (confirmed live)

GenTech is still NOT cataloged on OpenDexter. `capabilitySearch({ query: "gentechlabs" })`,
`"api.gentechlabs.net"`, and `"gentech"` all return `strongResults: []` (only unrelated
results). The Aug 12 self-settlement did NOT list us.

## Root cause — the Dexter rail is gated behind X402_USE_DEXTER

The gateway ALREADY has a `verify_proof_via_dexter()` path (routes Base proofs to
`x402.dexter.cash`), but it is **gated behind `X402_USE_DEXTER=1`** in the verify dispatch.
When that env var is unset (the default), `auto` mode routes Base proofs to **CDP**, NOT
Dexter. So a self-settlement that "succeeds" (payment lands on-chain) can still fail to
catalog on OpenDexter because it settled on the **wrong rail**:

- **CDP** facilitator → catalogs **Agentic.Market** (and even that is broken — see the
  CDP platform gap incident log).
- **Dexter** facilitator → catalogs **OpenDexter**.
- They are **separate catalogs**. A CDP settlement never lists you on OpenDexter.

## Diagnostic order when "settled but not on OpenDexter"

1. Confirm the gateway's Dexter path is actually enabled:
   ```bash
   grep X402_USE_DEXTER /root/.hermes/profiles/gentech/.env
   cat /proc/<pid>/environ | tr '\0' '\n' | grep X402_USE_DEXTER   # running process = ground truth
   ```
   (A stale process may not have picked up a new .env value — same class of trap as the
   stale-CDP-credential pitfall.)
2. If unset, the settlement went to CDP → OpenDexter will never catalog it. Flip
   `X402_USE_DEXTER=1` in the .env, `systemctl restart x402-api`, re-verify the running
   process env, THEN re-settle through Dexter.
3. Verify cataloging with `capabilitySearch({ query: "api.gentechlabs.net" })` — expect a
   `strongResults` hit with `url` containing our host. Indexing lags ~24h; don't re-settle
   to force it (burns USDC).

## The wallet gap is still the funding blocker

| Wallet | USDC on Base | Key in env? |
|---|---|---|
| `0x7ebff` (owner) | ~2.9 USDC | NO |
| `0x3d117` (GTA arb) | ~0.001 USDC | YES |

The unlock is BOTH: (a) enable `X402_USE_DEXTER=1` AND (b) get ~$2 USDC into a signable
wallet (fund `0x3d117`, or provide the key for `0x7ebff`).

## How to verify cataloging (read-only, free)

```js
import { capabilitySearch } from "@dexterai/x402-core";  // NOT @dexterai/x402 (no main export)
const r = await capabilitySearch({ query: "api.gentechlabs.net" });  // object, not string
const strong = r?.strongResults || [], related = r?.relatedResults || [];
// listed if any result.url contains "gentechlabs.net"
```

Note: `@dexterai/x402` has no top-level export (ERR_PACKAGE_PATH_NOT_EXPORTED); use
`@dexterai/x402/client` or `@dexterai/x402-core` for `capabilitySearch`.
