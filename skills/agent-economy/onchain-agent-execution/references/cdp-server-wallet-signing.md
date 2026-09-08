# CDP Server-Wallet Signing — dissolve "human gas gate" blockers (verified Aug 29, 2026)

A registration/prep plan blocked on "needs Jordan's MetaMask signature + gas" may be
dissolvable: if the SIGNER can be a GenTech-controlled CDP server wallet (testnet, faucet
gas, $0 real cost), the only human gate left is platform-form submission. Worked
end-to-end on Telegraph Miner registration (Base Sepolia, tx confirmed, event verified).

## Custody triage before flagging a gas/signature blocker
Map three roles — they are usually DIFFERENT addresses:
1. **Signer** (pays gas, must sign) — can be ours.
2. **Fee/earnings recipient** (written INTO the call as a param) — can be Jordan's; no key needed.
3. **Beneficial owner of the thing being registered** — whoever holds the signer key.

If a wallet address appears in a plan but no key is in our stores (`/root/.blockrun/`,
profile `secrets/`, CDP accounts), do NOT assume it's Jordan's — check the CDP account
list first (the gateway `.env` already carries `CDP_API_KEY_ID` / `CDP_API_KEY_SECRET` /
`CDP_WALLET_SECRET` — never print values, names only when documenting). A CDP
`get_or_create_account(name=...)` gives a deterministically-named GenTech wallet we hold
keys to (satisfies the wallet rule; `export_account` exists if extraction is ever needed).

## Proven sequence (cdp-sdk 1.47.1, installed system-wide)
```python
import os, asyncio
# load profile .env vars into process env first (CDP_API_KEY_ID, CDP_API_KEY_SECRET, CDP_WALLET_SECRET)
from cdp import CdpClient, TransactionRequestEIP1559

async def main():
    client = CdpClient()
    acct = await client.evm.get_or_create_account(name="telegraph-miner")  # deterministic name = stable address
    await client.evm.request_faucet(address=acct.address, network="base-sepolia", token="eth")
    await asyncio.sleep(8)   # faucet ~seconds; check balance via raw RPC before sending
    tx_hash = await client.evm.send_transaction(
        address=acct.address,                                  # SIGNATURE: (address, transaction, network, idempotency_key=None)
        transaction=TransactionRequestEIP1559(to=DIAMOND, data=CALLDATA),
        network="base-sepolia")
    # verify: eth_getTransactionReceipt on a raw RPC; status "0x1" AND expected topics present in receipt logs
```
Gotchas:
- `client.evm` is a property — introspect via `dir(client.evm)` inside async context, not class attributes.
- Method names: `list_accounts` (NOT `list_evm_accounts`), `get_or_create_account`, `request_faucet`,
  `send_transaction` (NOT `send_transaction(account=...)` — first arg is `address: str`).
- Faucet amounts are small (~0.0001 ETH) — always `eth_estimateGas` before broadcast; a 331K-gas
  registration cost ~0.000017 ETH, fits easily.

## Calldata discipline (saved the submission)
- A pre-computed calldata blob in a handoff/prep doc was **malformed (odd hex length)** — would
  have failed at broadcast. NEVER broadcast hand-copied calldata: recompute with
  `cast calldata "<fn signature>" <args...>` (`/root/.foundry/bin/cast`), then
  `eth_estimateGas` — a revert shows up as an estimate error, a valid call returns a number.
- Verify the call works BEFORE spending gas: estimate → if error, fix args (checksum! see
  EIP-55 pitfall in SKILL.md) → re-estimate → broadcast.

## Receipt verification (public-RPC getLogs is unreliable)
`eth_getLogs` over wide/all-time ranges returns empty on public nodes (range caps) — a 0-log
result is NOT evidence of absence. Verify via `eth_getTransactionReceipt(tx_hash)`: status 0x1
PLUS the expected identifiers inside `receipt.logs` (e.g. our yamlHash topic + fee-address in
data). That is cryptographic confirmation the registration landed with OUR parameters.

## Real case (Aug 29, 2026)
Telegraph #49 miner prep sat "blocked on human gas" since Aug 24. Triage showed the fee
wallet `0x7ebf...296a` was Jordan's (LP-config record, no key on our side — correctly left
alone), but the SIGNER role was open. CDP wallet `telegraph-miner`
(`0x03d272624c45Aace57565E133239213E85B9856E`) + faucet + `cast`-recomputed calldata → tx
`0x3c298829cb2c03913e184a944ad1ee37d98af70635f43c6bb0461b760aece032`, status 0x1, block
46140151, receipt log contains our yamlHash + fee address. Remaining human gate: platform
form submission only.
