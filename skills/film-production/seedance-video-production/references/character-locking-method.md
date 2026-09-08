# Seedance Character-Locking Method — Clean Single Render + Story Block + Scene Cues

Proven working for keeping a character's look consistent across sequential Seedance 2.0 clips.
Validated Aug 10, 2026 during the KAGE church-combat film after MANY failed attempts.

## The core problem
Seedance 2.0 takes ONE `image_url` seed per request. During an action, the character must move
between poses the seed doesn't show, so the model guesses → the character morphs (drift). Worse,
it can drift into another on-screen entity (KAGE became a shadow creature when chaining).

## The ONLY method that worked

### 1. Clean single render seed (NOT a multi-panel grid)
- Seed EVERY clip from ONE clean image of the character (a single full render, the "reference image").
- A multi-panel grid as seed makes Seedance render the grid itself in the video AND misread
  skin tone/complexion. Vanito: "you showed the character sheet and his skin tone changed."
  A grid is a reference for the artist, not a Seedance seed.

### 2. Match the text description to the sheet's ACTUAL appearance
- Run `vision_analyze` on the approved character sheet FIRST to get the real skin tone, hair,
  complexion, undertone.
- Write text that MATCHES it. Do not invent adjectives.
  - ❌ WRONG: "very pale skin" (invented → fought the reference, caused drift; Vanito: "the pale
    prompt is messing the character up")
  - ✅ RIGHT: "pale white porcelain skin with cool ashy undertone" (verified against the sheet)

### 3. Embed a MASTER STORY BLOCK in every clip prompt
Every clip prompt starts with the full locked character description + continuity statement:

```
CONTINUOUS SCENE: [context]. This is ONE continuous battle scene shown scene-by-scene.
[NAME]'s appearance NEVER changes across the whole scene. He looks EXACTLY like the
reference image: [full verified description — skin, hair, eyes, outfit, accessories].
This is a single continuous scene with consistent lighting and identity locked.
```

### 4. Add SCENE CUES with END OF SCENE handoffs
Each clip is numbered and ends by describing where the NEXT keyframe picks up:

```
SCENE 3 OF 7. [action beat].
END OF SCENE: KAGE is mid-swing, candlestick raised, creature reeling — the next scene
continues the swing connecting.
```

This tells the model it's one continuous film, not a fresh guess at the character.

### 5. NEVER chain last-frames
Feeding clip N's last frame as clip N+1's seed causes drift over generations (KAGE degraded
into the shadow creature). Always re-seed independently from the clean render.

## Rejected approaches (all failed with Vanito)
| Approach | Failure |
|----------|---------|
| Multi-panel grid as seed | Grid renders in video; skin tone misread |
| Invented skin/description text | Fought the reference; "pale prompt is messing the character up" |
| Last-frame chaining | KAGE morphs into the shadow creature |
| Panel grid from a different render | Vanito: "I like the other one better what we have" — use the approved seed |
| Parallel same-keyframe | Jumps back to static image each clip |

## Why the blood-moon skateboard film worked
It used a CLEAN SINGLE render as seed for every clip (not a grid), plus a locked coating block.
The church-combat film failed initially because it used a multi-panel sheet and chained last-frames.
