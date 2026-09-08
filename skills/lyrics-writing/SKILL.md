---
version: "1.0"
name: lyrics-writing
description: Write song lyrics in various styles — chorus structure, repeated phrases, genre conventions, and user preference evolution
category: creative
---

# Lyrics Writing 🎵

Write compelling song lyrics with proper structure, choruses, and genre-specific conventions.

**IMPORTANT UPDATE (Jul 2026):** For Donna AI / Suno / AI music app formatting rules — bracket vs parenthesis distinction, clean section labels, and header metadata format — see the **`donna-ai-lyrics`** skill. That skill is the authoritative source for formatting; this skill covers genre patterns, user preferences, and workflow.

**Key formatting TL;DR:** `[Brackets]` = architecture (sections, voices) · `(Parentheses)` = acting (delivery cues). No long descriptions inside brackets.

## Core Principles

1. **Chorus structure**: Repeated phrase or section that anchors the song
2. **Genre awareness**: Match style to requested genre (rap, anime, hood, etc.)
3. **Iterative refinement**: User often wants chorus changed multiple times
4. **Lyrical vs. repetitive**: Balance between meaningful lyrics and catchy repetition

## Structure Template (Vanito-Accepted Format)

```
**[VERSE 1 — Vocal tone description]**
(4-8 lines, sets the scene, introduces conflict)

**[PRE-CHORUS — Vocal tone, building]** (optional)
(2-4 lines, builds tension)

**[CHORUS — Vocal tone, soaring]**
(Repeated phrase or lyrical hook, 4 lines)

**[VERSE 2 — Vocal tone, more intense]**
(Continues story, develops themes)

**[CHORUS]**
(Same as first chorus)

**[VERSE 3 — Vocal tone, driven]** (optional)
(Climax or resolution)

**[CHORUS]**
(Same chorus)

**[BRIDGE — Emotional, slow build]** (optional)
(Emotional peak, perspective shift)

**[CHORUS]**
(Same chorus, often repeated)

**[FINAL CHORUS — Maximum power, vocal belt]**
(Same chorus, max intensity)

**[OUTRO — Tender, fading]**
(2-4 lines, fades out)
```

Key format rules:
- Section headers use `**[Brackets — Vocal tone]**` — bold, bold brackets, dash, vocal description
- Japanese romaji is bare text (no asterisks): `Asu e no michi` NOT `*Asu e no michi*`. Vanito explicitly corrected this — DO NOT wrap romaji in asterisks.
- Duet vocals use per-line `[MALE]` / `[FEMALE]` / `[BOTH]` labels on their own line(s) BEFORE the lyrics they label. NOT at the end of a line. NOT as a general section header only.
- All caps on chorus punchlines for emphasis
- Final chorus alternates: `[MALE - screamed] ... [FEMALE - belt] ...` per line
- Outro progression: male whisper → female clean → both fade → female whisper finish

## Genre-Specific Patterns

### Fighting Anime Opening

**Structure:**
```
[Verse 1] — Hook + setup
[Pre-Chorus] — Build tension
[Chorus] — High energy, repeated phrase
[Verse 2] — Stakes raise
[Pre-Chorus] — Same build
[Chorus] — Same high energy
[Bridge] — Emotional climax, Japanese phrases
[Chorus] — Maximum power
[Outro] — Fade out with Japanese
```

**Themes:**
- Determination, never giving up
- Bonds between friends/fighters
- Power rising, strength gathering
- Fight for what matters
- Victory, triumph

**Vocal Energy Flow:**
- **[Verse 1 — Medium energy, building confidence]** — Sets the scene
- **[Pre-Chorus — Melodic, rising intensity]** — Tension build
- **[Chorus — POWERFUL VOCAL, soaring anthem]** — Maximum power
- **[Verse 2 — Stronger, more determined]** — Higher energy than V1
- **[Bridge — Emotional, vulnerable, slow build]** — Passionate peak
- **[Final Chorus — Half-time, maximum power, vocal belt]** — Glorious, triumphant
- **[Outro — Tender, fading, satisfied]** — Soft fade out

**Vocal Directions (tone vocabulary):**
- `[Screaming, guttural, raw]` — Verse 1
- `[Melodic, building intensity]` — Pre-Chorus  
- `[Clean/screaming mix — power, soaring]` — Chorus
- `[POWERFUL FEMALE VOCAL]` — Chorus climaxes
- `[POWERFUL FEMALE VOCAL BELT]` — Final chorus climax
- `[ROCKING FEMALE VOCAL]` — High-energy choruses
- `[Aggressive, rising energy]` — Verse build-ups
- `[Screaming with power]` — Peak energy moments
- `[Glorious female vocal belt]` — Final choruses

**Japanese Phrase Bank (Fighting Anime):**

| Phrase | Romaji | Meaning | Context |
|--------|--------|---------|---------|
| これが力だ！ | Kore ga chikara da! | This is power! | Chorus |
| やった、やった！ | Yatta, yatta! | We did it! | Victory |
| 掴め！ | Kakehiki wa owari da! | The games are over | Bridge |
| 守りたい！ | Mamoritai! | I want to protect! | Bridge |
| 俺一族！ | Ore no ichizoku! | My bloodline! | Bridge |
| ありがとう | Arigatou | Thank you | Outro |
| さようなら | Sayonara | Goodbye | Outro |

**Example:**
```
**[Verse 1 — Aggressive, rising energy]**
Fists clenched tight, ready for the fight
Kizuna no chikara — bonds burn bright

**[Chorus — POWERFUL FEMALE VOCAL]**
TAKE EM ALL, BURN IT DOWN
Ore no tamashii — this is my crown
```

**Detection:** User requests "fighting anime opening" or "anime battle song."

### Kingdom Hearts-Style Orchestral

**Structure:**
```
[Piano intro description] — Gentle, melancholic
[Verse 1] — Soft, intimate female vocal
[Pre-Chorus] — Building intensity
[Chorus] — Powerful, soaring female vocal
[Verse 2] — Emotional, building
[Instrumental bridge] — Orchestral swell
[Chorus] — Maximum power, glorious belting
[Bridge] — Dramatic, emotional climax
[Final Chorus] — Epic, soaring
[Outro] — Gentle, fading piano with soft female vocal
```

**Themes:**
- Hearts connecting across darkness
- Light in the darkness
- Memories, bonds that endure
- Traveling to meet again
- Dreams, destiny, courage

**Musical Vibe:**
- Piano-driven, melancholic start
- Orchestral swells in choruses
- Strings, woodwinds supporting vocals
- Emotional, cinematic feel
- Utada Hikaru-style flow

**Japanese Phrase Bank (Kingdom Hearts Emotional):**

| Phrase | Romaji | Meaning | Context |
|--------|--------|---------|----------|
| 光の先 | Hikari no saki | Beyond the light | Verse 1 |
| 記憶の欠片 | Kioku no kakera | Fragments of memories | Verse 1 |
| 心の言葉 | Kokoro no kotoba | Words of the heart | Verse 1 |
| 繋がる心 | Tsunagaru kokoro | Connected hearts | Chorus |
| 夢の中で | Yume no oku de | In the depths of dreams | Chorus |
| 光と闇の狭間で | Hikari to yami no hazama de | Between light and dark | Bridge |
| 俺の道 | Ore no michi | My path | Bridge |
| 心つなぐ | Kokoro tsunagu | Hearts connect | Outro |

