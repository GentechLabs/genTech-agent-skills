# Facilitator ↔ Rail Matching Map (x402 "matching game")

Jordan's frame (Aug 11, 2026): getting an x402 API listed/settled is a **matching problem**,
not a single fix. Multiple facilitators, multiple rails, and each facilitator only settles
the rails it's wired for. If the payment settles through a different facilitator than the
gateway verifies through, the retry bounces 402 → never settles → no listing.

## The map (which facilitator ↔ which rail)

| Facilitator | Rails it settles | Gateway verify path | Triggers listing on |
|---|---|---|---|
| **CDP** (`api.cdp.coinbase.com/platform/v2/x402`) | Base (`eip155:8453`), Polygon, Arbitrum, World, Solana | `verify_proof_via_cdp` (JWT auth, `/verify` + `/settle`) | **CDP Bazaar / Agentic.Market** |
| **GoPlausible** | Algorand (`algorand:...`) | `verify_proof_via_goplausible` | x402 Global Challenge leaderboard |
| **PayAI** (`facilitator.payai.network`) | Avalanche (`eip155:43114`), X Layer (`eip155:196`), + ~14 more | `verify_proof_via_payai` | PayAI-orbitx / xPay |
| **Dexter** (`@dexterai/x402`) | Base (EVM), Solana | dexter `payAndFetch` | **OpenDexter (open.dexter.cash)** |

**Two separate catalogs, two separate mechanisms** (proven Aug 3 + Aug 11, 2026):
- **CDP Bazaar / Agentic.Market** catalogs on settlement through **CDP's** facilitator.
- **OpenDexter** catalogs on settlement through **Dexter's** facilitator.
- A settlement through CDP does NOT list you on OpenDexter, and vice versa. Don't assume
  one payment lists you everywhere.

## The decision rule

If the goal is "get listed somewhere real," prefer the path the gateway was **built for**.
Our gateway declares `bazaarResourceServerExtension` + CDP keys, so CDP Bazaar is the native
path (flip `PAYMENT_VERIFY_MODE=cdp`). OpenDexter requires re-wiring the gateway to accept
Dexter-facilitated proofs — a bigger change than a mode flag.

## The diagnostic sequence (when a self-settle "fails")

1. **Check the gateway's live 402 `accepts[]`** — decode the `PAYMENT-REQUIRED` header and
   list every `accepts[i].network`. This is ground truth for what rails the gateway actually
   advertises + which `payTo` each points to. If a rail is advertised but its `payTo` is a
   different facilitator's address than the client settles through → mismatch.
2. **Confirm the running process env** — `cat /proc/<pid>/environ` vs the `.env` file.
   A stale process (started before key rotation) holds old creds even after the file changes.
   Fix: `systemctl restart x402-api`. (This is the Aug 5 401-trap; a 30-second restart beats
   a code "fix" for a non-existent bug.)
3. **Match the facilitator** — verify the gateway's verify mode matches the facilitator the
   payment settles through. `PAYMENT_VERIFY_MODE=simulation` rejects every real EIP-3009 proof
   (expects old flat HMAC `{amount,recipient,nonce,validAfter,validBefore,signature}`, not a
   base64 JSON envelope) → always 402.
4. **Check for the simulation-overwrite bug** (Aug 11, 2026) — in `auto` mode, if
   `verify_proof_simulation()` runs **unconditionally** (missing `else`) after the CDP branch,
   it overwrites CDP's successful verify+settle with a simulation-format failure →
   `proof is not valid JSON` (no "or base64"). Wrap the simulation fallback in `else:`.
   Symptom string: `payment_proof_invalid / proof is not valid JSON` while CDP creds are
   present and mode=auto. Fix applied to BOTH the live gateway and the agent kit.
5. **Client-side "Invalid character"** (Dexter) — this is usually a *downstream symptom* of the
   gateway rejecting the real proof (step 3/4), not a client bug. The dexter client's retry
   returns 402 again → `Invalid character`. Fix the gateway verify path, not the client.

## Post-settlement indexing lag

- CDP Bazaar / Agentic.Market: ranking can lag **up to 6h** after settlement. Fresh search
  returning 0 right after is expected, not a failure. Verify ~6h later, not immediately.
- OpenDexter: catalogs on the first real mainnet settlement through Dexter (~$1+ USDC).
  Testnet USDC does NOT trigger it.

## Wallet reality check (before claiming readiness)

Self-settlement needs a wallet you can **sign from** that **holds USDC on the right chain**.
These frequently split across two wallets (one funded-no-key, one keyed-no-funds). Verify
balances on-chain (publicnode Base RPC + User-Agent header) before assuming you can settle.
Q402 trial is gasless *relay*, not a funded mainnet wallet — not settlement-capable.
