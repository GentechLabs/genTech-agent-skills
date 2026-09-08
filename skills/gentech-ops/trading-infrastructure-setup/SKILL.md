---
name: trading-infrastructure-setup
description: "Install and configure Condor + Hummingbot API + Tailscale for autonomous trading agents. Covers VPS setup, Tailscale private networking, Hummingbot API manual install (bypassing interactive prompts over SSH), Condor cloning, and verification."
tags: [trading, hummingbot, condor, tailscale, vps, infrastructure, agent-builders-cup]
trigger: "When setting up a new trading agent infrastructure — installing Condor, Hummingbot API, or Tailscale on a VPS. When the user says 'let's get Condor running' or 'install the trading API'. When preparing for a trading hackathon (Agent Builders Cup, etc.)."
version: 1.0.0
author: Gentech
---

# Trading Infrastructure Setup

## Purpose
Install and wire together the three components needed to run autonomous trading agents: Tailscale (private network), Hummingbot API (execution layer), and Condor (LLM agent harness).

## Architecture
```
Your Machine (Windows/Mac)          VPS (Linux)
┌─────────────────────┐             ┌──────────────────────┐
│  Condor (Telegram)  │◄─Tailnet──►│  Hummingbot API       │
│  or Condor Web UI   │  encrypted │  (port 8000)          │
│                     │  tunnel    │  ┌────────────────┐   │
│                     │            │  │ Tailscale       │   │
│                     │            │  │ sidecar         │   │
│                     │            │  └────────────────┘   │
│                     │            │  Hummingbot Gateway   │
│                     │            │  (Solana DEXs)        │
└─────────────────────┘            └──────────────────────┘
```

## Step 1: Tailscale Setup

### Prerequisites
- Tailscale account (free tier is enough)
- Auth key from https://login.tailscale.com/admin/settings/keys

### On the VPS
```bash
# Check if Tailscale is already installed
which tailscale && tailscale status

# If already on an old tailnet, leave it
tailscale logout

# Join new tailnet with auth key
tailscale up --auth-key tskey-auth-XXXXXXXX --hostname hummingbot-api --accept-dns=true

# Verify
tailscale status
# Should show: 100.x.x.x  hummingbot-api  you@  linux  -
```

### On the User's Machine
- Install Tailscale from https://tailscale.com/download
- Sign in with the same account
- Verify both machines appear in `tailscale status`

### MagicDNS
- Enable at https://login.tailscale.com/admin/dns
- After enabling, the VPS resolves as `hummingbot-api` (or whatever hostname you set)
- Verify: `host hummingbot-api` should return the Tailscale IP
- If MagicDNS doesn't show as enabled on the VPS after toggling, restart Tailscale:
  ```bash
  tailscale down && sleep 2 && tailscale up --auth-key KEY --hostname hummingbot-api --accept-dns=true
  ```

### Pitfalls
- **MagicDNS may not propagate immediately** — toggle it on in the admin console, then restart Tailscale on the VPS. The `tailscale status --json` output's `MagicDNS` field may still show False for a few minutes.
- **Old tailnet data is safe to discard** — Tailscale stores no user data. Logging out and re-authing to a new tailnet is clean.
- **Auth key expiry** — set a reminder for the expiry date. Generate reusable keys to avoid re-authing every time.

## Step 2: Hummingbot API Installation

### Clone the Repo
```bash
cd /root
git clone https://github.com/hummingbot/hummingbot-api.git
cd hummingbot-api
```

### Manual .env Creation (Bypass Interactive Installer)
The `setup.sh` script is interactive and reads from `/dev/tty`, which **fails over SSH** (no TTY available). The script loops forever asking "y/n" questions. **Do not run `bash setup.sh` over SSH** — create `.env` manually instead:

