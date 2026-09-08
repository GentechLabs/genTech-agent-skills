# Multi-Shot Concat Workflow for KAGEKŌ Music Videos

## Concept
Create a narrative sequence by stitching 2+ Seedance 2.0 animated clips together with synchronized audio. Each clip is a separate scene that moves the story forward.

## Standard Sequence Patterns

### Pattern 1: Walk On → Perform
1. Generate "walk-through-door" scene image (openai/gpt-image-2, 1536x1024)
2. Animate walk-on scene with Seedance 2.0 (8s, ~$2.55)
3. Animate performance scene from poster with Seedance 2.0 (10s, ~$3.19)
4. Concat both clips + audio overlay

### Pattern 2: Static Poster → Performance
1. Keep the poster image as-is for the intro (subtle motion)
2. Fade/transition to the performance animation
3. Use with song beginning for a music video intro

### Pattern 3: KAGE Entrance (Poster version)
1. KAGE on left, arms crossed → walks to right side → picks up guitar → plays
2. Requires: generate the "KAGE at guitar" scene image first
3. Animate with Seedance 2.0
4. The animation may not track the exact walking motion — the model animates from the starting image

## Concat Command (Verified 2026-07-12)
```bash
# Step 1: Rescale both clips to same resolution
ffmpeg -i clip1.mp4 -vf "scale=1112:834" -c:v libx264 -an clip1-resized.mp4
ffmpeg -i clip2.mp4 -vf "scale=1112:834" -c:v libx264 -an clip2-resized.mp4

# Step 2: Create concat file
echo "file 'clip1-resized.mp4'" > concat.txt
echo "file 'clip2-resized.mp4'" >> concat.txt

# Step 3: Concat with audio
ffmpeg -f concat -safe 0 -i concat.txt -i song.mp3 \
  -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest -movflags +faststart \
  output.mp4
```

## Predefined Concat Poster Scenes
Generated as of 2026-07-12 and available on hub:
| Scene | File | Description |
|-------|------|-------------|
| Walk-on stage | `scenes/walk-on-stage.png` | Characters walking from wings toward center stage |
| Clean poster (no text) | `scenes/poster-no-text.png` | Poster with all text/logos removed |
| Door-to-stage | `scenes/door-to-stage.png` | Characters walking through backstage door onto stage |

## Song Sync Points (Kono Sora no Shita — 4:33)
| Section | Timestamp | Best For |
|---------|-----------|----------|
| Intro/verse build | 0:00-0:52 | Walking onto stage |
| First chorus | 1:11-1:41 | Performance peak |
| Bridge buildup | 2:57-3:25 | Emotional moment |
| Final chorus | 3:25-4:08 | Full energy climax |
| Verse build-up | 0:40-1:00 | Short teaser (verses into chorus) |
| Mid-chorus | 1:40-1:52 | Medium emotional hook |
