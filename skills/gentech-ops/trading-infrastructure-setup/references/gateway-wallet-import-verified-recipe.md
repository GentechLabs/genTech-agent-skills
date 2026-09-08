# Gateway Solana Wallet Import — Verified Working Recipe

Proven end-to-end Aug 20 2026: imported `DSvtQzkw...` as the Solana default wallet
via the Hummingbot API's own authenticated `GatewayClient`, with NO manual passphrase
interaction. Use this when a Condor LP/arb agent must sign on Solana and the gateway's
wallet store is empty (`conf/wallets/` empty, `/accounts/gateway/wallets` → `[]`).

## Why this works without the manual passphrase
The `hummingbot-api` container already holds the mTLS cert factory + `CONFIG_PASSWORD`.
Run the recipe INSIDE that container so the `gateway` hostname and certs resolve, and reuse
the API's `GatewayClient` (which builds its own SSL context from `settings.security.config_password`).

## Step 1 — read-only probe FIRST (never write before verifying the path is alive)
```python
# /tmp/probe.py  (copy into container, run in-container)
import asyncio, sys
sys.path.insert(0, "/hummingbot-api")
from services.gateway_client import GatewayClient
from config import settings
from utils.gateway_certs import build_client_ssl_context

async def m():
    c = GatewayClient("https://gateway:15888",
                      ssl_context_factory=lambda: build_client_ssl_context(settings.security.config_password))
    print("ping ->", await c.ping())                                   # must be True
    print("wallets ->", await c.get_wallets())                          # [] first time
    print("default sol ->", await c.get_default_wallet_address("solana"))  # placeholder before import
    await c.close()
asyncio.run(m())
```
```bash
docker cp /root/probe.py hummingbot-api:/tmp/probe.py
docker exec hummingbot-api sh -c "cd /hummingbot-api && python /tmp/probe.py"
```
Expect: `ping -> True`, `wallets -> []`, `default sol -> <placeholder>`. If ping is False,
the mTLS/certs/auth path is broken — fix before any write.

## Step 2 — the write (import wallet, set as default)
Pass the base58 secret via env; never hardcode it.
```python
# /tmp/add_wallet.py
import asyncio, os, sys
sys.path.insert(0, "/hummingbot-api")
from services.gateway_client import GatewayClient
from config import settings
from utils.gateway_certs import build_client_ssl_context

async def m():
    c = GatewayClient("https://gateway:15888",
                      ssl_context_factory=lambda: build_client_ssl_context(settings.security.config_password))
    print("add ->", await c.add_wallet("solana", os.environ["TRADE_B58"], set_default=True))
    print("wallets ->", await c.get_wallets())
    print("default sol ->", await c.get_default_wallet_address("solana"))
    await c.close()
asyncio.run(m())
```
```bash
B58="$(python3 - <<'PY'   # derive base58 from the 64-byte keypair, in-memory
import json
from solders.keypair import Keypair
kp = Keypair.from_bytes(bytes(json.load(open('/root/.solana-trade/trade-keypair.json'))))
A='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'; n=int.from_bytes(bytes(kp),'big'); s=''
while n>0: n,r=divmod(n,58); s=A[r]+s
pad=0
for x in bytes(kp):
    if x==0: pad+=1
    else: break
print('1'*pad+s)
PY
)"
docker cp /root/add_wallet.py hummingbot-api:/tmp/add_wallet.py
docker exec -e TRADE_B58="$B58" hummingbot-api sh -c "cd /hummingbot-api && python /tmp/add_wallet.py"
```
Expect `add -> {'address': '<the derived address>'}`.

## Step 3 — verify persistence (across calls, on disk)
- Encrypted file must exist at BOTH:
  - in the `gateway` container: `/home/gateway/conf/wallets/solana/{addr}.json`
  - on the host: `/hummingbot-api/bots/gateway-files/conf/wallets/solana/{addr}.json`
- Re-call `get_wallets()` in a FRESH session (new process) — the wallet must still be present
  (proves it was written to disk, not just held in memory).

## Hygiene
- Delete the temp `.py` probe/write scripts after use (`docker exec rm` + host rm).
- Verify the base58 secret is NOT in any log/vault/script (`grep` the container logs + cwd).
- The keypair file `/root/.solana-trade/trade-keypair.json` is chmod 600 — keep it that way.

## Follow-on (fund + verify race-readiness)
- Fund the gateway-derived address with SOL (see main skill: rent ~0.057 SOL/slot + 0.3 SOL
  reserve + swap gas ≈ $25-30).
- Verify `getBalance > 0` on-chain, then confirm the gateway can sign (swap quote/execute or
  `manage_executors(search, executor_types=["lp_executor"])` returns the RUNNING set).
