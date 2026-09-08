# Meteora Trade-Rail Wallet Path (Aug 20, 2026)

## The decisive fact: a loose keypair file does NOT sign Condor trades

The `consigliere` strategy (Meteora/Agent Builders Cup submission) calls
`manage_executors` / `order_executor` and reads executors via core providers.
Tracing the signing path (`condor/agents/engine.py` → `_get_client()` →
`get_bots_client` / `get_config_manager` → `HummingbotAPIClient`):

```
consigliere strategy → HummingbotAPIClient (base_url http://{host}:{port})
  → Hummingbot API (port 8002) → Gateway (port 15888) → signs on-chain
```

The executor does **NOT** read a local keypair file. Trades are signed by the
**Gateway's own wallet**, stored encrypted in the gateway's wallet store. So a
loose Solana keypair you generate with `solders` on the VPS is **not wired into
the executor at all** — dropping it in a file won't make the LP bot use it.

### Verified state of the gateway wallet store (Aug 20)
- `/hummingbot-api/bots/gateway-files/conf/wallets/` → empty
- Inside the `gateway` container (`docker exec gateway ls .../conf/wallets/`) → empty
- No `.keystore` / `.seed` / wallet files anywhere in the gateway
- `GET /accounts/gateway/wallets` (via `accounts.list_accounts`) → `[]`

=> The gateway has **no signing wallet created yet**.

### The correct path (manual, interactive)
Run the gateway's wallet-creation flow (Hummingbot CLI / `gateway` setup) which
generates a wallet **inside the gateway's encrypted wallet store**. It needs the
gateway `CONFIG_PASSWORD`. Then fund the gateway-derived Solana address. That is
the account the executor actually signs with.

## Generating a standalone Solana keypair (when you need a file-based one)

`solders` is available on the system python. Generate + verify a fresh keypair:

```bash
python3 -c "
from solders.keypair import Keypair
import json, os
kp = Keypair()
print('ADDRESS:', str(kp.pubkey()))
open('/root/.solana-trade/trade-keypair.json','w').write(json.dumps(list(bytes(kp))))
os.chmod('/root/.solana-trade/trade-keypair.json', 0o600)
"
# Verify round-trip (address re-derives from the saved file):
python3 -c "
import json
from solders.keypair import Keypair
print(Keypair.from_bytes(bytes(json.load(open('/root/.solana-trade/trade-keypair.json')))).pubkey())
"
# Confirm on-chain (expect 0 for a brand-new wallet):
curl -s https://api.mainnet-beta.solana.com -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"getBalance","params":["<ADDR>"]}'
```

`X402_PAYTO_SOLANA` (`Hv2N2XJT...`) is the x402 **receive-only** address — no
signing key behind it. It cannot sign LP/swap txs. It is NOT the trade-rail
wallet. Do not route race funding to it.

## What actually must happen before the race (the real "fund the wallet" step)
1. Create the gateway wallet (interactive, needs config password).
2. Read the derived Solana address from the gateway.
3. Fund THAT address with ~$25-30 SOL (gas + ~0.057 SOL/Meteora slot rent + 0.3 SOL reserve).
4. Verify on-chain balance. Only then can the executor deploy.

If instead you want Condor to sign directly from a file keypair, that is a
**code change** to Condor's signing layer — the non-default path, more work.