```bash
cat > .env << 'ENVEOF'
# Hummingbot API Configuration
USERNAME=gentech
PASSWORD=gentech_api_2026
CONFIG_PASSWORD=gentech_config_2026

# Tailscale
TAILSCALE_ENABLED=true
TAILSCALE_AUTH_KEY=tskey-auth-XXXXXXXX
TAILSCALE_HOSTNAME=hummingbot-api

# Database
POSTGRES_USER=hummingbot
POSTGRES_PASSWORD=hummingbot_db_2026
POSTGRES_DB=hummingbot

# Redis
REDIS_PASSWORD=hummingbot_redis_2026
ENVEOF
chmod 600 .env
```

### Deploy
```bash
make deploy
```

### Verify
```bash
# Check containers are running
docker ps --filter name=hummingbot

# Test API locally
curl -u gentech:gentech_api_2026 http://localhost:8000/

# Test via Tailscale (from another machine on the same tailnet)
curl -u gentech:gentech_api_2026 http://hummingbot-api:8000/
```

### Pitfalls
- **Port 8000 may be taken** — check with `ss -tlnp | grep 8000` before deploying. If occupied (e.g., by rota-core), either stop the conflicting service or change the API port in docker-compose.yml. The API port is in the `hummingbot-api` service's `ports:` section. EMQX broker also uses ports 8081 (management), 8083 (WS), 8084 (WSS) — all may conflict on a shared VPS.
- **Port conflict resolution pattern:** When deploying on a VPS with existing services, check ALL ports the compose file uses before deploying. Run `ss -tlnp | grep -E '8000|8081|8083|8084|1883|8883|5432'` to find conflicts. Remap conflicting ports in docker-compose.yml with sed BEFORE `make deploy`. After remapping, run `docker compose down && make deploy` to recreate cleanly.
- **The interactive installer loops forever over SSH** — never run `bash setup.sh` without a TTY. The script reads from `/dev/tty` which fails over SSH, causing it to loop indefinitely. Always create `.env` manually and use `make deploy`.
- **Tailscale sidecar** — with `TAILSCALE_ENABLED=true`, `make deploy` runs a Tailscale sidecar container. The API binds to `127.0.0.1:8000` and Tailscale serve exposes it on the tailnet. No public port exposure needed.
- **Docker must be running** — verify with `docker ps` before deploying.
- **MagicDNS may not propagate immediately** — after toggling MagicDNS on in the admin console, the VPS may still show `MagicDNS: False` in `tailscale status --json`. Restart Tailscale: `tailscale down && sleep 2 && tailscale up --auth-key KEY --hostname hummingbot-api --accept-dns=true`. The short hostname resolves on the tailnet even before the status field updates.
- **Auth key expiry** — set a cron reminder for the day before expiry. Generate reusable keys to avoid re-authing every time. The key is reusable but has a fixed expiry date.

## Step 3: Condor Installation

### Clone
```bash
cd /root
git clone https://github.com/hummingbot/condor.git
cd condor
```

### Structure
```
condor/
├── main.py              # Entry point
├── config_manager.py    # API client config
├── routines/            # Deterministic Python workflows
│   ├── arb_check.py     # CEX-CEX arbitrage checker
│   ├── market_scanner.py # Perp market scanner
│   ├── solenrich.py     # SolEnrich data enrichment (custom)
│   └── ...
├── agents/              # Trading agent definitions
├── handlers/            # Telegram command handlers
├── frontend/            # Web UI
└── mcp_servers/         # MCP tool servers
```

### Routines
Routines are deterministic Python workflows that execute without LLM tokens. They live in `routines/` and follow this pattern:

```python
"""Routine description."""
CATEGORY = "Category Name"

from pydantic import BaseModel, Field
from telegram.ext import ContextTypes

class Config(BaseModel):
    """Config docstring becomes the routine description in the UI."""
    param: str = Field(default="value", description="Parameter description")

async def run(config: Config, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Execute the routine. Return a string for Telegram display."""
    # ... logic ...
    return "Result string"
```

### SolEnrich Routine Pattern
For x402-native data APIs (like SolEnrich), the routine pattern is:

