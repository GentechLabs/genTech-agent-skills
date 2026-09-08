# ClawRouter as a Hermes fallback provider (BlockRun)

Installed + enabled Aug 7, 2026. Local LLM router for autonomous agents — by BlockRun
(same company as the blockrun wallet). Runs as a local proxy on `127.0.0.1:8402/v1`,
gives Hermes 71 models from 12 labs behind ONE provider. Wallet-signature auth (no API
keys), USDC per-request via x402 on Base or Solana. 6 models free, no signup, no balance.

## Why it fits our stack
- Real fallback for when Ollama Cloud is exhausted (weekly reset) or OpenCode Go is at cap.
- Uses the **blockrun wallet** — fund with USDC, non-custodial, $5 covers thousands of calls.
- Same x402/USDC rail we already run — consistent architecture.
- Dedicated Hermes plugin `hermes-plugin-clawrouter` (pip). Does NOT replace existing
  providers — it ADDS one.

## Setup (no OpenClaw required)
```bash
# 1. Install into Hermes' own venv
~/.hermes/hermes-agent/venv/bin/python -m pip install -U hermes-plugin-clawrouter

# 2. Enable the plugin
hermes plugins enable clawrouter            # says "takes effect on next session"

# 3. Register provider + API key (hermes-clawrouter, NOT npx clawrouter)
hermes-clawrouter setup
#   - Writes model-provider plugin to plugins/model-providers/clawrouter/
#   - Seeds CLAWROUTER_API_KEY=clawrouter-local in .env
#   - Registers ClawRouter in config.yaml
#   - Reports "No wallet found" — expected next step

# 4. Make the proxy DURABLE — systemd service, NOT a session background process
#    (a background process dies on gateway/VPS restart and silently kills the
#    provider for ALL groups. This was a real failure mode we hit and fixed.)
sudo tee /etc/systemd/system/clawrouter-proxy.service > /dev/null << 'EOF'
[Unit]
Description=ClawRouter LLM proxy (x402 USDC smart routing) for Hermes
After=network.target

[Service]
Type=simple
WorkingDirectory=/root/.hermes/profiles/gentech/home
ExecStart=/usr/local/node22/bin/npx @blockrun/clawrouter --port 8402
Environment=HOME=/root/.hermes/profiles/gentech/home
Restart=always
RestartSec=5
# HOME must point at the profile home so the wallet mnemonic is found
# (~/.openclaw/blockrun/mnemonic + wallet.key) on every boot.

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
# Kill any session-bound proxy FIRST to free the port, then start the service
sudo kill <old-pid> 2>/dev/null; sleep 2
sudo systemctl start clawrouter-proxy.service
sudo systemctl enable clawrouter-proxy.service   # boot persistence
# Verify: is-active, is-enabled, ss -tlnp | grep 8402, curl /health
# Wallet is preserved because HOME points to the profile home.

NOTE: `npx @blockrun/clawrouter setup` (not `hermes-clawrouter`) errors with
"openclaw not found on PATH". Ignore it — you don't need OpenClaw. Just start the
proxy directly; the wallet is generated on first boot.

## Config (write-guarded — use hermes config, NOT direct patch)
`config.yaml` refuses direct edits ("Refusing to write to Hermes config file...
security-sensitive configuration"). Use:
```bash
hermes config set model.default "free/deepseek-v4-flash"
hermes config set model.provider "clawrouter"
```
Takes effect on gateway restart.

## CRITICAL pitfall: the `free` alias is NOT DeepSeek
- Model id `free` or `blockrun/auto` (on an empty wallet) aliases to **`free/gpt-oss-120b`**,
  NOT DeepSeek V4 Flash. The proxy log shows: `"free" -> alias: "free/gpt-oss-120b"`.
- gpt-oss-120b gets rate-limited (`All 1 models failed. Tried: free/gpt-oss-120b (rate_limited)`),
  so traffic stalls on an empty wallet.
- **Fix: pin the EXACT id `free/deepseek-v4-flash`** (1M context). It resolves directly
  and works. Verified live via `POST /v1/chat/completions` with `"model":"free/deepseek-v4-flash"`.

## Free tier congestion
- Free DeepSeek often returns `FREE_... capacity exhausted — retry shortly, or use a paid
  model (from $0.002/request)`. The free model is hammered by everyone.
- Paid models start at $0.002/request; $5 covers thousands of calls. Fund the wallet to
  route around the congestion.
- Wallet address (Base USDC, default chain): `0xf5f99007Fc7e14133D3817dee2BA45169eA9280D`
  (check live via `npx @blockrun/clawrouter wallet`).
- Solana USDC: `BX9ELMCGPy3qmGNrhH3c2W5NJmapSQ435k8hqE5K43XT`.

## Free-tier congestion is the #1 failure mode (Aug 8, 2026)
When `free/deepseek-v4-flash` upstream stalls, the shared provider goes silent for ALL 4
Telegram groups at once — it looks like "Entertainment is down" but it's global (one
Hermes config, one agent, one provider). Diagnosis signature:
- clawrouter journal: `All models in fallback chain failed` + `Socket timeout, destroying connection`
- gateway/agent log: `httpx.ReadTimeout` on the model call
- ClawRouter `/health` still returns `{"status":"ok"}` and `/v1/models` returns 200 — the
  proxy is fine, its UPSTREAM is slow. Don't restart the proxy; fix the fallback.

**Fix: configure a paid fallback** so a free stall auto-routes to `blockrun/auto` instead
of going silent. No manual provider flip needed.

## Fallback chain config (correct schema, Aug 2026)
`fallback_providers` is a LIST of `{provider, model, base_url}` dicts. The legacy
single-dict `fallback_model` key is deprecated — `hermes config set fallback_model.*`
warns "not a recognized config key" and Hermes may not read it.

**PITFALL: `hermes config set fallback_providers '[...]'` stores the list as a QUOTED
STRING**, which `get_fallback_chain` does NOT parse — `hermes fallback list` then reports
"No fallback providers configured" even though the key is present. To write a real YAML
list, use the config module directly:

```bash
/usr/local/lib/hermes-agent/venv/bin/python -c "
from hermes_cli.config import load_config, save_config
cfg = load_config()
cfg['fallback_providers'] = [{'provider':'clawrouter','model':'blockrun/auto','base_url':'http://127.0.0.1:8402/v1'}]
save_config(cfg)
"
```

**Verify with the dedicated CLI** (source of truth, not grep):
```bash
hermes fallback list
# Primary:   free/deepseek-v4-flash  (via clawrouter)
# Fallback chain (1 entry):
#   1. blockrun/auto  (via clawrouter)  [http://127.0.0.1:8402/v1]
```

## Clearing a per-session /model override
If a user manually flipped a session to another provider (e.g. Ollama) to reach you during
a stall, that override is persisted per-session in the session store and rehydrated on
gateway restart — it does NOT live in config.yaml. To clear it back to the global
ClawRouter path:

```bash
/usr/local/lib/hermes-agent/venv/bin/python -c "
from gateway.session import SessionStore
from pathlib import Path
import gateway.config as gc
store = SessionStore(Path('/root/.hermes/profiles/gentech/sessions'), gc.GatewayConfig())
key = 'agent:main:telegram:group:-1003863540828:7105876857'  # <session_key>
print('current:', store.get_model_override(key))
store.set_model_override(key, None)   # None clears the persisted override
print('after:', store.get_model_override(key))
"
```
The session key format is `agent:main:telegram:group:<chat_id>:<user_id>` (seen in the
gateway log line `Rehydrated persisted /model override for session=...`). Passing `None`
to `set_model_override` clears it (same path `/new` uses).

## Slash commands (hermes-clawrouter)
```
hermes-clawrouter setup    # materialize provider + verify deps
hermes-clawrouter wallet   # address + USDC balances
hermes-clawrouter doctor   # health check
hermes-clawrouter route    # show/set routing profile (eco/auto/premium)
hermes-clawrouter stats    # proxy usage stats
```

## All four Telegram groups share ONE Hermes config
There is a single `model:` block and one agent for all four groups (HQ, Strategies,
Labs, Entertainment). Each group only differs by its `channel_prompts:` entry. So when
the provider/default model is set, **all four groups inherit it automatically** — there
is NO per-group model wiring. To verify coverage, just confirm the 4 group IDs are all
present in `channel_prompts:` (grep with `-F` because the `-100...` IDs parse as flags:
`grep -qF -- "-1003863540828" config.yaml`). Restart the gateway once and every group is
on the new provider.

## Jordan's routing plan (as of Aug 7, 2026)
- Ollama Cloud = **Kimi K2.7** for audits / heavier reasoning (targeted, keeps usage low).
- ClawRouter = **free DeepSeek V4 Flash** for everything else ($0).
- If Ollama can't run Kimi → ClawRouter **paid** Kimi (small top-up only when needed).
- ClawRouter stays PRIMARY for now since we'll flip to it during the switch anyway.

## Model id formats
- Free: `free/deepseek-v4-flash`, `free/gpt-oss-120b`, `free/qwen3-coder-480b`, etc.
- Routing profiles: `blockrun/auto` (balanced), `blockrun/eco` (cheapest, 98% cheaper),
  `blockrun/premium` (best), `blockrun/free`.
- Providers prefix the model: `blockrun/anthropic/claude-opus-5`, `blockrun/openai/gpt-5.6`,
  `blockrun/deepseek/deepseek-v4-flash`, `blockrun/moonshot/kimi-k2.6`.
- Free 1M-ctx DeepSeek V4 Flash is the key value prop for bridging the Ollama gap at $0.
