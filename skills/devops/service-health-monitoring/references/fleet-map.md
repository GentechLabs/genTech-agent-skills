# GenTech API Fleet — Audit Recipe & Findings

## When to run
Jordan asks "look at our APIs and ports", "what's running", or a port/URL is
down. This is the read-only inventory that maps every listener to a service
and surfaces dead nginx backends.

## Audit recipe (validated Aug 9, 2026)

1. **List all listeners with owning processes:**
   ```bash
   ss -tlnp 2>/dev/null | grep -E "LISTEN" | sort -t: -k2 -n
   ```

2. **Identify each Python/Node service by its working directory:**
   ```bash
   for pid in <pids from ss>; do
     echo "=== PID $pid ==="; ls -l /proc/$pid/cwd | awk '{print $NF}'
     tr '\0' ' ' < /proc/$pid/cmdline | head -c 200; echo
   done
   ```
   The cwd reveals the project (e.g. `/root/vaults/gentech/10-Labs/deal-tracker-api`).

3. **Probe HTTP health per port** — `/docs` returns 200 only if FastAPI is up:
   ```bash
   for p in 8080 8082 8084 8086 8088 8090 8091 8092 8093 8094 8095; do
     curl -s --max-time 5 "http://127.0.0.1:$p/docs" -o /dev/null -w "docs: %{http_code}\n"
     curl -s --max-time 5 "http://127.0.0.1:$p/v1/health" | head -c 200; echo
   done
   ```
   Most GenTech backends expose `/v1/health` → `{"status":"ok",...}`.

4. **Cross-check nginx backends against listeners** — the dead-backend finder:
   ```bash
   grep -rnE "proxy_pass" /etc/nginx/sites-enabled/ | \
     awk -F'proxy_pass http://127.0.0.1:' '{print $2}' | cut -d'/' -f1 | cut -d';' -f1 | sort -u
   ```
   Every port in this list MUST appear in `ss -tlnp`. Any port missing = a
   dead backend (502 through nginx). (Aug 9 found exactly two: 5188 and 8096.)

5. **Confirm public URL impact:**
   ```bash
   for host in gentechlabs.net api.gentechlabs.net rugcheck.gentechlabs.net ...; do
     curl -s -o /dev/null -w "$host -> %{http_code}\n" --max-time 8 "https://$host/"
   done
   ```

## Known dead/expected-gap backends

- **cad.gentechlabs.net → :5188 → 502 is EXPECTED** when Forge's laptop is
  offline. The VPS nginx proxies to a Vite dev server that runs on Forge's
  machine (see vault notes `11-Mess Hall/agent-brain/*` and
  `01-HANDOFFS/for-the-forge.md`). Not a VPS fault — do not chase it as a bug.
- **Treasury Defender (:8096) was DISABLED, not missing** — the unit
  `x402-backend@treasury_defender.service` and its PORT=8096 drop-in existed
  but the unit was `inactive (dead)` and not enabled. Fix:
  ```bash
  systemctl enable --now x402-backend@treasury_defender.service
  systemctl is-active x402-backend@treasury_defender.service  # → active
  ```
  Then verify the real route (nginx prefix is /demo/v1/defender/):
  ```bash
  curl -s -o /dev/null -w "%{http_code}\n" \
    "https://gentechlabs.net/demo/v1/defender/classify/8453/0x0000000000000000000000000000000000000000"  # 200
  ```
  Note: the FastAPI routes are mounted under `/demo/v1/defender/...`, so the
  bare prefix `/demo/v1/defender/` returns 404 — that's normal, the classified
  route is the real test.

## x402 backend systemd pattern

- Template unit: `/etc/systemd/system/x402-backend@.service`
  - WorkingDirectory=/root/gentechlabs/services
  - ExecStart=`/usr/local/lib/hermes-agent/venv/bin/python3 %i.py`
  - EnvironmentFile=/root/.hermes/profiles/gentech/.env
- Per-service drop-in: `/etc/systemd/system/x402-backend@<name>.service.d/port.conf`
  - e.g. `Environment=PORT=8096` for treasury_defender (its py default is 8095;
    the drop-in overrides to 8096 to match nginx)
- Backend scripts live in `/root/gentechlabs/services/*.py`, each a FastAPI app
  with `uvicorn.run(app, port=int(os.getenv("PORT", "<default>")))`.
- **Pitfall:** a unit + drop-in existing does NOT mean the service runs. Always
  check `systemctl is-active x402-backend@<name>` and `systemctl is-enabled`
  before assuming the backend is up.

## Verified port map (Aug 9, 2026)

| Port | Service | systemd unit | Public |
|------|---------|--------------|--------|
| 3099 | x402 Test Harness (node) | x402-test | gentechlabs.net |
| 8080 | Deal Tracker API | deal-tracker-api | — |
| 8082 | Crypto Price API | crypto-price-api | — |
| 8084 | Gas Price API | gas-price-api | — |
| 8086 | Token Security API | token-security-api | — |
| 8088 | Rugcheck v2 (sim mode) | rugcheck-api | rugcheck.gentechlabs.net |
| 8090 | x402 Gateway v2.0 | x402-api | api.gentechlabs.net |
| 8091 | agent_discovery | x402-backend@agent_discovery | — |
| 8092 | defi_lp_analytics | x402-backend@defi_lp_analytics | — |
| 8093 | wallet_analysis | x402-backend@wallet_analysis | — |
| 8094 | nft_search | x402-backend@nft_search | — |
| 8095 | lineage_guard | x402-backend@lineage_guard | — |
| 8096 | treasury_defender | x402-backend@treasury_defender | gentechlabs.net/demo/v1/defender/ |
| 8765 | hermes-bridge | gentech-bridge | — |
| 8402 | ClawRouter proxy (node) | clawrouter-proxy | — |
| 8011 | ClawWork router | clawwork-router | — |
| 9119 | Hermes dashboard | hermes-dashboard | — |

Docker infra: 3306 MySQL (datahub), 5432 Postgres (hummingbot), EMQX broker
1883/8883/18083/61613 + dashboards 8097-8099, trek :3002, multica :3001/:8081,
rota :8000, hummingbot gateway :15888.

## Old monitor mapping that was WRONG (fixed Aug 9)
The earlier port-health-monitor listed 8080=Token Security, 8082=Wallet
Analysis, 8086=Rug Check. Verified reality: 8080=Deal Tracker, 8082=Crypto
Price, 8086=Token Security, 8088=Rugcheck. The port map in this reference is
authoritative.
