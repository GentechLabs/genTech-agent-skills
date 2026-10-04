---
name: donna-ai-lyrics
description: Format lyrics for Donna AI, Suno, and similar AI music apps using proper bracket/parenthesis tags
---

# Donna AI — Lyrics Formatting Guide

## 🔴 CRITICAL: NO SAVING Without Explicit Permission

Vanito is very clear on this. Do NOT save any lyrics, songs, images, or videos to vault, hub, or GitHub until he **explicitly says so**.

**The pattern:**
1. Write lyrics in the **chat** only — present them inline in your response
2. Wait for him to say "save this" or "put it on the hub"
3. **Only then** write to disk and commit

**Previous violations caused frustration.** If he asks you to write a lyric, show it in your response and stop there. Let him drive the save decision.

## Core Rule (memorize this)

- **`[Square Brackets]`** = **architecture AND direction** — sections, voices, structure, and every tone / mood / delivery cue (none of it is sung)
- **(Parentheses)** = **ad-libs and asides only** — and Donna does not reliably render them

**Mental model:** Brackets = everything the app must act on · Parentheses = ad-libs

### 🔴 CORRECTION — Vanito, Oct 1 2026 (supersedes the "parentheses = acting" rule below)

Verbatim: *"when you're planning to tone an instrument whatever, it has to have brackets. You can't put parentheses. Parentheses does not work on dona app. You have to use brackets."*

- **Tone / mood / delivery goes in brackets.** Never in a parenthesis, and never as a bare prose line — a bare line is treated as lyric and gets sung.
- Use the format Vanito already confirmed: **`[Section - Tone1, Tone2, Tone3]`** — section FIRST, then direction. Examples: `[Verse 1 - Breathless, Staccato, Manic]`, `[Chorus - Scream, Full Throat, Wild]`, `[Bridge - Fragile, Barely Spoken, Cracking, Quiet]`.
- Repeated sections take DIFFERENT direction (e.g. the last chorus `[Chorus - Scream, Hoarse, Voice Shot]`), and a header `Mood:` line is fine because it sits above the first tag.
- Why it matters: a parenthetical cue line is either dropped or read back as lyric, so the direction never reaches the voice. The older stacked form `[Verse 2][Frantic][Cocky][Fast][Twitchy]` was already correct — converting those tags into a parenthetical line was the error, not the stacking.
- ❌ Do NOT move ad-libs such as `(uh, yeah)` into brackets. Brackets are read as architecture, so a bracketed ad-lib becomes a section instruction instead of a vocal. Leave ad-libs in parentheses.

## Song Structure Template

```
Song Title
Artist · Genre

[FEMALE] (or [MALE] or [DUET])

[INTRO]
Lyrics...

[VERSE 1]
Lyrics...

[PRE-CHORUS]
Lyrics...

[CHORUS]
Lyrics...

[VERSE 2]
Lyrics...

[BRIDGE]
Lyrics...

[FINAL CHORUS]
Lyrics...

[OUTRO]
Lyrics...
```

## Header Metadata (before the sections)

```
Song Title
Artist · Genre
Mood: Vulnerable, Warm, Hopeful
```

This replaces long descriptions inside brackets. Keep the bracket labels clean.

## Full Lyrics Format (Voice + Tone + Scream Tags)

**Use when:** Vanito says "write the full lyrics out with the correct tags for vocals male or female and tone", "add scream tag or aggressive or soft tags", or asks for complete vocal direction.

This format combines voice assignment `[MALE]` / `[FEMALE]` / `[DUET]`, section structure `[VERSE 1]` / `[CHORUS 1]` / `[BRIDGE]` / `[OUTRO]`, and parenthetical tone cues.

**⚠️ CRITICAL — Vanito's correction (Jul 2026, confirmed again Jul 17):** The section label MUST come FIRST, then gender, then style. Format: `[SECTION - GENDER - STYLE]`. Do NOT put gender first like `[MALE][VERSE]` — that caused Donna AI to sing the wrong parts. Vanito explicitly confirmed the correct format is:

