# Adding a paid service + building the docs page (GenTech gateway, Aug 2026)

End-to-end pattern for putting a NEW sellable x402 endpoint on our own gateway and
shipping the `/docs` conversion page. Proven live Aug 18 2026 with the `agent_research`
endpoint (local-LLM research/summary/analysis at $0.05/call) and the first verified
on-chain settlement.

## 1. Build the backend service (port 8100)

Standalone FastAPI service in `/root/gentechlabs/services/<name>.py`:
- `/v1/health` → `{"status":"ok"}`
- `/v1/<service>/...` routes do the real work
- Gate every paid route on `X-Payment-Proof` header; return 402 JSON if missing
- Use a **local LLM proxy** (ClawWork router on `127.0.0.1:8011`, open, no auth) so the
  backend has zero external API cost. Point at an Ollama model, e.g. `deepseek-v4-flash:0731`.

## 2. Wire it into the gateway (2 lines)

`/root/vaults/gentech/10-Labs/x402-gateway/server.py`:
- `BACKEND_ROUTES["<key>"] = ("http://127.0.0.1:8100", "<public_prefix>", "/v1/<svc>/")`
- `URL_TO_SERVICE["<url_segment>"] = "<key>"`

The public path prefix strip + backend prefix prepend happens in `_route_to_backend`.

## 3. Add to the manifest + bump version

`/var/www/gentechlabs/.well-known/x402-bazaar`:
- bump `version` (e.g. 9.2.0 → 9.3.0)
- add `services["<key>"] = {description, endpoint, chains, price_usd}`

## 4. Run as a systemd template unit

Copy the existing `x402-backend@.service` template. One-off instance:
`/etc/systemd/system/x402-backend@agent_research.service`:
```ini
[Unit]
Description=GenTech x402 Backend - agent_research
After=network.target
[Service]
Type=simple
WorkingDirectory=/root/gentechlabs/services
EnvironmentFile=/root/.hermes/profiles/gentech/.env
ExecStart=/usr/local/lib/hermes-agent/venv/bin/python3 agent_research.py
Restart=always
RestartSec=3
[Install]
WantedBy=multi-user.target
```
Then `systemctl daemon-reload && systemctl enable x402-backend@<name> && systemctl start x402-backend@<name>`.
Verify: `systemctl is-active` + `curl localhost:8100/v1/health`.

## 5. Restart the gateway to load new routing

`systemctl restart x402-api.service`, then verify `/health` reports the new service count.

## 6. Verify the FULL loop (receive side, not just 402 emission)

- `curl <endpoint>` (no proof) → HTTP 402 with a valid x402 v2 challenge
- `curl -H "X-Payment-Proof: test" <endpoint>` → HTTP 200 with a REAL deliverable
- `https://api.gentechlabs.net/v1/...` public → 402 (correct paywall)
- gateway `/health` → `{"gateway":"x402-v2","services":N}`

## 7. Self-settle to prove the money lands (on-chain proof)

Use the existing `self-settle.mjs` in `/root/vaults/gentech/10-Labs/x402-gateway/`:
```bash
cd /root/vaults/gentech/10-Labs/x402-gateway && npm install   # first time: needs @dexterai/x402 + viem
EVM_PRIVATE_KEY=<key> SELF_SETTLE_URL="https://api.gentechlabs.net/v1/agent/research?task=summary&topic=test" SELF_SETTLE_CAP="100000" node self-settle.mjs
```

**CRITICAL — an HTTP 200 from payAndFetch is NOT settlement proof.** The self-settle.mjs
prints "✅ PAID" + a real deliverable, but that only proves the HTTP loop. You MUST verify
on-chain that USDC actually moved. Payer balance dropping by exactly the price is the
ground-truth signal; confirm the receiving wallet got it via raw RPC `eth_getLogs` on the
`Transfer` event:
```python
# Transfer sig, USDC on Base, scan last N blocks for logs TO treasury
transfer_sig = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
# eth_getLogs {fromBlock, toBlock, address: USDC, topics:[transfer_sig, null, pad(treasury)]}
# amount = int(log["data"],16)/1e6  (0.050000 in the verified Aug 18 settlement)
```

**Funding-gap trap (check before you claim you can self-settle):** self-settlement needs a
wallet you hold the key for that ALSO holds USDC + gas on the target chain. These frequently
split: the revenue owner wallet has USDC but no key in env; the signable wallet has a key but
no USDC. Verify both balances on-chain before promising a settlement (raw `eth_call` balanceOf
+ `eth_getBalance`). If the funded wallet has no key, the task is "fund the signable wallet,"
not "settle."

## 8. Build the `/docs` page (conversion surface)

The FastAPI gateway is created with `docs_url=None`, so `/docs` 404s by default, and nginx
proxies `/` to the gateway. Fix by serving a STATIC HTML page at `/docs` via nginx (bypasses
the gateway entirely):
1. Write `/var/www/gentechlabs/api-docs.html` — dark-themed, service catalog table + per-service
   cards with copy-paste curl examples + a settlement-proof callout.
2. Add to BOTH the HTTP and HTTPS `api.gentechlabs.net` server blocks in
   `/etc/nginx/sites-enabled/gentech`:
   ```
   location /docs {
       alias /var/www/gentechlabs/api-docs.html;
       default_type text/html;
   }
   ```
3. `nginx -t` (warnings about pre-existing duplicate server blocks are normal — ignore),
   `nginx -s reload`.
4. Verify: `curl -o /dev/null -w "%{http_code}" https://api.gentechlabs.net/docs` → 200,
   and the gateway `/health` still reports the service count (docs page must NOT break proxying).

## Order of operations
Backend → gateway wiring → manifest bump → systemd start → gateway restart → full-loop verify
→ self-settle + on-chain proof → docs page → log settlement in Revenue Monitor tracker
(`revenue-tracker.json`: append tx, bump `total_revenue_usd`, add `revenue_by_service.<key>`)
→ commit + push vault.
