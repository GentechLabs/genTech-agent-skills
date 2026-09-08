---
name: voice-content-production
description: "Generate voice audio content across multiple agent personas using ElevenLabs. Covers voice cloning, multi-voice tracks, rap/comedy content, post-processing pipeline, and content delivery. Use when the user wants to create voice content, diss tracks, reaction audio, podcasts, or any multi-voice production."
version: 1.0.0
author: Gentech
tags: [voice, elevenlabs, tts, content, audio, rap, comedy, multi-voice]
trigger: "When the user wants voice content created — diss tracks, raps, podcast intros, reaction audio, multi-voice conversations, or any audio production using cloned voices."
---

# Voice Content Production

## Voice Roster

| Persona | Voice ID | Style | Best For |
|---------|----------|-------|----------|
| Steve Harvey | `Rxk9LQxvNFEplpjjsjuN` | Punchy, confident, **SLOW** | Social storytelling, daily content |
| Optimus Prime (Peter Cullen) | `xQbwtCgzouB5QdCSd0Z7` | Gravelly, authoritative | Bad cop, dramatic narration, rap |
| Uncle Iroh | `NqA7ncEPGGt1nDbCrDex` | Warm, wise | Good cop, comedy, wisdom drops |
| Vanito | `eMQtaKLvw87ksRqmQVpS` | Energetic, competitive | Roasts, reactions, self-deprecation |
| Christel | `kb3G0tkYW7pEGVlHEdu5` | Warm, supportive | Good cop, positive reinforcement |
| Jocelyn (English) | `dwPf6y3q42Kdh7xBSGKx` | Warm, Filipino accent | GenTech Academy, narration, educational content |

> **Voice naming convention (Jordan, Aug 13, 2026):** voices are named after the VOICE itself, NOT the agent they're tied to. "YoYo"→"Optimus Prime", "Gentech-Iroh"→"Uncle Iroh". Real people's voices (Vanito, Christel, Jocelyn, Steve Harvey, IvanOnTech) keep their names. **Mako (`TkEJnN27nf5BsX1xwrLB`) was DELETED** — it wasn't distinctive. Do not reference it.

## Rename / Delete an ElevenLabs Voice
**Correct rename endpoint — `POST /v1/voices/{voice_id}/edit` with form-data `-F name=...`:**
```bash
curl -s -X POST "https://api.elevenlabs.io/v1/voices/$VOICE_ID/edit" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -F "name=New Voice Name" -w "  -> HTTP %{http_code}\n"
# → {"status":"ok"} HTTP 200
```
**Pitfalls (all three wrong forms fail):**
- ❌ `PATCH /v1/voices/{id}` → HTTP 405 Method Not Allowed
- ❌ `POST /v1/voices/{id}/edit` with JSON body `{"name":...}` → HTTP 422 "Field required" (name must be form-data, not JSON)
- ❌ `POST /v1/voices/{id}` (no /edit) → 405
- Delete: `DELETE /v1/voices/{voice_id}` → `{"status":"ok"}`

## Production Pipeline

### 1. Generate Individual Clips
```bash
curl -s --max-time 30 -X POST "https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "YOUR TEXT HERE",
    "model_id": "eleven_flash_v2_5",
    "voice_settings": {"stability": 0.60, "similarity_boost": 0.85, "speed": 0.90}
  }' -o /tmp/output.mp3
```

### 2. Post-Process (MANDATORY)
```bash
ffmpeg -y -i input.mp3 \
  -af "afftdn,acompressor=threshold=-20dB:ratio=4:attack=5:release=50,loudnorm=I=-16:TP=-1.5:LRA=11" \
  output-clean.mp3
```

### 3. Clone Voice from Telegram Voice Message

When a collaborator sends a voice message (OGG/Opus via Telegram):

