# ElevenLabs Voice Cloning — Quick Reference

## Pipeline (first student pilot, Jul 24, 2026)

1. **Get recording** — ~1 min voice message, quiet room, natural tone, native language
2. **Find audio file** in Telegram audio cache: `ls -lt ~/.hermes/profiles/gentech/audio_cache/*.ogg`
3. **Clone voice** via API:
   ```bash
   curl -s -X POST \
     -H "xi-api-key: $ELEVENLABS_API_KEY" \
     -F "files=@/path/to/recording.ogg" \
     -F "name=VoiceName" \
     "https://api.elevenlabs.io/v1/voices/add"
   ```
   Returns `voice_id` (e.g. `aWJOnPY23xAoAyL1eQwL`)
4. **Test the voice:**
   ```bash
   VOICE_ID="<voice_id>"
   curl -s -X POST \
     -H "xi-api-key: $ELEVENLABS_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello, testing 1 2 3", "model_id": "eleven_flash_v2_5", "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}}' \
     "https://api.elevenlabs.io/v1/text-to-speech/$VOICE_ID" \
     -o test.mp3
   ```
5. **Save voice ID** to `.env`:
   ```
   JOCELYN_VOICE_ID=<archived-original-voice-id>
   ```

## Key Notes
- Recording file must be valid audio (OGG/Opus from Telegram voice messages works)
- Model ID is `eleven_flash_v2_5` (not `elevenlabs/flash-v2.5`)
- Default model for TTS testing: `eleven_flash_v2_5` (fast, cheap)
- For highest quality (voice cloning): `eleven_monolingual_v1`
- Voice settings: stability 0.3-0.5 (lower = more expressive), similarity_boost 0.7-0.85 (higher = more accurate)
