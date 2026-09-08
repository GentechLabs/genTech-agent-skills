# Direct BlockRun Node SDK Invocation (when MCP tools are unavailable)

When the `blockrun_image` / `blockrun_video` / `blockrun_wallet` MCP tools are NOT
loaded in the current session's toolset (config `enabled: true` does not guarantee
they're exposed), you can still do paid image + video generation by calling the
BlockRun Node SDK directly. Confirmed working Aug 4, 2026.

## SDK location (this profile's install)
```
/root/.hermes/blockrun-mcp/node_modules/@blockrun/llm/dist/index.js
```
Exports used: `ImageClient`, `VideoClient`, `getOrCreateWallet`.
Also present: `MusicClient`, `SpeechClient` (same `generate` pattern).

## Key rule — public URLs
- **ImageClient.edit** accepts a base64 `data:image/...` URI built from a LOCAL file
  (`readFileSync(...).toString('base64')`). Local source works here.
- **VideoClient.generate** requires a **public `imageUrl`** seed frame. Host the
  keyframe on the VPS first (`https://vanito.gentechlabs.net/characters/...`), then
  pass that URL. Local paths / data URIs will not work for the video seed.
- Run paid ops in **background** (`terminal background=true, notify_on_complete=true`)
  to avoid orphan/interrupt. If a run gets orphaned, verify the wallet balance before
  retrying — the failed run may not have charged (seen: wallet unchanged after orphan).

## Image generation (img2img / reference fusion) — keyframe
```js
import { ImageClient, getOrCreateWallet } from '/root/.hermes/blockrun-mcp/node_modules/@blockrun/llm/dist/index.js';
import { readFileSync } from 'node:fs';
const wallet = getOrCreateWallet();
const client = new ImageClient({ privateKey: wallet.privateKey });
const sheetUri = `data:image/png;base64,${readFileSync('/path/sheet.png').toString('base64')}`;
const result = await client.edit(prompt, sheetUri, { model: 'openai/gpt-image-2', size: '1024x1024' });
console.log(result.data?.[0]?.url, result.cost_usd);
```

## Video generation — Seedance 2.0 (character-locked seed)
```js
import { VideoClient, getOrCreateWallet } from '/root/.hermes/blockrun-mcp/node_modules/@blockrun/llm/dist/index.js';
const client = new VideoClient({ privateKey: wallet.privateKey });
const result = await client.generate(prompt, {
  model: 'bytedance/seedance-2.0',
  imageUrl: 'https://vanito.gentechlabs.net/characters/<keyframe>.png', // MUST be public
  durationSeconds: 10,      // max 10s per clip
  aspectRatio: '16:9',      // or '1:1'
  generateAudio: true       // bakes in orchestral/score audio track
});
const url = result.data?.[0]?.url || result.url;
```
Response shape: `result.data[0].url` (some versions `result.url`). Video returns as MP4
(H.264 + AAC). Cost for 10s ≈ $3.20; keyframe edit ≈ $0.13.

## Wallet balance via direct Base RPC (no MCP wallet tool)
Derive the address from the key in `~/.blockrun/.session` (both `/root/.blockrun/.session`
and `/root/.hermes/profiles/gentech/home/.blockrun/.session` must match), then query USDC:
```bash
ADDR=$(python3 -c "from eth_account import Account; print(Account.from_key(open('/root/.blockrun/.session').read().strip()).address)")
# USDC on Base = 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913, decimals 6
DATA="0x70a08231000000000000000000000000${ADDR}"
curl -s https://mainnet.base.org -H "Content-Type: application/json" \
  -d "{\"jsonrpc\":\"2.0\",\"method\":\"eth_call\",\"params\":[{\"to\":\"0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913\",\"data\":\"$DATA\"},\"latest\"],\"id\":1}" \
  | python3 -c "import sys,json; print(f'USDC: \${int(json.load(sys.stdin)[\"result\"],16)/1e6:,.2f}')"
```
Note the address in the RPC hex MUST be concatenated WITHOUT a leading `0x` on the
address (the `0x70a08231...` selector already carries the `0x`) — a double `0x` yields
`Invalid params`. ETH balance: `eth_getBalance`.

## Cost estimate convention
State video cost as **"~$X"** (estimated), not a flat guarantee — upstream Seedance
pricing can exceed the listed rate. Report exact cost only after it settles.
