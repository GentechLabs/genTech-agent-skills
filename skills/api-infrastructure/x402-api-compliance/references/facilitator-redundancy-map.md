# Facilitator ↔ Network Redundancy Map (verified Aug 19, 2026)

Jordan's rule (Aug 19): every network we advertise must have ≥1 wired facilitator +
payTo, and we should aim for 3-4 alternatives per network where the ecosystem allows,
so a single facilitator outage never blocks revenue. Verified live from each
facilitator's `/supported` endpoint.

## Verified coverage (from /supported)

| Facilitator | v2 networks it settles |
|---|---|
| **PayAI** (facilitator.payai.network) | Base, Base Sepolia, Avalanche, Avalanche Fuji, Sei, Sei devnet, Polygon, Polygon Amoy, X Layer, X Layer testnet, SKALE (×2), Arbitrum One, Arbitrum Sepolia, Solana mainnet, Solana devnet |
| **GoPlausible** (facilitator.goplausible.xyz) | Base, Base Sepolia, Solana mainnet, Solana devnet, Algorand mainnet, Algorand testnet |
| **CDP** (api.cdp.coinbase.com/platform/v2/x402) | Base, Polygon, Arbitrum, World, Solana (per x402 docs) |
| **Naven** (facilitator.naven.network) | eip155:4663 (Robinhood Chain), eip155:46630 (testnet), Base, X Layer, eip155:2368 |
| **Dexter** (@dexterai/x402) | Base (EVM), Solana — catalogs on OpenDexter (separate from CDP) |

## Redundancy map (network → facilitators)

| Network | CAIP-2 | Primary | Alts | Count |
|---|---|---|---|---|
| **Base** | eip155:8453 | CDP | PayAI, GoPlausible, Naven | 4 |
| **Solana** | solana:5eykt4… | CDP | PayAI, GoPlausible, Dexter | 4 |
| **X Layer** | eip155:196 | PayAI | Naven | 2 |
| **Polygon** | eip155:137 | PayAI | CDP | 2 |
| **Arbitrum** | eip155:42161 | PayAI | CDP | 2 |
| **Avalanche** | eip155:43114 | PayAI | — | 1 |
| **Algorand** | algorand:wGHE… | GoPlausible | — | 1 |
| **Sei** | eip155:1329 | PayAI | — | 1 |
| **SKALE** | eip155:1187947933 | PayAI | — | 1 |
| **Robinhood Chain** | eip155:4663 | Naven | — | 1 |

**Base and Solana are the most resilient** (4 facilitators each). Avalanche, Algorand,
Sei, SKALE, Robinhood Chain are single-facilitator today — the redundancy gaps to close
as new facilitators come online.

## Injective — NOT yet supported (Aug 19, 2026)
None of PayAI / GoPlausible / Naven support Injective. Injective IS an x402 Foundation
member (Jul 16) and x402 is live on Injective mainnet, so facilitator support is likely
coming — but until then, do NOT advertise an Injective rail (never advertise a rail you
can't settle). Re-check `/supported` quarterly; coverage grows fast.

## Adding a non-EVM rail (Solana pattern, proven Aug 19)
Solana is non-EVM: USDC is an SPL token (mint `EPjFWdd5…`), not a contract address, and
`payTo` is a Solana address. Pattern:
1. Add a `NETWORKS["solana"]` entry: `network: solana:5eykt4…`, `asset: EPjFWdd5…`,
   `decimals: 6`, `payto_env: X402_PAYTO_SOLANA`, `payto_default: ""`.
2. Route Solana proofs to PayAI in the verify dispatch (`is_solana = proof_network.startswith("solana:")`).
3. Set `X402_PAYTO_SOLANA=<addr>` + add `solana` to `X402_NETWORKS` in `.env`, restart.
4. **Fail-safe:** `enabled_networks()` drops any rail without a payTo — so the code can
   be in place and the rail stays inert until a payTo is set. Never advertise a rail
   you can't settle.
