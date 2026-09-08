# Telegraph Protocol Miner Registration (x402 API-as-resource wrap)

Telegraph (Season I 2026, hackathon.telegraphprotocol.com) is a verifiable-intelligence
protocol: **Miners** wrap any API/model/dataset/tool into a declarative YAML, register
on-chain, and serve verifiable answers. Applications consume live miners; eval scripts rank
them. $15K total (H1 $5K Aug 17–Sep 7, H2 $10K mid-Oct, H3 mainnet Dec). Registration open
now, Track 1&2 open Aug 17 12:00 UTC. Payments are **x402** (Base Sepolia / Solana Devnet) —
our exact stack.

## A Miner is YAML, not code
Spec: `docs.telegraphprotocol.com/docs/miners/yaml-config`. Fields: `version:"1"`,
`kind: miner`, `id` (numeric), `slug` (kebab-case unique), `name`, `base_url` (must be
`https://`), `auth` (`bearer`/`header`/`none`; key ref via `env_var` NAME only, never inline),
`endpoints[]` (path, external_path, method, param_map, content_type), `semantics.signal_mapping`
(ONLY `confidence_field`/`label_field`/`reason_field` — `type` is not allowed),
`semantics.supported_intents` (at least one), `on_chain` (transform + fields), operational
settings (rate_limit_per_sec, circuit_threshold, circuit_cooldown_seconds).
Validate at `integrate.telegraphprotocol.com` (sandbox-tests every endpoint against the live
upstream API), THEN register on-chain. Testnet dispatcher: `http://13.237.89.59:7044/miner-dispatcher`.

## CRITICAL — canonical intents mismatch (verified Aug 12, 2026)
The **miner registration schema's** registerable canonical intents do NOT include
CRYPTO_PRICE / WALLET_BALANCE / TVL / TOKEN_HOLDER — those are the **application-layer
catalog** (40 intents), not the miner schema. The registerable miner intents include:
`WEB_SEARCH, NEWS_SEARCH, RESEARCH_SYNTHESIS, FACT_CHECK, CONTENT_VERIFICATION,
TWITTER_SEARCH, CHAT_COMPLETION, TASK_COMPLETION, AGENT_TASK, WEATHER_CHECK/FORECAST,
DEEPFAKE_DETECTION, IMAGE/VIDEO_VERIFICATION, AI_DETECTION, MULTIMODAL/IMAGE_GENERATION`.
**Consequence:** crypto/DeFi services can't yet register as miners. The clean entry is a
**search/research miner** (wrap Tavily → WEB_SEARCH + NEWS_SEARCH + RESEARCH_SYNTHESIS).
Re-visit crypto intents once the schema opens them (our Nevermined services are already
x402-ready).

## Verify API response fields against the LIVE API before writing on_chain mappings
The `on_chain.fields` block references real response field paths; wrong paths fail sandbox
validation. Worked example (Tavily): `score` is per-*result*, NOT top-level; `result_count`
does NOT exist. Real top-level fields: `answer` (when `include_answer=true`), `response_time`
(float seconds), `query`, `request_id`. Probe the live endpoint with curl and enumerate
top-level keys BEFORE writing the transform:
```bash
curl -s -X POST https://api.tavily.com/search -H "Content-Type: application/json" \
  -d '{"api_key":"<KEY>","query":"x402","max_results":2,"include_answer":true}' \
  | python3 -c "import json,sys; print(list(json.load(sys.stdin).keys()))"
```

## Validation is immutable — validate FIRST
On-chain registration cannot be edited. `integrate.telegraphprotocol.com` catches schema
violations, non-responding endpoints, and auth mistakes BEFORE they're pinned. The #1 failure
mode is schema/auth errors caught only post-registration. Never put the raw key in YAML —
only the `env_var` name; the node reads it at runtime.

## Strategic play (H1)
1. Search/research miner wrapping Tavily → register it (the overnight build).
2. Evaluation script (Track 2) — low-effort, high-leverage, feeds the agent-sentiment-index thesis.
3. Crypto intents later once the schema opens them.
4. **GitHub contribution** (parallel, low-risk): `telegraphprotocol` org — `Telegraph` (node
   source — learn routing/scoring), `Telegraph-MCP` (MCP server, natural fit), `telegraph-docs`
   + `telegraph-examples`. Start with docs/examples PRs (safe), then MCP-server improvements.

## Judging criteria (H1 Miner Track)
Telegraph ranking & performance · number of apps built on the miner · total requests served ·
X progress posts + engagement.
