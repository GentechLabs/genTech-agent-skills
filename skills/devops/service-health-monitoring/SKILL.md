---
name: service-health-monitoring
description: Monitoring backend services, ports, and public URLs on the GenTech VPS — with cron-based alerts
category: devops
---

# Service Health Monitoring

## When to use
- Setting up monitoring for backend services
- Checking if all ports and public URLs are healthy
- Creating alerting when services go down
- Auditing which services are running

## The Pattern
The Port Health Monitor is a no-agent cron script that:
1. Checks each backend port via SSH (`ss -tlnp | grep -E ':<port> '`) — TCP-level, not HTTP-level
2. Checks public URLs via HTTP (any response = alive, even 4xx/5xx)
3. Reports only on failure (silent when healthy)
4. Delivers to the origin chat so the user sees it

## Script Location
`/root/.hermes/profiles/gentech/scripts/port-health-monitor.py`

## Services Checked

**Verified port map (Aug 9, 2026 audit — cross-checked via `ss -tlnp` + `/proc/PID/cwd`):**

**GenTech API fleet (systemd, Python uvicorn):**
- 3099 — x402 Test Harness (`x402-test.service`, node) → `gentechlabs.net`
- 8080 — Deal Tracker API (`deal-tracker-api.service`) → 10-Labs/deal-tracker-api
- 8082 — Crypto Price API (`crypto-price-api.service`) → 10-Labs/crypto-price-api
- 8084 — Gas Price API (`gas-price-api.service`) → 10-Labs/gas-price-api
- 8086 — Token Security API (`token-security-api.service`) → 10-Labs/token-security-api
- 8088 — Rugcheck v2 API (`rugcheck-api.service`, sim mode) → /root/rugcheck/api → `rugcheck.gentechlabs.net`
- 8090 — x402 Gateway v2.0 (`x402-api.service`) → `api.gentechlabs.net`
- 8091–8096 — x402 backends (`x402-backend@.service` template): agent_discovery, defi_lp_analytics, wallet_analysis, nft_search, lineage_guard, treasury_defender
- 8765 — hermes-bridge (`gentech-bridge.service`)

**Infra:**
- 8402 ClawRouter proxy | 8011 ClawWork router | 9119 Hermes dashboard
- Docker: 3306 MySQL (datahub), 5432 Postgres (hummingbot), EMQX broker (1883/8883/18083/61613/8097-8099), trek :3002, multica :3001/:8081, rota :8000, hummingbot gateway :15888

**Public URLs (HTTP response check — any response = alive):**
- `https://gentechlabs.net` (→3099)
- `https://api.gentechlabs.net` (→8090)
- `https://rugcheck.gentechlabs.net/v1/health` (→8088)
- `https://gentechlabs.net/demo/v1/defender/classify/{chain}/{token}` (→8096)
- `https://yield.gentechlabs.net`, `https://arcade.gentechlabs.net`

Full audit recipe + verified port table: see `references/fleet-map.md`.
NOTE: the OLD monitor mapping (8080=Token Security, 8082=Wallet Analysis,
8086=Rug Check) was wrong — the reference file table is authoritative.

## Cron Schedule
Twice daily: `0 6,18 * * *` (6am/6pm ET)
Job ID: `eb6fffc08d0e`
Created: Jul 28, 2026 (replaced earlier port health check that was paused)

## Key Design Decisions
- **TCP-level check** (is the port open?) rather than HTTP-level (is there a /health endpoint?). Backends may not have a /health endpoint but are still running.
- **Silent on success** — only alerts when something is down. No noise.
- **No-agent mode** — the script runs standalone, no LLM cost per tick.
- **SSH-based** for port checks (can't check internal ports from outside).

## Pitfalls
- **4xx responses are NOT failures** — they mean the server is alive but the endpoint doesn't exist. Only 5xx, timeouts, and connection refused are real failures.
- **SSL cert mismatches** on subdomains (e.g., `demo.gentechlabs.net` using the main domain's cert) cause false positives. Use `-k` flag or check via HTTP first.
- **Cloudflare** can return 403 for requests without proper headers. Check from the VPS directly to bypass.
- **A systemd unit existing does NOT mean the service runs.** The x402-backend@<name> units + port drop-ins can exist but be disabled/inactive — the Aug 9, 2026 audit found treasury_defender (:8096) had a PORT=8096 drop-in but the unit was dead, causing a 502 on the defender URL. Always check `systemctl is-active` and `systemctl is-enabled` before assuming a backend is up; fix with `systemctl enable --now x402-backend@<name>`.
- **nginx 502 with a listener gap = dead backend.** Cross-check `grep -rnE "proxy_pass" /etc/nginx/sites-enabled/` ports against `ss -tlnp`; every proxied port must be listening.
- **cad.gentechlabs.net → :5188 → 502 is EXPECTED** when Forge's laptop is offline (VPS proxies to Forge's local Vite dev server). Check vault agent-brain notes before treating it as a bug.
- **Test the real route, not the nginx prefix.** treasury_defender routes are mounted under `/demo/v1/defender/...`, so the bare prefix `/demo/v1/defender/` 404s while `/demo/v1/defender/classify/{chain}/{token}` returns 200. The 404 on the prefix is normal.
