---
name: clawrouter-proxy-media-generation
description: "Use when generating images or video via ClawRouter proxy."
tags: [media, video, image, proxy, clawrouter, seedance, gpt-image-2, wallet]
---

# ClawRouter Proxy Media Generation

## Model Lock (Standing Rules Aug 2026)

- **Images:** GPT Image 2 ONLY (`openai/gpt-image-2`). Never switch unless Vanito says.
- **Video:** Seedance 2.0 ONLY (`bytedance/seedance-2.0`). Never switch to FLUX 3, xAI Grok, or anything else.

## Proxy Endpoints

- Images: `POST http://127.0.0.1:8402/v1/images/generations` with `Authorization: Bearer hermes-plugin`
- Video: `POST http://127.0.0.1:8402/v1/videos/generations` with `Authorization: Bearer hermes-plugin`

## Wallet

- Address: `0xebc8c71970EEb6973bd87F1FF146B3Ec4a5972f8` on Base
- Balance check: `cd /root/.hermes/blockrun-mcp && node bal.mjs`
- GPT Image 2: ~$0.06–0.13/image, Seedance 2.0: ~$1.14/clip

## Critical Pitfalls

### 1. Proxy caps all video at ~5 seconds
The `duration` field is ignored. Every Seedance clip is ~5s. Chain multiple clips via ffmpeg concat.

### 2. Proxy delivers video-only — NO audio
Output contains video track only. Audio MUST be added separately. Source from `/root/vaults/gentech/music/`.

### 3. Check balance BEFORE every generation
Wallet low = misleading payment errors. Always run `node bal.mjs` first.

### 4. Stale wallet cache
If wallet has funds but generation rejected: `sudo systemctl restart clawrouter-proxy.service`.

## Video Workflow

1. Check balance: `node bal.mjs`
2. Submit clips in parallel background processes with notify_on_complete=true
3. Download each clip via proxy URL
4. Concat: ffmpeg concat demuxer with `-c copy`
5. Add audio from vault via ffmpeg
6. Verify: `ffprobe` for duration + audio

## Image Editing (img2img)

Use BlockRun `ImageClient` directly: import from `/root/.hermes/blockrun-mcp/node_modules/@blockrun/llm/dist/index.js`. Pass scene as `image`, character sheet in `images` array. Model: `openai/gpt-image-2`.