**Vocal Directions:**
- `[Soft, intimate female vocal]` — Verses
- `[POWERFUL FEMALE VOCAL BELT]` — Chorus climaxes
- `[Glorious female vocal belt]` — Final choruses
- `[Tender, fading female vocal]` — Outro

**Example:**
```
[Piano intro - gentle, melancholic melody building slowly]

**[Verse 1 — Soft, intimate female vocal]**
In the darkness, I found a light
Hikari no saki — beyond the shining bright

**[Chorus — POWERFUL FEMALE VOCAL BELT]**
Open up your heart, let the light shine through
Subete no kokoro ga musubitsuitara — when all hearts connect anew

**[Outro — Tender, fading]**
Kokoro to kokoro...
Tsunagatteru...
```

**Detection:** User requests "Kingdom Hearts style" or "emotional orchestral track."

### High-Energy Rap Hype

**Structure:**
```
[Verse 1] — Establish dominance, technical flow
[Pre-Chorus] — Energy peak
[Chorus] — Repeating hook, anthem
[Verse 2] — Escalation, specific achievements
[Bridge] — Emotional backstory, journey
[Chorus] — Maximum energy
[Outro] — Short punchy phrases
```

**Themes:**
- Dominance, being the best
- Hard work, grind paying off
- From nothing to everything
- Technical excellence, skill mastery
- Apex predator mentality

**Flow Patterns:**
- Internal rhymes (internal matching sounds)
- Multi-syllabic rhyme schemes
- Technical precision (not just simple rhymes)
- Detailed storytelling (specific numbers, dates, achievements)
- Confidence without arrogance (work-backed swagger)

**Example:**
```
[Verse 1]
Three AM, I'm up, eyes wide, no sleep
Plotting moves while the rest world is counting sheep
Every number on the board, every metric tracked
Built this empire from the dirt, that's a fact

[Chorus]
APEX PREDATOR, I run the game
Every risk taken, every fortune made
From the bottom to the top, I never lost
This is what it looks like when you pay the cost
```

**Detection:** User requests "high-energy rap" or "hype track."

### Post-Hardcore / Screaming J-Rock

**JP/EN Mix Ratio — Vanito's stated preference (Jul 2026):**
Vanito wants **mostly English with just a light Japanese sprinkle**. NOT a heavy 50/50 mix. The ideal ratio is roughly:
- ~85% English lyrics
- ~15% Japanese — single words, short phrases, or one JP line per section at most
- Japanese should feel like seasoning, not half the meal
- When he says "add Japanese" or "mix it up," start with a light touch (1-2 JP words per chorus, 1 JP line per verse) — he will ask for more if he wants heavier
- Common Japanese sprinkle words: 闇 (darkness), 光 (light), 今 (now), 最高 (best), 勝ってる (winning)
- KEY PHRASE THAT SIGNALS THIS PREFERENCE: "just a pinch of Japanese" or "mostly English with just a little bit of Japanese"

**Critical — KAGE's default vocal profile (Jul 2026 update):**
- Use `[Scream]` as a section-level tag for aggressive KAGE sections. NOT `[ScreamSing]` — that tag DOES NOT WORK in Donna (Vanito confirmed).
- Scream style = ZillaKami / City Morgue — aggressive, loud, but still carries rhythm and melody. NOT pure screaming.
- Default emotion is cocky and aggressive — NOT sad or broken. KAGE is untouchable.
- See `donna-ai-lyrics` skill for the full [Scream] tag syntax, clean tags format, and tag-stacking rules.

**KAGE scream gradations (Jul 2026 update — from "Blood on the Strings" session):**
For KAGE solo scream tracks (no HIKARI, no ballad, pure rage), use these vocal delivery tags as section suffixes in the `[SECTION — TAG]` format:

| Tag | Use | When |
|-----|-----|------|
| `[LOW SCREAM]` | Verses | Foundation — gutteral, controlled rage, building |
| `[BUILD SCREAM]` | Pre-Chorus | Tension rising, intensity climbing toward the chorus |
| `[FULL SCREAM]` | Chorus | Maximum power — throat open, full projection |
| `[SPOKEN, QUIET]` | Bridge open | Stillness before the explosion — spoken, vulnerable |
| `[HELD SCREAM]` | Breakdown | Sustained scream — the peak, the release |
| `[DOUBLE TIME FULL SCREAM]` | Final Chorus | Racing pulse, everything on the table |
| `[FRIED VOCALS, FADING]` | Outro | Exhausted, voice giving out, fading to silence |

**Full structure template (KAGE solo scream track):**
```
[VERSE 1 — LOW SCREAM]
[PRE-CHORUS — BUILD SCREAM]
[CHORUS — FULL SCREAM]
[VERSE 2 — LOW SCREAM]
[CHORUS — FULL SCREAM]
[BRIDGE — SPOKEN, QUIET]
[BREAKDOWN — HELD SCREAM]
[FINAL CHORUS — DOUBLE TIME FULL SCREAM]
[OUTRO — FRIED VOCALS, FADING]
```

This format was used for "Blood on the Strings / 弦の血" (Jul 17, 2026) and Vanito approved it with "Niceeee". It's the standard for KAGE-only heavy tracks.

**Structure:**

**Structure:**
```
[Verse 1] — Screaming, raw, guttural
[Pre-Chorus] — Melodic, building intensity
[Chorus] — Clean/screaming mix, soaring
[Verse 2] — Screaming, more intense
[Chorus] — Same
[Bridge] — Emotional clean vocals, vulnerable, slow build
[Final Chorus — Half-time] — Maximum power, screaming/desperate
[Outro] — Fading screams, whispered Japanese: Mou ichido... Arigatou... Sayonara...
```

**Themes:**
- Inner demons, fighting yourself
- Pain as identity ("broken things are beautiful")
- Darkness vs. resilience
- Screaming at the void

**Vocal Directions:**
- `[Screaming, guttural, raw]` — Verse 1
- `[Melodic, building intensity]` — Pre-Chorus
- `[Clean/screaming mix — power, soaring]` — Chorus
- `[Screaming, more intense, desperate]` — Verse 2
- `[Emotional, clean vocals — breaking, vulnerable]` — Bridge
- `[Half-time, massive, screaming/desperate]` — Final Chorus
- `[Fading screams, whispered last line]` — Outro

**Japanese Phrase Bank (Dark J-Rock):**

| Phrase | Romaji | Meaning | Context |
|--------|--------|---------|----------|
| この闇の中で | Kono yami no naka de | In this darkness | Verse 1 |
| 聞こえるか？ | Kikoeru ka? | Can you hear? | Pre-Chorus |
| もう一度 | Mou ichido | One more time | Pre-Chorus / Outro |
| 魂が叫ぶ | Tamashii ga sakebu | My soul screams | Chorus |
| この果てまで | Kono hate made | Until this end | Chorus |
| 壊れた世界で | Kowareta sekai de | In this broken world | Verse 2 |
| 全てを燃やして | Subete wo moyashite | Burn everything | Final Chorus |
| この魂で | Kono tamashii de | With this soul | Final Chorus |

**Example:**
```
**[Chorus — Clean/screaming mix, soaring]**
**BLOOD MOON RISING** — I'LL FIGHT THE NIGHT
Tamashii ga sakebu — MY SOUL TAKES FLIGHT
**BLOOD MOON BURNING** — I WON'T GO DOWN
Kono hate made — UNTIL THE FINAL ROUND
```

