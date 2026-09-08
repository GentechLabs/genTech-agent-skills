# RWA Token Evaluation Checklist

Systematic framework for evaluating Real World Asset (RWA) tokens. Jordan is actively exploring RWA plays (Propbase, Landshare, real estate tokens). Use this checklist before committing capital.

## The Hard Rule: Liquidity Before APY

**Always check DEX liquidity BEFORE assessing yield.** A 20% APY means nothing if you can't exit.

Red flags:
- Daily DEX volume < $1,000 → you can't exit meaningful size
- Daily DEX volume < $10,000 → slippage will eat your yields
- Pool TVL < $50,000 → one whale can move the price 50%

Source: DexScreener, GeckoTerminal, or direct DEX page. Check the actual pair, not just the token's total volume across exchanges.

## Evaluation Checklist

### 1. Token Basics
- [ ] Chain (Aptos, Ethereum, BSC, Solana?)
- [ ] Market cap (micro-cap < $5M = high risk)
- [ ] ATH decline (>90% off ATH = either deep value or dead)
- [ ] 24h volume across all exchanges
- [ ] Token supply (circulating vs total, inflation schedule)

### 2. DEX Liquidity (THE CRITICAL CHECK)
- [ ] Find the primary DEX pair (PancakeSwap, Uniswap, Thala, etc.)
- [ ] Check 24h volume on that specific pair
- [ ] Check pool TVL
- [ ] Calculate slippage for your intended position size
- [ ] If volume < $1K/day, STOP — liquidity is too thin

### 3. Yield Sources
- [ ] Where does the yield come from? (rental income, token emissions, trading fees)
- [ ] Is yield backed by real cashflow (rental, revenue) or just inflation?
- [ ] What's the APY? (20%+ from emissions = unsustainable)
- [ ] Lock-up period? (3-month, 6-month, no lock?)
- [ ] Per-participant cap? (indicates demand management)

### 4. RWA-Specific Checks
- [ ] What's the underlying asset? (property, land, commodity, invoice)
- [ ] Who manages the asset? (operator risk — are they reputable?)
- [ ] Is there proof of asset ownership? (legal docs, on-chain verification)
- [ ] How does yield flow from asset to token holders? (direct distribution or re-invested?)
- [ ] What's the legal structure? (SPV, tokenized deed, synthetic?)
- [ ] KYC required? (non-KYC = more accessible but potentially less regulated)

### 5. Team & Execution
- [ ] Previous offerings? How many, what happened?
- [ ] Did previous offerings sell out? (demand signal)
- [ ] Secondary market performance of previous offerings
- [ ] Team doxxed? Background check?
- [ ] Partnerships or institutional backing?

### 6. Exit Strategy
- [ ] Can you sell on DEX without 20%+ slippage?
- [ ] Is there a secondary marketplace for the RWA tokens?
- [ ] What's the redemption process for the underlying asset?
- [ ] Is there a buyback mechanism?

## Propbase Case Study (June 2026)

**What looked good:**
- 7th property offering, 200+ registrations (execution proof)
- 6.79% gross rental yield from real Bangkok properties
- 20% APY staking pools on Aptos
- Non-KYC yield farming (permissionless DeFi)
- Previous 6 offerings sold out, 15-21% above launch on secondary

**What killed it:**
- PROPS/APT on PancakeSwap: $73 daily volume, 101 transactions
- DexScreener: "This pair has very little liquidity"
- You literally cannot exit anything beyond dust amounts
- Micro-cap at $2.3M, 98% off ATH

**Verdict:** Real execution, real yield, but zero exit liquidity. The APY is a trap — you'd earn 20% on tokens you can't sell.

## Comparison Template

When evaluating multiple RWA tokens, use this format:

```
Token: [Name]
Chain: [Aptos/ETH/BSC]
Asset: [What's tokenized]
Yield Source: [Rental/Revenue/Emissions]
APY: [X%]
DEX Volume: [$X/day] ← CRITICAL
Pool TVL: [$X]
Slippage for $500 exit: [X%]
Lock-up: [None/3mo/6mo]
KYC: [Required/Non-KYC]
Previous Offerings: [N sold out, X% above launch]
Verdict: [Pass/Watch/Small Position]
```

## Decision Framework

| DEX Volume | APY | Action |
|------------|-----|--------|
| > $10K/day | Any | Evaluate normally |
| $1K-$10K/day | > 20% | Small position only (<$200) |
| $1K-$10K/day | < 20% | Watch, wait for volume growth |
| < $1K/day | Any | **PASS** — can't exit |
