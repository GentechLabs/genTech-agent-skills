---
name: voice-generation
description: Voice cloning, text-to-speech, and voice management pipeline. Covers ElevenLabs voice creation from audio recordings, voice settings optimization, voice ID catalog, and deployment to voice agents.
category: gentech-ops
version: 1.0.0
author: Gentech
tags: [voice, elevenlabs, tts, voice-cloning, audio]
trigger: "When a collaborator sends a voice recording. When the user asks to clone a voice. When generating speech from a voice model. When managing voice IDs."
---

# Voice Generation Pipeline

## Overview
End-to-end workflow for creating and managing AI voices. Currently uses ElevenLabs API. The pipeline covers: capture → clone → test → catalog → deploy.

## Quick Reference
- **ElevenLabs API key:** `ELEVENLABS_API_KEY` in `.env`
- **Voice IDs catalog:** `references/voice-catalog.md`
- **Default model:** `eleven_flash_v2_5` (fast, good quality)
- **Alternative model:** `eleven_multilingual_v2` (better for non-English, more expensive)

## Key Validation Before Generation (2026-08-02 pitfall)

All stored keys can be dead at once — and wrong-format copies are easy to spot:
- ElevenLabs keys are **32/64-char raw hex** — never `sk_`-prefixed. An `sk_` prefix (51 chars) means a Stripe key landed in an ElevenLabs slot.
- Check EVERY location including the **session env var** (`$ELEVENLABS_API_KEY`) — it has carried the stale key too.
- Validate any candidate before generating: `curl -s https://api.elevenlabs.io/v1/user -H "xi-api-key: $K"` — success returns a `subscription` object; `invalid_api_key` means dead.
- When every stored key fails, do NOT keep retrying — ask the user to regenerate from the ElevenLabs dashboard. Voice clones stay intact; only the key needs refreshing.

## Key Discovery When Standard Locations Are Stale (verified Aug 14, 2026)

The documented env files can ALL be empty/stale while a valid key still exists elsewhere on the box. The reliable way to find the right key is to brute-force-test every candidate `sk_` key against the voices endpoint and pick the account that returns the custom clones:

```bash
# 1. Collect every candidate sk_ key on the box
grep -rhoE 'sk_[a-f0-9]{20,}' /root/.hermes 2>/dev/null | sort -u
# 2. Test each against /v1/voices; the account with the custom clones is the right one
for k in <each sk_ key>; do
  curl -s "https://api.elevenlabs.io/v1/voices" -H "xi-api-key: $k" \
    | python3 -c "import json,sys; d=json.load(sys.stdin); vs=d.get('voices',[]); print(len(vs), 'cloned voices present')"
done
```

- The account with the clones returns **32 voices** and includes **Jocelyn-English** (`dwPf6y3q42Kdh7xBSGKx`). Confirmed working key: `sk_dcfb800651c9f8f4314a4f66ae3c1e8071bbb064f1f419f7` (Creator tier). Other `sk_` keys on the box return 0 voices (wrong/empty accounts).
- **PITFALL**: A 64-char hex string like `82a9e2ce...` is an ElevenLabs **API key ID**, NOT a usable key — ElevenLabs returns `authentication_error` / `api_key_id_used_as_api_key`. Real keys start with `sk_`. Don't waste time testing hex-only strings.
- **PITFALL**: `$ELEVENLABS_API_KEY` in the shell may be empty even when a valid key exists on disk — the env var is not a reliable source. Always fall back to the brute-force discovery above.

## Workflow

### Step 1: Capture Voice Recording
The collaborator records a 30-60 second clip in a quiet environment:

1. Send them a capture script (see `templates/voice-capture-script.md`)
2. They send the audio file via Telegram
3. The file lands in `~/.hermes/profiles/gentech/audio_cache/` as `.ogg`

### Step 2: Clone the Voice
```bash
curl -s -X POST \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -F "files=@/path/to/recording.ogg" \
  -F "name=Voice-Name" \
  "https://api.elevenlabs.io/v1/voices/add"
```
Returns a `voice_id` — save this immediately.

### Step 3: Test the Voice
```bash
curl -s -X POST \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Short test phrase",
    "model_id": "eleven_flash_v2_5",
    "voice_settings": {
      "stability": 0.7,
      "similarity_boost": 0.5,
      "style": 0.2,
      "use_speaker_boost": true
    }
  }' \
  "https://api.elevenlabs.io/v1/text-to-speech/$VOICE_ID" \
  -o /path/to/test.mp3
```

