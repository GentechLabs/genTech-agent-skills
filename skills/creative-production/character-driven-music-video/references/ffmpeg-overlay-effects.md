# ffmpeg Overlay Effects — Keep Image Intact, Add Visuals

## When to Use
When the xAI video model makes the image look "too real" or drifts the art style. This technique keeps the reference image **100% unchanged** and adds animated overlay effects on top.

## CRITICAL: Make Effects VISIBLE (The #1 Mistake)
**The effects must be 3-5x stronger than you think necessary.** The user's poster/art already has atmospheric lighting built in — subtle overlays get completely lost. If the user says "I don't see the effects," your alpha values are way too low.

### Effective Alpha Ranges (visible on dark concert art):
| Layer | Alpha that actually shows | What too-subtle looks like |
|-------|--------------------------|---------------------------|
| Moon glow | 40-80 (not 12-15) | Invisible against existing moon |
| Spotlights | 80-120 (not 25-30) | "I barely notice the sweep" |
| Particles | 160-220 (not 150) | "I don't see the effects" |
| Crowd glow | 40-80 (not 12-15) | Lost in existing crowd lighting |
| Strobe/flash | 80-120 at peak | Nothing happens at climax |
| Border glow | 40-80 at corners | "Is it supposed to pulse?" |

### Verify with vision_analyze
After generating frames, check a BEFORE vs AFTER frame:
```
vision_analyze(image_url="frame_0000.png", question="Do you see any visual effects like glow, particles, pulsing lights?")
vision_analyze(image_url="frame_0200.png", question="Do you see any visual effects like glow, particles, pulsing lights?")
```
If both frames look the same to the AI, the effects are too subtle. REDO with 3x higher alpha values.

## How It Works
1. Render each frame of the video in Python using PIL (Pillow)
2. Composite the base image + animated overlay layers per frame
3. Encode the frames into an MP4 with libx264
4. Add audio with ffmpeg

## Python Frame Generator Pattern (BOLD Effects)

```python
from PIL import Image, ImageDraw
import math

W, H = 1280, 720  # MUST be even dimensions (libx264 requirement)
FPS = 24
DURATION = 12  # seconds
TOTAL_FRAMES = DURATION * FPS

poster = Image.open("poster.png").convert("RGBA")
poster = poster.resize((W, H))
mx, my = W//2, H//3  # moon center (adjust per image)

for frame_idx in range(TOTAL_FRAMES):
    t = frame_idx / FPS
    intensity = min(1.0, t / 8.0)  # Build over time
    
    frame = poster.copy()
    overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    od = ImageDraw.Draw(overlay)
    
    # (1) MOON GLOW — 3-5x stronger than first attempt
    mp = 0.5 + 0.5 * math.sin(t * 2.0)
    ms = intensity * mp
    for r in range(300, 0, -15):
        a = int(60 * ms * (1 - r/300))  # was 12 — now 60
        od.ellipse([mx-r, my-r, mx+r, my+r], fill=(255,220,180,a))
    
    # (2) SWEEPING SPOTLIGHTS — bold red beams
    spd = 2.0 + intensity * 2.0
    lp = 0.5 + 0.5 * math.sin(t * spd)
    rp = 0.5 + 0.5 * math.sin(t * spd + 1.5)
    a = int(120 * intensity * lp)  # was 25 — now 120
    if a > 5:
        od.polygon([(-50,0), (W//2,H), (0,H)], fill=(255,30,30,a))
        od.polygon([(W+50,0), (W//2,H), (W,H)], fill=(255,30,30,a))
    
    # (3) FLOATING EMBERS — bright and large
    cnt = int(100 * intensity)
    for i in range(cnt):
        px = (i * 197 + int(t * 30)) % W
        py = (i * 311 + int(t * -100) + int(60 * math.sin(t + i*0.3))) % H
        sz = 2 + int(intensity * 5)
        a = int(200 * intensity * (0.2 + 0.8 * ((i%10)/10)))  # was 150 — now 200
        od.ellipse([px-sz, py-sz, px+sz, py+sz], fill=(255,180,80,a))
        od.ellipse([px-sz//3, py-sz//3, px+sz//3, py+sz//3], 
                   fill=(255,255,200,min(255,a+40)))
    
    # (4) CROWD WARM GLOW
    cp = 0.5 + 0.5 * math.sin(t * 2.5)
    ci = int(60 * intensity * cp)  # was 15 — now 60
    if ci > 3:
        od.rectangle([0, int(H*0.65), W, H], fill=(255,40,20,ci))
    
    # (5) STROBE FLASH at peak
    if intensity > 0.5:
        flash = max(0, math.sin(t * 5.0)) ** 6
        if flash > 0.2:
            a = int(80 * (intensity-0.5) * flash * 2)
            od.rectangle([0, 0, W, H], fill=(255,50,50,a))
    
    frame = Image.alpha_composite(frame, overlay)
    frame.convert("RGB").save(f"frame_{frame_idx:04d}.png", "PNG")
```

## Encoding Commands

```bash
# Video from frames (scale to even dimensions first)
ffmpeg -framerate 24 -i frame_%04d.png \
  -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2" \
  -c:v libx264 -pix_fmt yuv420p -t 12 video.mp4

# Add audio
ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac -shortest -movflags +faststart output.mp4

# Convert to GIF
ffmpeg -i output.mp4 \
  -vf "fps=10,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=256[p];[s1][p]paletteuse" \
  -loop 0 output.gif
```

## Effect Layers (in order of compositing)
1. Moon glow (radial gradient, pulsing with sin wave)
2. Red spotlights (triangle polygons, left/right beams)
3. Floating embers/particles (small ellipses, drift upward)
4. Border glow (rectangle outline + corner blooms)
5. Crowd energy (subtle warm dots over crowd area)

## Key Technical Details
- **libx264 requires even width/height** — use `scale=1280:720` or pad odd dimensions
- PNG intermediate files can be large (~1-5MB each) — clean up after encoding
- Use `-movflags +faststart` for web-optimized MP4
- Intensity curve: `t / 8.0` gives a slow build over 8 seconds to full intensity