1. **Config** — endpoint name, address/mint, format (json/llm/both), demo vs paid
2. **Build payload** — map endpoint name to request body
3. **Call API** — POST with JSON body, handle 402 (payment required), 429 (rate limit), timeout
4. **Format output** — prefer `format: "llm"` for natural language briefings the agent can reason over
5. **Return** — formatted string for the agent's context

See `references/solenrich-routine-pattern.md` for the full worked example.

### Pitfalls
- **uv package manager** — Condor uses `uv` (Rust-based Python package manager). Install with `pip install uv` if missing.
- **Telegram bot token required** — Condor needs a Telegram bot token to run. Set `TELEGRAM_TOKEN` in `.env`.
- **Tailscale recommended** — Condor controls real trading. Use Tailscale to avoid exposing the API on public ports.

## Step 4: Verification Checklist

- [ ] Tailscale: both machines on same tailnet, MagicDNS enabled
- [ ] Hummingbot API: containers running, responds on port 8000 (or remapped)
- [ ] Condor: cloned, routines directory populated
- [ ] Cross-machine: `curl -u USER:PASS http://hummingbot-api:8000/` works from user's machine
- [ ] SolEnrich: free demo endpoint responds (10 queries/hr per IP)

## Deployment State (verified Aug 4, 2026) — Builder Cup

The GenTech VPS has Hummingbot API + Condor live already:
- **Hummingbot API** runs on **port 8002** (remapped from 8000 — 8000 was taken by
  another service). docker-compose.yml remaps `8000→8002` and EMQX `8083/8084/8081 →
  8098/8097/8099`. Containers: `hummingbot-api`, `hummingbot-postgres`,
  `hummingbot-broker` (EMQX), `hummingbot-tailscale` — all healthy.
- **Condor** is cloned at `/root/condor` with agents (`delta_neutral_funding_agent`,
  `market_making_expert`, `routine_builder`, `solana_dex_lp_expert`) and routines
  (`arb_check`, `market_scanner`, `price_monitor`, `solenrich`).

### "Finish the build" blockers — what actually stops it from running/submitting
1. **Condor has no `.env`** → no `TELEGRAM_TOKEN` → Condor can't start. This is the
   #1 runtime blocker; only Jordan can create the bot token (BotFather).
2. **Registration gate** — Agent Builders Cup is a limited-seat competition (10 seats,
   registration closes Aug 15). No submission can happen without registering at
   botcamp.xyz. Always check registration is done before "finishing" a build.
3. **API port mismatch for Condor** — Condor's `config_manager.py` builds
   `http://{host}:{port}` from its stored server config; if Hummingbot API is on 8002
   (not 8000), that config must be updated or Condor will fail to connect. When
   remapping ports, wire the new port into Condor's config, not just docker-compose.

## Agent Builders Cup — funding model (verified Aug 6, 2026)

**The cup provides the trading capital — you do NOT fund it.** The official rules
(botcamp.xyz/hackathons/agent-builders-cup-1) state: *"Builders aren't risking their own
funds. Each team fields two agents — they each go live with $800, race for 48 hours, and
the builder keeps whatever's in the account at the end (up or down)."*

- **Starting capital is $800 USDC per agent** (NOT $1K — correct any queue/note that says
  $1K). Two agents per team, racing in parallel.
- **What you DO fund is operational SOL** for the agent to deploy + pay gas on Solana
  (Meteora venue): ~0.057 SOL rent per Meteora slot, plus the strategy's
  `min_wallet_sol_reserve` (0.3 SOL) + Jupiter swap gas. **~$25-30 of SOL** on the Solana
  keypair is enough to make the agent deployable. The $800 trading capital is separate.
- **Check the Solana keypair balance before asking Jordan to fund** — raw RPC
  `getBalance` + `getTokenAccountsByOwner` (USDC mint `EPjFWdd5...`). A keypair file
  existing does NOT mean it's funded; verify the actual SOL/USDC on-chain.

## Condor model wiring — use an existing subscription, NOT OpenAI (Aug 6, 2026)

