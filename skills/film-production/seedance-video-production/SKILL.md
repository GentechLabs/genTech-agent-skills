---
name: seedance-video-production
description: Use when generating Seedance 2.0 video clips.
tags: [video, seedance, clawrouter, character-locking]
---

# Seedance 2.0 Video Production

## Quick Reference

| Property | Value |
|----------|-------|
| **Model** | `bytedance/seedance-2.0` |
| **Endpoint** | `POST http://127.0.0.1:8402/v1/videos/generations` |
| **Auth** | `Authorization: Bearer hermes-plugin` |
| **Cost** | ~$1.14 per clip (~5s actual output despite requesting 10s) |
| **Audio** | Video-only — NO audio tracks. Mix separately with ffmpeg. |

## Standing Model Rules (Aug 2026)
- **Images:** GPT Image 2 ONLY via ClawRouter or BlockRun MCP. ~$0.06-0.13.
- **Video:** Seedance 2.0 ONLY. Never switch unless Vanito says so.

## Seedance 2.5 vs 2.0 (Aug 2026 — 2.0 remains default for KAGE)
2.5 is live (Aug 7, 2026) but NOT a drop-in upgrade for character combat. 2.5 gains: up to 30s single-pass (2.0 caps at 15s), larger reference budget (30 img / 10 vid / 10 audio vs 2.0's 9/3/3), timestamp-level editing + green-screen/R2V control.
**Why STAY on 2.0 for KAGE:** independent fighting tests show 2.5 gets blurry during fast motion — a direct problem for gunfights, flips, kicks. 2.0 preserves the dark gothic digital painting style on short stitched clips, is predictable, and is already wired through ClawRouter. Route short action/combat clips → 2.0; only test 2.5 for a single continuous 30s scene or when stitching creates a continuity break. Do NOT switch the KAGE pipeline to 2.5 without an explicit user OK.

## Submission Pattern
Always `cat > file <<'ENDJSON'` — inline JSON in curl breaks on shell quoting:
```bash
cat > /tmp/payload.json << 'ENDJSON'
{"model":"bytedance/seedance-2.0","duration":10,"resolution":"720p","prompt":"...","image_url":"https://...","aspect_ratio":"16:9"}
ENDJSON
curl -s -X POST http://127.0.0.1:8402/v1/videos/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer hermes-plugin" \
  -d @/tmp/payload.json > /tmp/response.json
```

## Character Locking
Character degrades during action because the keyframe shows one pose but the action needs different poses → model guesses → character morphs.

**Fix A: Action Reference Sheets.** Generate multi-pose sheet via GPT Image 2 (3-5 poses, 1536×1024, ~$0.13). Use as `image_url` seed.
**Fix B: Locked description in every prompt.** Paste full character visual description into every Seedance prompt.

For multi-character scenes, generate matching sheets for each character type.

## Clip Generation Strategies

**Parallel (same keyframe):** Fast but jumps back to static image. User rejects.
**Sequential chain:** Each clip feeds its last frame as seed for next. Cinematic flow but character degrades.
**Action sheets + chain (BEST):** Use action sheets for first 2-3 clips, then sequential chain.

Extract last frame:
```bash
ffmpeg -y -sseof -1 -i clipN.mp4 -vframes 1 frameN.png
cp frameN.png /var/www/gentechlabs/frameN.png && chmod 644 /var/www/gentechlabs/frameN.png
```

## Audio Mixing
Seedance returns video-only. Mix audio separately:
```bash
ffmpeg -y -ss 30 -i "track.mp3" -t 30 -c:a libmp3lame -b:a 192k \
  -af "afade=t=in:d=1,afade=t=out:st=28:d=2" audio.mp3
# VERIFY: if max_volume is -91 dB, trim captured silence → re-extract
ffmpeg -i audio.mp3 -af "volumedetect" -f null /dev/null 2>&1 | grep max_volume
# Stitch + mix
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy video-only.mp4
ffmpeg -y -i video-only.mp4 -i audio.mp3 -c:v copy -c:a aac -b:a 192k -shortest \
  -map 0:v:0 -map 1:a:0 final.mp4
```

## Wallet
- ClawRouter caches balance at startup. After funding: `sudo systemctl restart clawrouter-proxy.service`
- Payment failure + "execution reverted" = insufficient USDC (~$1.14/clip needed)
- Wallet: `0xebc8c71970EEb6973bd87F1FF146B3Ec4a5972f8` (Base)

## Dimensions
| Keyframe | Seedance Output | Result |
|----------|----------------|--------|
| 1024×1024 | 1280×720 | ❌ Stretched |
| 1536×1024 | 1280×720 | ✅ OK |

## BlockRun Quirks
- `client.edit()` → CDN URLs; `client.generate()` → data URLs (base64, save via decode)
- `client.getBalance()` broken — use `node bal.mjs`
