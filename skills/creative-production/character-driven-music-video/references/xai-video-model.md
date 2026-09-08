# xAI Video Model (grok-imagine-video) — Reference Animation Workflow

## How It Works
- Takes a source image + text prompt → generates a short animated MP4
- Duration: 5-12 seconds supported
- Keeps the source image as the first frame (image-to-video)
- Cost: ~$0.26 (5s) to ~$0.63 (12s) per clip

## Constraints
- Cannot do complex multi-step sequential actions reliably (e.g. "walk to her, hold hand, then walk to guitar, then play")
- Tends to make digital painted styles look more photorealistic — the shimmer/float effect
- Length is limited — 12s is the max for reliable results
- No control over exact motion or frame-by-frame output

## Best Prompts for Character Consistency
Structure every prompt with these three elements:

1. **Scene preservation:** "The exact same image comes to life from the same camera angle..."
2. **Character anchor:** "Nothing about their appearance changes — same [key details]..."
3. **Action:** Keep it simple — one action per clip

### Good prompt pattern:
> "This exact scene comes to life from the same camera angle behind the characters. [Character] stays facing [direction]. [One simple action]. [Atmospheric effects like lights, fog, crowd]. Nothing about their appearance changes. Same art style, same perspective."

## Pitfalls
1. **Style drift (THE #1 PROBLEM):** The model adds a "shimmer/float" texture that makes digital painted art look photorealistic. This happens EVERY time with poster/album art images. **If the user says "too real," "looks like Keanu Reeves," "the style changed," or "looks like a different person"** — stop using this model for that image. It will NOT improve with different prompts. Switch to ffmpeg overlay effects (Path B in the pipeline).
2. **Perspective drift:** The model sometimes turns characters around or moves them. Anchor with "facing the crowd/away from camera" explicitly.
3. **Detail loss:** Small details (pendant shape, earring, specific embroidery) may blur. Check extracted frames with vision_analyze after generation.

## Signals That The Model Is Wrong For The Job
- User says "too real" or any variation
- User says "it doesn't look like the picture I sent"
- User says "the animation looks almost right but the style changed"
- The poster has a painted/illustrated art style (the model ALWAYS makes this look realistic)
- The user sends a poster/album art image and asks for a "loop" or "GIF" — they want the image untouched with effects on top

## Frame Checking (Post-Generation QA)
```bash
# Extract a frame at 1-second intervals
ffmpeg -i clip.mp4 -vf "fps=1" /tmp/check_%03d.png
```
Then use vision_analyze on the extracted frames to verify character details haven't drifted.

## Alternatives When This Fails
- Use the poster/character sheet directly with Python/PIL frame-by-frame effects (see ffmpeg-overlay-effects reference)
- Full lip-sync requires Wav2Lip (separate post-generation step, not built into xAI)
