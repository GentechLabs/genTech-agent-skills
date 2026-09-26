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

## The 7-section prompt (harvested 2026-09-25 — sections marked ★ each fixed a failure that cost a full run)

Structure, in this order. Keep it even when the prompt is short.

1. **REFERENCE ROLES** — say what each reference governs **and what it does not**. Bind by index:
   `@image1` = identity only (face, hair, costume); `@image2` = board, staging only. A reference with
   no stated boundary gets used for everything.
2. **★ GUIDES ARE NOT CONTENT** — **a prohibition does not work here; a definition does.** Three runs
   carrying *"no arrows, symbols or annotation marks of any kind in frame"* still rendered a drawn
   arrow into the delivery; deleting the clause changed only the arrow's colour. What worked was
   telling the model what the marks **are**: *"frame borders, panel numbers, caption text and motion
   arrows are planning guides drawn on paper by the director. They describe the shot, they are not
   objects in the world. None of them exists in the scene."* Keep both halves.
3. **STARTING STATE** — one sentence of place, one of opening pose.
4. **★ TIMELINE** — one entry per beat, each carrying **all five**: timecode, `Panel N`, shot size +
   angle + lens/move, **entry pose**, **exit pose**. Each beat begins in the pose the last ended.
5. **CAMERA** — real rigs only (dolly/tripod); no drift where static is specified; fix motion blur
   with a shutter ("consistent with a 1/48 second shutter on 35mm film").
6. **MUST REMAIN UNCHANGED** — identity restated as invariants **plus the anatomy count** ("two arms,
   two legs, five fingers on each hand in every frame"). Cheap, catches the most common failure.
7. **CONSTRAINTS** — only failures the timeline cannot express (duplicated limbs, feet sliding
   without weight transfer, teleporting, watermarks, slow motion, freeze frames).

**Write action as physics, not adjectives.** Name approach → contact → transfer of force → recovery,
and give soft matter its **lag**: sleeves settling a beat after the arms stop, dust falling back after
heel contact. Measured: these render correctly from prose alone — **which is why motion never needs a
drawn arrow.**

**Audio asks — name the SURFACES, never the instrument.** *"Diegetic sound only: heel taps on the
boards, fabric, breath, room tone. No music, no score."* delivered clean audio; the same line **with
"a distant guitar" added failed the whole job on `OutputAudioSensitiveContentDetected`** — naming an
instrument invites music synthesis and can trip output-audio copyright. (Our 2.0 path is video-only,
so this bites only on audio-capable lanes.) `generateAudio: false` is the fallback *after* a
refusal, never the default.

## Board craft — draw the board LIGHT (measured, and counter-intuitive)

The board is a plan; **a board drawn as a competing picture gets treated as one.**

- A **photoreal** board leaked its **panel numeral into 6 of 8 shots** with the prompt held
  byte-identical. A light pencil board leaked none.
- A **heavily drawn** pencil board — full environment, dark solid arrows — **still rendered its
  arrows into the delivery as real arrows in shot**; three runs, no prompt clause suppressed them.
  Redrawn light with the same arrows in the same places → **48/48 frames clean.**
- So: thin pale pencil, bare white paper, setting in two or three quick lines, no heavy shading, no
  rendered environment. **Markings are safe on a light board, including motion arrows** — draw them
  broad, soft, feathered. **Numbering and captions have never transferred: 0 leaks in 93 chances.**
- Give **each character its own plate**, never a combined sheet — the prompt binds references by
  index, so `@image1` is fighter A and `@image2` is fighter B, each unambiguous. (2.5 takes up to 30
  reference images.)

## Consistency — the durability ladder

Holds come from what you feed the model, in **rising durability**: prompt baseline → reference images
→ style reference → control map → trained model.

- **Seeds do not solve consistency.** A seed reproduces one generation and transfers nothing. Leave
  it unset across a set; set one only to re-roll a single unchanged prompt.
- **Baseline-plus-delta:** write out everything that must **not** change, put the single change in a
  final clause, keep the baseline **byte-identical** between runs. **Look at the baseline first** —
  you cannot enumerate what you have not seen. Never write "same as before": there is no memory
  between calls.
- **⚠️ Never chain output → output.** Drift compounds. Our "sequential chain" strategy buys cinematic
  flow by degrading the character — that is a workaround, not the fix. **Anchor every clip to the
  same approved baseline** and use the chain only when continuity genuinely demands it.
- **Never put a turnaround sheet in a reference slot for video** — it animates the grid. Use
  individual neutral-pose shots; a scene still carries its props and pose into the slot.
- **Judge identity across the WHOLE clip, not one frame.** A clip's defect appeared at 11.0s; a
  one-frame-per-shot check read clean at 10.5s. Sample **~2 frames/second** before shipping. A named
  part gained/lost/recoloured/reshaped = drift; a part that **moves with the action** (a cloak
  swinging, an antenna tilting) = animation, and passes.

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
