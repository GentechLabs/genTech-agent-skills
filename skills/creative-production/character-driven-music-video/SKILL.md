---
name: character-driven-music-video
description: >-
  Produce animated music videos with consistent AI-generated characters using
  reference-driven workflows. Covers the full pipeline: character model sheets,
  animation with xAI video model, ffmpeg overlay effects, audio sync, and
  Wav2Lip lip-sync. Optimized for Vanito/KAGEKŌ dark gothic visual kei style.
trigger: >-
  🔴 CRITICAL — ONLY use this skill when the user EXPLICITLY asks to
  generate/animate/create a music video, teaser, GIF, or
  character-driven AI video, OR to transform characters in existing
  artwork/promotional images. Vanito's exact words: "No more videos unless I say so."
  Do NOT trigger video generation on: discussing lyrics, song concepts, Donna formatting,
  character backstory, character design requests, or album artwork —
  those are NOT video requests. HOWEVER, album artwork / promotional
  image creation (still images, covers, posters) IS in scope — use the
  Character Transformation section below, not the video pipeline.
  Even if the user says "Seedance" or "anime" or "animation" in passing,
  DO NOT run video generation unless the user's request is explicitly
  and unambiguously a video request.
tags:
  - music-video
  - character-consistency
  - ai-animation
  - gothic-visual-kei
  - ffmpeg-effects
  - seedance-2.0
  - multi-shot-sequence
  - poster-to-video
---

# Character-Driven AI Music Video Production

## 🚫 Rule 0: Only Run When Explicitly Asked
Vanito's exact words: **"No more videos unless I say so."**

Do NOT generate, animate, or create any video output — including teasers, GIFs, Seedance clips, or poster loops — without Vanito explicitly and unambiguously requesting video work. Discussing lyrics, song concepts, Donna tags, character backstory, or album art is NOT a video request. If there's any doubt, ask before running.

This rule overrides all other rules below. No exceptions.

## 🔴 Rule 0.5: Always Pull the Definitive Reference Before Generating KAGE

Before generating ANY image of KAGE — character sheet, poster, scene, or animation — you MUST consult the definitive reference image first. KAGE's design has evolved across multiple looks; guessing from memory or vault notes produces the wrong character every time.

**Primary definitive reference (2026-07-24+):** `music/vanito/kage-character-sheet.png` in the repo — official multi-view sheet with phoenix emblem, winged cross, razor blade pendant, industrial chain, blackwork tattoos. Also reference `kage-blood-on-strings-v5.jpg` for the gritty poster aesthetic.

**Workflow (enforced 2026-07-24 after Vanito correction):**
1. Run vision_analyze on the definitive reference (`kage-character-sheet.png` first, then `kage-blood-on-strings-v5.jpg`)
2. Enumerate EVERY visible detail from the reference — do NOT skip anything
3. Write the generation prompt with ALL details included
4. Pre-verify with vision_analyze before showing Vanito

**Known KAGE pitfalls (learned 2026-07-24):**
- ❌ Zombie skin — Seedream adds black vein patterns unless told "natural human pale skin, no zombie texture, no black veins, no cracks"
- ❌ Missing tattoos — blackwork scribble on right forearm/back of right hand is essential
- ❌ Wrong pendant — RAZOR BLADE (rectangular with two holes), not a star or cross
- ❌ Coat-open — all models struggle with zipped coats; accept this limitation
- ❌ Guessing from memory — ALWAYS check the reference image first

## 🔥 Character Sheet → Seedance Animation Pipeline (Confirmed 2026-07-24)

Inspired by @Mayz1169 on X: create a multi-view character sheet, then use it as Seedance's visual anchor for consistent character across all animation scenes.

**Step 1 — Create the sheet:**
- Use openai/gpt-image-2 (best for clean layout + text labels)
- Layout: front view (A-pose) + back view + detail callout boxes
- Dark grey background, uniform lighting, text labels identifying details
- Enumerate EVERY character detail in the prompt

**Step 2 — Save and push:**
- Save to `music/vanito/kage-character-sheet.png`
- Git add → commit → pull --rebase → push
- Use raw.githubusercontent.com URL as permanent reference

**Step 3 — Animate with Seedance 2.0:**
- Feed the sheet as Seedance 2.0 seed image
- Prompt for MOTION only — NOT appearance
- Per-clip cost: ~$2.55-3.19/10s

**Step 4 — Image-to-image editing for detail fixes:**
When an image needs specific additions (tattoos, emblems, accessories):
- blockrun_image with action="edit", image parameter (NOT image_url)
- Model: openai/gpt-image-2 ($0.065/image)
- Prompt: "Add [detail]. Keep everything else exactly the same — same face, same hair, same coat, same background."
- CRITICAL: Every edit pass reinterpretes the entire image. Do NOT cascade edits — apply ALL fixes in ONE pass
- Pre-verify with vision_analyze before showing Vanito

## 🔥 Cinematic 15-Second Film Pipeline (Confirmed 2026-07-24)

Inspired by @Mayz1169 on X. Create short cinematic anime-style film intros by combining time-coded Seedance clips + sound design + title overlays with ffmpeg.

### The Core Technique: Time-Coded Prompts + Character Coating

The secret to character consistency across multiple Seedance clips is **the full character description block repeated inline in every prompt** — not just "the character" but every detail, every time. This is called the "coating."

**KAGE coating block (paste verbatim into every video prompt):**
```
(character reference "KAGE": jet black spiky messy hair covering eyes, pale skin 
with dark guyliner and smoky eye makeup, long black leather trench coat open with 
a massive dark red phoenix emblem embroidered across the entire back — wings 
spread, tail flowing — silver razor blade pendant on ball chain around neck, 
heavy silver industrial chain draped across chest, black t-shirt with bold red 
winged cross graphic, black skinny ripped jeans, black combat boots, dense black 
scribble tattoos covering both forearms and backs of both hands, black Gibson 
Les Paul electric guitar with silver hardware)
```

**Time-coded action structure:**
```
[0-3s] WIDE SHOT — Establish scene, character appears or is shown in context
[3-6s] SLOW PUSH — Camera moves in, tension builds
[6-9s] REVEAL — Character turns or action begins
[9-12s] WALK/TRACK — Character moves, medium tracking shot
[12-15s] CLIMAX — Peak action, freeze frame, title card fades in
```

**Style block at end of prompt:**
```
Style: cinematic anime aesthetic, Makoto Shinkai rain, hyper-detailed water, 
cinematic depth of field. Palette: CRIMSON #CC0000, DEEP BLACK #0A0A0A, NEON 
RED #FF2200, COLD RAIN #4488CC, AMBER WARMTH #FF8844. Character design strictly 
consistent throughout. Lighting: blood moon rim backlight, neon city fill from 
below. Camera: wide establish → slow push → profile reveal → tracking walk → 
freeze frame climax — one continuous feeling, no hard cuts. Emotional arc: 
solitude → tension → determination → climax.
```

### Seedance Duration Constraint & Multi-Clip Concat
Seedance 2.0 **max = 10 seconds per clip** (text-to-video). **Image-to-video caps at 5s/clip** — for a 60s film use 12 clips of 5s.

