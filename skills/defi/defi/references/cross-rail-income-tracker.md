# Cross-Rail Income Tracker

Build and operate a single income tracker that works across all concentrated-liquidity venues by
operating on the abstraction, not by per-venue copy-paste.

**Abstraction:**
```
our_fees = Δ(cumulative_fee_accumulator) × our_share
```

| Venue | accumulator | our_share read |
|---|---|---|
| LFJ Liquidity Book (Avalanche) | per-bin `fee_factor` (cumulative fees per unit of share) | our share of each bin |
| Meteora DLMM (Solana) | `feeX` / `feeY` on the position account | directly readable |
| Uniswap v3/v4 (Ethereum) | `feeGrowthGlobal0/1X128` | our liquidity |

**Core rules:**
1. **Key the income to the shape** in force during the window. A curve window and a bid-ask window are
   not the same measurement; averaging them across a shape switch manufactures a number that belongs
   to neither.
2. **Reset the baseline after any change in our share.** Rebuilds, re-centres, adds, and removes all
   change the liquidity in the pool. A naive delta across them measures the action, not the earnings.
   Write `baseline_reset` and open a new window.
3. **Never interpolate across a shape change.** If a window contains a rebuild or switch, return `null`
   with the reason.
4. **Fees and reward emissions are separate income.** A venue paying mostly in emissions is a promotion,
   not a yield. Report them on distinct lines.
5. **Do not publish a number we cannot attribute.** Pool-level fee receipts (e.g. "$4,000 in the pool
   today") are not our income. Only our share is ours.

**Why this is the gate before testing Solana:** a Meteora rebalance costs ~$0.001–0.01 against ~$0.19 on
Avalanche. The case for Solana is cheap concentration; a cheap re-centre is only a good idea if we can
measure whether it earned more than it cost.

**Verification after each rail adapter:**
- Run a known position through the adapter and compare the result to the venue UI.
- Check that a rebuild flips `baseline_reset` true.
- Check that reward tokens are recorded separately from fees.
