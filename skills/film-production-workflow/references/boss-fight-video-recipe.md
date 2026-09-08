# Boss-Fight Video Recipe (Seedance 2.0)

Canonical recipe for a "fight video" / "make a video of them fighting" request.
This is what Vanito means by a fight video — an ANIMATED Seedance clip, NOT an
ffmpeg slideshow. Modeled on the Lightning vs Embermaw workflow (Aug 4, 2026) and
the Ringed Knight vs Nameless King build (Aug 5, 2026).

## Steps

1. **Compose a keyframe** of both characters facing off. Use `ImageClient.edit`
   with BOTH character sheets as the image array (gpt-image-2, 1536x1024):
   ```js
   import { ImageClient, getOrCreateWallet } from '/root/.hermes/blockrun-mcp/node_modules/@blockrun/llm/dist/index.js';
   import { readFileSync } from 'node:fs';
   const wallet = getOrCreateWallet();
   const client = new ImageClient({ privateKey: wallet.privateKey });
   const a = readFileSync('/path/charA.png'); const aUri = `data:image/png;base64,${a.toString('base64')}`;
   const b = readFileSync('/path/charB.png'); const bUri = `data:image/png;base64,${b.toString('base64')}`;
   const result = await client.edit(prompt, [aUri, bUri], { model: 'openai/gpt-image-2', size: '1536x1024' });
   // result.data[0].url
   ```
   Keyframe prompt: name BOTH characters' full locked descriptions, the standoff
   pose, the arena, and the style. Add negatives for anything the model hallucinates
   (e.g. "NO WINGS on the Nameless King — he has NO wings, he is on foot").

2. **Show the keyframe to Vanito and get his "yes" BEFORE animating.** One-scene-at-a-time rule.

3. **Animate** with `VideoClient.generate`:
   ```js
   import { VideoClient, getOrCreateWallet } from '/root/.hermes/blockrun-mcp/node_modules/@blockrun/llm/dist/index.js';
   const client = new VideoClient({ privateKey: wallet.privateKey });
   const result = await client.generate(prompt, {
     model: 'bytedance/seedance-2.0',
     imageUrl: KEYFRAME_URL,
     durationSeconds: 10,
     aspectRatio: '16:9',
     generateAudio: true
   });
   // result.data[0].url
   ```

4. **Fight-clip prompt structure** (from make-lightning-vs-embermaw.mjs):
   ```
   [Style] boss fight CG, N seconds, one continuous cinematic take, [setting].
   Seeds from the provided image: [CHARACTER A full description] versus [CHARACTER B full description].
   TIMELINE:
   0-3s: [opening beat — action verbs, blood/impact]
   3-6s: [middle beat — charge, dodge, weapon raised]
   6-10s: [climax — leap, drive weapon in, boss slain, no victory pose]
   CAMERA: one seamless move (push-in → tracking → pull-back/tilt), no orbits.
   STYLE: [game] / FromSoftware gothic horror game art, AAA cutscene, painterly dark fantasy,
   cinematic HDR, volumetric fog, 24fps, [palette].
   NEGATIVE: static opening, scene reset, fade-in, character re-entry, camera reset, time jump,
   character redesign, outfit change, weapon change, extra characters, deformed hands, bad anatomy,
   text, watermark, subtitles, UI, low resolution, blurry, live-action realism, freeze frame.
   ```
   Action verbs in the first 15 words of each beat (CHARGE, lunge, burst, claw) — never "stand."

5. **Layer the requested theme** as background sound (see OST sourcing in the main
   SKILL.md — khinsider → vgmtreasurechest CDN when YouTube is blocked).

6. **Deploy** — bump version in filename to bypass Cloudflare cache, chmod 644.

## Cost
- Keyframe (gpt-image-2 1536x1024): ~$0.065
- 10s Seedance clip: ~$3.20 (can exceed listed rate by 30-75%)
- Check wallet balance first (need $5+). Balance check via direct RPC eth_call on
  USDC contract `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` on Base mainnet.

## Pitfalls
- The keyframe model adds wings to characters that shouldn't have them, or a beard
  to a hollowed face — add explicit negatives and verify with vision_analyze.
- Show the keyframe to Vanito before animating; he will flag lore/design errors.
- The `edit` method takes a single `image` param — pass the array of data URIs there.
