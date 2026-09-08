# Self-Settle Funding Pre-Flight — verify a KEYED wallet is funded (Aug 24, 2026)

When firing a self-settle (paying our own x402 endpoint to trigger settlement-gated auto-listing on
Agentic.Market / CDP Bazaar / OpenDexter), the blocker is usually **funding, not code** — and earlier
"funded wallet" notes go STALE.

## Why this matters
Previous notes claimed the GTA arb wallet `0x3d117…eCb` held ~0.45 USDC on Base. A live sweep Aug 24 showed
it had **dropped to $0 real USDC** (only PONS dust). Meanwhile the only real Base USDC (~$4.55) sat in the
**keyless** stranded wallet `0xF9dc…` (the loss we already took). So no keyed wallet could settle — a genuine
funding blocker, not a protocol bug. Re-diagnosing the x402 flow would have been wasted effort.

## Pre-flight checklist (run BEFORE firing or before declaring the funding gap "stale")
1. **For every known wallet**, query the live USDC balance on Base:
   ```bash
   # canonical Base USDC: 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
   curl -s "https://base.blockscout.com/api/v2/addresses/<addr>/token-balances"
   ```
   AND confirm we hold a private key for it (`secure/*.json`, `.env`). **Both must be true.**
2. **Distinguish scam-dust from real USDC** by matching the token *contract address* to the canonical Base
   USDC, not by symbol. Wallets accumulate fake `t.me/s/US_CIRCLE` "USDC" tokens — a symbol match proves nothing.
3. **If no keyed wallet has real USDC**, the blocker is funding. Drop a couple USDC + a little ETH gas into a
   keyed wallet (arb `0x3d117…` or circle `0x49f3…` both have keys), get Jordan's explicit nod (spend rule:
   "spend less, never fake receipts" — get sign-off on the tiny on-chain spend), then fire.
4. A self-settle also needs a little native gas on the payer wallet for the settlement tx, not just USDC.

## If truly blocked
Don't burn a dead settle or re-diagnose the protocol. Report the specific gap (which wallet, which missing
asset) to Jordan with the cheapest funding path (which keyed wallet to top up). Once funded, fire the settle
and wait up to ~6h for indexing (verify by search; don't re-fire).