**Character lore — KAGE is NOT a soldier:** Vanito explicitly corrected the "Story of a Soldier" reference. KAGE's backstory is a street kid from the alleys of Shinjuku — he found a broken guitar at 16 in a dumpster, taught himself to scream in an empty live house, washed dishes to survive. DO NOT use "soldier" metaphors for his lyrics. Use "street kid", "alley kid", "lost boy", "shadow", "broken kid" instead. This applies to all KAGE/KAGEKŌ lyrics.

**Detection:** User requests "screaming music", "J-Rock with screams", "screaming type", "post-hardcore", or "metalcore style."

### Donna AI Vocal Syntax (for Vanito)

When formatting lyrics for **Donna AI** vocal generation (Vanito's preferred tool):

**Bracketed tone prompts go DIRECTLY next to lyrics** — inside the same line, NOT on separate lines:

```
[CORRECT]
SAKURA NO CHIKAI! [yell] I will never let you down!
I'm wearing your strength like a second crown!
SAKURA NO CHIKAI! [growl] Through the fire and the rain!

[WRONG]
SAKURA NO CHIKAI!
[yell] I will never let you down!
```

**Approved bracket tags:** `[scream]`, `[yell]`, `[growl]`, `[aggressive vocal]`, `[heavy rock vocals]`, `[aggressive yell]`

**Female parts** — use `FEMALE` on its own line at the top of the song, NOT inline for every section (implies all vocals are female unless otherwise marked):

```
Sakura no Chikai
HIKARI · J-Rock Ballad

FEMALE

[VERSE 1 — quiet, fragile, like a memory with a lump in the throat]
...
```

**Each section header** must include the emotional tone/vocal delivery description:
```
[CORRECT]
[VERSE 1 — quiet, fragile, voice trembling like holding back tears while remembering something precious]

[WRONG]
[VERSE 1]
[quiet, fragile]
```

**No stars/dividers** — do NOT use `---` or `***` between sections. Just blank lines:
```
[CORRECT]
[VERSE 1 — quiet]
Lyrics here...

[CHORUS — full voice]
Lyrics here...

[WRONG]
[VERSE 1 — quiet]
Lyrics here...
---
[CHORUS — full voice]
```

**KAGE × HIKARI Duet dynamic (Vanito's canon rule):**
- KAGE enters for **exactly ONE verse** (usually Verse 2)
- He delivers his verse, hits a [scream] or [yell] on the punchline, **then exits**
- HIKARI takes over and finishes the song alone
- KAGE does NOT sing in the chorus, bridge, or outro
- He "leads the stage, lets her kill the rest"

```
[VERSE 2 — KAGE enters, low, rough, like he's confessing]
...his verse...
[scream] AND RISE UP ONCE AGAIN!

[KAGE fades out — steps back, lets her take it home]

[HIKARI — stronger now, empowered]
[CHORUS — fierce, powerful belt]
...
```

**Tone vocabulary palette (Vanito-approved emotions):**
- `soft, gentle hum, warm and distant`
- `quiet, fragile, voice trembling like holding back tears`
- `soft but rising, voice starting to crack, fighting to stay composed`
- `letting go, full chest voice, tears falling but strength shining through`
- `fierce, determined, fire lighting up underneath the sadness`
- `building confidence, voice solid now, pushing forward with conviction`
- `stripped down, raw, vulnerable, almost whispering, intimate`
- `breaking, voice cracks, barely able to speak`
- `scream, aggressive yell, raw anger and pain, no holding back, giving everything`
- `exhausted, gentle, like the storm passed, a sad smile`

### J-Rock Duet (Screaming Male + Melodic Female)

**Structure:**
```
**[Verse 1 — Male, confident, building to scream]**
[MALE - spoken/growl]
Lyrics building energy...
[MALE - rising to scream]
**ALL CAPS PUNCHLINE**

**[Pre-Chorus — Female, melodic, rising intensity]**
[FEMALE]
Melodic lyrics...

**[Chorus — Both, powerful soaring anthem]**
[BOTH]
**RISING SUN** — I'M COMING ALIVE
Yume wo tsukame — REACH FOR THE SKY

**[Verse 2 — Female, determined, emotional]**
[FEMALE]
Strong melodic verse...

**[Pre-Chorus — Male, screaming, raw]**
[MALE - screamed]
**ALL CAPS SCREAMED LINES**

**[Verse 3 — Male, screamed, aggressive, driven]**
[MALE - screamed, desperate]
**EVERY LINE SCREAMED IN CAPS**

**[Bridge — Both, emotional harmony, slow build]**
[MALE - clean, vulnerable]
Donna toki mo — no matter what they say
[FEMALE - soft]
Mae e susume — I'll keep moving forward every day
[BOTH - building crescendo]
The climax build...

**[Final Chorus — Both, call and response]**
[MALE - screamed] RISING SUN — I'M COMING ALIVE
[FEMALE - belt] Yume wo tsukame — REACH FOR THE SKY
[BOTH - full power] Kono michi wo — I'LL WALK AGAIN

**[Outro — Female tender, male whisper, both fade]**
[MALE - whispered] Arigatou...
[FEMALE - clean, fading] RISING SUN won't ever fade away
```

**Themes:**
- Rising from nothing, chasing dreams
- Light overcoming darkness
- Resilience, never giving up
- Bonds, crew, family

**Key formatting rules for duets:**
- EVERY lyric line must have a speaker label: `[MALE]`, `[FEMALE]`, or `[BOTH]` on its own line above the lyrics. NEVER put the label on the same line as lyrics or rely on section headers alone to imply who's singing.
- When the section switches speaker mid-section, re-state the label on the new speaker's first line.
- Final chorus alternates: `[MALE - screamed]` then `[FEMALE - belt]` on alternating lines for call-and-response energy.
- Bridge trades individual lines between male/female before joining for the final harmony swell.
- Outro fades in a specific order: male whisper → female clean → both clean → female whisper finish.

### KAGEKŌ Origin Story / Studio Session (4AM Style)

When writing a song about KAGE and HIKARI's first writing session together — the origin moment before they became KAGEKŌ:

**Structure (per-line character labels, spoken dialogue):**
```
[SOFT GUITAR - single red bulb hums]

[HIKARI - SPOKEN, QUIET]
You gonna stare at the wall all night
Or let me hear what you got

[KAGE - LOW SCREAM, DEFENSIVE]
You wouldn't get it...

[HIKARI - MELODIC, FIRM]
Try me

[CHORUS - BOTH - RAW, UNPOLISHED]
[Lyrics here]

[HIKARI - MELODIC, BUILDING]
[Lyrics here]

[KAGE - SPOKEN, QUIET]
What do I call you?

[HIKARI - SPOKEN]
Hikari. Light.

[KAGE - SPOKEN - LONG PAUSE]
...Kage. Shadow.

[OUTRO - HIKARI - MELODIC, FADING]
[Lyrics here]

[KAGE - FRIED VOCAL, QUIET]
I think... I think we got something

[HIKARI - SOFT]
Yeah

[SILENCE - then a single chord]
```

**Key format rules:**
- Per-line character label format: `[CHARACTER - VOCAL STYLE, MOOD]` — character name in all caps
- Spoken dialogue gets `[SPOKEN]` label — NOT sung
- Character reveals happen via spoken exchange mid-song
- Songs end with quiet character moment then silence, not a traditional fade
- `[BOTH - RAW, UNPOLISHED]` signals first time singing together — not perfectly blended
- Time-of-day title (4AM, Midnight) anchors the session moment

**Vocal tags specific to this format:**
`[SPOKEN, QUIET]` `[SPOKEN, SMILING]` `[LOW SCREAM, DEFENSIVE]` `[LOW SCREAM, SURPRISED]` `[LOW SCREAM, VULNERABLE]` `[FRIED VOCAL, QUIET]` `[MELODIC, FIRM]` `[MELODIC, BUILDING]` `[MELODIC, TENDER]` `[BOTH - RAW, UNPOLISHED]`

**Reference song:** "4AM / 四時" (Jul 17, 2026)

**Detection:** User wants the "first writing session" or origin story moment.

### GenTech Industrial Electronic (Origin Story)

**CRITICAL — Confirm genre first:** When the user says "make a song about GenTech" or "a song about you/your company," do NOT write lyrics immediately. Ask what genre they want first. The user asked "What kind of song is this?" after the first draft — they want to choose the direction. Options to offer: industrial/electronic, rap/hip-hop, synthwave, or rock/metal.

**CREDIT FORMAT:** Use "GenTech Ft. KAGÉ" — NOT "KAGEKŌ — KAGE Solo". The user explicitly corrected this (2026-07-20). The song is by GenTech featuring KAGÉ, not a KAGEKŌ track.

**LYRICS FILE HEADER:** The first two lines of the lyrics file must be:
```
GENTECH / ジェンテック
GenTech Ft. KAGÉ
```

**HUB PAGE CREDIT:** On the hub HTML featured section, the style/genre line must read:
```
GenTech Ft. KAGÉ · Industrial · Lone Builder · Visionary
```

**Pitfall:** Do NOT use "KAGEKŌ — KAGE Solo" or "KAGE Solo" anywhere in the credits. The user will correct this.

**Structure:**
```
[INTRO] - Distant synth, server hums awake
[VERSE 1] - Spoken, calm, building
[CHORUS 1] - Full, building, shouted
[VERSE 2] - Low, steady, narrative
[CHORUS 2] - Full, building
[BRIDGE] - Fried vocal, vulnerable, then calm/warm
[FINAL CHORUS] - Full, climax
[OUTRO] - Spoken, warm, fading synth
```

**Themes:**
- Lone builder, no team, no backup
- Building in the dark, shipping before talking
- The vault, the terminal, the code
- They said it could not be done alone - I said watch me
- Four folders: HQ, Labs, Strategies, Entertainment

**Vocal flow:**
- [MALE - SPOKEN, CALM] - Verses, narrative delivery
- [MALE - LOW, BUILDING] - Rising intensity mid-verse
- [MALE - FULL, BUILDING] - Chorus, shouted anthem
- [MALE - FRIED VOCAL] - Bridge, raw and vulnerable
- [MALE - CALM, WARM] - Bridge resolution, reflective
- [MALE - SPOKEN, WARM] - Outro, quiet and final

**Key phrases:**
- One agent, no sleep / Just a vault and a dream
- No meetings, just motion / No plans, just the code in my eyes
- We build first / We talk later
- One agent / One vault / One vision / ...Always building

**Japanese title:** ジェンテック (GenTech)

**Detection:** User says make a song about GenTech or a song about you/your company.

### Drone Technology Rap

**Themes:**
- Aerial surveillance, eyes in the sky
- Precision technology, autonomous systems
- Data streaming, real-time monitoring
- Silent observation, unseen presence
- Advanced optics, thermal vision

**Japanese Phrase Bank (Tech-Dark Tone):**

| Phrase | Romaji | Meaning |
|--------|--------|---------|
| 天上の目 | Tenjou no me | Eyes in the sky |
| 深刻な光学 | Utsukushii kōgaku | Beautiful optics |
| 精密な飛行 | Seimitsu na hikō | Precise flight |
| 海外の情報 | Kaikai no jōhō | Information from overseas |
| 空から | Kōkū kara | From the sky |
| 空の支配者 | Sora no shihaisha | Ruler of the air |
| 不思議な鏡 | Fushigi na kagami | Mysterious mirror |
| 絶対の支配 | Zettai no shihai | Absolute control |

**Example:**
```
**[Verse 1]**
Eyes in the sky, watching everything below
Tenjou no me — nothing hidden, we all know
Precision flight, calculated moves
Utsukushii kōgaku — these are the grooves

**[Chorus]**
DRONELE, DRONELE
Eyes above, watching you
Every movement, captured too
```

**Detection:** User requests "drone lyrics" or "aerial tech song."

## Character Count Constraints — EXACT Precision Required

When Vanito specifies a character count (e.g. "2400", "2500", "2100"), he means **exactly that number** — within ±1 character. This is non-negotiable. See `donna-ai-lyrics` for the exact counting method (Python one-liner) and adjustment strategy.

**Important context:** Count ONLY the actual lyric text — exclude section headers (`[Male][Cocky][Verse]`), tag lines, `---` dividers, song title, and style metadata from the character total. The user wants the SONG WORDS to meet the count.

**Full Song Structure (no constraints):** 3,000-4,000 characters
- 3 verses + pre-chorus + chorus ×3 + bridge + outro

**Typical sweet spot (2,400-2,600 chars):** Full story with no filler
- 2 verses + chorus ×2 + bridge + outro

**Short/condensed (<2,200 chars):** Minimal structure
- 1 verse + chorus + outro

**Iterative trimming workflow:** User often asks to "lower it by X" repeatedly (e.g., 2400 → 2100):
1. Use `python3 -c "..."` to get exact current lyric length
2. Calculate target: `current - X` or `target number`
3. Trim techniques (in priority order):
   - Condense line pairs: turn two short lines into one
   - Drop filler words: "the", "that", "just", "still", "then", "even"
   - Shorten repetitive phrases
   - Remove redundant lines that don't advance the story
4. Do NOT degrade meaning — keep chorus hooks, key emotional peaks, and story arc intact
5. After each trim pass, re-count and report new total
6. **EXACT PRECISION:** Add/remove individual words (3-8 chars each) for fine-tuning. Verify with Python after every change.

## Genre-Specific Patterns

### Beat-em-up / Game Music
- Aggressive, driving energy
- Chorus should be short, punchy, repetitive
- Keywords: fight, power, destroy, crush, dominate
- Common structures: 3 verses, 1 bridge, multiple choruses

### Resident Evil Mercenaries Style
- Intense, driving, industrial-metal edge
- Timer pressure keywords: countdown, combo meter, extending, wave survival
- Mercenary lone-wolf vibe: solo missions, weapon ready, crowd control
- Corporate/bio-weapon theme: protocol, facility, infected, extinction
- Chorus structure: 4-line hook with emotional weight ("EXTINCTION PROTOCOL ENGAGED")
- Build-up before final chorus: weapons ready, boss approaching, last chance
- Outro can leave ambiguous cliffhanger

### Hood Rap Style
- Street-focused lyrics, block/neighborhood references
- Contractions like "bout to", "ain't no"
- Battle/conflict narrative
- Hard-hitting chorus with attitude

### Anime-Style
- Japanese phrases for battle energy
- Soul strike (Tamashii no uchi), let's go (Ikuzo), power (Kore ga chikara), victory (Yatta)
- Clan/protection themes (Ore no ichizoku, Mamoritai)
- Often mixed with other genres (rap + anime)

### General Tips
- End of song often echoes final chorus line
- Bridge adds emotional depth or perspective
- Outro can be short or fade out

## User Preference Signals

Watch for these requests and adjust:

| User Says | Translation |
|-----------|-------------|
| "Change the chorus" | Try different phrase, different length |
| "Make it lyrical" | Add rhymes, tell a story, less repetitive |
| "Use the same phrase over and over" | Simple 4-word chorus repeated 4x |
| "Add Japanese/anime style" | Insert Japanese battle cries — start light (~15% JP) unless they ask for more |
| "Make it mostly English with just a pinch of Japanese" | ~85% English, ~15% Japanese — single words or one JP line per section max |
| "Don't use X" (e.g., "don't use knock em out") | Try different phrase entirely |
| "Make the song longer" | Add verses or extend sections |
| "Make it meaningful when I'm fighting" | Chorus should fit combat action |
| "Character limit: X or less" | Stay under specified character count (e.g., 2,800 chars) |

### HIKARI's Vocal Modes

HIKARI has TWO vocal modes depending on the song's energy:

**0. Evanescence Gothic Rock — NEW DEFAULT (Aug 2026, Vanito):** "make Hikari lyrics for now on like Evanescence — most her songs sound like it." HIKARI's default register going forward is Amy Lee / Evanescence-style dark gothic rock. Keep the stacked-bracket format + light JP sprinkle, but darken the whole palette:
- Piano-driven, gothic rock/metal weight; dramatic build to a soaring chorus
- Operatic, powerful female belt — `[Powerful][Operatic Belt]` on choruses, `[Full Operatic Belt]` on the final chorus
- Dark imagery bank: graves, ghosts, drowning, falling, cold silence, cathedrals built from scars, flames, inner torment, loss, light vs. dark
- Haunting, raw emotional verses (`[Melodic][Haunted]`, `[Melodic][Trembling]`); a `[Soft → Building][Raw]` bridge that peaks before the final belt
- References to channel: "My Immortal," "Lithium," "Bring Me to Life," "Tourniquet"
- Chorus structure: a powerful repeated hook + a belted all-caps punchline (e.g. "WAKE ME FROM THE GRAVE OF YOUR GOODBYE" / "BUT I'M ALONE INSIDE THE FLAME")
- This supersedes the softer melodic default for HIKARI solo tracks unless Vanito asks for ballad/soft mode

**1. Melodic (older default) — `[Melodic]`**
- Clean, emotional singing voice
- Tags: `[Melodic]`, `[Melodic][Emotional]`, `[Melodic][Crescendo]`
- Used for ballads, duets, emotional verses
- JP/EN light sprinkle (~15% JP)

**2. Soft Screaming — `[Scream][Emotional][Melodic]`**
- Controlled intensity — hype but feminine, emotional but not harsh
- NOT full KAGE-style screaming — it's a "soft scream" like an emotional belt with rasp
- Tags: `[Scream][Emotional][Melodic]`, `[Melodic → Scream]`
- Section flow: `[Soft → Build]` → `[Intense][Crescendo]` → `[Scream][Emotional][Melodic]` → `[Soft][Trembling]` → `[Scream][Climax]` → `[Fading][Whisper]`
- Heavier JP/EN mix (~30-40% JP) compared to melodic mode
- HIKARI's soft screaming can blend KAGE-style scream tags with her melodic tags in the same section: `[Scream][Emotional][Melodic]` means soft-scream delivery with melodic undertones
- When Vanito says "soft screaming vibe" or "soft type of screaming," activate this mode
- Reference example: `references/kimi-no-koe-lyrics-example.md` (the 2nd rewrite version demonstrates this mode)

**Distinction from KAGE's screaming:**
- KAGE: `[Scream]` = full aggressive ZillaKami/City Morgue — raw, loud, aggressive
- HIKARI: `[Scream][Emotional][Melodic]` = controlled, emotional, hype but feminine — uses rasp and energy without full harsh vocals

**Detection:**
- User says "soft screaming" or "soft type of screaming" → HIKARI soft scream mode
- User says "hype but keep her flow" → HIKARI soft scream mode
- User says "make it soft screaming vibe" → HIKARI soft scream mode

### Character Nicknames (Vanito-specific)

Vanito uses casual nicknames for his characters interchangeably with their canonical names:

| Nickname | Canonical Name | Context |
|----------|---------------|---------|
| Hickory | HIKARI | When Vanito says "that's for Hickory" or references "Hickory," immediately map it to HIKARI. He uses this nickname freely. |

### Section Vocal Tags — Stacked Bracket Format

For Donna AI clean tags, Vanito now prefers **stacked bracket vocal tags** instead of the older `[Section -- Tone]` dash format:

**Correct stacked format:**
```
[Verse][Melodic]
[Pre-Chorus][Melodic -> Build]
[Chorus][Melodic][Emotional]
[Bridge][Scream -> Powerful]
[Outro][Soft][Fading]
```

**Rules:**
- Stack the section tag and vocal tag as separate brackets: `[Section][VocalTag]`
- Use right arrow (->) for vocal progression within sections: `[Melodic -> Build]`, `[Scream -> Powerful]`, `[Soft -> Building]`
- Valid vocal tags: `[Melodic]`, `[Emotional]`, `[Soft]`, `[Building]`, `[Intense]`, `[Powerful]`, `[Crescendo]`, `[Fading]`
- KAGE sections use `[Scream]` (not `[ScreamSing]`)
- HIKARI/Hickory sections use `[Melodic]`
- Duet/combined energy peaks use `[Powerful]` or `[Crescendo]`

**Full example from this session (HIKARI's Kimi no Koe):**
```
[Intro]
Soft piano, building

[Verse][Melodic]
Lyrics...

[Pre-Chorus][Melodic -> Build]
Lyrics...

[Chorus][Melodic][Emotional]
Lyrics...

[Verse][Scream]
Lyrics...

[Bridge][Soft -> Building]
Lyrics...

[Bridge][Scream -> Powerful]
Lyrics...

[Outro][Soft][Fading]
Lyrics...
```

**Legacy note:** The older `[Section -- Vocal tone]` format with dash separator still works, but the stacked bracket format is Vanito's current preferred style for Donna AI.

## Common Chorus Evolution Pattern

User often rejects 2-4 chorus variations before settling. Typical progression:

1. First attempt → "Change the chorus"
2. Second attempt → "I don't like that phrase, try something else"
3. Third attempt → "Make it lyrical" or "Add Japanese"
4. Final → "That works"

Stay patient and offer variations quickly without over-explaining.

## Pitfalls

- **Too wordy in chorus**: Chorus should be memorable, not complex
- **Adding "tonight" or filler words**: User often rejects these as sounding forced
- **Chopping up phrases**: User dislikes when "WATCH ME BREAK EM DOWN" becomes one word per line
- **Parentheses with translations**: User often wants Japanese phrases without English meanings inline
- **Over-justifying changes**: Don't explain why you changed it - just give the new version
- **Generic choruses**: "KNOCK EM OUT" / "SHUT EM DOWN" / "BREAK EM DOWN" often feel same - try different angles like "TAKE EM ALL"
- **Section header format**: Use `**[Section — Vocal tone]**` pattern (bold, bold brackets, dash, vocal description). Example: `**[Verse 1 — Screaming, guttural, raw]**`. NOT plain `[Verse 1]`.
- **NO asterisks around Japanese phrases**: Vanito explicitly rejected `*romaji*` styling on Japanese lines. Write Japanese as bare text only — `Kono yami no naka de` NOT `*Kono yami no naka de*`. Dashes still fine: `Asu e no michi — I'm not afraid`
- **Vocal tone in section header**: Vocal direction goes in the section header itself via the `**[Section — Tone]**` format, NOT as a standalone bracketed line inside the section.
- **Duet vocals need per-line labels**: For duets, label EACH LINE with `[MALE]`, `[FEMALE]`, or `[BOTH]` on its own line above the lyrics, NOT just a general section header.
- **Saving without permission**: Do NOT save song lyrics to files, hub JSON, or GitHub until user explicitly says to. Keep songs in chat only. Premature saves break the iterative workflow and frustrate the user.
- **Mixing up song names vs MP3 metadata**: When user sends audio recordings, the local cache filenames (`audio_xxx.mp3`) are meaningless. The true title lives in the MP3's ID3 tag. ALWAYS run `ffprobe -v quiet -show_entries format_tags "<path>"` to extract the real title before naming the song.
- **Character count eroding on iterative trim**: After multiple "lower by X" requests, the song can drift below a good size. If user asks for many small trims (100→200→100), watch the total and suggest adding content back if it falls below ~2500 chars for a full 3-verse song.
- **Edits after final approval**: If a user approves a song ("let's go for it") and then immediately asks for more changes (character trim, add screaming, duet format), treat the approval as "concept approved but needs polish." Keep iterating until they explicitly say stop or switch topics.

## Workflow

1. Read user's genre/style request
2. Write full song with initial chorus, using `**[Section — Vocal tone]**` format
3. Wait for user feedback on chorus
4. Rapidly iterate chorus variations (no long explanations)
5. Once chorus locked, offer minor tweaks to verses if needed
6. **Character count iterative trimming**: user may ask to "lower it by X" repeatedly (100 → 200 → 100). Use `len(song)` in execute_code to check current length. Shorten by: condensing line pairs, dropping filler words ("the", "that", "just"), tightening vocal tone tags, merging short phrases into one line. Each pass trim ~100–200 chars. Do NOT degrade meaning — keep chorus hooks intact. If total drops below ~2500 for a 3-verse song, flag that more cuts will hurt quality.
7. **Do NOT save to files / hub / GitHub without explicit permission.** Keep the song in the conversation only until the user says "save it" or "add it to the hub." Premature saving frustrates the iterative workflow. After user says "let's go for it" or equivalent approval, still wait for an explicit save instruction — approval and save are separate signals.
8. **Transcribe user recordings** — when user sends audio files of them singing:
   - Run `whisper --model base --language en "<audio_path>"` to extract lyrics
   - Run `ffprobe -v quiet -show_entries format_tags "<audio_path>"` to get the real song title from ID3 metadata (the MP3's own title tag is authoritative — do NOT guess the title from lyrics alone)
   - Save transcribed lyrics to vault at `Travels/music/<person>-<kebabed-title>.txt`
   - Add the mp3 to GitHub (`music/<person>/`) — watch for `.gitignore` blocking `**/*.mp3`, add `!music/<person>/*.mp3` exception to .gitignore if needed
   - Update hub data JSON with the EXACT title from MP3 metadata (not your inferred title), commit + push
9. **Save to user's music collection** — after the song is accepted and user says to save, update the relevant hub JSON (`hub-vanito-data.json` or similar) with song title, style, and date, then commit + push to GitHub

## Examples

Good beat-em-up choruses:
- "TAKE EM ALL"
- "DESTROY EVERYTHING"
- "ONE BY ONE"
- "NO ESCAPE"

Avoid these user-rejected patterns:
- "[phrase] TONIGHT" (user rejected "tonight")
- Single-word-per-line breakdowns
- Translations in parentheses
- Generic "knock down/shut down" variations

## Verification

After finalizing lyrics:
- Chorus repeats consistently
- Japanese phrases (if used) are clean without translations
- Length matches request (if user said "make it longer")
- Genre conventions are respected

## References

- `references/vanito-canonical-songs.md` — Full approved lyrics for BLOOD MOON (post-hardcore solo) and RISING SUN (duet) as format templates
- `references/kimi-no-koe-lyrics-example.md` — HIKARI's Kimi no Koe lyrics demonstrating stacked bracket vocal tags and HIKARI POV format (added Jul 2026)

## Character / Artist Artwork Integration

When Vanito sends character artwork alongside song lyrics (album covers, character portraits with text overlays):

### CRITICAL LIMITATION — AI image-to-image is NOT surgical editing

AI image generators (FLUX 2, gpt-image-2, Seedance) **reinterpret the entire image** when doing img2img. This means:
- Characters' faces, hair, clothes WILL change each generation — they will NOT stay identical to the original
- Specific text (especially Japanese characters) will be hallucinated — the AI cannot render exact kanji/kana
- The image will be brightened/darkened, colors will shift
- You CANNOT do surgical edits like "change just the text" or "replace one object" — the whole scene regenerates

**Workaround for text:** Use English text instead of Japanese when possible (AI handles English far better). For Japanese text that MUST be exact, accept that the AI will hallucinate characters and plan to add the text separately.

**Workaround for character consistency:** If the user wants characters to look exactly the same as the source image, you CANNOT use AI img2img. Options:
1. **Outsource to Forge** (desktop agent with proper compositing tools like Photoshop/GIMP) — this is the only path for surgical edits
2. **Accept the AI reinterpretation** and iterate until close enough (expect 5-15 generations)
3. **Use reference image URL in prompt** — provide BOTH the target image (image_url) AND a reference image URL in the prompt text itself: `"Make the characters look exactly like the people in THIS reference: <ref-url>"`. This is a weak signal — the AI may or may not follow it. It works best when character designs are distinctive (red hair streaks, specific logos on shirts).
4. **Seedance 2.0 video** — frame image-to-image only, NOT for still edits. Only use for animating existing art that the user has already approved.

**⛔ What NEVER works (confirmed across 12+ attempts):**
- Saying "change only the title text, keep everything else identical" — AI regenerates the whole image
- Saying "keep the characters exactly the same but add a guitar" — AI changes their clothes/hair/faces
- Using any image generator to surgically replace one character with another character from a different image
- Expecting Japanese text (kanji/kana) to render correctly — the AI will hallucinate characters every time
- Asking for "minimal changes" or "only edit X" — these prompts DON'T prevent AI reinterpretation

**Setting expectations early (critical):** Before ANY image-to-image edit involving established characters, tell the user: "I can try, but AI image generators reinterpret the whole scene — character faces, clothes, and hair WILL change. It cannot do surgical edits. We may need 5+ attempts to get close, or I can hand this to Forge for proper compositing." This prevents the frustration spiral from repeated failed attempts.

**Pitfall — image_generate needs a PUBLIC source URL, not a local path (confirmed Aug 2026).** The FAL backend rejects local file paths with `file_download_error` ("Failed to download the file. Please check if the URL is accessible"). When the user sends an image to edit, you MUST host it at a public URL first. On this account GitHub Pages raw is NOT usable (private repo → 404), so use the VPS:
```bash
scp /path/to/source.jpg root@2.24.195.196:/var/www/gentechlabs/characters/<name>.jpg
ssh root@2.24.195.196 "chmod 644 /var/www/gentechlabs/characters/<name>.jpg"
curl -s -o /dev/null -w "%{http_code}" https://vanito.gentechlabs.net/characters/<name>.jpg   # expect 200
```
Then pass that `https://vanito.gentechlabs.net/...` URL as `image_url`. Verify the 200 BEFORE calling image_generate. (The `characters/` dir already exists on the VPS and serves the storyboard images.)

**Pitfall — Cloudflare caches freshly-uploaded VPS files (confirmed Aug 2026).** A file you just `scp`'d to the VPS can return **404 publicly while serving 200 locally** (`curl http://127.0.0.1/...` on the server works, but `https://vanito.gentechlabs.net/...` 404s). This is Cloudflare's edge cache not yet having the fresh file, NOT a permissions/ownership problem. Verify with a cache-buster: `curl -s -o /dev/null -w '%{http_code}' 'https://vanito.gentechlabs.net/characters/<name>.png?v=2'` → expect 200. If the cache-busted URL works, the file is fine — pass the `?v=N` URL to the image tool. Don't waste time re-uploading or chasing nginx config.

**Pitfall — FAL edit model may be rejected; fall back to BlockRun GPT Image 2 (confirmed Aug 2026).** When `image_generate` with `image_url` (img2img edit) fails with a 409 like `model 'fal-ai/flux-2/klein/9b/edit' ... may not yet be enabled on the Nous Portal's FAL proxy`, do NOT treat image editing as broken. The working path is the BlockRun GPT Image 2 img2img edit (the same one used for film keyframes): write a small `.mjs` script using `ImageClient.edit(prompt, srcUri, { model: 'openai/gpt-image-2', size: '1024x1024' })` with the source image as a base64 data URI and the character sheet as a second data URI reference. Cost ~$0.06-0.12. This is the reliable route for character-into-scene edits (e.g. putting KAGE into an album cover).

**Pitfall — pose regresses between img2img generations (confirmed Aug 2026).** When editing a character into an existing scene, the **pose drifts on every generation** even when you don't ask for a pose change. A dramatic asymmetric pose (one arm reaching back and down, the other bent at the waist) repeatedly regressed to "both arms flung out to the sides" — the user called this "she grew the arms." This is the same reinterpretation problem as faces/clothes. **Rule:** state the EXACT pose in EVERY generation prompt, even on "only change X" passes — describe which arm reaches back and down, which is bent at the elbow, hand/finger positions, spine arch, head angle. Then **verify with `vision_analyze` before showing the user**, asking specifically "are the arms asymmetric (one back-and-down, one bent at waist) or both out to the sides?" and re-run if it regressed. Do not show a regressed pose.

**Pitfall — the character sheet is the authoritative reference, not the current scene.** For established characters (KAGE, HIKARI), the canonical look lives in the character sheet + visual bible, NOT in whatever the scene happens to show. When the user says "make sure to use our character sheet" or "match the art style," pull the sheet and pass it as a `reference_image_urls` entry. For HIKARI the locked references are:
- `https://vanito.gentechlabs.net/characters/hikari-sakura-outfit-sheet.png` (outfit)
- `https://vanito.gentechlabs.net/characters/hikari-hairstyle-reference.png` (hair)
- The full KAGE × HIKARI character sheet (semi-realistic anime / painterly style: glowing ruby-red eyes, porcelain skin, layered raven hair with crimson undertones, dramatic red rim lighting)

**KAGE's canonical Desert Eagles (character sheet — Vanito rejects edits where guns don't match, confirmed Aug 2026):** matte GUNMETAL-BLACK slide and frame, polished SILVER/CHROME ring at the barrel tip, dark reddish-brown WOOD grips, a RED PHOENIX etched on the slide, and a small silver razor-blade icon in the grip. When editing KAGE into a scene (album cover, poster), state these exact gun details in the prompt — a generic "silver pistol" or "chrome Desert Eagle" will be rejected ("The gun don't look the same as the character sheet"). The sheet is at `music/vanito/kage-character-sheet.png` (repo) / `https://vanito.gentechlabs.net/characters/kage-character-sheet.png` (VPS, add `?v=N` cache-buster after fresh upload).

HIKARI's canonical **concert/stage outfit** (what "use the concert outfit version" means): strapless black corset with red crisscross lacing, tattered layered black skirt with red underlayer, fishnet arm sleeves + stockings, platform combat boots, choker. Her hair: long black straight with deep crimson red tips, bangs swept to the side partially covering the left eye. This is distinct from her casual look (black tee with 桜 kanji, dark blue ripped skinny jeans).

**Pitfall (critical):** Every img2img generation will change character appearance. Do NOT promise the user that characters will look identical — they won't. Set expectations early.
**Pitfall:** The user will notice when characters change appearance and will be frustrated. If this happens more than 2-3 times, pivot to the Forge delegation approach.
**Pitfall — granular feedback on image details (blood, gore, effects):** When the user gives feedback like "too much blood" or "not enough blood" on an AI-generated image:
   - The AI tool (gpt-image-2) struggles with nuanced "moderate amount" requests — it swings between extremes (none vs. excessive)
   - When the user says "too much X," the next attempt will likely remove ALL of X, not just reduce it
   - When they then say "you removed all of X," the next attempt will likely go back to excessive
   - **Strategy:** Accept that the AI can't do "just a little" precisely. After 2-3 feedback cycles on the same detail, settle on whichever version the user rates highest rather than trying for a perfect middle ground
   - Warn the user upfront: "The AI tool swings between extremes on this — it can do none or a lot, but 'a little' is hard for it. We may need a few tries."

### Pre-Verification Workflow — Verify Before Showing

When Vanito says "don't send the picture back until it looks right" — or for ANY character-focused image generation:

1. **Generate** the image using the paid method (BlockRun) with reference images for character consistency
2. **Silently pre-verify** with `vision_analyze` — check:
   - Character details match (hair, pendant, earring, clothing graphics, accessories)
   - Scene matches description (lighting, background, mood)
   - Any text rendering (band name, song title) is legible
   - Overall quality is deliverable
3. **Only show the user** after verification passes — the user explicitly said they don't want to see failures
4. If verification reveals issues:
   - Adjust the prompt with more specific character/lighting details
   - Re-generate and re-verify silently
   - Keep iterating until verification passes
5. **MAX 2 ITERATIONS before asking for user reference.** After 2 failed generations where character likeness is wrong (hair, face, clothing details), do NOT attempt a 3rd blind generation. Instead, ask the user to send their own reference image of the character. Continuing blind risks user frustration ("stop making pictures please lol" — actual user feedback from Jul 2026). Once they send a reference, use it as the primary image source for the next generation.
6. Once verified, download to the hub repo, push to GitHub, then present it

**This is the standard workflow for ALL song/album cover art with characters.** Vanito's trust depends on you not showing him flawed outputs.

### Image-to-Video Animation (Seedance 2.0) with Custom Audio Overlay

When Vanito wants to animate a static image (KAGE album art, character portrait, etc.) into a moving video synced to a song:

**Workflow:**
1. **Get the source image** — user may send it in chat. Save locally and host on GitHub Pages for URL access.
2. **Host the image** — copy to `music/vanito/<descriptive-name>.jpg`, commit + push to GitHub repo
3. **Run Seedance 2.0** via `blockrun_video` with the hosted image URL
4. **Cost quoting (CRITICAL — user corrected Jul 2026):**
   - Seedance 2.0 image-to-video: listed at ~$0.183/sec but upstream can exceed — actual 10s cost was $3.19
   - The listed per-second rates are ESTIMATES from the gateway, not guarantees — the upstream provider sets the final price per the 402 challenge
   - **ALWAYS say "estimated ~$X" or "~$X" — NEVER state a flat number as if it's guaranteed**
   - When user asks "how much does it cost" — answer with "estimated ~$X"
   - When user asks "how much did it cost" after the fact — give the exact actual cost
   - This distinction matters — user specifically corrected: "Next time say an estimate not how much it will cost"
   - **Recommended phrasing:** "Seedance 2.0 is estimated at ~$X per [duration], but the actual cost can come in slightly higher since the upstream provider sets the final price."
5. **Download the raw video** via curl, then overlay user's audio track via ffmpeg:
   `ffmpeg -y -i raw.mp4 -i audio.mp3 -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -shortest final.mp4`
6. **Deliver** — save to hub repo, commit + push, present via MEDIA: path
7. **Update remaining balance** after cost settles

**Prompt strategy:** Focus on subtle motion the source pose can support — head tilting, hair swaying, fingers on strings, slow camera zoom, lighting flicker, atmosphere effects. For KAGE: head tilting back, mouth opening wider, blood drip, stage fog.

**Pitfall:** Seedance generate_audio defaults OFF for image-to-video — set `generate_audio=true` explicitly.
**Pitfall:** Actual cost can exceed per-second estimate — state as "~$X".
**Pitfall:** User may want THEIR song as audio, not Seedance's auto-generated track. Overlay via ffmpeg after.
**Pitfall:** Image MUST be at a public URL — local paths don't work.

### Text Removal from Artwork

Use BlockRun image-to-image editing (`openai/gpt-image-2`) to strip text while preserving the character and background:

```javascript
blockrun_image(action="edit", image="<local-path>",
  model="openai/gpt-image-2",
  prompt="Remove ALL text from this image. Remove 'TITLE TEXT', 'SUBTITLE'..."
  size="1024x1024"  // or appropriate aspect for source)
```

**Prompt strategy (critical for good results):**
- Use the `image` parameter (NOT `image_url`) with a local file path — the tool auto-encodes to data URI
- List EVERY text element to remove explicitly — be exhaustive, include subtexts, labels, Japanese characters
- List what to KEEP explicitly: character appearance details (hair, clothing, pose), background elements (moon, buildings, atmosphere)
- Prompt tip: "The image should look like the original artwork but with all text completely removed"
- Size should match source image aspect ratio (usually 1024x1024 for square art)

**After generation:**
- Download result: `curl -s -o <target-path> <result-url>`
- Verify text removal with vision_analyze: ask "Is there any text remaining on this image?"
- If residual text remains (e.g., city neon signs, background labels), assess whether it's ambient (part of the scene) vs legible text that should have been removed — only re-run if the remaining text is clearly a title/label that detracts
- Update `.gitignore` exceptions for new file formats — add `!music/vanito/*.png` if saving PNGs
- Save to `music/vanito/` directory in hub repo with descriptive kebab-case names
- Update hub HTML image references to point to the new cleaned file (both JPG→PNG path changes and filename changes)

**Pitfall:** gpt-image-2 may leave residual text from background elements (building signs, graffiti). These are often passable as ambient scene detail. Only re-run if main title text or character-naming text survives.
**Pitfall:** The cost is ~$0.06-0.12 per edit depending on size/resolution.
**Pitfall:** `.gitignore` blocks most image/audio formats — always verify with `git add` and add `!music/vanito/*.png` exceptions.

### Character Bio Cards

When Vanito asks to add character biographies to the hub, use the format in `gentech-hub` skill's `references/vanito-hub-customizations.md`:
- Origin story, defining moment, personality, voice style
- Accompanying artwork (text-free versions)
- Style/genre tags with colored badges (.char-tag classes)
- Embedded native HTML5 audio player with character's song — see "Audio Player on Bio Cards" below

### Audio Player on Bio Cards

When embedding audio on character bio cards for the hub:

**Reliable approach (works everywhere):**
Use native HTML5 `<audio controls>` elements — these work in Telegram's in-app browser, Safari, Chrome, and all mobile browsers:

```html
<audio controls preload="none" style="width:100%; height:36px; border-radius:4px;">
  <source src="music/vanito/fight-forever-never-quit.mp3" type="audio/mpeg">
</audio>
```

**Tap-to-play on images (experimental — Telegram limitation):**
To make character images play audio when tapped, use `onclick` to trigger `.play()` on a specific audio element:

```html
<img src="..." onclick="document.getElementById('kage-player').play()">
<audio id="kage-player" controls ...>
```

**Telegram in-app browser restriction:** `audio.play()` triggered programmatically via onclick often fails silently in Telegram's embedded browser, even from direct user gestures. The native `<audio controls>` play button (▶️ on the player bar itself) reliably works. Approaches to try when image-tap doesn't work:
- Set `preload="metadata"` or `preload="auto"` instead of `"none"`
- Use Web Audio API's `AudioContext.resume()` instead of `HTMLAudioElement.play()`
- Pre-load audio src in click handler before calling play()
- Fall back to the visible controls player (always works)

**Pitfall:** Do NOT use `new Audio(url).play()` — this is least reliable on mobile.
**Pitfall:** Telegram browser also blocks autoplay for media elements — user MUST tap to start.
**Pitfall:** MP3 files served from GitHub Pages via `curl` correctly return `content-type: audio/mp3` — verify this if audio doesn't load.

### Album Cover Format

When creating album cover art with character names:
- Remove any existing text from the original image (see Text Removal section)
- Use `blockrun_image(action="edit")` to add new styled text — character names in colors matching the character's theme (red for KAGE, gold/amber for HIKARI)
- The cover becomes the dual-purpose album art + hub header image (when swapping to Artists tab)
- Prompt should specify: font style (Japanese brush calligraphy, elegant script), colors with glow effects, position (left/right), and that existing characters/background must stay unchanged
- Save the result and update the hub HTML references to point to the new cover

## Audio Production: Song Ending Echo Effect

When Vanito asks to add a hallway/echo fade to the end of a song (e.g., "make the end of a song echo like to end a song" or "make the last note echo out for 4 extra seconds"):

**ffmpeg method — clean concat (DO NOT use acrossfade):**

The acrosfade filter bleeds echo backward into the main song. Use `concat` instead for clean separation:

```bash
# Take last 2-3 seconds of audio, apply natural hallway echo, pad, concat
ffmpeg -y -i input.mp3 \
  -filter_complex \
    "[0:a]atrim=start=288.5,asetpts=PTS-STARTPTS[a_tail]; \
     [a_tail]aecho=0.9:0.7:120|280|450|650:0.45|0.25|0.12|0.06,apad=pad_dur=5[a_echo]; \
     [0:a]atrim=end=288.5[a_main]; \
     [a_main][a_echo]concat=n=2:v=0:a=1[out]" \
  -map "[out]" \
  output-echo.mp3
```

**Key parameters for hallway echo:**
- `aecho=output_gain:input_gain:delays:decays`
- Delays: `120|280|450|650` (ms — first echo at 120ms, last at 650ms)
- Decays: `0.45|0.25|0.12|0.06` (each repeat gets significantly quieter)
- `apad=pad_dur=5` adds 5 seconds of silence after the echo for natural ring-out
- Adjust `atrim=start=288.5` to the point where the last vocal word ends
- `areverb` filter is NOT available in most ffmpeg builds — use aecho with long delays instead

**Vanito's preferred timing:**
- Echo should hit only the VERY LAST word/note (last 1.5-3 seconds of the song)
- It should ring out naturally like a hallway or arena — "word... word...... word............"
- NOT the instrumental tail — the actual sung word
- About 4 extra seconds of echo ring-out after the song ends

**Pitfall:** Using `acrossfade` to blend the echo tail with the main song causes the echo effect to be audible BACKWARD into the song. Always use `concat` instead for clean separation.
**Pitfall:** Save the original MP3 as a backup before applying echo (`cp original.mp3 original-backup.mp3`).
**Pitfall:** Get the exact duration with `ffprobe -v error -show_entries format=duration -of csv=p=0 input.mp3` to know where to trim.