The agent's default `agent_key: claude-acp:sonnet` requires the **Claude Code CLI**
(`claude` binary), which is often NOT installed. Condor's pydantic-ai client supports any
OpenAI-compatible endpoint, so you can point the agent at an existing subscription instead
of asking Jordan for an OpenAI key.

**Wiring:** set the run config to `agent_key: openai:<model>`, `model_base_url: <url>`,
`api_key: <key>`. Condor resolves this through pydantic-ai's OpenAI-compatible path
(`condor/acp/pydantic_ai_client.py` — `openai:model` with custom base_url).

**CRITICAL placement gotcha (Aug 6, 2026):** in a `strategy.md`, `model_base_url` MUST go
inside the `default_config:` block, NOT as a top-level frontmatter field. The strategy
loader (`condor/agents/strategy.py` `_load_strategy_from_file`) only captures `agent_key`
and `default_config` from frontmatter — a top-level `model_base_url:` is silently dropped
(`s.default_config.get('model_base_url')` returns `None`). The engine reads
`self.config.get("model_base_url")`, and `self.config` is built from `default_config`, so
the URL only flows through if it's a key inside `default_config`. Verify with:
```python
s = _load_strategy_from_file(path, slug)
print(s.agent_key, s.default_config.get('model_base_url'))  # both must be set
print(is_pydantic_ai_model(s.agent_key))  # must be True for openai:model
```
Also confirm the `.env` is gitignored before committing — Condor's `.gitignore` already
excludes `.env`, so the Telegram token + API key stay out of git. `git ls-files .env`
should return nothing.

**Provider triage (test each with a real chat-completions call before wiring):**
- **ollama.com** (`OLLAMA_API_KEY`, base `https://ollama.com/v1`) — ✅ works, `kimi-k2.7-code`
  returns clean content. Strong code model for the LP/arb agent. **Preferred.**
- **GLM/Zhipu** (`GLM_API_KEY`/`ZAI_API_KEY`, `https://open.bigmodel.cn/api/paas/v4/`) — often
  out of balance (error 1113 "余额不足"). Test before relying on it.
- **opencode-go** (`OPENCODE_GO_API_KEY`, `https://opencode.ai/zen/go/v1`) — hits monthly
  usage limits (`GoUsageLimitError`) and some models need region opt-in. Unreliable for
  agent runtime.
- **Claude Code CLI** (`claude-acp:sonnet`) — only if the `claude` binary is installed.

## Condor launch-readiness verification (Aug 6, 2026)

Before asking Jordan to fund anything, prove the agent can actually launch. Boot-check
pattern (no funds needed — catches wiring bugs):
1. **Deps import** — `python3 -c "import condor, telegram, fastapi, solana"`.
2. **Agents load** — `AgentStore().list_all()` shows all agents incl. `solana_dex_lp_expert`.
3. **Strategy parses** — `_load_strategy_from_file(path, slug)` returns a valid Strategy
   (frontmatter name/config/skills intact).
4. **Routines import** — `import cross_venue_arb, lp_scanner` (agent-local routines). A
   missing dep here (e.g. `geckoterminal_py` for the Solana DEX agent) breaks the agent at
   runtime even though the strategy loads — `pip install geckoterminal_py` fixes it.
   (Reconfirmed Aug 20 2026 — `lp_scanner` fails with `ModuleNotFoundError: No module named
   'geckoterminal_py'` until installed; `cross_venue_arb` uses plain `aiohttp` + pydantic so
   it imports fine either way.)
5. **Server imports** — `from main import main` succeeds.

The strategy can load cleanly while the routines fail on a missing dependency — always
test BOTH the strategy parse AND the routine imports. A "structurally ready" verdict
requires all five checks to pass.

## References

- `references/solenrich-routine-pattern.md` — Full SolEnrich Condor routine code and usage
- `references/agent-builders-cup-2026.md` — Competition rules, strategy, and build queue
- `references/hummingbot-gateway-mtls-certs.md` — Fix the Hummingbot Gateway mTLS cert crash (SEC-048): generate CA+server+client certs with openssl, the hostname-mismatch SAN pitfall, and syncing certs to BOTH API-container cert locations.