```
[VERSE 1 - FEMALE - SPOKEN, QUIET]
[VERSE 1 - MALE - LOW SCREAM, DEFENSIVE]
[CHORUS 1 - MALE & FEMALE - RAW, UNPOLISHED]
[VERSE 2 - FEMALE - MELODIC, BUILDING]
[BRIDGE - MALE - LOW SCREAM, VULNERABLE]
[BRIDGE - FEMALE - MELODIC, TENDER]
[FINAL CHORUS - MALE & FEMALE - FULL, BUILDING]
[OUTRO - FEMALE - MELODIC, FADING]
[OUTRO - MALE - FRIED VOCAL, QUIET]
```

**Template:**

```
Song Title
Artist · Genre
Mood: [mood tags]

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
I don't know how to share

[FEMALE - MELODIC, TENDER]
You don't have to trust me yet
Just trust the song

[FINAL CHORUS]
[MALE & FEMALE - FULL, BUILDING]
四時に — four in the morning!

[OUTRO]
[FEMALE - MELODIC, FADING]
四時に...

[MALE - FRIED VOCAL, QUIET]
I think... I think we got something
```

**Key rules:**
- Section label FIRST on its own line: `[VERSE 1]`, `[CHORUS 1]`, `[BRIDGE]`, `[FINAL CHORUS]`, `[OUTRO]`
- Gender + style SECOND on the next line: `[FEMALE - SPOKEN, QUIET]` — indented under the section
- Number sections: `[VERSE 1]`, `[VERSE 2]`, `[CHORUS 1]`, `[CHORUS 2]` — NOT just `[VERSE]` / `[CHORUS]`
- `[INTRO]` and `[BRIDGE]` and `[OUTRO]` don't need numbers
- `[FINAL CHORUS]` for the last chorus
- `[MALE & FEMALE]` for duet sections
- `(tone cue)` — first line of section, tells the AI the delivery style
- Line-level cues like `(Male)` / `(Female)` / `(Both)` inside DUET sections
- Blank line between sections, no `---`
- The `[INTRO]` section can have a brief instrumental description on the next line (no gender tag needed)

### Approved Tone Cues for Parentheses

| Cue | When to Use |
|-----|-------------|
| (spoken-sung) | Half-spoken, half-sung — vulnerable KAGE |
| (raw) | Unpolished, emotional delivery |
| (quiet) | Barely above a whisper, intimate |
| (warm) | HIKARI's comforting, melodic tone |
| (reaching) | Trying to connect, voice extending |
| (cracking open) | Walls coming down, voice wavering |
| (vulnerable) | Soft, exposed, guard down |
| (whisper) | Almost silent, tender |
| (tender) | Gentle, careful, loving |
| (voice cracking) | Emotion breaking through mid-line |
| (yell) | Loud, aggressive, punched out |
| (breaking open) | Explosive release after building tension |
| (building) | Growing intensity, gathering power |
| (triumphant) | Victory, relief, soaring |
| (breathy) | Soft, airy, almost a sigh |
| (fading to silence) | Dying note, trailing off |
| (long pause) | Silence between lines for dramatic effect |

## Brackets [ ] — Architecture

Used for song structure and voice assignment:

| Usage | Example |
|-------|---------|
| Section labels | `[INTRO]`, `[VERSE 1]`, `[CHORUS]`, `[BRIDGE]`, `[OUTRO]` |
| Voice/gender | `[FEMALE]`, `[MALE]`, `[DUET]`, `[Female Vocal]` |
| Production notes | `[guitar solo]`, `[beat drop]` |

## Parentheses ( ) — Acting / Delivery

> ⚠️ **SUPERSEDED FOR TONE (Oct 2026):** Donna does not render parenthetical tone cues. Every tone/mood cue belongs in brackets — see the Core Rule at the top. Parentheses survive only for ad-libs. Everything below in this section describes the old (broken) approach; keep it only for historical context.

