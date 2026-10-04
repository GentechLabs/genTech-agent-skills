# Album Art Iterative Workflow (with blockrun_image)

Lessons learned from the Vanito session (July 2026) about creating album art using AI image editing.

## Process

1. **Start with a reference image** the user provides (or one we generate)
2. **Use blockrun_image with action="edit"** to make changes iteratively
3. **Let the user see each version** before moving on — show it via MEDIA: path
4. **Expect multiple rounds** — album art usually takes 5-8 iterations

## Common Edit Types

| Edit | How to prompt |
|------|---------------|
| Replace character(s) | "Replace the [description] with [new character description] in the same pose" |
| Change background | "Change the background to [new setting], keep the characters" |
| Remove elements | "Remove [specific element] completely" |
| Add elements | "Add [new element] to [position]" |
| Change text | "Change the title text from [old] to [new]" |
| Change color palette | "Change the colors to [dark red/black/gold/etc] palette" |
| Match a style | "Match the same dark gothic heavy metal style as this reference image" |

## Lessons Learned

### 🔴 CRITICAL: AI Cannot Do Surgical Edits

**This is the single most important lesson from the Vanito session (Jul 13-14, 2026):**
**AI image-to-image generators CANNOT make surgical edits while keeping the original image identical.**

Every time you use `image_generate` or `blockrun_image` with `image_url`/`image`, the AI **regenerates the entire image** — it does NOT edit like Photoshop. This means:

- **Characters WILL change** — different hair, clothes, faces, and poses every time, no matter how many times you prompt "keep them exactly the same"
- **Text WILL be hallucinated** — especially Japanese characters, every single time
- **Background elements WILL shift** — graffiti text changes, crowd positions change, lighting shifts
- **You CANNOT preserve the original and change just one element**

**When you need multiple changes (e.g., "add guitar, remove papers, change shirt text, add paper in hand"), do NOT try one edit per change in sequence.** Each edit creates a new version that's further from the original. Instead:

1. **Start from the ORIGINAL** source image every time, not a previously AI-edited version
2. **Batch ALL changes** into ONE single prompt
3. **Accept that the characters will be slightly different** — it's unavoidable
4. **Let the user choose the closest iteration** rather than trying to perfect one

The Vanito poster took 8+ attempts because each edit changed the characters slightly, then Vanito said "put them back how they looked." By attempt 7, the image had drifted so much that going back to the original source was the only option.

### The Simplification Pattern: "Add Everything, Then Strip Back"

Vanito's poster editing cycle follows a consistent pattern:

1. **First request** — Wants many changes at once (title change, character swap, add guitar, remove papers, add crumpled paper, change shirt text, change background text)
2. **Mid-cycle** — Each AI generation drifts further from the original. User says "they look different from what I had"
3. **Correction** — "Put it back how it looked" — simplify the request down
4. **Refinement** — User picks a version he likes and asks for fewer things to change
5. **Final** — One simple change makes it perfect (e.g., "just remove the guitar")

**Lesson:** When the user wants 5+ simultaneous changes in round 1, expect the FINAL result to involve far fewer changes. Do not burn budget on complex multi-element edits early. Start with the 1-2 most important changes first, let the user approve, then layer more from there.

**Pitfall from Jul 14 session:** The user initially wanted 7+ changes simultaneously. After 8+ iterations and $0.48+ in edits, the FINAL approved version required only: title change + remove guitar. Everything else was fine in the original or the user decided they didn't want it after seeing iterations.

### Text Rendering — Limitation Confirmed

**Neither FLUX 2 (image_generate) nor GPT-Image-2 (blockrun_image) can render specific text reliably, especially Japanese.**

Over 8 attempts during the Vanito session:
- "闇の中で" was hallucinated as: 隠して, 捨てて, 隅肉わて, 陽の灯で, and several other wrong variants
- No Japanese text survived correctly in any attempt
- English text was mangled but occasionally close ("Yami road my wordz" instead of "Yami no Naka De")

**Decision rule:** If the user needs EXACT text (especially Japanese), do NOT rely on AI image generation. Propose one of:
1. Add the text after generation using image editing software
2. Use English instead of Japanese (renders slightly better but still unreliable)
3. Generate the image without text, then add text separately

### Copyright Avoidance
- ❌ Avoid any symbols that resemble copyrighted material (Naruto symbols, anime logos, band logos)
- ❌ Don't include "Parental Advisory Explicit Content" stickers — they come from source images
- ❌ Remove flag symbols, credit columns, kanji, or any markings that look borrowed
- ✅ Keep only: characters, title text, and the scene

### Character Consistency
- **KAGE**: spiky dark hair, long black trench coat with red interior lining, silver chain necklace, black combat boots, carries a black electric guitar
- **HIKARI**: long flowing dark hair with crimson red highlights at tips, fitted black corset top with red lacing, tattered black skirt, fishnet arm warmers, black platform boots, holds a microphone
- Describe visually rather than by character name to avoid AI confusion with existing anime
- For detailed model references, generate a side-by-side character sheet first before creating scenes

### Thematic Matching
- When creating art for related songs (same duo), match the style:
  - Dark gothic/cinematic aesthetic
  - Blood moon or golden-white moon
  - Ruined/dystopian city skyline
  - Dark red and black color palette
  - High contrast backlighting

### Text on Album Art
- Keep text minimal — title + subtitle only
- Use jagged/distressed serif fonts for heavy themes
- Clean cursive fonts for warmer songs

