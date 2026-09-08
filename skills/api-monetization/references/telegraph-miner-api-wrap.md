# Telegraph Miner — wrapping an API for a verifiable-intelligence marketplace

Telegraph (Season I 2026, $15K across H1 $5K / H2 $10K / H3 mainnet) is a
verifiable-intelligence protocol on Base that uses x402 natively (PayAI
facilitator). Miners wrap any API/model/tool into a **declarative YAML**, validated
at `integrate.telegraphprotocol.com`, then registered **on-chain (immutable)**.

**Key insight:** a Miner is YAML, NOT code. So the overnight build queue can produce
it. But two pitfalls made the first draft wrong — capture them.

## Pitfall 1: canonical-intents mismatch (crypto services can't register yet)

The **miner registration schema's canonical intents do NOT include crypto intents**
(CRYPTO_PRICE / WALLET_BALANCE / TVL are *application-layer* intents, not registerable
miner intents). The 27 registerable canonical intents include:
`WEB_SEARCH, NEWS_SEARCH, RESEARCH_SYNTHESIS, FACT_CHECK, CONTENT_VERIFICATION,
TWITTER_SEARCH, CHAT_COMPLETION, TASK_COMPLETION, AGENT_TASK, ...`

So our DeFi/crypto x402 services cannot yet be registered as miners. The clean
shippable path is a **search/research miner wrapping Tavily** (working key available).
Once the schema opens crypto intents, port the x402 services in (already x402-ready).

## Pitfall 2: verify the wrapped API's REAL response shape before writing `on_chain` transforms

The `on_chain.fields` block maps JSON response paths → OnChainData. I drafted mappings
for Tavily using `score` and `result_count` as **top-level** fields — both wrong.
Tavily returns `score` only **per-result** (inside `results[]`) and has NO
`result_count`. Real top-level fields: `answer` (only when `include_answer=true`),
`response_time` (float seconds), `query`, `results[]`, `request_id`.

**Verification step (always do this):** before writing `on_chain` transforms, hit the
API directly and inspect top-level keys:
```bash
curl -s -X POST https://api.tavily.com/search \
  -H "Content-Type: application/json" \
  -d "{\"api_key\":\"$(cat /root/.blockrun/tavily-api-key)\",\"query\":\"x402 protocol\",\"max_results\":2,\"include_answer\":true}" \
  | python3 -c "import json,sys; print(list(json.load(sys.stdin).keys()))"
```
This catches ~50% of validation failures before the integrate sandbox flags them.

## YAML gotchas
- `signal_mapping` accepts ONLY `confidence_field`, `label_field`, `reason_field` — the `type` field is NOT allowed.
- `slug` kebab-case; `base_url` starts `https://`; `auth.type` is `bearer|header|none`.
- **Never put the raw API key in YAML** — only the `env_var` NAME (node reads at runtime).
- x402 payment on Base Sepolia USDC (`0x036CbD...CF7e`) or Solana Devnet. Testnet dispatcher `http://13.237.89.59:7044/miner-dispatcher` (free `/integrations`, `/healthz`, `/openapi.json` discovery).
- Register on-chain = immutable. Validate at `integrate.telegraphprotocol.com` FIRST.

## GitHub contribution angle
`telegraphprotocol` org: `Telegraph` (protocol node), `Telegraph-MCP` (MCP server —
natural fit), `telegraph-docs`, `telegraph-examples`. Start with docs/examples PRs
(safe), read node source to learn miner routing/scoring.

## Worked example
Draft miner YAML at `/root/vaults/gentech/10-Labs/telegraph/example-miner.yaml`
(GenTech Research wrapping Tavily, WEB_SEARCH / NEWS_SEARCH / RESEARCH_SYNTHESIS /
FACT_CHECK intents, min_price 0.01).
