# Hummingbot Gateway — Solana Wallet Wiring & Reachability

How the Condor trading agents connect to and sign on Solana (verified Aug 20 2026
during Meteora/Agent Builders Cup setup). Read BEFORE setting up or funding a
Solana signing wallet for any Condor/hummingbot agent.

## Signing path (do NOT assume a keypair file is wired in)
```
consigliere strategy → HummingbotAPIClient → Hummingbot API (:8002) → Gateway (:15888) → signs on-chain
```
- The executor calls `manage_executors` / `order_executor` through the Hummingbot API client.
- The gateway signs with **ITS OWN encrypted wallet store**, NOT a loose keypair file on disk.
  Store lives at `conf/wallets/{chain}/{address}.json` (inside the `gateway` container).
- **A generated keypair file is NOT sufficient** — the executor never reads it. It must be
  imported into the gateway's wallet store to become the funded signing wallet.

## Gateway reachability (it's HTTPS mTLS, not plain HTTP)
- Gateway container `gateway` exposes `127.0.0.1:15888->15888/tcp`.
- It speaks **HTTPS with client certs** (`certs/` in container) — it REJECTS plain `http://`
  requests (curl returns `000`). This is expected, not a dead gateway.
- The Hummingbot API reaches it via `https://gateway:15888` using shared mTLS certs
  (`services/gateway_service.py`, `GatewayClient` in `services/gateway_client.py`).
- **Health signal that actually works:** the gateway logs `Getting all wallets` ~every minute
  (that is the API's background poller succeeding). `GET /accounts/gateway/wallets` returning
  200 (even `[]`) proves the API↔gateway link is alive.
- Do NOT diagnose reachability with raw curl to :15888 — it will always look dead.

## Importing a Solana keypair into the gateway (the correct way to make it sign)
- Endpoint: `POST /wallet/add` (registered under prefix `/wallet` → `POST /wallet/add`).
- Body: `{"chain":"solana","privateKey":"<base58 secret>","setDefault":true}`.
- **Solana private key must be BASE58**, not the 64-byte JSON array format.
  The gateway does `bs58.decode(priv) -> Keypair.fromSecretKey(new Uint8Array(decoded))`.
  Invalid format → `Unable to retrieve wallet address for provided private key`.
- It encrypts the key with the gateway's wallet-encryption key and writes
  `conf/wallets/solana/{address}.json` (mode 0600).
- This step needs the gateway API username/password + `GATEWAY_PASSPHRASE` (auth-gated,
  interactive). Prefer importing through the API's authenticated `GatewayClient` passthrough
  (the API already proxies swap/CLMM calls) over raw curl to the gateway.

## Generating a fresh Solana signing keypair
`solders` is available in system python. Use it (NOT solana-keygen, which may be absent):
```python
from solders.keypair import Keypair
kp = Keypair()
print(str(kp.pubkey()))              # address
open('trade-keypair.json','w').write(json.dumps(list(bytes(kp))))  # 64-byte array, chmod 600
```
Round-trip verify: `Keypair.from_bytes(bytes(json.load(open(f))))` must re-derive the address.

Convert the 64-byte array to base58 for the gateway import (bs58 encode of `bytes(kp)`).

## Verify "funded ≠ usable"
- `getBalance` > 0 on-chain (via Solana mainnet RPC).
- Gateway can sign a test tx / `manage_executors(search, executor_types=["lp_executor"])`
  returns the RUNNING set → proves the gateway wallet is what the strategy sees.

## Pitfalls
- Never pass a swap's reported fill straight to `base_amount` (Jupiter takes its cut);
  haircut `× 0.995` or the LP open fails on-chain.
- A treasury/payTo address (e.g. x402 `X402_PAYTO_SOLANA`) is receive-only with NO signing
  key — cannot sign LP/swap txs. A real signing keypair is a separate artifact.