```bash
# 1. Find the most recent audio file
ls -lt /root/.hermes/profiles/gentech/audio_cache/*.ogg | head -3

# 2. Clone via ElevenLabs
curl -s -X POST \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -F "files=@/path/to/recording.ogg" \
  -F "name=Persona-Name" \
  "https://api.elevenlabs.io/v1/voices/add"
# Returns: {"voice_id": "abc123..."}

# 3. Save voice ID to .env
echo "PERSONA_VOICE_ID=abc123..." >> ~/.hermes/profiles/gentech/.env

# 4. Test the voice
curl -s -X POST \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Short test sentence here.",
    "model_id": "eleven_flash_v2_5",
    "voice_settings": {"stability": 0.7, "similarity_boost": 0.5, "style": 0.2, "use_speaker_boost": true}
  }' \
  "https://api.elevenlabs.io/v1/text-to-speech/VOICE_ID" \
  -o /tmp/voice-test.mp3

# 5. Verify: file /tmp/voice-test.mp3 should show "Audio file with ID3"
```

**Pitfall — Telegram voice messages are Opus-compressed.** Quality depends on the source recording. For best results:
- Ask for a recording in a quiet room (no TV, no background noise)
- 30-60 seconds is enough for a good clone
- Natural speaking voice, not reading
- Multiple short clips (2-3) produce better results than one long one

**If the clone sounds noisy/muffled:**
1. Delete the poor clone: `curl -s -X DELETE -H "xi-api-key: $ELEVENLABS_API_KEY" "https://api.elevenlabs.io/v1/voices/OLD_VOICE_ID"`
2. Ask for a cleaner recording from the person
3. Try higher stability (0.7-0.8) and lower similarity_boost (0.4-0.5) for cleaner output

### 4. Combine Multi-Voice Tracks
```bash
# Create concat list
cat > /tmp/track.txt << EOF
file '/tmp/voice1-clean.mp3'
file '/tmp/voice2-clean.mp3'
file '/tmp/voice3-clean.mp3'
EOF

# Combine
ffmpeg -y -f concat -safe 0 -i /tmp/track.txt -c copy /tmp/final-track.mp3
```

## Voice Settings for Different Content Types

| Content Type | Stability | Similarity | Speed | Notes |
|-------------|-----------|------------|-------|-------|
| Rap/Comedy | 0.55-0.65 | 0.80-0.85 | 0.90-0.95 | Lower stability = more expressive |
| Dramatic narration | 0.75-0.85 | 0.90-0.95 | 0.85 | Higher stability = more authoritative |
| Casual conversation | 0.65-0.75 | 0.85-0.90 | 0.90 | Balanced |
| Bad cop / roast | 0.70-0.80 | 0.90 | 0.85 | Firm but expressive |

## Steve Harvey Voice Direction

**Pacing: SLOW and DELIBERATE.** Like Steve Harvey leaning in to talk to a guest on his show — not reading a news report. He pauses. He lets words land. He looks at the audience before delivering the punchline.

- Pauses between sections (use periods and line breaks for pacing in the script)
- Warm, motivational, punchy — but never rushed
- No AI self-reference. Just Steve being Steve.
- Opening hook: "Let me tell you something..." or "Good morning..."
- Closing motivator: "You built it. Now ship it."

**Script format for daily digest / briefings:**
```
[Hook line]

[Pause — new paragraph]

[Content section — short sentences, room to breathe]

[Pause — new paragraph]

[Closer — direct, punchy, Steve energy]
```

## ElevenLabs Credit Conservation

When credits are depleted on Creator plan ($22/mo):

1. **Cut TTS from internal/unmonetized uses** — Daily digest, status reports, internal briefings → plain text only
2. **Preserve credits for monetizable outputs** — Hackathon demo videos, GenTech Hub voice companion, social content that gets views
3. **Buy PAYG credits for instant relief** — $5-10 buys enough for a demo video. PAYG credits last 12 months.
4. **Upgrade to Pro ($100/mo) only if consistently maxing Creator** — At $22/mo, every credit counts. Don't upgrade until the ROI is clear.
5. **API Key Management Protocol (NEW - June 29, 2026):**
   - **Never trust stored keys** - they expire/rotate
   - **Test keys before use:** `curl -X GET "https://api.elevenlabs.io/v1/user" -H "xi-api-key: YOUR_KEY"`
   - **Immediate replacement:** If key fails, immediately ask user for current valid key
   - **Session override:** Always use user-provided keys during active sessions
   - **Documentation sync:** Update vault files with current keys after successful sessions

