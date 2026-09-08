---
name: elevenlabs-voice-generation
description: ElevenLabs voice generation workflow - API integration, audio validation, workflow patterns, and Gentech custom voices. Covers endpoint format, duration validation, and gentech-ops integration.
version: 1.0.0
author: Gentech
tags: [elevenlabs, voice, tts, audio, gentech-ops, workflow]
---

# ElevenLabs Voice Generation

## Trigger Conditions
- User requests custom voice generation
- ElevenLabs API calls for voice cloning or TTS
- Audio duration issues or truncation problems
- Voice workflow integration needed
- Human collaborator voice capture for cloning — onboarding new talent (see Human Voice Capture for Cloning section)

## Voice Audit & Discovery

Before using a voice, verify it exists and confirm the correct voice ID:

### List All Account Voices
```bash
curl -s "https://api.elevenlabs.io/v1/voices" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for v in data.get('voices', []):
    name = v.get('name', '??')
    vid = v.get('voice_id', '??')
    cat = v.get('category', '??')
    print(f'{cat:15s} {vid:26s} {name}')
"
```

This returns premade voices + any custom clones on the account. The Steve Harvey clone appears as `"Desmond-SteveHarvey"` with voice ID `Rxk9LQxvNFEplpjjsjuN`.

### Check Subscription & Usage
```bash
curl -s "https://api.elevenlabs.io/v1/user/subscription" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" | python3 -m json.tool
```
Returns character_count, character_limit, tier, next billing. Confirmed Jul 2026: Creator tier ($22/mo), 8,897 chars used of 121,005 (7.4%).

### Verify a Specific Voice ID
Use the same list command and grep for the ID:
```bash
curl -s "https://api.elevenlabs.io/v1/voices" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" | python3 -c "
import json, sys
data = json.load(sys.stdin)
target = 'Rxk9LQxvNFEplpjjsjuN'  # Steve Harvey
for v in data.get('voices', []):
    if v['voice_id'] == target:
        print(f'✅ FOUND: {v[\"name\"]} ({v[\"category\"]})')
        sys.exit(0)
print('❌ NOT FOUND')
sys.exit(1)
"
```

## Pre-Flight Checklist
1. **Load supporting skills** as needed:
   - `gentech-ops` — for complex operational workflows, project coordination, or multi-step builds
   - `voice-content-production` — for multi-voice production, social media scripts, or character-driven content
2. **Key recovery** — Keys rot and live in multiple locations. Check in order:
   - `~/.hermes/profiles/gentech/home/.hermes/profiles/gentech/.env` (actual working profile env path — nested home dirs on some setups)
   - `~/.hermes/profiles/gentech/.env` (profile env — may be symlinked or not exist)
   - `~/.hermes/profiles/gentech/config/elevenlabs.env` (profile config — often the freshest ElevenLabs-specific key, e.g. `sk_fc9d...a6df`)
   - `~/.hermes/.env` (root Hermes env)
   - Vault `HQ/config/secrets-vault.env` (may be stale or mis-copied)
   - Portfolio `HQ/Integrations/elevenlabs-api-key.md` (documented key)
   - If all are expired, ask the user to regenerate from ElevenLabs dashboard
   - **PITFALL**: On some Hermes setups, the actual profile env file is nested under home directory (`~/.hermes/profiles/gentech/home/.hermes/profiles/gentech/.env`). Always verify actual paths with `find ~/.hermes -name ".env"` before assuming standard locations.
3. Check voice ID exists and is accessible
4. Validate text length (minimum 4-6 seconds of speech)

## API Endpoint Format
**CORRECT:**
```bash
POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}
Content-Type: application/json
xi-api-key: {api_key}

{
  "text": "Longer sentence with natural pacing...",
  "model_id": "eleven_turbo_v2_5",
  "voice_settings": {
    "stability": 0.75,
    "similarity_boost": 0.90
  }
}
```

**WRONG (Common Errors):**
- `/v1/text-to-speech` (missing voice_id in path)
- Short phrases (<3 seconds) - get truncated
- Using `eleven_multilingual_v2` instead of `eleven_turbo_v2_5`
- Missing `voice_settings` — voices without settings use defaults that may not match the clone

## Human Voice Capture for Cloning

When cloning a human collaborator's voice (e.g. the first-student pipeline), follow this end-to-end flow from introduction to ElevenLabs model creation.

### Trigger
- A collaborator (especially non-technical) needs a cloned voice for agent deployment
- Jordan introduces someone as voice talent

### Step 1 — Create a Voice Capture Script

