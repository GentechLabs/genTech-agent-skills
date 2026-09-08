# Facilitator → Platform → Rail → Wallet Map (Aug 16, 2026)

**Purpose:** Track which x402 facilitator settles which platform, which rail (chain) each
uses, and which wallet needs funding + how much. Prevents the "settled but not listed"
trap — a settlement only catalogs you on the platform whose facilitator it went through.

## The core rule
**A settlement only lists you on the platform whose facilitator it settled through.**
Separate facilitators = separate catalogs. Settling through CDP does NOT list you on
OpenDexter, and vice versa.

## Facilitator → Platform map

| Facilitator | Platforms it catalogs | Our gateway verify path | Status |
|---|---|---|---|
| **CDP (Coinbase)** | Agentic.Market, CDP Bazaar | `verify_proof_via_cdp` (default for Base) | ⚠️ CDP indexing gap (#2112/#3045) — settled but NOT indexed |
| **Dexter** (`x402.dexter.cash`) | OpenDexter (open.dexter.cash) | `verify_proof_via_dexter` — gated behind `X402_USE_DEXTER=1` | ✅ ENABLED Aug 16 |
| **GoPlausible** | GoPlausible Bazaar, Algorand x402 Challenge | `verify_proof_via_goplausible` (AVM proofs) | ✅ LIVE (Algorand rail) |
| **PayAI** | PayAI Bazaar, OrbitX402, xPay | `verify_proof_via_payai` | ✅ wired |
| **RelAI** | RelAI marketplace | platform-side | ✅ registered |
| **APIHub** | APIHub | platform-side | ✅ registered |

## Rail (chain) → gateway config

| Chain | Gateway env | Verify path | Status |
|---|---|---|---|
| Base | `X402_NETWORKS=base` | CDP (or Dexter if `X402_USE_DEXTER=1`) | ✅ live |
| Algorand | `X402_NETWORKS=algorand`, `X402_PAYTO_ALGORAND=<addr>` | GoPlausible (AVM) | ✅ live + settled |
| Avalanche | `X402_NETWORKS=avalanche`, `X402_PAYTO_AVALANCHE=<addr>` | CDP | ✅ live |
| X Layer | `X402_NETWORKS=xlayer`, `X402_PAYTO_XLAYER=<addr>` | CDP | ✅ live |

**Current gateway state (verified Aug 16):** `PAYMENT_VERIFY_MODE=auto`,
`X402_NETWORKS=base,algorand,avalanche,xlayer`. `X402_USE_DEXTER=1` set + running.

## Wallet funding map

| Wallet | Address | Has key? | USDC on Base | Gas | Purpose |
|---|---|---|---|---|---|
| **Owner (Jordan)** | `0x7ebff...96a` | ❌ no key in env | **2.94 USDC** ✅ | — | Revenue/settlement owner |
| **Arb (GTA)** | `0x3d117...eCb` | ✅ key in `secure/gentech-arb-wallet.json` | **0 USDC** ❌ | 0.0002 ETH | Signable, needs funding |
| **Algorand** | `6IXPRMSYQBZSP2KIPH6BQ7MP4XN7VP6MWGHCLLF52K5R4IYCPA74TU2MTI` | ✅ key in `/root/.algorand/` | — (ALGO rail) | 55 ALGO | Algorand x402 Challenge |

## OpenDexter listing — the exact unlock (Aug 16)

**Goal:** get cataloged on OpenDexter (open.dexter.cash).

**Blocker:** OpenDexter only catalogs settlements through **Dexter's** facilitator. Our
gateway's Dexter path is gated behind `X402_USE_DEXTER=1` (was NOT set), so the Aug 12
self-settlement routed to CDP → wrong rail → not listed.

**Two steps:**
1. **Gateway:** set `X402_USE_DEXTER=1` in `.env` + restart `x402-api.service`
   (routes Base proofs to Dexter instead of CDP). ✅ **DONE Aug 16** — verified running
   process has `X402_USE_DEXTER=1`, 402 challenge intact, discovery all 200. Safe: only
   affects Base proofs; Algorand→GoPlausible, Avalanche/XLayer→PayAI unchanged.
2. **Wallet:** fund a signable wallet with ~$2 USDC on Base. Either:
   - (a) send ~$2 USDC to arb wallet `0x3d117...eCb` (key we hold), OR
   - (b) provide the private key for owner wallet `0x7ebff...96a` (has 2.94 USDC).

**Then:** run `self-settle.mjs` against our own endpoint → settles through Dexter →
auto-cataloged → verify via `capabilitySearch` after ~24h.

## Other platforms needing a funded signable wallet
- **Agentic.Market / CDP Bazaar** — blocked on CDP indexing gap (#2112/#3045), NOT wallet.
  Do NOT burn settlements until CDP fixes indexing.
- **x402scan** — non-CDP discovery via `/.well-known/x402` + OpenAPI (already 200). Check
  separately; may already be discoverable without settlement.
