# Algorand USDC Opt-in — the Coinbase send blocker

**When:** funding an Algorand wallet to receive USDC (e.g. the Algorand x402 Challenge mainnet payment).

## The wall
Algorand, unlike EVM, requires an address to **opt in to an ASA (Algorand Standard Asset) before it can receive it**. If you try to send USDC (ASA 31566704) to an address that hasn't opted in, the transfer fails/reverts — and exchanges like **Coinbase refuse the send outright** ("can't send USDC to this wallet"). This is NOT a Coinbase bug; it's the Algorand opt-in requirement.

## The fix — 0-unit asset transfer to self
Opt-in is a 0-unit `AssetTransferTxn` to yourself, paid from the wallet's own ALGO balance (needs a little ALGO for the fee).

```python
from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod

USDC_ASA = 31566704
client = algod.AlgodClient("", "https://mainnet-api.algonode.cloud")
mn = open("/root/.algorand/jordan-mainnet.mnemonic").read().strip()
sk = mnemonic.to_private_key(mn)
addr = account.address_from_private_key(sk)

acct = client.account_info(addr)
assets = {a["asset-id"]: a for a in acct.get("assets", [])}
if USDC_ASA in assets:
    print("already opted in")
else:
    params = client.suggested_params()
    txn = transaction.AssetTransferTxn(sender=addr, sp=params, receiver=addr, amt=0, index=USDC_ASA)
    signed = txn.sign(sk)
    txid = client.send_transaction(signed)
    transaction.wait_for_confirmation(client, txid, 10)
    print("opted in:", txid)
```

## Verification
After opt-in, `account_info` shows the asset with amount 0:
```
assets: 1
  asset 31566704 amount: 0
```
Then Coinbase will accept the USDC send.

## Confirmed Aug 5, 2026
GenTech Algorand wallet `6IXPRMSY…2MTI` had 55 ALGO but 0 USDC; Coinbase refused the send. Opt-in txn `D4ZESUWYNZ6HYN77FQDVDQ2RVN7MRNRCC3FVH4ATJVZIKZJUAYUA` (round 63794335) cleared it. Script saved at `/root/.algorand/optin_usdc.py`.

## Notes
- The `algosdk` pip package is actually `py-algorand-sdk` (import name `algosdk`).
- Algorand addresses are 58-char base32 (uppercase + digits 2-7) — they legitimately look different from 42-char `0x…` EVM addresses. A checksum check uses SHA-512/256 (not plain SHA-512): `hashlib.new('sha512_256', pubkey).digest()[-4:]`.