Used to shape HOW a line is delivered:

| Cue | Effect |
|-----|--------|
| (yell) | Line is shouted |
| (scream) | Line is screamed |
| (growl) | Line is growled |
| (whisper) | Line is whispered |
| (speak-sing) | Half-spoken, half-sung |
| (yell softly) | Restrained intensity |
| (spoken) | Spoken like dialogue |
| (ad-libs) | Improvised backing |

**Key:** Parentheses tell the AI the *performance style* — the lyrics inside may be spoken, shouted, or treated as background.

## How Brackets vs Parentheses Work Together

```
[VERSE 1]
I remember spring, the cherry trees in bloom

[CHORUS]
Sakura no chikai! (yell) I will never let you down!
```

- `[VERSE 1]` and `[CHORUS]` = structure markers (brackets)
- `(yell)` = delivery instruction right next to the line (parentheses)

## Mixed English + Japanese — Two Mix Levels

Vanito may switch between two mix levels mid-session. Use the MOST RECENT one he stated.

### Heavy Mix (50/50 — Full Verse Alternation)

**Use when:** Vanito says "mixed English and Japanese," "JP/EN mix," or requests the heavy blend without further qualification.

Each line alternates between English and Japanese — NOT just dropping a word here and there:

```
虚ろなステージに散らばった幽霊たち！
An empty stage tonight, twelve ghosts scattered in the dark！
Half walked out before the second verse even hit！
バーテンダーはグラスを拭くだけ、誰も見ない！
```

**Use natural Japanese phrasing** — full sentences and phrases, not single words.

**For KAGE specifically:** Use aggressive Japanese phrases with exclamation marks (！). His Japanese lines should feel punched out.

### Light Sprinkle (Mostly English + Occasional Japanese)

**Use when:** Vanito says "switch it back to just English flat out with some Japanese in it" or "a little bit not too much."

Mostly English lines with just a pinch of Japanese — a key word, a short phrase, or a single Japanese line per section:

```
Empty stage, ghosts scattered — I don't give a damn
Half walked out, good riddance, less noise for me
She stayed — 最高の選択だった best move you made
```

**When to use which:**
- Start at Heavy (50/50) if he hasn't specified
- If he says "too much Japanese" or "switch it back," drop to Light Sprinkle
- Light Sprinkle is his more recent preference — use for follow-up songs after he said "mostly English"

## Instrumental Sections — [Intro][Guitar]

When the song needs an instrumental opening before the vocals start, add it as a tagged section before the first verse. Keep it simple — one direction tag max:

```
[Intro]
Heavy guitar riff
```

Or with a production sub-tag:

```
[Intro][Guitar]
Heavy distorted riff
```

For outros, solos, or instrumental breaks:

```
[Outro][Guitar]
Clean arpeggio fading out
```

**Rules:**
- Keep the description short (5-10 words) — just enough for Donna to generate the right feel
- No full lyrics under these tags, just a brief direction
- ❌ Don't stack emotion tags on the intro — `[Intro]` or `[Intro][Guitar]` only
## Vocal Style Tags — Scream / (scream)

For aggressive/hybrid vocal styles like **ZillaKami** / City Morgue, or post-hardcore where the vocalist **screams WITH rhythm/melody** (not pure screaming):

- Use `[Scream]` as a **section-level bracket tag** for aggressive delivery across an entire section
- Use `(scream)` as a **line-level parenthetical delivery cue** for one specific shouted/screamed line

**NOTE: `[ScreamSing]` is NOT a valid Donna tag.** Vanito explicitly tested it and confirmed it doesn't work. Always use plain `[Scream]` instead.

**Use with basic section tags:** `[Chorus][Scream]` or `[Verse][Scream]`

**Use (scream) for line-level cues:**
```
[Chorus]
You picked it up! (scream) You knew what it was!
```

**Rule of thumb:** Use `[Scream]` (bracket) when the WHOLE section is screamed/aggressive. Use `(scream)` (parentheses) when just one line needs the push.