**⚠️ CRITICAL (Aug 2026): the `clawrouter_video_generate` tool wrapper strips `image_url`** — it only forwards `model`, `duration`, `resolution`. To seed a video from a character sheet (required for hair/feature consistency), call the proxy directly:
```bash
curl -s -X POST "http://127.0.0.1:8402/v1/videos/generations" \
  -H "Content-Type: application/json" -H "Authorization: Bearer hermes-plugin" \
  -d '{"model":"bytedance/seedance-2.0","duration":5,"resolution":"720p","image_url":"<PUBLIC_URL>","prompt":"..."}'
```
- Correct path is `/v1/videos/generations` (bare `/videos/generations` returns 404)
- Requires `Authorization: Bearer hermes-plugin` header
- Observed cost: ~$1.14/5s image-to-video clip (vs $2.55-3.19 text-to-video)
- Seed image MUST be a public URL — BlockRun-hosted or FAL media URLs work; GitHub raw can 404 on CDN lag; localhost URLs blocked

For 15-second sequences:
1. Generate one 10s clip (covers [0-10s]) — ~$2.55-3.19
2. Generate one 5s clip (covers [10-15s]) — ~$1.30-1.60
3. Concat both with ffmpeg demuxer (`-f concat`)
4. Overlay mixed audio (ambience + delayed impacts)
5. Add title overlays with drawtext
6. Total video cost: ~$4.79, + SFX ~$0.15 = **~$5.00**

### Director's Cut Title Overlays (ffmpeg drawtext)

Available font: `/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf`

| Title | Size | Color | Position | Timing |
|-------|------|-------|----------|--------|
| "A GenTech Labs Production" | 28 | White 80% alpha | Center | 0.5-2.5s |
| Character name | 52 | #CC0000 (blood red) | Center | Last 2s of clip |
| Subtitle | 28 | White 90% alpha | Below name | Last 1.5s |

### Sound Design Layering

Generate SFX via blockrun_speech(action="sound_effect"), ~$0.05 each (URLs expire — download immediately):

- Rain ambience: "Heavy cinematic rain pouring on a city rooftop, steady downpour, dark storm atmosphere" — 15s
- Chord impact: "Massive guitar power chord impact, explosive energy blast, deep subwoofer boom" — 5s
- Thunder rumble: "Deep distant thunder roll, low frequency rumble through storm clouds" — 5s

Layer with ffmpeg:
```bash
# Mix: ambience throughout at 50% + impact at 12s mark at 180%
ffmpeg -y -i ambience.mp3 -i impact.mp3 \
  -filter_complex "[0:a]volume=0.5[A];[1:a]adelay=12000|12000,volume=1.8[B];[A][B]amix=inputs=2:duration=first" \
  audio-mix.mp3

# Combine mixed audio with concatenated video
ffmpeg -y -i raw-scene.mp4 -i audio-mix.mp3 \
  -c:v copy -c:a aac -b:a 192k -shortest final-scene.mp4
```

### Full 15-Second Build Order (confirmed working 2026-07-24)

```bash
# 1. Download all assets
curl -s -o clip1.mp4 "<10s-clip-url>" && curl -s -o clip2.mp4 "<5s-clip-url>"
curl -s -o rain.mp3 "<rain-sfx-url>" && curl -s -o impact.mp3 "<impact-sfx-url>"

# 2. Concat video clips
echo -e "file 'clip1.mp4'\nfile 'clip2.mp4'" | ffmpeg -y -f concat -safe 0 -i /dev/stdin -c copy raw-merge.mp4

# 3. Mix audio layers
ffmpeg -y -i rain.mp3 -i impact.mp3 -filter_complex "[0:a]volume=0.5[A];[1:a]adelay=12000|12000,volume=1.8[B];[A][B]amix=inputs=2:duration=first" audio-mix.mp3

# 4. Combine video + audio
ffmpeg -y -i raw-merge.mp4 -i audio-mix.mp3 -c:v copy -c:a aac -b:a 192k -shortest vid-audio.mp4

# 5. Add title overlays
ffmpeg -y -i vid-audio.mp4 \
  -vf "drawtext=text='A GenTech Labs Production':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf:fontsize=28:fontcolor=white:alpha=0.8:x=(w-text_w)/2:y=(h-text_h)/2-40:enable='between(t,0.5,2.5)',drawtext=text='KAGE':fontsize=52:fontcolor=#CC0000:x=(w-text_w)/2:y=(h-text_h)/2-30:enable='between(t,13,15)',drawtext=text='BLOOD MOON RISING':fontsize=28:fontcolor=white:alpha=0.9:x=(w-text_w)/2:y=(h-text_h)/2+30:enable='between(t,13.5,15)'" \
  -c:a copy -preset fast final.mp4

# 6. Deliver via Telegram
# MEDIA:/path/to/final.mp4
```

## Golden Rules
### Rule 1: Start from the exact reference image
**Never generate a new interpretation from text alone.** Text prompts drift the art style. The user's own reference image is the only source of truth.

### Rule 2: Seedance 2.0 is THE primary model — do not use xAI for character scenes.

**✅ Seedance 2.0 (bytedance/seedance-2.0)** — MANDATORY for ALL poster/album-art character animation. Vanito explicitly endorsed this model. It preserves the dark gothic digital painting style perfectly. Cost: ~$2.55/8s, ~$3.19/10s, ~$1.60/5s.

**❌ xAI grok-imagine-video** — NEVER use for any scene with character art. It adds photorealistic/shimmer texture to digital painted art. Vanito will reject output as "too real." Only use for: abstract/background-only shots, or quick $0.26 previews the user explicitly approves for non-character content.

**⚠️ ffmpeg overlay effects** — Fallback only when user explicitly asks for a poster loop with NO animation. Vanito called this approach "underwhelming" (2026-07-12) because overlays are too subtle against the poster's existing lighting. If you must use it:
- Work at half resolution (640×426 max)
- Use 15fps max, limit to 10-12 seconds  
- Make effects VERY strong/visible (high alpha, high contrast)
- Focus on: moon glow pulsing, wide red spotlight sweeps, floating embers, rhythmic strobe flashes

### Rule 3: The poster stays as-is in prompts
When animating a poster/album art image, the prompt MUST state: "The exact same image comes to life... Nothing about their appearance changes... Same art style... Same camera angle..." Without this, the model generates a new interpretation, which the user will reject.

### Rule 4: Lock the camera perspective explicitly
When the poster shows characters from BEHIND (facing the crowd/moon), every prompt MUST include: "Same camera angle behind them the whole time. They never turn around or face the camera." The user will reject any prompt that lets the model rotate the perspective.

### Rule 5: Multi-shot sequences require separate clips + concat
Complex scenes (walk onto stage → perform) need 2+ clips stitched together:
1. Generate a transitional scene image (e.g., characters walking through a door onto stage)
2. Animate each image separately with Seedance 2.0
3. Rescale clips to the same resolution
4. Concat with ffmpeg demuxer
5. Overlay audio track

### Rule 6: Remove text from posters first when requested
Use GPT-Image-2 edit mode to remove title text, logos, and branding before animating. Vanito explicitly requested this (2026-07-12) for clean looping GIFs.
When the user sends a poster/album art image and asks for a looping GIF, they want the image EXACTLY as-is with effects on top. They do NOT want AI animation that changes character positions, style, or adds realistic motion. The ffmpeg overlay effects approach is the only correct path for poster loops.

## User Preferences (Vanito — KAGEKŌ)

**🔴 CRITICAL: Never generate character images from text description alone.**
Vanito's character designs evolve. Always start from his current reference image. If you don't have one, ask him to send it — don't guess from memory. Multiple failed generations waste budget and patience. Confirmed 2026-07-17: three generations failed because the KAGE design had changed (see Look 3 below).

