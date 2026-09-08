# BlockRun ImageClient img2img — VERIFIED API (Aug 16, 2026)

The `clawrouter-proxy-media-generation` SKILL.md's "Image Editing (img2img)" section
describes an API shape that does NOT exist. This is the verified, working pattern.

## Correct class + method

- Class: **`ImageClient`** (NOT `VideoClient` — that's video-only)
- Method: **`edit(prompt, imageDataUri, options)`**
- There is NO `generateImage` method. `generate()` is text-to-image only and does
  NOT accept a reference image.

## Working example

```js
import { ImageClient, getOrCreateWallet } from '/root/.hermes/blockrun-mcp/node_modules/@blockrun/llm/dist/index.js';
import { readFileSync } from 'node:fs';

const wallet = getOrCreateWallet();
const client = new ImageClient({ privateKey: wallet.privateKey });  // auth: privateKey, NOT {wallet}

// Reference image MUST be a base64 data:image/... URI. Local paths and plain URLs
// are NOT accepted by edit().
const b64 = readFileSync('/path/to/source.jpg').toString('base64');
const sourceUri = `data:image/jpeg;base64,${b64}`;

const result = await client.edit(prompt, sourceUri, {
  model: 'openai/gpt-image-2',
  size: '1024x1024'
});
// result.data[0].url = generated image URL
```

## Key facts

- `edit()` takes a single base64 `data:image/...` URI, or an array of 2–4 URIs for
  image fusion (e.g. reference photo + brand logo). Server caps: `openai/*` up to 4,
  `google/*` (Nano Banana) up to 3. A `mask` cannot combine with multiple sources.
- Edit-capable models: `openai/gpt-image-1`, `openai/gpt-image-2`,
  `google/nano-banana`, `google/nano-banana-pro`.
- Auth: `new ImageClient({ privateKey: wallet.privateKey })`. Passing `{ wallet }`
  throws "Private key required".
- Cost ~$0.063/image. Run `node bal.mjs` first.
- Download the result URL, then SCP to VPS + `chmod 644` (web files default to 600
  = HTTP 403).

## Pitfall: vision_analyze falls back to text-only when the vision model is out of balance

When the wallet is low, `vision_analyze` silently falls back to a free text-only
model that cannot see images — it returns a generic "I can't view images" response
instead of describing the image. This is NOT a signal the image is bad; it's a
balance issue. Verify the image yourself (or top up the wallet) before trusting a
"can't view" response as a failure.
