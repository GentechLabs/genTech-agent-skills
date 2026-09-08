# BlockRun MCP Server — Quick Reference

**Added:** June 15, 2026
**Package:** `@blockrun/mcp@latest`
**Install:** `hermes mcp add blockrun --command npx --args -y @blockrun/mcp@latest`

## Tool Categories

### FREE Tools (no USDC needed)
| Tool | What it does |
|------|-------------|
| `blockrun_dex` | DexScreener data — real-time DEX pairs, prices, volume, liquidity |
| `blockrun_price` | Pyth oracle prices — crypto, FX, commodities. Single symbol per call |

### Paid Tools (need USDC in BlockRun wallet)
| Tool | Cost | What it does |
|------|------|-------------|
| `blockrun_search` | $0.25/search | Grok Live Search — web + X/Twitter + news |
| `blockrun_exa` | Pay-per-call | Neural web search via Exa |
| `blockrun_defi` | Pay-per-call | DefiLlama TVL, yields, protocol data |
| `blockrun_markets` | Pay-per-call | Prediction market + derivatives data |
| `blockrun_rpc` | Pay-per-call | Raw JSON-RPC on 40+ blockchains |
| `blockrun_chat` | Pay-per-call | Multi-model access (GPT-5, Claude, Gemini, etc.) |
| `blockrun_image` | Pay-per-call | Image generation/editing |
| `blockrun_speech` | Pay-per-call | ElevenLabs TTS |
| `blockrun_video` | Pay-per-call | AI video generation |
| `blockrun_music` | Pay-per-call | Music track generation |
| `blockrun_wallet` | Free | Payment wallet management |

## Tool Argument Shapes

### blockrun_price
```json
{"action": "price", "category": "crypto", "symbol": "AVAX"}
```
- `action`: "price" | "history" | "list"
- `category`: "crypto" | "fx" | "commodity" | "usstock" | "stocks"
- `symbol`: single symbol string (not comma-separated)

### blockrun_dex
```json
{"query": "WAVAX USDC"}
```
- Simple text query, returns matching DEX pairs from DexScreener

### blockrun_search
```json
{"body": {"query": "search terms", "max_results": 3, "sources": ["web", "x", "news"]}}
```
- `max_results` drives cost: default 10 = $0.25 per search
- `sources` filters: "web", "x" (Twitter), "news"

## Wallet Setup
```json
{"name": "blockrun_wallet", "arguments": {"action": "setup"}}
```
Returns funding address. Send USDC on Base to activate paid tools.

## GenTech Integration Points
- **DeFi Monitor:** `blockrun_dex` + `blockrun_price` for free real-time data
- **Career Scanner:** `blockrun_search` for job market research
- **Grant Research:** `blockrun_exa` for deep research
- **Dashboard Engine:** `blockrun_defi` for protocol TVL data
- **Agent Kit:** Wallet management pattern for agent-owned spending