**When Vanito describes the style verbally**, look for signals like:
- "scream-singing" / "scream most of the time but he's still singing"
- "like ZillaKami when he's screaming but it's still rapping"
- "post-hardcore" / "cocky style"
→ Use `[Scream]` on sections, not `[ScreamSing]`.

## Approved Emotion Tags

**Standard:** `[Angry]`, `[Tired]`, `[Vulnerable]`, `[Desperate]`, `[Confused]`, `[Defensive]`, `[Hopeful]`, `[Breaking]`, `[Reflective]`, `[Fragile]`, `[Warm]`, `[Triumphant]`, `[Peaceful]`, `[Resolved]`, `[Awkward]`

**Cocky/Aggressive (added Jul 2026 per Vanito):** `[Cocky]`, `[Proud]`

**Note on tone:** Vanito prefers KAGE's lyrics to be cocky and aggressive, NOT sad or emo. ZillaKami energy — "I'm the best and she saw it" over "I'm broken and alone." Even vulnerable moments should sound strong.

## Clean Tags Format (for Donna Music Mode)

For generating *music only* (not video) in Donna, Vanito prefers the **simplest possible tag format** — just section structure tags, no vocal assignment, no crowded multi-tag lines.

**Approved simple format:**

```
[Intro]
Heavy guitar riff

[Verse]
Lyrics here...

[Chorus][Scream]
Lyrics here...

[Verse][Scream]
Lyrics here...

[Chorus][Scream]
Lyrics here...

[Bridge]
Lyrics here...

[Bridge][Scream]
Lyrics here...

[Chorus][Scream]
Lyrics here...

[Outro]
Lyrics here...
```

