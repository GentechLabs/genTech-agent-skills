# Vanito's KAGEKŌ Session 2 — 2026-07-09

## Overview
Continued building Vanito's Artists tab on `hub-vanito.html`. Added animated profiles, rain effects, narrative story sections, scene generation/animation, and song swaps. Extensive use of BlockRun video generation and canvas-based effects.

---

## New Patterns

### 1. Character Profile Picture Animation
Static character images → looping 5s video for profile pics:

```bash
blockrun_video action=create model=xai/grok-imagine-video \
  image_url=<character_png_url> \
  prompt="Portrait of character, slow subtle motion, hair sways, light pulses gently..."
  duration_seconds=5
# Cost: ~$0.26 per character
```

**In HTML:** Replace `<img>` with `<video autoplay loop muted playsinline poster="original.png">`
**Size:** Vanito wanted 140×140 instead of 100×100 (hard to see at small size)
**Poster fallback:** Always include `poster` attribute so static image shows if video fails

### 2. Canvas Rain Effect (not CSS)
Full JavaScript canvas rain with splashes for realistic water effect:

- 150 raindrops with varying speed, opacity, thickness, wind
- Splash particles when drops hit bottom of screen
- Runs on `requestAnimationFrame` loop
- Canvas positioned `fixed` with `pointer-events:none` over the entire page
- Water sheen overlay on cards via CSS `::after` with gradient

**Cost:** Free (all client-side) — about 200 lines of JS
**Files:** Canvas element in HTML, CSS for overlay, JS engine
**Performance:** 150 drops + splashes runs smooth on mobile

### 3. xAI Grok Video as Seedance Fallback
When Seedance rejects images with "real person detected" error, fall back to xAI Grok:

```javascript
// ✅ THIS WORKS — xAI Grok accepts AI-generated character images
model: "xai/grok-imagine-video"  // $0.05/sec, cheaper than Seedance

// ❌ THIS FAILS — Seedance rejects some AI faces
model: "bytedance/seedance-2.0-fast"  // Returns INPUT_IMAGE_REAL_PERSON error
```

**Cost comparison:** xAI Grok ~$0.26/5s clip vs Seedance 2.0 Fast ~$1.27/5s clip

### 4. Video in Story Sections
Inline looping video within narrative text:

```html
<strong>Epilogue</strong><br>
<video src="..." autoplay loop muted playsinline 
  style="width:100%; border-radius:8px; margin-bottom:8px;">
</video>
The text continues right after the video...
```

### 5. Raw GitHub URLs for Video Delivery
GitHub Pages has a 30-60s deploy delay. Use raw.githubusercontent.com URLs:

```html
<!-- ✅ Instant delivery (raw CDN, no delay) -->
<video src="https://raw.githubusercontent.com/ProtoJay4789/ProtoJay4789.github.io/main/music/vanito/file.mp4">

<!-- ❌ Delayed (GitHub Pages build) -->
<video src="music/vanito/file.mp4">
```

### 6. Gitignore Exception Ordering
**CRITICAL RULE:** Exception MUST come AFTER the blanket deny:

```gitignore
# ❌ BROKEN — exception is overridden by later deny
!music/vanito/*.mp4   # ignored!
**/*.mp4               # overrides the ! exception

# ✅ CORRECT — deny first, then allow
**/*.mp4
!music/vanito/*.mp4   # works!
```

### 7. MEDIA: Prefix for Telegram Inline Display
When sending images/videos to Telegram, embed them inline using MEDIA prefix:

```
MEDIA:/path/to/local/file.png
```

This renders the media directly in chat instead of showing a blue hyperlink.

### 8. Full Narrative Story Writing
Multi-part character backstory for the hub:

```
Part I — The Boy Who Screamed at the Moon (KAGE origin)
Part II — The Girl Who Sang to the Stars (HIKARI origin)  
Part III — KAGEKŌ (how they met)
Epilogue (the rooftop scene, "Now it feels warm")
```

Save to vault: `/root/vaults/gentech/Travels/music/kageko-story.txt`
Embed in hub as styled card with `<div class="char-bio">` and inline `<video>` for epilogue

### 9. User-Sung Audio Workflow
1. Vanito sends MP3 via Telegram
2. Save to `music/vanito/<kebab-name>.mp3`
3. Update player `src` in `hub-vanito.html`
4. Transcribe with Whisper
5. Save lyrics to vault: `Travels/music/vanito-<song>.txt`
6. Update data JSON if needed
7. Push to GitHub

### 10. Theme Preferences (Vanito)
- **No orange/gold** — replaced with dark red (`#8a1a1a`, `#cc2222`, `#4a0a0a`)
- **No "Wyvern" subtitle** — header should just say "Vanito's Hub"
- **Header gradient** — black → dark red (was gold → orange)
- **No glowing halos** around characters in generated images
- **Preview before save** — always show generated media first, wait for explicit approval

---

## Key Tool Costs (per operation)

| Operation | Tool | Cost |
|-----------|------|------|
| Animated 5s clip | xAI Grok | ~$0.26 |
| Animated 5s clip | Seedance 2.0 Fast | ~$1.27 |
| Image generation | FLUX 2 (FAL) | ~$0.04 |
| Image generation | GPT-Image-2 | ~$0.12 |
| Audio transcription | Whisper (local) | Free |
| Canvas rain effect | Custom JS | Free |
| Image edit (text removal) | GPT-Image-2 | ~$0.12 |
| Wav2Lip lip-sync | Not yet operational | ~$0 (need model download) |

---

## Lightning Effects CSS
Pulse glow on banner, border glow on cards, light sweep on album card, text pulse on titles, floating ember particles. All in `<style>` under `/* ═══ CHARACTERS LIGHTING EFFECTS ═══ */`.

**Important:** These CSS rules target `img` selectors — if elements change to `<video>`, update selectors:

```css
/* Update from: */
#tab-characters > img:first-child { }
.card-together img { }

/* To: */
#tab-characters > img:first-child,
#tab-characters > video:first-child { }
.card-together img,
.card-together video { }
```

---

## Forge Handoff Format
Tasks delegated to Forge go in:

```
01-HANDOFFS/gentech-to-forge/<date>-<topic>.md
```

Format: Task description, desired effect, constraints, files involved, design references.
