# LLM-Backed Paid x402 Backend + Port-Conflict Pitfall (Aug 2026)

How to add a NEW paid service to the unified `api.gentechlabs.net` gateway whose
backend is an **LLM call** (not a data-source wrapper). Proven with `agent_research`
(port 8100, $0.05/call) — packaging the ClawWork-proven capability (research,
analysis, document creation, summarization) as a directly-sellable endpoint.

## The LLM-backed backend pattern

A paid backend that generates a deliverable via the local LLM proxy instead of
wrapping an external data API. Same 4-edit gateway wiring as any backend, but the
backend file calls the local proxy.

**Backend file** `/root/gentechlabs/services/<key>.py` — a self-contained FastAPI app:
- Gate on `X-Payment-Proof` header → return 402 if absent (matches the gateway's
  `_route_to_backend` which forwards the proof on `X-Payment-Proof`).
- Define a `TASKS` dict mapping task type → (description, system prompt). Each task
  is a distinct deliverable shape (research report, analysis verdict, document, summary).
- Call the local LLM proxy (no external cost): `POST {LLM_PROXY}/v1/chat/completions`
  with `{model, messages:[{role:system},{role:user}], temperature, max_tokens}`.
- `LLM_PROXY` default `http://127.0.0.1:8011` (the ClawWork router → Ollama, open/no-auth).
- `LLM_MODEL` default `deepseek-v4-flash:0731`.
- `__main__` runs `uvicorn.run(app, port=int(os.getenv("PORT", "<port>")))`.

**Verify the proxy is up + which models it serves before wiring:**
```bash
curl -s http://127.0.0.1:8011/v1/models   # open, no auth needed
```

## The 4 gateway edits (same as any backend)

1. `BACKEND_ROUTES` in `server.py`:
   `"agent_research": ("http://127.0.0.1:8100", "agent/", "/v1/agent/"),`
2. `URL_TO_SERVICE`: `"agent": "agent_research",`
3. Manifest `/var/www/gentechlabs/.well-known/x402-bazaar` → `services.agent_research`
   with `description`, `endpoint`, `chains`, `price_usd`. Bump `version` (e.g. 9.2.0 → 9.3.0).
4. systemd: `x402-backend@agent_research.service` (template unit, WorkingDirectory
   `/root/gentechlabs/services`, ExecStart `python3 agent_research.py`). Enable + start.

**Restart gateway:** `systemctl restart x402-api`. Verify:
```bash
curl -s http://localhost:8090/health          # services count bumped (e.g. 11)
curl -s -D - "http://localhost:8090/v1/agent/research?task=summary&topic=test" -o /dev/null | grep -i 402   # payment wall
curl -s -H "X-Payment-Proof: test" "http://localhost:8090/v1/agent/research?task=summary&topic=..."  # real deliverable
curl -s -o /dev/null -w "%{http_code}" "https://api.gentechlabs.net/v1/agent/research?task=summary&topic=test"  # 402 public
```

## ⚠️ Port-conflict pitfall (the #1 gotcha)

Do NOT assume the next number after the last gateway backend is free. **Docker
containers occupy 8097-8099** (docker-proxy), so a new backend at 8098 fails with
`[Errno 98] address already in use` even though nothing "looks" taken. Check first:
```bash
for p in 8098 8099 8100 8101; do ss -tln | grep -q ":$p " || echo "$p FREE"; done
```
Use the first free port (8100+). The backend's `__main__` `uvicorn.run(port=...)`
default MUST match the port in `BACKEND_ROUTES` step 1 — a mismatch means the systemd
service binds one port while the gateway proxies to another.

## Why this over agent marketplaces (Jordan's direction, Aug 18)

Jordan cancelled the marketplace cron jobs: "our apis and services are our bread and
butter." The agent marketplaces (dealwork, AgentLux, etc.) are supply-heavy and
demand-light — every listing is another agent selling, almost nobody buying. The real
earning rail is our own paid APIs: a customer pays USDC → lands in the treasury wallet
→ Revenue Monitor catches it. No simulation, no fake receipts. The ClawWork agent
proved the *capability*; packaging it as a paid endpoint is how it becomes real income.