Write a natural recording script with **4-5 short sections** mixing:
- **English introduction** (30s) — formal, clear: name, role, excitement
- **Native language** (30s) — natural, conversational, like talking to a friend
- **Warm/emotional English** (30s) — friendly tone, gratitude, future goals
- **Professional English** (30s) — clear enunciated, professional cadence
- **Casual native language** (20s) — short, relaxed sign-off

Use the template at `templates/voice-capture-script.md` — adapt the native language and personal details.

### Step 2 — Recording Instructions (send to the person)

- Find a quiet room with no echo (small room with soft furniture is best)
- Hold phone 15-20cm from mouth — not too close (distortion), not too far (room noise)
- Speak naturally — like talking to a friend, not reading an announcement
- Smile while talking — it warms the voice naturally
- Don't worry about mistakes — just keep going, natural is better than perfect
- Record each section as a SEPARATE file (makes it easier to select the best takes)
- Send via Telegram voice message or audio file attachment

### Step 3 — Receive & Validate Audio

```bash
# Check format, duration, quality
file /path/to/audio.ogg
ffprobe -v quiet -show_format -show_streams /path/to/audio.ogg
# Look for: duration >= 30s, mono/stereo OK, clean Opus/MP3
```

Target: at least **1 minute total clean audio** (ElevenLabs minimum for decent clone).

### Critical: Check Audio Cache Before Asking for Re-Recording

When someone says they sent a recording but you don't see it in the chat, **check the Telegram audio cache first** before asking them to re-record:

```bash
ls -lt ~/.hermes/profiles/gentech/audio_cache/*.ogg | head -10
```

The Telegram gateway stores voice messages as `.ogg` files in the audio cache. The most recent file is likely their recording. Do not ask someone to re-record something they already sent — Jordan will call you out for repeating yourself.

The most common reason you "never received" the message is the Telegram gateway filtering the user's ID via `TELEGRAM_ALLOWED_USERS` in `.env`, not the recording itself. Check that first (see `collaborator-onboarding` skill).

### Step 4 — Create ElevenLabs Voice Model

Requires a valid `ELEVENLABS_API_KEY` in env. Use the ElevenLabs Add Voice API:

```bash
curl -s -X POST "https://api.elevenlabs.io/v1/voices/add" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -F "name=VoiceName" \
  -F "files=@/path/to/best_take.ogg" \
  -F "description=Natural voice of ..." \
  -F 'labels={"accent":"filipino","gender":"female","age":"young adult"}'
```

Returns the new voice_id. Save it to `references/voice-catalog.md` immediately.

**Pitfalls:**
- ❌ **If no API key found**: The key may not be in any env file. Ask Jordan to paste it directly — don't search endlessly through stale config files. This session confirmed the key was absent from all config locations.
- ❌ **OGG files work fine with ElevenLabs** — no need to convert to MP3 first. ElevenLabs accepts Ogg Opus natively.
- ❌ **Multiple short recordings over one long file**: Multiple short takes give ElevenLabs more vocal variety to model from.
- ❌ **Character drift on long reads**: Same rule as all cloned voices — use `eleven_multilingual_v2`, not `eleven_turbo_v2_5`.

### Step 5 — Track Progress

After model creation, update:
- `references/voice-catalog.md` — add voice_id, settings, source
- Collaborator's progress tracker (`00-HQ/collaborators/{name}-progress.md`) — mark voice cloning as done
- Next stage: Pipecat/Omnivoice integration for agent deployment

---

## Content Pipeline Integration

The content pipeline at `scripts/content-pipeline.py` + `scripts/elevenlabs-narrate.py` generates automated build report voiceovers:

### Pipeline Flow
1. `scripts/content-pipeline.py --preview` — reads build queue + PR portfolio, generates a video script
2. `scripts/elevenlabs-narrate.py` — takes the script, narrates with ElevenLabs using the default voice, saves MP3
3. `npx remotion studio` — design the video using Remotion skills
4. `npx remotion render` — exports final video

### Default Voice
- **YoYo** (`xQbwtCgzouB5QdCSd0Z7`) — default for content pipeline narration
- Set in `scripts/elevenlabs-narrate.py` as the fallback voice
- Uses direct ElevenLabs API (not BlockRun) — your API key, your cloned voices
- Settings: stability 0.4, similarity_boost 0.7, model `eleven_multilingual_v2`

### Key Files
- `scripts/content-pipeline.py` — generates scripts from build queue data
- `scripts/elevenlabs-narrate.py` — narrates scripts via ElevenLabs API
- `assets/content-pipeline/` — output directory for MP3 files

