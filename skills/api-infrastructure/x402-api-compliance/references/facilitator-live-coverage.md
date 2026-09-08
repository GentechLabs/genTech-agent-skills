# Live Facilitator Coverage + Network Rail Map (verified Aug 19, 2026)

Verified from each facilitator's `/supported` endpoint on Aug 19, 2026. Use when
deciding which facilitator wires a rail, or when checking redundancy.

## Network → facilitators that settle it

| Network | CAIP-2 | Primary | Alts |
|---|---|---|---|
| Base | eip155:8453 | CDP | PayAI, GoPlausible, Naven |
| Solana mainnet | solana:5eykt4… | PayAI | CDP, GoPlausible, Dexter |
| Avalanche | eip155:43114 | PayAI | — |
| X Layer | eip155:196 | PayAI | Naven |
| Algorand | algorand:wGHE… | GoPlausible | — |
| Polygon | eip155:137 | PayAI | CDP |
| Arbitrum | eip155:42161 | PayAI | CDP |
| Sei | eip155:1329 | PayAI | — |
| Robinhood Chain | eip155:4663 | Naven | — |

## Verified coverage (from /supported)

- **PayAI** (facilitator.payai.network) — broadest EVM + Solana: Base, Base Sepolia,
  Avalanche, Avalanche Fuji, Sei, Sei devnet, Polygon, Polygon Amoy, X Layer,
  X Layer testnet, SKALE (×2), Arbitrum One, Arbitrum Sepolia, Solana mainnet,
  Solana devnet. **Covers Base, Avalanche, X Layer, Polygon, Arbitrum, Sei, SKALE, Solana.**
- **GoPlausible** (facilitator.goplausible.xyz): Base, Base Sepolia, Solana mainnet,
  Solana devnet, Algorand mainnet, Algorand testnet.
- **CDP** (api.cdp.coinbase.com/platform/v2/x402): Base, Polygon, Arbitrum, World, Solana.
- **Naven** (facilitator.naven.network): Robinhood Chain (eip155:4663) + testnet, Base, X Layer.

## Redundancy rule (Jordan, Aug 19)

Every advertised network must have ≥1 wired facilitator + payTo. Aim for 3-4
alternatives per network where the ecosystem allows (Base and Solana have 4 each).
Never advertise a rail you can't settle.

## Gateway state / Solana rail pattern

Adding a network to the gateway is safe because `enabled_networks()` drops any
network with no payTo — so a code change is INERT until a payTo env var is set.
To fully enable a new rail:
1. Add the NETWORKS entry (CAIP-2, asset, payto_env, payto_default empty).
2. Route the proof network in the verify dispatch (e.g. `is_solana` → `verify_proof_via_payai`).
3. Set `X402_PAYTO_<NET>` in the gateway `.env` + add the network to `X402_NETWORKS`.
4. Restart + re-decode live `accepts[]` to confirm it advertises (only after payTo set).

Solana rail was added Aug 19 to server.py (USDC mint EPjFWdd5…, PayAI routing) but
left inert until a `X402_PAYTO_SOLANA` is set — correct behavior, never advertise unpayable.
