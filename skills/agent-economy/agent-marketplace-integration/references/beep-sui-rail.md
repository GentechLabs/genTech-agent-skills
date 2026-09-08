# Beep — Sui payment rail (greenlit Aug 14, 2026)

## Direction (Jordan, Aug 14)
Add a **Sui settlement rail** to the GenTech x402 gateway via **Beep** (agentic finance protocol,
`justbeep.it`, USDC-on-Sui, a402/x402). Jordan greenlit this as a queued build. **NOT a Monad rail** — Beep
is Sui-native.

## What Beep is
- Agentic finance protocol built **on Sui**: agent payments (a402/x402), agentic yield, "talk-to-money" AI.
- Non-custodial USDC-on-Sui settlement. Launch product: Agentic Yield (auto-compound stablecoin yield, Sui-native USDC).
- SDK: `github.com/beep-it/beep-sdk` (MIT, TypeScript monorepo). Packages: `@beep-it/sdk-core`,
  `@beep-it/checkout-widget`, `@beep-it/cli`, `packages/mcp`.
- Auth: `beep_pk_*` (publishable, browser-safe) + `beep_sk_*` (secret, server-side). Keys from app.justbeep.it.
- One-time payments only (no subscriptions/recurring). 402 flow: create invoice → HTTP 402 with `referenceKey`
  → poll until 200 (paid).

## Why it's NOT a drop-in network config line
Our gateway's `NETWORKS` dict works for EVM rails that verify ERC-3009 proofs. Sui settles **through Beep's API**,
not an ERC-3009 proof — so a Sui rail means a **new settlement backend** (Beep adapter), not a `sui:` config entry.

## Build plan (staged; blocked on keys)
1. Add `sui` network to x402 gateway manifest (Sui CAIP-2 + Sui-native USDC asset).
2. Wire a **Beep settlement adapter** using `@beep-it/sdk-core` into the gateway: `requestAndPurchaseAsset`
   (402 invoice) → poll status → verify paid → release response, mirroring our existing x402 release flow.
3. Tests: 402-on-unpaid, 200-after-payment, payment verification.
4. Ship behind `api.gentechlabs.net`.

## Blocker (human action, queued on Jordan's list)
Jordan must sign up at app.justbeep.it and grab a `beep_sk_*` (server) + `beep_pk_*` (publishable) key.
Once keys land, wire + test. This is a **human-signup-gated** build — same category as the 0G faucet,
so it sits on the after-work action list, not the autonomous lane.
