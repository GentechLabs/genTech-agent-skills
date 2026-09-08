# Solana Homebase — Agentic Treasury (Superteam Tranche-2 MVP)

Built Aug 5, 2026. The Agentic Treasury that settles + yields on **Solana** (native
USDC), used as the Superteam Earn Agentic Engineering **tranche-2 unlock** (live MVP
+ Solana integration). Pattern is the venue-agnostic treasury generalized to a
Solana home base.

## The loop (earn → bridge → yield → pay)
```
Agent earns USDC via x402 (any chain)
   → bridge EVM→Solana (Across adapter, sub-5s)
   → deploy USDC on Solana (Jupiter-routed)
   → regime gate decides: accumulate (yield) vs trade (SOL/TAO via Jupiter)
   → pay services from Solana wallet (sub-cent gas)
   → Q402 trust receipt logged
```

## Files (all in the gentech-treasury profile scripts dir + vault Treasury/scripts/)
- `gta_solana_leg.py` — Jupiter swap leg (SOL/TAO), mirrors the CDP spot-leg pattern:
  quote (read-only) → sign → swap → verify tx signature.
- `solana_homebase.py` — orchestrator wrapping status/bridge/buy/pay, DRY_RUN by default.
- `tranche2_demo.py` — one-command demo for the grant reviewer (live quotes + bridge
  quote + allocation plan).
- `solana_bridge_adapter.py` — Across Base/Avalanche → Solana USDC (in
  `10-Labs/AAE-Dry-Powder-Vault/agent/`).
- Yield engine + close executor + regime gate: `yield_lp_engine.py`,
  `gta_close_executor.py`, `regime_gate.py` (Phase A/B/C of the treasury).

## Key constants (Jupiter / Solana)
- SOL mint `So11111111111111111111111111111111111111112`; USDC mint
  `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`
- TAO mint `taoC6xyv2v8tDLcev4uaGUgV4vdQsWJrGft2kcBRrBY` (6 decimals, verified vs live quote)
- Quote `GET https://api.jup.ag/swap/v1/quote`; Swap `POST https://api.jup.ag/swap/v1/swap`
- Sign `swapTransaction` (base64 → VersionedTransaction) with a `solders` Keypair;
  send via RPC. **Always use median priority fee, not max** (`getRecentPrioritizationFees`).
- Solana USDC bridge via Across (Base SpokePool `0xb4a8d45647445EA9FC3E1058096142390683dBC2`).

## Pitfall — dry-run/quote must NOT require a signing keypair
`gta_solana_leg.py` originally called `_keypair()` BEFORE the dry-run branch, so a
quote couldn't run without a keypair. Fix: in `run_leg`, try to load the keypair but
allow `None` in DRY_RUN (quote only needs a pubkey for the request, and a live quote
is the point of a dry run). Load the keypair only when actually executing. This is the
same "quote should be read-only" principle as the CDP `get_swap_price` oracle.

## Pitfall — verify the token's chain before advising swap/bridge/allocation
The same USDG balance was misread as Robinhood Chain (wrong) then correctly identified
as Solana (right — it was in the MetaMask Solana wallet, and Paxos mints USDG natively
on Solana). Never assume a stablecoin's chain from the symbol alone; read the wallet
context (which app/account, which network the wallet UI shows) and confirm the chain
supports the token natively. If both tokens are on the same chain, a swap (e.g.
USDG→USDC on Solana via Jupiter) is ~1:1 with no bridge needed — don't recommend a
bridge when a same-chain swap suffices.

## Grant tie-in (Superteam tranche-2)
- Requirement: live MVP + **some Solana integration** + $200 coding-subscription receipts.
- A hackathon build with Solana rails can double as the tranche-2 MVP — one build,
  two unlocks (hackathon submission + second grant tranche).
- $200 coding subs = document 2-3 months of the model stack (OpenCode $10 + Ollama $20
  + Nous $20 + VPS $42 ≈ $92/mo) as receipts. Budget these as a real deliverable.
- Funding to go LIVE: ~$2 SOL gas + ~$20 USDC on Solana. Set `SOLANA_REAL=1` +
  `SOLANA_PRIVATE_KEY` (or `SOLANA_KEYPAIR_FILE`) + Jordan greenlight to execute;
  else the engine refuses to fake a success.
