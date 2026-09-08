# Wallet Funding Addresses + Verification Technique (Aug 5, 2026)

## The rule: verify addresses against the live system BEFORE handing them to the user

When a user asks "what wallet do I fund / send to?", NEVER trust a truncated brain
reference (e.g. `0x77C6…`) or a manual derivation from a private key. Deriving an
Ethereum address from a DER PKCS#8 EC P-256 secret is error-prone (the pubkey
extraction + keccak step can silently produce a DIFFERENT address than the one the
platform actually uses). Confirm the real address via the platform's own read API.

## Verified addresses (as of Aug 5, 2026)

| Wallet | Chain | Address | How verified |
|--------|-------|---------|--------------|
| CDP server account (Agentic Treasury) | Base | `0x77C622D02A1518fC0FDcd83B8C28010FA5ebB7dE` | CDP SDK `client.evm.list_accounts()` → first account |
| KeeperHub execution wallet | Base | `0x53A8DFA431D03A36499f9DB70AAFbb00C28308EA` | brain (Aug 4) |
| Algorand wallet | Algorand | `6IXPRMSYQBZSP2KIPH6BQ7MP4XN7VP6MWGHCLLF52K5R4IYCPA74TU2MTI` | generated Aug 5, keys at /root/.algorand/ |
| Solana personal wallet | Solana | `BE815V7ojVz63PDxFFSEQyGSe5PZE2fAdKUU6Rd5pUvP` | read `address` field from `/root/.gentech/wallets/solana_jordan-personal_20260622_120527.json` |

## CDP server account address — the correct way to fetch it

```python
import os, asyncio
from dotenv import load_dotenv
load_dotenv()
from cdp import CdpClient

async def main():
    client = CdpClient()  # reads CDP_API_KEY_ID/SECRET from env
    accts = dict(list(await client.evm.list_accounts()))['accounts']
    a = accts[0]
    print('address:', a.address if hasattr(a, 'address') else a)

asyncio.run(main())
```

- The working script uses `client.evm.list_accounts()` (NOT `client.evm_accounts` —
  that attribute doesn't exist on `CdpClient`).
- `CdpClient()` with no args reads creds from env; `CdpClient(api_key_id=..., api_key_secret=...)`
  also works but the no-arg form is what the existing `gta_coinbase_leg.py` uses.
- The brain's `0x77C6…` truncated reference matches the real `0x77C622D02A1518fC0FDcd83B8C28010FA5ebB7dE`.

## Solana wallet address — read the stored field, don't derive

The personal Solana wallet file is a dict with an `address` field already populated:
```python
import json
d = json.load(open('/root/.gentech/wallets/solana_jordan-personal_20260622_120527.json'))
print(d['address'])  # BE815V7ojVz63PDxFFSEQyGSe5PZE2fAdKUU6Rd5pUvP
```
The file shape is `{chain, address, private_key(list of 32), created_at, purpose, warning}`.
Do NOT try to derive the pubkey from `private_key` via solders — the stored `address`
field is authoritative and avoids the dict-vs-bytes conversion trap.

## Funding amounts (from the ~$109 grant, priority order)

| Destination | Amount | Unlocks |
|-------------|--------|---------|
| CDP Agentic Treasury | ~$26 ($25 USDC + $1 ETH gas) | first x402 settlement → Agentic.Market auto-indexes ($52M+ TPV) + OpenDexter catalog |
| KeeperHub | ~$25 ($15 ETH + $10 USDC) | live-tx link for KeeperHub judging (Aug 13) |
| Algorand | ~$8 ($5 ALGO + $3 USDC ASA 31566704) | Algorand x402 Challenge mainnet payment |
| Solana | ~$22 ($2 SOL + $20 USDC) | Solana Homebase on-chain proof (tranche-2 + Colosseum + Arc) |
| Reserve | ~$28 | subscriptions + buffer |

**Algorand gotcha:** the address must OPT-IN to USDC ASA 31566704 before it can
receive USDC. Send ALGO first, opt-in, then send USDC.