### Pitfalls
- ❌ **Built-in TTS vs ElevenLabs clone**: The `text_to_speech` tool uses Edge TTS, not ElevenLabs. For cloned voices, always use the direct ElevenLabs API via curl with your API key. User explicitly rejected Edge TTS for cloned voices.
- ❌ **BlockRun speech for cloned voices**: BlockRun's speech tool only works with premade ElevenLabs voices. Custom clones return HTTP 502. Always use direct API for clones.
- ❌ **Voice ID confusion**: ElevenLabs voice IDs are short alphanumeric (e.g. `xQbwtCgzouB5QdCSd0Z7`). 64-char hex strings are API keys, not voice IDs.

## Gentech Custom Voices

Full catalog with settings in `references/voice-catalog.md`.

- **Steve Harvey:** `Rxk9LQxvNFEplpjjsjuN` — stability 0.45, similarity 0.75, model `eleven_multilingual_v2`. Expressive/preacher cadence. Social media narration, comic announcements. See `references/steve-harvey-config.md` for verified settings and pacing template. **For product announcement script structure** (concrete-before-abstract framing), see `references/product-announcement-script-structure.md`.
- **Optimus Prime (Peter Cullen):** `xQbwtCgzouB5QdCSd0Z7` — gravelly, resonant baritone. Stability 0.75, similarity 0.85, speed 0.88, model `eleven_multilingual_v2`. Renamed from "YoYo" (Aug 13, 2026) — voices are named by the voice, not the agent. Confirmed working API key `sk_dcfb800651c9f8f4314a4f66ae3c1e8071bbb064f1f419f7` (Creator tier).
- **Vanito:** `eMQtaKLvw87ksRqmQVpS` — Gaming content
- **IvanOnTech:** `ToA54GQ3jBRB2zt0fBXj`
- **Christel (TrustGuard Good Cop):** `kb3G0tkYW7pEGVlHEdu5`
- **Christel:** `R8Nmfj7gteuYpqJBPrMD`
- **D-Mob:** `n2icbiwmCen7udwM65GS`
- **Gentech-Iroh:** `NqA7ncEPGGt1nDbCrDex` (Uncle Iroh clone)
- **Alex (professional):** `XaEUesE01wKIKaa0xI0h`
- **Alexei (professional):** `NQJnREzQtnAHHZnia0tY`

**No Optimus Prime / Peter Cullen voice found in account.** The 64-char hex string Jordan provided is an API key, not a voice ID. ElevenLabs voice IDs are shorter alphanumeric (e.g. `Rxk9LQxvNFEplpjjsjuN`).

## Payment Fallback Chain

When the primary payment path fails, fall back in this order:

1. **Direct ElevenLabs API via curl** — Preferred for ALL custom cloned voices. Uses `ELEVENLABS_API_KEY` from env (confirmed working key: `6e3f26583ebfb5cfcc13fb60b23a2d0bc45b7ebf6208bd86eed0ea3394337fef`).

   ```bash
   # Direct API call — no BlockRun dependency
   export ELEVENLABS_API_KEY=$(grep ELEVENLABS_API_KEY ~/.hermes/profiles/gentech/.env 2>/dev/null | head -1 | cut -d= -f2)
   
   curl -s --max-time 60 -X POST "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}" \
     -H "xi-api-key: $ELEVENLABS_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Message with natural pacing...",
       "model_id": "eleven_turbo_v2_5",
       "voice_settings": {
         "stability": 0.75,
         "similarity_boost": 0.90
       }
     }' \
     --output output.mp3
   ```

2. **BlockRun speech tool** (`mcp_blockrun_blockrun_speech`) — x402, uses wallet USDC. **LIMITATION: Only works with ElevenLabs PREMADE voices.** Custom/cloned voices (Desmond-SteveHarvey, Vanito, Iroh, etc.) return HTTP 502 from BlockRun gateway because it uses BlockRun's own ElevenLabs integration which lacks access to account-specific clones. Verified Jul 2026.

3. **Edge TTS** (`text_to_speech` tool) — only for non-character, informational audio. User explicitly rejects this for character voices — it re-encodes through Edge TTS and discards the cloned voice character.

**Rule of thumb:**
- Premade ElevenLabs voices (Roger, Sarah, George, etc.) → BlockRun OR direct API
- Custom/cloned voices (Steve Harvey, Vanito, Iroh, etc.) → **Direct API only**

## Audio Duration Validation
```bash
# Check duration before delivery
ffprobe -v quiet -show_format -show_streams audio.mp3
# Look for: duration=X.XXXXXX (must be >3.0)
```

## Workflow Pattern
1. **Load supporting skills** as needed (see Pre-Flight Checklist)
2. **Apply session hygiene** protocols
3. **Route through proper task classification**
4. **Run Pre-Flight key recovery** — keys are often stale in vault; check root `.hermes/.env` first
5. **Generate audio** with correct endpoint
6. **Validate duration** (>3 seconds minimum)
7. **Persist working key** — save to `~/.hermes/profiles/gentech/.env` for next session
8. **Deliver to target channel** with proper context

