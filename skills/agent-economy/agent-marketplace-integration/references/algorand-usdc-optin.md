# Algorand USDC Opt-In (ASA 31566704) — wallet funding for settlement-gated rails

## The problem
Coinbase (and most exchanges) **refuse to send USDC to an Algorand address that has not
opted in to the USDC ASA**. The transfer fails/bounces with no clear error. This is NOT an
exchange limitation — it's Algorand's asset model: unlike EVM, an Algorand address must
"subscribe" to an ASA (asset) before it can receive it. Relevant to the Algorand x402
Challenge (a settlement-gated marketplace) and any Algorand USDC funding.

## The fix (agent can do it autonomously)
Opt the address in yourself with a 0-unit asset transfer to self, paid from the wallet's own
ALGO balance. Requires the wallet's mnemonic/private key (we hold ours at
`/root/.algorand/jordan-mainnet.mnemonic`).

```python
from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod

USDC_ASA = 31566704
ALGOD = "https://mainnet-api.algonode.cloud"

mn = open("/root/.algorand/jordan-mainnet.mnemonic").read().strip()
sk = mnemonic.to_private_key(mn)
addr = account.address_from_private_key(sk)

client = algod.AlgodClient("", ALGOD)
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

## Key facts
- **Package is `py-algorand-sdk`, NOT `algosdk`** — `pip install algosdk` fails with "no
  matching distribution"; `pip install py-algorand-sdk` works.
- **Address format is different by design** — Algorand addresses are 58 chars, base32,
  uppercase letters + digits 2-7 (e.g. `6IXPRMSY...TU2MTI`). They do NOT look like EVM
  `0x...` 42-char addresses. This is correct, not an error.
- **Checksum verification** uses Algorand's SHA-512/256 (not plain SHA-512) over the last 4
  bytes of the base32-decoded address.
- **Opt-in costs a tiny ALGO fee** — the wallet needs a small ALGO balance (we had 55 ALGO).
- **After opt-in, the wallet shows the USDC asset with amount 0** — ready to receive. Then
  the exchange send lands clean.

## Verify
`GET https://mainnet-api.algonode.cloud/v2/accounts/<ADDR>` → `assets` array contains
`{"asset-id": 31566704, "amount": 0}`.

## Script
`/root/.algorand/optin_usdc.py` (uses jordan-mainnet.mnemonic)
