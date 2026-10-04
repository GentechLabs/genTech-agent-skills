# Session Corrections — July 2026

Key corrections Vanito made this session that shaped the final format:

## 1. Bracket vs Parenthesis Distinction (THE definitive rule)

- **`[Brackets]`** = **Architecture** (song sections, voice assignment, structure — NOT sung)
- **`(Parentheses)`** = **Acting** (delivery cues, tone, how a line is performed)

Mental model from Vanito: "Brackets = architecture · Parentheses = acting"

### Correct examples:
```
[VERSE 1]
Eight billion souls on this spinning stone

[CHORUS]
Kono sora no shita! (yell) I will never let you down!
```

## 2. Clean Section Labels — No Long Descriptions Inside Brackets

Old (rejected): `[VERSE 1 — female, quiet, reflective, a small smile while remembering]`
New (correct): `[VERSE 1]`

Vocal tone descriptions belong in the header metadata area (Genre: / Mood: / Vocal: fields), NOT inside the bracket.

## 3. Header Metadata Format

```
Song Title
Artist · Genre
Genre: J-Rock, Ballad
Mood: Warm, Hopeful, Nostalgic
Vocal: Female
```

## 4. Inline Delivery Cues Use Parentheses

```
(scream)   — screamed delivery
(yell)     — shouted
(growl)    — growled
(whisper)  — whispered
(speak-sing) — half-spoken
(yell softly) — restrained intensity
```

## 5. NO SAVE WITHOUT PERMISSION — THIS TRIGGERS FRUSTRATION

Writing lyrics in chat = OK. Saving them to disk/vault/hub/GitHub = NOT OK without explicit instruction.

**The exact frustration signal:** "Hey, what do I tell you about saving? I did not say save anything."

**Response when this happens:** Immediately delete the saved file(s) and revert the commit(s). Apologize briefly and wait for next instruction.

## 6. "Clean tags" meaning

When Vanito says "write it with clean tags" he means:
- Clean `[VERSE 1]` style section labels
- No tone descriptions inside brackets
- Header metadata at top (Genre, Mood, Vocal)
- Inline delivery cues in parentheses like (yell), (scream)

## 7. No Dividers

No `---` or `***` between sections. Just blank lines.

---

## Jul 13 Session — Additional Corrections

### Vocal Style — ScreamSing (ZillaKami)
Vanito wants KAGE's delivery to be **scream-singing** — like ZillaKami/City Morgue. Aggressive, rhythmic screaming with melody. NOT pure screaming, NOT emo/sad. Added `[ScreamSing]` bracket tag.

### Tone — Cocky, Not Sad
KAGE should sound cocky and aggressive, not sad/emotional. Added `[Cocky]` and `[Proud]` emotion tags.

### Character Count Precision
When given an exact number, match to single character. Verify with Python counting only lyric text.

### Cost Awareness
Vanito surprised by cumulative Seedance costs. Now requires: cost + balance + explicit OK before paid gen.

### Kimi ga Hirotta
KAGE's perspective on meeting HIKARI. Mixed English/Japanese. Donna format.

## Jul 14 Session — Additional Corrections

### Too Many Tags — SIMPLIFY
Vanito rejected the stacked format `[Male][Cocky][ScreamSing][Verse]` saying it was **"too many tags"**. The correct format is just `[Verse]` or `[Chorus][Scream]` — only one additional tag max per section, and `[Scream]` is the only one that matters.

### [ScreamSing] Does Not Work
Vanito explicitly tested and confirmed `[ScreamSing]` is NOT a valid Donna tag. Use `[Scream]` instead (it works). `[ScreamSing]` should never be used again.

### Clean Tag Format Finalized
The approved "clean tags" format for Donna music mode is now:
- `[Intro]` — optionally with one sub-tag like `[Intro][Guitar]`
- `[Verse]`
- `[Chorus][Scream]`
- `[Bridge]`
- `[Outro]`
- No voice tags, no emotion tags, no style tags
- No stacking beyond one tag per line (`[Chorus][Scream]` is max)

### Character Count Flexibility
Vanito changed character targets mid-session multiple times (2699→2690→2500→2400→2100). Always ask if not 100% sure. EXACT precision required (±1 char).

### Mixed JP/EN Confirmed
KAGE's song should mix Japanese and English lines (full alternating lines, not single words). Use natural Japanese phrasing with ！ marks for aggressive delivery.

## Jul 14 Session — Album Art & Image Editing Corrections

### "Soldier" → "Street Kid" — Backstory Correction
Vanito corrected "Story of a Soldier" in the poster. KAGE's backstory is NOT a soldier — he's a street kid from Shinjuku alleys who found a guitar in a dumpster at 16. Changed to "street kid" / "alley kid" metaphors. See `lyrics-writing` skill for the full character lore rule.

### Two Image Editing Tools — Cost & Capabilities