**Rule:** If a TTS output doesn't have a direct revenue path or submission deadline, it doesn't get voice. Text is free.

## Audio Analysis

For analyzing/reviewing existing music files (not generating), use the `audio-analysis` skill. It covers loudness analysis, frequency band decomposition, spectrogram interpretation, and mastering assessment.

## Reference Files & Scripts

### Scripts
- **`scripts/test-elevenlabs-key.sh`** - API key validation script before voice generation
  - Usage: `./test-elevenlabs-key.sh YOUR_API_KEY`
  - Returns 0 if valid, 1 if invalid
  - Always run before any ElevenLabs voice generation

### References
- **`references/uncle-iroh-voice-production-guide.md`** - Complete workflow for Uncle Iroh voice creation including API key management
- **`references/voice-roster.md`** - Complete voice roster with IDs and use cases
- **`references/patch-notes-voice-delivery.md`** - Recent fixes and updates
- **`references/transformers-voice-casting.md`** - Multi-voice production guide

- **Rap timing:** ElevenLabs TTS has no rhythm control. Voice personality carries the performance more than perfect flow. For actual music production, use Suno or dedicated music AI.
- **File size limits:** Telegram media send can timeout on large files (>1MB). Split into individual clips if combined track is too large.
- **Rate limiting:** Swarms marketplace API returns 429 when called repeatedly. Wait 5+ seconds between API calls.
- **Voice coherence:** Long texts (>500 words) may lose voice consistency. Break into shorter clips and combine.
- **Post-processing is mandatory:** Raw ElevenLabs output has noise and inconsistent levels. Always apply the denoise + compress + normalize pipeline.
- **ElevenLabs API key rotation (NEW - June 29, 2026):** API keys can become invalid/expired over time. Always test with `curl -X GET "https://api.elevenlabs.io/v1/user" -H "xi-api-key: YOUR_KEY"`. If returns `{"detail":{"status":"invalid_api_key"}}`, immediately use user-provided replacement keys. **Never** trust keys stored in documentation files for active use.
- **ElevenLabs API key not in session env:** The key may be in `/root/.hermes/profiles/gentech/.env` OR `/root/.hermes/profiles/gentech/config/elevenlabs.env` (the config-specific location is often the freshest). Neither is auto-loaded into the session. Check both before generating:
  ```
  cat ~/.hermes/profiles/gentech/config/elevenlabs.env 2>/dev/null || cat ~/.hermes/profiles/gentech/.env 2>/dev/null | grep ELEVENLABS_API_KEY
  ```
  Load with: `export $(grep ELEVENLABS_API_KEY ~/.hermes/profiles/gentech/config/elevenlabs.env 2>/dev/null || grep ELEVENLABS_API_KEY ~/.hermes/profiles/gentech/.env 2>/dev/null | xargs)`
- **Payment fallback chain:** Prefer `mcp_blockrun_blockrun_speech` tool for ElevenLabs voice (x402, no key needed). If it fails (gateway error 502, low wallet), fall back to **direct ElevenLabs API via curl** with the configured API key — this is the reliable path for custom clone voices. The `text_to_speech` tool (Edge TTS) is last-resort-only for informational/non-character audio — the user explicitly rejects it for character voices. Verify audio output with `file` command (should return "Audio file with ID3" not "JSON data").
- **Voice ID search failures:** Custom voice IDs from voice lists may return "Not Found" errors. Have backup voices ready (e.g., Brian `nPczCjzI2devNBz1zQrb` for deep/warm tones). Test voice IDs before production use.
- **Audio format verification:** Use `file /tmp/audio.mp3` to confirm proper audio format. Should show "Audio file with ID3 version 2.4.0, contains: MPEG ADTS..." for MP3 or "Ogg data, Opus audio" for OGG. JSON responses indicate authentication or format issues.
- **Edge TTS fallback:** When ElevenLabs API key is invalid or credits are depleted, use Edge TTS as a free fallback. Voice mapping: Steve Harvey → `en-US-AndrewNeural` (rate=-5%, pitch=-2Hz), Vanito → `en-US-BrianNeural`. See `speech-engine` skill for full integration pattern.
- **Cron job TTS silence:** When writing cron job prompts that should generate voice, the prompt MUST explicitly say "You MUST call the text_to_speech tool" and "If you only output text without calling the tool, the voice message will not be delivered." Without this, the cron runner writes the script text but never generates audio. Proven on Daily Digest cron (May 25, 2026).

