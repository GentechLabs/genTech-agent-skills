# Add a New Paid x402 Endpoint to the Gateway (proven Aug 18, 2026)

The bread-and-butter play: package a capability (e.g. the ClawWork-proven research
agent) as a sellable x402 endpoint on our own gateway, then prove the payment loop
lands in the treasury. This is the full, verified workflow.

## The 5 wiring points (all required)

1. **Backend service** — `/root/gentechlabs/services/<name>.py`. Model on an existing
   one (e.g. `wallet_analysis.py`). It must:
   - Return **HTTP 402** when `X-Payment-Proof` header is absent (the front gate
     enforces payment; the backend re-checks as defense-in-depth).
   - Do the real work when the proof header is present.
   - Run on a **free port** (check `ss -tlnp` first — 8098/8099 are Docker, use 8100+).
   - Default port in `__main__` must match the systemd `PORT` (or set `PORT` env).

2. **Gateway routing** — `/root/vaults/gentech/10-Labs/x402-gateway/server.py` (the
   LIVE copy; the systemd unit runs from the vault, not `/root/gentechlabs`):
   - `BACKEND_ROUTES[<key>] = (backend_base, public_prefix, backend_prefix)`
   - `URL_TO_SERVICE[<public_segment>] = <key>`
   - The public URL is `/v1/<public_segment>/...`; the router strips `public_prefix`
     from the path and applies `backend_prefix`.

3. **Manifest** — `/var/www/gentechlabs/.well-known/x402-bazaar`:
   - Add `services[<key>]` with description, endpoint, chains, `price_usd`.
   - **Bump `version`** (e.g. 9.2.0 → 9.3.0). The manifest version is what discovery
     layers and the landing page report.

4. **systemd backend service** — `/etc/systemd/system/x402-backend@<name>.service`
   (template pattern, same as the other backends):
   ```ini
   [Service]
   Type=simple
   WorkingDirectory=/root/gentechlabs/services
   EnvironmentFile=/root/.hermes/profiles/gentech/.env
   ExecStart=/usr/local/lib/hermes-agent/venv/bin/python3 <name>.py
   Restart=always
   RestartSec=3
   ```
   Then `systemctl daemon-reload && systemctl enable --now x402-backend@<name>`.

5. **Restart the gateway** — `systemctl restart x402-api.service` to load the new
   routing + manifest. Verify `/health` reports the new service count.

## Verify (in order)

```bash
# backend health
curl -s http://127.0.0.1:<port>/v1/health
# no-proof → must be 402
curl -s "http://127.0.0.1:<port>/v1/agent/research?task=summary&topic=test"
# with-proof → real deliverable
curl -s -H "X-Payment-Proof: test" "http://127.0.0.1:<port>/v1/agent/research?task=summary&topic=..."
# gateway serves 402 challenge (paid endpoint)
curl -s -D - "http://127.0.0.1:8090/v1/agent/research?task=summary&topic=test" | grep -iE 'HTTP/|payment-required'
# manifest has the service + bumped version
curl -s http://127.0.0.1:8090/.well-known/x402-bazaar | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['version'], d['services'].keys())"
# public URL reachable (paid → 402 is CORRECT)
curl -s -o /dev/null -w "%{http_code}" "https://api.gentechlabs.net/v1/agent/research?task=summary&topic=test"
```

## Self-settle to prove the loop (and trigger auto-cataloging)

Use `self-settle.mjs` in the gateway dir (needs `@dexterai/x402` + `viem` installed
via `npm install`). Requires a Base wallet you hold the key to WITH USDC + a little
ETH for gas. The owner wallet `0x7ebf…96a` has USDC but no key on the box; the
remit-test wallet `0x3679…AE93` has a key but needs funding.

```bash
EVM_PRIVATE_KEY=<hex> SELF_SETTLE_URL="https://api.gentechlabs.net/v1/agent/research?task=summary&topic=test" SELF_SETTLE_CAP="100000" node self-settle.mjs
```

## ⚠️ HTTP 200 is NOT proof of settlement — verify on-chain

The settle script prints "✅ PAID" on an HTTP 200, but that only means the facilitator
accepted it. **Always confirm the USDC actually moved** via raw RPC `eth_getLogs`
(blockscout can time out):

```python
# Transfer event to the treasury wallet, last N blocks
transfer_sig = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
# eth_getLogs: address=USDC, topics=[transfer_sig, None, "0x0000...<treasury>"[2:].lower()]
# amount = int(log["data"],16)/1e6 ; sender = "0x"+log["topics"][1][-40:]
```

Cross-check the payer balance dropped by exactly the price (e.g. 1.00 → 0.95 USDC for
a $0.05 settle). Then log it in the Revenue Monitor tracker
(`/root/.hermes/profiles/gentech/scripts/revenue-tracker.json`) and sync to the vault.

## Landing page update

`/var/www/gentechlabs/index.html` — add a card for the new service, bump the
"X production APIs" count, and add a "First Settlement Verified" proof card. Verify
the public site serves the new content (`curl -s https://gentechlabs.net | grep ...`).