| Tool | Best For | Cost | File Source |
|------|----------|------|-------------|
| **blockrun_image (gpt-image-2)** | Text editing, character replacement, fine detail preservation | $0.06-0.12/edit | Local path OR URL (auto-encodes) |
| **image_generate (FLUX 2 / FAL)** | Free/alternative when BlockRun wallet is low | Free (no USDC) | Public URL only — local files FAIL |

**FAL limitation:** `image_generate` with `image_url` requires a PUBLIC URL — it CANNOT read local file paths. Upload to GitHub first, then use the `raw.githubusercontent.com` URL.

### Wallet Constraints
When BlockRun wallet drops below $0.03, `blockrun_image` rejects with "wallet is out of funds." At that point:
1. Upload the reference image to GitHub hub repo
2. Use `image_generate` with the raw.githubusercontent.com URL as image_url
3. FLUX 2 via FAL handles img2img editing for free (no wallet charge)
4. Quality is slightly lower than gpt-image-2 for text rendering — expect distorted/smeared text

### Iterative Album Art Workflow (Poster Editing)

When editing a poster/album art through multiple rounds:

1. **Source image** → start from the ORIGINAL every time, not a previously-edited version (avoids compounding artifacts)
2. **Clear prompt structure:** list exactly what to change, what to keep, and what to remove
3. **Text rendering:** gpt-image-2 handles English text best when prompted with the exact font description ("distressed white font with red drop shadows"); FLUX 2 struggles with text
4. **Check with vision_analyze** after each round — verify text renders correctly
5. **KAGE appearance** — when Vanito says "put him back to how he looked originally," that means: sleeveless black t-shirt with "VOICE CRACKING STILL TOP THREE" on back, dark pants, messy black hair. NOT the leather jacket / studs / cross necklace version.
6. **Props add story** — a black electric guitar on the ground to the left of KAGE, a crumpled paper with song lyrics between the characters
7. **Ground papers** — Vanito may want only ONE specific paper on the ground (the Yami no Naka De lyrics), not multiple scattered papers

### 🔴 CRITICAL: AI Cannot Do Surgical Edits (Jul 14 Final Round)

**Confirmed across 8+ attempts:** Neither FLUX 2 nor GPT-Image-2 can keep characters identical while making changes. Every img2img call regenerates the full image — characters change, text hallucinates, background shifts.

**When Vanito says "they look different from what I had" — STOP iterating with AI tools.** The solution is not more prompt engineering. Options:
1. **Accept the closest version** and move on
2. **Delegate to Forge** for real compositing (see delegation pattern below)
3. **Start from the ORIGINAL source** (not the last edited version) and try one final batch prompt with ALL changes together

**Key poster changes Vanito wanted in the final round:**
- Title: "SCREAM: Story of a Soldier" → "KIMI GA HIROTTA" + "You Picked It Up"
- Remove ALL scattered ground papers
- Add black guitar lying flat on ground left of KAGE
- HIKARI holds the Yami no Naka De crumpled paper
- One ground paper with Yami no Naka De lyrics
- Remove text from KAGE's shirt (plain black)
- Keep everything else 100% identical to the original
- "RAW BUZZ RAW ART" → "闇の中で 光を見つけた" (found light in darkness)
- Dark mood — do NOT brighten

### Delegation Pattern for Forge
When AI image editing fails 3-5 times, delegate to Forge with:
- Original source image URL (from GitHub hub, never AI-edited)
- All reference images with descriptions
- Numeric list of exact changes
- "Keep characters identical" in bold
- Use delegate_task with detailed context string

**Pitfall:** Forge may timeout (600s). Fall back to accepting best AI version or user sends images directly.

---

## Jul 15 Session — Duet Voice Tags & Standalone Scream Section

### [MALE][BRIDGE][SCREAM] is WRONG — Scream Gets Its Own Section

Vanito corrected the triple-stacked tag `[MALE][BRIDGE][SCREAM]`. The scream should be its own standalone section with its own tag — NOT stacked on the bridge.

**Correct pattern for a duet scream moment:**

```
[MALE][BRIDGE]
(soft, almost spoken)
The quiet line before the turn...

[FEMALE]
(whisper, tender)
The question...

[MALE]
(voice cracking, raw)
The answer...

[MALE][SCREAM]
(yell, breaking open)
The explosion!
```

**Rules:**
- Max TWO tags per section header: `[MALE][BRIDGE]`, `[MALE][SCREAM]`
- `[SCREAM]` is a STANDALONE section, not stacked on `[BRIDGE]`
- The scream hits hardest when isolated after quiet dialogue

### Duet Format Confirmed

When Vanito asks for "tags for vocals male or female", use:
- `[MALE]` on KAGE sections
- `[FEMALE]` on HIKARI sections
- `[DUET]` when they sing together
- `(Male)` / `(Female)` / `(Both)` line-level cues inside DUET sections
- `(tone cue)` as the first line under each section header

### When to Use Each Format — Decision Guide

