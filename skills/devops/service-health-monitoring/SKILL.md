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
`${PROFILE_DIR}/scripts/port-health-monitor.py`

## Services Checked

**Verified port map (Aug 9, 2026 audit — cross-checked via `ss -tlnp` + `/proc/PID/cwd`):**

**GenTech API fleet (systemd, Python uvicorn):**
- 3099 — x402 Test Harness (`x402-test.service`, node) → `gentechlabs.net`
- 8080 — Deal Tracker API (`deal-tracker-api.service`) → 10-Labs/deal-tracker-api
- 8082 — Crypto Price API (`crypto-price-api.service`) → 10-Labs/crypto-price-api
- 8084 — Gas Price API (`gas-price-api.service`) → 10-Labs/gas-price-api
- 8086 — Token Security API (`token-security-api.service`) → 10-Labs/token-security-api  ⛔ RETIRED 2026-09-15 (duplicate of rugcheck; gateway serves it)
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
- **A 200 does NOT mean the target exists — a catch-all route answers EVERY path, and it reads as a pass.** The inverse of the rule above, and the more dangerous direction: a vhost or SPA with a fallback (`try_files $uri $uri/ /index.html`, a wildcard route, or a custom error page that still returns 200) serves the SAME successful response for a path that exists and for one that never has. Measured: a game subdirectory returned **200** while the game had never been deployed — the real directory answered **403**; the 200 was the arcade's SPA fallback serving the root page. Nothing in the status code distinguishes them. **Always run a CONTROL probe against a deliberately nonsense path in the same namespace** (e.g. `/cabinet/definitely-not-a-game-xyz/`) and compare the **served content**, not the code: when the control returns the same status AND the same title/body, the probe has established nothing about the target. Cite a matched `<title>` (or a body fingerprint) as the evidence of liveness — never the status code alone.
- **`/health` 200 does NOT mean the service accepts work.** A concurrency cap can refuse every real request (`HTTP 429 Too many concurrent runs`) while `/health` and `/v1/models` both return 200 — measured on the gentech gateway for 9 minutes straight. The 429 gate is `active_agent_work_count()` (pending admissions + in-flight turns + live run tasks); `/health` never consults it. **Liveness = one real POST, not a status read.**
- **Do not probe your own api_server from inside its own turn.** If you run as the agent the gateway serves, a self-POST queues behind the turn issuing it — and it *consumes* the concurrency slot you are testing, so the probe can wedge the seat it is measuring. Probe from outside, or use the async `/v1/runs` path and poll it. A `000` on a timeout sized below real latency reads as "dead peer" but may only mean "slow".
- **Wait one polling cycle before declaring "needs an operator."** A transient that clears on its own and a wedge that genuinely needs a restart are the same picture at t+0. Poll twice before escalating; the measured case cleared in 9 min with the process PID unchanged (no restart was ever needed).
- **SSL cert mismatches** on subdomains (e.g., `demo.gentechlabs.net` using the main domain's cert) cause false positives. Use `-k` flag or check via HTTP first.
- **Cloudflare** can return 403 for requests without proper headers. Check from the VPS directly to bypass.
- **A systemd unit existing does NOT mean the service runs.** The x402-backend@<name> units + port drop-ins can exist but be disabled/inactive — the Aug 9, 2026 audit found treasury_defender (:8096) had a PORT=8096 drop-in but the unit was dead, causing a 502 on the defender URL. Always check `systemctl is-active` and `systemctl is-enabled` before assuming a backend is up; fix with `systemctl enable --now x402-backend@<name>`.
- **nginx 502 with a listener gap = dead backend.** Cross-check `grep -rnE "proxy_pass" /etc/nginx/sites-enabled/` ports against `ss -tlnp`; every proxied port must be listening.
- **cad.gentechlabs.net → :5188 → 502 is EXPECTED** when Forge's laptop is offline (VPS proxies to Forge's local Vite dev server). Check vault agent-brain notes before treating it as a bug.
- **Test the real route, not the nginx prefix.** treasury_defender routes are mounted under `/demo/v1/defender/...`, so the bare prefix `/demo/v1/defender/` 404s while `/demo/v1/defender/classify/{chain}/{token}` returns 200. The 404 on the prefix is normal.
- **Two endpoints that name the same subject must be verified to AGREE, not each verified to work.** Measured on sovereign-router402 (Sep 15): `POST /score {"name":"gpt-oss:120b"}` returned **85/Poor** while `POST /route` returned **529/Fair** for the same model, both advertised and payable through the public gateway. `/score` built its profile from the request body alone and never consulted the candidate pool `/route` reads, so each endpoint was individually "working" — the defect lived strictly in the disagreement. **Fix pattern:** when a paid endpoint accepts an identifier for an entity the service already holds, resolve the held entity instead of scoring an empty shell, and **return which source was used** (`scored_profile_source: registered|supplied`) so a caller can never be unsure what was scored. **Test pattern:** assert equality across the two paths for every registered entity, and run the new test against base — the base run is what proves the test can fail.