## Common Pitfalls
- ❌ **Expired API key in vault**: Vault backups and documented keys often go stale. When all stored keys return `invalid_api_key` or `authentication_error`, immediately ask user to regenerate fresh key from ElevenLabs dashboard. Do not attempt to retry with same stale key — confirmed session Jul 6, 2026: `bb158b2f8063a7d10519ffb3a349d168195f67c9fe5698532e5c191d70298674` expired, required manual fresh key `6e3f26583ebfb5cfcc13fb60b23a2d0bc45b7ebf6208bd86eed0ea3394337fef`.
- ❌ **Stripe key mistaken for ElevenLabs**: Backup files may copy the wrong key (e.g. `sk_` prefixed Stripe keys). ElevenLabs keys are raw hex strings.
- ❌ **Voice degradation on long reads (cloned voices)**: Cloned voices crumble/drift on single-shot generations over 35-40 seconds — especially with `eleven_turbo_v2_5`. Fix: split into segments of ~35s max, generate each with `eleven_multilingual_v2`, stitch with ffmpeg concat.
- ❌ **Settings mismatch for voice type**: Expressive voices (Steve Harvey) need low stability (~0.45). Using defaults (0.75) makes them sound stiff, then the model overcompensates and degrades. Match settings to voice type using the Voice Settings Guide above or `gentech/voice-agent-config`.
- ❌ Short audio truncation: Use longer sentences (4-6s minimum)
- ❌ Wrong endpoint format: Always `/v1/text-to-speech/{voice_id}`
- ❌ Missing duration check: Validate before delivery
- ❌ **Generic TTS fallback**: User explicitly rejected — use real custom voices
- ❌ **`text_to_speech` tool overrides cloned voices**: The `text_to_speech` tool re-encodes audio through Edge TTS, discarding the ElevenLabs voice character. For cloned voices (Steve Harvey, Vanito, Iroh, etc.), always use the ElevenLabs API directly or `mcp__blockrun__blockrun_speech` with the raw voice ID. Never use `text_to_speech` for custom voice clones.

## Verification Steps
1. Check file exists and is valid MP3
2. Verify duration >3.0 seconds
3. Confirm voice ID matches requested clone
4. Test playback before delivery
5. Send to correct Telegram channel with context

## Model Selection Guide

| Model | When to Use | Notes |
|-------|------------|-------|
| `eleven_turbo_v2_5` | Short non-clone reads (<30s), speed-priority | Degrades on cloned voices over 30s. Avoid for character work. |
| **`eleven_multilingual_v2`** | **All cloned voices, any length** | **Preferred for Steve Harvey, Iroh, Vanito, Mako, D-Mob** — retains character better than turbo with no degradation on long reads. Also supports multi-language. |
| `eleven_monolingual_v1` | Production long-form English narration | Highest quality English model. Overkill for short social clips. |

## Voice Settings Guide

Default settings (stability 0.75, similarity 0.90) are a starting point only. Cloned voices almost always need tuning per voice type:

| Voice Type | Stability | Similarity | Style | Model |
|-----------|-----------|-----------|-------|-------|
| Expressive / Preacher (Steve Harvey — v2 tuned) | **0.85** | 0.75 | 0.15 | `eleven_multilingual_v2` |
| Professional / Narrator | 0.65–0.80 | 0.80–0.92 | 0.20 | `eleven_turbo_v2_5` |
| Energetic / Gaming (Vanito) | 0.45–0.60 | 0.72–0.85 | 0.25 | `eleven_multilingual_v2` |
| Deep / Authoritative (Optimus Prime, Mako) | 0.70–0.85 | 0.85–0.95 | 0.10 | `eleven_turbo_v2_5` |
| Warm / Storyteller (Iroh) | 0.55–0.70 | 0.72–0.85 | 0.20 | `eleven_multilingual_v2` |

> **Steve Harvey v2 note:** Stability 0.85 is higher than typical expressive voices because it eliminates background noise artifacts from the Desmond-SteveHarvey clone. The script at `steve-harvey-tts.py` uses stability 0.85 + similarity 0.75 + style 0.15 with post-processing (highpass filter + noise gate + loudnorm) for clean broadcast-grade output. See that script for the full verified pipeline.

For complete pacing templates, script formatting rules, and a reusable voice config template, see **`gentech/voice-agent-config`** skill.

## Delivery Format
```
[Voice Name] says: [Message text] 🎵
AUDIO: Custom voice description
MEDIA:/path/to/audio.mp3
```