| Signal | Format | Example |
|--------|--------|---------|
| Vanito says nothing | Clean Tags | `[Verse]`, `[Chorus][Scream]` |
| "write the lyrics with vocals male/female and tone" | Full Lyrics Format | `[MALE][VERSE]`, `[FEMALE][CHORUS]` |
| "add scream tag or aggressive or soft tags" | Add `[SCREAM]` + tone cues to Full Format | Standalone `[MALE][SCREAM]` section |
| "clean tags" | Clean Tags (minimal, no voice tags) | `[Verse]`, `[Chorus][Scream]` |

### Vision API Fallback — When vision_analyze Is Down

When the vision API (provider Console Go) fails with "Upstream request failed" or invalid request errors, you can still work with images:

1. **Check file info** — use `file` command and PIL to get dimensions, format, type
2. **Pixel analysis via Python/PIL** — use `np.array()` to sample color regions (top/mid/bottom, left/right), check for warm/cool colors, brightness distribution, and sky vs ground transitions
3. **ASCII art layout** — resize to ~40x33 and render grayscale as text to see character positions
4. **BlockRun image still works** — `blockrun_image` with a local file path processes the image server-side even if you can't see it. The model reads pixels on the backend. You can trust the edit result.
5. **Browser screenshot** — `browser_navigate` to the image URL, then `browser_vision` may work even when direct `vision_analyze` fails (backend routes differently)
6. **Fallback to hub URL** — upload to GitHub hub first, then use the `raw.githubusercontent.com` URL — some tool routes prefer public URLs over local paths

---

## Jul 17 Session — Section Label Order Correction (CRITICAL for Donna AI)

### Section Label MUST Come First, Then Gender

Vanito explicitly corrected the tag order. The old format `[MALE][VERSE]` was causing Donna AI to sing the wrong parts — it wasn't parsing correctly.

**Correct format (confirmed working):**

```
[VERSE 1]
[FEMALE - SPOKEN, QUIET]
You gonna stare at the wall all night

[MALE - LOW SCREAM, DEFENSIVE]
You wouldn't get it
```

**Structure:**
- Section label on its own line: `[VERSE 1]`, `[CHORUS 1]`, `[BRIDGE]`, `[FINAL CHORUS]`, `[OUTRO]`
- Gender + style on the next line: `[FEMALE - SPOKEN, QUIET]`
- Number sections: `[VERSE 1]`, `[VERSE 2]`, `[CHORUS 1]`, `[CHORUS 2]`
- `[MALE & FEMALE]` for duet sections
- `[FINAL CHORUS]` for the last chorus
- `[INTRO]` and `[BRIDGE]` and `[OUTRO]` don't need numbers
- `[INTRO]` can have a brief instrumental description on the next line (no gender tag)

**What changed from the old format:**
- Old: `[MALE][VERSE]` → New: `[VERSE 1]` then `[MALE - STYLE]`
- Old: `[FEMALE][CHORUS]` → New: `[CHORUS 1]` then `[FEMALE - STYLE]`
- Old: `[DUET][FINAL CHORUS]` → New: `[FINAL CHORUS]` then `[MALE & FEMALE - STYLE]`

**Vanito's exact words:**
"The problem is that with the brackets, you're not adding verse one, two, three, nothing like that in front of like who's singing, like the female and male. You did it at the end where you said outro, dash, female, dash, melodic, fading, bracket. You did that right, but everything on top is missing."

Then: "All you need to do really is add verse, the intro bracket, verse bracket, one, two, three, stuff like that."

And confirmed: "Yeah, it should work, but you're not putting the lyrics like you can still add the lyrics you just got to put the stuff in front of it. That's what you're missing. So like what you have before was fine, you just need to add like the course one, two, three, verse one, two, three, um, intro, bridge, that's all you really need to add it."

### Full Corrected Example (4AM / 四時)

```
[INTRO]
Soft guitar — single red bulb hums

[VERSE 1]
[FEMALE - SPOKEN, QUIET]
You gonna stare at the wall all night
Or let me hear what you got

[MALE - LOW SCREAM, DEFENSIVE]
You wouldn't get it
It's not pretty, it's not clean

[CHORUS 1]
[MALE & FEMALE - RAW, UNPOLISHED]
四時に — four in the morning
Two strangers in a coffin-sized room

[VERSE 2]
[FEMALE - MELODIC, BUILDING]
I found a chord that fit your rage
G minor — felt like home

[CHORUS 2]
[MALE & FEMALE - RAW, UNPOLISHED]
四時に — four in the morning

[BRIDGE]
[MALE - LOW SCREAM, VULNERABLE]
I don't know how to trust

[FEMALE - MELODIC, TENDER]
You don't have to trust me yet

[FINAL CHORUS]
[MALE & FEMALE - FULL, BUILDING]
四時に — four in the morning!

[OUTRO]
[FEMALE - MELODIC, FADING]
四時に...

[MALE - FRIED VOCAL, QUIET]
I think... I think we got something
```