**Rules — CRITICAL (from Vanito's corrections):**
- ❌ DO NOT stack 3+ tags like `[Male][Cocky][ScreamSing][Verse]` — Vanito said this is **too many tags** per section
- ✅ Use at most ONE emotion/additional tag per section: `[Chorus][Scream]` or `[Verse]` — that's it
- ✅ `[Scream]` is the ONLY approved additional tag for aggressive sections
- ❌ No `[Male]` / `[Female]` / `[Duet]` voice tags needed in this format — Donna handles it
- ❌ No `[Cocky]` / `[Angry]` / `[Hopeful]` emotion tags in this format — keep it clean
- ❌ No `[ScreamSing]` — this tag DOES NOT WORK in Donna (Vanito confirmed)
- ✅ Blank line between sections, no `---` dividers
- ✅ `[Intro]` can accept a sub-tag like `[Intro][Guitar]` for instrumental direction — keep the description short (5-10 words on the next line)

**When Vanito says "clean tags" or "add clean tags to the lyrics," use this minimal format.** Do not add vocal, emotion, or style noise to the tags. Let the lyrics themselves carry the content.

**Format selection guide:**
- **Vanito says nothing about format** → Use Clean Tags (minimal, Donna handles voices)
- **Vanito says "write the full lyrics with vocals male/female and tone"** → Use Full Lyrics Format with section-first structure: `[VERSE 1]` then `[FEMALE - STYLE]`
- **Vanito says "add scream tag or aggressive or soft tags"** → Add `[SCREAM]` to KAGE sections and parenthetical tone cues to the Full Lyrics Format
- **Vanito says "clean tags"** → Use Clean Tags (no voice tags, no emotion tags, minimal)

### Character Count Constraints — EXACT Precision Required

When Vanito specifies a character count (e.g. "2400", "2500", "2100"), he means **exactly that number** — within ±1 character. This is non-negotiable; he will call it out if it's off.

**Counting method:**
Count ONLY the lyric text lines — exclude `[tag]` lines and the title line. Use this Python one-liner for precision:
```bash
python3 -c "
with open('file.txt') as f:
    lines = f.read().split('\n')
text = '\n'.join(lines[1:])  # skip title line
print(f'Lyric chars: {len(text)}')
"
```

**Adjustment strategy:**
- **Too long (>target+5):** Condense by shortening lines (remove filler words like "the", "and", "that", "just", "then"), merge line pairs, or remove redundant lines
- **Too short (<target-5):** Add sensory detail, expand backstory, add a line per section, or expand transitions
- **Close (±5):** Add/remove a single word, change punctuation, expand/contract contractions (can't→cannot adds 3 chars, do not→don't removes 2)
- **VERIFY AFTER EVERY CHANGE** — adjust one thing, count again. Never batch-and-hope.

**Common padding words (adds ~3-8 chars each):**
- "just", "still", "even", "only", "there", "then", "back", "down", "now", "yeah"
- Articles: "the", "a", "an" before nouns
- Possessives: "my", "your", "her"

## When to Delegate to Forge (Desktop Compositing)

AI image editing tools cannot do surgical compositing. After 3-5 failed attempts with `image_generate` or `blockrun_image` where the AI keeps changing characters or mangling text, **stop iterating and delegate to Forge**.

**Trigger signals:**
- The AI keeps changing KAGE's hair, clothes, or face despite "keep them exactly the same" prompts
- Japanese text is hallucinated differently every time (3+ attempts)
- The user says "they look different from what I had" or "why do they look different"
- You need to composite a specific element (like the Yami no Naka De paper) from one image into another

**Delegate pattern:**
Use `delegate_task` with a `context` string containing:
1. The ORIGINAL source image URL (from GitHub hub, not an AI-edited version)
2. All reference images with clear descriptions
3. A numeric list of every change needed
4. Bold "KEEP CHARACTERS IDENTICAL" with exact description of original appearance
5. Output expectation — "The result should look like a seamless professional edit, not an AI regen"

**Pitfall:** Forge may time out (600s limit) on complex compositing. The key is recognizing WHEN to stop burning money/time on AI edits that fundamentally cannot deliver surgical precision.

## What NOT to do

- ❌ No long descriptions inside brackets — just clean section labels like `[VERSE 1]`
- ❌ No `---` dividers between sections — just blank lines
- ❌ No markdown formatting inside lyrics (`*`, `**`, `###`)
- ❌ No saving to vault/hub/GitHub without Vanito's explicit say-so
- ❌ Don't even save "research" or "guides" — keep everything in conversation

## Reference Files

| File | What It Covers |
|------|---------------|
| `references/vanito-bracket-parenthesis-rule.md` | Vanito's exact words on brackets vs parentheses |
| `references/session-corrections-jul-2026.md` | All corrections from the July 2026 session — bracket/parenthesis rules, clean tags, [ScreamSing] invalidation, character count precision, album art editing workflow, wallet fallback, KAGE backstory lore |
| `references/iterative-album-art-workflow.md` | Album art creation with blockrun_image, pricing, story elements |
| `references/music-video-treatment-structure.md` | Scene-by-scene music video treatment template |
| `references/kimi-ga-hirotta-donna-example.md` | Full Donna-tagged lyrics example: KAGE's Kimi ga Hirotta. Demonstrates correct use of [brackets] for structure/architecture, (parentheses) for delivery cues, plus [emotion:], [scene:], [camera:], [intensity:], and [action:] tags across a 5-min post-hardcore J-Rock song from Vanito's July 2026 session |
| `references/where-moon-feels-warm-donna-example.md` | Full Donna-tagged duet lyrics example: KAGE & HIKARI's Where the Moon Feels Warm. Demonstrates [MALE]/[FEMALE]/[DUET] voice tags, standalone [MALE][SCREAM] section, and dialogue-to-scream arc. Use when the user asks for "tags for vocals male or female" |
| `references/hub-song-addition-pattern.md` | How to add a new song (audio + album art + GIF + lyrics) to Vanito's hub page — JSON data update, HTML card pattern, and verification |
| `templates/password-gate.html` | Copy-paste HTML/CSS/JS for password locking a hub page |