## Hummingbot Gateway mTLS cert crash (Aug 6, 2026)

The Gateway (v2.x) runs **secured mTLS mode** and will NOT start without a full cert set —
an empty `certs/` dir makes it crash-loop with `ENOENT: ./certs/server_key.pem`. The certs are
normally generated by the Hummingbot CLI (`gateway generate-certs`), NOT inside the gateway
image, so a bare `gateway/start` on a fresh box fails. Fix: generate the CA + server + client
certs with openssl (passphrase = `GATEWAY_PASSPHRASE`), and **add `DNS:gateway` to the server
cert SAN** or the API fails with `CERTIFICATE_VERIFY_FAILED: Hostname mismatch`. Then sync the
client certs into BOTH the API container's cwd certs dir AND `root_path()/certs`, and restart
the API so its cached SSL context rebuilds. Full recipe + verification in
`references/hummingbot-gateway-mtls-certs.md`.

## Agent Builders Cup — hyper-stork submission (Aug 2026)

The Botcamp submission is named **hyper-stork** and maps to the **HIP-3 Delta-Neutral Funding MM**
strategy in Condor:
`agents/delta_neutral_funding_agent/strategies/hip_3_delta_neutral_funding_mm/strategy.md`.

Filling the Botcamp form (botcamp.xyz → Dashboard → My Strategies → hyper-stork):
- **Strategy Type:** `Agent - AI/autonomous trading agent`
- **Core logic:** delta-neutral MM on a correlated pair of Hyperliquid HIP-3 perps (CL/BRENTOIL
  default). Quotes both sides of BOTH legs via two `pmm_mister` controllers in one shared account,
  holds a beta-weighted long/short so net delta ≈ 0, leans the funding-favorable side. Earns maker
  spread + net funding carry (~+33%/yr) with market risk hedged out. NOT stat-arb.
- **Neutrality is INDUCED via MM re-tuning**, never a market/hedge order. Routine `hip3_dn_pair_monitor`
  is the analysis brain (returns RECOMMENDATION: RUN A/B, RESIZE, HEDGE, REDUCE-ROTATE, HOLD-FLATTEN).
- **Markets:** Hyperliquid HIP-3 perps (`hyperliquid_perpetual`, `xyz:` issuer prefix, UPPERCASE).
- **Parameters:** leg_a, leg_b, hedge_beta (1.02), total_amount_quote (500), min_corr (0.9),
  net_delta_band_pct (0.04), flip_margin_pct_yr (15), buy/sell_spread_bps (5), take_profit_bps (4),
  leverage_cap (2), risk_limits.max_position_size_quote (300) / max_open_executors (8).
- **Status fields:** actual per-leg signed notionals, net factor delta vs band (IN-BAND/BREACH),
  fill gap, live corr + β, per-leg funding + net carry %/yr, spread P&L, fees, funding accrued,
  total net, and the action taken.
- **Events:** corr break → FLATTEN both legs/stop/alert; net delta breach → REBALANCE (re-tune, no
  market hedge); funding flip → REDUCE/ROTATE; A/B flip gated by funding hysteresis (≥ 15%/yr, never
  twice within 3 ticks).
- **Form not yet filled (as of Aug 4):** Code Files (package `agents/delta_neutral_funding_agent/`)
  and Video (60-90s Loom/YouTube). Tags: delta-neutral, funding, market-making, hyperliquid, perp,
  AI-agent. Exchanges: Hyperliquid.

### Execution layer is Gentech, NOT Forge
Forge is a desktop-only Telegram presence, not 24/7, so it can NOT run a live trading submission.
**Gentech (VPS, 24/7) is the executor** — already wired to Hummingbot API (port 8002) + Condor. Do
NOT go hunting for "Forge's old bot" for a trading competition; the VPS agent is the correct
execution layer. (Aug 4, 2026: Jordan floated "use Forge's old bot" then corrected — Forge has no
24/7 presence on the apps.)
