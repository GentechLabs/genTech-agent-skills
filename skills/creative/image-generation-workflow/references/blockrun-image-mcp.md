# BlockRun MCP — invoking blockrun_image directly (verified 2026-08-07)

`blockrun_image` (and the other `blockrun_*` tools) may not be loaded as first-class
tools in every Hermes session, even though the BlockRun MCP server is enabled in
`config.yaml`. When the tool isn't in the session toolset, invoke it directly via the
MCP JSON-RPC protocol with a node spawn.

## Prerequisites
- BlockRun MCP server installed at `/root/.hermes/blockrun-mcp/node_modules/@blockrun/mcp/dist/index.js`
- Node available (`node --version` → v22.x)
- Wallet funded with USDC on the active chain (Base default). Check first:
  `blockrun_wallet action:"status"` → expect `$X.XX USDC` on Base.

## Probe script (wallet status)
```bash
cd /root/.hermes/blockrun-mcp && timeout 25 node -e '
const { spawn } = require("child_process");
const child = spawn("node", ["node_modules/@blockrun/mcp/dist/index.js"], {stdio:["pipe","pipe","pipe"]});
let out="";
child.stdout.on("data", d=>{out+=d;});
child.stderr.on("data", d=>{});
child.stdin.write(JSON.stringify({jsonrpc:"2.0",id:1,method:"initialize",params:{protocolVersion:"2024-11-05",capabilities:{},clientInfo:{name:"probe",version:"1"}}})+"\n");
setTimeout(()=>{child.stdin.write(JSON.stringify({jsonrpc:"2.0",id:2,method:"tools/call",params:{name:"blockrun_wallet",arguments:{action:"status"}}})+"\n");},1500);
setTimeout(()=>{console.log(out); process.exit(0);},6000);
'
```

## Generate an image (gpt-image-2)
```bash
cd /root/.hermes/blockrun-mcp && timeout 60 node -e '
const { spawn } = require("child_process");
const child = spawn("node", ["node_modules/@blockrun/mcp/dist/index.js"], {stdio:["pipe","pipe","pipe"]});
let out="";
child.stdout.on("data", d=>{out+=d;});
child.stderr.on("data", d=>{});
child.stdin.write(JSON.stringify({jsonrpc:"2.0",id:1,method:"initialize",params:{protocolVersion:"2024-11-05",capabilities:{},clientInfo:{name:"probe",version:"1"}}})+"\n");
setTimeout(()=>{child.stdin.write(JSON.stringify({jsonrpc:"2.0",id:2,method:"tools/call",params:{name:"blockrun_image",arguments:{prompt:"<YOUR PROMPT>",model:"openai/gpt-image-2",size:"1024x1024"}}})+"\n");},1500);
setTimeout(()=>{console.log(out); process.exit(0);},45000);
'
```

## Response shape
The `tools/call` result returns `structuredContent` with:
- `url` — permanent BlockRun-hosted image URL (`https://blockrun.ai/api/media/media/images/...`)
- `prompt`, `model`, `cost_usd` (e.g. `0.065` for a 1024×1024 gpt-image-2)

Download with `curl -s -L -o out.png <url>` and verify with `file out.png` + `vision_analyze`.

## Edit (img2img) — local file path works
`blockrun_image` accepts a **local file path** for the `image` param (auto-encoded to a
data URI) — unlike FAL, which requires a public URL. This is a major advantage for
editing user-sent photos that live in `image_cache/`.

## Model pricing (1024×1024 base)
- `openai/gpt-image-2` — $0.06–0.12 (default; best on-image text + character consistency)
- `openai/gpt-image-1` — $0.02–0.04
- `google/nano-banana` — $0.05
- `google/nano-banana-pro` — $0.10 ($0.15 at 4096px; strongest photorealism)
- `xai/grok-imagine-image` — $0.02
- `xai/grok-imagine-image-pro` — $0.07
- `zai/cogview-4` — $0.015 (cheapest)

Edit (img2img) models: `openai/gpt-image-2` (default), `openai/gpt-image-1`,
`google/nano-banana`, `google/nano-banana-pro`. Multi-image edit: array of 2–4 source
images (openai/* up to 4, google/* up to 3). Inpaint mask via `mask` (gpt-image-* only).

## Other blockrun_* tools (same MCP server)
`blockrun_wallet`, `blockrun_chat`, `blockrun_models`, `blockrun_music`, `blockrun_speech`,
`blockrun_video`, `blockrun_realface`, `blockrun_search`, `blockrun_exa`, `blockrun_markets`,
`blockrun_price`, `blockrun_dex`, `blockrun_modal`, `blockrun_phone`, `blockrun_surf`,
`blockrun_rpc`, `blockrun_defi`, `blockrun_polymarket`. All paid via USDC on the active
chain (Base or Solana) — no separate API keys.
