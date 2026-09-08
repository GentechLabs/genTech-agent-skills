# Agent Payment Rails — Chain Coverage (verified Aug 2026)

Quick reference for which payment/yield rail reaches which chain. Prevents proposing a rail for a chain it can't settle on.

## Beep (justbeep.it) — SUI-ONLY
- Beep = agentic finance protocol: a402/x402 payments + agentic yield, settled in **USDC-on-SUI** (Sui-native).
- SDK (`@beep-it/*`, github.com/beep-it/beep-sdk) is built on Sui. Keys: `beep_pk_*` / `beep_sk_*`.
- **Does NOT reach Monad or other EVM chains.** Its a402 is designed for Sui's sub-second, near-zero-fee model.
- Use case for us: adding **Sui** as a settlement chain to our x402 gateway (new chain #4), NOT as a Monad/EVM rail.
- Galxe quest `GCfyStZbpx` ($20K BEEP pool) — requires 1 trade >$10 via Beep Telegram terminal + 1 referral. Optional.

## Monad (chain 143, EVM) — covered WITHOUT Beep
- **Q402** supports Monad: gasless USDC/USDT settlement for the payer (confirmed live via q402_quote).
- **Trader Joe** has Monad pools — LP rail extends there for free (same Trader Joe V2 pattern as AVAX).
- Almanak `traderjoe_v2` connector does NOT cover Monad yet (avalanche/arbitrum/bsc/ethereum only) — use direct Trader Joe router call instead.
- Monad is a "when the ecosystem matures" play — rail ready, no active build.

## Our x402 gateway — current settlement
- Base, Polygon, Arbitrum (USDC). Chain-agnostic protocol; Solana, Algorand, TON etc. via facilitator implementations.

## Rule of thumb
- Before proposing a rail, confirm the chain: Beep=Sui, Q402+TraderJoe=Monad, our x402=Base/Poly/Arb.
- Don't map a Sui-native protocol onto an EVM L1 (Monad) — verify settlement chain first.
