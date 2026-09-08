# Character Transformation Prompts — Proven Examples

> Session: 2026-07-15 — "I Heard Your Voice / Kimi no Koe" promotional images
> Model: openai/gpt-image-2 (edit mode)
> Cost: $0.12/image · 3 images = $0.36 total

## Template Structure

All three transformations follow the same structure:
1. Identify each character in the image by position
2. Describe their exact KAGE/HIKARI appearance
3. List environment elements to preserve
4. List ALL text to preserve
5. Art style guard

---

## Image 1: Theatrical Poster (Theater + Torn Paper Composition)

**Source:** Promotional poster with dark silhouette left, spotlighted figure center, torn paper effect right revealing purple background, lyrics overlaid in columns.

**⚠️ FIRST ATTEMPT HAD WRONG ROLE ASSIGNMENT:** Initially put HIKARI screaming in the center spotlight. Vanito corrected: KAGE is the screamer, HIKARI is the melodic vocalist. The prompt below is the CORRECTED version.

```python
mcp__blockrun__blockrun_image(
    action="edit",
    image="<source_path>",
    model="openai/gpt-image-2",
    size="1536x1024",
    prompt="""Edit this theatrical poster for "I Heard Your Voice." Transform the characters to match established character designs while keeping the exact same composition, lighting, text overlays, torn paper effect, and empty theater setting.

CENTER FIGURE IN SPOTLIGHT: Transform into KAGE — a young man with messy spiky black hair, wearing a dark leather biker jacket with silver studs on collar and shoulders. Sharp angular jaw, pale skin. He stands in the spotlight with his arms raised and head tilted back, SCREAMING with intense emotion and anguish. Powerful, raw, desperate energy. This is his scream — the scream that was heard.

LEFT SIDE DARK SILHOUETTE: Transform into HIKARI — a young woman with long flowing black hair, her silhouette visible against the dark theater. She stands with her back partly to viewer, looking toward KAGE in the spotlight. Faint crimson red highlights catch the edge of her hair where the spotlight spill reaches her.

Keep all existing text, lyrics, and the "KIMI NO KOE" paper on the floor exactly as shown. Keep the empty theater chairs, the beam of spotlight hitting center stage, the torn paper effect on the right revealing purple background.

Art style: Dark gothic visual kei digital painting. Detailed, textured, dramatic lighting. NOT photorealistic. NOT anime/cartoon. The characters should look like they belong in the same image naturally — not pasted in."""
)

**Result:** PASS — KAGE screaming in center spotlight (correct role). HIKARI silhouette with flowing hair + red highlights on the left. All text preserved.

> **💡 Note:** The fragment above is from the FIRST (incorrect) attempt that was partially overwritten during editing. The CORRECTED version (KAGE screaming in center, HIKARI silhouette on left) is the one displayed first under the Image 1 heading, and that is the version that passed Vanito's review.


---

## Image 2: Auditorium Connection (Guy Playing Guitar, Girl Kneeling)

**Source:** Dark auditorium with rows of empty chairs, window letting in rainy light. Guy on chair playing acoustic guitar with head back singing. Girl kneeling on wet floor looking up. Heavy lyrics overlay in English + Japanese.

```python
mcp__blockrun__blockrun_image(
    action="edit",
    image="<source_path>",
    model="openai/gpt-image-2",
    size="1536x1024",
    prompt="""Edit this scene to transform the characters into KAGE and HIKARI from the song "I Heard Your Voice / Kimi no Koe." Keep the exact same setting, lighting, and atmosphere.

GUY ON CHAIR WITH GUITAR: Transform into KAGE — a young man with messy spiky black hair, wearing a dark leather biker jacket with silver studs on the collar and shoulders, dark t-shirt underneath. Sharp angular jaw, intense expression. He plays an acoustic guitar passionately, head tilted back, mouth open in song.

GIRL KNEELING ON FLOOR: Transform into HIKARI — a young woman with long flowing black hair with vibrant crimson red highlights/streaks throughout (not just tips), wearing a black off-shoulder corset bustier with criss-cross lacing, a black lace choker with a silver pendant, detached black lace fingerless sleeves, and fishnet stockings. She kneels on the wet floor looking up at KAGE with a focused, hopeful expression.

Keep all existing elements exactly the same: the empty wooden chairs on both sides, the rainy window in the background, the wet reflective floor, the scattered sheet music papers, the purple/blue moody lighting, the beam of light coming through the window.

Preserve all text overlays and lyrics in English and Japanese including "YOUR VOICE", "闇の中で聞こえた" (Heard in the darkness), "I heard it in the dark", "NOBODY HEARD YOU?", "聞こえてたよ" (I heard you), "I WAS LISTENING RIGHT THERE", "SHADOW MET LIGHT", "影と光が出会った夜" (The night shadow and light met), "MADE RIGHT", "THE SONG WE WROTE TOGETHER", "もう逃げないよ" (I won't run away), "NO MORE RUNNING", "I HEARD YOUR VOICE —", "I'M HERE STANDING IN THE SOUND", "KIMI NO KOE", "君の声".

Art style: Dark gothic visual kei digital painting. Textured, dramatic lighting. NOT photorealistic. NOT anime/cartoon. The characters should look naturally part of the scene."""
)
```

**Result:** PASS — KAGE with spiky hair + studded jacket + sharp jaw. HIKARI with red-streaked hair + off-shoulder corset + choker + fishnets. All lyrics preserved. Natural composition.

---

## Image 3: The Room Before and After (Hunched Figure + Doorway Silhouette)

**Source:** Concrete room with spotlight on hunched figure in chair, window with rain left, guitar leaning against wall, notebook in foreground with "Kimi no koe / Your voice" text, silhouette in doorway right.

```python
mcp__blockrun__blockrun_image(
    action="edit",
    image="<source_path>",
    model="openai/gpt-image-2",
    size="1536x1024",
    prompt="""Edit this scene to transform it into KAGE and HIKARI from "I Heard Your Voice / Kimi no Koe." Keep the exact same composition, setting, and mood.

HUNCHED FIGURE IN CHAIR UNDER SPOTLIGHT: Transform into KAGE — a young man with messy spiky black hair, wearing a dark leather biker jacket. He sits hunched forward on the wooden chair, head down, bathed in a harsh white spotlight from above. Despairing, intense, isolated.

SILHOUETTE IN DOORWAY ON RIGHT: Transform into HIKARI — a young woman with long flowing black hair with vibrant red highlights visible at the edges of her silhouette, standing in the doorway. The light from outside creates a backlit silhouette effect. She is looking into the room toward KAGE.

ELECTRIC GUITAR LEANING AGAINST WALL ON LEFT: Transform into a black electric guitar with a dramatic shape (similar to a Dean ML or Flying V style).

Keep all existing elements exactly the same: the concrete room with wet floor, the window with rain on the left, the wooden chairs, the crumpled paper sheets scattered on the floor, the open notebook in the foreground with "Kimi no koe / 君の声 / Your voice / I heard your voice - 聞こえたんだ / Your voice" written in it, the purple pen next to the notebook, the purple brushstroke styling, the dark moody color palette.

Preserve all text on the walls including "I Heard Your Voice" title text, "Kimi no koe. 君の声." subtitle, and the graffiti text "Your voice cracked felt it in my chest" on the wall with the purple heart.

Art style: Dark gothic visual kei digital painting. Textured, dramatic lighting. NOT photorealistic. NOT anime/cartoon. The characters should feel naturally part of the scene."""
)
```

**Result:** PASS — KAGE spiky black hair + leather jacket + despairing pose under spotlight. HIKARI silhouette with red-rimmed hair in doorway. Guitar transformed to black Dean ML style. Notebook text preserved. Natural composition.

---

## Image 3 Iterative Edit Rounds (4 corrections after initial)

This image required the most rounds. Each edit costs $0.12 and risks drifting unchanged elements.

| Round | Fix | Vanito's trigger |
|-------|-----|------------------|
| 1 | Initial character transformation (accepted) | — |
| 2 | Guitar: Flying V → Les Paul with blood splatters | "Doesn't look like his guitar... looks like a bass" |
| 3 | Guitar: darkened to blend into shadow | "Should not be that noticeable" |
| 4 | Paper artifact: removed chain/edge line | "Looks like it was stickered on" |
| 5 | Chain under guitar: removed | "You can see like a black mind on it" |

**Lesson:** Plan for 3-5 rounds per image on character transformation work. Each round can subtly drift other elements (text readability, character features, lighting consistency). Review EVERYTHING after each edit, not just the fix target.

**Total cost for Image 3:** $0.60 (5 edits × $0.12)

---

## Common Pitfalls Encountered

1. **HIKARI's red highlights → "ombre" or "tips-only"** — The model defaults to subtle ombre if you don't specify "vibrant crimson red highlights/streaks throughout (not just tips)."
2. **Japanese text dropped** — You MUST enumerate every Japanese phrase the model should preserve. Generic "keep all text" is not enough for non-Latin scripts.
3. **Art style drift** — Without the explicit "NOT photorealistic. NOT anime/cartoon." guard, the model defaults to a photorealism-adjacent style. The three-part negation is required.
4. **Clothing defaults to generic gothic** — Specificity matters: "studded leather jacket" not "dark jacket", "corset bustier with criss-cross lacing" not "dark top", "platform boots with silver buckles" not just "boots".
5. **Silhouette/distant characters lose fine details** — For far-away figures, focus on silhouette (hair shape, jacket outline, stance). Don't expect chokers or rings to render at that distance.

6. **KAGE vs HIKARI vocal roles** — KAGE screams (raw, anguished, arms raised, head back). HIKARI sings (melodic, emotive, microphone/hands at chest). Do NOT assign scream poses to HIKARI or passive poses to KAGE when the song calls for intensity.

7. **Guitar model per song** — The default spec says Dean ML / Flying V, but the confirmed Yami no Naka De / Kimi no Koe guitar is a gloss black Les Paul double-cutaway with red blood splatters. Always verify which guitar belongs to the song before prompting.

8. **Objects in shadow must not draw focus** — The spotlight is the scene's main light source. Background props (guitar, furniture) sitting in shadow should be dark and subtle, not detailed and bright.

9. **Check foreground artifacts** — The model can create unnatural hard edge lines or glow borders around foreground objects (papers, notebooks). These look like stickers. Check with vision_analyze and re-edit with explicit "remove any visible unnatural border, chain line, or edge" instructions if spotted.
