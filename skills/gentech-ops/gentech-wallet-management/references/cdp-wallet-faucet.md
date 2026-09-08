# CDP Server Wallets — v2 SDK patterns (cdp-sdk 1.47.1, tested Sep 3 2026)

Coinbase CDP server wallets are how the fleet holds keys for infrastructure wallets (treasury, telegraph-miner) without key files on disk. The wallet rule still holds: we control signing via the CDP API.

## Credential loading

- `CDP_API_KEY_ID` / `CDP_API_KEY_SECRET` / `CDP_WALLET_SECRET` — from profile `.env` or `/root/.blockrun/cdp-wallet-secret` (wallet secret file).
- Pass all three explicitly to `CdpClient(...)` — the implicit env-only constructor is easy to get wrong.

## Client init + listing accounts (async)

```python
import asyncio, os
from cdp import CdpClient

async def main():
    client = CdpClient(api_key_id=..., api_key_secret=..., wallet_secret=...)
    accounts = await client.evm.list_accounts()          # NOT list_evm_accounts (AttributeError)
    items = accounts.accounts if hasattr(accounts, 'accounts') else accounts
    for a in items:
        name = getattr(a, "name", None) or "?"          # name CAN be None — guard before .lower()
        addr = getattr(a, "address", "?")
        print(name, addr)
    await client.close()

asyncio.run(main())
```

## Token balances (Base Sepolia)

```python
balances = await client.evm.list_token_balances(address=addr, network="base-sepolia")
bs = balances.balances if hasattr(balances, 'balances') else balances
for b in bs:
    print(getattr(getattr(b, 'token', None), 'symbol', '?'), getattr(b.amount, 'amount', b))
```

## Faucet (testnet funding, no human gate needed)

```python
# signature: request_faucet(self, address: str, network: str, token: str) -> str (tx hash)
res = await client.evm.request_faucet(address=ADDR, network="base-sepolia", token="usdc")
```

- Token string is lowercase `"usdc"` (uppercase also accepted but lowercase is what's tested).
- Proven Sep 3, 2026: returned tx `0xaa958394498ced4d5fdfc63699bab8612709930239a35a38ec1a0dbd235c8b9b`, wallet ended with 1.0 USDC + existing gas on Base Sepolia.
- Known wallets on this CDP project: `0x77C622D02A1518fC0FDcd83B8C28010FA5ebB7dE` (treasury), `0x60D31Ff0255566f7f2e4F1764a381e98c161Ac5d`, `0x0C92953F7Ae53040F84FB8ca4F58f1a847473A2d`, `telegraph-miner` → `0x03d272624c45Aace57565E133239213E85B9856E`.

## Discovery tip

Method names drift between SDK versions. Before writing against the client, enumerate:

```python
from cdp.evm_client import EvmClient
print([m for m in dir(EvmClient) if not m.startswith('_') and callable(getattr(EvmClient, m))])
import inspect
print(inspect.signature(EvmClient.request_faucet))
```

This session: `list_evm_accounts` → renamed `list_accounts`; `network_id` param → `network`. Enumerate first, don't guess.