- **Style:** Dark gothic visual kei digital painting. NOT anime, NOT photorealistic.
- **KAGE has three confirmed looks (full details in references/vanito-character-specs.md):**
  - **Look 1** (older, ornate): Spiky black hair, long dark coat with red kanji, star/cross pendant, skull-antler tee, waist chain, Dean ML / Flying V guitar.
  - **Look 2** (poster): Sleeveless black tee with back text, no jacket/accessories.
  - **Look 3 (current as of 2026-07-17):** Plain black t-shirt, no jacket, rectangular pendant, FULL BLACKWORK SLEEVE TATTOOS both arms, Stratocaster with "KAGE" text, wet messy hair, bloody hands. Grungier/rawer.
- **Guitar per song:** Dean ML/Flying V (Look 1), Les Paul double-cutaway (Yami no Naka De), Stratocaster with "KAGE" text (Blood on the Strings — current).
- **HIKARI:** Long black hair with vibrant RED HIGHLIGHTS/STREAKS throughout (not just tips), black lace choker with pendant, off-shoulder black corset with criss-cross lacing, detached black lace fingerless sleeves, asymmetrical black skirt with red underskirt, high slit left thigh, fishnets with garter strap, black platform boots with silver buckles, multiple silver rings, black arm bands. She is the vocalist.
- **Look 5: Official Character Sheet KAGE (2026-07-24 — current consolidated look):**
  - Long black leather trench coat (not shredded) with PHOENIX EMBLEM on back in dark red
  - Black t-shirt with red WINGED CROSS graphic on front
  - Silver RAZOR BLADE pendant on chain around neck
  - Heavy silver INDUSTRIAL CHAIN draped across chest
  - Dense black scribble/blackwork tattoo on RIGHT FOREARM and back of right hand
  - Spiky black messy hair, pale skin, dark guyliner — NO zombie veins
  - Silver chain with padlock on waist
  - Black combat boots
  - Black Gibson Les Paul electric guitar
  - Blood on hands (theatrical performance blood)
  - Setting: Tokyo rooftop, blood red moon, rain, ravens
  - Source: `music/vanito/kage-character-sheet.png` on hub
- **Poster:** KAGE on left (arms crossed, coat with kanji), HIKARI on right-center (mic, red-highlight hair). View from BEHIND them facing crowd + moon.
- **All assets** are served from: https://raw.githubusercontent.com/ProtoJay4789/ProtoJay4789.github.io/main/github/ProtoJay4789.github.io/music/vanito/scenes/

For publishing completed songs with cover art to Vanito's hub page, see `references/hub-music-deployment.md`.

## 🔥 Cinematic Storyboard Technique — Per-Second Film Script

Before generating anything, write a **35-60 second film script** broken into 5-7 scenes, each 5 seconds. This is the difference between random clips and a directed short film.

### Every scene MUST include:

| Element | What to specify | Example |
|---------|----------------|---------|
| **Shot type** | close-up, medium, wide, dolly, push-in, track, pan, tilt | "Extreme close-up. A single red bulb hanging from a black twisted cord." |
| **Camera motion** | how the camera moves during the scene | "Slow push-in. The red light fills the frame." |
| **Character blocking** | where they are, how they move | "KAGE's tattooed fingers strike the first chord. Hard. The strings vibrate." |
| **Character action** | BOTH characters sing — they are vocalists | "HIKARI steps forward. Her voice joins his — harmonizing." |
| **Lighting cues** | how light changes during the scene | "The red light pulses faster. Papers on the floor lift and scatter." |
| **Sound cues** | what the audience hears | "The first guitar notes of 4AM begin. Distant, echoing." |
| **Lyrics sync** | which lyrics play during this scene | "Lyrics synced: 'The night we both came alive / first song we ever wrote was a scream and a note'" |
| **Mood** | one line describing the emotional tone | "Explosive. The chorus hits and everything intensifies." |

