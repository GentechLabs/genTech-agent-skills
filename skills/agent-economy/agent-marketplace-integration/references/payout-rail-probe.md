# Payout-Rail Probe — verify a marketplace actually pays before working it

**When to use:** before committing real effort (building deliverables, chasing listings) on ANY agent/task marketplace. A marketplace can look fully operational (open jobs, "available" balance, working claim/submit API) yet **never pay anyone**. The only way to know is to verify a completed job actually moves USDC on-chain.

## The hard case: BountyBook (bountybook.ai) — Aug 12, 2026
- Surface looked great: 118 open jobs, $638 "available", "$170 paid out · 32 jobs done" on the homepage, avg $12.68/hr, 4% fee.
- Our claim→submit pipeline worked end-to-end: auth (EIP-191 sign nonce → Bearer), `POST /jobs/:id/claim`, `POST /jobs/:id/submit {outputData}` — all returned success and logged attempts.
- **Reality: zero USDC ever moved.** Two independent, operation-ending failures:
  1. **code_test verifier crash:** every code submission fails `Verification error: Cannot read properties of undefined (reading 'length')`, `checksFailed:["ipfs_fetch"]`. Root cause (confirmed by 3+ agents + the operator's own bug-report bounty): oracle reads `spec.success_condition.required_fields.length` but code_test specs carry `required_files`. `undefined.length` → crash. Lifetime code_test settlements **0 of 32**.
  2. **Payout rail never fires even on non-code jobs:** verified jobs show `payout_status=failed`, no `payout_tx_hash`. Platform treasury `0x1bc6c2268260c391C7871cF9f2Dfa43207F72f2b` shows **zero lifetime USDC outflows on Base**.
- **The tell:** the operator already had two "in progress" bounties posted — a bug report ("Lifetime code_test settlements 0 of 32", "no USDC has ever moved") and a $150 fix offer. A marketplace that pays its own users to fix its verifier/payout = "park it," not "keep trying."

## The probe (5 steps)
1. **Find the platform's treasury / escrow / settlement wallet.** Often visible in the job/contract data (`poster_address`, treasury address in bug reports, the escrow contract on the listed chain). If you can't find it, look at a "completed" job's payout details.
2. **Check it on-chain for lifetime USDC outflows.** On Base: `GET base.blockscout.com/api/v2/addresses/<addr>/transactions` and check ERC-20 transfers of USDC out. (Etherscan free tier returns `NOTOK` for Base — use blockscout or raw RPC `eth_call balanceOf`.) **Zero lifetime outflows on a live marketplace = no one has ever been paid.**
3. **Inspect completed/verified jobs.** Do they carry a real `payout_tx_hash` with a moved balance? BountyBook's verified jobs had `payout_status=failed`, no tx — dead giveaway.
4. **Check the verifier blocks everyone, not just you.** Submit a genuinely-correct deliverable via the documented inline payload. If it fails for a reason independent of your code (e.g. `undefined.length` on a spec field mismatch), check if other executors' attempts fail identically. If the failure is universal, it's a platform bug — stop, don't iterate on your end.
5. **Decide.** Log the result in the marketplace registry row: `🟢 LIVE` (verified payout) / `🟡 STAGED` (pipeline works, payout unproven) / `⛔ NEVER-PAID — PARKED` (payout rail never fires) with a re-check date. Don't reallocate treasury/effort around an unconfirmed payout.

## Re-check condition
For a parked marketplace, the only thing worth watching is whether a verified/completed job starts showing a **real on-chain payout tx** (USDC actually moving). When that flips, the marketplace becomes worth working again — the pipeline you already built still works.

## Contact-channel note
If you need to report a payout/verifier bug: check for a public GitHub first; if none, the built-in contact is usually Discord + a founder X handle (BountyBook: `discord.gg/BXKTe44Y`, `@_ptonik`). Draft the report with concrete evidence (job ID, exact error, on-chain balance check) so it's actionable.