### Story Elements That Worked Well
- **Crowd below**: Adding a massive crowd of silhouetted people (\"8 billion souls\") below a stage gives scale and emotional weight
- **Hand-holding**: Characters holding hands reads as romantic/intimate instantly — describe hand position explicitly
- **Standing side-by-side**: Looking at the same horizon together = unity
- **Stage setting with moon**: Characters on a concert stage with a bright moon behind the crowd reads as epic and cinematic
- **Props add story**: A crumpled paper in HIKARI's hand connects directly to the lyrics; a guitar on stage grounds KAGE as a musician
- **KAGEKŌ branding**: Monitors/amps/banners with the KAGEKŌ logo make it feel like a real band

### Pricing Reference (July 2026)
- **blockrun_image (openai/gpt-image-2)** = $0.06 per edit (1024×1024), $0.12 (1536×1024)
- **blockrun_video (xai/grok-imagine-video)** = ~$0.42 for 8s clip
- **blockrun_video (bytedance/seedance-2.0-fast)** = ~$2.04 for 8s clip (better quality + audio)
- **image_generate (FLUX 2 Klein 9B via FAL)** = FREE (no wallet charge, no API key needed)
- Budget ~$0.48 for 8 edit iterations, ~$20-35 for full music video treatment

### Vanito's Hard Stop Signal — "Why do they look different"

Vanito's most direct frustration signal is: **"Why do they look different from what I had"** or **"What the ? GenTech? Why they look different."**

**When you hear this, STOP what you're doing IMMEDIATELY.** Do NOT:
- ❌ Try another AI generation with a more detailed prompt
- ❌ Blame the AI's limitations
- ❌ Offer to try again with a different model

**Instead:**
1. ✅ Acknowledge the problem — the AI changed the characters
2. ✅ Immediately offer to **delegate to Forge** — Vanito already knows Forge is the compositing agent
3. ✅ Package up all references (original image + reference images + numbered change list)
4. ✅ Include the EXACT appearance description of each character so Forge can reconstruct them

**Early detection saves time:** If after 3 AI image edits you see KAGE's hair, clothes, or face changing, don't wait for Vanito to notice. Proactively offer to hand off to Forge.

### Seedance Video — Image URL Must Be Publicly Reachable

When running `blockrun_video` with an image from the hub:

- **GitHub raw URLs can return 404** for recently pushed files — GitHub's CDN takes time to propagate. Even after `git push` reports success, the raw URL may 404 for 30-60 seconds.
- **Workaround:** Use the BlockRun media URL from the original image generation (e.g., `https://blockrun.ai/api/media/media/images/2026/07/20/93f8f30a-...png`) instead of the GitHub raw URL. This URL is immediately accessible.
- **Local file paths don't work** — the upstream provider needs a public URL.
- **PNG vs JPG doesn't matter** — the 404 is a CDN propagation issue, not a format issue.
- **Retry strategy:** If the video server returns "unreachable" errors, wait ~30-60s and retry. The server may be rate-limiting or temporarily down.

### The "Edit the Original" Pattern

When Vanito wants character-accurate album art, the most efficient workflow is:

1. **Vanito sends a reference image** (the base scene he likes)
2. **Edit that exact image** via `blockrun_image(action="edit")` — change character hair, clothes, accessories to match KAGE/HIKARI
3. **Keep the room/background identical** — only change the characters
4. **If the style is wrong** (too anime, too photorealistic), send a style reference video/image and regenerate from scratch with that style baked in, rather than trying to edit the style of an existing image
5. **If Vanito then sends the ORIGINAL image** (the one he found, not the AI-generated one), edit THAT instead — it's the source he actually likes

**Key insight:** Vanito's preferred workflow is:
- Find a base image he likes → edit characters onto it → if style is off, generate new with style reference → if that's still off, go back to the original base image and edit that one directly

This is faster than generating from scratch with text prompts, because the base image's composition, lighting, and mood are already what he wants.

### Wallet Fallback — FLUX 2 via image_generate

When the BlockRun wallet drops below ~$0.03, `blockrun_image` rejects with "out of funds." Switch to **`image_generate`** which uses FLUX 2 Klein 9B via FAL.ai — no USDC required.

| Factor | blockrun_image (gpt-image-2) | image_generate (FLUX 2 / FAL) |
|--------|------------------------------|-------------------------------|
| Cost | $0.06-0.12 per edit | Free |
| English text rendering | Decent (mangled but readable) | Poor (consistently garbled) |
| Japanese text rendering | Hallucinates wrong characters | Hallucinates wrong characters |
| Image source | Local path OR public URL | **Public URL ONLY** — local paths fail |
| Style preservation | Good with image_url | Decent but drifts slightly |
| Speed | ~5-10s | ~10-20s |

**⚠️ Critical limitation: Neither tool can render specific text reliably.** This is a fundamental AI limitation. Over 6+ attempts, both models produced wrong Japanese and garbled English text. Do NOT expect precise text to survive AI image editing.

### FAL Local File Limitation
`image_generate` with `image_url` CANNOT read local paths. Always upload to GitHub first and use the `raw.githubusercontent.com` URL.

### Album Art Editing — Per-Round Workflow (Vanito Pattern)
Vanito's typical cycle runs 5-12 iterations:

1. **Title + subtitle** → prompt exact replacement text describing the font style
2. **Character appearance** → "Keep as in original" or specify changes precisely
3. **Add/remove props** → black guitar left of KAGE, crumpled paper in HIKARI's hand
4. **Clean up debris** → "Remove ALL papers except the one at center"
5. **Adjust text** → never rely on exact text rendering
6. **Restore mood** → "Keep the exact same dark mood, do not brighten"