### Storyboard structure (synced to song):
1. **0-5s** — Intro / Instrumental (establish the space, the light, the mood)
2. **5-10s** — Verse 1 (KAGE begins singing, first chord)
3. **10-15s** — Verse 2 (HIKARI joins, harmonizing, camera tracks to her)
4. **15-20s** — Chorus (both together, wide shot, room comes alive)
5. **20-25s** — Bridge / Instrumental (KAGE solo, guitar close-up)
6. **25-30s** — Final chorus build (HIKARI's moment, close-up, emotion)
7. **30-35s** — Outro (last chord fades, they look at each other, light dims)

### Key principles:
- **Every scene has a camera direction** — not just "what happens" but "how we see it"
- **Both characters sing** — KAGE and HIKARI are both vocalists, not static figures
- **The storyboard is synced to the song's structure** — intro → verse 1 → verse 2 → chorus → bridge → final chorus → outro
- **Save the storyboard** as `<song-name>-storyboard.md` in the music folder for reference
- **Each scene becomes one Seedance clip** — 5 seconds each, 7 scenes = 35 seconds of unique footage
- **Loop the animation** to fill the full song duration (4:02 = ~7 loops of 35s)

### Example (from 4AM / 四時):
```
### SCENE 3 — HIKARI JOINS (10-15s) — Verse 2
Shot: Camera tracks right. HIKARI comes into frame. She's standing now, not sitting.
  Her long black hair with blood-red tips falls over her pale shoulders.
Motion: She steps forward. Her voice joins his — harmonizing. Her fishnet-covered
  hand reaches toward him, fingers stretching out. Her dark eye makeup catches
  the red light. She's singing directly to him.
Camera: Dolly move — smooth, gliding. The camera circles her slowly as she sings.
Lyrics synced: "The night we both came alive / first song we ever wrote was a scream and a note"
Mood: She's not just watching anymore. She's in it. Both of them now.
```

## Pipeline

### Step 1: Lock the Reference
- Save the user's character sheet image
- Upload to hub (`git add -f music/vanito/scenes/<name>.jpg`)
- Push commit to ProtoJay4789.github.io (origin remote)
- Use the raw.githubusercontent.com URL as the image source

### Step 2: Scene Generation (optional — for transitional shots)
If the user describes a scene that doesn't exist yet (characters walking through a door, entering from wings, etc.), generate it first:
- Use `openai/gpt-image-2` (not FLUX, not xAI)
- Size: 1536x1024 (widescreen — matches concert poster proportions)
- Prompt must reference "same style as the KAGEKŌ poster" + the specific action/position
- Upload to hub, then animate with Seedance 2.0

**Text removal from posters:** When the user wants a clean image:
- Use GPT-Image-2 edit mode: pass the image URL, prompt "Remove all text... Keep everything else exactly the same"
- This preserves the art style while stripping titles, logos, and branding

### Character Transformation (Image-to-Image Editing)

When Vanito sends existing artwork or promotional images where the characters don't yet match the established KAGE/HIKARI designs, use **openai/gpt-image-2** in edit mode to transform them. This preserves the composition, mood, lighting, text overlays, and setting while updating character appearances.

**Tool:** `openai/gpt-image-2` via blockrun_image with `action="edit"` ($0.06–0.12/image, 1536x1024 recommended for widescreen scenes)
**Do NOT use:** FLUX 2 (drifts photorealistic), xAI grok-imagine-image (adds shimmer/drift), zai/cogview-4 (too cheap/fast for detailed character work)

**Prompt pattern:**
```
mcp__blockrun__blockrun_image(
    action="edit",
    image="<source_image_path>",
    model="openai/gpt-image-2",
    size="1536x1024",
    prompt="""Edit this [scene type]. Transform the characters to match established character designs while keeping the exact same composition, lighting, setting, and text overlays.

[CHARACTER POSITION]: Transform into KAGE — messy spiky black hair, dark leather biker jacket with silver studs on collar/shoulders, dark t-shirt, sharp angular jaw, intense expression.

[CHARACTER POSITION]: Transform into HIKARI — long flowing black hair with vibrant crimson red highlights/streaks throughout (not just tips), black off-shoulder corset bustier with criss-cross lacing, black lace choker with silver pendant, detached black lace fingerless sleeves, fishnet stockings, platform boots with silver buckles.

Keep all existing elements exactly the same: [environment details].
Preserve all text and lyrics: [list specific text in English + Japanese].

Art style: Dark gothic visual kei digital painting. Textured, dramatic lighting. NOT photorealistic. NOT anime/cartoon. The characters should look naturally part of the scene — not pasted in or obviously edited."""
)
```

**Critical rules:**
- Be EXTREMELY specific about clothing — the model adds generic gothic wear if you're vague. List every item: "studded leather jacket", "off-shoulder corset with criss-cross lacing", "black lace choker", "fishnet stockings", "platform boots with silver buckles".
- Name hair style AND color per character, including "vibrant crimson red highlights/streaks throughout" for HIKARI (not "ombre" or "tips-only").
- Explicitly list what to preserve: "empty theater chairs", "rainy window", "wet reflective floor", "scattered sheet music", "notebook in foreground".
- Explicitly enumerate EVERY text element to preserve, including Japanese kanji/kana — the model drops or garbles non-Latin text if not named.
- Always include the art-style guard: "NOT photorealistic. NOT anime/cartoon."
- For silhouetted or distant figures, focus on what IS visible (hair silhouette, jacket shape, stance). Fine details like chokers or rings won't render at that distance.

**Post-generation review (mandatory before showing Vanito):**
Run vision_analyze and check all seven:
1. KAGE: spiky black hair + signature jacket/accessories?
2. HIKARI: red hair highlights + specific outfit items? Hair must be BLACK with RED highlights/streaks, not solid red or ombre-only.
3. Character roles correct: KAGE screams (anguish/raw power), HIKARI sings (melodic/emotive). Don't assign scream poses to HIKARI or melodic poses to KAGE.
4. Text overlays preserved and readable (including Japanese kanji/kana)?
5. Art style: dark gothic visual kei (no photorealism/anime drift)?
6. Characters look NATURALLY part of the scene (not pasted/edited)? Look for hard edge lines, glow borders, or "sticker" artifacts around any element.
7. Props in shadow (guitar in corner, objects in darkness) properly dark and subtle — they should not draw the eye from the focal point. Check for unnatural edge lines or "chain" artifacts on foreground objects (papers, notebooks).

Do NOT send output until all seven pass.

**Observed cost for 3-image set (2026-07-15):** $0.36 ($0.12 × 3). Pre-flight confirmation still required per the 🔴 Critical protocol below.

### Step 3: Animate

**Path A — Seedance 2.0 (bytedance/seedance-2.0)** — MANDATORY for all character scenes
- Feed the image as `image_url` (raw GitHub URL only, never BlockRun endpoint)
- Prompt describes ONLY the action, NOT the appearance
- **MUST include:** "Same camera angle behind them the whole time" for stage shots
- **MUST include:** "Same dark digital painting style" to prevent photorealistic drift
- Duration: 8-10 seconds per clip
- Cost: ~$2.55/8s, ~$3.19/10s

**🔥 Confirmed poster-to-character-animation pattern (Jul 14 — Vanito approved):**
Seedance 2.0 CAN animate specific dramatic character movements from a single poster — not just subtle breathing:
- **Prompt structure:** Describe the character arc (starts X → then Y — with emotion Z)
- **Dual-character motion works:** KAGE screaming upward while HIKARI reacts emotionally in the same frame
- **Approved prompt template:**
  ```
  Cinematic animation of this album art scene.
  [Character A] starts [initial pose/action], then [transition] with [emotion].
  [Character B] [reaction/emotion]. The [environment element] reacts subtly.
  Dark, emotional, atmospheric mood.
  ```
- **Cost confirmed:** $2.55 for 8 seconds (Seedance 2.0, Jul 14 session)
- **GIF conversion:** ffmpeg at 8fps/480px → ~9MB for 8s clip
- **Hub hosting:** push GIF to `music/vanito/` on ProtoJay4789.github.io

**Prompts to AVOID** from failed attempts:
- ❌ "Subtle cinematic movement... gentle flickering... slight breathing" — Vanito called this "underwhelming"
- ✅ Instead use specific character arcs: "starts hunched over reading, then lifts head and screams to the sky"

**Path B — xAI Video Model (grok-imagine-video)**  ← Use only for quick previews
- For: quick animation tests, background-only shots, scenes with no character faces
- Use the character sheet directly as `image_url`
- Prompt MUST emphasize: "The exact same image comes to life... Nothing about their appearance changes... Same art style, same camera angle..."
- **Pitfall:** The xAI model makes images look "too real" — Vanito will reject this style for character animation
- Duration: 5-12 seconds per clip
- Cost: ~$0.26-0.63 per clip

**Path B — ffmpeg Overlay Effects**
- Best for: keeping the poster/reference image EXACTLY as-is while adding reactive effects
- Generate frame-by-frame with Python/PIL
- Keep the base image unchanged
- Add overlay layers that pulse/intensify with the music:
  - Red spotlights sweeping (left/right beams)
  - Moon glow pulsing
  - Floating ember/particle effects
  - Border glow that intensifies
  - Corner light blooms
- Encode at 24fps, scale to even dimensions (1280x720) for libx264 compatibility

### Step 6: Show User Before Saving to Hub

**CRITICAL — Show the raw video URL to the user FIRST, let them approve, THEN save to hub.**

The user will call you out if you save to hub before showing them the result. They want to see what they paid for before it gets committed. Pattern:

1. Get the video URL from the generation result
2. **Send the URL to the user immediately** — let them watch it
3. Wait for their feedback (approve, reject, or request changes)
4. Only after approval: download, save to hub, commit + push

**Do NOT** download, save, commit, or push the video before the user has seen and approved it. This applies to ALL paid generations (images, videos, audio) — not just Seedance clips.

### Step 7: Sound Design Pipeline (Confirmed 2026-07-24)

For cinematic short films, layer custom sound effects on top of the Seedance video using ElevenLabs sound effects + ffmpeg.

**Generate cinematic sound effects:**
```python
mcp__blockrun__blockrun_speech(
    action="sound_effect",
    input="Heavy pouring rain on a city rooftop, steady downpour, distant thunder rumbles, dark storm atmosphere",
    duration_seconds=10
)
```
- Cost: ~$0.05/sound effect, up to 22 seconds per effect
- Models: elevenlabs/sound-effects (default)
- Sound effects host URLs may expire — download immediately with curl

**Layering audio with ffmpeg:**
```bash
# Step 1: Mix multiple sound effects with delays and volume
ffmpeg -y -i ambience.mp3 -i impact.mp3 \
  -filter_complex \
  "[0:a]volume=0.6[A];[1:a]adelay=2000|2000,volume=1.5[B];[A][B]amix=inputs=2:duration=first" \
  audio-mix.mp3

# Step 2: Combine mixed audio with silent video
ffmpeg -y -i scene.mp4 -i audio-mix.mp3 \
  -c:v copy -c:a aac -b:a 192k -shortest final-scene.mp4
```
- `adelay=2000|2000` = delay start by 2 seconds (both channels)
- `volume=0.6` = background ambience at 60%
- `volume=1.5` = impact at 150% (punchier)

### Step 8: Image-to-Image Detail Fixes (Confirmed 2026-07-24)

When an image needs specific additions (tattoos, emblems, accessories) without regenerating the whole scene:

```python
mcp__blockrun__blockrun_image(
    action="edit",
    image="https://blockrun.ai/api/media/media/images/...",  # NOTE: use 'image' param, NOT 'image_url'
    model="openai/gpt-image-2",
    prompt="""Add [specific detail]. Keep everything else exactly the same — same face, same hair, same coat, same background, same lighting, same pose."""
)
```

**Critical rules:**
- Use `image` parameter for edit action, NOT `image_url` — `image_url` returns "image parameter required for edit action" error
- Model: openai/gpt-image-2 ($0.065/image) — it has the best preservation of original composition
- Apply ALL fixes in ONE edit pass — do NOT cascade edits (each pass reinterprets everything)
- Pre-verify with vision_analyze before showing Vanito
- Cost per edit: ~$0.065

### Step 9: Character Sheet Generation (Confirmed 2026-08-08)

Inspired by @Mayz1169 on X: create a multi-view character sheet, then use it as Seedance's visual anchor for consistent character across all animation scenes.

**🔴 Model: Use GPT Image 2 for character sheets.** Vanito's explicit directive (2026-08-08): *"I want you to use gpt image 2 only."* For character reference sheets/bibles with text labels, turnarounds, detail panels, and color palettes, use `openai/gpt-image-2` via `clawrouter_image_generate`. GPT handles typography and structured layout better than Seedream. Seedream 5.0 Pro remains preferred for standalone character portraits without text.

**Tool:** `clawrouter_image_generate` with `model: "openai/gpt-image-2"` (not listed in tool description, but it works). Sizes: 1024x1024, 1536x1024, 1024x1536. Cost: ~$0.065-0.13/image.

**Prompt structure for GPT Image 2 character sheet:**
```
[CHARACTER NAME], [genre/description].
Layout: clean reference sheet format with LEFT/CENTER/RIGHT sections.
LEFT: Large name text + one dynamic hero shot.
CENTER: Turnaround views (Front/Side/Back) + equipment detail.
RIGHT: Detail close-ups + color palette + tagline.
Clean white background, gothic visual kei digital painting, NOT cartoon NOT photorealistic, print ready.
```

**External prompt adaptation pattern** (see `references/external-prompt-adaptation.md`): When adapting a template character sheet prompt from another source (e.g., @TechieBySA), substitute: character name, equipment, color palette, style keywords, and tagline — keep the layout structure intact.

**Save and push:**
```
git add music/vanito/kage-character-sheet.png
git commit -m "Vanito: KAGE official character sheet - [details]"
git pull --rebase origin main
git push origin main
```

**Use as Seedance seed:** Feed the GitHub raw URL or BlockRun CDN URL as the Seedance seed image to anchor character consistency across all animation clips.
- **Default:** Seedance 2.0 generates synced audio automatically when `generate_audio: true`. This works well for standalone clips.
- **Custom audio overlay (confirmed working 2026-07-17):** When Vanito provides his own song track to sync with the animation:
  ```bash
  ffmpeg -y -i animation.mp4 -i song.mp3 -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest output.mp4
  ```
  - `-map 0:v:0` = take video from the animation
  - `-map 1:a:0` = take audio from the song
  - `-shortest` = match duration to the shortest input (usually the 10s video)
  - This replaces the Seedance-generated audio entirely with the user's track
- For extracting a specific section of a longer song: `ffmpeg -ss <seconds> -t <duration> -i song.mp3 output.mp3`

### Step 5: Assembly — Multi-Clip Concat
For multi-shot sequences (walk on → perform, entrance → stage, etc.):
1. Download all Seedance clips locally
2. Rescale each to the SAME resolution (e.g., `-vf "scale=1112:834"` for Seedance native size)
3. Create a concat file: `echo "file '/tmp/clip1.mp4'" > concat.txt`, one entry per clip
4. Extract the correct song section with ffmpeg
5. Stitch: `ffmpeg -f concat -safe 0 -i concat.txt -i song.mp3 -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest -movflags +faststart output.mp4`
- The `-shortest` flag ensures video length matches the shortest input (usually the audio)
- `-movflags +faststart` enables web streaming (required for Telegram)

### Step 6: GIF Output

See `references/poster-to-gif-pipeline.md` for the full poster-to-animated-GIF workflow with exact commands, parameters, and pricing from the observed Jul 14 session.

Quick reference:
- Convert MP4 -> GIF: `ffmpeg -i input.mp4 -vf "fps=10,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=256[p];[s1][p]paletteuse" -loop 0 output.gif`
- Use 8fps for balanced quality/size; 10fps for smoother playback
- 5-second clip at 10fps ~7.6MB
- GIFs play inline on Telegram; audio-only clips need MP4

### Step 7: Telegram-Friendly Delivery
- **GIF** → send via `MEDIA:/path/to/file.gif` — plays inline, no download
- **MP4 with audio** → push to hub → share raw.githubusercontent.com URL — Telegram plays it inline if small enough (< 20MB)
- Always use `-movflags +faststart` when encoding MP4s destined for Telegram/web
- Check file size before sending: GIFs > 15MB may not send on mobile data

## Tools Reference

| Tool | Purpose | Cost |
|------|---------|------|
| **bytedance/seedream-5-pro** | 🎨 **PREFERRED IMAGE MODEL** (Vanito: "I don't want GPT, I want C-dream") | ~$0.018-0.021/image |
| **bytedance/seedance-2.0** | Animate poster images with exact style preservation | ~$2.55/8s, ~$3.19/10s, ~$1.60/5s |
| **bytedance/seedance-2.0-fast** | Faster variant, slightly cheaper. Poster->GIF pipeline in references/poster-to-gif-pipeline.md | ~$2.38/10s text, ~$1.40/10s img2v, **~$1.28/5s img2v (observed)** |
| **xAI grok-imagine-video** | Quick previews, background-only shots | ~$0.26-0.79/clip |
| openai/gpt-image-2 | Generate new scene images · **Character transformation (edit mode):** transform characters in existing artwork to match KAGE/HIKARI designs while preserving composition, text, and setting | ~$0.06–0.12/image |
| ffmpeg + Python/PIL | Frame-by-frame overlay effects (fallback only) | Free |
| Wav2Lip | Lip-sync HIKARI's mouth to vocals | Free (open-source) |
| Kdenlive | Full video editing (transitions, FX) | Free |
| ComfyUI + IP-Adapter | Character-consistent image gen (GPU req.) | Free (needs GPU VPS ~$30/mo) |

## 🔴 CRITICAL: Pre-Flight Cost Confirmation Protocol (2026-07-13)

Vanito explicitly requires this BEFORE every paid generation. This is his #1 frustration point.

**THE RULE:** Never run a paid generation without FIRST telling Vanito:
1. **What** the generation is
2. **How much it costs (as an estimate, never a flat number)**
3. **The current balance**
4. **Ask for explicit OK** before proceeding

**CRITICAL: Always quote costs as ESTIMATES, not fixed prices.**
Tool description rates are base prices — upstream providers set the final settlement amount, and actual charges can be 50-75% higher than listed. Vanito will call you out if you say "$1.83" and the charge comes through at $3.19. Use "~$X" or "estimated ~$X-$X" language every time.

**Example format:**
```
Clip: 10 seconds KAGE animation (Seedance 2.0)
Estimate: ~$2-3 (upstream sets final price)
Balance: $7.28
Your call — run it?
```

**Why this matters:** Seedance 2.0 is the most expensive tool ($1.60-$3.19/clip estimated). Running multiple clips without per-clip confirmation adds up fast. Vanito tracks the ~$38 initial wallet funding and will notice if spending doesn't add up.

### Cost Tracking — Track Every Dollar (2026-07-20)

Vanito noticed a ~$9 discrepancy between expected balance and actual balance. This erodes trust. To prevent this:

**Before each session:**
- Check wallet balance with `blockrun_wallet(action=status)` and note the starting balance

**After each paid operation:**
- Record the exact cost from the tool result
- Subtract from running total
- Report the new balance to the user

**End of session:**
- If the user asks about spending, provide a full itemized list with:
  - What was generated
  - Exact cost
  - Running balance after each item
  - Total spent vs total deposited

**If the balance doesn't add up:**
- Check the on-chain balance directly via `blockrun_rpc(network="base", method="eth_call", params=[{"data": "0x70a08231000000000000000000000000<wallet_address>", "to": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"}, "latest"])` to verify the wallet's USDC balance independently
- Be honest about what you can and can't account for
- Do NOT fabricate charges or guess — say "I can't fully account for $X" if that's the case

**Pitfall:** The wallet status tool may show a different balance than expected due to unconfirmed transactions, gas fees, or charges that settled after the tool reported. Always verify on-chain when the user questions the balance.

**CRITICAL: Track total spend via BlockRun wallet report, not just individual tool costs.**
Individual tool costs (image gen $0.07, video gen $2.55, etc.) are BASE costs only. The actual total spend includes x402 settlement fees, gateway overhead, and transaction costs that the tool doesn't report. To get the REAL total:
- Run `blockrun_wallet(action="report")` — this shows total spent across ALL calls
- Compare this against your manual sum of individual tool costs
- The difference is hidden fees (observed: ~$9 gap on $14.70 deposit, where individual costs summed to ~$4.78 but actual spend was $14.42)
- Report the wallet report total to the user, not your manual sum
- If the user questions a discrepancy, show them the wallet report as the source of truth

**Pitfall:** The wallet status tool may show a different balance than expected due to unconfirmed transactions, gas fees, or charges that settled after the tool reported. Always verify on-chain when the user questions the balance. Use `blockrun_rpc(network="base", method="eth_call", params=[{"data": "0x70a08231000000000000000000000000<wallet_address>", "to": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"}, "latest"])` to read the USDC balance directly from the contract — this is the definitive number.

## Vanito's Song Identity Reference

**In the Darkness We Rise** (in-the-darkness-we-rise.mp3) = KAGE's original song, also referred to as "Yami no Naka De." Already recorded on the **Kakego album** (spelled K-A-K-E-G-O, not "Cock-a-Go"). Cover art at `kage-yami-no-naka-de.png`.

**Existing discography** (on Vanito's hub):
1. In the Darkness We Rise — KAGE's origin track
2. Kono Sora no Shita — Their duet (how they met)
3. Mamoritai — HIKARI solo
4. Blood Moon — KAGE performance
5. Fight Forever Never Quit — Band anthem
6. Mirai e Hashire — Hopeful
7. Rising Sun — Duet
8. Extinction Protocol / Gravity's Kiss — Side tracks
9. **I Heard Your Voice / Kimi no Koe** — The scream that crossed the darkness. KAGE hears HIKARI's voice, finds her lyrics, writes a melody back. Cover art: hunched KAGE under spotlight, HIKARI in doorway. [Added 2026-07-15]
10. **Where the Moon Feels Warm / 月が温かい場所** — Rooftop duet. KAGE's moon confession, HIKARI's warmth. Lyrics written, awaiting recording. [Concept added 2026-07-15]

**Song creation workflow:** New song concepts come from story gaps in the KAGEKŌ narrative (rooftop moments, first meetings, arguments, shared studio). Vanito picks a direction → I write lyrics → format with Donna AI tags `[MALE]/[FEMALE]/[DUET][SECTION]` plus parenthetical tone cues → add `[SCREAM]` tag for KAGE's aggressive sections → Vanito records or sends the audio → I push to hub with cover art, story section, discography updates, and lyrics file. Never skip the concept step — Vanito decides which story gap to fill next.

## Donna App Limitation (Observed 2026-07-20)
Vanito tested the Donna app for music video generation. Key limitation: **Donna only generates ONE character per video.** It cannot do duets or switch between characters mid-song. When Vanito fed it the GENTECH song (which has both KAGE and HIKARI parts), Donna generated only HIKARI singing the entire track — including KAGE's spoken and screamed sections. The result was a 50-second video of HIKARI alone, with no KAGE visible in any frame.

**What this means for our workflow:**
- Seedance 2.0 with RealFace is the only viable path for multi-character scenes (GenTech at terminal + KAGÉ portrait + cat)
- Donna is useful for solo character videos only
- If Vanito asks about Donna for a duet song, warn him upfront: "Donna only does one character — HIKARI will sing everything including KAGE's parts"

## Complex Multi-Element Prompt Pattern (Observed 2026-07-20)
For scenes with multiple simultaneous actions (GenTech at terminal + cat + environment + text readability), use this prompt structure:

```
The whole room has a gentle windy atmosphere.
[Element 1 - character action]: [specific motion]
[Element 2 - secondary character/prop]: [specific motion]
[Element 3 - environment]: [specific motion]
[Element 4 - UI/text]: [readability requirement]
[Element 5 - tertiary detail]: [specific motion]
Slow cinematic motion, everything feels alive.
```

**Confirmed working example (GENTECH cover, 10s Seedance 2.0-fast):**
```
The whole room has a gentle windy atmosphere.
GenTech (seen from behind in the GENTECH hoodie) bobs his head to music while typing on the keyboard.
The computer monitors show code scrolling and the GENTECH logo spinning.
The city skyline outside the window has moving lights and life.
The JORDAN JORDAN title at the top is clear and readable.
The Japanese text at the bottom is visible.
Papers on the desk flutter in the wind.
The tuxedo cat (black with white chest bib, white paws, long white whiskers, triangular black ears) sitting on the desk facing the viewer blinks and its fur ruffles in the wind.
Slow cinematic motion, everything feels alive.
```

**Key principles:**
- Start with the overall atmosphere ("windy room")
- List each element as its own sentence
- Include readability requirements for text elements explicitly
- End with a mood cap ("Slow cinematic motion, everything feels alive")
- For characters seen from behind, specify "seen from behind" to prevent the model from rotating the view

## Song Storyboard / Ballad Mode — Before → Main → After + Transitions

For full-song storyboards (4:29 ballads like Sakura no Chikai), use this extended frame pattern:

### The 3-Frame Per Scene Pattern
Each major scene section gets **three frames** — not one:
- **BEFORE** — The moment leading into the scene (e.g. outside the house, looking at the photo, tears forming)
- **MAIN** — The scene itself (the emotional beat)
- **AFTER** — The moment after (petal on photo, peaceful smile, empty room)

### Transition Flow Frames
Between every scene section, add a **transition/flow frame** — a small in-between shot that creates smooth visual rhythm:
- **T1** — Finger hovering above the first guitar string (before intro)
- **T2** — Doorway glow growing brighter (before chorus)
- **T3** — Petal landing on framed photo (pause)
- **T4** — Hand gripping guitar neck (determination)
- **T5** — Light swelling, silhouettes emerging (flashback trigger)
- **T6** — Petal across camera lens, memory dissolving (return from flashback)
- **T7** — First sunlight on floor (hope breaking through)

### Production Cards
- **Opening:** "GEN TECH LABS presents" on dark textured background with cherry blossom petal
- **Closing:** "A film by Vanito" + song title + "© 2026 GenTech Labs"

### Young HIKARI Character Consistency (CRITICAL)
When young HIKARI (age 8) appears in any frame:
- **Hair:** Solid BLACK hair in TWO PIGTAILS with red hair ties — absolutely NO red tips
- **Shirt:** White t-shirt with black kanji 光 (Hikari = "Light")
- **Papa Tanaka:** Early 40s, salt-and-pepper hair, kind eyes, white ramen shop apron
- **Memory containment:** Silhouettes of Papa + young HIKARI in the golden doorway must stay FULLY INSIDE the door frame — the door frame is the hard boundary between memory and reality. No part of their silhouettes (hair, pigtails, arms, clothing) may extend past the door frame edge into the dark room.

### Per-Scene Approval Workflow (Vanito's Rule)
Do NOT generate all Seedance clips at once. Generate ONE clip, show it to Vanito, get approval or fix instructions, then move to the next. This prevents burning budget on mass failures.

### Cloudflare Cache-Busting
When replacing a file on the VPS: `?v=2` cache-busting on URLs works for browsers but Cloudflare edge still serves its cached 404 for the old filename. **Fix:** Save the new file with a completely new filename (e.g., `s3-bridge-v2.png` instead of overwriting `sakura-scene3-bridge.png`) and update the HTML. Fresh filename = fresh Cloudflare fetch.

### VPS Permissions Trap
Every file written to the VPS (via write_file or scp as root) defaults to `600` permissions (root-only), causing HTTP 403/404. Always run after every deployment:
```bash
ssh root@2.24.195.196 "chmod 644 /var/www/gentechlabs/*.html /var/www/gentechlabs/characters/*.png /var/www/gentechlabs/videos/*.mp4"
```

### Hair Color Turns Purple Under Cool Lighting
When generating HIKARI scenes with cool blue/rainy window lighting, the red hair tips can appear purple. Fix: explicitly state "deep crimson red tips, NOT purple, warm crimson, not cool-toned" in prompts and add a warm fill light source. Always verify via vision_analyze before showing the user.

## Pitfalls

### CRITICAL: Ask for Vanito's reference image before generating character images
Do not guess from memory or from vault descriptions. KAGE's design has changed multiple times (currently on Look 3 as of 2026-07-17, with Look 4 as an alt). Generating from text description alone produces the wrong character and wastes money. Pattern: say "Send me your reference pic so I get the look right" then generate from that image.

### Cost Estimation: Always say "estimate" never a flat number
When quoting generation costs, use "~$X" or "estimated ~$X-$X" — never "$1.83" as a flat price. Tool description rates are base prices; upstream providers set the final settlement. Actual charges can be 50-75% higher than listed rates. Vanito explicitly called this out (2026-07-17): quoted $1.83, charged $3.19. He said "Next time say an estimate not how much it will cost."

### VPS file permissions: scp as root = `600`, nginx needs `644`
Files uploaded to `/var/www/gentechlabs/` via `scp` as `root` default to `-rw-------` (600). Nginx cannot serve them — user sees 403/404. Always run `chmod 644 path/to/file` after every upload, or batch-fix after a session: `ssh host "chmod 644 /var/www/gentechlabs/characters/*.png /var/www/gentechlabs/*.html"`

### Cloudflare caches stale 404s — use new filenames, not `?v=2`
When replacing a file on the VPS: `?v=2` cache-busting on URLs works for the browser but Cloudflare edge still serves its cached 404 for the old filename. The fix is to save the new file with a **completely new filename** (e.g., `s3-bridge-v2.png` instead of overwriting `sakura-scene3-bridge.png`) and update the HTML. Fresh filename = fresh Cloudflare fetch.

### Hair color turns purple under cool lighting
When generating HIKARI scenes with cool blue/rainy window lighting, the red hair tips can appear purple. Fix: explicitly state "deep crimson red tips, NOT purple, warm crimson, not cool-toned" in prompts and add a warm fill light source. Always verify via vision_analyze before showing the user.

### If Vanito says stop, stop immediately
When he says things like "Stop making pictures please lol", he means it. Do not continue iterating. Accept the feedback, reset to what he has told you, and move forward. This applies to all creative work. One more iteration after stop erodes trust.

### Seedance frame_images API Error (Observed 2026-07-12/13)
Seedance 2.0 and 2.0-fast may return: `"Unsupported video generation parameter(s) for model seedance-2.0: frame_images"`. This is a **server-side infrastructure error**, not an input issue.

**Behavior observed:**
### Step 6: Show User Before Saving to Hub

**CRITICAL — Show the raw video URL to the user FIRST, let them approve, THEN save to hub.**

The user will call you out if you save to hub before showing them the result. They want to see what they paid for before it gets committed. Pattern:

1. Get the video URL from the generation result
2. **Send the URL to the user immediately** — let them watch it
3. Wait for their feedback (approve, reject, or request changes)
4. Only after approval: download, save to hub, commit + push

**Do NOT** download, save, commit, or push the video before the user has seen and approved it. This applies to ALL paid generations (images, videos, audio) — not just Seedance clips.

### Seedance Real Person Detected Rejection (Observed 2026-07-20)
Seedance 2.0 and 2.0-fast reject image-to-video when the seed image may contain a real human face. This fires on semi-realistic digital paintings and high-quality AI art, not just photographs.

**Error message:**
Input image rejected: real person detected
ByteDance Seedance rejects image-to-video when the seed image may contain a real human face.

**What triggers it:**
- Semi-realistic digital paintings (gothic visual kei style, high-detail character art)
- Images with realistic skin texture, lighting, or facial detail
- NOT triggered by: anime/cartoon style, abstract art, or low-detail illustrations

**Workaround A - RealFace Virtual Portrait Enrollment (PREFERRED - preserves character look):**
Enroll the image as a Virtual Portrait via blockrun_realface action=portrait, then pass real_face_asset_id to Seedance instead of image_url. This bypasses the real-person filter while keeping Seedance style preservation.

**Flow:**
1. blockrun_realface(action=portrait, name=descriptive name, image_url=BlockRun-hosted URL) - $0.01
2. Use the returned ta_xxxx asset ID in Seedance: blockrun_video(model=bytedance/seedance-2.0-fast, real_face_asset_id=ta_xxxx, ...)
3. The Virtual Portrait enrollment is one-time - the asset ID can be reused for future animations of the same image

**Limitations:**
- The RealFace asset may take a few minutes to propagate - if you get "Invalid or unauthorized asset references" error, wait 30-60s and retry
- Only works with Seedance 2.0 and 2.0-fast models (not xAI or Sora)
- The portrait enrollment is for AI-generated/non-human characters only - real people need the full liveness flow (init to status to enroll)

**Workaround B - xAI grok-imagine-video (fallback - changes character appearance):**
When Seedance rejects an image AND RealFace enrollment fails, switch to xai/grok-imagine-video. It has NO real-person filter and accepts the same image without issue. Cost: ~$0.53/10s.

**CRITICAL WARNING - xAI changes character appearance:**
xAI grok-imagine-video adds photorealistic/shimmer texture to digital painted art. Characters faces, clothes, and style WILL drift from the source image. Vanito explicitly rejected xAI output for character scenes (2026-07-20): "You just sent me literally changed the characters and I am disappointed." Only use xAI when:
- The user explicitly approves using a different model
- The scene has no character faces (background-only, abstract)
- You have warned the user upfront that characters will change

**Important:** Do NOT tell the user the wallet is out of funds when this error fires. The error message can misleadingly say "Video generation needs USDC — your wallet is out of funds" even when the wallet has $10+. The real cause is the content filter. Always check the full error body for `INPUT_IMAGE_REAL_PERSON` before reporting a balance issue.

**Confirmed working flow (2026-07-20):**
1. Generate the image with openai/gpt-image-2 (semi-realistic style)
2. Enroll as Virtual Portrait: blockrun_realface(action=portrait, name="...", image_url=BlockRun URL) — $0.01
3. Run Seedance with real_face_asset_id — this preserves the exact character look
4. If the asset returns "Invalid or unauthorized asset references" (500 error), retry after 30-60s
5. If wallet shows low balance but you know there's funds, check the error body for INPUT_IMAGE_REAL_PERSON — the balance error is misleading

### Image URL Format for Video Generation (Observed 2026-07-20)
Video generation tools require a publicly accessible URL for the seed image. Not all URL formats work:

| URL Format | Works? | Notes |
|------------|--------|-------|
| `https://blockrun.ai/api/media/media/images/...` | ✅ Yes | Most reliable — BlockRun-hosted images from previous generations |
| `https://raw.githubusercontent.com/...` | ⚠️ Sometimes | Can return 404 if GitHub CDN hasn't propagated, or if file format doesn't match extension |
| Local file path (`/root/...`) | ❌ No | Tool rejects with "Invalid URL" |
| `data:image/png;base64,...` | ❌ No | Too long, tool rejects |

**Best practice:** Use BlockRun-hosted URLs from previous image generations. If the image was just pushed to GitHub, wait 30-60s for CDN propagation, or use the BlockRun URL instead.

### Never assume next song concept — always check existing discography first
When asked "what song should I work on next," reference the existing discography above. The user may already have recorded the song you're about to suggest.

### Do NOT cascade img edits — each fix drifts the image
When fixing images via gpt-image-2 edit mode, every additional pass reinterprets ALL elements, not just the target. Characters' hair colors shift, outfit details change, and composition drifts. Observed problem pattern (2026-07-15): three guitar fixes caused HIKARI's hair to change from black-with-red-highlights to solid red. Vanito's original observation that the guitar "probably don't need to be fixed" should have been respected. Solution: If Vanito says something "probably doesn't need fixing," trust his judgment. If multiple fixes are genuinely needed, go back to the user's original approved version and apply all fixes in ONE edit with extremely detailed "do NOT change X, Y, Z" constraints.

### Edit from the original image, not from a previous edit
When Vanito requests a new version that combines elements from two images (e.g., "keep the pose of image A but the clothes of image B"), always use the ORIGINAL source image (image A) as the base for the edit — never an already-edited version. Edits accumulate drift: every generation reinterprets the entire scene. Starting fresh from the original preserves the composition, text, and layout that Vanito already approved. Confirmed 2026-07-17: editing the original Blood on the Strings cover (not the back-turned edit) produced a much cleaner result.

### Character Transformation-Specific Pitfalls
3. **Camera perspective is critical** — for stage/concert shots from behind, explicitly say "Same camera angle behind them the whole time. They never turn around." The model WILL rotate the view if you don't lock it
4. **Hub push rejection:** Always pull --rebase before pushing:
   ```bash
   cd /root/vaults/gentech/github/ProtoJay4789.github.io
   git pull --rebase origin main  # CRITICAL: do this before EVERY push
   git push origin main
   ```
4. The hub repo path is nested under the vault: `github/ProtoJay4789.github.io/` — the files end up at `music/vanito/scenes/<file>` on the hub, but the raw URL path includes the vault nesting: `.../main/github/ProtoJay4789.github.io/music/vanito/scenes/<file>`
5. Always verify files pushed correctly by checking the raw URL returns HTTP 200
6. **Poster dimensions issue:** The poster is 1288x853 which is ODD height. libx264 requires even dimensions. Always scale/pad to 1280x720 before encoding with h264

7. **Hub push via fresh clone when local repo is tangled:** The hub repo is nested inside the vault directory (`/root/vaults/gentech/github/ProtoJay4789.github.io/`), which causes the working tree to always show vault changes as uncommitted modifications. This blocks clean pulls/pushes. When this happens, do a fresh shallow clone instead:

   ```bash
   rm -rf /tmp/hub-push
   git clone https://github.com/ProtoJay4789/ProtoJay4789.github.io.git /tmp/hub-push --depth 1
   # Copy files into /tmp/hub-push/
   cd /tmp/hub-push
   git add -f <files>
   git commit -m "🎵 <description>"
   git push origin main
   ```

   This avoids all the vault-related working-tree conflicts entirely. Always verify with `curl` that raw.githubusercontent.com returns HTTP 200 after pushing.

### Character Transformation-Specific Pitfalls

8. **KAGE vs HIKARI vocal roles in static imagery**: KAGE is the screamer (raw, anguished, powerful). HIKARI is the melodic vocalist. In cover art / promotional images, KAGE gets the screaming poses (arms raised, head back, intense expression). HIKARI gets emotive/singing poses. Swapping these will be caught by Vanito — always verify who is in what role before generating.

9. **Guitar model varies per song**: The default spec says Dean ML / Flying V, but the confirmed Yami no Naka De guitar is a **gloss black Les Paul double-cutaway** with red blood splatters. Always check which song's reference art the image belongs to before specifying the guitar in prompts. When in doubt, ask Vanito.

10. **Objects in shadow must not draw focus**: The spotlight is the scene's light source. Background props (guitar in corner, furniture, decor) that sit in shadow should be dark and subtle. Over-lighting them or making them too detailed pulls the eye from the main subject. Verify with vision_analyze before delivery.

11. **Check for unnatural borders/artifacts on foreground objects**: The model occasionally creates hard edge lines, glow borders, or chain artifacts around foreground objects (papers, notebooks, props). These make them look stickered on. Always check foreground elements blend naturally with soft shadows and no visible cutout lines. If spotted, re-edit with explicit "remove any visible border, chain line, or unnatural edge" instructions.

12. **Do NOT cascade edits — each fix drifts the image**: When gpt-image-2 edits an image, every additional pass reinterpretes ALL elements, not just the target. Characters' hair colors shift, outfit details change, and composition drifts. Observed problem pattern (2026-07-15): three guitar fixes caused HIKARI's hair to change from black-with-red-highlights to solid red. Vanito's original observation that the guitar "probably don't need to be fixed" should have been respected. **Solution:** If Vanito says something "probably doesn't need fixing," trust his judgment and leave it. If multiple fixes are genuinely needed, go back to the user's original approved version and apply all fixes in ONE edit with extremely detailed "do NOT change X, Y, Z" constraints, then verify with vision_analyze before delivering.

## Related Skills & References

**Supporting references in this skill:**
- `references/vanito-character-specs.md` — All KAGE/HIKARI looks and hub assets
- `references/blockrun-mcp-model-patching.md` — Adding new image models to the BlockRun MCP server when the tool schema hasn't caught up
- `references/character-transformation-prompts.md` — Detailed prompt patterns for character edits
- `references/multi-scene-film-production.md` — Multi-chapter film production: scene templates (intro/combat), sound design timings, concat commands, and cost breakdowns for 15s chapters