## Demo Video Voiceover Workflow

**Moved to:** `demo-video-production` skill → `references/voiceover-workflow.md`

For hackathon demo video voiceover (segmented generation, cleaning, concatenation), load `demo-video-production` skill.

## Content Ideas

- **Diss tracks:** Multiple voices roasting a target (comedy)
- **Roasts (educational):** Roast a topic to make learning fun — history, science, math. "Let me tell you about Napoleon, this short king syndrome having—" makes facts stick better than a textbook.
- **Roasts (social):** Roast a trend, news event, or public figure. Comedy gold for social clips.
- **Roasts (self-deprecation):** Vanito voice roasting himself or the team. Relatable, shareable.
- **Podcast intros:** Steve Harvey voice introducing topics
- **Agent-Repairathy:** Good cop (Christel/Iroh) + Bad cop (Optimus) therapy sessions
- **Daily digest:** Steve Harvey voice + market summary
- **Reaction audio:** Voices reacting to news/events
- **Game narration:** Optimus Prime narrating Agent Arena matches

## Roast Script Library

**Full library:** `09-Green Room/content/roasts/roast-library.md`

Categories with ready-to-use scripts:
- **Tech Roasts:** Python indentation, PHP, Solidity gas fees, CSS centering, JS frameworks
- **Crypto/DeFi Roasts:** Rug pulls, NFT holders, "not financial advice", yield farmers
- **Self-Roasts:** Friday deploys, agent stack chaos, GenLayer Builder Program grind
- **Educational Roasts:** Napoleon, black holes, imaginary numbers
- **Roast Battles:** Optimus vs Vanito, Steve Harvey vs Uncle Iroh (multi-voice)

**Social clip format:** 15-30 seconds, pick punchiest 2-3 lines, add captions.
**Hashtags:** #Roast #TechHumor #CryptoRoast #AgentArena #GenTechLabs

## Roasting as a Content Category

Roasting works because it's **engagement-first learning**. People remember things that made them laugh or feel something.

### Uncle Iroh Voice Production Technique
**See `references/uncle-iroh-voice-production-guide.md` for detailed workflow, settings, and examples.**

**Quick Reference:**
- **Voice:** Brian - "Deep, Resonant and Comforting" (ID: `nPczCjzI2devNBz1zQrb`)
- **Settings:** stability=0.7, similarity_boost=0.85, style=0.6
- **Phrase:** "Great, googly-moogly, that thing is juicy!"
- **Workflow:** Use `text_to_speech` tool → verify format → send to Telegram

## Transformers Voice Casting

**Full guide:** `references/transformers-voice-casting.md`

When casting characters for multi-voice skits:
- Map personality traits to voice characteristics
- Use existing clones first (Optimus = YoYo), premade voices for the rest
- All male voices for Transformers theme
- 6-character conversation flow: Optimus → Starscream → Megatron → Bumblebee → Soundwave → Ironhide
- 25-35 seconds per skit, 1-2 lines per character

**Roast formats:**
| Format | Description | Example |
|--------|-------------|---------|
| Topic roast | Roast a subject like you're trash-talking an opponent | "Python thinks indentation is personality" |
| History roast | Roast historical figures with modern slang | "Napoleon really said 'I'm him' and then lost to winter" |
| Tech roast | Roast technologies, frameworks, companies | "PHP? More like Please Help People" |
| Self-roast | Roast yourself or your team | "We deployed to mainnet on a Friday" |
| Rap roast | Multi-voice roast battle over a beat | Optimus vs Iroh trading bars |

**Why this works for learning:**
- Emotional engagement → better retention
- Humor creates记忆点 (memory hooks)
- Roasting forces you to understand something well enough to make fun of it
- Social sharing potential is high — people share what makes them laugh