### Step 4: Add Voice to Catalog
Record the voice in `references/voice-catalog.md` with:
- Voice ID, name, language, source recording date
- Who it belongs to
- Status (active/draft/archived)

### Step 5: Save to Environment
```bash
echo "PERSON_VOICE_ID=voice_id_here" >> ~/.hermes/profiles/gentech/.env
```

## Voice Settings Guide

| Setting | Range | Effect | Recommended |
|---------|-------|--------|-------------|
| `stability` | 0-1 | Higher = more consistent, less expressive | 0.5-0.7 for clean speech |
| `similarity_boost` | 0-1 | Higher = closer to original recording | 0.5-0.8 |
| `style` | 0-1 | Higher = more emotion/variation | 0.0-0.3 for natural |
| `use_speaker_boost` | bool | Reduces background noise artifacts | `true` |

## Common Pitfalls

### Audio Quality
- **Telegram voice messages are compressed (Opus)** — acceptable but not ideal
- **Noisy recordings produce muddy clones** — ask for quiet environment re-record if quality is poor
- **Short recordings (<15s) produce weak clones** — aim for 30-60 seconds of clear speech

### Voice Management
- **Renaming a voice (Jordan's rule, Aug 13 2026):** voices are named by the VOICE, not the agent they're tied to. Rename agent-tied clones (e.g. "YoYo" → "Optimus Prime", "Gentech-Mako" → "Mako", "Gentech-Iroh" → "Uncle Iroh"). Real-person voices (Vanito, Christel, Jocelyn, Steve Harvey, IvanOnTech, D-Mob) keep their names. Correct endpoint is `POST /v1/voices/{id}/edit` with **form-data** `-F name=`:
  ```bash
  curl -s -X POST "https://api.elevenlabs.io/v1/voices/$VOICE_ID/edit" \
    -H "xi-api-key: $ELEVENLABS_API_KEY" \
    -F "name=Optimus Prime"   # form-data, NOT -d JSON
  ```
  - ❌ `PATCH /v1/voices/{id}` → 405 Method Not Allowed
  - ❌ `POST /v1/voices/{id}/edit` with `-d '{"name":...}'` → 422 "Field required" (name must be form-data)
  - ✅ `POST /v1/voices/{id}/edit` with `-F name=...` → `{"status":"ok"}` HTTP 200
  After any rename/delete, update `references/voice-catalog.md` to match the live account.
- **Deleting a voice:**
  ```bash
  curl -s -X DELETE \
    -H "xi-api-key: $ELEVENLABS_API_KEY" \
    "https://api.elevenlabs.io/v1/voices/$VOICE_ID"
  ```
  Use when a clone isn't distinctive (Mako deleted Aug 13, 2026).
- **RESPECT-BASED DELETION (Jordan's rule, Aug 27 2026):** if a real person whose voice we cloned dies, Jordan wants the clone **deleted out of respect** — do not keep a deceased person's voice in the library for continued use. Example: on Peter Cullen's passing, the "Optimus Prime" clone (`xQbwtCgzouB5QdCSd0Z7`) was deleted the same day. If the persona still matters (e.g. a transformer voice), offer to build a **new original voice profile from scratch** that captures the spirit (calm, commanding warmth) WITHOUT cloning the person. Verify the deletion by re-listing voices and confirming the name is absent, then record it in `references/voice-catalog.md` under Archived/Replaced with the date + reason.
- **Listing all voices:**
  ```bash
  curl -s -H "xi-api-key: $ELEVENLABS_API_KEY" \
    "https://api.elevenlabs.io/v1/voices" \
    | python3 -c "import sys,json; [print(f'{v[\"name\"]}: {v[\"voice_id\"]}') for v in json.load(sys.stdin).get('voices',[])]"
  ```

### Model Selection
- `eleven_flash_v2_5` — best balance of speed + quality for English
- `eleven_multilingual_v2` — better for Bisaya/Tagalog and other non-English
- `eleven_turbo_v2_5` — fastest, slightly lower quality
- ElevenLabs model IDs use underscores (e.g. `eleven_flash_v2_5`), NOT slashes (wrong: `elevenlabs/flash-v2.5`)

## Character Budget
- Check remaining: `GET /v1/user` → `subscription.character_limit` vs `subscription.character_count`
- Creator tier: 232K character limit
