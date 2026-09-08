# Revenue Monitor — Wrong-Wallet / Stale-Contract Pitfall (Aug 6, 2026)

When the Revenue Monitor reports `$0 / 0 transactions` but real settlements have
happened, check TWO things before trusting the script:

## 1. Which wallet does it scan?
The `WALLET_EVM` constant must be the wallet that actually RECEIVES x402 settlements.
When the treasury moved to a new CDP server account (`0x77C622D02A1518fC0FDcd83B8C28010FA5ebB7dE`)
and the arb wallet (`0x3d117Bf42218c3244AA0Ad011E8651A615230eCb`) became the payer, the
monitor was still scanning the old `0x7ebff188...` wallet — so it missed every settlement.

**Fix:** scan BOTH the receiving wallet AND the payer wallet. Loop over a tuple of
addresses in the chain scan:
```python
for wallet in (WALLET_EVM, WALLET_ARB):
    transfers = fetch_usdc_transfers(chain, wallet, last_block)
    for t in transfers:
        if t["tx_hash"] not in existing_txs:
            new_transfers.append(t)
```
Also add ALL our own wallets to the self-transfer filter so internal moves aren't
miscounted as revenue:
```python
our_wallets = {WALLET_EVM.lower(), WALLET_SOL.lower(), WALLET_ARB.lower(), WALLET_KH.lower()}
external = [t for t in new_transfers if t["sender"].lower() not in our_wallets]
```

## 2. Is the USDC contract address current?
Base USDC changed from `0x83358933e220DBD71d557b2c7c88c4b48eb88b43` (stale) to
`0x833589fCD6eDb6E08f4c7C32D4f71b54bDA02913` (current). A stale contract address means
even a correct-wallet scan finds nothing. Verify the live address before debugging further.

## Verify the fix
Run the monitor — it should now pick up the funding/settlement that was previously
invisible. Confirmed Aug 6, 2026: after correcting the wallet + contract, the monitor
detected the $26 USDC that had landed in the CDP account (was showing $0 before).

## Also: the 3-rail breakdown
The treasury now settles across three rails — x402 (CDP facilitator, Base USDC EIP-3009),
Q402 (gasless, 12 chains EIP-7702), and Solana/Jupiter. Add a `🛤️ Settlement Rails` section
to `format_report` so the digest reflects all three, not just the EVM scan.
