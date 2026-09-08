# Sakura no Chikai — Emotion-First Music Video Storyboard (2026-07-27)

## The 4-Scene Emotional Arc (269s / 4:29)

For a song about memory, loss, and resolution (not action/battle), use this emotional arc:

| Scene | Section | Time | Emotional Arc | Shot Type |
|-------|---------|------|---------------|-----------|
| 1 | Intro | 0:00-0:45 | Gathering courage, silence before the first note | Wide shot, back to camera |
| 2 | Chorus | 0:45-1:45 | Memory arrives, doorway glows, first emotional peak | Medium 3/4, face visible |
| 🎬 Flashback | Insert | 2:45-3:00 | Full memory — young HIKARI + Papa dancing in cherry blossom whirlwind | Wide golden field |
| 3 | Bridge | 1:45-3:30 | Raw emotion, tears, then release → peace | Close-up |
| 4 | Final Chorus / Outro | 3:30-4:29 | Resolution, rain stops, room warms, memory fades | Wide → empty room → end credit |

## Before → Main → After Frame Pattern

Each of the 4 scenes gets THREE keyframes for smooth editing:

| Frame | Purpose | When to use |
|-------|---------|-------------|
| **Before** | The moment before action — tension, hesitation, gathering | "She looks at the photo, gathering courage" |
| **Main** | The peak of the scene | "She plays, doorway glows, memory arrives" |
| **After** | The moment after — reaction, emotion landing | "Crying but smiling, memory fully present" |

Plus extra frames: Verse 1, Verse 2, Chorus 2, Build (hands close-up), Outro transition, End credit.
**Total: 19 keyframes.** Budget: ~$1.24 in image generation.

## Flashback Design (Cherry Blossom Whirlwind)

Papa Tanaka spinning young HIKARI around at golden hour:
- Young HIKARI (age 8): pigtails, "光" shirt, bandaid on knee, barefoot, laughing
- Papa Tanaka: apron, salt-and-pepper hair, warm smile
- Petals swirl around them in a gentle whirlwind — "like a tornado of joy, but not too much"
- Background: coastal town, ocean visible, warm amber/pink sky
- Mood: pure joy — this is her happiest memory, what gave her strength to keep singing

## Music Video End Credit Pattern

Every emotional music video needs a closing title card matching character sheet style:
- Dark textured background with red floral patterns
- Centered: "桜の約束" / "SAKURA NO CHIKAI" / "A promise that never dies"
- Below: "For Papa" / "ありがとう"
- Single cherry blossom petal floating through frame
- Same distressed white serif typography as character sheets

## Hair Color Pitfall — Cool Lighting Causes Purple Hair

**Observed:** When HIKARI's scene has cool blue/rainy window lighting, the red hair tips can appear purple/magenta in the generated output.

**Root cause:** GPT Image 2 mixes the warm red pigment with cool blue ambient light, producing a purple tone. The model interprets the scene's overall cool color cast and shifts the hair accordingly.

**Fix in prompts:**
- Explicitly state: "the hair is jet BLACK transitioning to DEEP CRIMSON RED at the tips, NOT purple, NOT purple-tinted"
- Add: "The red should be a warm crimson, not cool-toned"
- For scenes with blue/cool lighting: add a warm fill light to the prompt (e.g., "warm golden light from a doorway spills across her face")

**Verification:** Always run vision_analyze to confirm hair is black→red, not black→purple, before showing the user.

## VPS File Permission Pitfall

**Problem:** Files uploaded to `/var/www/gentechlabs/` via `scp` as `root` default to `-rw-------` (600 permissions). Nginx requires `-rw-r--r--` (644) to serve them. The user sees 403/404 errors.

**Fix:**
```bash
ssh host "chmod 644 /var/www/gentechlabs/path/to/file"
```
Or batch-fix after every upload session:
```bash
ssh host "chmod -R 644 /var/www/gentechlabs/characters/*.png /var/www/gentechlabs/*.html"
```

## Cloudflare Cache-Busting Strategy

**Don't rely on `?v=2` query params** — Cloudflare edge cache serves stale 404s for old filenames even when the file exists. The browser's `?v=2` forces a fresh fetch, but Cloudflare returns its cached 404 before the browser request reaches origin.

**Working approach:** Use a **new filename** for replaced images:
- ❌ Overwrite `sakura-scene3-bridge.png` → Cloudflare still returns its old cached 404
- ✅ Save as `s3-bridge-v2.png` → update HTML → fresh filename = fresh Cloudflare fetch

## Asset Audit Command

After every batch upload, verify ALL referenced files return 200:
```bash
for f in file1.png file2.png file3.png; do
  curl -sI -o /dev/null -w "%{http_code}" "https://vanito.gentechlabs.net/characters/$f"
done
```
Do this BEFORE telling the user the content is live — prevents the "404" surprise.
