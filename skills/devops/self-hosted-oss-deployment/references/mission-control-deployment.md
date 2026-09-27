# Mission Control Deployment

**Project:** https://github.com/builderz-labs/mission-control  
**Purpose:** AI agent orchestration dashboard (32 panels, multi-agent coordination)  
**Demo Value:** OKX hackathon presentation layer — "no black boxes, full visibility"

---

## One-Command Install Pattern

```bash
cd /root
git clone https://github.com/builderz-labs/mission-control.git
cd mission-control
bash install.sh --local
```

The installer handles:
- ✅ Node.js 22+ detection
- ✅ pnpm installation and dependencies (973 packages)
- ✅ Native module compilation (better-sqlite3, node-pty, sharp)
- ✅ Secure `.env` generation with auto-generated AUTH_SECRET and API_KEY
- ✅ Database migrations
- ✅ Scheduler initialization

---

## Build and Run

```bash
# Build (already done by installer, but available for rebuild)
pnpm build

# Production (standalone mode)
cd .next/standalone
node server.js
```

**Note:** Standalone mode requires `.next/standalone/server.js`, NOT `pnpm start` (which needs full `node_modules`).

---

## Background Deployment with Hermes

```python
# Start in background
terminal(
    background=True,
    notify_on_complete=True,
    command="cd /root/mission-control && node .next/standalone/server.js"
)

# Verify health
sleep 3
curl -s http://localhost:3000/health
```

Expected output: `{"status":"ok","db":"ok","ts":"2026-07-05T14:25:38.529Z"}`

---

## Credentials

Auto-generated credentials stored in `.next/standalone/.data/.auto-generated`:

```bash
AUTH_SECRET=378c7e958dfe7ff214a7af429e4f9f2d9f18bfe2b2569bb755ebd642aafede5c
API_KEY=61472633547acc929fc18a5cacc760c979ec799ae10ae960489719aa9ee742d9
```

Setup URL: `http://localhost:3000/setup`

---

## Key Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/health` | Health check (status, db, timestamp) |
| `/setup` | Admin account creation (if AUTH_PASS not set) |
| `/docs` | OpenAPI interactive docs |
| `/api/...` | 101 REST API routes |

---

## Demo Value for OKX Hackathon

**Narrative:** "We didn't just build agents — we built an operations center. One dashboard, 32 panels, real-time agent fleet coordination."

| Panel | What Judges See |
|-------|-----------------|
| Agent Management | Gentech (VPS) + Forge (desktop) live status |
| Kanban Task Board | Build queue flowing from inbox → done |
| Cost Tracking | x402 payments transparent, per-model breakdown |
| Security Audit | Trust scores, MCP call auditing — enterprise-ready |
| Skills Hub | Browse + install skills instantly — ecosystem integration |
| Activity Feed | Real-time agent operations via WebSocket/SSE |
| Memory Graph | Knowledge relationships visualized |
| Cron Scheduler | Natural language recurring tasks |

**Demo Script Hook:**
1. Open Mission Control → 32 panels load instantly
2. Show agent fleet → Gentech + Forge both online
3. Pull build queue → Tasks flowing through Kanban columns
4. Trigger cost panel → x402 payment history visible
5. Security audit → Trust score 98/100, no vulnerabilities
6. Skills Hub → "Click install, agent gets new capability"

"See? No black boxes. Full visibility."

---

## MCP Integration (Optional)

Mission Control provides 35 MCP tools for agent control:

```bash
# Add MCP server
claude mcp add mission-control -- node /path/to/mission-control/scripts/mc-mcp-server.cjs

# Environment config
export MC_URL=http://127.0.0.1:3000
export MC_API_KEY=<key>
```

---

## Pitfalls

1. **Build interruptions** — The install script can be interrupted. Use `process(poll)` to check status.
2. **Turbopack warnings** — 67 NFT warnings during build are cosmetic. Real errors appear at the end.
3. **Auth setup** — If `AUTH_PASS` not set, admin must create account via `/setup`. For headless/CI, set `AUTH_USER`/`AUTH_PASS` in `.env`.
4. **Port conflicts** — Default port is 3000. Check with `ss -tlnp | grep 3000` before starting.